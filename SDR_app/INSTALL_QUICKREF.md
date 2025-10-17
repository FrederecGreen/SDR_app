# Installation Quick Reference - Updated with Blacklist Fix

## What Was Added
The installer now automatically blacklists kernel DVB-T modules that prevent RTL-SDR access.

## Fresh Installation Steps

1. **Clone the repository:**
   ```bash
   cd /home/pi
   rm -rf SDR_app  # Remove old installation
   git clone <your-repo-url> SDR_app
   cd SDR_app
   ```

2. **Run the installer:**
   ```bash
   ./install.sh
   ```

3. **What the installer does automatically:**
   - ✅ Creates 4GB swap
   - ✅ Installs all dependencies
   - ✅ Builds React frontend
   - ✅ Sets up udev rules
   - ✅ **NEW: Blacklists DVB-T kernel modules**
   - ✅ Updates initramfs
   - ✅ Unloads conflicting modules
   - ✅ Installs systemd services
   - ✅ Configures static IP (interactive)

4. **REBOOT (Required!):**
   ```bash
   sudo reboot
   ```
   The kernel module blacklist requires a reboot to fully take effect.

5. **Verify after reboot:**
   ```bash
   cd /home/pi/SDR_app
   
   # Check no DVB modules loaded
   lsmod | grep -E "rtl|dvb"
   
   # Run verification script
   ./scripts/verify_fixes.sh
   
   # Test devices
   ./scripts/test_devices.sh
   ```

## Expected Test Results

### Before Blacklist (OLD - would fail):
```
--- Device 1 Test (rtl_test) ---
usb_claim_interface error -6  ❌
Failed to open rtlsdr device #1.
```

### After Blacklist (NEW - should work):
```
--- Device 1 Test (rtl_test) ---
Using device 1: Generic RTL2832U OEM
Found Rafael Micro R820T tuner  ✅

--- Device 1 Test (rtl_fm) ---
✓ Device 1 accessible via rtl_fm (test completed)  ✅

--- Audio Pipeline Test ---
✓ Test file created: /tmp/sdr_test_XXX.ogg (24576 bytes)  ✅
✓ File size looks good (>10KB)  ✅
✓ Valid Opus file  ✅
```

## Troubleshooting

### If test still shows "usb_claim_interface error -6":

1. **Verify blacklist file exists:**
   ```bash
   cat /etc/modprobe.d/blacklist-rtl-sdr.conf
   ```
   Should contain:
   ```
   blacklist dvb_usb_rtl28xxu
   blacklist rtl2832
   blacklist rtl2830
   ```

2. **Check if modules are loaded:**
   ```bash
   lsmod | grep -E "dvb|rtl"
   ```
   Should NOT show: `dvb_usb_rtl28xxu`

3. **If modules are still loaded:**
   ```bash
   # Manually unload
   sudo rmmod dvb_usb_rtl28xxu
   
   # Update initramfs again
   sudo update-initramfs -u
   
   # Reboot again
   sudo reboot
   ```

4. **Manual blacklist (if installer failed):**
   ```bash
   sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf > /dev/null <<EOF
   blacklist dvb_usb_rtl28xxu
   blacklist rtl2832
   blacklist rtl2830
   EOF
   
   sudo update-initramfs -u
   sudo reboot
   ```

## What's Fixed

✅ **Phase 1:** Missing imports in signal_detector.py (scanner now works)
✅ **Phase 2:** test_devices.sh no longer hangs
✅ **Phase 2.5:** Kernel modules automatically blacklisted (devices accessible)

## Next: Test the Scanner

After successful device tests, test the scanner via the UI:

1. Access UI: `http://<pi-ip>:8080`
2. Start scanner with "FM Broadcast" group
3. Should detect active FM stations
4. Check logs: `sudo tail -f /home/pi/SDR_app/logs/backend.log`
5. Look for: "✓ SIGNAL DETECTED"
