import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSimStore } from '../../store/useSimStore'
import { X } from 'lucide-react'

const INITIAL_DRONES = [
  { id: 1, name: 'FALCON', battery: 100, thermal: true, obstacle: 10, signal: 100, cpu: 40 },
  { id: 2, name: 'HAWK', battery: 100, thermal: true, obstacle: 10, signal: 100, cpu: 40 },
  { id: 3, name: 'OSPREY', battery: 100, thermal: true, obstacle: 10, signal: 100, cpu: 40 },
  { id: 4, name: 'KESTREL', battery: 100, thermal: true, obstacle: 10, signal: 100, cpu: 40 },
  { id: 5, name: 'MERLIN', battery: 100, thermal: true, obstacle: 10, signal: 100, cpu: 40 },
]

const styles = {
  panel: {
    background: '#0d1117',
    padding: '16px 20px',
    maxHeight: '70vh',
    overflow: 'auto',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '14px',
    flexWrap: 'wrap',
    gap: '12px',
  },
  title: {
    fontFamily: 'Rajdhani, sans-serif',
    fontSize: '14px',
    fontWeight: 700,
    letterSpacing: '2px',
    color: '#00e5ff',
    margin: 0,
  },
  subtitle: {
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '10px',
    color: '#64748b',
    margin: '4px 0 0',
  },
  tableWrap: {
    overflowX: 'auto',
    borderRadius: '8px',
    border: '1px solid #1e293b',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '11px',
  },
  th: {
    textAlign: 'left',
    padding: '10px 12px',
    color: '#64748b',
    fontWeight: 600,
    letterSpacing: '1px',
    borderBottom: '1px solid #1e293b',
    background: '#0a0a0f',
    whiteSpace: 'nowrap',
  },
  td: {
    padding: '8px 12px',
    borderBottom: '1px solid rgba(30, 41, 59, 0.6)',
    color: '#94a3b8',
    verticalAlign: 'middle',
  },
  row: (selected) => ({
    cursor: 'pointer',
    background: selected ? 'rgba(0, 229, 255, 0.08)' : 'transparent',
    boxShadow: selected ? 'inset 3px 0 0 #00e5ff' : 'none',
    transition: 'background 0.2s ease',
  }),
  name: {
    color: '#e2e8f0',
    fontWeight: 600,
    letterSpacing: '1px',
  },
  input: {
    width: '64px',
    padding: '6px 8px',
    background: '#0a0a0f',
    border: '1px solid #334155',
    borderRadius: '4px',
    color: '#e2e8f0',
    fontSize: '11px',
    fontFamily: 'JetBrains Mono, monospace',
  },
  toggle: (on) => ({
    padding: '4px 10px',
    borderRadius: '4px',
    border: `1px solid ${on ? 'rgba(0, 229, 255, 0.5)' : 'rgba(239, 68, 68, 0.5)'}`,
    background: on ? 'rgba(0, 229, 255, 0.12)' : 'rgba(239, 68, 68, 0.12)',
    color: on ? '#00e5ff' : '#f87171',
    cursor: 'pointer',
    fontSize: '10px',
    fontWeight: 600,
    letterSpacing: '1px',
  }),
  linkBtn: {
    padding: '8px 16px',
    borderRadius: '6px',
    border: '1px solid rgba(0, 229, 255, 0.4)',
    background: 'transparent',
    color: '#00e5ff',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '10px',
    fontWeight: 600,
    letterSpacing: '1px',
    cursor: 'pointer',
  },
  closeBtn: {
    background: 'none',
    border: '1px solid #334155',
    borderRadius: '4px',
    color: '#94a3b8',
    cursor: 'pointer',
    padding: '4px',
    display: 'flex',
    alignItems: 'center',
  },
  liveBadge: {
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '9px',
    color: '#00ff88',
    letterSpacing: '1px',
  },
  error: {
    marginTop: '12px',
    padding: '10px 12px',
    borderRadius: '6px',
    border: '1px solid rgba(239, 68, 68, 0.4)',
    background: 'rgba(239, 68, 68, 0.08)',
    color: '#f87171',
    fontSize: '11px',
    fontFamily: 'JetBrains Mono, monospace',
  },
}

