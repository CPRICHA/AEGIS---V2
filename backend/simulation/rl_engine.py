"""Lightweight reward simulation for AI decisions (not full RL)."""

# Positive rewards for proactive / recovery actions
REWARD_MAP = {
    "RETURN_TO_BASE": 10,
    "REROUTE": 8,
    "AUTONOMOUS_MODE": 5,
    "REQUEST_NEAREST_SENSOR": 12,
    "LOW_POWER_MODE": 6,
    "REDUCE_SPEED": 4,
    "INCREASE_ALTITUDE": 4,
    "CONTINUE_MISSION": 1,
}

# Penalties for risky states the model should avoid
PENALTY_MAP = {
    "CONTINUE_MISSION": 0,
}


def calculate_reward(action: str) -> float:
    if action in PENALTY_MAP and PENALTY_MAP[action] < 0:
        return PENALTY_MAP[action]
    return float(REWARD_MAP.get(action, 0))
