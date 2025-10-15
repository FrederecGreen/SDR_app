"""Scanner control routes."""
from fastapi import APIRouter, HTTPException
from backend.app.models import (
    ScanStartRequest, 
    Detection, 
    FrequencyGroup,
    ConfigUpdateRequest
)
from backend.app.scanner.engine import scanner_engine
from backend.app.frequency_groups import get_all_groups
from backend.app.config import scanner_config, resource_thresholds
import logging
from typing import List, Dict

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/api/scanner", tags=["scanner"])

@router.post("/start")
async def start_scanner(request: ScanStartRequest):
    """Start scanning."""
    try:
        success = await scanner_engine.start_scan(
            frequency_groups=request.frequency_groups,
            custom_frequencies=request.custom_frequencies,
            dwell_seconds=request.dwell_seconds,
            squelch_db=request.squelch_db
        )
        
        if success:
            return {"status": "started", "message": "Scanner started successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to start scanner")
    
    except Exception as e:
        logger.error(f"Error starting scanner: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_scanner():
    """Stop scanning."""
    try:
        success = await scanner_engine.stop_scan()
        
        if success:
            return {"status": "stopped", "message": "Scanner stopped successfully"}
        else:
            return {"status": "not_running", "message": "Scanner was not running"}
    
    except Exception as e:
        logger.error(f"Error stopping scanner: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detections", response_model=List[Detection])
async def get_detections():
    """Get active frequency detections."""
    try:
        return scanner_engine.get_detections()
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frequency-groups", response_model=Dict[str, FrequencyGroup])
async def get_frequency_groups():
    """Get all available frequency groups."""
    try:
        return get_all_groups()
    except Exception as e:
        logger.error(f"Error getting frequency groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config():
    """Get current scanner configuration."""
    return {
        "scanner": scanner_config.dict(),
        "thresholds": resource_thresholds.dict()
    }

@router.post("/config")
async def update_config(request: ConfigUpdateRequest):
    """Update scanner configuration."""
    try:
        updated = []
        
        if request.dwell_seconds is not None:
            scanner_config.default_dwell_seconds = request.dwell_seconds
            updated.append("dwell_seconds")
        
        if request.squelch_db is not None:
            scanner_config.default_squelch_db = request.squelch_db
            updated.append("squelch_db")
        
        if request.chunk_duration_seconds is not None:
            scanner_config.chunk_duration_seconds = request.chunk_duration_seconds
            updated.append("chunk_duration_seconds")
        
        if request.retention_days is not None:
            scanner_config.retention_days = request.retention_days
            updated.append("retention_days")
        
        if request.storage_cap_gb is not None:
            scanner_config.storage_cap_gb = request.storage_cap_gb
            updated.append("storage_cap_gb")
        
        if request.cpu_threshold is not None:
            resource_thresholds.cpu_percent_max = request.cpu_threshold
            updated.append("cpu_threshold")
        
        if request.memory_threshold is not None:
            resource_thresholds.memory_percent_max = request.memory_threshold
            updated.append("memory_threshold")
        
        if request.io_wait_threshold is not None:
            resource_thresholds.io_wait_percent_max = request.io_wait_threshold
            updated.append("io_wait_threshold")
        
        return {
            "status": "updated",
            "fields": updated
        }
    
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
