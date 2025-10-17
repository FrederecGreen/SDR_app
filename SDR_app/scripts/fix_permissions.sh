#!/bin/bash
# Fix file permissions for SDR_app

echo "=========================================="
echo "  SDR_app Permission Fix"
echo "=========================================="
echo ""

BASE_DIR="/home/pi/SDR_app"

if [ ! -d "$BASE_DIR" ]; then
    echo "ERROR: $BASE_DIR not found"
    exit 1
fi

echo "Checking ownership of ${BASE_DIR}..."
OWNER=$(stat -c '%U:%G' "$BASE_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$BASE_DIR" 2>/dev/null)
echo "Current owner: $OWNER"
echo ""

if [ "$OWNER" != "pi:pi" ]; then
    echo "⚠ Incorrect ownership detected"
    echo ""
    read -p "Fix ownership to pi:pi? (y/n): " CONFIRM
    
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        echo ""
        echo "Fixing ownership..."
        sudo chown -R pi:pi "$BASE_DIR"
        echo "✓ Ownership corrected"
    else
        echo "Aborted"
        exit 0
    fi
else
    echo "✓ Ownership is correct (pi:pi)"
fi

echo ""
echo "Setting proper permissions..."
sudo chmod -R 755 "$BASE_DIR"
echo "✓ Permissions set"

echo ""
echo "Checking log files..."
if [ -d "${BASE_DIR}/logs" ]; then
    LOG_OWNER=$(stat -c '%U:%G' "${BASE_DIR}/logs" 2>/dev/null || stat -f '%Su:%Sg' "${BASE_DIR}/logs" 2>/dev/null)
    echo "Logs directory owner: $LOG_OWNER"
    
    if [ "$LOG_OWNER" != "pi:pi" ]; then
        echo "⚠ Fixing logs directory..."
        sudo chown -R pi:pi "${BASE_DIR}/logs"
        sudo chmod -R 755 "${BASE_DIR}/logs"
        echo "✓ Logs directory fixed"
    else
        echo "✓ Logs directory ownership correct"
    fi
fi

echo ""
echo "Checking recordings directory..."
if [ -d "${BASE_DIR}/recordings" ]; then
    REC_OWNER=$(stat -c '%U:%G' "${BASE_DIR}/recordings" 2>/dev/null || stat -f '%Su:%Sg' "${BASE_DIR}/recordings" 2>/dev/null)
    echo "Recordings directory owner: $REC_OWNER"
    
    if [ "$REC_OWNER" != "pi:pi" ]; then
        echo "⚠ Fixing recordings directory..."
        sudo chown -R pi:pi "${BASE_DIR}/recordings"
        sudo chmod -R 755 "${BASE_DIR}/recordings"
        echo "✓ Recordings directory fixed"
    else
        echo "✓ Recordings directory ownership correct"
    fi
fi

echo ""
echo "=========================================="
echo "  Permissions Fixed!"
echo "=========================================="
echo ""
echo "Restarting services..."
sudo systemctl restart scanner

echo ""
echo "Waiting for services to start..."
sleep 5

echo ""
echo "Service status:"
sudo systemctl status scanner --no-pager -l | head -10

echo ""
echo "If scanner is running, try accessing Web UI:"
echo "  http://$(hostname -I | awk '{print $1}'):8080"
echo ""
