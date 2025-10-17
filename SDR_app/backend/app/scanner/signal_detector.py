"""Signal detection using rtl_power or simple squelch-based detection."""
import subprocess
import logging
import re
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
            
            logger.debug(f"Detecting signal on {freq_entry.freq_mhz} MHz ({mode}, {sample_rate})")
            
            # Use rtl_fm with squelch for quick signal detection
            # This is more reliable than rtl_power on Pi2B
            result = subprocess.run([
                "timeout", "1",  # 1 second max
                "rtl_fm",
                "-d", str(scanner_config.scanner_device),
                "-f", str(freq_hz),
                "-M", mode,
                "-s", sample_rate,
                "-l", str(scanner_config.default_squelch_db),  # Squelch level
                "-E", "dc",  # DC blocking
                "-"
            ], capture_output=True, text=False, timeout=2)
            
            # Check if rtl_fm produced output (signal present)
            # If squelch opens, rtl_fm outputs audio samples
            output_size = len(result.stdout) if result.stdout else 0
            
            # If we got significant audio output, signal is present
            # Typical: silence = 0 bytes, signal = thousands of bytes in 1 second
            has_signal = output_size > 5000  # At least 5KB of audio data
            
            if has_signal:
                # Estimate signal strength based on output size
                # This is rough but works for presence detection
                estimated_strength = -40.0 + (output_size / 10000)  # Rough estimate
                logger.info(f"Signal detected on {freq_entry.freq_mhz} MHz: {output_size} bytes, ~{estimated_strength:.1f}dB")
                return True, estimated_strength
            else:
                logger.debug(f"No signal on {freq_entry.freq_mhz} MHz (output: {output_size} bytes)")
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
