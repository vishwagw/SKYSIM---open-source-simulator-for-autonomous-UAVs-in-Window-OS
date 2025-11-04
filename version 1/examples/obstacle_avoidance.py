"""
Obstacle avoidance demonstration using LiDAR sensor.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml
from src.core import Simulator
from src.algorithms import ObstacleAvoidance
from src.visualization import RealtimeVisualizer
from src.core.logger import DataLogger
from src.core.types import Vector3D


def create_obstacle_course_config():
    """Create configuration with obstacles."""
    # Load base config
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'default_config.yaml')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Add more obstacles for demonstration
    config['obstacles'] = [
        # Original obstacles
        {
            'type': 'sphere',
            'position': [10.0, 10.0, 5.0],
            'radius': 2.0
        },
        {
            'type': 'box',
            'position': [20.0, -15.0, 3.0],
            'dimensions': [4.0, 4.0, 6.0]
        },
        {
            'type': 'cylinder',
            'position': [-10.0, 20.0, 0.0],
            'radius': 1.5,
            'height': 8.0
        },
        
        # Additional obstacles for avoidance demo
        {
            'type': 'sphere',
            'position': [15.0, 5.0, 4.0],
            'radius': 1.5
        },
        {
            'type': 'box',
            'position': [5.0, 15.0, 2.5],
            'dimensions': [3.0, 3.0, 5.0]
        },
        {
            'type': 'cylinder',
            'position': [-5.0, -5.0, 0.0],
            'radius': 2.0,
            'height': 6.0
        },
        {
            'type': 'sphere',
            'position': [25.0, 20.0, 6.0],
            'radius': 2.5
        }
    ]
    
    # Enhance LiDAR configuration for better obstacle detection
    config['sensors']['lidar']['resolution'] = 720  # Higher resolution
    config['sensors']['lidar']['range'] = 15.0
    config['sensors']['lidar']['update_rate'] = 30
    
    return config


def main():
    """Run obstacle avoidance example."""
    print("=== Drone Autonomy Core Simulator - Obstacle Avoidance ===")
    
    # Create config with obstacles
    config = create_obstacle_course_config()
    
    # Create simulator
    simulator = Simulator(config_dict=config)
    
    # Create obstacle avoidance algorithm
    avoidance_config = {
        'avoidance_distance': 4.0,
        'avoidance_strength': 3.0,
        'max_avoidance_force': 0.8,
        'base_controller': {
            'target_position': [20.0, 20.0, 5.0],  # Target through obstacle field
            'position_gains': {'kp': 0.8, 'kd': 0.4},
            'altitude_gains': {'kp': 2.0, 'kd': 1.0},
            'yaw_gains': {'kp': 1.0, 'kd': 0.1},
            'hover_thrust': 0.6
        }
    }
    algorithm = ObstacleAvoidance(avoidance_config)
    
    # Create visualizer
    visualizer = RealtimeVisualizer(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Create logger
    logger = DataLogger(simulator.config)
    logger.start_session(simulator.config, {
        'example_name': 'Obstacle Avoidance',
        'algorithm': 'ObstacleAvoidance',
        'description': 'LiDAR-based obstacle avoidance demonstration',
        'target_position': avoidance_config['base_controller']['target_position']
    })
    
    # Variables to track progress
    target_position = Vector3D(*avoidance_config['base_controller']['target_position'])
    mission_complete = False
    
    # Add callbacks
    def on_step(timestamp, physics_state, sensor_data):
        nonlocal mission_complete
        
        # Update visualization
        if not visualizer.update(physics_state, sensor_data):
            simulator.stop()
        
        # Log data
        control_input = algorithm.control_outputs[-1] if algorithm.control_outputs else None
        if control_input:
            # Calculate distance to obstacles from LiDAR
            min_obstacle_distance = float('inf')
            if sensor_data and sensor_data.lidar_ranges:
                min_obstacle_distance = min(sensor_data.lidar_ranges)
            
            logger.log_step(timestamp, physics_state, sensor_data, control_input, {
                'obstacle_avoidance': algorithm.get_status(),
                'min_obstacle_distance': min_obstacle_distance,
                'distance_to_target': (physics_state.position - target_position).magnitude()
            })
        
        # Check if target is reached
        distance_to_target = (physics_state.position - target_position).magnitude()
        if distance_to_target < 3.0 and not mission_complete:
            mission_complete = True
            logger.log_event('mission_complete', 'Target reached successfully while avoiding obstacles')
            print(f"Target reached! Final distance: {distance_to_target:.2f}m")
            # Continue for a bit to show hovering
            simulator.set_simulation_speed(0.5)  # Slow down to observe
    
    simulator.add_step_callback(on_step)
    
    # Add collision callback
    def on_collision(physics_state):
        logger.log_event('collision', f'Drone collided at position {physics_state.position}')
        print(f"COLLISION! Position: {physics_state.position}")
        print("Obstacle avoidance failed!")
    
    simulator.add_collision_callback(on_collision)
    
    print("Starting obstacle avoidance demonstration...")
    print(f"Number of obstacles: {len(config['obstacles'])}")
    print(f"Target position: ({target_position.x:.1f}, {target_position.y:.1f}, {target_position.z:.1f})")
    print("The drone will use LiDAR to detect and avoid obstacles while moving to the target.")
    print("Press Ctrl+C to stop the simulation")
    print("Watch for real-time obstacle avoidance behavior!")
    
    try:
        # Run autonomous simulation
        success = simulator.run_autonomous(algorithm, max_steps=20000)
        
        if success and mission_complete:
            print("Mission completed successfully! Drone avoided all obstacles.")
        elif success:
            print("Simulation completed without reaching target.")
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
        print("Obstacle avoidance example completed!")


if __name__ == "__main__":
    main()