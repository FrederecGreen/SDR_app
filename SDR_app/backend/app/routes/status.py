"""Status and diagnostics routes."""
from fastapi import APIRouter, HTTPException
from backend.app.models import SystemStatus, ResourceUsage
from backend.app.scanner.resource_monitor import resource_monitor
from backend.app.scanner.engine import scanner_engine
from backend.app.config import throttle_state, RECORDINGS_DIR
import subprocess
import logging
import socket

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/api", tags=["status"])

def get_ip_address() -> str:
    """Get system IP address."""
    try:
        result = subprocess.run(
            ["hostname", "-I"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            return ips[0] if ips else "unknown"
    except:
        pass
    return "unknown"

def check_service_status(service_name: str) -> bool:
    """Check if systemd service is running."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout.strip() == "active"
    except:
        return False

@router.get("/status", response_model=SystemStatus)
async def get_status():
    """Get complete system status."""
    try:
        # Get resource usage
        resources = resource_monitor.get_resource_usage()
        
        # Check services
        rtltcp_running = check_service_status("rtltcp.service")
        scanner_service_running = check_service_status("scanner.service")
        
        # Get scanner state
        scan_active = scanner_engine.is_running()
        
        # Count detections and recordings
        detections = scanner_engine.get_detections()
        
        recordings_count = 0
        if RECORDINGS_DIR.exists():
            recordings_count = len(list(RECORDINGS_DIR.glob("*.ogg")))
        
        # USB errors
        usb_errors = resource_monitor.check_usb_errors()
        
        # IP address
        ip_address = get_ip_address()
        
        return SystemStatus(
            rtltcp_running=rtltcp_running,
            scanner_running=scanner_service_running,
            scan_active=scan_active,
            resources=resources,
            throttle_active=throttle_state.active,
            throttle_reason=throttle_state.reason,
            usb_errors=usb_errors,
            active_detections=len(detections),
            total_recordings=recordings_count,
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(name: str = "backend", lines: int = 100):
    """Get log file tail."""
    from backend.app.config import LOGS_DIR
    
    valid_logs = ["backend", "scanner", "rtltcp", "install"]
    if name not in valid_logs:
        raise HTTPException(status_code=400, detail=f"Invalid log name. Must be one of: {valid_logs}")
    
    log_file = LOGS_DIR / f"{name}.log"
    
    if not log_file.exists():
        return {"log": f"Log file not found: {log_file}"}
    
    try:
        # Read last N lines
        result = subprocess.run(
            ["tail", "-n", str(lines), str(log_file)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {"log": result.stdout}
    except Exception as e:
        logger.error(f"Error reading log: {e}")
        raise HTTPException(status_code=500, detail=str(e))
