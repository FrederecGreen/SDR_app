# SDR_app Installation Guide - Fresh Pi2B Setup

## Prerequisites

- Raspberry Pi 2B with Raspberry Pi OS Bookworm 32-bit
- SD card boot + USB SSD root (optional but recommended)
- 2x RTL-SDR dongles connected to powered USB hub
- Network connection (Ethernet or WiFi)
- At least 2 GB free disk space

## Quick Start

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Clone repository
cd /home/pi
git clone https://github.com/FrederecGreen/SDR_app.git
cd SDR_app

# 3. Navigate to install.sh location
# If you see nested SDR_app/, cd into it:
ls -la  # Check if install.sh is here
[ -f install.sh ] || cd SDR_app  # Go into nested dir if needed

# 4. Make scripts executable
chmod +x install.sh scripts/*.sh

# 5. Run installer
./install.sh
```

**The installer automatically fixes any nested directory issues!**

## What the Installer Does

### 1. Directory Structure Fix (Automatic)
- Detects nested SDR_app/SDR_app structure
- Automatically reorganizes to correct structure
- No user action required

### 2. Interactive IP Configuration
- Detects current IP address
- Option to accept or enter custom IP
- Validates availability with ping test
- Configures static IP (if dhcpcd available)

### 3. Swap Configuration
- Creates 4GB swap file (if dphys-swapfile available)
- Required for React build on Pi2B
- Falls back gracefully if unavailable

### 4. Package Installation
- **Pass 1:** Build tools (build-essential, python3-dev, etc.)
- **Pass 2:** Runtime dependencies (rtl-sdr, ffmpeg, sox, etc.)
- Node.js 18.x LTS installation
- Fallback to default repos if NodeSource fails

### 5. RTL-SDR Device Setup
- Creates udev rules for device permissions
- Adds pi user to plugdev group
- Reloads udev and triggers rule application

### 6. Python Environment
- Creates virtual environment
- Installs pinned packages with --prefer-binary
- Retries on failures

### 7. React Frontend Build
- npm install with ARM rollup binary
- Vite build (5-10 minutes on Pi2B)
- Uses nice/ionice for low priority
- Copies build to backend/static

### 8. Service Installation
- Installs systemd units (rtltcp, scanner, prune timer)
- Enables services for auto-start
- Starts both services
- Verifies service status

## Installation Timeline

**Total: 25-35 minutes on Pi2B**

- Directory fix: < 5 seconds
- IP configuration: Interactive
- Swap creation: 1-2 minutes
- APT packages: 10-15 minutes
- Node.js: 2-3 minutes
- Python packages: 5-8 minutes
- **React build: 5-10 minutes** (most resource intensive)
- Services: 1-2 minutes

## Monitoring Installation

### Watch Resources (Optional)

Open second SSH session:

```bash
watch -n 2 'free -h && echo "" && top -bn1 | head -5'
```

**During React build expect:**
- CPU: 90-100% (normal with nice -n 19)
- Memory + Swap: 600-800 MB
- Process: node (building React)

### Check Logs

```bash
# Follow installation log
tail -f /home/pi/SDR_app/logs/install.log

# Check for errors
grep -i error /home/pi/SDR_app/logs/install.log
```

## Post-Installation Verification

### 1. Service Status

```bash
sudo systemctl status rtltcp scanner
```

**Expected:**
```
● rtltcp.service - active (running)
● scanner.service - active (running)
```

### 2. Device Test

```bash
cd /home/pi/SDR_app
./scripts/test_devices.sh
```

**Expected:**
```
✓ udev rules exist
✓ rtl_tcp service is running
✓ Device 1 accessible via rtl_fm
✓ Test file created
✓ Valid Opus file
```

### 3. Web UI Access

```bash
# Get your IP
hostname -I

# Open browser to: http://<IP>:8080
```

**Should show:**
- Dashboard with resource monitors
- Both services showing green/running
- No errors in browser console

### 4. Scanner Test

1. Navigate to Scanner tab
2. Add custom frequency: **98.1 MHz, WFM** (or local FM station)
3. Click "Start Scan"
4. Watch Active Detections table
5. Let run 30+ seconds

**Expected:**
- Detection appears within 2-4 seconds
- Signal strength shown
- Recording starts automatically

### 5. Verify Recording

```bash
ls -lh /home/pi/SDR_app/recordings/
```

**Should show `.ogg` files:**
```
20251017_140530_98_1000_CustomFM_part000.ogg
20251017_140530_98_1000_CustomFM_part001.ogg
```

Download via Web UI and play to verify audio.

## Troubleshooting

### Nested Directory Issue

**Symptom:** `install.sh: No such file or directory`

**Solution:**
```bash
cd /home/pi/SDR_app
ls -la  # Check structure

# If you see SDR_app subdirectory:
cd SDR_app
./install.sh  # Auto-fixes structure
```

### React Build Fails (Out of Memory)

**Symptoms:**
- Build hangs
- Process killed
- OOM in dmesg

**Solutions:**
1. Check swap: `free -h` (need ~4GB)
2. Close other programs
3. Reboot and retry

**Manual retry:**
```bash
cd /home/pi/SDR_app/server
rm -rf node_modules dist
npm install
npm run build
```

### Service Won't Start

**Check logs:**
```bash
journalctl -u scanner -n 50 --no-pager
tail -50 /home/pi/SDR_app/logs/backend.log
```

**Common issues:**
- Log permission: `sudo chown -R pi:pi /home/pi/SDR_app/logs/`
- Missing files: Verify structure correct
- Port in use: `sudo netstat -tulpn | grep 8080`

### Scanner Doesn't Detect Signals

**Run device test:**
```bash
./scripts/test_devices.sh
```

**Check:**
1. Both dongles connected to powered USB hub?
2. udev rules exist? `ls -la /etc/udev/rules.d/20-rtlsdr.rules`
3. In plugdev group? `groups pi | grep plugdev`
4. Scanner logs active? `tail -f /home/pi/SDR_app/logs/scanner.log`

**If plugdev membership missing:**
```bash
sudo usermod -a -G plugdev pi
# Log out and back in
```

### No Recordings Created

**Check:**
1. Scanner detected signal? (Active Detections table)
2. Scan ran > 30 seconds?
3. Recordings directory writable? `ls -la /home/pi/SDR_app/`
4. Disk space available? `df -h /home/pi/SDR_app`

**Check scanner logs:**
```bash
grep -i "record\|signal\|detect" /home/pi/SDR_app/logs/scanner.log
```

## Advanced Configuration

### Change Scan Parameters

Web UI → Settings tab:
- Dwell time (default: 2 seconds)
- Squelch level (default: 40 dB)
- Chunk duration (default: 30 seconds)
- Retention days (default: 14 days)

### Manual Service Control

```bash
# Restart services
sudo systemctl restart rtltcp scanner

# View service logs
journalctl -u rtltcp -f
journalctl -u scanner -f

# Stop scanner
sudo systemctl stop scanner

# Start scanner
sudo systemctl start scanner
```

### View Application Logs

```bash
# Backend log
tail -f /home/pi/SDR_app/logs/backend.log

# Scanner log
tail -f /home/pi/SDR_app/logs/scanner.log

# Installation log
less /home/pi/SDR_app/logs/install.log
```

## Expected File Sizes

- **30s recording chunk:** ~240 KB (64 kbps Opus)
- **5min session:** ~2.4 MB
- **1 hour of recording:** ~28 MB
- **60 GB storage cap:** ~2,140 hours of recording

## Next Steps After Installation

1. ✅ Verify scanner detects FM broadcasts
2. ✅ Confirm recordings are created and playable
3. ✅ Test CTCSS detection (if signals with tones available)
4. Configure saved frequency groups
5. Customize scan parameters
6. Set up regular monitoring

## Getting Help

If installation fails:

1. Check `/home/pi/SDR_app/logs/install.log`
2. Run `./scripts/test_devices.sh`
3. Check service status: `systemctl status rtltcp scanner`
4. Verify structure: `ls -la /home/pi/SDR_app/`

Provide these outputs when reporting issues.

## Documentation

- **README.md** - Full feature documentation
- **SCANNER_FIX_SUMMARY.md** - Signal detection fix details
- **NESTED_DIRECTORY_FIX.md** - Directory structure issue
- **PI2B_ARM_NOTES.md** - Pi2B compatibility notes
- **DEPLOYMENT.md** - Deployment and troubleshooting
- **QUICKSTART.md** - Quick reference guide

## Success Criteria

Installation is successful when:

✅ Both services running (rtltcp, scanner)  
✅ Web UI accessible with no errors  
✅ Device test script passes all checks  
✅ Scanner detects FM broadcast signals  
✅ Recordings created and playable  
✅ No errors in logs  

Once these are verified, the system is fully operational!
