"""
Drone Models Showcase - Demonstrates different 3D drone designs in the simulator.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import numpy as np
from src.core import Simulator
from src.algorithms import SimpleHoverController
from src.visualization import RealtimeVisualizer
from src.core.logger import DataLogger
from src.core.types import Vector3D
from src.core.drone_models import DroneDesigner


def demonstrate_drone_model(model_name: str, target_position: list, duration: float = 30.0):
    """Demonstrate a specific drone model."""
    print(f"\n=== Demonstrating {model_name} ===")
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'default_config.yaml')
    
    # Create simulator with custom drone model
    simulator = Simulator(config_file=config_file)
    
    # Update drone configuration with the selected model
    drone_designer = DroneDesigner()
    drone_spec = drone_designer.get_drone_spec(model_name)
    
    if drone_spec:
        # Update simulator configuration with drone specs
        physics_config = drone_designer.get_physics_config(model_name)
        simulator.config['drone'].update(physics_config)
        simulator.config['drone']['model'] = model_name
        
        print(f"Model: {drone_spec.name}")
        print(f"Mass: {drone_spec.mass} kg")
        print(f"Max Thrust: {drone_spec.max_thrust} N")
        print(f"Arm Length: {drone_spec.arm_length} m")
        
        # Reinitialize physics with new parameters
        simulator._initialize_physics()
    else:
        print(f"Warning: Model '{model_name}' not found, using default")
    
    # Create algorithm with adjusted parameters for the drone model
    hover_thrust = 0.6
    if drone_spec:
        # Adjust hover thrust based on mass and max thrust
        hover_thrust = min(0.8, (drone_spec.mass * 9.81) / drone_spec.max_thrust)
    
    hover_config = {
        'target_position': target_position,
        'position_gains': {'kp': 1.0, 'kd': 0.5},
        'altitude_gains': {'kp': 2.0, 'kd': 1.0},
        'yaw_gains': {'kp': 1.0, 'kd': 0.1},
        'hover_thrust': hover_thrust
    }
    algorithm = SimpleHoverController(hover_config)
    
    # Create visualizer with the drone model
    visualizer = RealtimeVisualizer(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Print current drone info
    drone_info = visualizer.get_current_drone_info()
    if drone_info['loaded']:
        print(f"Visualizer loaded: {drone_info['name']}")
        print(f"3D Mesh: {'Yes' if drone_info['mesh_loaded'] else 'Simple wireframe'}")
    
    # Create logger
    logger = DataLogger(simulator.config)
    logger.start_session(simulator.config, {
        'example_name': 'Drone Models Showcase',
        'drone_model': model_name,
        'algorithm': 'SimpleHoverController',
        'description': f'Demonstration of {model_name} drone model'
    })
    
    # Step counter for demo
    step_count = [0]
    max_steps = int(duration / simulator.config['simulation']['timestep'])
    
    # Add callbacks
    def on_step(timestamp, physics_state, sensor_data):
        step_count[0] += 1
        
        # Update visualization
        if not visualizer.update(physics_state, sensor_data):
            simulator.stop()  # User closed window
        
        # Log data
        control_input = algorithm.control_outputs[-1] if algorithm.control_outputs else None
        if control_input:
            logger.log_step(timestamp, physics_state, sensor_data, control_input, {
                'hover_controller': algorithm.get_status(),
                'drone_model': model_name
            })
        
        # Stop after duration
        if step_count[0] >= max_steps:
            simulator.stop()
    
    simulator.add_step_callback(on_step)
    
    # Add collision callback
    def on_collision(physics_state):
        logger.log_event('collision', f'Drone {model_name} collided at position {physics_state.position}')
        print(f"Collision detected at {physics_state.position}")
    
    simulator.add_collision_callback(on_collision)
    
    print(f"Target position: {target_position}")
    print(f"Duration: {duration}s")
    print("Press Ctrl+C to skip to next model")
    
    try:
        # Run autonomous simulation
        success = simulator.run_autonomous(algorithm, max_steps=max_steps)
        
        if success:
            print(f"{model_name} demonstration completed successfully!")
        else:
            print(f"{model_name} demonstration ended early.")
            
    except KeyboardInterrupt:
        print(f"\n{model_name} demonstration interrupted by user")
        simulator.stop()
    
    finally:
        # Clean up
        logger.close()
        visualizer.close()
        
        print(f"Data logged to: {logger.get_session_directory()}")
    
    return success


def main():
    """Run drone models showcase."""
    print("=== Drone Autonomy Core Simulator - 3D Drone Models Showcase ===")
    print("This example demonstrates different drone models with 3D visualization")
    
    # Get available models
    drone_designer = DroneDesigner()
    models = drone_designer.list_available_models()
    
    print("\nAvailable Drone Models:")
    for key, name in models.items():
        spec = drone_designer.get_drone_spec(key)
        print(f"  {key}: {name} ({spec.mass}kg, {spec.max_thrust}N max thrust)")
    
    # Define demonstration sequence
    demonstrations = [
        ("micro_quad", [5.0, 5.0, 3.0], 20.0),
        ("racing_quad", [10.0, -5.0, 5.0], 25.0),
        ("consumer_quad", [0.0, 0.0, 8.0], 30.0),
        ("heavy_lift", [-10.0, 10.0, 6.0], 35.0),
        ("vtol_wing", [15.0, 0.0, 10.0], 30.0)
    ]
    
    print(f"\nWill demonstrate {len(demonstrations)} drone models")
    print("Each model will fly to a different target position")
    print("You can press Ctrl+C during any demonstration to skip to the next model")
    
    input("\nPress Enter to start the showcase...")
    
    success_count = 0
    
    for i, (model_name, target_pos, duration) in enumerate(demonstrations):
        print(f"\n--- Demonstration {i+1}/{len(demonstrations)} ---")
        
        try:
            success = demonstrate_drone_model(model_name, target_pos, duration)
            if success:
                success_count += 1
            
            if i < len(demonstrations) - 1:
                print("\nWaiting 3 seconds before next demonstration...")
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\nShowcase interrupted by user")
            break
    
    print(f"\n=== Showcase Complete ===")
    print(f"Successfully demonstrated {success_count}/{len(demonstrations)} models")
    print("All drone models support both 3D mesh rendering and wireframe fallback")
    print("Mesh rendering requires the 'trimesh' library (already in requirements.txt)")


def interactive_mode():
    """Interactive mode to explore different drone models."""
    print("\n=== Interactive Drone Model Explorer ===")
    
    drone_designer = DroneDesigner()
    models = list(drone_designer.list_available_models().keys())
    
    while True:
        print(f"\nAvailable models: {', '.join(models)}")
        print("Commands:")
        print("  <model_name> - Demonstrate a specific model")
        print("  list - List all models with details")
        print("  info <model_name> - Show detailed info about a model")
        print("  quit - Exit interactive mode")
        
        command = input("\nEnter command: ").strip().lower()
        
        if command == "quit":
            break
        elif command == "list":
            models_dict = drone_designer.list_available_models()
            for key, name in models_dict.items():
                spec = drone_designer.get_drone_spec(key)
                print(f"  {key}: {name}")
                print(f"    Mass: {spec.mass} kg")
                print(f"    Max Thrust: {spec.max_thrust} N")
                print(f"    Arm Length: {spec.arm_length} m")
                print(f"    Color: {spec.color}")
        elif command.startswith("info "):
            model_name = command[5:].strip()
            spec = drone_designer.get_drone_spec(model_name)
            if spec:
                print(f"\nDetailed info for {model_name}:")
                print(f"  Name: {spec.name}")
                print(f"  Mass: {spec.mass} kg")
                print(f"  Max Thrust: {spec.max_thrust} N")
                print(f"  Max Angular Velocity: {spec.max_angular_velocity} rad/s")
                print(f"  Drag Coefficient: {spec.drag_coefficient}")
                print(f"  Moment of Inertia: {spec.moment_of_inertia}")
                print(f"  Arm Length: {spec.arm_length} m")
                print(f"  Propeller Diameter: {spec.propeller_diameter} m")
                print(f"  Body Dimensions: {spec.body_dimensions} m")
                print(f"  Color: {spec.color}")
                print(f"  Mesh File: {spec.mesh_file or 'Procedural'}")
            else:
                print(f"Model '{model_name}' not found")
        elif command in models:
            # Demonstrate the selected model
            target_pos = [0.0, 0.0, 5.0]  # Default hover position
            print(f"Demonstrating {command} at position {target_pos}")
            demonstrate_drone_model(command, target_pos, 30.0)
        else:
            print(f"Unknown command or model: {command}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Drone Models Showcase')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--model', '-m', type=str,
                        help='Demonstrate a specific model')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.model:
        # Demonstrate specific model
        demonstrate_drone_model(args.model, [0.0, 0.0, 5.0], 30.0)
    else:
        # Run full showcase
        main()