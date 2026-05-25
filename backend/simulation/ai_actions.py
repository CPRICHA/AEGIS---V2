"""Apply ML-predicted actions to a drone (shared by live sim and test harness)."""

import numpy as np

from simulation.swarm_failover import request_nearest_sensor
from simulation.rl_engine import calculate_reward
from simulation.ai_logging import log_ai_brain, log_failover, log_rl


_CHARGING_STATIONS = [
    [45, 0, 45],
    [-45, 0, 45],
    [45, 0, -45],
    [-45, 0, -45],
    [0, 0, 0],
]


def apply_ai_decision(drone, decision, all_drones, *, verbose: bool = True):
    """
    Execute model output on drone state.
    Returns dict: action, reason, reward, helper_id
    """
    action = decision["action"]
    reason = decision["reason"]
    drone.last_decision = action
    helper_id = None

    if verbose:
        log_ai_brain(drone.id, action, reason)

    if action == "RETURN_TO_BASE":
        drone.status = "RETURNING"
        nearest = min(
            _CHARGING_STATIONS,
            key=lambda s: np.linalg.norm(np.array(s) - drone.pos),
        )
        drone.current_target = np.array([nearest[0], 25, nearest[2]])

    elif action == "AUTONOMOUS_MODE":
        drone.autonomous_mode = True

    elif action == "REDUCE_SPEED":
        drone.vel *= 0.5

    elif action == "REROUTE":
        drone.direction += 45

    elif action == "INCREASE_ALTITUDE":
        drone.altitude += 5

    elif action == "LOW_POWER_MODE":
        drone.vel *= 0.7

    elif action == "REQUEST_NEAREST_SENSOR":
        drone.requesting_support = True
        helper_id = request_nearest_sensor(drone, all_drones)
        if helper_id and verbose:
            log_failover(helper_id, drone.id)

    reward = calculate_reward(drone, decision)
    drone.reward_score += reward

    if verbose:
        log_rl(drone.id, reward, drone.reward_score)

    return {
        "action": action,
        "reason": reason,
        "reward": reward,
        "helper_id": helper_id,
    }
