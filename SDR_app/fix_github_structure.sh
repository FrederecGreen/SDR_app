#!/bin/bash
# Script to completely reset GitHub repository with correct structure

echo "This script will force push the correct structure to GitHub"
echo "WARNING: This will overwrite the GitHub repository!"
echo ""
read -p "Continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Aborted"
    exit 1
fi

cd /app/SDR_app

# Verify we're in the right place
if [ ! -f "install.sh" ]; then
    echo "ERROR: Not in SDR_app directory"
    exit 1
fi

# Remove any accidental nested directories
if [ -d "SDR_app" ]; then
    echo "Found nested SDR_app directory - removing it"
    rm -rf SDR_app
    git add -A
    git commit -m "Remove nested SDR_app directory"
fi

# Show current structure
echo ""
echo "Current repository structure:"
git ls-tree HEAD --name-only
echo ""

# Force push to overwrite GitHub
echo "Force pushing to GitHub..."
git push -f origin main

echo ""
echo "Done! Repository structure fixed on GitHub"
echo ""
echo "On your Raspberry Pi, run:"
echo "  cd ~"
echo "  rm -rf SDR_app"
echo "  git clone https://github.com/FrederecGreen/SDR_app.git"
echo "  cd SDR_app"
echo "  ls -la  # Verify files are at root level"
echo "  chmod +x install.sh scripts/*.sh"
echo "  ./install.sh"
