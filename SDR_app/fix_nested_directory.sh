#!/bin/bash
# Fix nested SDR_app directory structure
# Run this if you have: /home/pi/SDR_app/SDR_app/

echo "=========================================="
echo "  SDR_app Nested Directory Fix"
echo "=========================================="
echo ""

CURRENT_DIR="$(pwd)"
echo "Current directory: ${CURRENT_DIR}"
echo ""

# Check if we're in a nested structure
if [[ "$CURRENT_DIR" == */SDR_app/SDR_app ]]; then
    echo "✓ Detected nested directory structure"
    echo ""
    
    PARENT_DIR="$(dirname "$CURRENT_DIR")"
    TEMP_DIR="${PARENT_DIR}_temp_$$"
    
    echo "Will perform:"
    echo "  1. Move ${CURRENT_DIR}"
    echo "     to ${TEMP_DIR}"
    echo "  2. Remove ${PARENT_DIR}"
    echo "  3. Move ${TEMP_DIR}"
    echo "     to ${PARENT_DIR}"
    echo ""
    
    read -p "Proceed with fix? (y/n): " CONFIRM
    
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    
    echo ""
    echo "Fixing directory structure..."
    
    # Move nested directory to temp
    mv "$CURRENT_DIR" "$TEMP_DIR"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to move directory"
        exit 1
    fi
    echo "✓ Moved to temp location"
    
    # Remove empty parent
    rmdir "$PARENT_DIR" 2>/dev/null || rm -rf "$PARENT_DIR"
    echo "✓ Removed old parent directory"
    
    # Move temp to correct location
    mv "$TEMP_DIR" "$PARENT_DIR"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to move to final location"
        exit 1
    fi
    echo "✓ Moved to correct location"
    
    echo ""
    echo "=========================================="
    echo "  Fix Complete!"
    echo "=========================================="
    echo ""
    echo "Directory is now: ${PARENT_DIR}"
    echo ""
    echo "Next steps:"
    echo "  cd ${PARENT_DIR}"
    echo "  chmod +x install.sh scripts/*.sh"
    echo "  ./install.sh"
    echo ""
    
elif [[ "$CURRENT_DIR" == */SDR_app ]] && [ ! -d "SDR_app" ]; then
    echo "✓ Directory structure is correct!"
    echo ""
    echo "You are in: ${CURRENT_DIR}"
    echo "You can proceed with installation:"
    echo "  chmod +x install.sh scripts/*.sh"
    echo "  ./install.sh"
    echo ""
    
elif [ -d "SDR_app" ]; then
    echo "⚠ Found nested SDR_app subdirectory"
    echo ""
    echo "Current location: ${CURRENT_DIR}"
    echo "Nested directory: ${CURRENT_DIR}/SDR_app"
    echo ""
    echo "This script should be run from inside the nested directory."
    echo ""
    echo "Run these commands:"
    echo "  cd SDR_app"
    echo "  ./fix_nested_directory.sh"
    echo ""
    
else
    echo "✓ No nesting detected"
    echo ""
    echo "Current directory: ${CURRENT_DIR}"
    echo ""
    
    if [ -f "install.sh" ]; then
        echo "✓ install.sh found - you can proceed with installation"
        echo ""
        echo "Run:"
        echo "  chmod +x install.sh scripts/*.sh"
        echo "  ./install.sh"
    else
        echo "⚠ install.sh not found"
        echo ""
        echo "Are you in the correct directory?"
        echo "Expected to find install.sh here."
    fi
    echo ""
fi
