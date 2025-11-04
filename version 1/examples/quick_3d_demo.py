"""
Quick 3D Drone Models Test - Shows different drone models in 3D visualization.
Run this to see the 3D drone designs in action!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from src.core import Simulator
from src.algorithms import SimpleHoverController
from src.visualization import RealtimeVisualizer
from src.core.types import Vector3D


def quick_demo(model_name: str = "consumer_quad", duration: float = 10.0):
    """Quick demonstration of a specific drone model."""
    print(f"=== Quick 3D Demo: {model_name} ===")
    
    # Simple configuration for quick demo
    config = {
        'simulation': {
            'timestep': 0.02,
            'duration': duration,
            'real_time': True
        },
        'drone': {
            'model': model_name,
            'initial_position': [0, 0, 0],
            'initial_velocity': [0, 0, 0],
            'initial_orientation': [0, 0, 0]
        },
        'environment': {
            'gravity': 9.81,
            'wind': {'enabled': False},
            'boundaries': {
                'x_min': -20, 'x_max': 20,
                'y_min': -20, 'y_max': 20,
                'z_min': 0, 'z_max': 15
            }
        },
        'obstacles': [
            {
                'type': 'sphere',
                'position': [8, 8, 4],
                'radius': 1.5
            }
        ],
        'sensors': {
            'gps': {'enabled': True, 'noise_std': 0.1},
            'imu': {'enabled': True},
            'lidar': {'enabled': True, 'range': 15.0}
        },
        'visualization': {
            'enabled': True,
            'window_size': [1000, 700],
            'camera_follow': True,
            'show_trajectory': True,
            'trajectory_length': 50,
            'show_sensors': False,
            'update_rate': 30
        },
        'logging': {'enabled': False}
    }
    
    # Create simulator
    simulator = Simulator(config_dict=config)
    
    # Create simple hover controller
    hover_config = {
        'target_position': [0.0, 0.0, 5.0],
        'position_gains': {'kp': 1.2, 'kd': 0.6},
        'altitude_gains': {'kp': 2.5, 'kd': 1.2},
        'yaw_gains': {'kp': 1.0, 'kd': 0.1},
        'hover_thrust': 0.65
    }
    algorithm = SimpleHoverController(hover_config)
    
    # Create visualizer
    from src.visualization.visualizer_3d import Visualizer3D
    visualizer = Visualizer3D(simulator.config)
    visualizer.set_obstacles(simulator.environment.get_obstacles())
    
    # Print drone info
    drone_info = visualizer.get_current_drone_info()
    print(f"Drone: {drone_info['name']}")
    print(f"Mass: {drone_info.get('mass', 'N/A')} kg")
    print(f"Max Thrust: {drone_info.get('max_thrust', 'N/A')} N")
    print(f"3D Mesh: {'Yes' if drone_info['mesh_loaded'] else 'Simple wireframe'}")
    print(f"Target: Hover at (0, 0, 5)")
    print(f"Duration: {duration}s")
    print()
    print("3D Controls:")
    print("- Mouse: Rotate view")
    print("- Mouse wheel: Zoom")
    print("- Close window to end demo")
    print()
    
    # Simple step callback
    def on_step(timestamp, physics_state, sensor_data):
        if not visualizer.update(physics_state, sensor_data):
            simulator.stop()  # User closed window
    
    simulator.add_step_callback(on_step)
    
    try:
        print("Starting 3D visualization...")
        success = simulator.run_autonomous(algorithm, max_steps=int(duration/config['simulation']['timestep']))
        
        if success:
            print(f"Demo completed successfully!")
        else:
            print(f"Demo ended early")
            
    except KeyboardInterrupt:
        print("Demo interrupted by user")
        simulator.stop()
    
    finally:
        visualizer.close()
        print("Demo finished!")


def compare_models():
    """Compare different drone models side by side."""
    models = ['micro_quad', 'racing_quad', 'consumer_quad', 'heavy_lift', 'vtol_wing']
    
    print("=== 3D Drone Models Comparison ===")
    print("This will show each drone model for 8 seconds")
    print("Watch how the different designs look and move!")
    print()
    
    for i, model in enumerate(models):
        print(f"[{i+1}/{len(models)}] Showing: {model}")
        quick_demo(model, 8.0)
        
        if i < len(models) - 1:
            print("Next model in 2 seconds...")
            time.sleep(2)
    
    print("\n🎉 Comparison complete!")
    print("Each model has different:")
    print("- Size and proportions")
    print("- Flight characteristics") 
    print("- Color coding")
    print("- 3D mesh geometry")


def interactive_3d_explorer():
    """Interactive explorer for 3D drone models."""
    from src.core.drone_models import DroneDesigner
    
    designer = DroneDesigner()
    models = list(designer.list_available_models().keys())
    
    print("=== Interactive 3D Drone Explorer ===")
    print("Choose a drone model to see in 3D!")
    print()
    
    while True:
        print("Available models:")
        for i, model in enumerate(models):
            spec = designer.get_drone_spec(model)
            if spec:
                print(f"  {i+1}. {model} - {spec.name} ({spec.mass}kg)")
            else:
                print(f"  {i+1}. {model} - Unknown model")
        
        print(f"  {len(models)+1}. Compare all models")
        print(f"  {len(models)+2}. Exit")
        
        try:
            choice = input(f"\nChoose (1-{len(models)+2}): ").strip()
            
            if choice == str(len(models)+2):
                break
            elif choice == str(len(models)+1):
                compare_models()
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(models):
                    model = models[choice_idx]
                    duration = float(input("Duration in seconds (default 15): ") or "15")
                    quick_demo(model, duration)
                else:
                    print("Invalid choice!")
        except (ValueError, KeyboardInterrupt):
            break
        
        print()
    
    print("Thanks for exploring!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick 3D Drone Models Demo')
    parser.add_argument('--model', '-m', type=str, default='consumer_quad',
                        help='Drone model to demo (default: consumer_quad)')
    parser.add_argument('--duration', '-d', type=float, default=15.0,
                        help='Demo duration in seconds (default: 15)')
    parser.add_argument('--compare', '-c', action='store_true',
                        help='Compare all models')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_3d_explorer()
    elif args.compare:
        compare_models()
    else:
        quick_demo(args.model, args.duration)