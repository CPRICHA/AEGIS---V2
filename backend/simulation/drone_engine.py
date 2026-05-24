import numpy as np
import random
from simulation.world_state import world, LogEntry
from simulation.decision_engine import evaluate_drone
from simulation.ai_actions import apply_ai_decision
from simulation.ai_logging import (
    make_ai_log_entry,
    make_failover_log_entry,
    log_telemetry,
)


MAX_SPEED_H = 15.0  # m/s
MAX_SPEED_V = 5.0   # m/s

_TELEMETRY_INTERVAL = 25


def tick_all(dt: float):
    if not world.running:
        return

    for drone in world.drones:
        if drone.current_target is not None:
            diff = drone.current_target - drone.pos
            dist = np.linalg.norm(diff)

            if dist < 1.0:
                drone.current_target = None
                if drone.status == "RETURNING":
                    drone.status = "CHARGING"
            else:
                direction = diff / dist
                dt_factor = min(1.0, 0.1 * world.speed)
                desired_vel = direction * np.array([MAX_SPEED_H, MAX_SPEED_V, MAX_SPEED_H])
                drone.vel = drone.vel * (1 - dt_factor) + desired_vel * dt_factor

                drone.update_telemetry()

                if world.tick % _TELEMETRY_INTERVAL == 0:
                    log_telemetry(
                        drone.id,
                        drone.battery,
                        drone.signal_strength,
                        drone.thermal_status,
                    )

                decision = evaluate_drone(drone)
                prev_action = drone.last_decision
                result = apply_ai_decision(
                    drone,
                    decision,
                    world.drones,
                    verbose=False,
                )

                if result["action"] != prev_action or result["helper_id"]:
                    world.event_log.append(
                        make_ai_log_entry(
                            world.sim_time,
                            drone.id,
                            result["action"],
                            result["reason"],
                        )
                    )
                    if result["helper_id"]:
                        world.event_log.append(
                            make_failover_log_entry(
                                world.sim_time,
                                drone.id,
                                result["helper_id"],
                            )
                        )

                drone.pos += drone.vel * dt
                drone.pos += np.random.normal(0, 0.02, 3)
                drone.heading = np.degrees(np.arctan2(drone.vel[0], drone.vel[2]))
        else:
            drone.vel *= 0.9

        if drone.status == "SCANNING":
            drone.battery -= 0.008 * world.speed
        elif drone.status == "SEARCHING":
            drone.battery -= 0.010 * world.speed
        elif drone.status == "RETURNING":
            drone.battery -= 0.006 * world.speed
        elif drone.status == "CHARGING":
            drone.battery = min(100.0, drone.battery + 0.020 * world.speed)

        if world.scenario == "flood":
            drone.battery -= 0.004 * world.speed

        if drone.battery < 15.0 and drone.status in ["SCANNING", "SEARCHING"]:
            drone.status = "RETURNING"
            stations = [[45, 0, 45], [-45, 0, 45], [45, 0, -45], [-45, 0, -45], [0, 0, 0]]
            nearest = min(stations, key=lambda s: np.linalg.norm(np.array(s) - drone.pos))
            drone.current_target = np.array([nearest[0], 25, nearest[2]])
            world.event_log.append(
                LogEntry(
                    world.sim_time,
                    drone.id,
                    "warning",
                    f"[WARNING] Battery low: {drone.battery:.1f}%. Automated return-to-base.",
                )
            )

        if drone.status == "CHARGING" and drone.battery > 95.0:
            drone.status = "SCANNING"
            world.event_log.append(
                LogEntry(
                    world.sim_time,
                    drone.id,
                    "system",
                    f"[SYSTEM] {drone.callsign} maintenance complete. Re-deploying.",
                )
            )

        if world.tick % 5 == 0:
            drone.trail.append(drone.pos.copy())
            if len(drone.trail) > 200:
                drone.trail.pop(0)

        if world.tick % 5 == 0:
            from simulation.thermal_engine import generate_thermal_frame, generate_camera_frame
            drone.thermal_frame = generate_thermal_frame(drone, world)
            drone.camera_frame = generate_camera_frame(drone, world)


def assign_drone_target(drone_id: int, target: np.ndarray):
    for d in world.drones:
        if d.id == drone_id:
            d.current_target = target
            d.status = "SEARCHING"
            break
