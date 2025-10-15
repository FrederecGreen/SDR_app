"""Frequency group definitions for SDR scanner."""
from typing import Dict, List
from backend.app.models import FrequencyGroup, FrequencyEntry, ModulationType

# GMRS Channels (462-467 MHz)
GMRS_CHANNELS = [
    FrequencyEntry(freq_mhz=462.5625, mode=ModulationType.NFM, label="GMRS 1"),
    FrequencyEntry(freq_mhz=462.5875, mode=ModulationType.NFM, label="GMRS 2"),
    FrequencyEntry(freq_mhz=462.6125, mode=ModulationType.NFM, label="GMRS 3"),
    FrequencyEntry(freq_mhz=462.6375, mode=ModulationType.NFM, label="GMRS 4"),
    FrequencyEntry(freq_mhz=462.6625, mode=ModulationType.NFM, label="GMRS 5"),
    FrequencyEntry(freq_mhz=462.6875, mode=ModulationType.NFM, label="GMRS 6"),
    FrequencyEntry(freq_mhz=462.7125, mode=ModulationType.NFM, label="GMRS 7"),
    FrequencyEntry(freq_mhz=467.5625, mode=ModulationType.NFM, label="GMRS 8"),
    FrequencyEntry(freq_mhz=467.5875, mode=ModulationType.NFM, label="GMRS 9"),
    FrequencyEntry(freq_mhz=467.6125, mode=ModulationType.NFM, label="GMRS 10"),
    FrequencyEntry(freq_mhz=467.6375, mode=ModulationType.NFM, label="GMRS 11"),
    FrequencyEntry(freq_mhz=467.6625, mode=ModulationType.NFM, label="GMRS 12"),
    FrequencyEntry(freq_mhz=467.6875, mode=ModulationType.NFM, label="GMRS 13"),
    FrequencyEntry(freq_mhz=467.7125, mode=ModulationType.NFM, label="GMRS 14"),
    # Repeater inputs
    FrequencyEntry(freq_mhz=462.550, mode=ModulationType.NFM, label="GMRS 15 (RPT)"),
    FrequencyEntry(freq_mhz=462.575, mode=ModulationType.NFM, label="GMRS 16 (RPT)"),
    FrequencyEntry(freq_mhz=462.600, mode=ModulationType.NFM, label="GMRS 17 (RPT)"),
    FrequencyEntry(freq_mhz=462.625, mode=ModulationType.NFM, label="GMRS 18 (RPT)"),
    FrequencyEntry(freq_mhz=462.650, mode=ModulationType.NFM, label="GMRS 19 (RPT)"),
    FrequencyEntry(freq_mhz=462.675, mode=ModulationType.NFM, label="GMRS 20 (RPT)"),
    FrequencyEntry(freq_mhz=462.700, mode=ModulationType.NFM, label="GMRS 21 (RPT)"),
    FrequencyEntry(freq_mhz=462.725, mode=ModulationType.NFM, label="GMRS 22 (RPT)"),
    # Repeater outputs
    FrequencyEntry(freq_mhz=467.550, mode=ModulationType.NFM, label="GMRS 15 OUT"),
    FrequencyEntry(freq_mhz=467.575, mode=ModulationType.NFM, label="GMRS 16 OUT"),
    FrequencyEntry(freq_mhz=467.600, mode=ModulationType.NFM, label="GMRS 17 OUT"),
    FrequencyEntry(freq_mhz=467.625, mode=ModulationType.NFM, label="GMRS 18 OUT"),
    FrequencyEntry(freq_mhz=467.650, mode=ModulationType.NFM, label="GMRS 19 OUT"),
    FrequencyEntry(freq_mhz=467.675, mode=ModulationType.NFM, label="GMRS 20 OUT"),
    FrequencyEntry(freq_mhz=467.700, mode=ModulationType.NFM, label="GMRS 21 OUT"),
    FrequencyEntry(freq_mhz=467.725, mode=ModulationType.NFM, label="GMRS 22 OUT"),
]

# MURS Channels (151-154 MHz)
MURS_CHANNELS = [
    FrequencyEntry(freq_mhz=151.820, mode=ModulationType.NFM, label="MURS 1"),
    FrequencyEntry(freq_mhz=151.880, mode=ModulationType.NFM, label="MURS 2"),
    FrequencyEntry(freq_mhz=151.940, mode=ModulationType.NFM, label="MURS 3"),
    FrequencyEntry(freq_mhz=154.570, mode=ModulationType.NFM, label="MURS 4"),
    FrequencyEntry(freq_mhz=154.600, mode=ModulationType.NFM, label="MURS 5"),
]

