# SDR_app Quick Start Guide

## 60-Second Setup

```bash
# 1. Transfer SDR_app to your Raspberry Pi 2B
cd /home/pi
git clone <YOUR_REPO_URL> SDR_app

# 2. Run installer
cd SDR_app
chmod +x install.sh
./install.sh

# 3. Follow interactive prompts for IP selection
# Installation takes ~20-30 minutes on Pi2B

# 4. Access Web UI
# Open browser to: http://<YOUR_PI_IP>:8080
```

## First Scan

1. Open Web UI: `http://<YOUR_PI_IP>:8080`
2. Navigate to **Scanner** tab
3. Select frequency groups (e.g., "2M Ham Band", "GMRS")
4. Click **Start Scan**
5. Watch **Active Detections** appear in real-time
6. Navigate to **Recordings** tab to download captures

## rtl_tcp Server

The rtl_tcp server (device 0) runs automatically on port 1234.

**Connect from SDR++ / GQRX:**
- Server: `<YOUR_PI_IP>`
- Port: `1234`
- Sample Rate: Use SDR++ defaults

## Key Features

### Frequency Groups
- **Ham Radio:** 6M, 2M, 1.25M, 70cm bands
- **Public Safety:** GMRS (30 channels), MURS (5 channels), FRS (14 channels)
- **Weather:** NOAA Weather Radio (7 channels)
- **Aviation:** Aircraft band (118-137 MHz)
- **Marine:** Marine VHF (156-163 MHz)
- **Broadcast:** FM radio (88-108 MHz)
- **Custom:** Add any frequency 24-1766 MHz

### Recording
- **Automatic:** Records when signal detected
- **Format:** Ogg Opus, 64 kbps stereo, 48 kHz
- **Chunks:** 30-second segments, assembled into 5-minute sessions
- **Size:** ~240 KB per 30 seconds (~2.4 MB per 5 minutes)
- **Storage:** 14-day retention, 60 GB cap (configurable)

### Resource Management
- **Adaptive Throttling:** Automatically reduces scan rate when CPU/IO high
- **Conservative Defaults:** Tuned for Pi2B baseline (257 MB RAM used, 0.5% CPU)
- **Real-time Monitoring:** Dashboard shows CPU, RAM, swap, disk usage
- **USB Protection:** Throttles to prevent USB bus saturation

## Essential Commands

```bash
# Check service status
sudo systemctl status rtltcp scanner

# View logs
tail -f /home/pi/SDR_app/logs/backend.log
tail -f /home/pi/SDR_app/logs/scanner.log

# Restart services
sudo systemctl restart rtltcp scanner

# Run diagnostics
/home/pi/SDR_app/scripts/diagnostics.sh

# Manual storage prune
/home/pi/SDR_app/scripts/prune_storage.sh
```

## Troubleshooting

### No Detections

**Check:**
1. Both dongles connected to powered USB hub
2. Services running: `sudo systemctl status rtltcp scanner`
3. Correct frequency groups selected
4. Squelch level (try lowering in Settings)

### USB Errors

**Fix:**
1. Use powered USB hub (required!)
2. Reduce scan rate: Settings → increase dwell time
3. Scan fewer frequency groups
4. Check USB errors: `dmesg | grep -i usb`

### High CPU Usage

**Throttle triggers automatically when:**
- CPU > 80%
- IO wait > 10%
- Swap usage increasing
- USB errors detected

**Manual adjustment:**
- Settings → increase dwell time
- Settings → increase CPU threshold
- Scan fewer frequencies

### Services Not Starting

```bash
# Check detailed logs
journalctl -u rtltcp -n 50
journalctl -u scanner -n 50

# Verify dongles detected
lsusb | grep Realtek

# Check ports available
sudo netstat -tulpn | grep 8080
sudo netstat -tulpn | grep 1234

# Restart if needed
sudo systemctl restart rtltcp scanner
```

## Tuning for Your Environment

### High Activity Area (Lots of Signals)

Settings → Advanced:
- Increase **Chunk Duration** to 45-60 seconds
- Increase **Dwell Time** to 3-4 seconds
- Lower **CPU Threshold** to 70%

