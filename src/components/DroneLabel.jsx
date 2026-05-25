import { Html } from "@react-three/drei";

export default function DroneLabel({ drone }) {
  const rawAction = drone.action || drone.last_decision;
  const action = typeof rawAction === "string" ? rawAction : rawAction?.action || "CONTINUE";
  const reason = typeof rawAction === "object" ? rawAction.reason : "";

  return (
    <Html
      position={[0, 8, 0]}
      center
      occlude={false}
      style={{ pointerEvents: "none" }}
    >
      <div
        style={{
          background: "rgba(0, 10, 20, 0.85)",
          padding: "6px 10px",
          borderRadius: "8px",
          border: "1px solid #00ffff",
          color: "#ffffff",
          fontSize: "11px",
          minWidth: "120px",
          textAlign: "center",
          whiteSpace: "nowrap",
          boxShadow: "0 0 8px rgba(0,255,255,0.4)"
        }}
      >
        {/* DRONE NAME */}
        <div style={{ color: "#00ffff", fontWeight: "bold", fontSize: "12px" }}>
          {drone.callsign}
        </div>
        {/* ACTION */}
        <div>{action}</div>
        {/* ONLY SHOW REASON IF FAILURE */}
        {reason && reason !== "All systems nominal" && (
          <div style={{ color: "#ff4d4d", fontSize: "10px" }}>{reason}</div>
        )}
        {/* ASSIST */}
        {drone.nearby && (
          <div style={{ color: "#00ffcc", fontSize: "10px" }}>
            Assist: {drone.nearby}
          </div>
        )}
      </div>
    </Html>
  );
}
