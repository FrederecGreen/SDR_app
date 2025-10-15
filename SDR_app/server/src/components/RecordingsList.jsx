import React, { useState, useEffect } from 'react'
import { Download, Trash2, Play, Radio } from 'lucide-react'
import './RecordingsList.css'

function RecordingsList() {
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRecordings()
  }, [])

  const fetchRecordings = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/recordings')
      if (response.ok) {
        const data = await response.json()
        setRecordings(data)
      }
    } catch (error) {
      console.error('Error fetching recordings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = (recording) => {
    window.open(`/api/recordings/${recording.id}`, '_blank')
  }

  const handleDelete = async (recording) => {
    if (!confirm(`Delete recording ${recording.id}?`)) return

    try {
      const response = await fetch(`/api/recordings/${recording.id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setRecordings(recordings.filter(r => r.id !== recording.id))
      } else {
        alert('Failed to delete recording')
      }
    } catch (error) {
      console.error('Error deleting recording:', error)
      alert('Error deleting recording')
    }
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  if (loading) {
    return (
      <div className="recordings-loading">
        <div className="loading-spinner"></div>
        <p>Loading recordings...</p>
      </div>
    )
  }

  return (
    <div className="recordings-list" data-testid="recordings-list">
      <div className="recordings-header">
        <h2>Recordings</h2>
        <div className="recordings-stats">
          <span>{recordings.length} total</span>
        </div>
      </div>

      {recordings.length === 0 ? (
        <div className="card empty-state">
          <Radio size={48} />
          <h3>No Recordings Yet</h3>
          <p>Start scanning to create recordings</p>
        </div>
      ) : (
        <div className="recordings-grid">
          {recordings.map((recording) => (
            <div key={recording.id} className="card recording-card" data-testid="recording-card">
              <div className="recording-header">
                <div className="recording-freq">
                  <Radio size={20} />
                  <span>{recording.freq_mhz.toFixed(4)} MHz</span>
                </div>
                <span className="badge badge-info">{recording.mode.toUpperCase()}</span>
              </div>

              <div className="recording-info">
                {recording.label && (
                  <div className="recording-label">{recording.label}</div>
                )}
                
                <div className="recording-meta">
                  <div>
                    <span className="meta-label">Duration:</span>
                    <span className="meta-value">{formatDuration(recording.duration_seconds)}</span>
                  </div>
                  <div>
                    <span className="meta-label">Size:</span>
                    <span className="meta-value">{formatFileSize(recording.file_size_bytes)}</span>
                  </div>
                  <div>
                    <span className="meta-label">Recorded:</span>
                    <span className="meta-value">
                      {new Date(recording.start_time).toLocaleString()}
                    </span>
                  </div>
                </div>

                {(recording.ctcss_tone || recording.dcs_code) && (
                  <div className="recording-codes">
                    {recording.ctcss_tone && (
                      <span className="badge badge-warning">CTCSS: {recording.ctcss_tone.toFixed(1)} Hz</span>
                    )}
                    {recording.dcs_code && (
                      <span className="badge badge-warning">DCS: {recording.dcs_code}</span>
                    )}
                  </div>
                )}
              </div>

              <div className="recording-actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => handleDownload(recording)}
                  data-testid="download-recording-btn"
                >
                  <Download size={16} />
                  <span>Download</span>
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleDelete(recording)}
                  data-testid="delete-recording-btn"
                >
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RecordingsList
