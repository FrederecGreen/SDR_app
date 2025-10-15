# SDR_app Deployment Guide for Raspberry Pi 2B

## Pre-Deployment Checklist

### Hardware Requirements
- [ ] Raspberry Pi 2B with SD card boot + USB SSD root filesystem
- [ ] Powered USB hub
- [ ] 2x RTL-SDR dongles (identified as device 0 and device 1)
- [ ] Network connection (Ethernet or WiFi)
- [ ] Monitor and keyboard for initial setup (optional after SSH configured)

### Software Requirements
- Raspberry Pi OS Bookworm 32-bit (tested with Python 3.11.2)
- Fully updated system: `sudo apt update && sudo apt upgrade -y`
- At least 2 GB free disk space for installation
- Internet connection for package downloads

## Deployment Methods

### Method 1: Direct Clone (Recommended)

```bash
# On your Raspberry Pi 2B (as user 'pi')
cd /home/pi
git clone <YOUR_REPOSITORY_URL> SDR_app
cd SDR_app
chmod +x install.sh
./install.sh
```

### Method 2: curl | bash One-Liner

```bash
# If repository is public on GitHub
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/SDR_app/main/install.sh | bash
```

**Note:** For production use, always review scripts before running with `curl | bash`.

### Method 3: Manual File Transfer

If deploying without git:

```bash
# On your local machine
cd /path/to/SDR_app
tar -czf sdr_app.tar.gz .

# Transfer to Pi (replace PI_IP with your Pi's IP)
scp sdr_app.tar.gz pi@PI_IP:/home/pi/

# On Raspberry Pi
cd /home/pi
tar -xzf sdr_app.tar.gz
mv . SDR_app
cd SDR_app
chmod +x install.sh scripts/*.sh
./install.sh
```

## Installation Process

The installer performs these steps:

1. **Network Configuration (Interactive)**
   - Detects current IP address
   - Prompts to use detected IP or enter custom IP
   - Validates IP availability (ping test)
   - Writes static IP configuration to `/etc/dhcpcd.conf`
   - Prints access URLs for Web UI and rtl_tcp

2. **Swap Configuration**
   - Checks current swap size
   - Creates/resizes swap to 4 GB if needed
   - Uses `dphys-swapfile` for configuration

3. **Package Installation (Two-Pass)**
   - **Pass 1:** Build tools (build-essential, python3-dev, pkg-config)
   - **Pass 2:** Runtime dependencies (rtl-sdr, sox, ffmpeg, etc.)
   - All installs use `nice -n 19` for low priority

4. **Node.js Installation**
   - Installs Node 18.x LTS via NodeSource repository
   - Skips if already installed

5. **Python Environment**
   - Creates virtual environment at `/home/pi/SDR_app/venv`
   - Installs packages from `requirements.txt` with `--prefer-binary`
   - Uses `nice -n 19` for CPU throttling

6. **React Frontend Build**
   - Runs `npm ci` and `npm run build` in `server/`
   - Copies built files to `backend/static/`
   - Removes `node_modules` and `dist` to free space
   - Uses `nice -n 19` and `ionice -c3`

7. **Systemd Service Installation**
   - Installs `rtltcp.service`, `scanner.service`, `sdr-prune.service`, `sdr-prune.timer`
   - Enables services to start on boot
   - Starts services (rtltcp first, scanner after 10s delay)

8. **Verification**
   - Checks service status with `systemctl is-active`
   - Displays logs if services failed to start
   - Prints access URLs and useful commands

## Expected Installation Time

- **Pi2B with moderate internet:** 20-30 minutes
- **Breakdown:**
  - Package installation: 10-15 minutes
  - Python packages: 5-8 minutes
  - React build: 5-7 minutes

## Post-Installation Verification

### Check Services

```bash
sudo systemctl status rtltcp
sudo systemctl status scanner
```

Both should show "active (running)".

### Test rtl_tcp Server

```bash
# From another device on the same network
telnet <PI_IP> 1234
# Should connect successfully (Ctrl+C to exit)
```

Or use SDR++ or GQRX to connect to `<PI_IP>:1234`.

### Access Web UI

Open browser to `http://<PI_IP>:8080`

You should see:
- Dashboard with resource monitors
- Both services showing as "Running"
- Frequency groups available in Scanner tab

### Run Diagnostics

```bash
/home/pi/SDR_app/scripts/diagnostics.sh
```

This checks:
- RTL-SDR device detection
- Service status
- ffmpeg codecs
- Disk usage
- Log errors
- Performs 10s test capture

## Troubleshooting Installation Issues

### Services Won't Start

**Check logs:**
```bash
journalctl -u rtltcp -n 50
journalctl -u scanner -n 50
```

