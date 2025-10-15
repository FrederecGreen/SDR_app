#!/bin/bash
# Diagnostics script for SDR_app
# Checks RTL-SDR dongles, services, and performs basic tests

set -e

BASE_DIR="/home/pi/SDR_app"

echo "========================================"
echo "SDR_app Diagnostics"
echo "========================================"
echo ""

# Check RTL-SDR dongles
echo "--- RTL-SDR Dongles ---"
if command -v rtl_test &> /dev/null; then
    echo "Checking device 0 (rtl_tcp):"
    timeout 5 rtl_test -d 0 -t 2 2>&1 || echo "Device 0 test failed or timeout"
    echo ""
    
    echo "Checking device 1 (scanner):"
    timeout 5 rtl_test -d 1 -t 2 2>&1 || echo "Device 1 test failed or timeout"
    echo ""
else
    echo "rtl_test not found!"
fi

# Check lsusb for RTL devices
echo "--- USB Devices (RTL) ---"
lsusb | grep -i realtek || echo "No Realtek devices found"
echo ""

# Check services
echo "--- Systemd Services ---"
echo "rtltcp.service: $(systemctl is-active rtltcp.service 2>/dev/null || echo 'not running')"
echo "scanner.service: $(systemctl is-active scanner.service 2>/dev/null || echo 'not running')"
echo ""

# Check ffmpeg
echo "--- ffmpeg ---"
if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -n 1
    ffmpeg -codecs 2>&1 | grep -i opus || echo "Opus codec not found"
else
    echo "ffmpeg not found!"
fi
echo ""

# Check disk usage
echo "--- Disk Usage ---"
df -h "$BASE_DIR" 2>/dev/null || df -h /home
echo ""

if [ -d "${BASE_DIR}/recordings" ]; then
    RECORDINGS_SIZE=$(du -sh "${BASE_DIR}/recordings" 2>/dev/null | cut -f1)
    RECORDINGS_COUNT=$(find "${BASE_DIR}/recordings" -name "*.ogg" -type f 2>/dev/null | wc -l)
    echo "Recordings: ${RECORDINGS_COUNT} files, ${RECORDINGS_SIZE}"
fi
echo ""

# Check logs
echo "--- Recent Log Errors ---"
for log in backend scanner rtltcp; do
    LOG_FILE="${BASE_DIR}/logs/${log}.log"
    if [ -f "$LOG_FILE" ]; then
        ERROR_COUNT=$(grep -ci error "$LOG_FILE" 2>/dev/null || echo 0)
        echo "${log}.log: ${ERROR_COUNT} errors"
    fi
done
echo ""

# Test audio capture (10 seconds)
echo "--- Test Audio Capture (10s on 146.52 MHz) ---"
if command -v rtl_fm &> /dev/null && command -v ffmpeg &> /dev/null; then
    TEST_FILE="/tmp/sdr_test_$(date +%s).ogg"
    echo "Capturing to: $TEST_FILE"
    
    timeout 12 rtl_fm -d 1 -f 146.52M -M fm -s 24k -r 48k -g 40 - 2>/dev/null | \
        ffmpeg -f s16le -ar 48k -ac 1 -i - -t 10 -c:a libopus -b:a 64k "$TEST_FILE" -y 2>&1 | tail -n 5
    
    if [ -f "$TEST_FILE" ]; then
        TEST_SIZE=$(du -h "$TEST_FILE" | cut -f1)
        echo "Test file created: ${TEST_SIZE}"
        echo "You can play it with: ffplay $TEST_FILE"
    else
        echo "Test capture failed"
    fi
else
    echo "rtl_fm or ffmpeg not available"
fi
echo ""

echo "========================================"
echo "Diagnostics complete"
echo "========================================"
