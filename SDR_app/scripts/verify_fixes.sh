#!/bin/bash
# Quick verification script for Phase 1 & Phase 2 fixes
# Run this on the Raspberry Pi after cloning

echo "=========================================="
echo "  Phase 1 & 2 Verification Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Verify signal_detector.py has correct imports
echo "Check 1: Verifying signal_detector.py imports..."
if grep -q "^import os$" /home/pi/SDR_app/backend/app/scanner/signal_detector.py && \
   grep -q "^import signal$" /home/pi/SDR_app/backend/app/scanner/signal_detector.py && \
   grep -q "^import time$" /home/pi/SDR_app/backend/app/scanner/signal_detector.py; then
    echo -e "${GREEN}✓${NC} All required imports present"
else
    echo -e "${RED}✗${NC} Missing imports in signal_detector.py"
    exit 1
fi

# Check 2: Verify no duplicate inline import time
echo "Check 2: Checking for duplicate imports..."
INLINE_IMPORT_COUNT=$(grep -c "import time" /home/pi/SDR_app/backend/app/scanner/signal_detector.py)
if [ "$INLINE_IMPORT_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✓${NC} No duplicate imports found"
else
    echo -e "${YELLOW}⚠${NC} Found $INLINE_IMPORT_COUNT 'import time' statements (expected 1)"
fi

# Check 3: Verify test_devices.sh uses setsid
echo "Check 3: Verifying test_devices.sh improvements..."
if grep -q "setsid rtl_fm" /home/pi/SDR_app/scripts/test_devices.sh; then
    echo -e "${GREEN}✓${NC} test_devices.sh uses setsid for process isolation"
else
    echo -e "${RED}✗${NC} test_devices.sh missing setsid improvements"
    exit 1
fi

# Check 4: Verify test_devices.sh has process group killing
if grep -q "kill -TERM -- -\$RTL_FM_PID" /home/pi/SDR_app/scripts/test_devices.sh; then
    echo -e "${GREEN}✓${NC} test_devices.sh uses process group killing"
else
    echo -e "${RED}✗${NC} test_devices.sh missing process group cleanup"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  All checks passed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart backend: sudo supervisorctl restart backend"
echo "2. Check logs: sudo tail -f /var/log/supervisor/backend.*.log"
echo "3. Run device test: ./scripts/test_devices.sh"
echo "4. Test scanner via UI"
echo ""
