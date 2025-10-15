#!/bin/bash
# Run this script on your Raspberry Pi to manually set up SDR_app
# This creates the entire structure without needing to download files

set -e

echo "Creating SDR_app directory structure..."
cd /home/pi
mkdir -p SDR_app/{backend/app/{routes,scanner},server/src/components,services,scripts,logs}
cd SDR_app

echo "Creating requirements.txt..."
cat > requirements.txt << 'PYEOF'
fastapi==0.115.2
uvicorn[standard]==0.30.1
pydantic==2.9.2
python-multipart==0.0.9
starlette==0.38.2
aiofiles==24.1.0
soundfile==0.12.1
tenacity==8.3.0
rich==13.9.2
psutil==6.0.0
PYEOF

echo "Creating package.json..."
cat > server/package.json << 'PKGEOF'
{
  "name": "sdr-app-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
PKGEOF

echo ""
echo "=========================================="
echo "SDR_app structure created!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. I will show you the remaining files to copy"
echo "2. After all files are created, run: chmod +x install.sh scripts/*.sh"
echo "3. Then run: ./install.sh"
echo ""
echo "Location: /home/pi/SDR_app"
