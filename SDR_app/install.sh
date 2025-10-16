#!/bin/bash
# SDR_app Installer for Raspberry Pi 2B
# Optimized for SD boot + USB SSD root + 2x RTL-SDR dongles
# 
# This script:
# - Creates 4GB swap (if swap tools available)
# - Installs dependencies in two passes
# - Builds React frontend once
# - Installs Python packages with --prefer-binary
# - Configures static IP interactively (if dhcpcd available)
# - Installs systemd services
# - Uses resource throttling during install

# Don't exit on error - we'll handle errors gracefully
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/home/pi/SDR_app"
LOGS_DIR="${BASE_DIR}/logs"
INSTALL_LOG="${LOGS_DIR}/install.log"
VENV_DIR="${BASE_DIR}/venv"
SWAP_SIZE_MB=4096

# Create logs directory
mkdir -p "$LOGS_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$INSTALL_LOG"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$INSTALL_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$INSTALL_LOG"
}

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}" | tee -a "$INSTALL_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$INSTALL_LOG"
}

# Error handler
error_exit() {
    log_error "$1"
    exit 1
}

# Safe command execution with fallback
safe_execute() {
    local cmd="$1"
    local fallback_msg="$2"
    
    if eval "$cmd"; then
        return 0
    else
        log_warning "$fallback_msg"
        return 1
    fi
}

echo ""
echo "=========================================="
echo "    SDR_app Installer for Pi2B"
echo "=========================================="
echo ""

log "Installation started"

# Check if running as pi user
if [ "$(whoami)" != "pi" ]; then
    error_exit "This script must be run as user 'pi'"
fi

# Detect current IP
log_info "Detecting network configuration..."
DETECTED_IP=$(hostname -I | awk '{print $1}')
ACTIVE_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n 1)

if [ -z "$DETECTED_IP" ]; then
    error_exit "Could not detect IP address. Please check network connection."
fi

if [ -z "$ACTIVE_INTERFACE" ]; then
    error_exit "Could not detect active network interface."
fi

log_info "Detected IP: ${DETECTED_IP} on interface ${ACTIVE_INTERFACE}"

# Interactive IP selection
echo ""
echo "=========================================="
echo "  Network Configuration"
echo "=========================================="
echo ""
echo -e "${BLUE}Detected IP address: ${DETECTED_IP}${NC}"
echo -e "${BLUE}Active interface: ${ACTIVE_INTERFACE}${NC}"
echo ""
read -p "Use this IP address? (y/n): " USE_DETECTED

CHOSEN_IP="$DETECTED_IP"

