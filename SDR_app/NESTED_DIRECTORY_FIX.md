# Nested Directory Issue Fix

## Problem

When cloning from GitHub, you may get a nested directory structure:

```
/home/pi/SDR_app/
  └── SDR_app/          ← Nested! (wrong)
      ├── install.sh
      ├── backend/
      ├── server/
      └── ...
```

**Expected structure:**
```
/home/pi/SDR_app/
  ├── install.sh        ← Files at root level (correct)
  ├── backend/
  ├── server/
  └── ...
```

## Solution 1: Installer Auto-Fix (Recommended)

The installer now **automatically detects and fixes** the nested directory issue.

Simply run:

```bash
cd /home/pi/SDR_app/SDR_app  # Go into nested directory
chmod +x install.sh scripts/*.sh
./install.sh
```

The installer will:
1. Detect it's in a nested structure
2. Automatically fix it
3. Continue installation from correct location

**You'll see:**
```
⚠ Detected nested SDR_app directory structure
ℹ Fixing directory structure...
✓ Directory structure fixed! Now in: /home/pi/SDR_app
✓ Continuing installation...
```

## Solution 2: Manual Fix Script

Before running the installer, you can manually fix the structure:

```bash
cd /home/pi/SDR_app/SDR_app
chmod +x fix_nested_directory.sh
./fix_nested_directory.sh
```

This will:
1. Show you what it will do
2. Ask for confirmation
3. Fix the directory structure
4. Tell you the next steps

## Solution 3: Manual Command

If you prefer to fix it manually:

```bash
cd /home/pi
mv SDR_app SDR_app_temp
mv SDR_app_temp/SDR_app SDR_app
rm -rf SDR_app_temp
cd SDR_app
ls -la  # Verify install.sh is here
```

## How to Check if You Have the Issue

```bash
cd /home/pi/SDR_app
ls -la
```

**If you see `SDR_app/` subdirectory** → You have the nested issue  
**If you see `install.sh` at this level** → Structure is correct

## Why Does This Happen?

This appears to be related to how the repository was initially structured on GitHub. The installer and fix scripts handle it automatically, so you don't need to worry about the root cause.

## Verification After Fix

After running the installer or fix script:

```bash
cd /home/pi/SDR_app
pwd
# Should output: /home/pi/SDR_app

ls -la
# Should show:
# install.sh
# backend/
# server/
# scripts/
# etc.
```

## For Fresh Installs

When doing a fresh installation:

```bash
cd /home/pi
git clone https://github.com/FrederecGreen/SDR_app.git
cd SDR_app

# Check structure
ls -la

# If you see nested SDR_app/, either:
# Option 1: Just run installer (it auto-fixes)
cd SDR_app  # if nested
chmod +x install.sh scripts/*.sh
./install.sh

# Option 2: Fix first, then install
cd SDR_app  # if nested
./fix_nested_directory.sh
cd /home/pi/SDR_app
./install.sh
```

## Prevention

The nesting issue is being tracked. Future updates may resolve it at the repository level. For now, the auto-fix in the installer handles it transparently.

## Troubleshooting

### "install.sh: No such file or directory"

You're probably in the wrong directory. Run:

```bash
cd /home/pi/SDR_app
find . -name "install.sh" -type f
```

This will show you where install.sh actually is. Navigate there and run it.

### "Missing required files" Error

The installer checks for required files. If you get this error after the auto-fix:

1. Check current directory: `pwd`
2. List files: `ls -la`
3. Verify you have:
   - `requirements.txt`
   - `backend/app/main.py`
   - `server/package.json`
   - `services/` directory

If files are missing, re-clone from GitHub.

### Fix Script Says "No Nesting Detected" But Structure Seems Wrong

Run from the **innermost** SDR_app directory:

```bash
# Find all SDR_app directories
find /home/pi -type d -name "SDR_app" 2>/dev/null

# Go to the one that contains install.sh
cd /home/pi/SDR_app/SDR_app  # adjust based on find output
./fix_nested_directory.sh
```

## Summary

**You don't need to worry about this issue anymore** - the installer handles it automatically. Just:

1. Clone from GitHub
2. Navigate to wherever install.sh is located
3. Run `./install.sh`
4. Installer detects and fixes any nesting

The fix is transparent and happens in seconds before the main installation begins.
