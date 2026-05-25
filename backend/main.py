from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from simulation.world_state import world, DroneState
from simulation import drone_engine, survivor_engine, scenario_loader, trajectory
from api.routes import router
from api.api_websocket import hub
from simulation.decision_engine import evaluate_drone
from simulation.ai_actions import apply_ai_decision

CALLSIGNS = ["FALCON", "HAWK", "OSPREY", "KESTREL", "MERLIN"]


def ensure_world_drones():
    if world.drones:
        return
    for i in range(5):
        world.drones.append(
            DroneState(
                id=i + 1,
                callsign=CALLSIGNS[i],
                status="ACTIVE",
                pos=np.array([float(i * 15), 0.0, 20.0]),
            )
        )

@asynccontextmanager
async def lifespan(app):
    ensure_world_drones()
    # Start simulation loop as background task
    loop_task = asyncio.create_task(simulation_loop())
    yield
    loop_task.cancel()

app = FastAPI(lifespan=lifespan)

# Allow CORS for dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

async def simulation_loop():
    while True:
        try:
            if world.running:
                # dt = 0.05s * world.speed (20Hz base)
                dt = 0.05 * world.speed
                world.sim_time += dt
                world.tick += 1
                
                # Engines
                drone_engine.tick_all(dt)
                survivor_engine.update_survivors(world, dt)
                survivor_engine.check_detections(world)
                scenario_loader.handle_scenario_events()
                trajectory.update_all_trajectories()
                
                # Broadcast state via WS
                await hub.broadcast(world)
                
            # Delta time wait
            await asyncio.sleep(0.05 / world.speed if world.speed > 0 else 0.05)
        except Exception as e:
            print(f"Simulation Error: {e}")
            await asyncio.sleep(0.1)

def run_simulation_step():
    ensure_world_drones()
    results = []
    for drone in world.drones:
        # Skip evaluation if this drone was manually simulated
        if getattr(drone, "isSimulated", False):
            # Use existing fields directly, assuming action already set
            action_field = drone.action if hasattr(drone, "action") else drone.last_decision
            # Ensure action is a plain string for UI consistency
            if isinstance(action_field, dict):
                action_str = action_field.get("action", "CONTINUE_MISSION")
            else:
                action_str = str(action_field)
            reason_str = action_field.get("reason", "") if isinstance(action_field, dict) else ""
        else:
            decision = evaluate_drone(drone)
            apply_ai_decision(drone, decision, world.drones, verbose=False)
            # Flatten action to a plain string and extract reason separately
            raw_last = getattr(drone, "last_decision", "CONTINUE_MISSION")
            if isinstance(raw_last, dict):
                action_str = raw_last.get("action", "CONTINUE_MISSION")
            else:
                action_str = str(raw_last)
            reason_str = decision.get("reason", "") if isinstance(decision, dict) else ""
        cpu_temp = getattr(drone, "cpu_temperature", 0)
        signal = getattr(drone, "signal_strength", 0)
        propeller = getattr(drone, "propeller_health", 100)
        results.append({
            "id": drone.id,
            "callsign": getattr(drone, "callsign", f"DRONE-{drone.id}"),
            "battery": round(getattr(drone, "battery", 100.0), 1),
            "signal": round(signal, 1),
            "cpu": round(cpu_temp, 1),
            "propeller": round(propeller, 1),
            "action": action_str,
            "reason": reason_str,
            "status": getattr(drone, "status", "ACTIVE"),
            "nearby": getattr(drone, "nearby_drone_id", None)
        })
    return {"drones": results}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            try:
                data = run_simulation_step()
                await websocket.send_json(data)
                await asyncio.sleep(1)

            except Exception as e:
                print("WebSocket Error:", str(e))
                break   # STOP LOOP if error happens

    except WebSocketDisconnect:
        print("Client disconnected")

    finally:
        print("WebSocket closed safely")


@app.post("/override")
def override(data: dict):
    try:
        drone_id = data.get("id")

        for drone in world.drones:
            if drone.id == drone_id:
                drone.battery = data.get("battery", drone.battery)
                drone.signal_strength = data.get("signal", drone.signal_strength)
                drone.cpu_temperature = data.get("cpu", drone.cpu_temperature)
                drone.obstacle_distance = data.get("obstacle", drone.obstacle_distance)
                drone.thermal_status = data.get("thermal", drone.thermal_status)

        return {"status": "ok"}

    except Exception as e:
        print("Override Error:", str(e))
        return {"error": str(e)}


@app.post("/simulate")
def simulate_drone(data: dict = Body(...)):
    from simulation.decision_engine import evaluate_drone
    from simulation.ai_actions import apply_ai_decision

    ensure_world_drones()
    drone_id = data.get("id")
    target_drone = None
    for drone in world.drones:
        if drone.id == drone_id:
            target_drone = drone
            break

    if not target_drone:
        return {"error": f"Drone with ID {drone_id} not found."}

    target_drone.battery = float(data["battery"])
    target_drone.thermal_status = bool(data["thermal"])
    target_drone.obstacle_distance = float(data["obstacle"])
    target_drone.signal_strength = float(data["signal"])
    target_drone.cpu_temperature = float(data["cpu"])
    target_drone.propeller_health = float(data.get("propeller", target_drone.propeller_health))
    target_drone.isSimulated = True

    # Evaluate decision using the real evaluate_drone
    result = evaluate_drone(target_drone)
    
    # Apply AI decision (e.g. cooperative assists, etc.)
    apply_ai_decision(target_drone, result, world.drones, verbose=False)

    # Set last_decision and action
    target_drone.last_decision = result
    target_drone.action = result

    return {
        "drone_id": target_drone.id,
        "action": result,
        "status": getattr(target_drone, "status", "UNKNOWN"),
        "nearby_drone_id": getattr(target_drone, "nearby_drone_id", None),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
