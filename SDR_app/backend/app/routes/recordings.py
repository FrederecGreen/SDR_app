"""Recordings management routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.app.models import Recording
from backend.app.config import RECORDINGS_DIR
from datetime import datetime
from typing import List
import logging
import os

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/api/recordings", tags=["recordings"])

def parse_recording_filename(filename: str) -> dict:
    """Parse recording filename to extract metadata.
    
    Format: YYYYMMDD_HHMMSS_FREQ_LABEL.ogg
    """
    try:
        stem = filename.replace(".ogg", "")
        parts = stem.split("_")
        
        if len(parts) >= 3:
            timestamp_str = parts[0] + parts[1]  # YYYYMMDDHHMMSS
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            
            freq_str = parts[2].replace("_", ".")
            freq_mhz = float(freq_str)
            
            label = "_".join(parts[3:]) if len(parts) > 3 else "unknown"
            
            return {
                "timestamp": timestamp,
                "freq_mhz": freq_mhz,
                "label": label
            }
    except Exception as e:
        logger.warning(f"Failed to parse filename {filename}: {e}")
    
    return None

@router.get("", response_model=List[Recording])
async def list_recordings():
    """List all recordings."""
    try:
        recordings = []
        
        if not RECORDINGS_DIR.exists():
            return recordings
        
        for file_path in sorted(RECORDINGS_DIR.glob("*.ogg"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                stat = file_path.stat()
                metadata = parse_recording_filename(file_path.name)
                
                if metadata:
                    # Get duration from file (simple approximation: size / bitrate)
                    # 64 kbps = 8 KB/s, so duration ≈ file_size / 8000
                    duration_seconds = stat.st_size / 8000
                    
                    recording = Recording(
                        id=file_path.stem,
                        freq_mhz=metadata["freq_mhz"],
                        mode="nfm",  # Default, would need to parse from filename if stored
                        start_time=metadata["timestamp"],
                        end_time=metadata["timestamp"],  # Would need actual end time
                        duration_seconds=duration_seconds,
                        file_size_bytes=stat.st_size,
                        file_path=file_path.name,
                        label=metadata["label"]
                    )
                    recordings.append(recording)
            except Exception as e:
                logger.warning(f"Error processing recording {file_path}: {e}")
        
        return recordings
    
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{recording_id}")
async def get_recording(recording_id: str):
    """Download a recording."""
    file_path = RECORDINGS_DIR / f"{recording_id}.ogg"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return FileResponse(
        path=file_path,
        media_type="audio/ogg",
        filename=file_path.name
    )

@router.delete("/{recording_id}")
async def delete_recording(recording_id: str):
    """Delete a recording."""
    file_path = RECORDINGS_DIR / f"{recording_id}.ogg"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Recording not found")
    
    try:
        file_path.unlink()
        logger.info(f"Deleted recording: {recording_id}")
        return {"status": "deleted", "id": recording_id}
    except Exception as e:
        logger.error(f"Error deleting recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))
