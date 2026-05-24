import joblib
import pandas as pd
import numpy as np

# -------------------------
# LOAD TRAINED MODEL
# -------------------------

model = joblib.load("drone_decision_model.pkl")


# -------------------------
# AI DECISION FUNCTION
# -------------------------

def evaluate_drone(drone):

    # -------------------------
    # CREATE INPUT DATAFRAME
    # -------------------------

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
        "speed": np.linalg.norm(drone.vel)
    }])

    # -------------------------
    # MODEL PREDICTION
    # -------------------------

    action = model.predict(input_data)[0]

    # -------------------------
    # REASON GENERATION
    # -------------------------

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

    return {
        "action": action,
        "reason": reason
    }