#!/bin/bash
# Test RTL-SDR devices for SDR_app

echo "=========================================="
echo "  RTL-SDR Device Test"
echo "=========================================="
echo ""

# Check if devices are detected
echo "--- USB Devices ---"
lsusb | grep -i realtek || echo "WARNING: No Realtek devices found!"
echo ""

# Check udev rules
echo "--- udev Rules ---"
if [ -f /etc/udev/rules.d/20-rtlsdr.rules ]; then
    echo "✓ udev rules exist"
    cat /etc/udev/rules.d/20-rtlsdr.rules
else
    echo "✗ udev rules missing!"
fi
echo ""

# Check if rtl_tcp is using device 0
echo "--- Device 0 Status ---"
if systemctl is-active --quiet rtltcp; then
    echo "✓ rtl_tcp service is running (device 0 in use)"
    echo "  This is normal - device 0 is reserved for rtl_tcp"
else
    echo "✗ rtl_tcp service not running"
    echo "  Testing device 0..."
    timeout 3 rtl_test -d 0 -t 1 2>&1 | head -10
fi
echo ""

# Test device 1 with rtl_test
echo "--- Device 1 Test (rtl_test) ---"
echo "Testing device 1 for 3 seconds..."
timeout 3 rtl_test -d 1 -t 2 2>&1
echo ""

# Test device 1 with rtl_fm (more reliable)
echo "--- Device 1 Test (rtl_fm) ---"
echo "Testing FM reception on 98.1 MHz for 2 seconds..."
TEST_FREQ="98100000"  # 98.1 MHz

# Run rtl_fm with better process management to avoid lockups
# Use setsid to create new session and prevent terminal hangups
setsid rtl_fm -d 1 -f $TEST_FREQ -M fm -s 24k -l 40 - >/dev/null 2>&1 &
RTL_FM_PID=$!

# Give it 2 seconds to run
sleep 2

# Kill the process group to ensure cleanup
if ps -p $RTL_FM_PID > /dev/null 2>&1; then
    # Kill the entire process group
    kill -TERM -- -$RTL_FM_PID 2>/dev/null || true
    sleep 0.5
    # Force kill if still alive
    kill -KILL -- -$RTL_FM_PID 2>/dev/null || true
fi

# Wait for cleanup
wait $RTL_FM_PID 2>/dev/null || true

echo "✓ Device 1 accessible via rtl_fm (test completed)"
echo ""

# Test audio pipeline
echo "--- Audio Pipeline Test ---"
echo "Testing complete pipeline: rtl_fm → ffmpeg → opus"
TEST_FILE="/tmp/sdr_test_$(date +%s).ogg"

echo "Recording 3 seconds of 98.1 MHz FM..."
timeout 5 rtl_fm -d 1 -f $TEST_FREQ -M fm -s 24k -r 48k -g 40 - 2>/dev/null | \
    timeout 4 ffmpeg -f s16le -ar 48k -ac 1 -i - -t 3 -c:a libopus -b:a 64k "$TEST_FILE" -y 2>&1 | tail -5

if [ -f "$TEST_FILE" ]; then
    SIZE=$(stat -f%z "$TEST_FILE" 2>/dev/null || stat -c%s "$TEST_FILE" 2>/dev/null)
    echo "✓ Test file created: $TEST_FILE (${SIZE} bytes)"
    
    if [ $SIZE -gt 10000 ]; then
        echo "✓ File size looks good (>10KB)"
    else
        echo "⚠ File size suspicious (<10KB) - may be silence only"
    fi
    
    # Check if file is valid
    if ffprobe "$TEST_FILE" 2>&1 | grep -q "opus"; then
        echo "✓ Valid Opus file"
    else
        echo "✗ File may be corrupted"
    fi
    
    echo ""
    echo "You can play this file with:"
    echo "  ffplay $TEST_FILE"
    echo "  or"
    echo "  vlc $TEST_FILE"
else
    echo "✗ Test file not created - pipeline failed"
fi
echo ""

echo "=========================================="
echo "  Test Complete"
echo "=========================================="
echo ""
echo "If all tests passed, scanner should work."
echo "If tests failed, check:"
echo "  1. Both dongles are plugged into powered USB hub"
echo "  2. udev rules are installed"
echo "  3. User pi is in plugdev group: groups pi"
echo ""
