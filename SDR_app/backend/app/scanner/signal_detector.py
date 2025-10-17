"""Signal detection using rtl_power or simple squelch-based detection."""
import subprocess
import logging
import re
import os
import signal
import time
from backend.app.config import scanner_config
from backend.app.models import FrequencyEntry

logger = logging.getLogger("scanner")

class SignalDetector:
    """Detect signals on frequencies."""
    
    def __init__(self):
        self.noise_floor_db = -50  # Typical noise floor
    
    def detect_signal(self, freq_entry: FrequencyEntry) -> tuple[bool, float]:
        """Detect if signal is present on frequency.
        
        Returns: (has_signal, signal_strength_db)
        
        Uses rtl_fm with squelch-based detection (more reliable than rtl_power).
        """
        try:
            freq_hz = int(freq_entry.freq_mhz * 1e6)
            
            # Determine sample rate based on modulation
            if freq_entry.mode.value == "wfm":
                sample_rate = "200k"
                mode = "wbfm"
            elif freq_entry.mode.value == "am":
                sample_rate = "24k"
                mode = "am"
            else:  # fm, nfm
                sample_rate = "24k"
                mode = "fm"
            
            logger.info(f"Scanning {freq_entry.freq_mhz} MHz (mode: {mode}, rate: {sample_rate}, squelch: {scanner_config.default_squelch_db})")
            
            # Use rtl_fm with squelch for quick signal detection
            # Run in background to avoid blocking, kill after timeout
            cmd = [
                "rtl_fm",
                "-d", str(scanner_config.scanner_device),
                "-f", str(freq_hz),
                "-M", mode,
                "-s", sample_rate,
                "-l", str(scanner_config.default_squelch_db),  # Squelch level
                "-g", "40",  # Fixed gain
                "-E", "dc",  # DC blocking
                "-"
            ]
            
            logger.debug(f"Running: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create process group for cleanup
            )
            
            # Read output for 1 second
            import time
            start_time = time.time()
            output_data = b""
            
            while time.time() - start_time < 1.0:
                try:
                    chunk = process.stdout.read(4096)
                    if chunk:
                        output_data += chunk
                    else:
                        break
                except:
                    break
            
            # Kill process and wait
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=1)
            except:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    process.wait(timeout=1)
                except:
                    pass
            
            # Check stderr for errors
            stderr_output = ""
            if process.stderr:
                try:
                    stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
                    if stderr_output and len(stderr_output) > 0:
                        logger.debug(f"rtl_fm stderr: {stderr_output[:200]}")
                except:
                    pass
            
            output_size = len(output_data)
            
            # If we got significant audio output, signal is present
            # FM broadcasts produce lots of data even with squelch
            # Threshold: >5KB indicates signal (FM broadcast produces 24KB/sec at 24kHz sample rate)
            has_signal = output_size > 5000
            
            if has_signal:
                # Estimate signal strength based on output size
                estimated_strength = -40.0 + (output_size / 10000)
                logger.info(f"✓ SIGNAL DETECTED: {freq_entry.freq_mhz} MHz - {output_size} bytes (~{estimated_strength:.1f}dB)")
                return True, estimated_strength
            else:
                logger.debug(f"✗ No signal: {freq_entry.freq_mhz} MHz ({output_size} bytes)")
                return False, self.noise_floor_db
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Signal detection timeout on {freq_entry.freq_mhz} MHz")
            return False, self.noise_floor_db
        except Exception as e:
            logger.error(f"Signal detection error on {freq_entry.freq_mhz} MHz: {e}", exc_info=True)
            return False, self.noise_floor_db
    
    def detect_ctcss(self, audio_chunk_path: str) -> float:
        """Detect CTCSS tone from audio file.
        
        Returns: CTCSS tone in Hz, or None if not detected.
        
        Uses sox to analyze low frequencies for CTCSS (67-254 Hz).
        """
        try:
            # Use sox to get spectral analysis of low frequencies
            result = subprocess.run([
                "sox",
                audio_chunk_path,
                "-n",
                "stat",
                "-freq"
            ], capture_output=True, text=True, timeout=5)
            
            # Parse output for dominant frequency in CTCSS range
            # This is a simplified implementation
            # A more robust implementation would use multimon-ng
            
            if result.stderr:
                # Look for frequency information in stderr (sox outputs to stderr)
                freq_match = re.search(r'Rough frequency:\s+(\d+)', result.stderr)
                if freq_match:
                    freq = float(freq_match.group(1))
                    if 67 <= freq <= 254:  # CTCSS range
                        return freq
            
            return None
            
        except Exception as e:
            logger.debug(f"CTCSS detection error: {e}")
            return None
