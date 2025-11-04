"""
Example plugin file showing how to write a custom algorithm.
Drop your own files in `plugins/` and they will be discovered by the PluginManager.

Define one or more classes that inherit from `src.algorithms.base.Algorithm`.

Example class name: `MyCustomController` (use this name with --algorithm if running from CLI).
"""

from src.algorithms.base import Algorithm
from src.core.types import ControlInput, DronePhysicsState, SensorData
from src.core.types import Vector3D

class MySimplePlugin(Algorithm):
    """A trivial algorithm that slowly moves the drone to a fixed target."""
    def __init__(self, config):
        super().__init__(config)
        self.target = Vector3D(*config.get('target_position', [0.0, 0.0, 3.0]))

    def compute_control(self, physics_state: DronePhysicsState, sensor_data: SensorData, timestamp: float) -> ControlInput:
        control = ControlInput()
        # Simple proportional control to target
        kp = 0.2
        dx = self.target.x - physics_state.position.x
        dy = self.target.y - physics_state.position.y
        dz = self.target.z - physics_state.position.z
        control.roll = kp * (-dy)
        control.pitch = kp * dx
        control.thrust = 0.6 + 0.3 * kp * dz
        control.clamp()
        return control

    def reset(self):
        pass