const applyOverride = async (drone) => {
  await fetch('http://localhost:8000/override', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: drone.id,
      battery: drone.battery,
      thermal_status: drone.thermal,
      obstacle_distance: drone.obstacle,
      signal_strength: drone.signal,
      cpu_temperature: drone.cpu,
    }),
  })
}

export default function SimulationPanel({ onClose }) {
  const navigate = useNavigate()
  const liveAiDrones = useSimStore((s) => s.liveAiDrones)
  const backendConnected = useSimStore((s) => s.backendConnected)

  const [drones, setDrones] = useState(INITIAL_DRONES)
  const [selectedDrone, setSelectedDrone] = useState(1)
  const [error, setError] = useState(null)

  const updateDrone = (id, field, value) => {
    setDrones((prev) =>
      prev.map((d) => (d.id === id ? { ...d, [field]: value } : d)),
    )
  }

  const parseNum = (value, fallback = 0) => {
    const n = Number(value)
    return Number.isFinite(n) ? n : fallback
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      Promise.all(drones.map((d) => applyOverride(d))).catch((e) => {
        setError(e.message || 'Override sync failed')
      })
    }, 300)
    return () => clearTimeout(timer)
  }, [drones])

  const activeCount = (liveAiDrones || []).filter(
    (d) => d.action && d.action.action !== 'CONTINUE_MISSION',
  ).length

  const selected = drones.find((d) => d.id === selectedDrone)

  return (
    <section style={styles.panel} aria-label="Drone failure simulation">
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>DRONE FAILURE SIMULATION</h2>
          <p style={styles.subtitle}>
            Live overrides — {selected?.name ?? '—'} · changes apply in real time
          </p>
          {backendConnected && (
            <p style={styles.liveBadge}>● LIVE AI ENGINE ACTIVE</p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            type="button"
            style={styles.linkBtn}
            onClick={() => navigate('/ai-dashboard')}
          >
            VIEW AI DECISIONS{activeCount > 0 ? ` (${activeCount})` : ''}
          </button>
          {onClose && (
            <button type="button" style={styles.closeBtn} onClick={onClose} title="Close">
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      <div style={styles.tableWrap}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>DRONE</th>
              <th style={styles.th}>BATTERY %</th>
              <th style={styles.th}>THERMAL</th>
              <th style={styles.th}>OBSTACLE (m)</th>
              <th style={styles.th}>SIGNAL</th>
              <th style={styles.th}>CPU °C</th>
            </tr>
          </thead>
          <tbody>
            {drones.map((d) => {
              const isSelected = d.id === selectedDrone
              return (
                <tr
                  key={d.id}
                  style={styles.row(isSelected)}
                  onClick={() => setSelectedDrone(d.id)}
                >
                  <td style={{ ...styles.td, ...styles.name }}>{d.name}</td>
                  <td style={styles.td} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={0.1}
                      value={d.battery}
                      style={styles.input}
                      onChange={(e) =>
                        updateDrone(d.id, 'battery', parseNum(e.target.value, d.battery))
                      }
                    />
                  </td>
                  <td style={styles.td} onClick={(e) => e.stopPropagation()}>
                    <button
                      type="button"
                      style={styles.toggle(d.thermal)}
                      onClick={() => updateDrone(d.id, 'thermal', !d.thermal)}
                    >
                      {d.thermal ? 'OK' : 'FAIL'}
                    </button>
                  </td>
                  <td style={styles.td} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      min={0}
                      max={50}
                      step={0.1}
                      value={d.obstacle}
                      style={styles.input}
                      onChange={(e) =>
                        updateDrone(d.id, 'obstacle', parseNum(e.target.value, d.obstacle))
                      }
                    />
                  </td>
                  <td style={styles.td} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={1}
                      value={d.signal}
                      style={styles.input}
                      onChange={(e) =>
                        updateDrone(d.id, 'signal', parseNum(e.target.value, d.signal))
                      }
                    />
                  </td>
                  <td style={styles.td} onClick={(e) => e.stopPropagation()}>
                    <input
                      type="number"
                      min={0}
                      max={120}
                      step={0.1}
                      value={d.cpu}
                      style={styles.input}
                      onChange={(e) =>
                        updateDrone(d.id, 'cpu', parseNum(e.target.value, d.cpu))
                      }
                    />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {error && <div style={styles.error}>{error}</div>}
    </section>
  )
}
