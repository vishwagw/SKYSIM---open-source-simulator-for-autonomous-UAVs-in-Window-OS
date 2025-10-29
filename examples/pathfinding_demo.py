"""
Advanced pathfinding demonstration using A* algorithm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml
from src.core import Simulator
from src.algorithms import PathFollowingController, AStarPathfinder
from src.visualization import RealtimeVisualizer
from src.core.logger import DataLogger
from src.core.types import Vector3D


def create_pathfinding_config():
    """Create configuration optimized for pathfinding."""
    # Load base config
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'default_config.yaml')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create a complex obstacle environment
    config['obstacles'] = [
        # Create a maze-like environment
        {'type': 'box', 'position': [5.0, 0.0, 2.5], 'dimensions': [2.0, 15.0, 5.0]},
        {'type': 'box', 'position': [15.0, 5.0, 2.5], 'dimensions': [2.0, 10.0, 5.0]},
        {'type': 'box', 'position': [25.0, -5.0, 2.5], 'dimensions': [2.0, 20.0, 5.0]},
        {'type': 'box', 'position': [10.0, -15.0, 2.5], 'dimensions': [15.0, 2.0, 5.0]},
        {'type': 'box', 'position': [20.0, 15.0, 2.5], 'dimensions': [15.0, 2.0, 5.0]},
        
        # Additional obstacles
        {'type': 'sphere', 'position': [12.0, 8.0, 4.0], 'radius': 2.0},
        {'type': 'cylinder', 'position': [30.0, 10.0, 0.0], 'radius': 2.5, 'height': 8.0},
        {'type': 'sphere', 'position': [8.0, -8.0, 3.0], 'radius': 1.5},
    ]
    
    # Extend boundaries for pathfinding demo
    config['environment']['boundaries'] = {
        'x_min': -10.0,
        'x_max': 40.0,
        'y_min': -25.0,
        'y_max': 25.0,
        'z_min': 0.0,
        'z_max': 15.0
    }
    
    return config


def main():
    """Run pathfinding example."""
    print("=== Drone Autonomy Core Simulator - A* Pathfinding ===")
    
    # Create config with complex obstacles
    config = create_pathfinding_config()
    
    # Create simulator
    simulator = Simulator(config_dict=config)
    
    # Define start and goal positions
    start_position = Vector3D(0.0, 0.0, 5.0)
    goal_position = Vector3D(35.0, 20.0, 5.0)
    
    # Create A* pathfinder
    pathfinder = AStarPathfinder(
        boundaries=config['environment']['boundaries'],
        obstacles=simulator.environment.get_obstacles(),
        grid_resolution=1.0
    )
    
    print("Computing path using A* algorithm...")
    path = pathfinder.find_path(start_position, goal_position)
    
    if path is None:
        print("ERROR: No path found from start to goal!")
        print(f"Start: {start_position}")
        print(f"Goal: {goal_position}")
        return
    
    print(f"Path found! {len(path)} waypoints computed.")
    
    # Create path following algorithm
    path_config = {
        'lookahead_distance': 4.0,
        'path_threshold': 1.5,
        'max_speed': 3.0,
        'hover_controller': {
            'position_gains': {'kp': 1.0, 'kd': 0.5},
            'altitude_gains': {'kp': 2.0, 'kd': 1.0},
            'yaw_gains': {'kp': 1.0, 'kd': 0.1},
            'hover_thrust': 0.6
        }
    }
    algorithm = PathFollowingController(path_config)
    algorithm.set_pathfinder(pathfinder)
    
    # Set the computed path
    algorithm.path = path
    algorithm.current_path_index = 0
    algorithm.path_complete = False
    
    # Create visualizer
    visualizer = RealtimeVisualizer(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Create logger
    logger = DataLogger(simulator.config)
    logger.start_session(simulator.config, {
        'example_name': 'A* Pathfinding',
        'algorithm': 'PathFollowingController',
        'description': 'A* pathfinding through complex obstacle environment',
        'start_position': [start_position.x, start_position.y, start_position.z],
        'goal_position': [goal_position.x, goal_position.y, goal_position.z],
        'path_length': len(path),
        'grid_resolution': 1.0
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
                'path_follower': algorithm.get_status(),
                'path_status': algorithm.get_path_status(),
                'distance_to_goal': (physics_state.position - goal_position).magnitude()
            })
        
        # Check path completion
        path_status = algorithm.get_path_status()
        if path_status['path_complete']:
            final_distance = (physics_state.position - goal_position).magnitude()
            logger.log_event('path_complete', f'Path following completed. Final distance to goal: {final_distance:.2f}m')
            print(f"Path following completed! Final distance to goal: {final_distance:.2f}m")
            simulator.stop()
    
    simulator.add_step_callback(on_step)
    
    # Add collision callback
    def on_collision(physics_state):
        logger.log_event('collision', f'Drone collided during pathfinding at position {physics_state.position}')
        print(f"COLLISION during pathfinding! Position: {physics_state.position}")
        print("Pathfinding failed - path may have been too close to obstacles.")
    
    simulator.add_collision_callback(on_collision)
    
    print("\nStarting pathfinding demonstration...")
    print(f"Start position: ({start_position.x:.1f}, {start_position.y:.1f}, {start_position.z:.1f})")
    print(f"Goal position: ({goal_position.x:.1f}, {goal_position.y:.1f}, {goal_position.z:.1f})")
    print(f"Computed path has {len(path)} waypoints")
    print(f"Number of obstacles to navigate: {len(config['obstacles'])}")
    print("The drone will follow the A* computed path to reach the goal.")
    print("Press Ctrl+C to stop the simulation")
    
    # Print some path waypoints
    print("\nFirst few waypoints:")
    for i, waypoint in enumerate(path[:5]):
        print(f"  {i+1}: ({waypoint.x:.1f}, {waypoint.y:.1f}, {waypoint.z:.1f})")
    if len(path) > 5:
        print(f"  ... and {len(path)-5} more waypoints")
    
    try:
        # Run autonomous simulation
        success = simulator.run_autonomous(algorithm, max_steps=25000)
        
        if success:
            print("Pathfinding mission completed successfully!")
        else:
            print("Pathfinding mission ended early.")
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        simulator.stop()
    
    finally:
        # Clean up
        logger.close()
        visualizer.close()
        
        print(f"Data logged to: {logger.get_session_directory()}")
        print("Pathfinding example completed!")


if __name__ == "__main__":
    main()