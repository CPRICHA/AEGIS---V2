import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# -------------------------
# LOAD TRAINED MODEL
# -------------------------

_MODEL_CANDIDATES = [
    Path(__file__).resolve().parent / "drone_decision_model.pkl",
    Path(__file__).resolve().parent.parent / "drone_decision_model.pkl",
]


def _load_model():
    for path in _MODEL_CANDIDATES:
        if path.is_file():
            return joblib.load(path)
    raise FileNotFoundError(
        "drone_decision_model.pkl not found. Run: python simulation/train_model.py"
    )


model = _load_model()


# -------------------------
# AI DECISION FUNCTION
# -------------------------

def evaluate_drone(drone):
    input_data = pd.DataFrame([{
        "battery": drone.battery,
        "propeller_health": drone.propeller_health,
        "cpu_temperature": drone.cpu_temperature,
        "signal_strength": drone.signal_strength,
        "thermal_status": int(drone.thermal_status),
        "lidar_status": int(drone.lidar_status),
        "obstacle_distance": drone.obstacle_distance,
        "moisture_level": drone.moisture_level,
        "smoke_density": drone.smoke_density,
        "altitude": drone.altitude,
        "speed": np.linalg.norm(drone.vel),
    }])

    action = model.predict(input_data)[0]

    reason = "AI autonomous decision"

    if action == "RETURN_TO_BASE":
        reason = "Battery critically low"
    elif action == "REROUTE":
        reason = "Obstacle detected"
    elif action == "AUTONOMOUS_MODE":
        reason = "Weak signal"
    elif action == "REQUEST_NEAREST_SENSOR":
        reason = "Thermal sensor failure"
    elif action == "LOW_POWER_MODE":
        reason = "CPU overheating"
    elif action == "REDUCE_SPEED":
        reason = "Propeller degraded"
    elif action == "INCREASE_ALTITUDE":
        reason = "High moisture — climbing"
    elif action == "CONTINUE_MISSION":
        reason = "All systems nominal"

    return {
        "action": action,
        "reason": reason,
    }
