"""Data models for SDR_app."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ModulationType(str, Enum):
    """Modulation types."""
    NFM = "nfm"  # Narrow FM
    FM = "fm"    # Wide FM
    WFM = "wfm"  # Broadcast FM
    AM = "am"    # Amplitude modulation
    USB = "usb"  # Upper sideband
    LSB = "lsb"  # Lower sideband

class FrequencyEntry(BaseModel):
    """A single frequency to scan."""
    freq_mhz: float = Field(..., description="Frequency in MHz")
    mode: ModulationType = Field(..., description="Modulation type")
    label: Optional[str] = Field(None, description="Optional label")
    ctcss: Optional[float] = Field(None, description="CTCSS tone in Hz")
    dcs: Optional[int] = Field(None, description="DCS code")

class FrequencyGroup(BaseModel):
    """A group of related frequencies."""
    name: str = Field(..., description="Group identifier")
    display_name: str = Field(..., description="Human-readable name")
    frequencies: List[FrequencyEntry] = Field(..., description="Frequencies in group")
    description: Optional[str] = Field(None, description="Group description")

class ScanStartRequest(BaseModel):
    """Request to start scanning."""
    frequency_groups: List[str] = Field(default_factory=list, description="Group names to scan")
    custom_frequencies: List[FrequencyEntry] = Field(default_factory=list, description="Additional frequencies")
    dwell_seconds: Optional[float] = Field(None, description="Override default dwell time")
    squelch_db: Optional[int] = Field(None, description="Override default squelch")

class Detection(BaseModel):
    """Active frequency detection."""
    freq_mhz: float = Field(..., description="Frequency in MHz")
    mode: ModulationType = Field(..., description="Modulation type")
    signal_strength_db: float = Field(..., description="Signal strength in dB")
    ctcss_tone: Optional[float] = Field(None, description="Detected CTCSS tone in Hz")
    dcs_code: Optional[int] = Field(None, description="Detected DCS code")
    label: Optional[str] = Field(None, description="Frequency label")
    first_seen: datetime = Field(..., description="First detection time")
    last_seen: datetime = Field(..., description="Last detection time")
    recording_id: Optional[str] = Field(None, description="Associated recording ID")

class Recording(BaseModel):
    """A recording session."""
    id: str = Field(..., description="Unique recording ID")
    freq_mhz: float = Field(..., description="Frequency in MHz")
    mode: ModulationType = Field(..., description="Modulation type")
    start_time: datetime = Field(..., description="Recording start time")
    end_time: Optional[datetime] = Field(None, description="Recording end time")
    duration_seconds: float = Field(..., description="Recording duration")
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="Relative file path")
    ctcss_tone: Optional[float] = Field(None, description="CTCSS tone if detected")
    dcs_code: Optional[int] = Field(None, description="DCS code if detected")
    label: Optional[str] = Field(None, description="Frequency label")

class ResourceUsage(BaseModel):
    """System resource usage."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    cpu_user: float = Field(..., description="User CPU percentage")
    cpu_system: float = Field(..., description="System CPU percentage")
    cpu_iowait: float = Field(..., description="IO wait percentage")
    memory_used_mb: float = Field(..., description="Used RAM in MB")
    memory_available_mb: float = Field(..., description="Available RAM in MB")
    memory_percent: float = Field(..., description="Memory usage percentage")
    swap_used_mb: float = Field(..., description="Used swap in MB")
    swap_total_mb: float = Field(..., description="Total swap in MB")
    swap_percent: float = Field(..., description="Swap usage percentage")
    disk_used_gb: float = Field(..., description="Used disk space in GB")
    disk_total_gb: float = Field(..., description="Total disk space in GB")
    disk_percent: float = Field(..., description="Disk usage percentage")
    recordings_size_gb: float = Field(..., description="Total recordings size in GB")

class SystemStatus(BaseModel):
    """Complete system status."""
    rtltcp_running: bool = Field(..., description="rtl_tcp service status")
    scanner_running: bool = Field(..., description="Scanner service status")
    scan_active: bool = Field(..., description="Active scan in progress")
    resources: ResourceUsage = Field(..., description="Resource usage")
    throttle_active: bool = Field(..., description="Throttle active")
    throttle_reason: Optional[str] = Field(None, description="Throttle reason")
    usb_errors: int = Field(0, description="USB error count")
    active_detections: int = Field(0, description="Number of active detections")
    total_recordings: int = Field(0, description="Total number of recordings")
    ip_address: str = Field(..., description="System IP address")

class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    dwell_seconds: Optional[float] = None
    squelch_db: Optional[int] = None
    chunk_duration_seconds: Optional[int] = None
    retention_days: Optional[int] = None
    storage_cap_gb: Optional[int] = None
    cpu_threshold: Optional[float] = None
    memory_threshold: Optional[float] = None
    io_wait_threshold: Optional[float] = None
