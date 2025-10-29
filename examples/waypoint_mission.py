"""
Waypoint following mission example.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core import Simulator
from src.algorithms import WaypointFollower
from src.visualization import RealtimeVisualizer
from src.core.logger import DataLogger
from src.core.types import Vector3D


def main():
    """Run waypoint following example."""
    print("=== Drone Autonomy Core Simulator - Waypoint Mission ===")
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'default_config.yaml')
    
    # Create simulator
    simulator = Simulator(config_file=config_file)
    
    # Create waypoint mission
    waypoints = [
        [0.0, 0.0, 5.0],    # Takeoff
        [10.0, 0.0, 5.0],   # Move east
        [10.0, 10.0, 5.0],  # Move north
        [0.0, 10.0, 5.0],   # Move west
        [0.0, 0.0, 5.0],    # Return home
        [0.0, 0.0, 2.0]     # Descend
    ]
    
    # Create algorithm
    waypoint_config = {
        'waypoints': waypoints,
        'waypoint_threshold': 2.0,
        'hover_controller': {
            'position_gains': {'kp': 1.2, 'kd': 0.6},
            'altitude_gains': {'kp': 2.5, 'kd': 1.2},
            'yaw_gains': {'kp': 1.0, 'kd': 0.1},
            'hover_thrust': 0.6
        }
    }
    algorithm = WaypointFollower(waypoint_config)
    
    # Create visualizer
    visualizer = RealtimeVisualizer(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Create logger
    logger = DataLogger(simulator.config)
    logger.start_session(simulator.config, {
        'example_name': 'Waypoint Mission',
        'algorithm': 'WaypointFollower',
        'description': 'Autonomous waypoint following demonstration',
        'waypoints': waypoints
    })
    
    # Add callbacks
    def on_step(timestamp, physics_state, sensor_data):
        # Update visualization
        if not visualizer.update(physics_state, sensor_data):
            simulator.stop()
        
        # Log data
        control_input = algorithm.control_outputs[-1] if algorithm.control_outputs else None
        if control_input:
            logger.log_step(timestamp, physics_state, sensor_data, control_input, {
                'waypoint_follower': algorithm.get_status(),
                'mission_status': algorithm.get_mission_status()
            })
        
        # Check mission progress
        mission_status = algorithm.get_mission_status()
        if mission_status['mission_complete']:
            print("Mission completed! All waypoints reached.")
            simulator.stop()
    
    simulator.add_step_callback(on_step)
    
    # Add collision callback
    def on_collision(physics_state):
        logger.log_event('collision', f'Drone collided at position {physics_state.position}')
        print(f"Collision detected at {physics_state.position}")
    
    simulator.add_collision_callback(on_collision)
    
    print("Starting waypoint mission...")
    print(f"Mission includes {len(waypoints)} waypoints:")
    for i, wp in enumerate(waypoints):
        print(f"  {i+1}: ({wp[0]:.1f}, {wp[1]:.1f}, {wp[2]:.1f})")
    print("Press Ctrl+C to stop the simulation")
    
    try:
        # Run autonomous simulation
        success = simulator.run_autonomous(algorithm, max_steps=15000)
        
        if success:
            print("Mission completed successfully!")
        else:
            print("Mission ended early.")
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        simulator.stop()
    
    finally:
        # Clean up
        logger.close()
        visualizer.close()
        
        print(f"Data logged to: {logger.get_session_directory()}")
        print("Mission example completed!")


if __name__ == "__main__":
    main()