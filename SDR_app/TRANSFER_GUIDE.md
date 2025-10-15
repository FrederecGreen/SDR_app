# How to Transfer SDR_app to Your Raspberry Pi

Since you can't access the file browser, here are the best methods:

## Method 1: Manual Recreation (Recommended)

Run this ONE command on your Pi to download and setup everything:

```bash
# This will be available once you push to GitHub
git clone https://github.com/YOUR_USERNAME/SDR_app.git /home/pi/SDR_app
cd /home/pi/SDR_app
chmod +x install.sh scripts/*.sh
./install.sh
```

## Method 2: Create Core Files Manually

If you want to manually create files, here's the minimal set:

### 1. Create base structure
```bash
mkdir -p /home/pi/SDR_app/{backend/app/{routes,scanner},server/src/components,services,scripts,logs}
cd /home/pi/SDR_app
```

### 2. Create requirements.txt
```bash
cat > requirements.txt << 'EOF'
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
EOF
```

### 3. Copy install.sh
You can copy the install.sh content shown above into a file:

```bash
nano install.sh
# Paste the content, save with Ctrl+X, Y, Enter
chmod +x install.sh
```

### 4. Get remaining files
The complete repository has 41 files. I recommend using git clone once you push to GitHub.

## Method 3: Direct SSH/SCP from Another Machine

If you have this code on another computer:

```bash
# On the machine with the code
scp -r /path/to/SDR_app pi@<your_pi_ip>:/home/pi/

# Then SSH to Pi
ssh pi@<your_pi_ip>
cd /home/pi/SDR_app
chmod +x install.sh scripts/*.sh
./install.sh
```

## What You Need

The complete application requires:
- 11 Python backend files
- 6 React frontend files (+ package.json)
- 4 systemd service files
- 3 shell scripts
- Configuration files (README, requirements.txt, logging.ini)

**All files are in /app/SDR_app/** in this development environment.
