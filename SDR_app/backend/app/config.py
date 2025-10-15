"""Configuration for SDR_app."""
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

# Base paths
BASE_DIR = Path("/home/pi/SDR_app")
LOGS_DIR = BASE_DIR / "logs"
RECORDINGS_DIR = BASE_DIR / "recordings"
STATIC_DIR = BASE_DIR / "backend" / "static"

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

class ResourceThresholds(BaseModel):
    """Resource monitoring thresholds for adaptive throttling."""
    cpu_percent_max: float = 80.0  # CPU usage > 80% triggers throttle
    io_wait_percent_max: float = 10.0  # IO wait > 10% triggers throttle
    swap_growth_mb_max: float = 50.0  # Swap increase > 50MB triggers throttle
    memory_percent_max: float = 85.0  # Memory usage > 85% triggers throttle
    usb_error_count_max: int = 10  # USB errors > 10 triggers throttle
    hysteresis_seconds: int = 30  # Wait 30s before reverting throttle

class ScannerConfig(BaseModel):
    """Scanner configuration parameters."""
    # Device assignment
    rtl_tcp_device: int = 0  # Device 0 for rtl_tcp server
    scanner_device: int = 1  # Device 1 for scanning
    
    # Scan parameters
    default_dwell_seconds: float = 2.0  # Time to listen per frequency
    default_squelch_db: int = 40  # Squelch level (0-100)
    scan_delay_seconds: float = 0.1  # Delay between frequency hops
    
    # Audio parameters
    chunk_duration_seconds: int = 30  # Duration of each audio chunk
    max_session_duration_seconds: int = 300  # Max 5 minutes per session
    opus_bitrate_kbps: int = 64  # Opus bitrate (64 kbps stereo)
    opus_sample_rate: int = 48000  # Output sample rate
    
    # Recording settings
    min_signal_duration_seconds: float = 1.0  # Minimum signal to record
    signal_timeout_seconds: float = 5.0  # Max silence before stopping record
    
    # Storage management
    retention_days: int = 14  # Keep recordings for 14 days
    storage_cap_gb: int = 60  # Maximum storage for recordings
    
    # Resource management
    nice_level: int = 19  # Process nice level (lower priority)
    ionice_class: int = 3  # IO scheduling class (idle)
    ffmpeg_threads: int = 1  # Single-threaded ffmpeg
    
    # Service startup
    scanner_startup_delay_seconds: int = 10  # Wait after rtltcp starts

class ThrottleState(BaseModel):
    """Current throttle state."""
    active: bool = False
    reason: Optional[str] = None
    dwell_multiplier: float = 1.0  # Multiply dwell time by this
    chunk_duration_seconds: int = 30  # Can increase to 60s when throttled
    skip_frequencies: int = 0  # Skip every N frequencies
    paused: bool = False  # Completely pause scanning

# Global configuration instances
resource_thresholds = ResourceThresholds()
scanner_config = ScannerConfig()
throttle_state = ThrottleState()

# RTL-SDR hardware limits for Pi2B
RTL_SDR_MIN_FREQ_MHZ = 24
RTL_SDR_MAX_FREQ_MHZ = 1766

# API configuration
API_TITLE = "SDR_app API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Raspberry Pi 2B dual-dongle SDR scanner and recorder"
