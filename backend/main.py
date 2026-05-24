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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    ensure_world_drones()

    try:
        while True:
            results = []

            for drone in world.drones:
                decision = evaluate_drone(drone)
                apply_ai_decision(drone, decision, world.drones, verbose=False)

                results.append({
                    "id": drone.id,
                    "battery": drone.battery,
                    "signal": drone.signal_strength,
                    "cpu": drone.cpu_temperature,
                    "status": drone.status,
                    "action": decision,
                    "nearby_drone_id": getattr(drone, "nearby_drone_id", None),
                })

            await websocket.send_json({"drones": results})
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("WebSocket Error:", e)

    finally:
        print("Connection closed cleanly")


@app.post("/override")
def override_drone(data: dict = Body(...)):
    ensure_world_drones()
    drone_id = data["id"]

    for drone in world.drones:
        if drone.id == drone_id:
            for key, value in data.items():
                if key == "id":
                    continue
                if hasattr(drone, key):
                    setattr(drone, key, value)
            return {"status": "updated", "drone_id": drone_id}

    return {"status": "not_found", "drone_id": drone_id}


@app.post("/simulate")
def simulate_drone(data: dict = Body(...)):
    from simulation.decision_engine import evaluate_drone
    from simulation.ai_actions import apply_ai_decision

    def _make_drone(drone_id, pos_offset):
        d = type("DummyDrone", (), {})()
        d.id = drone_id
        d.battery = 100.0
        d.thermal_status = True
        d.obstacle_distance = 10.0
        d.signal_strength = 100.0
        d.cpu_temperature = 40.0
        d.propeller_health = 100.0
        d.lidar_status = True
        d.moisture_level = 0.0
        d.smoke_density = 0.0
        d.altitude = 20.0
        d.vel = np.zeros(3)
        d.pos = np.array([float(pos_offset), 0.0, 20.0])
        d.status = "ACTIVE"
        d.reward_score = 0.0
        d.direction = 0.0
        d.autonomous_mode = False
        d.requesting_support = False
        d.nearby_drone_id = None
        d.recent_events = []
        return d

    fleet = [_make_drone(i, i * 15) for i in range(1, 6)]
    drone = fleet[data["id"] - 1]

    drone.battery = float(data["battery"])
    drone.thermal_status = bool(data["thermal"])
    drone.obstacle_distance = float(data["obstacle"])
    drone.signal_strength = float(data["signal"])
    drone.cpu_temperature = float(data["cpu"])
    drone.propeller_health = float(data.get("propeller", 100))

    result = evaluate_drone(drone)
    apply_ai_decision(drone, result, fleet, verbose=False)

    return {
        "drone_id": drone.id,
        "action": result,
        "status": getattr(drone, "status", "UNKNOWN"),
        "nearby_drone_id": getattr(drone, "nearby_drone_id", None),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
