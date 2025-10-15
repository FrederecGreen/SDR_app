import React, { useState, useEffect } from 'react'
import { Settings, Save, FileText } from 'lucide-react'
import './AdvancedSettings.css'

function AdvancedSettings() {
  const [config, setConfig] = useState(null)
  const [formData, setFormData] = useState({
    dwell_seconds: '',
    squelch_db: '',
    chunk_duration_seconds: '',
    retention_days: '',
    storage_cap_gb: '',
    cpu_threshold: '',
    memory_threshold: '',
    io_wait_threshold: ''
  })
  const [logs, setLogs] = useState({ backend: '', scanner: '', rtltcp: '' })
  const [selectedLog, setSelectedLog] = useState('backend')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/scanner/config')
      if (response.ok) {
        const data = await response.json()
        setConfig(data)
        setFormData({
          dwell_seconds: data.scanner.default_dwell_seconds,
          squelch_db: data.scanner.default_squelch_db,
          chunk_duration_seconds: data.scanner.chunk_duration_seconds,
          retention_days: data.scanner.retention_days,
          storage_cap_gb: data.scanner.storage_cap_gb,
          cpu_threshold: data.thresholds.cpu_percent_max,
          memory_threshold: data.thresholds.memory_percent_max,
          io_wait_threshold: data.thresholds.io_wait_percent_max
        })
      }
    } catch (error) {
      console.error('Error fetching config:', error)
    }
  }

  const fetchLogs = async (logName) => {
    try {
      const response = await fetch(`/api/logs?name=${logName}&lines=100`)
      if (response.ok) {
        const data = await response.json()
        setLogs(prev => ({ ...prev, [logName]: data.log }))
      }
    } catch (error) {
      console.error('Error fetching logs:', error)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    try {
      const response = await fetch('/api/scanner/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dwell_seconds: parseFloat(formData.dwell_seconds),
          squelch_db: parseInt(formData.squelch_db),
          chunk_duration_seconds: parseInt(formData.chunk_duration_seconds),
          retention_days: parseInt(formData.retention_days),
          storage_cap_gb: parseInt(formData.storage_cap_gb),
          cpu_threshold: parseFloat(formData.cpu_threshold),
          memory_threshold: parseFloat(formData.memory_threshold),
          io_wait_threshold: parseFloat(formData.io_wait_threshold)
        })
      })

      if (response.ok) {
        setMessage('Configuration saved successfully!')
        setTimeout(() => setMessage(''), 3000)
      } else {
        setMessage('Failed to save configuration')
      }
    } catch (error) {
      console.error('Error saving config:', error)
      setMessage('Error saving configuration')
    } finally {
      setSaving(false)
    }
  }

  const handleLogChange = (logName) => {
    setSelectedLog(logName)
    if (!logs[logName]) {
      fetchLogs(logName)
    }
  }

  if (!config) {
    return <div className="loading">Loading configuration...</div>
  }

  return (
    <div className="advanced-settings" data-testid="advanced-settings">
      <div className="settings-header">
        <h2>Advanced Settings</h2>
      </div>

      <div className="settings-grid">
        {/* Scanner Configuration */}
        <div className="card settings-section">
          <div className="section-header">
            <Settings size={20} />
            <h3>Scanner Parameters</h3>
          </div>

          <div className="settings-form">
            <div className="form-group">
              <label>Dwell Time (seconds)</label>
              <input
                type="number"
                value={formData.dwell_seconds}
                onChange={(e) => setFormData({ ...formData, dwell_seconds: e.target.value })}
                step="0.1"
                min="0.1"
                data-testid="dwell-seconds-input"
              />
              <span className="form-help">Time to listen on each frequency</span>
            </div>

            <div className="form-group">
              <label>Squelch Level (dB)</label>
              <input
                type="number"
                value={formData.squelch_db}
                onChange={(e) => setFormData({ ...formData, squelch_db: e.target.value })}
                min="0"
                max="100"
                data-testid="squelch-input"
              />
              <span className="form-help">Signal threshold for detection (0-100)</span>
            </div>

            <div className="form-group">
              <label>Chunk Duration (seconds)</label>
              <input
                type="number"
                value={formData.chunk_duration_seconds}
                onChange={(e) => setFormData({ ...formData, chunk_duration_seconds: e.target.value })}
                min="10"
                max="60"
                data-testid="chunk-duration-input"
              />
              <span className="form-help">Recording chunk size (10-60 seconds)</span>
            </div>
          </div>
        </div>

        {/* Storage Configuration */}
        <div className="card settings-section">
          <div className="section-header">
            <Settings size={20} />
            <h3>Storage Management</h3>
          </div>

          <div className="settings-form">
            <div className="form-group">
              <label>Retention Period (days)</label>
              <input
                type="number"
                value={formData.retention_days}
                onChange={(e) => setFormData({ ...formData, retention_days: e.target.value })}
                min="1"
                data-testid="retention-days-input"
              />
              <span className="form-help">Keep recordings for this many days</span>
            </div>

            <div className="form-group">
              <label>Storage Cap (GB)</label>
              <input
                type="number"
                value={formData.storage_cap_gb}
                onChange={(e) => setFormData({ ...formData, storage_cap_gb: e.target.value })}
                min="1"
                data-testid="storage-cap-input"
              />
              <span className="form-help">Maximum storage for all recordings</span>
            </div>
          </div>
        </div>

        {/* Throttle Thresholds */}
        <div className="card settings-section">
          <div className="section-header">
            <Settings size={20} />
            <h3>Adaptive Throttle Thresholds</h3>
          </div>

          <div className="settings-form">
            <div className="form-group">
              <label>CPU Threshold (%)</label>
              <input
                type="number"
                value={formData.cpu_threshold}
                onChange={(e) => setFormData({ ...formData, cpu_threshold: e.target.value })}
                min="10"
                max="100"
                step="1"
                data-testid="cpu-threshold-input"
              />
              <span className="form-help">Throttle when CPU usage exceeds this</span>
            </div>

            <div className="form-group">
              <label>Memory Threshold (%)</label>
              <input
                type="number"
                value={formData.memory_threshold}
                onChange={(e) => setFormData({ ...formData, memory_threshold: e.target.value })}
                min="10"
                max="100"
                step="1"
                data-testid="memory-threshold-input"
              />
              <span className="form-help">Throttle when memory usage exceeds this</span>
            </div>

            <div className="form-group">
              <label>IO Wait Threshold (%)</label>
              <input
                type="number"
                value={formData.io_wait_threshold}
                onChange={(e) => setFormData({ ...formData, io_wait_threshold: e.target.value })}
                min="1"
                max="50"
                step="0.1"
                data-testid="io-wait-threshold-input"
              />
              <span className="form-help">Throttle when IO wait exceeds this</span>
            </div>
          </div>
        </div>

        {/* Logs Viewer */}
        <div className="card settings-section logs-section">
          <div className="section-header">
            <FileText size={20} />
            <h3>System Logs</h3>
          </div>

          <div className="logs-controls">
            <button
              className={`btn ${selectedLog === 'backend' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleLogChange('backend')}
              data-testid="log-backend-btn"
            >
              Backend
            </button>
            <button
              className={`btn ${selectedLog === 'scanner' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleLogChange('scanner')}
              data-testid="log-scanner-btn"
            >
              Scanner
            </button>
            <button
              className={`btn ${selectedLog === 'rtltcp' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleLogChange('rtltcp')}
              data-testid="log-rtltcp-btn"
            >
              rtl_tcp
            </button>
          </div>

          <div className="logs-viewer" data-testid="logs-viewer">
            <pre>{logs[selectedLog] || 'Click refresh to load logs...'}</pre>
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => fetchLogs(selectedLog)}
            data-testid="refresh-logs-btn"
          >
            Refresh Logs
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="settings-actions">
        {message && (
          <div className={`message ${message.includes('success') ? 'message-success' : 'message-error'}`}>
            {message}
          </div>
        )}
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
          data-testid="save-settings-btn"
        >
          <Save size={18} />
          <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
        </button>
      </div>
    </div>
  )
}

export default AdvancedSettings
