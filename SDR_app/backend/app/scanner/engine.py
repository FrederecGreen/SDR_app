"""Scanner engine that orchestrates frequency scanning and recording."""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

from backend.app.config import scanner_config, throttle_state, RECORDINGS_DIR
from backend.app.models import FrequencyEntry, Detection, ModulationType
from backend.app.frequency_groups import get_all_groups, get_group
from backend.app.scanner.audio_pipeline import AudioPipeline, assemble_session
from backend.app.scanner.resource_monitor import resource_monitor
from backend.app.scanner.signal_detector import SignalDetector

logger = logging.getLogger("scanner")

class ScannerEngine:
    """Main scanner engine."""
    
    def __init__(self):
        self.running = False
        self.scan_task: Optional[asyncio.Task] = None
        self.frequency_list: List[FrequencyEntry] = []
        self.detections: Dict[float, Detection] = {}  # freq_mhz -> Detection
        self.audio_pipeline = AudioPipeline()
        self.signal_detector = SignalDetector()
        self.current_freq_index = 0
        self.recording_freq: Optional[float] = None
        self.recording_start_time: Optional[datetime] = None
    
    async def start_scan(self, 
                        frequency_groups: List[str],
                        custom_frequencies: List[FrequencyEntry],
                        dwell_seconds: Optional[float] = None,
                        squelch_db: Optional[int] = None) -> bool:
        """Start scanning."""
        if self.running:
            logger.warning("Scanner already running")
            return False
        
        # Build frequency list from groups
        self.frequency_list = []
        all_groups = get_all_groups()
        
        for group_name in frequency_groups:
            if group_name in all_groups:
                group = all_groups[group_name]
                self.frequency_list.extend(group.frequencies)
                logger.info(f"Added {len(group.frequencies)} frequencies from {group_name}")
            else:
                logger.warning(f"Unknown frequency group: {group_name}")
        
        # Add custom frequencies
        self.frequency_list.extend(custom_frequencies)
        
        if not self.frequency_list:
            logger.error("No frequencies to scan")
            return False
        
        logger.info(f"Starting scan with {len(self.frequency_list)} frequencies")
        
        # Apply config overrides
        if dwell_seconds is not None:
            scanner_config.default_dwell_seconds = dwell_seconds
        if squelch_db is not None:
            scanner_config.default_squelch_db = squelch_db
        
        self.running = True
        self.current_freq_index = 0
        self.detections = {}
        
        # Start scan loop
        self.scan_task = asyncio.create_task(self._scan_loop())
        return True
    
    async def stop_scan(self) -> bool:
        """Stop scanning."""
        if not self.running:
            return False
        
        logger.info("Stopping scanner...")
        self.running = False
        
        # Stop any active recording
        if self.audio_pipeline.is_recording():
            await self._stop_recording()
        
        # Cancel scan task
        if self.scan_task:
            self.scan_task.cancel()
            try:
                await self.scan_task
            except asyncio.CancelledError:
                pass
            self.scan_task = None
        
        logger.info("Scanner stopped")
        return True
    
    async def _scan_loop(self):
        """Main scanning loop."""
        try:
            while self.running:
                # Monitor resources and adjust throttling
                await asyncio.to_thread(resource_monitor.monitor_and_adjust)
                
                # Check if paused by throttle
                if throttle_state.paused:
                    logger.info("Scan paused by throttle")
                    await asyncio.sleep(5)
                    continue
                
                # Get next frequency to scan
                freq_entry = self._get_next_frequency()
                if not freq_entry:
                    # Reached end of list, wrap around
                    self.current_freq_index = 0
                    await asyncio.sleep(scanner_config.scan_delay_seconds)
                    continue
                
                # Scan this frequency
                await self._scan_frequency(freq_entry)
                
                # Apply dwell time with throttle multiplier
                dwell = scanner_config.default_dwell_seconds * throttle_state.dwell_multiplier
                await asyncio.sleep(dwell)
                
        except asyncio.CancelledError:
            logger.info("Scan loop cancelled")
        except Exception as e:
            logger.error(f"Scan loop error: {e}", exc_info=True)
        finally:
            self.running = False
    
    def _get_next_frequency(self) -> Optional[FrequencyEntry]:
        """Get next frequency to scan, applying skip if throttled."""
        if self.current_freq_index >= len(self.frequency_list):
            return None
        
        freq_entry = self.frequency_list[self.current_freq_index]
        
        # Apply frequency skip if throttled
        skip = throttle_state.skip_frequencies + 1
        self.current_freq_index += skip
        
        return freq_entry
    
    async def _scan_frequency(self, freq_entry: FrequencyEntry):
        """Scan a single frequency."""
        try:
            # Check for signal
            has_signal, signal_strength = await asyncio.to_thread(
                self.signal_detector.detect_signal,
                freq_entry
            )
            
            if has_signal:
                logger.info(f"Signal detected: {freq_entry.freq_mhz} MHz ({signal_strength:.1f} dB)")
                
                # Update or create detection
                if freq_entry.freq_mhz in self.detections:
                    detection = self.detections[freq_entry.freq_mhz]
                    detection.last_seen = datetime.utcnow()
                    detection.signal_strength_db = signal_strength
                else:
                    detection = Detection(
                        freq_mhz=freq_entry.freq_mhz,
                        mode=freq_entry.mode,
                        signal_strength_db=signal_strength,
                        label=freq_entry.label,
                        first_seen=datetime.utcnow(),
                        last_seen=datetime.utcnow()
                    )
                    self.detections[freq_entry.freq_mhz] = detection
                
                # Start recording if not already recording
                if not self.audio_pipeline.is_recording():
                    await self._start_recording(freq_entry, detection)
                elif self.recording_freq == freq_entry.freq_mhz:
                    # Continue recording on same frequency
                    await self._continue_recording(detection)
                else:
                    # Different frequency has signal, stop current and start new
                    await self._stop_recording()
                    await self._start_recording(freq_entry, detection)
            else:
                # No signal on this frequency
                if self.recording_freq == freq_entry.freq_mhz:
                    # We were recording this freq, check if we should stop
                    elapsed = (datetime.utcnow() - self.recording_start_time).total_seconds()
                    if elapsed > scanner_config.signal_timeout_seconds:
                        logger.info(f"Signal timeout on {freq_entry.freq_mhz} MHz")
                        await self._stop_recording()
        
        except Exception as e:
            logger.error(f"Error scanning {freq_entry.freq_mhz} MHz: {e}")
    
    async def _start_recording(self, freq_entry: FrequencyEntry, detection: Detection):
        """Start recording a frequency."""
        try:
            success = await asyncio.to_thread(
                self.audio_pipeline.start_recording,
                freq_entry
            )
            
            if success:
                self.recording_freq = freq_entry.freq_mhz
                self.recording_start_time = datetime.utcnow()
                logger.info(f"Started recording: {freq_entry.freq_mhz} MHz")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
    
    async def _continue_recording(self, detection: Detection):
        """Continue recording, check if we should stop due to max duration."""
        if not self.recording_start_time:
            return
        
        elapsed = (datetime.utcnow() - self.recording_start_time).total_seconds()
        
        # Stop if max session duration reached
        if elapsed >= scanner_config.max_session_duration_seconds:
            logger.info(f"Max session duration reached: {elapsed:.1f}s")
            await self._stop_recording()
    
    async def _stop_recording(self):
        """Stop recording and assemble session."""
        try:
            chunk_files = await asyncio.to_thread(self.audio_pipeline.stop_recording)
            
            if chunk_files and len(chunk_files) > 0:
                # Assemble session
                first_chunk = chunk_files[0]
                session_name = first_chunk.name.rsplit('_part', 1)[0] + ".ogg"
                session_path = first_chunk.parent / session_name
                
                success = await asyncio.to_thread(
                    assemble_session,
                    chunk_files,
                    session_path
                )
                
                if success:
                    logger.info(f"Session created: {session_path}")
                    # Update detection with recording ID
                    if self.recording_freq in self.detections:
                        self.detections[self.recording_freq].recording_id = session_path.stem
            
            self.recording_freq = None
            self.recording_start_time = None
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
    
    def get_detections(self) -> List[Detection]:
        """Get list of active detections (seen in last 60 seconds)."""
        cutoff = datetime.utcnow() - timedelta(seconds=60)
        active = [d for d in self.detections.values() if d.last_seen > cutoff]
        return sorted(active, key=lambda d: d.last_seen, reverse=True)
    
    def is_running(self) -> bool:
        """Check if scanner is running."""
        return self.running

# Global scanner instance
scanner_engine = ScannerEngine()
