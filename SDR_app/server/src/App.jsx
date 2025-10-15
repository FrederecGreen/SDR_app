import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Radio, Settings, List, Activity } from 'lucide-react'
import Dashboard from './components/Dashboard'
import ScannerControl from './components/ScannerControl'
import RecordingsList from './components/RecordingsList'
import AdvancedSettings from './components/AdvancedSettings'
import './App.css'

function App() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/status')
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data)
      }
    } catch (error) {
      console.error('Error fetching status:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading SDR_app...</p>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <div className="app" data-testid="sdr-app">
        <nav className="nav-bar glass">
          <div className="nav-brand">
            <Radio size={28} />
            <h1>SDR_app</h1>
          </div>
          <div className="nav-links">
            <NavLink to="/" end data-testid="nav-dashboard">
              <Activity size={18} />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/scanner" data-testid="nav-scanner">
              <Radio size={18} />
              <span>Scanner</span>
            </NavLink>
            <NavLink to="/recordings" data-testid="nav-recordings">
              <List size={18} />
              <span>Recordings</span>
            </NavLink>
            <NavLink to="/settings" data-testid="nav-settings">
              <Settings size={18} />
              <span>Settings</span>
            </NavLink>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard systemStatus={systemStatus} />} />
            <Route path="/scanner" element={<ScannerControl systemStatus={systemStatus} onStatusChange={fetchStatus} />} />
            <Route path="/recordings" element={<RecordingsList />} />
            <Route path="/settings" element={<AdvancedSettings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
