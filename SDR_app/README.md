# SDR_app - Raspberry Pi 2B Software Defined Radio Scanner

A comprehensive dual-dongle SDR scanner and recorder for Raspberry Pi 2B, optimized for resource-constrained operation.

## Hardware Requirements

- **Raspberry Pi 2B** running Raspberry Pi OS Bookworm 32-bit (Python 3.11.2)
- **SD Card Boot** with **USB SSD as root filesystem**
- **Powered USB Hub** with two RTL-SDR dongles:
  - Device 0: rtl_tcp server (network streaming)
  - Device 1: Scanner/recorder
- **Minimum 4GB swap** (created during installation)

## Baseline Resource Profile

Tested on fully updated Pi2B with GUI:
- RAM: 257 MB used, 660 MB cached, 80 MB free, 664 MB available
- CPU: 0.5% user, 99.2% idle
- Swap: 512 MB total, 13.4 MB used

All defaults are tuned to operate safely within these constraints.

## Features

### Frequency Coverage

Pre-configured frequency groups:
- **6M Ham Band**: 50-54 MHz (AM/SSB/FM)
- **2M Ham Band**: 144-148 MHz (FM/NFM)
- **1.25M Ham Band**: 219-225 MHz (FM/NFM)
- **70cm Ham Band**: 420-450 MHz (FM/NFM)
- **FM Broadcast**: 88-108 MHz (WFM)
- **Aircraft**: 118-137 MHz (AM)
- **GMRS**: 30 channels (462-467 MHz, NFM)
- **MURS**: 5 channels (151-154 MHz, NFM)
- **FRS**: 14 channels (462-467 MHz, NFM)
- **Marine VHF**: 156-163 MHz (NFM)
- **Weather Radio**: 7 NOAA channels (162 MHz, NFM)
- **Business Band**: 450-470 MHz (NFM)

### Scanner Capabilities

- Multi-group frequency scanning
- Automatic modulation detection (NFM/FM/WFM/AM)
- CTCSS/DCS privacy code detection
- Signal strength monitoring
- Active frequency recording
- Session assembly (30s chunks → 5min max sessions)
- 14-day retention with 60GB storage cap

### Web Interface

- **Responsive design** for PC, tablet, and phone
- **Main Dashboard**:
  - Real-time CPU/RAM/swap/disk usage
  - Scanner start/stop controls
  - Frequency group selection (dropdowns + custom entry)
  - Active detections table
  - Recent recordings browser
- **Advanced Settings**:
  - Scan parameters (dwell time, squelch)
  - Retention configuration
  - Throttle thresholds
  - System diagnostics

### Resource Management

**Conservative defaults for Pi2B**:
- Sample rates: 24kHz (NFM), 200kHz (WFM)
- Dwell time: 2 seconds per frequency
- Chunk size: 30 seconds
- Audio: Ogg Opus, 64 kbps stereo, 48 kHz (~240 KB per 30s chunk)
- Process priority: nice -n 19, ionice -c3
- ffmpeg: single-threaded, limited buffers
- Staggered service startup (10s delay)

**Adaptive throttling** activates when:
- CPU usage > 80%
- IO wait > 10%
- Swap usage increasing
- USB errors detected

**Throttle actions**:
- Increase dwell skip (scan fewer frequencies)
- Lengthen chunk interval (up to 60s)
- Reduce demod complexity
- Pause scanning temporarily

## Installation

### One-Command Install

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/SDR_app/main/install.sh | bash
```

### Manual Install

```bash
cd /home/pi
git clone https://github.com/YOUR_REPO/SDR_app.git
cd SDR_app
chmod +x install.sh
./install.sh
```

### Installation Process

1. **Interactive IP selection**: Detects LAN IP, allows override with availability check
2. **Swap creation**: Ensures 4GB swap file exists
3. **APT packages**: Two-pass install (build tools, then runtime deps)
4. **RTL-SDR udev rules**: Configures device permissions
5. **Kernel module blacklist**: Blacklists DVB-T drivers that conflict with RTL-SDR
6. **Node.js**: Installs Node 18.x LTS via NodeSource
7. **Python environment**: Creates venv, installs pinned packages with --prefer-binary
8. **React build**: Builds frontend, copies to backend/static, prunes artifacts
9. **Systemd services**: Installs and enables rtltcp.service and scanner.service
10. **Verification**: Checks service status, prints access URLs

**IMPORTANT**: After installation completes, **reboot the Pi** for kernel module blacklist to take effect:
```bash
sudo reboot
```

**Expected installation time**: 20-30 minutes on Pi2B

**Peak resource usage during install**:
- RAM: ~700 MB (with swap)
- Storage: ~1.5 GB temporary build files (pruned after)

## Usage

### Access URLs

After installation:
- **Web UI**: http://<your_pi_ip>:8080
- **rtl_tcp server**: <your_pi_ip>:1234 (for SDR++ and other clients)

### Service Management

```bash
# Check status
sudo systemctl status rtltcp
sudo systemctl status scanner

# View logs
journalctl -u rtltcp -n 50
journalctl -u scanner -n 50

# Restart services
sudo systemctl restart rtltcp
sudo systemctl restart scanner

