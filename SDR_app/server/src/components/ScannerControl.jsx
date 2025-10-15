import React, { useState, useEffect } from 'react'
import { Play, Square, Radio, Plus, X } from 'lucide-react'
import './ScannerControl.css'

function ScannerControl({ systemStatus, onStatusChange }) {
  const [frequencyGroups, setFrequencyGroups] = useState({})
  const [selectedGroups, setSelectedGroups] = useState([])
  const [customFrequencies, setCustomFrequencies] = useState([])
  const [newFreq, setNewFreq] = useState({ freq: '', mode: 'nfm', label: '' })
  const [detections, setDetections] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchFrequencyGroups()
    const interval = setInterval(fetchDetections, 2000)
    return () => clearInterval(interval)
  }, [])

  const fetchFrequencyGroups = async () => {
    try {
      const response = await fetch('/api/scanner/frequency-groups')
      if (response.ok) {
        const data = await response.json()
        setFrequencyGroups(data)
      }
    } catch (error) {
      console.error('Error fetching frequency groups:', error)
    }
  }

  const fetchDetections = async () => {
    if (systemStatus?.scan_active) {
      try {
        const response = await fetch('/api/scanner/detections')
        if (response.ok) {
          const data = await response.json()
          setDetections(data)
        }
      } catch (error) {
        console.error('Error fetching detections:', error)
      }
    }
  }

  const handleStartScan = async () => {
    if (selectedGroups.length === 0 && customFrequencies.length === 0) {
      alert('Please select at least one frequency group or add custom frequencies')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/scanner/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          frequency_groups: selectedGroups,
          custom_frequencies: customFrequencies.map(f => ({
            freq_mhz: parseFloat(f.freq),
            mode: f.mode,
            label: f.label || `${f.freq} MHz`
          }))
        })
      })

      if (response.ok) {
        onStatusChange()
      } else {
        const error = await response.json()
        alert('Failed to start scan: ' + (error.detail || 'Unknown error'))
      }
    } catch (error) {
      console.error('Error starting scan:', error)
      alert('Error starting scan')
    } finally {
      setLoading(false)
    }
  }

  const handleStopScan = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/scanner/stop', { method: 'POST' })
      if (response.ok) {
        setDetections([])
        onStatusChange()
      }
    } catch (error) {
      console.error('Error stopping scan:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleGroup = (groupName) => {
    setSelectedGroups(prev => 
      prev.includes(groupName)
        ? prev.filter(g => g !== groupName)
        : [...prev, groupName]
    )
  }

  const addCustomFrequency = () => {
    const freq = parseFloat(newFreq.freq)
    if (isNaN(freq) || freq < 24 || freq > 1766) {
      alert('Please enter a valid frequency between 24 and 1766 MHz')
      return
    }

    setCustomFrequencies([...customFrequencies, { ...newFreq }])
    setNewFreq({ freq: '', mode: 'nfm', label: '' })
  }

  const removeCustomFrequency = (index) => {
    setCustomFrequencies(customFrequencies.filter((_, i) => i !== index))
  }

  const isScanning = systemStatus?.scan_active

  return (
    <div className="scanner-control" data-testid="scanner-control">
      <div className="scanner-header">
        <h2>Scanner Control</h2>
        <div className="scanner-actions">
          {!isScanning ? (
            <button
              className="btn btn-primary"
              onClick={handleStartScan}
              disabled={loading}
              data-testid="start-scan-btn"
            >
              <Play size={18} />
              <span>Start Scan</span>
            </button>
          ) : (
            <button
              className="btn btn-danger"
              onClick={handleStopScan}
              disabled={loading}
              data-testid="stop-scan-btn"
            >
              <Square size={18} />
              <span>Stop Scan</span>
            </button>
          )}
        </div>
      </div>

      <div className="scanner-grid">
        {/* Frequency Groups Selection */}
        <div className="card">
          <h3>Frequency Groups</h3>
          <div className="groups-list" data-testid="frequency-groups-list">
            {Object.values(frequencyGroups).map(group => (
              <label key={group.name} className="group-item">
                <input
                  type="checkbox"
                  checked={selectedGroups.includes(group.name)}
                  onChange={() => toggleGroup(group.name)}
                  disabled={isScanning}
                  data-testid={`group-checkbox-${group.name}`}
                />
                <div className="group-info">
                  <span className="group-name">{group.display_name}</span>
                  <span className="group-desc">{group.description}</span>
                  <span className="group-count">{group.frequencies.length} frequencies</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Custom Frequencies */}
        <div className="card">
          <h3>Custom Frequencies</h3>
          {!isScanning && (
            <div className="custom-freq-input">
              <input
                type="number"
                placeholder="Frequency (MHz)"
                value={newFreq.freq}
                onChange={(e) => setNewFreq({ ...newFreq, freq: e.target.value })}
                step="0.001"
                min="24"
                max="1766"
                data-testid="custom-freq-input"
              />
              <select
                value={newFreq.mode}
                onChange={(e) => setNewFreq({ ...newFreq, mode: e.target.value })}
                data-testid="custom-mode-select"
              >
                <option value="nfm">NFM</option>
                <option value="fm">FM</option>
                <option value="wfm">WFM</option>
                <option value="am">AM</option>
              </select>
              <input
                type="text"
                placeholder="Label (optional)"
                value={newFreq.label}
                onChange={(e) => setNewFreq({ ...newFreq, label: e.target.value })}
                data-testid="custom-label-input"
              />
              <button
                className="btn btn-secondary"
                onClick={addCustomFrequency}
                data-testid="add-custom-freq-btn"
              >
                <Plus size={18} />
                <span>Add</span>
              </button>
            </div>
          )}

          {customFrequencies.length > 0 && (
            <div className="custom-freq-list" data-testid="custom-freq-list">
              {customFrequencies.map((freq, index) => (
                <div key={index} className="custom-freq-item">
                  <Radio size={16} />
                  <span>{freq.freq} MHz</span>
                  <span className="badge badge-info">{freq.mode.toUpperCase()}</span>
                  <span>{freq.label}</span>
                  {!isScanning && (
                    <button
                      className="btn-remove"
                      onClick={() => removeCustomFrequency(index)}
                      data-testid={`remove-custom-freq-${index}`}
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Active Detections */}
      {isScanning && detections.length > 0 && (
        <div className="card detections-card">
          <h3>Active Detections</h3>
          <div className="detections-table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Frequency</th>
                  <th>Mode</th>
                  <th>Signal</th>
                  <th>CTCSS/DCS</th>
                  <th>Label</th>
                  <th>Last Seen</th>
                </tr>
              </thead>
              <tbody data-testid="detections-table-body">
                {detections.map((detection, index) => (
                  <tr key={index}>
                    <td className="freq-cell">{detection.freq_mhz.toFixed(4)} MHz</td>
                    <td><span className="badge badge-info">{detection.mode.toUpperCase()}</span></td>
                    <td>{detection.signal_strength_db.toFixed(1)} dB</td>
                    <td>
                      {detection.ctcss_tone && `${detection.ctcss_tone.toFixed(1)} Hz`}
                      {detection.dcs_code && `DCS ${detection.dcs_code}`}
                      {!detection.ctcss_tone && !detection.dcs_code && '—'}
                    </td>
                    <td>{detection.label || '—'}</td>
                    <td>{new Date(detection.last_seen).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isScanning && detections.length === 0 && (
        <div className="card scanning-status" data-testid="scanning-status">
          <div className="scanning-spinner"></div>
          <p>Scanning... No active signals detected yet.</p>
        </div>
      )}
    </div>
  )
}

export default ScannerControl
