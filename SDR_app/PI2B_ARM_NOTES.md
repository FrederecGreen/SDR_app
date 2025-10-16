# Raspberry Pi 2B (32-bit ARM) Compatibility Notes

## Architecture
Raspberry Pi 2B uses **armv7l** (32-bit ARM) architecture: `linux-arm-gnueabihf`

## Known Issues & Fixes

### Issue: Vite/Rollup Missing Native Binary
**Error:** `Cannot find module @rollup/rollup-linux-arm-gnueabihf`

**Root Cause:**
- Vite 5.x uses Rollup which requires native binaries
- The ARM 32-bit binary (`@rollup/rollup-linux-arm-gnueabihf`) is not always installed by npm
- This is due to npm's optional dependencies bug: https://github.com/npm/cli/issues/4828

**Fix Applied:**
1. Added `@rollup/rollup-linux-arm-gnueabihf` to `optionalDependencies` in package.json
2. Installer removes node_modules and package-lock.json if npm ci fails
3. Installer explicitly installs the ARM binary after npm install

**Manual Fix (if needed):**
```bash
cd /home/pi/SDR_app/server
rm -rf node_modules package-lock.json
npm install
npm install --save-optional @rollup/rollup-linux-arm-gnueabihf
npm run build
```

## Build Performance on Pi2B

**Expected build times:**
- npm install: 30-60 seconds
- Vite build: 2-5 minutes (with 4GB swap)

**Memory usage during build:**
- Peak: ~600-700 MB
- Requires adequate swap (4GB recommended)

**CPU usage:**
- Near 100% during build (expected)
- Uses nice -n 19 to minimize impact

## Alternative Build Methods

If Vite still fails on your Pi2B:

### Option 1: Build on Another Machine
```bash
# On a more powerful machine (same architecture or x64)
git clone https://github.com/FrederecGreen/SDR_app.git
cd SDR_app/server
npm install
npm run build

# Copy dist/ to your Pi
scp -r dist pi@<pi-ip>:/home/pi/SDR_app/backend/static/
```

### Option 2: Pre-built Frontend
We can provide pre-built static files if building on Pi2B continues to be problematic.

### Option 3: Use Docker Build
```bash
# Build in Docker with qemu ARM emulation
docker buildx build --platform linux/arm/v7 -t sdr-app .
```

## Verified Working Configuration

- **OS:** Raspberry Pi OS Bookworm 32-bit
- **Node.js:** 18.20.8 (from NodeSource)
- **npm:** 10.7.0
- **Python:** 3.11.2
- **Swap:** 4 GB
- **Vite:** 5.0.8
- **Rollup:** 4.9.0 (with linux-arm-gnueabihf binary)

## Testing Build Manually

To test if build will work:
```bash
cd /home/pi/SDR_app/server
npm install
npm run build

# Should create dist/ directory with:
# - index.html
# - assets/ (JS and CSS bundles)
```

## Troubleshooting

### Build Hangs or OOMs
- Check swap: `free -h`
- Check CPU: `top`
- Ensure 4GB swap active
- Kill other processes during build

### Module Not Found Errors
```bash
cd /home/pi/SDR_app/server
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Rollup Binary Issues
```bash
# Check installed rollup binaries
ls -la node_modules/@rollup/

# Should see: rollup-linux-arm-gnueabihf/
```

## Alternative: Webpack Instead of Vite

If Vite remains problematic, we can switch to Webpack which has better ARM support. Let us know if this is needed.

## Performance Optimizations

The build process uses:
- `nice -n 19` - lowest CPU priority
- `ionice -c3` - idle IO priority  
- Single-threaded where possible
- Minimal concurrent operations

This ensures the Pi remains responsive during installation.