# View application logs
tail -f /home/pi/SDR_app/logs/backend.log
tail -f /home/pi/SDR_app/logs/scanner.log
tail -f /home/pi/SDR_app/logs/rtltcp.log
```

### Log Rotation

Logs are automatically rotated:
- Max file size: 5 MB
- Retention: Last 50 files per log
- Location: /home/pi/SDR_app/logs/

### Storage Pruning

Automatic daily pruning via systemd timer:
- Removes recordings older than 14 days
- Enforces 60 GB storage cap
- Logs to /home/pi/SDR_app/logs/prune.log

```bash
# Manual prune
/home/pi/SDR_app/scripts/prune_storage.sh

# Check prune schedule
systemctl list-timers | grep sdr-prune
```

## Diagnostics

### Run Diagnostics Script

```bash
/home/pi/SDR_app/scripts/diagnostics.sh
```

Checks:
- RTL-SDR dongle detection (device 0 and 1)
- rtl_test on both devices
- ffmpeg version and codec support
- Test 10s audio capture
- Service status
- Disk usage

### Test Dongles Manually

```bash
# Test device 0
rtl_test -d 0 -t 5

# Test device 1
rtl_test -d 1 -t 5

# Test rtl_tcp connection
telnet <your_pi_ip> 1234
```

### View USB Errors

```bash
# Check dmesg for USB errors
sudo dmesg | grep -i usb | tail -20

# Monitor USB in real-time
sudo dmesg -w | grep -i usb
```

### Test Audio Pipeline

```bash
# Capture 10 seconds on 146.52 MHz (2M calling frequency)
rtl_fm -d 1 -f 146.52M -M fm -s 24k -r 48k -g 40 - | \
  ffmpeg -f s16le -ar 48k -ac 1 -i - -t 10 -c:a libopus -b:a 64k /tmp/test.ogg

# Play with VLC or ffplay
ffplay /tmp/test.ogg
```

## Troubleshooting

### Services Won't Start

```bash
# Check service failures
sudo systemctl status rtltcp --no-pager -l
sudo systemctl status scanner --no-pager -l

# View detailed logs
journalctl -u rtltcp --no-pager -n 100
journalctl -u scanner --no-pager -n 100

# Check for dongle detection
lsusb | grep Realtek
```

### High CPU/Memory Usage

```bash
# Check resource usage
htop

# View scanner throttle status via API
curl http://localhost:8080/api/status

# Adjust throttle thresholds in Web UI → Advanced Settings
```

### USB Bus Saturation

If experiencing USB errors or stuttering:

1. Verify powered USB hub is used
2. Increase scan dwell time (Advanced Settings)
3. Reduce number of frequency groups scanned
4. Check for USB errors: `dmesg | grep -i 'usb\|rtl'`
5. Lower sample rates if needed (edit /home/pi/SDR_app/backend/app/frequency_groups.py)

### No Audio in Recordings

```bash
# Test rtl_fm manually
rtl_fm -d 1 -f 146.52M -M fm -s 24k -r 48k -g 40 - | aplay -r 48k -f S16_LE

# Check ffmpeg opus support
ffmpeg -codecs | grep opus

# Verify sox installation
sox --version
```

### Network/IP Issues

```bash
# Check current IP
hostname -I

# View static IP configuration
cat /etc/dhcpcd.conf

# Reconfigure IP (edit and restart)
sudo nano /etc/dhcpcd.conf
sudo systemctl restart dhcpcd
```

## File Size Estimates

- **30s chunk**: ~240 KB (64 kbps stereo Opus)
- **5min session**: ~2.4 MB (10 chunks)
- **1 hour recording**: ~28 MB
- **60 GB storage**: ~2,140 hours of recording

## Configuration Files

- **Backend config**: /home/pi/SDR_app/backend/app/config.py
- **Frequency groups**: /home/pi/SDR_app/backend/app/frequency_groups.py
- **Logging**: /home/pi/SDR_app/backend/logging.ini
- **Systemd units**: /etc/systemd/system/rtltcp.service, scanner.service

## API Reference

### GET /api/status
Returns system status, resource usage, throttle state

### POST /api/scanner/start
Body: `{"frequency_groups": ["2M_HAM", "GMRS"], "custom_frequencies": [{"freq": 146.52, "mode": "fm"}]}`

### POST /api/scanner/stop
Stops active scan

### GET /api/recordings
Lists all recording sessions

### GET /api/recordings/{id}
Downloads recording file

### DELETE /api/recordings/{id}
Deletes recording

### GET /api/logs?name=backend&lines=100
Returns log tail

### GET /api/frequency-groups
Returns all available frequency groups

### GET /api/detections
Returns active frequency detections with CTCSS/DCS

## Advanced Tuning

For experienced users:

1. **Edit frequency groups**: /home/pi/SDR_app/backend/app/frequency_groups.py
2. **Adjust resource thresholds**: Backend config or via Web UI
3. **Modify audio pipeline**: /home/pi/SDR_app/backend/app/scanner/audio_pipeline.py
4. **Change sample rates**: Frequency group definitions
5. **Custom scan patterns**: Scanner engine logic

## Development

```bash
# Activate venv
source /home/pi/SDR_app/venv/bin/activate

# Run backend manually (for debugging)
cd /home/pi/SDR_app
uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload

# Frontend development
cd /home/pi/SDR_app/server
npm run dev
```

## License

MIT License - Use freely, attribution appreciated.

## Credits

Built for the ham radio and SDR community. Uses rtl-sdr, ffmpeg, FastAPI, React, and other excellent open-source tools.

## Support

For issues, please provide:
1. Output of /home/pi/SDR_app/scripts/diagnostics.sh
2. Relevant logs from /home/pi/SDR_app/logs/
3. `dmesg | grep -i usb` output if USB-related

73 de SDR_app!
