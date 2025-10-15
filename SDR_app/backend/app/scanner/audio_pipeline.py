"""Audio recording pipeline using rtl_fm and ffmpeg."""
import subprocess
import logging
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from backend.app.config import scanner_config, RECORDINGS_DIR
from backend.app.models import FrequencyEntry, ModulationType

logger = logging.getLogger("scanner")

class AudioPipeline:
    """Manage audio recording pipeline."""
    
    def __init__(self):
        self.rtl_fm_process: Optional[subprocess.Popen] = None
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        self.current_recording_path: Optional[Path] = None
        self.recording_start_time: Optional[datetime] = None
    
    def _get_rtl_fm_params(self, freq_entry: FrequencyEntry) -> list:
        """Get rtl_fm parameters based on modulation."""
        freq_hz = int(freq_entry.freq_mhz * 1e6)
        
        # Base parameters
        params = [
            "rtl_fm",
            "-d", str(scanner_config.scanner_device),
            "-f", str(freq_hz),
            "-g", str(scanner_config.default_squelch_db),
        ]
        
        # Modulation-specific parameters
        if freq_entry.mode == ModulationType.NFM:
            params.extend(["-M", "fm", "-s", "24k", "-r", "48k"])
        elif freq_entry.mode == ModulationType.FM:
            params.extend(["-M", "fm", "-s", "50k", "-r", "48k"])
        elif freq_entry.mode == ModulationType.WFM:
            params.extend(["-M", "wbfm", "-s", "200k", "-r", "48k"])
        elif freq_entry.mode == ModulationType.AM:
            params.extend(["-M", "am", "-s", "24k", "-r", "48k"])
        else:
            # Default to NFM
            params.extend(["-M", "fm", "-s", "24k", "-r", "48k"])
        
        params.append("-")  # Output to stdout
        return params
    
    def _get_chunk_path(self, freq_entry: FrequencyEntry, chunk_num: int) -> Path:
        """Generate chunk file path."""
        timestamp = self.recording_start_time.strftime("%Y%m%d_%H%M%S")
        freq_str = f"{freq_entry.freq_mhz:.4f}".replace('.', '_')
        label = freq_entry.label.replace(' ', '_') if freq_entry.label else "unknown"
        filename = f"{timestamp}_{freq_str}_{label}_part{chunk_num:03d}.ogg"
        return RECORDINGS_DIR / filename
    
    def start_recording(self, freq_entry: FrequencyEntry) -> bool:
        """Start recording on a frequency."""
        try:
            self.recording_start_time = datetime.utcnow()
            chunk_path = self._get_chunk_path(freq_entry, 0)
            chunk_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Start rtl_fm
            rtl_fm_params = self._get_rtl_fm_params(freq_entry)
            logger.info(f"Starting rtl_fm: {' '.join(rtl_fm_params)}")
            
            self.rtl_fm_process = subprocess.Popen(
                ["nice", "-n", str(scanner_config.nice_level)] + rtl_fm_params,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Start ffmpeg with Opus encoding
            ffmpeg_params = [
                "nice", "-n", str(scanner_config.nice_level),
                "ionice", "-c", str(scanner_config.ionice_class),
                "ffmpeg",
                "-f", "s16le",
                "-ar", "48000",
                "-ac", "1",
                "-i", "-",  # Input from stdin
                "-threads", str(scanner_config.ffmpeg_threads),
                "-c:a", "libopus",
                "-b:a", f"{scanner_config.opus_bitrate_kbps}k",
                "-ac", "2",  # Stereo output
                "-f", "segment",
                "-segment_time", str(scanner_config.chunk_duration_seconds),
                "-segment_format", "ogg",
                "-reset_timestamps", "1",
                str(chunk_path).replace("_part000.ogg", "_part%03d.ogg")
            ]
            
            logger.info(f"Starting ffmpeg: {' '.join(ffmpeg_params)}")
            
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_params,
                stdin=self.rtl_fm_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.current_recording_path = chunk_path
            logger.info(f"Recording started: {freq_entry.freq_mhz} MHz -> {chunk_path.parent}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.stop_recording()
            return False
    
    def stop_recording(self) -> Optional[list[Path]]:
        """Stop recording and return list of chunk files."""
        chunk_files = []
        
        try:
            # Stop ffmpeg first (gracefully)
            if self.ffmpeg_process:
                try:
                    self.ffmpeg_process.terminate()
                    self.ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.ffmpeg_process.kill()
                    self.ffmpeg_process.wait()
                self.ffmpeg_process = None
            
            # Stop rtl_fm
            if self.rtl_fm_process:
                try:
                    self.rtl_fm_process.terminate()
                    self.rtl_fm_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.rtl_fm_process.kill()
                    self.rtl_fm_process.wait()
                self.rtl_fm_process = None
            
            # Find all chunk files
            if self.current_recording_path:
                pattern = self.current_recording_path.stem.rsplit('_part', 1)[0] + "_part*.ogg"
                chunk_files = sorted(self.current_recording_path.parent.glob(pattern))
                logger.info(f"Recording stopped: {len(chunk_files)} chunks created")
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
        
        finally:
            self.current_recording_path = None
            self.recording_start_time = None
        
        return chunk_files if chunk_files else None
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.rtl_fm_process is not None and self.rtl_fm_process.poll() is None

def assemble_session(chunk_files: list[Path], output_path: Path) -> bool:
    """Assemble chunks into a single session file."""
    try:
        if len(chunk_files) == 1:
            # Single chunk, just rename
            chunk_files[0].rename(output_path)
            logger.info(f"Single chunk session: {output_path}")
            return True
        
        # Multiple chunks, use ffmpeg concat
        concat_list = output_path.parent / f"concat_{output_path.stem}.txt"
        with open(concat_list, 'w') as f:
            for chunk in chunk_files:
                f.write(f"file '{chunk.absolute()}'\n")
        
        # Concat without re-encoding
        result = subprocess.run([
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path)
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            # Remove chunks and concat list
            for chunk in chunk_files:
                chunk.unlink()
            concat_list.unlink()
            logger.info(f"Session assembled: {output_path}")
            return True
        else:
            logger.error(f"Failed to assemble session: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"Error assembling session: {e}")
        return False
