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

def get_val(obj, key, default):
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return getattr(obj, key, default)
    except AttributeError:
        return default


def evaluate_drone(drone):
    battery = get_val(drone, "battery", 100.0)
    
    # Get signal (supporting both signal_strength and signal)
    signal = get_val(drone, "signal_strength", None)
    if signal is None:
        signal = get_val(drone, "signal", 100.0)
        
    # Get thermal (supporting both thermal_status and thermal)
    thermal = get_val(drone, "thermal_status", None)
    if thermal is None:
        thermal = get_val(drone, "thermal", True)
        
    # Get obstacle (supporting both obstacle_distance and obstacle)
    obstacle = get_val(drone, "obstacle_distance", 10.0)

    # 1. Battery critically low
    if battery < 30:
        return {
            "action": "RETURN_TO_BASE",
            "reason": "Battery critically low"
        }

    # 2. Weak signal
    if signal < 25:
        return {
            "action": "REROUTE",
            "reason": "Weak signal"
        }

    # 3. Thermal sensor failure
    if thermal is False:
        return {
            "action": "REQUEST_NEAREST_SENSOR",
            "reason": "Thermal sensor failure"
        }

    # 4. Obstacle too close
    if obstacle < 1:
        return {
            "action": "AVOID_OBSTACLE",
            "reason": "Obstacle too close"
        }

    # fallback to model evaluation
    input_data = pd.DataFrame([{
        "battery": battery,
        "propeller_health": get_val(drone, "propeller_health", 100.0),
        "cpu_temperature": get_val(drone, "cpu_temperature", 40.0),
        "signal_strength": signal,
        "thermal_status": int(thermal),
        "lidar_status": int(get_val(drone, "lidar_status", True)),
        "obstacle_distance": obstacle,
        "moisture_level": get_val(drone, "moisture_level", 0.0),
        "smoke_density": get_val(drone, "smoke_density", 0.0),
        "altitude": get_val(drone, "altitude", 20.0),
        "speed": np.linalg.norm(get_val(drone, "vel", np.zeros(3))) if not isinstance(get_val(drone, "vel", None), (int, float)) else get_val(drone, "vel", 0.0),
    }])

    try:
        action = model.predict(input_data)[0]
    except Exception:
        action = "CONTINUE_MISSION"

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
