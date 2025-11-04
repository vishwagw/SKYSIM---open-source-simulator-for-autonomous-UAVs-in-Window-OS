"""
Basic flight example demonstrating simple hover control.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from src.core import Simulator
from src.algorithms import SimpleHoverController
from src.visualization import RealtimeVisualizer
from src.core.logger import DataLogger
from src.core.types import Vector3D


def main():
    """Run basic flight example."""
    print("=== Drone Autonomy Core Simulator - Basic Flight Example ===")
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'default_config.yaml')
    
    # Create simulator
    simulator = Simulator(config_file=config_file)
    
    # Create algorithm
    hover_config = {
        'target_position': [0.0, 0.0, 5.0],
        'position_gains': {'kp': 1.0, 'kd': 0.5},
        'altitude_gains': {'kp': 2.0, 'kd': 1.0},
        'yaw_gains': {'kp': 1.0, 'kd': 0.1},
        'hover_thrust': 0.6
    }
    algorithm = SimpleHoverController(hover_config)
    
    # Create visualizer
    visualizer = RealtimeVisualizer(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Create logger
    logger = DataLogger(simulator.config)
    logger.start_session(simulator.config, {
        'example_name': 'Basic Flight',
        'algorithm': 'SimpleHoverController',
        'description': 'Basic hover control demonstration'
    })
    
    # Add callbacks
    def on_step(timestamp, physics_state, sensor_data):
        # Update visualization
        if not visualizer.update(physics_state, sensor_data):
            simulator.stop()  # User closed window
        
        # Log data
        control_input = algorithm.control_outputs[-1] if algorithm.control_outputs else None
        if control_input:
            logger.log_step(timestamp, physics_state, sensor_data, control_input, {
                'hover_controller': algorithm.get_status()
            })
    
    simulator.add_step_callback(on_step)
    
    # Add collision callback
    def on_collision(physics_state):
        logger.log_event('collision', f'Drone collided at position {physics_state.position}')
        print(f"Collision detected at {physics_state.position}")
    
    simulator.add_collision_callback(on_collision)
    
    print("Starting simulation...")
    print("Target position: (0, 0, 5)")
    print("Press Ctrl+C to stop the simulation")
    print("In the visualization window: V = toggle view, C = clear trajectory")
    
    try:
        # Run autonomous simulation
        success = simulator.run_autonomous(algorithm, max_steps=10000)
        
        if success:
            print("Simulation completed successfully!")
        else:
            print("Simulation ended early.")
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        simulator.stop()
    
    finally:
        # Clean up
        logger.close()
        visualizer.close()
        
        print(f"Data logged to: {logger.get_session_directory()}")
        print("Example completed!")


if __name__ == "__main__":
    main()