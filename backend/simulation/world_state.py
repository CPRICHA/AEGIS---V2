import numpy as np
import random

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field

@dataclass
class DroneState:
    id: int
    callsign: str            # FALCON, HAWK, OSPREY, KESTREL, MERLIN
    status: str              # SCANNING | SEARCHING | RETURNING | CHARGING | IDLE
    pos: np.ndarray          # [x, y, z] in metres, z = altitude
    vel: np.ndarray = field(default_factory=lambda: np.zeros(3))
    battery: float = 100.0   # 0.0 to 100.0
    trajectory: List[np.ndarray] = field(default_factory=list) # planned future waypoints
    trail: List[np.ndarray] = field(default_factory=list)      # last 200 positions
    heading: float = 0.0     # degrees 0-360
    current_target: Optional[np.ndarray] = None
    thermal_frame: bytes = b""
    camera_frame: bytes = b""
    scan_radius: float = 15.0 # current thermal scan cone radius in metres
    radius: float = 40.0      # orbit radius
    phaseOffset: float = 0.0  # orbit start angle
    orbitSpeed: float = 1.0   # angular velocity
    assigned_zone: Tuple[int, int, int, int] = (0, 0, 10, 10) # (x1,y1,x2,y2) grid indices
    
    propeller_health: float = 100.0
    motor_temperature: float = 45.0
    cpu_temperature: float = 40.0

    signal_strength: float = 100.0
    packet_loss: float = 0.0

    thermal_status: bool = True
    lidar_status: bool = True
    camera_status: bool = True
    gps_status: bool = False

    
    smoke_density: float = 0.0
    moisture_level: float = 0.0
    wind_speed: float = 0.0
    ambient_temperature: float = 25.0

    altitude: float = 20.0
    direction: float = 0.0
    obstacle_distance: float = 10.0

   
    autonomous_mode: bool = False
    last_decision: str = "CONTINUE_MISSION"
    reward_score: float = 0.0

   
    nearby_drone_id: Optional[int] = None
    requesting_support: bool = False

    

    recent_events: List[str] = field(default_factory=list)
    
    def update_telemetry(self):

        # -------------------------
        # BATTERY DRAIN
        # -------------------------
        self.battery -= random.uniform(0.01, 0.2)
        self.battery = max(0, self.battery)

        # -------------------------
        # SIGNAL FLUCTUATION
        # -------------------------
        self.signal_strength += random.uniform(-2, 2)
        self.signal_strength = max(0, min(100, self.signal_strength))

        # -------------------------
        # TEMPERATURE CHANGES
        # -------------------------
        self.cpu_temperature += random.uniform(-1, 1)
        self.motor_temperature += random.uniform(-1, 1)

        # -------------------------
        # ENVIRONMENT CHANGES
        # -------------------------
        self.smoke_density = random.uniform(0, 100)
        self.moisture_level = random.uniform(0, 100)
        self.wind_speed = random.uniform(0, 30)

        # -------------------------
        # NAVIGATION
        # -------------------------
        self.altitude += random.uniform(-1, 1)
        self.obstacle_distance = random.uniform(0.2, 15)

        # -------------------------
        # RANDOM FAILURES
        # -------------------------
        if random.random() < 0.002:
            self.thermal_status = False
            self.recent_events.append("THERMAL_SENSOR_FAILURE")

        if random.random() < 0.002:
            self.lidar_status = False
            self.recent_events.append("LIDAR_FAILURE")

        if random.random() < 0.002:
            self.propeller_health -= random.uniform(20, 50)
            self.recent_events.append("PROPELLER_DAMAGE")

        self.propeller_health = max(0, self.propeller_health)

        # -------------------------
        # AUTONOMOUS FALLBACK
        # -------------------------
        if self.signal_strength < 20:
            self.autonomous_mode = True
            self.recent_events.append(
                "AUTONOMOUS_MODE_ENABLED"
            )


    
    
@dataclass
class Survivor:
    id: int
    pos: np.ndarray          # [x, y, z] in world units
    alive: bool = True
    body_temp: float = 37.0  # 36.0 to 38.5
    confidence: float = 0.0  # 0.0 to 1.0, increases as drone gets closer
    detected: bool = False
    detected_by: Optional[int] = None
    detected_at: float = 0.0 # sim_time
    rescued: bool = False
    real_coords: Tuple[float, float] = (0.0, 0.0) # (lat, lon)
    moving: bool = False

@dataclass
class LogEntry:
    time: float
    drone_id: Optional[int]
    category: str            # "drone" | "survivor" | "warning" | "critical" | "system"
    message: str

class WorldState:
    def __init__(self):
        self.scenario: str = "earthquake"
        self.running: bool = False
        self.speed: float = 1.0
        self.sim_time: float = 0.0          # seconds elapsed
        self.tick: int = 0
        
        self.drones: List[DroneState] = []
        self.survivors: List[Survivor] = []
        self.detected_survivors: List[int] = [] # IDs of found survivors
        self.event_log: List[LogEntry] = []
        
        # Grid settings (100m x 100m zone, 20x20 cells, 5m per cell)
        self.terrain_grid: np.ndarray = np.zeros((20, 20)) # Values 0-1 (damage level)
        self.zone_coverage: np.ndarray = np.zeros((20, 20)) # Values 0/1 (scanned or not)
        
        self.ambient_temp: float = 20.0
        self.water_level: float = 0.0
        self.wind_vector: np.ndarray = np.array([0.0, 0.0])
        self.hazard_zones: List[Dict] = [] # list of {center: [x,y], radius: r, type: str}
    
    def reset(self, scenario: str):
        self.scenario = scenario
        self.running = False
        self.sim_time = 0.0
        self.tick = 0
        self.drones = []
        self.survivors = []
        self.detected_survivors = []
        self.event_log = []
        self.terrain_grid = np.zeros((20, 20))
        self.zone_coverage = np.zeros((20, 20))
        self.water_level = 0.0
        self.hazard_zones = []

# Single global world state
world = WorldState()
