import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Brain } from 'lucide-react'
import AIDecisionPanel from '../components/mission/AIDecisionPanel'

export default function AIDashboard() {
  const navigate = useNavigate()

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0a0a0f',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          borderBottom: '2px solid #00e5ff',
          background: '#0d1117',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            type="button"
            onClick={() => navigate('/mission')}
            style={navBtn}
            title="Back to Mission"
          >
            <ArrowLeft size={18} />
          </button>
          <Brain size={22} color="#00e5ff" />
          <div>
            <h1
              style={{
                margin: 0,
                fontFamily: 'Rajdhani, sans-serif',
                fontSize: '20px',
                fontWeight: 700,
                letterSpacing: '3px',
                color: '#e2e8f0',
              }}
            >
              AI DECISION DASHBOARD
            </h1>
            <p
              style={{
                margin: '4px 0 0',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '10px',
                color: '#64748b',
                letterSpacing: '1px',
              }}
            >
              COMMAND CENTER // LIVE INTERVENTION MONITOR
            </p>
          </div>
        </div>
      </header>

      <AIDecisionPanel />
    </div>
  )
}

const navBtn = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '8px',
  background: 'rgba(0, 229, 255, 0.08)',
  border: '1px solid rgba(0, 229, 255, 0.3)',
  borderRadius: '6px',
  color: '#00e5ff',
  cursor: 'pointer',
}
