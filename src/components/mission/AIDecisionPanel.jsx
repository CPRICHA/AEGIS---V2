import { useSimStore } from '../../store/useSimStore'

const CALLSIGNS = {
  1: 'FALCON',
  2: 'HAWK',
  3: 'OSPREY',
  4: 'KESTREL',
  5: 'MERLIN',
}

const styles = {
  panel: {
    flex: 1,
    padding: '24px',
    overflow: 'auto',
  },
  title: {
    fontFamily: 'Rajdhani, sans-serif',
    fontSize: '18px',
    fontWeight: 700,
    letterSpacing: '3px',
    color: '#00e5ff',
    margin: '0 0 8px',
  },
  subtitle: {
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '11px',
    color: '#64748b',
    marginBottom: '24px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '16px',
  },
  card: (critical) => ({
    background: critical ? 'rgba(239, 68, 68, 0.08)' : '#0d1117',
    border: critical
      ? '1px solid rgba(239, 68, 68, 0.55)'
      : '1px solid rgba(0, 229, 255, 0.35)',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: critical
      ? '0 0 18px rgba(239, 68, 68, 0.12)'
      : '0 0 18px rgba(0, 229, 255, 0.08)',
  }),
  cardHeader: {
    fontFamily: 'Rajdhani, sans-serif',
    fontSize: '14px',
    fontWeight: 700,
    letterSpacing: '2px',
    color: '#e2e8f0',
    marginBottom: '12px',
    paddingBottom: '8px',
    borderBottom: '1px solid #1e293b',
  },
  line: {
    margin: '6px 0',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '12px',
    color: '#94a3b8',
  },
  action: {
    color: '#00e5ff',
    fontWeight: 600,
  },
  assist: {
    marginTop: '8px',
    color: '#00e5ff',
    fontSize: '11px',
    fontFamily: 'JetBrains Mono, monospace',
  },
  empty: {
    padding: '48px 24px',
    textAlign: 'center',
    color: '#64748b',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '12px',
    border: '1px dashed #334155',
    borderRadius: '8px',
  },
}

export default function AIDecisionPanel() {
  const liveAiDrones = useSimStore((s) => s.liveAiDrones)
  const backendConnected = useSimStore((s) => s.backendConnected)

  const drones = liveAiDrones || []
  const activeDecisions = drones.filter(
    (d) => d.action && d.action.action !== 'CONTINUE_MISSION',
  )

  return (
    <div className="ai-decision-panel" style={styles.panel}>
      <h3 style={styles.title}>AI DECISIONS</h3>
      <p style={styles.subtitle}>
        {backendConnected
          ? 'Live stream — all drones evaluated every second'
          : 'Waiting for backend connection…'}
      </p>

      {activeDecisions.length > 0 ? (
        <div style={styles.grid}>
          {activeDecisions.map((d) => {
            const critical = (d.battery ?? 100) < 20
            const label = CALLSIGNS[d.id] || `DRONE-${d.id}`

            return (
              <div key={d.id} className="ai-card" style={styles.card(critical)}>
                <div style={styles.cardHeader}>
                  {label} // ID {d.id}
                  {critical && (
                    <span style={{ color: '#f87171', marginLeft: '8px', fontSize: '10px' }}>
                      CRITICAL
                    </span>
                  )}
                </div>
                <div style={styles.line}>
                  Drone: {d.id}
                </div>
                <div style={styles.line}>
                  Action: <span style={styles.action}>{d.action?.action}</span>
                </div>
                <div style={styles.line}>Reason: {d.action?.reason}</div>
                <div style={styles.line}>Status: {d.status}</div>
                {d.battery != null && (
                  <div style={styles.line}>
                    Battery: {Number(d.battery).toFixed(1)}%
                  </div>
                )}
                {d.nearby_drone_id && (
                  <div style={styles.assist}>
                    Assisting Drone: {CALLSIGNS[d.nearby_drone_id] || d.nearby_drone_id}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      ) : (
        <div style={styles.empty}>
          No active AI interventions. Inject failures in the simulation panel to trigger decisions.
        </div>
      )}
    </div>
  )
}