# FRS Channels (462-467 MHz, overlaps with GMRS)
FRS_CHANNELS = [
    FrequencyEntry(freq_mhz=462.5625, mode=ModulationType.NFM, label="FRS 1"),
    FrequencyEntry(freq_mhz=462.5875, mode=ModulationType.NFM, label="FRS 2"),
    FrequencyEntry(freq_mhz=462.6125, mode=ModulationType.NFM, label="FRS 3"),
    FrequencyEntry(freq_mhz=462.6375, mode=ModulationType.NFM, label="FRS 4"),
    FrequencyEntry(freq_mhz=462.6625, mode=ModulationType.NFM, label="FRS 5"),
    FrequencyEntry(freq_mhz=462.6875, mode=ModulationType.NFM, label="FRS 6"),
    FrequencyEntry(freq_mhz=462.7125, mode=ModulationType.NFM, label="FRS 7"),
    FrequencyEntry(freq_mhz=467.5625, mode=ModulationType.NFM, label="FRS 8"),
    FrequencyEntry(freq_mhz=467.5875, mode=ModulationType.NFM, label="FRS 9"),
    FrequencyEntry(freq_mhz=467.6125, mode=ModulationType.NFM, label="FRS 10"),
    FrequencyEntry(freq_mhz=467.6375, mode=ModulationType.NFM, label="FRS 11"),
    FrequencyEntry(freq_mhz=467.6625, mode=ModulationType.NFM, label="FRS 12"),
    FrequencyEntry(freq_mhz=467.6875, mode=ModulationType.NFM, label="FRS 13"),
    FrequencyEntry(freq_mhz=467.7125, mode=ModulationType.NFM, label="FRS 14"),
]

# Weather Radio Channels
WEATHER_CHANNELS = [
    FrequencyEntry(freq_mhz=162.400, mode=ModulationType.NFM, label="WX 1"),
    FrequencyEntry(freq_mhz=162.425, mode=ModulationType.NFM, label="WX 2"),
    FrequencyEntry(freq_mhz=162.450, mode=ModulationType.NFM, label="WX 3"),
    FrequencyEntry(freq_mhz=162.475, mode=ModulationType.NFM, label="WX 4"),
    FrequencyEntry(freq_mhz=162.500, mode=ModulationType.NFM, label="WX 5"),
    FrequencyEntry(freq_mhz=162.525, mode=ModulationType.NFM, label="WX 6"),
    FrequencyEntry(freq_mhz=162.550, mode=ModulationType.NFM, label="WX 7"),
]

def generate_ham_2m() -> List[FrequencyEntry]:
    """Generate 2M ham band frequencies (144-148 MHz)."""
    freqs = []
    # Calling frequencies and popular simplex
    simplex_freqs = [146.40, 146.43, 146.46, 146.49, 146.52, 146.55, 146.58]
    for f in simplex_freqs:
        freqs.append(FrequencyEntry(freq_mhz=f, mode=ModulationType.FM, label=f"2M {f} MHz"))
    
    # Common repeater outputs (every 20 kHz from 145.1 to 145.5)
    for f in range(1451, 1451 + 21, 2):  # 145.1 to 145.5 in 20 kHz steps
        freq_mhz = f / 10.0
        freqs.append(FrequencyEntry(freq_mhz=freq_mhz, mode=ModulationType.FM, label=f"2M RPT {freq_mhz}"))
    
    return freqs

def generate_ham_70cm() -> List[FrequencyEntry]:
    """Generate 70cm ham band frequencies (420-450 MHz)."""
    freqs = []
    # Common simplex frequencies
    simplex_freqs = [446.0, 446.5, 447.0, 147.5]
    for f in simplex_freqs:
        freqs.append(FrequencyEntry(freq_mhz=f, mode=ModulationType.NFM, label=f"70cm {f} MHz"))
    
    # Repeater outputs (440-445 MHz, every 25 kHz)
    for f in range(44000, 44501, 25):  # 440.0 to 445.0 in 25 kHz steps
        freq_mhz = f / 100.0
        if freq_mhz % 1.0 == 0 or freq_mhz % 0.5 == 0:  # Sample every 500 kHz
            freqs.append(FrequencyEntry(freq_mhz=freq_mhz, mode=ModulationType.NFM, label=f"70cm RPT {freq_mhz}"))
    
    return freqs

def generate_ham_1_25m() -> List[FrequencyEntry]:
    """Generate 1.25M ham band frequencies (219-225 MHz)."""
    freqs = []
    # Sample every 500 kHz
    for f in range(2190, 2251, 5):  # 219.0 to 225.0 in 500 kHz steps
        freq_mhz = f / 10.0
        freqs.append(FrequencyEntry(freq_mhz=freq_mhz, mode=ModulationType.NFM, label=f"1.25M {freq_mhz}"))
    return freqs

def generate_ham_6m() -> List[FrequencyEntry]:
    """Generate 6M ham band frequencies (50-54 MHz)."""
    freqs = []
    # Common calling and simplex frequencies
    simplex_freqs = [50.125, 50.200, 51.0, 52.0, 53.0]
    for f in simplex_freqs:
        freqs.append(FrequencyEntry(freq_mhz=f, mode=ModulationType.FM, label=f"6M {f} MHz"))
    return freqs