**Common issues:**
- **Dongle not detected:** Check `lsusb | grep Realtek`
- **Port already in use:** Check `sudo netstat -tulpn | grep 8080`
- **Python import errors:** Verify venv activation and package installation

### Network Configuration Issues

If static IP doesn't work after reboot:

```bash
# Check dhcpcd.conf
cat /etc/dhcpcd.conf

# Restart networking
sudo systemctl restart dhcpcd

# Check IP
hostname -I
```

### Swap Not Created

```bash
# Check swap status
free -m

# Manually recreate
sudo dphys-swapfile swapoff
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### React Build Fails

**Out of memory:**
- Ensure 4 GB swap is active
- Check `free -m`
- Retry: `cd /home/pi/SDR_app/server && nice -n 19 npm run build`

**Build artifacts remain:**
```bash
cd /home/pi/SDR_app
rm -rf server/node_modules server/dist
cd server
npm ci && npm run build
```

### USB Errors

Check dmesg for USB issues:
```bash
dmesg | grep -i usb
dmesg | grep -i rtl
```

**Common fixes:**
- Use powered USB hub
- Reduce scan aggressiveness in Web UI settings
- Increase dwell time
- Reduce number of frequency groups scanned

## Resource Monitoring During Installation

Installation is designed to be gentle on Pi2B resources:
- All heavy operations use `nice -n 19` (lowest priority)
- Disk I/O uses `ionice -c3` (idle class)
- 4 GB swap ensures no OOM during build
- Peak memory usage ~700 MB (with swap)

Monitor during install:
```bash
# In another terminal
watch -n 2 'free -m && echo "" && df -h / && echo "" && top -bn1 | head -n 12'
```

## Uninstallation

To completely remove SDR_app:

```bash
# Stop and disable services
sudo systemctl stop rtltcp scanner sdr-prune.timer
sudo systemctl disable rtltcp scanner sdr-prune.timer

# Remove service files
sudo rm /etc/systemd/system/rtltcp.service
sudo rm /etc/systemd/system/scanner.service
sudo rm /etc/systemd/system/sdr-prune.service
sudo rm /etc/systemd/system/sdr-prune.timer
sudo systemctl daemon-reload

# Remove application directory
rm -rf /home/pi/SDR_app

# Optionally restore dhcpcd.conf backup
# sudo cp /etc/dhcpcd.conf.backup.<timestamp> /etc/dhcpcd.conf
# sudo systemctl restart dhcpcd
```

## Updating the Application

To update after code changes:

```bash
cd /home/pi/SDR_app
git pull

# Rebuild frontend if changed
cd server
npm ci && npm run build
cp -r dist/* ../backend/static/

# Reinstall Python packages if changed
source ../venv/bin/activate
pip install -r ../requirements.txt

# Restart services
sudo systemctl restart rtltcp scanner
```

## Production Recommendations

1. **Backup Configuration**
   - Backup `/etc/dhcpcd.conf` before modification
   - Keep installation logs: `/home/pi/SDR_app/logs/install.log`

2. **Security**
   - Change default Pi password: `passwd`
   - Configure firewall if exposed to internet
   - Use SSH keys instead of password authentication

3. **Monitoring**
   - Check logs regularly: `tail -f /home/pi/SDR_app/logs/*.log`
   - Monitor resource usage via Web UI dashboard
   - Set up log rotation (automatically configured)

4. **Storage Management**
   - Prune service runs daily at midnight
   - Monitor recordings size via Web UI
   - Adjust retention/cap in Advanced Settings if needed

5. **USB Hub**
   - **Must use powered USB hub** for both RTL-SDR dongles
   - Insufficient power causes USB errors and scan failures

## Repository Structure

```
SDR_app/
├── install.sh                 # Main installation script
├── README.md                  # User documentation
├── DEPLOYMENT.md              # This file
├── requirements.txt           # Python dependencies
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   ├── models.py         # Data models
│   │   ├── frequency_groups.py  # Frequency definitions
│   │   ├── routes/           # API routes
│   │   └── scanner/          # Scanner engine
│   └── logging.ini           # Logging configuration
├── server/                   # React frontend
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── services/                 # Systemd unit files
│   ├── rtltcp.service
│   ├── scanner.service
│   ├── sdr-prune.service
│   └── sdr-prune.timer
├── scripts/
│   ├── prune_storage.sh      # Storage cleanup
│   └── diagnostics.sh        # System diagnostics
└── logs/                     # Log files (created during install)
```

## Support

For issues during deployment:

1. Check installation log: `/home/pi/SDR_app/logs/install.log`
2. Run diagnostics: `/home/pi/SDR_app/scripts/diagnostics.sh`
3. Review systemd logs: `journalctl -u rtltcp -u scanner -n 100`
4. Check USB devices: `lsusb | grep Realtek`
5. Verify network: `ping -c 4 8.8.8.8`

## License

MIT License - See repository for details.
