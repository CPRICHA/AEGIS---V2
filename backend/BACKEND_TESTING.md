# AEGIS Backend Intelligence — Testing Guide

## Quick start

From `backend/`:

```bash
pip install -r requirements.txt
python simulation/ai_test_simulation.py
```

Expected demo output includes `[AI BRAIN]`, `[FAILOVER]`, `[RL]`, and `[SYSTEM]` lines for all five test drones.

## AI test simulation (offline demo)

| Drone | Injected fault | Expected ML action |
|-------|----------------|-------------------|
| 1 FALCON | `battery = 10` | `RETURN_TO_BASE` |
| 2 HAWK | `thermal_status = False` | `REQUEST_NEAREST_SENSOR` + failover |
| 3 OSPREY | `obstacle_distance = 0.5` | `REROUTE` |
| 4 KESTREL | `signal_strength = 10` | `AUTONOMOUS_MODE` |
| 5 MERLIN | `cpu_temperature = 95` | `LOW_POWER_MODE` |

## Live simulation (FastAPI + WebSocket)

```bash
cd backend
python main.py
```

Start a scenario from the frontend or:

```bash
curl -X POST http://localhost:8000/api/simulation/start -H "Content-Type: application/json" -d "{\"scenario\":\"earthquake\"}"
```

Assign a target so drones move (AI runs while `current_target` is set):

```bash
curl -X POST http://localhost:8000/api/drone/command -H "Content-Type: application/json" -d "{\"drone_id\":1,\"action\":\"divert_survivor\"}"
```

Watch the mission log / notifications for `[AI BRAIN]` and `[FAILOVER]` entries.

## Manually trigger conditions (Python shell)

```python
from simulation.world_state import world
from simulation.scenario_loader import load_scenario
from simulation.decision_engine import evaluate_drone
from simulation.ai_actions import apply_ai_decision

load_scenario("earthquake")
world.running = True
drone = world.drones[0]

# Low battery → return to base
drone.battery = 10
print(evaluate_drone(drone))
apply_ai_decision(drone, evaluate_drone(drone), world.drones)

# Thermal failure → nearest sensor + swarm assist
drone = world.drones[1]
drone.thermal_status = False
apply_ai_decision(drone, evaluate_drone(drone), world.drones)

# Obstacle → reroute
drone = world.drones[2]
drone.obstacle_distance = 0.5
apply_ai_decision(drone, evaluate_drone(drone), world.drones)

# Weak signal → autonomous mode
drone = world.drones[3]
drone.signal_strength = 10
apply_ai_decision(drone, evaluate_drone(drone), world.drones)

# Overheat → low power
drone = world.drones[4]
drone.cpu_temperature = 95
apply_ai_decision(drone, evaluate_drone(drone), world.drones)
```

## Verify failover

1. Set `drone.thermal_status = False` on a drone with neighbors in `world.drones`.
2. Run `evaluate_drone` then `apply_ai_decision`.
3. Confirm `drone.nearby_drone_id` is set and console shows `[FAILOVER] Drone X assisting Drone Y`.

## Verify rewards

After any `apply_ai_decision` call:

```python
print(drone.reward_score)  # increases per action map in rl_engine.py
```

Console shows `[RL] Drone N Reward +10 (total: …)` during `ai_test_simulation.py`.

## Retrain model (optional)

```bash
cd backend/simulation
python generate_dataset.py
python train_model.py
```

Model is saved to `simulation/drone_decision_model.pkl` and `backend/drone_decision_model.pkl`.

## Frontend checks

With backend running and drones active:

- **Bottom mission log** — purple `[AI BRAIN]` lines, amber `[FAILOVER]` lines
- **Notification panel** — AI decisions as guide/warning toasts
- WebSocket payload includes `autonomous_mode`, `last_decision`, `nearby_drone_id`, `reward_score` per drone (for future UI use)