### Low Activity Area (Few Signals)

Settings → Advanced:
- Decrease **Dwell Time** to 1.0 seconds
- Keep default **Chunk Duration** (30 seconds)
- Scan more frequency groups

### Limited Storage

Settings → Advanced:
- Decrease **Retention Days** to 7
- Decrease **Storage Cap** to 30 GB

### Maximize Recording Quality

Settings → Advanced:
- Increase **Chunk Duration** to 60 seconds
- Increase **Squelch** to filter weak signals
- Focus on specific frequency groups

## Web UI Overview

### Dashboard Tab
- System status (services, scan state)
- Resource monitors (CPU, RAM, swap, disk)
- Throttle warnings
- Active detection count

### Scanner Tab
- Frequency group selection
- Custom frequency entry
- Start/stop controls
- Live detection table

### Recordings Tab
- Browse all recordings
- Download/delete files
- Recording metadata (freq, duration, size, CTCSS/DCS)

### Settings Tab
- Scanner parameters (dwell, squelch, chunk size)
- Storage management (retention, cap)
- Throttle thresholds (CPU, memory, IO)
- System logs viewer

## Performance Expectations

**Pi2B Baseline** (GUI install, fully updated):
- CPU: 0.5% user, 99.2% idle
- RAM: 257 MB used, 80 MB free, 664 MB available
- Swap: 13 MB / 512 MB

**During Active Scanning** (typical):
- CPU: 15-30%
- RAM: 400-500 MB
- Swap: 20-50 MB
- IO: Minimal (USB SSD root helps)

**During Recording** (1-2 active signals):
- CPU: 25-40%
- RAM: 450-550 MB
- Disk writes: ~8 KB/s (64 kbps audio)

## Frequency Range Recommendations

**Start with these groups for best results:**

1. **GMRS** - Active in most areas, easy to detect
2. **2M Ham** - Very active, good for testing
3. **Weather Radio** - Continuous broadcasts, excellent signal
4. **FRS** - Common walkie-talkies, moderate activity

**Add later:**
- **Aircraft** if near airport
- **Marine** if near water
- **Business** for local commercial activity

## Data Usage Estimates

**Storage:**
- 1 hour recording: ~28 MB
- 1 day (assuming 10% activity): ~67 MB
- 14 days: ~940 MB
- 60 GB cap: ~2,140 hours of recording

**Network (rtl_tcp streaming):**
- 2.4 Mbps typical for NFM
- 20 Mbps for WFM (broadcast FM)
- Local network only, no internet usage

## Daily Operation

SDR_app runs automatically on boot with no manual intervention:

1. **rtltcp.service** starts first (device 0)
2. **scanner.service** starts 10s later (device 1)
3. **Storage pruning** runs daily at midnight
4. **Logs rotate** automatically (50 files retained)

**You only need to:**
- Access Web UI to start/stop scans
- Select frequency groups of interest
- Download recordings
- Adjust settings as needed

## Advanced: API Access

All features available via REST API:

```bash
# Get system status
curl http://localhost:8080/api/status

# Start scan
curl -X POST http://localhost:8080/api/scanner/start \
  -H "Content-Type: application/json" \
  -d '{"frequency_groups": ["2M_HAM", "GMRS"]}'

# Stop scan
curl -X POST http://localhost:8080/api/scanner/stop

# List recordings
curl http://localhost:8080/api/recordings

# Get logs
curl http://localhost:8080/api/logs?name=backend&lines=100
```

See `backend/app/main.py` for full API documentation (or visit `/docs` in browser).

## Next Steps

1. Read full **README.md** for detailed documentation
2. Review **DEPLOYMENT.md** for troubleshooting
3. Explore frequency groups and tune squelch
4. Set up monitoring for long-term operation
5. Join SDR community forums for frequency recommendations

## Support

- Installation logs: `/home/pi/SDR_app/logs/install.log`
- Run diagnostics: `/home/pi/SDR_app/scripts/diagnostics.sh`
- Check service logs: `journalctl -u rtltcp -u scanner`
- View system logs via Web UI → Settings tab

**Happy scanning! 73 de SDR_app**
