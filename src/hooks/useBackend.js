import { useEffect, useRef, useState, useCallback } from 'react'
import { useSimStore } from '../store/useSimStore'

export const useBackend = () => {
  const socketRef = useRef(null)
  const [connected, setConnected] = useState(false)
  const [latency, setLatency] = useState(0)

  const applyState = useSimStore((s) => s.applyBackendState)
  const setTelemetry = useSimStore((s) => s.setTelemetry)
  const setLiveAiDrones = useSimStore((s) => s.setLiveAiDrones)

  const sendCommand = useCallback((action, payload = {}) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'command', action, ...payload }))
    }
  }, [])

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/ws')

      ws.onopen = () => {
        setConnected(true)
        useSimStore.setState({ backendConnected: true })
        console.log('%c[AEGIS SYSTEM] BACKEND CONNECTED', 'color: #00e5ff; font-weight: bold')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WS DATA:', data)

          if (data.drones) {
            setLiveAiDrones(data.drones)
            setTelemetry(data)

            const selectedId = useSimStore.getState().selectedDrone
            const drone =
              data.drones.find((d) => d.id === selectedId) ?? data.drones[0]
            if (drone) {
              setTelemetry({
                ...data,
                battery: drone.battery,
                signal_strength: drone.signal ?? drone.signal_strength ?? 100,
                thermal_status: drone.thermal_status ?? true,
                propeller_health: drone.propeller ?? drone.propeller_health ?? 100,
                cpu_temp: drone.cpu ?? drone.cpu_temp,
                action: drone.action,
              })
            }
          } else {
            setTelemetry(data)
          }

          if (data.type === 'state') {
            applyState(data)
          }
        } catch (err) {
          console.error('Message error:', err)
        }
      }

      ws.onclose = () => {
        setConnected(false)
        useSimStore.setState({ backendConnected: false })
        console.warn('[AEGIS SYSTEM] BACKEND DISCONNECTED. RECONNECTING...')
        setTimeout(connect, 3000)
      }

      socketRef.current = ws
    }

    connect()
    return () => socketRef.current?.close()
  }, [applyState, setTelemetry, setLiveAiDrones])

  return { connected, sendCommand, latency }
}
