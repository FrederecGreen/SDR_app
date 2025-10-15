import React from 'react'
import { Activity, Cpu, HardDrive, Zap, AlertTriangle, Radio, Disc } from 'lucide-react'
import './Dashboard.css'

function Dashboard({ systemStatus }) {
  if (!systemStatus) {
    return <div className="loading">Loading system status...</div>
  }

  const { resources, rtltcp_running, scanner_running, scan_active, throttle_active, throttle_reason, usb_errors, active_detections, total_recordings, ip_address } = systemStatus

  const getStatusColor = (value, threshold) => {
    if (value >= threshold) return 'danger'
    if (value >= threshold * 0.8) return 'warning'
    return 'success'
  }

  return (
    <div className="dashboard" data-testid="dashboard">
      <div className="dashboard-header">
        <h2>System Dashboard</h2>
        <div className="ip-badge">
          <span>IP: {ip_address}</span>
        </div>
      </div>

      {/* Service Status */}
      <div className="status-grid">
        <div className="card status-card">
          <div className="status-icon">
            <Radio size={24} />
          </div>
          <div className="status-info">
            <h3>rtl_tcp Server</h3>
            <span className={`badge badge-${rtltcp_running ? 'success' : 'danger'}`} data-testid="rtltcp-status">
              {rtltcp_running ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        <div className="card status-card">
          <div className="status-icon">
            <Activity size={24} />
          </div>
          <div className="status-info">
            <h3>Scanner Service</h3>
            <span className={`badge badge-${scanner_running ? 'success' : 'danger'}`} data-testid="scanner-status">
              {scanner_running ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        <div className="card status-card">
          <div className="status-icon">
            <Zap size={24} />
          </div>
          <div className="status-info">
            <h3>Scan Active</h3>
            <span className={`badge badge-${scan_active ? 'success' : 'info'}`} data-testid="scan-active-status">
              {scan_active ? 'Scanning' : 'Idle'}
            </span>
          </div>
        </div>

        <div className="card status-card">
          <div className="status-icon">
            <Disc size={24} />
          </div>
          <div className="status-info">
            <h3>Detections</h3>
            <span className="badge badge-info" data-testid="active-detections">
              {active_detections} active
            </span>
          </div>
        </div>
      </div>

      {/* Throttle Warning */}
      {throttle_active && (
        <div className="card alert-card" data-testid="throttle-warning">
          <AlertTriangle size={20} />
          <div>
            <strong>Adaptive Throttle Active</strong>
            <p>{throttle_reason}</p>
          </div>
        </div>
      )}

      {/* USB Errors */}
      {usb_errors > 0 && (
        <div className="card alert-card" data-testid="usb-errors">
          <AlertTriangle size={20} />
          <div>
            <strong>USB Errors Detected</strong>
            <p>{usb_errors} USB errors logged. Check dmesg for details.</p>
          </div>
        </div>
      )}

      {/* Resource Monitors */}
      <div className="resources-grid">
        {/* CPU */}
        <div className="card resource-card">
          <div className="resource-header">
            <Cpu size={20} />
            <h3>CPU Usage</h3>
          </div>
          <div className="resource-meter">
            <div className="meter-label">
              <span>Total</span>
              <span className={`value value-${getStatusColor(resources.cpu_percent, 80)}`} data-testid="cpu-percent">
                {resources.cpu_percent.toFixed(1)}%
              </span>
            </div>
            <div className="meter-bar">
              <div 
                className={`meter-fill meter-fill-${getStatusColor(resources.cpu_percent, 80)}`}
                style={{ width: `${Math.min(resources.cpu_percent, 100)}%` }}
              />
            </div>
          </div>
          <div className="resource-details">
            <div><span>User:</span><span data-testid="cpu-user">{resources.cpu_user.toFixed(1)}%</span></div>
            <div><span>System:</span><span data-testid="cpu-system">{resources.cpu_system.toFixed(1)}%</span></div>
            <div><span>IO Wait:</span><span data-testid="cpu-iowait">{resources.cpu_iowait.toFixed(1)}%</span></div>
          </div>
        </div>

        {/* Memory */}
        <div className="card resource-card">
          <div className="resource-header">
            <Activity size={20} />
            <h3>Memory</h3>
          </div>
          <div className="resource-meter">
            <div className="meter-label">
              <span>Used</span>
              <span className={`value value-${getStatusColor(resources.memory_percent, 85)}`} data-testid="memory-percent">
                {resources.memory_percent.toFixed(1)}%
              </span>
            </div>
            <div className="meter-bar">
              <div 
                className={`meter-fill meter-fill-${getStatusColor(resources.memory_percent, 85)}`}
                style={{ width: `${Math.min(resources.memory_percent, 100)}%` }}
              />
            </div>
          </div>
          <div className="resource-details">
            <div><span>Used:</span><span data-testid="memory-used">{resources.memory_used_mb.toFixed(0)} MB</span></div>
            <div><span>Available:</span><span data-testid="memory-available">{resources.memory_available_mb.toFixed(0)} MB</span></div>
          </div>
        </div>

        {/* Swap */}
        <div className="card resource-card">
          <div className="resource-header">
            <HardDrive size={20} />
            <h3>Swap</h3>
          </div>
          <div className="resource-meter">
            <div className="meter-label">
              <span>Used</span>
              <span className={`value value-${getStatusColor(resources.swap_percent, 75)}`} data-testid="swap-percent">
                {resources.swap_percent.toFixed(1)}%
              </span>
            </div>
            <div className="meter-bar">
              <div 
                className={`meter-fill meter-fill-${getStatusColor(resources.swap_percent, 75)}`}
                style={{ width: `${Math.min(resources.swap_percent, 100)}%` }}
              />
            </div>
          </div>
          <div className="resource-details">
            <div><span>Used:</span><span data-testid="swap-used">{resources.swap_used_mb.toFixed(0)} MB</span></div>
            <div><span>Total:</span><span data-testid="swap-total">{resources.swap_total_mb.toFixed(0)} MB</span></div>
          </div>
        </div>

        {/* Disk */}
        <div className="card resource-card">
          <div className="resource-header">
            <HardDrive size={20} />
            <h3>Storage</h3>
          </div>
          <div className="resource-meter">
            <div className="meter-label">
              <span>Disk Used</span>
              <span className={`value value-${getStatusColor(resources.disk_percent, 90)}`} data-testid="disk-percent">
                {resources.disk_percent.toFixed(1)}%
              </span>
            </div>
            <div className="meter-bar">
              <div 
                className={`meter-fill meter-fill-${getStatusColor(resources.disk_percent, 90)}`}
                style={{ width: `${Math.min(resources.disk_percent, 100)}%` }}
              />
            </div>
          </div>
          <div className="resource-details">
            <div><span>Used:</span><span data-testid="disk-used">{resources.disk_used_gb.toFixed(1)} GB</span></div>
            <div><span>Total:</span><span data-testid="disk-total">{resources.disk_total_gb.toFixed(1)} GB</span></div>
            <div><span>Recordings:</span><span data-testid="recordings-size">{resources.recordings_size_gb.toFixed(2)} GB</span></div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="card statistics-card">
        <h3>Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Active Detections</span>
            <span className="stat-value">{active_detections}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Recordings</span>
            <span className="stat-value" data-testid="total-recordings">{total_recordings}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Recordings Size</span>
            <span className="stat-value">{resources.recordings_size_gb.toFixed(2)} GB</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