if [ "$USE_DETECTED" != "y" ] && [ "$USE_DETECTED" != "Y" ]; then
    while true; do
        read -p "Enter desired IP address: " CUSTOM_IP
        
        # Validate IP format
        if [[ ! $CUSTOM_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            log_warning "Invalid IP format. Please try again."
            continue
        fi
        
        # Check if IP is available
        log_info "Checking if ${CUSTOM_IP} is available..."
        if ping -c 1 -W 1 "$CUSTOM_IP" &> /dev/null; then
            log_warning "IP ${CUSTOM_IP} is already in use. Please choose another."
            continue
        fi
        
        CHOSEN_IP="$CUSTOM_IP"
        log_success "IP ${CHOSEN_IP} is available"
        break
    done
fi

log_info "Selected IP address: ${CHOSEN_IP}"

# Configure static IP - check if dhcpcd.conf exists
if [ -f /etc/dhcpcd.conf ]; then
    log_info "Configuring static IP in /etc/dhcpcd.conf..."
    
    # Backup dhcpcd.conf
    if sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup.$(date +%s) 2>/dev/null; then
        log_info "Backed up dhcpcd.conf"
    fi
    
    # Remove any existing static IP config for this interface
    sudo sed -i "/^interface ${ACTIVE_INTERFACE}/,/^$/d" /etc/dhcpcd.conf 2>/dev/null
    
    # Get gateway and DNS
    GATEWAY=$(ip route | grep default | awk '{print $3}' | head -n 1)
    DNS_SERVER=$(grep "^nameserver" /etc/resolv.conf 2>/dev/null | head -n 1 | awk '{print $2}')
    
    if [ -z "$DNS_SERVER" ]; then
        DNS_SERVER="8.8.8.8"  # Fallback to Google DNS
    fi
    
    # Append static IP configuration
    if sudo tee -a /etc/dhcpcd.conf > /dev/null <<EOF

# SDR_app static IP configuration
interface ${ACTIVE_INTERFACE}
static ip_address=${CHOSEN_IP}/24
static routers=${GATEWAY}
static domain_name_servers=${DNS_SERVER}
EOF
    then
        log_success "Static IP configured: ${CHOSEN_IP}"
        log_info "Network will use this IP on next reboot"
    else
        log_warning "Failed to configure static IP"
    fi
else
    log_warning "dhcpcd.conf not found - skipping static IP configuration"
    log_warning "Your system may be using NetworkManager or systemd-networkd"
    log_info "Current IP (${CHOSEN_IP}) will be used, but may change on reboot"
    log_info "You can configure static IP manually after installation if needed"
    echo ""
    echo "To configure static IP manually, see:"
    echo "  - NetworkManager: nmtui or nmcli"
    echo "  - systemd-networkd: /etc/systemd/network/*.network files"
    echo ""
    read -p "Press Enter to continue installation..."
fi

# Print access URLs
echo ""
echo "=========================================="
echo "  Access URLs (after installation)"
echo "=========================================="
echo -e "${GREEN}Web UI:      http://${CHOSEN_IP}:8080${NC}"
echo -e "${GREEN}rtl_tcp:     ${CHOSEN_IP}:1234${NC}"
echo "=========================================="
echo ""

# Ensure swap is 4GB - check if dphys-swapfile is available
log_info "Checking swap configuration..."
CURRENT_SWAP=$(free -m 2>/dev/null | awk '/^Swap:/ {print $2}')

if [ -z "$CURRENT_SWAP" ]; then
    CURRENT_SWAP=0
fi

if command -v dphys-swapfile &> /dev/null && [ -f /etc/dphys-swapfile ]; then
    if [ "$CURRENT_SWAP" -lt "$SWAP_SIZE_MB" ]; then
        log_info "Current swap: ${CURRENT_SWAP} MB, creating ${SWAP_SIZE_MB} MB swap..."
        
        # Turn off existing swap if any
        sudo dphys-swapfile swapoff 2>/dev/null || true
        
        # Configure swap size
        if sudo sed -i "s/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=${SWAP_SIZE_MB}/" /etc/dphys-swapfile 2>/dev/null; then
            # Setup and start swap
            if sudo dphys-swapfile setup 2>&1 | tee -a "$INSTALL_LOG" && \
               sudo dphys-swapfile swapon 2>&1 | tee -a "$INSTALL_LOG"; then
                log_success "Swap configured: ${SWAP_SIZE_MB} MB"
            else
                log_warning "Failed to configure swap with dphys-swapfile"
                log_info "Installation will continue - ensure you have enough RAM"
            fi
        else
            log_warning "Could not modify /etc/dphys-swapfile"
        fi
    else
        log_success "Swap already configured: ${CURRENT_SWAP} MB"
    fi
else
    log_warning "dphys-swapfile not found - skipping swap configuration"
    log_warning "Current swap: ${CURRENT_SWAP} MB"
    if [ "$CURRENT_SWAP" -lt 2048 ]; then
        log_warning "WARNING: Low swap space may cause build failures!"
        log_info "Consider creating swap manually or ensure sufficient RAM"
        echo ""
        read -p "Press Enter to continue anyway, or Ctrl+C to abort..."
    fi
fi

# APT update - check if apt-get is available
log_info "Updating package lists..."
if command -v apt-get &> /dev/null; then
    if sudo apt-get update 2>&1 | tee -a "$INSTALL_LOG"; then
        log_success "Package lists updated"
    else
        log_warning "apt-get update had warnings, continuing..."
    fi
else
    error_exit "apt-get not found - this installer requires a Debian-based system"
fi

# APT Install - Pass 1: Build tools
log_info "Installing build tools (Pass 1/2)..."
if nice -n 19 sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-venv \
    python3-pip \
    pkg-config \
    git \
    2>&1 | tee -a "$INSTALL_LOG"; then
    log_success "Build tools installed"
else
    log_error "Failed to install some build tools"
    log_info "Attempting to continue..."
fi

# Verify critical tools
if ! command -v python3 &> /dev/null; then
    error_exit "python3 not found - cannot continue"
fi
if ! command -v git &> /dev/null; then
    log_warning "git not installed - some features may not work"
fi

# APT Install - Pass 2: Runtime dependencies
log_info "Installing runtime dependencies (Pass 2/2)..."
if nice -n 19 sudo apt-get install -y \
    rtl-sdr \
    librtlsdr-dev \
    sox \
    libsox-fmt-all \
    portaudio19-dev \
    ffmpeg \
    jq \
    logrotate \
    2>&1 | tee -a "$INSTALL_LOG"; then
    log_success "Runtime dependencies installed"
else
    log_warning "Some runtime dependencies failed to install"
    log_info "Checking critical components..."
fi

# Verify critical runtime dependencies
MISSING_DEPS=()
command -v rtl_fm &> /dev/null || MISSING_DEPS+=("rtl-sdr")
command -v ffmpeg &> /dev/null || MISSING_DEPS+=("ffmpeg")
command -v sox &> /dev/null || MISSING_DEPS+=("sox")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    log_warning "Missing critical dependencies: ${MISSING_DEPS[*]}"
    log_warning "Scanner functionality will be limited without these"
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        error_exit "Installation aborted by user"
    fi
fi

# Install Node.js 18.x LTS
log_info "Installing Node.js 18.x LTS..."
if ! command -v node &> /dev/null; then
    log_info "Downloading NodeSource setup script..."
    if curl -fsSL https://deb.nodesource.com/setup_18.x -o /tmp/node_setup.sh 2>&1 | tee -a "$INSTALL_LOG"; then
        if sudo -E bash /tmp/node_setup.sh 2>&1 | tee -a "$INSTALL_LOG"; then
            if nice -n 19 sudo apt-get install -y nodejs 2>&1 | tee -a "$INSTALL_LOG"; then
                log_success "Node.js installed: $(node --version 2>/dev/null || echo 'version unknown')"
            else
                log_error "Failed to install Node.js"
                error_exit "Node.js is required for building the frontend"
            fi
        else
            log_error "Failed to set up NodeSource repository"
            error_exit "Cannot install Node.js"
        fi
        rm -f /tmp/node_setup.sh
    else
        log_error "Failed to download NodeSource setup script"
        log_info "Attempting to install nodejs from default repositories..."
        if sudo apt-get install -y nodejs npm 2>&1 | tee -a "$INSTALL_LOG"; then
            log_success "Node.js installed from default repos: $(node --version 2>/dev/null || echo 'version unknown')"
        else
            error_exit "Failed to install Node.js"
        fi
    fi
else
    NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
    log_success "Node.js already installed: ${NODE_VERSION}"
fi

# Verify node and npm are available
if ! command -v node &> /dev/null; then
    error_exit "node command not found after installation"
fi
if ! command -v npm &> /dev/null; then
    log_warning "npm not found - attempting to install..."
    sudo apt-get install -y npm 2>&1 | tee -a "$INSTALL_LOG" || log_warning "npm install failed"
fi

# Create Python virtual environment
log_info "Creating Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    if python3 -m venv "$VENV_DIR" 2>&1 | tee -a "$INSTALL_LOG"; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
        log_info "Attempting to install python3-venv..."
        if sudo apt-get install -y python3-venv 2>&1 | tee -a "$INSTALL_LOG"; then
            if python3 -m venv "$VENV_DIR" 2>&1 | tee -a "$INSTALL_LOG"; then
                log_success "Virtual environment created after installing python3-venv"
            else
                error_exit "Failed to create virtual environment"
            fi
        else
            error_exit "Cannot create virtual environment"
        fi
    fi
else
    log_success "Virtual environment already exists"
fi

# Activate venv
if [ -f "${VENV_DIR}/bin/activate" ]; then
    source "${VENV_DIR}/bin/activate"
    log_info "Virtual environment activated"
else
    error_exit "Virtual environment activation script not found"
fi

# Upgrade pip
log_info "Upgrading pip..."
nice -n 19 pip install --upgrade pip | tee -a "$INSTALL_LOG"

# Install Python packages with --prefer-binary
log_info "Installing Python packages (this may take several minutes)..."
nice -n 19 pip install --prefer-binary -r "${BASE_DIR}/requirements.txt" 2>&1 | tee -a "$INSTALL_LOG" || {
    log_warning "Some packages may have failed. Retrying..."
    nice -n 19 pip install --prefer-binary -r "${BASE_DIR}/requirements.txt" 2>&1 | tee -a "$INSTALL_LOG"
}

log_success "Python packages installed"

# Build React frontend
log_info "Building React frontend (this may take several minutes)..."

# Check if server directory exists
if [ ! -d "${BASE_DIR}/server" ]; then
    log_error "Server directory not found: ${BASE_DIR}/server"
    error_exit "Frontend source files missing"
fi

cd "${BASE_DIR}/server"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    log_error "package.json not found in server directory"
    error_exit "Frontend configuration missing"
fi

# Install npm dependencies
log_info "Installing npm dependencies..."
if command -v ionice &> /dev/null; then
    IONICE_CMD="ionice -c3"
else
    IONICE_CMD=""
    log_warning "ionice not available - skipping IO priority setting"
fi

if nice -n 19 $IONICE_CMD npm ci 2>&1 | tee -a "$INSTALL_LOG"; then
    log_success "npm dependencies installed"
else
    log_warning "npm ci failed, trying npm install..."
    if nice -n 19 $IONICE_CMD npm install 2>&1 | tee -a "$INSTALL_LOG"; then
        log_success "npm dependencies installed with npm install"
    else
        log_error "Failed to install npm dependencies"
        error_exit "Frontend build cannot proceed"
    fi
fi

# Build
log_info "Building React app..."
if nice -n 19 $IONICE_CMD npm run build 2>&1 | tee -a "$INSTALL_LOG"; then
    log_success "React app built"
else
    log_error "React build failed"
    log_warning "Check logs for details"
    error_exit "Frontend build failed"
fi

# Verify build output exists
if [ ! -d "dist" ]; then
    log_error "Build output directory (dist) not found"
    error_exit "React build did not produce expected output"
fi

# Copy build to backend static
log_info "Copying build to backend static directory..."
mkdir -p "${BASE_DIR}/backend/static"
rm -rf "${BASE_DIR}/backend/static"/*
cp -r "${BASE_DIR}/server/dist"/* "${BASE_DIR}/backend/static/"

log_success "Frontend deployed to backend/static"

# Clean up build artifacts to free space
log_info "Cleaning up build artifacts..."
rm -rf "${BASE_DIR}/server/node_modules"
rm -rf "${BASE_DIR}/server/dist"

log_success "Build artifacts cleaned"

# Make scripts executable
log_info "Making scripts executable..."
chmod +x "${BASE_DIR}/scripts"/*.sh

# Install systemd services
log_info "Installing systemd services..."

sudo cp "${BASE_DIR}/services/rtltcp.service" /etc/systemd/system/
sudo cp "${BASE_DIR}/services/scanner.service" /etc/systemd/system/
sudo cp "${BASE_DIR}/services/sdr-prune.service" /etc/systemd/system/
sudo cp "${BASE_DIR}/services/sdr-prune.timer" /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
log_info "Enabling systemd services..."
sudo systemctl enable rtltcp.service
sudo systemctl enable scanner.service
sudo systemctl enable sdr-prune.timer

log_success "Systemd services installed and enabled"

# Start services
log_info "Starting services..."
sudo systemctl start rtltcp.service

# Wait a moment for rtltcp to start
sleep 5

sudo systemctl start scanner.service

# Wait for scanner to start
sleep 5

# Start prune timer
sudo systemctl start sdr-prune.timer

log_success "Services started"

# Check service status
log_info "Checking service status..."
echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="

RTLTCP_STATUS=$(systemctl is-active rtltcp.service)
SCANNER_STATUS=$(systemctl is-active scanner.service)

if [ "$RTLTCP_STATUS" = "active" ]; then
    echo -e "${GREEN}✓ rtltcp.service: active${NC}"
else
    echo -e "${RED}✗ rtltcp.service: ${RTLTCP_STATUS}${NC}"
    log_warning "rtltcp.service is not active. Check logs with: journalctl -u rtltcp.service -n 50"
fi

if [ "$SCANNER_STATUS" = "active" ]; then
    echo -e "${GREEN}✓ scanner.service: active${NC}"
else
    echo -e "${RED}✗ scanner.service: ${SCANNER_STATUS}${NC}"
    log_warning "scanner.service is not active. Check logs with: journalctl -u scanner.service -n 50"
fi

echo "=========================================="
echo ""

# Show recent logs if services failed
if [ "$RTLTCP_STATUS" != "active" ]; then
    log_warning "rtltcp.service logs:"
    sudo journalctl -u rtltcp.service -n 20 --no-pager | tee -a "$INSTALL_LOG"
fi

if [ "$SCANNER_STATUS" != "active" ]; then
    log_warning "scanner.service logs:"
    sudo journalctl -u scanner.service -n 20 --no-pager | tee -a "$INSTALL_LOG"
fi

# Final summary
echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
log_success "Installation completed successfully!"
echo ""
echo "Access URLs:"
echo -e "  ${GREEN}Web UI:      http://${CHOSEN_IP}:8080${NC}"
echo -e "  ${GREEN}rtl_tcp:     ${CHOSEN_IP}:1234${NC}"
echo ""
echo "Useful commands:"
echo "  Check status:      sudo systemctl status rtltcp scanner"
echo "  View logs:         tail -f ${LOGS_DIR}/backend.log"
echo "  Run diagnostics:   ${BASE_DIR}/scripts/diagnostics.sh"
echo "  Restart services:  sudo systemctl restart rtltcp scanner"
echo ""
echo "Installation log: ${INSTALL_LOG}"
echo ""
echo "=========================================="
echo ""

log "Installation script completed"
