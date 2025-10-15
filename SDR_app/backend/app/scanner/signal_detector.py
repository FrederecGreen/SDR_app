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
        
        Uses rtl_power for quick power measurement.
        """
        try:
            freq_hz = int(freq_entry.freq_mhz * 1e6)
            
            # Use rtl_power for quick scan
            # Scan narrow range around frequency for 0.1 seconds
            result = subprocess.run([
                "rtl_power",
                "-d", str(scanner_config.scanner_device),
                "-f", f"{freq_hz}:{freq_hz}:1k",  # Single bin
                "-i", "0.1",  # 100ms integration
                "-1",  # Single shot
                "-",  # Output to stdout
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout:
                # Parse rtl_power output
                # Format: date, time, hz_low, hz_high, hz_step, samples, dB, dB, ...
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[-1].split(',')
                    if len(parts) >= 7:
                        # Get power measurement (7th field onward)
                        power_values = [float(p.strip()) for p in parts[6:] if p.strip()]
                        if power_values:
                            avg_power = sum(power_values) / len(power_values)
                            
                            # Simple threshold: signal if power > noise floor + squelch
                            threshold = self.noise_floor_db + (scanner_config.default_squelch_db / 2)
                            has_signal = avg_power > threshold
                            
                            return has_signal, avg_power
            
            # Fallback: assume no signal
            return False, self.noise_floor_db
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Signal detection timeout on {freq_entry.freq_mhz} MHz")
            return False, self.noise_floor_db
        except Exception as e:
            logger.error(f"Signal detection error on {freq_entry.freq_mhz} MHz: {e}")
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