def generate_aircraft() -> List[FrequencyEntry]:
    """Generate aircraft band frequencies (118-137 MHz)."""
    freqs = []
    # Sample every 1 MHz (aircraft uses AM)
    for f in range(118, 138):
        freqs.append(FrequencyEntry(freq_mhz=float(f), mode=ModulationType.AM, label=f"AIR {f} MHz"))
    # Add guard frequency
    freqs.append(FrequencyEntry(freq_mhz=121.5, mode=ModulationType.AM, label="AIR Emergency"))
    return freqs

def generate_marine() -> List[FrequencyEntry]:
    """Generate marine VHF frequencies (156-163 MHz)."""
    freqs = []
    # Key channels
    channels = {
        156.800: "Ch 16 (Distress)",
        156.300: "Ch 06 (Safety)",
        156.650: "Ch 13 (Bridge)",
        156.450: "Ch 09 (Calling)",
    }
    for freq, label in channels.items():
        freqs.append(FrequencyEntry(freq_mhz=freq, mode=ModulationType.NFM, label=label))
    
    # Sample other marine channels every 500 kHz
    for f in range(1560, 1631, 5):
        freq_mhz = f / 10.0
        if freq_mhz not in channels:
            freqs.append(FrequencyEntry(freq_mhz=freq_mhz, mode=ModulationType.NFM, label=f"Marine {freq_mhz}"))
    return freqs

def generate_fm_broadcast() -> List[FrequencyEntry]:
    """Generate FM broadcast frequencies (88-108 MHz)."""
    freqs = []
    # Sample every 400 kHz (broadcast uses WFM)
    for f in range(880, 1081, 4):
        freq_mhz = f / 10.0
        freqs.append(FrequencyEntry(freq_mhz=freq_mhz, mode=ModulationType.WFM, label=f"FM {freq_mhz}"))
    return freqs

def generate_business_band() -> List[FrequencyEntry]:
    """Generate business band frequencies (450-470 MHz)."""
    freqs = []
    # Sample every 1 MHz
    for f in range(450, 471):
        freqs.append(FrequencyEntry(freq_mhz=float(f), mode=ModulationType.NFM, label=f"Business {f} MHz"))
    return freqs

# Define all frequency groups
FREQUENCY_GROUPS: Dict[str, FrequencyGroup] = {
    "GMRS": FrequencyGroup(
        name="GMRS",
        display_name="GMRS (General Mobile Radio Service)",
        frequencies=GMRS_CHANNELS,
        description="30 GMRS channels including repeaters (462-467 MHz)"
    ),
    "MURS": FrequencyGroup(
        name="MURS",
        display_name="MURS (Multi-Use Radio Service)",
        frequencies=MURS_CHANNELS,
        description="5 MURS channels (151-154 MHz)"
    ),
    "FRS": FrequencyGroup(
        name="FRS",
        display_name="FRS (Family Radio Service)",
        frequencies=FRS_CHANNELS,
        description="14 FRS channels (462-467 MHz)"
    ),
    "WEATHER": FrequencyGroup(
        name="WEATHER",
        display_name="NOAA Weather Radio",
        frequencies=WEATHER_CHANNELS,
        description="7 NOAA weather channels (162 MHz)"
    ),
    "2M_HAM": FrequencyGroup(
        name="2M_HAM",
        display_name="2M Ham Band (144-148 MHz)",
        frequencies=generate_ham_2m(),
        description="2 meter amateur radio band"
    ),
    "70CM_HAM": FrequencyGroup(
        name="70CM_HAM",
        display_name="70cm Ham Band (420-450 MHz)",
        frequencies=generate_ham_70cm(),
        description="70 centimeter amateur radio band"
    ),
    "1_25M_HAM": FrequencyGroup(
        name="1_25M_HAM",
        display_name="1.25M Ham Band (219-225 MHz)",
        frequencies=generate_ham_1_25m(),
        description="1.25 meter amateur radio band"
    ),
    "6M_HAM": FrequencyGroup(
        name="6M_HAM",
        display_name="6M Ham Band (50-54 MHz)",
        frequencies=generate_ham_6m(),
        description="6 meter amateur radio band"
    ),
    "AIRCRAFT": FrequencyGroup(
        name="AIRCRAFT",
        display_name="Aircraft Band (118-137 MHz)",
        frequencies=generate_aircraft(),
        description="Aviation communications (AM)"
    ),
    "MARINE": FrequencyGroup(
        name="MARINE",
        display_name="Marine VHF (156-163 MHz)",
        frequencies=generate_marine(),
        description="Marine VHF radio channels"
    ),
    "FM_BROADCAST": FrequencyGroup(
        name="FM_BROADCAST",
        display_name="FM Broadcast (88-108 MHz)",
        frequencies=generate_fm_broadcast(),
        description="Commercial FM radio broadcast band"
    ),
    "BUSINESS": FrequencyGroup(
        name="BUSINESS",
        display_name="Business Band (450-470 MHz)",
        frequencies=generate_business_band(),
        description="Business and industrial frequencies"
    ),
}

def get_all_groups() -> Dict[str, FrequencyGroup]:
    """Return all frequency groups."""
    return FREQUENCY_GROUPS

def get_group(name: str) -> FrequencyGroup:
    """Get a specific frequency group by name."""
    return FREQUENCY_GROUPS[name]
