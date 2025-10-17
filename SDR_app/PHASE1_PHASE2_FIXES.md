# Phase 1 & Phase 2 Fixes - Scanner Critical Bug Fixes

**Date:** January 2025
**Status:** Ready for testing on Raspberry Pi 2B
**Updated:** Added kernel module blacklist to installer

---

## Phase 1: Fix Critical Scanner Bug

### Problem
The scanner's signal detection was completely broken due to **missing imports** in `signal_detector.py`:
- Missing `import os` (used for `os.setsid`, `os.killpg`, `os.getpgid`)
- Missing `import signal` (used for `signal.SIGTERM`, `signal.SIGKILL`)
- Missing `import time` at module level (was imported inline)

### Root Cause
The `detect_signal()` method uses process group management to cleanly terminate `rtl_fm` processes:
```python
preexec_fn=os.setsid  # Line 63
os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Line 80
```

Without these imports, the code would crash with `NameError` whenever it tried to detect a signal.

### Fix Applied
**File:** `/app/SDR_app/backend/app/scanner/signal_detector.py`

Added missing imports at the top of the file:
```python
import os
import signal
import time
```

Also removed duplicate inline `import time` on line 67.

### Impact
✅ Signal detection should now work correctly
✅ Scanner can properly start and stop `rtl_fm` processes
✅ Process cleanup is now reliable

---

## Phase 2: Improve test_devices.sh

### Problem
The `test_devices.sh` script could cause the Pi to lock up during the rtl_fm test:
- Used `timeout` command with background process, which can have race conditions
- Process cleanup was not guaranteed
- Could leave zombie rtl_fm processes running

### Fix Applied
**File:** `/app/SDR_app/scripts/test_devices.sh`

#### Device 1 Test Section (Lines 42-68)
Improved process management:
```bash
# Use setsid to create new session (prevents terminal hangups)
setsid rtl_fm -d 1 -f $TEST_FREQ -M fm -s 24k -l 40 - >/dev/null 2>&1 &
RTL_FM_PID=$!

sleep 2

# Kill the entire process group
kill -TERM -- -$RTL_FM_PID 2>/dev/null || true
sleep 0.5
kill -KILL -- -$RTL_FM_PID 2>/dev/null || true

wait $RTL_FM_PID 2>/dev/null || true
```

#### Audio Pipeline Test Section (Lines 70-110)
Improved pipeline cleanup:
```bash
# Start in background
setsid rtl_fm ... | ffmpeg ... &
PIPELINE_PID=$!

# Wait with timeout
timeout 6 bash -c "wait $PIPELINE_PID" 2>/dev/null || true

# Force cleanup of any remaining rtl_fm processes
pkill -TERM -f "rtl_fm.*-d 1.*-f $TEST_FREQ" 2>/dev/null || true
sleep 0.5
pkill -KILL -f "rtl_fm.*-d 1.*-f $TEST_FREQ" 2>/dev/null || true
```

### Key Improvements
1. **Session isolation:** `setsid` creates a new session, preventing terminal issues
2. **Process group killing:** `kill -- -$PID` kills entire process group
3. **Fallback cleanup:** `pkill` ensures no stray processes remain
4. **Graceful then forceful:** TERM signal first, then KILL if needed
5. **Non-blocking:** Uses `|| true` to prevent script exit on expected errors

### Impact
✅ Test script will not lock up the Pi
✅ All rtl_fm processes are guaranteed to be cleaned up
✅ More reliable diagnostics

---

## Phase 2.5: Add Kernel Module Blacklist to Installer

### Problem
DVB-T kernel modules (`dvb_usb_rtl28xxu`, `rtl2832`, `rtl2830`) automatically claim RTL-SDR devices when they're plugged in, preventing rtl_fm and other SDR tools from accessing them. This causes:
- `usb_claim_interface error -6` when trying to use the devices
- Audio pipeline failures
- Scanner unable to record

### Fix Applied
**File:** `/app/SDR_app/install.sh`

Added automatic kernel module blacklisting during installation:

```bash
# Creates /etc/modprobe.d/blacklist-rtl-sdr.conf with:
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830

# Updates initramfs to persist across reboots
# Immediately unloads modules if currently loaded
```

**Benefits:**
- Installer now handles this automatically
- No manual intervention needed
- Modules are unloaded during install if present
- Blacklist persists across reboots via initramfs

### Impact
✅ RTL-SDR devices accessible to rtl_fm/rtl_tcp immediately after reboot
✅ No more USB claim errors
✅ Scanner can function properly

---

## Testing Recommendations

### Important: Reboot Required
After installation, **reboot the Pi** to ensure kernel module blacklist takes effect:
```bash
sudo reboot
```

### 1. Verify Blacklist (after reboot)
```bash
# Check that DVB modules are NOT loaded
lsmod | grep -E "rtl|dvb"

# Should show NO dvb_usb_rtl28xxu, rtl2832, or rtl2830
# May show rtl2832_sdr (this is OK - it's the SDR driver)
```

### 2. Test the Scanner Backend
```bash
# Check if backend starts without errors
sudo supervisorctl restart backend
sudo tail -f /var/log/supervisor/backend.*.log

# Look for:
# - No "NameError" or import errors
# - Successful service startup
```

### 3. Run Device Test Script
```bash
cd /home/pi/SDR_app
./scripts/test_devices.sh

# Should complete without hanging
# Should show:
# ✓ Device 1 accessible via rtl_fm
# ✓ Test file created (audio pipeline working)
```

### 4. Test Scanner via UI
1. Access UI in browser
2. Start scanner with any frequency group (e.g., FM Broadcast)
3. Check for signal detections
4. Monitor backend logs: `sudo tail -f /home/pi/SDR_app/logs/backend.log`

### 5. Expected Behavior
When scanning a known FM broadcast (e.g., 98.1 MHz):
```
[INFO] Scanning 98.1 MHz (mode: wbfm, rate: 200k, squelch: 0)
[INFO] ✓ SIGNAL DETECTED: 98.1 MHz - 28672 bytes (~-37.1dB)
[INFO] Started recording: 98.1 MHz
```

---

## Files Changed

1. `/app/SDR_app/backend/app/scanner/signal_detector.py`
   - Added imports: `os`, `signal`, `time`
   - Removed duplicate inline import

2. `/app/SDR_app/scripts/test_devices.sh`
   - Improved rtl_fm test with setsid and process group killing
   - Improved audio pipeline test with forced cleanup

3. `/app/SDR_app/install.sh`
   - Added kernel module blacklist creation
   - Automatic initramfs update
   - Immediate module unloading during install

---

## Next Steps (Phase 3 & 4)

Once scanner is confirmed working:
- Fix UI bugs (WFW→WFM, swap size display)
- Implement UI enhancements for frequency management
- Add data persistence for detections/recordings

---

## Rollback Instructions

If issues occur, revert these changes:
```bash
cd /home/pi/SDR_app
git diff HEAD~1  # Review changes
git reset --hard HEAD~1  # Revert to previous commit
sudo supervisorctl restart all
```
