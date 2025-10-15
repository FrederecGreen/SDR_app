"""Resource monitoring and adaptive throttling for Pi2B."""
import psutil
import time
import logging
from typing import Dict, Optional
from backend.app.config import resource_thresholds, throttle_state, scanner_config
from backend.app.models import ResourceUsage

logger = logging.getLogger("scanner")

class ResourceMonitor:
    """Monitor system resources and trigger adaptive throttling."""
    
    def __init__(self):
        self.baseline_swap_mb = 0
        self.last_throttle_time = 0
        self.throttle_hysteresis = resource_thresholds.hysteresis_seconds
        self.usb_error_count = 0
        
        # Record baseline
        self._record_baseline()
    
    def _record_baseline(self):
        """Record baseline resource usage."""
        try:
            swap = psutil.swap_memory()
            self.baseline_swap_mb = swap.used / (1024 * 1024)
            logger.info(f"Baseline swap usage: {self.baseline_swap_mb:.1f} MB")
        except Exception as e:
            logger.error(f"Failed to record baseline: {e}")
    
    def get_resource_usage(self) -> ResourceUsage:
        """Get current resource usage."""
        try:
            # CPU usage (per-core times)
            cpu_times = psutil.cpu_times_percent(interval=0.5)
            cpu_percent = psutil.cpu_percent(interval=0)
            
            # Memory
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk (recordings directory)
            from backend.app.config import RECORDINGS_DIR, BASE_DIR
            disk = psutil.disk_usage(str(BASE_DIR))
            
            # Calculate recordings size
            recordings_size_bytes = 0
            if RECORDINGS_DIR.exists():
                for f in RECORDINGS_DIR.rglob("*.ogg"):
                    try:
                        recordings_size_bytes += f.stat().st_size
                    except:
                        pass
            
            return ResourceUsage(
                cpu_percent=cpu_percent,
                cpu_user=cpu_times.user if hasattr(cpu_times, 'user') else 0,
                cpu_system=cpu_times.system if hasattr(cpu_times, 'system') else 0,
                cpu_iowait=cpu_times.iowait if hasattr(cpu_times, 'iowait') else 0,
                memory_used_mb=mem.used / (1024 * 1024),
                memory_available_mb=mem.available / (1024 * 1024),
                memory_percent=mem.percent,
                swap_used_mb=swap.used / (1024 * 1024),
                swap_total_mb=swap.total / (1024 * 1024),
                swap_percent=swap.percent,
                disk_used_gb=disk.used / (1024 * 1024 * 1024),
                disk_total_gb=disk.total / (1024 * 1024 * 1024),
                disk_percent=disk.percent,
                recordings_size_gb=recordings_size_bytes / (1024 * 1024 * 1024)
            )
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            # Return safe defaults
            return ResourceUsage(
                cpu_percent=0, cpu_user=0, cpu_system=0, cpu_iowait=0,
                memory_used_mb=0, memory_available_mb=0, memory_percent=0,
                swap_used_mb=0, swap_total_mb=0, swap_percent=0,
                disk_used_gb=0, disk_total_gb=0, disk_percent=0,
                recordings_size_gb=0
            )
    
    def check_usb_errors(self) -> int:
        """Check for USB errors in dmesg (simple count)."""
        try:
            import subprocess
            result = subprocess.run(
                ["dmesg", "-T"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Count USB-related error lines
                error_count = sum(1 for line in result.stdout.lower().split('\n') 
                                if 'usb' in line and ('error' in line or 'fail' in line))
                return error_count
        except Exception as e:
            logger.warning(f"Could not check USB errors: {e}")
        return 0
    
    def should_throttle(self, resources: ResourceUsage) -> tuple[bool, Optional[str]]:
        """Determine if throttling should be activated."""
        reasons = []
        
        # Check CPU usage
        if resources.cpu_percent > resource_thresholds.cpu_percent_max:
            reasons.append(f"CPU: {resources.cpu_percent:.1f}% > {resource_thresholds.cpu_percent_max}%")
        
        # Check IO wait
        if resources.cpu_iowait > resource_thresholds.io_wait_percent_max:
            reasons.append(f"IO wait: {resources.cpu_iowait:.1f}% > {resource_thresholds.io_wait_percent_max}%")
        
        # Check memory
        if resources.memory_percent > resource_thresholds.memory_percent_max:
            reasons.append(f"Memory: {resources.memory_percent:.1f}% > {resource_thresholds.memory_percent_max}%")
        
        # Check swap growth
        swap_growth = resources.swap_used_mb - self.baseline_swap_mb
        if swap_growth > resource_thresholds.swap_growth_mb_max:
            reasons.append(f"Swap growth: {swap_growth:.1f} MB > {resource_thresholds.swap_growth_mb_max} MB")
        
        # Check USB errors
        current_usb_errors = self.check_usb_errors()
        if current_usb_errors > self.usb_error_count + resource_thresholds.usb_error_count_max:
            reasons.append(f"USB errors: {current_usb_errors} new errors")
            self.usb_error_count = current_usb_errors
        
        if reasons:
            return True, "; ".join(reasons)
        return False, None
    
    def should_release_throttle(self, resources: ResourceUsage) -> bool:
        """Determine if throttling can be released (with hysteresis)."""
        if not throttle_state.active:
            return False
        
        # Check if enough time has passed since throttle activation
        if time.time() - self.last_throttle_time < self.throttle_hysteresis:
            return False
        
        # Check if all conditions are below thresholds (with 10% margin)
        margin = 0.9
        if (resources.cpu_percent < resource_thresholds.cpu_percent_max * margin and
            resources.cpu_iowait < resource_thresholds.io_wait_percent_max * margin and
            resources.memory_percent < resource_thresholds.memory_percent_max * margin):
            return True
        
        return False
    
    def apply_throttle(self, reason: str):
        """Apply throttling measures."""
        if not throttle_state.active:
            logger.warning(f"Activating throttle: {reason}")
            throttle_state.active = True
            throttle_state.reason = reason
            throttle_state.dwell_multiplier = 1.5  # Increase dwell by 50%
            throttle_state.chunk_duration_seconds = 45  # Increase chunk to 45s
            throttle_state.skip_frequencies = 1  # Skip every other frequency
            self.last_throttle_time = time.time()
        else:
            # Already throttled, escalate if needed
            if throttle_state.chunk_duration_seconds < 60:
                throttle_state.chunk_duration_seconds = 60
                throttle_state.skip_frequencies = 2  # Skip 2 out of 3 frequencies
                logger.warning("Escalating throttle: increased chunk to 60s, skip 2/3 frequencies")
    
    def release_throttle(self):
        """Release throttling measures."""
        if throttle_state.active:
            logger.info("Releasing throttle: conditions normalized")
            throttle_state.active = False
            throttle_state.reason = None
            throttle_state.dwell_multiplier = 1.0
            throttle_state.chunk_duration_seconds = scanner_config.chunk_duration_seconds
            throttle_state.skip_frequencies = 0
            throttle_state.paused = False
    
    def monitor_and_adjust(self) -> ResourceUsage:
        """Monitor resources and adjust throttling."""
        resources = self.get_resource_usage()
        
        should_throttle, reason = self.should_throttle(resources)
        
        if should_throttle:
            self.apply_throttle(reason)
        elif self.should_release_throttle(resources):
            self.release_throttle()
        
        return resources

# Global monitor instance
resource_monitor = ResourceMonitor()
