#!/bin/bash
# Storage pruning script for SDR_app
# Removes recordings older than retention period and enforces storage cap

set -e

BASE_DIR="/home/pi/SDR_app"
RECORDINGS_DIR="${BASE_DIR}/recordings"
LOG_FILE="${BASE_DIR}/logs/prune.log"

# Default values (can be overridden by config)
RETENTION_DAYS=14
STORAGE_CAP_GB=60

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting storage pruning" >> "$LOG_FILE"

# Check if recordings directory exists
if [ ! -d "$RECORDINGS_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Recordings directory does not exist" >> "$LOG_FILE"
    exit 0
fi

# Remove files older than retention period
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Removing files older than ${RETENTION_DAYS} days..." >> "$LOG_FILE"
FILES_REMOVED=$(find "$RECORDINGS_DIR" -name "*.ogg" -type f -mtime +${RETENTION_DAYS} -delete -print | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Removed ${FILES_REMOVED} old files" >> "$LOG_FILE"

# Check storage usage
STORAGE_USED=$(du -sb "$RECORDINGS_DIR" 2>/dev/null | cut -f1)
STORAGE_USED_GB=$((STORAGE_USED / 1024 / 1024 / 1024))

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Current storage: ${STORAGE_USED_GB} GB / ${STORAGE_CAP_GB} GB cap" >> "$LOG_FILE"

# If over cap, remove oldest files until under cap
if [ $STORAGE_USED_GB -gt $STORAGE_CAP_GB ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Storage cap exceeded, removing oldest files..." >> "$LOG_FILE"
    
    # Remove oldest files one by one until under cap
    REMOVED_COUNT=0
    while [ $STORAGE_USED_GB -gt $STORAGE_CAP_GB ]; do
        OLDEST_FILE=$(find "$RECORDINGS_DIR" -name "*.ogg" -type f -printf '%T+ %p\n' | sort | head -n 1 | cut -d' ' -f2-)
        
        if [ -z "$OLDEST_FILE" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] No more files to remove" >> "$LOG_FILE"
            break
        fi
        
        rm -f "$OLDEST_FILE"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
        
        STORAGE_USED=$(du -sb "$RECORDINGS_DIR" 2>/dev/null | cut -f1)
        STORAGE_USED_GB=$((STORAGE_USED / 1024 / 1024 / 1024))
    done
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Removed ${REMOVED_COUNT} files to enforce storage cap" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Storage pruning complete" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
