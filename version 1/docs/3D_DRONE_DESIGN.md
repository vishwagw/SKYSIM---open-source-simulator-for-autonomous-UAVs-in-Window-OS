# 3D Drone Design System

The SKYSIM Prototype 1 simulator includes a comprehensive 3D drone design system that allows you to visualize and simulate different types of drones with realistic 3D models.

## Features

### Available Drone Models

The system includes several predefined drone models:

1. **Micro Quadcopter** (`micro_quad`)
   - Mass: 0.15 kg
   - Max Thrust: 3.0 N
   - Ideal for: Indoor flight, tight spaces
   - Color: Yellow

2. **Racing Quadcopter** (`racing_quad`)
   - Mass: 0.8 kg
   - Max Thrust: 15.0 N
   - Ideal for: High-speed flight, racing
   - Color: Red

3. **Consumer Quadcopter** (`consumer_quad`) - Default
   - Mass: 1.5 kg
   - Max Thrust: 20.0 N
   - Ideal for: General purpose, aerial photography
   - Color: Blue

4. **Heavy Lift Hexacopter** (`heavy_lift`)
   - Mass: 4.5 kg
   - Max Thrust: 60.0 N
   - Ideal for: Payload delivery, industrial applications
   - Color: Gray

5. **VTOL Fixed-Wing** (`vtol_wing`)
   - Mass: 3.2 kg
   - Max Thrust: 35.0 N
   - Ideal for: Long-range missions, efficient flight
   - Color: Green

### 3D Visualization

The system supports two rendering modes:

1. **Procedural 3D Meshes**: Automatically generated 3D models using the `trimesh` library
2. **Wireframe Fallback**: Simple line-based representations when 3D meshes are unavailable

## Quick Start

### 1. Basic Usage

Select a drone model in your configuration file:

```yaml
# config/default_config.yaml
drone:
  model: "racing_quad"  # Choose your drone model
```

### 2. Running the Showcase

Experience all drone models with the showcase example:

```bash
# Run the full showcase (demonstrates all models)
python examples/drone_models_showcase.py

# Interactive mode to explore models
python examples/drone_models_showcase.py --interactive

# Demonstrate a specific model
python examples/drone_models_showcase.py --model racing_quad
```

### 3. Using the Utilities

Manage drone models with the utility script:

```bash
# List all available models
python tools/drone_model_utils.py list

# Export a model as 3D mesh file
python tools/drone_model_utils.py export consumer_quad my_drone.obj

# Export all models
python tools/drone_model_utils.py export-all ./drone_meshes/

# Validate a model
python tools/drone_model_utils.py validate heavy_lift

# Create custom drone template
python tools/drone_model_utils.py template
```

## Advanced Usage

### Creating Custom Drone Models

1. **Using the Designer API:**

```python
from src.core.drone_models import DroneDesigner

designer = DroneDesigner()

# Create a custom drone
custom_spec = designer.create_custom_drone(
    name="My Custom Drone",
    mass=2.0,                    # kg
    max_thrust=25.0,             # N
    max_angular_velocity=6.0,    # rad/s
    arm_length=0.25,             # meters
    color=(0.8, 0.2, 0.8),       # RGB purple
    body_dimensions=(0.4, 0.4, 0.15)  # L×W×H meters
)
```

2. **Programmatic Configuration:**

```python
from src.core import Simulator
from src.core.drone_models import DroneDesigner

# Create simulator
simulator = Simulator(config_file='config/default_config.yaml')

# Apply custom drone configuration
designer = DroneDesigner()
physics_config = designer.get_physics_config('racing_quad')
simulator.config['drone'].update(physics_config)
simulator.config['drone']['model'] = 'racing_quad'

# Reinitialize physics with new parameters
simulator._initialize_physics()
```

### Changing Models During Runtime

```python
# In your visualization code
visualizer.set_drone_model('heavy_lift')
visualizer.list_available_drone_models()

# Get current drone information
info = visualizer.get_current_drone_info()
print(f"Current model: {info['name']}")
print(f"3D mesh loaded: {info['mesh_loaded']}")
```

## Technical Details

### Drone Specifications

Each drone model includes:

- **Physical Properties**: Mass, thrust, angular velocity limits
- **Geometric Properties**: Arm length, propeller size, body dimensions
- **Visual Properties**: Color, 3D mesh (if available)
- **Flight Characteristics**: Drag coefficient, moment of inertia

### 3D Mesh Generation

The system automatically generates 3D meshes for different drone types:

- **Quadcopters**: Cross-frame with 4 arms and propellers
- **Hexacopters**: Circular frame with 6 arms
- **VTOL Aircraft**: Fuselage with wings and multiple propellers

### File Format Support

Supported 3D file formats for custom meshes:
- OBJ (recommended)
- STL
- PLY
- GLTF/GLB

## Integration with Physics

The drone models directly influence the physics simulation:

- **Mass**: Affects acceleration and energy requirements
- **Thrust Limits**: Determines maximum climb rate and agility
- **Moment of Inertia**: Influences rotational dynamics
- **Drag Coefficient**: Affects air resistance and efficiency

## Examples

### Example 1: Racing Simulation

```python
# Configure for racing scenario
config = {
    'drone': {
        'model': 'racing_quad',
        'initial_position': [0, 0, 1]
    },
    'visualization': {
        'camera_follow': True,
        'show_trajectory': True
    }
}
```

### Example 2: Payload Delivery

```python
# Configure for heavy lifting
config = {
    'drone': {
        'model': 'heavy_lift',
        'initial_position': [0, 0, 2]
    },
    'environment': {
        'wind': {
            'enabled': True,
            'base_velocity': [5, 0, 0]  # Strong wind
        }
    }
}
```

### Example 3: Long-Range Mission

```python
# Configure for efficiency
config = {
    'drone': {
        'model': 'vtol_wing',
        'initial_position': [0, 0, 10]
    },
    'simulation': {
        'duration': 600  # 10-minute mission
    }
}
```

## Troubleshooting

### Common Issues

1. **Missing 3D Meshes**: 
   - Ensure `trimesh` is installed: `pip install trimesh`
   - System will fallback to wireframe rendering

2. **Model Not Found**:
   - Check spelling: Use `python tools/drone_model_utils.py list`
   - Verify the model exists in the drone library

3. **Poor Performance**:
   - Disable 3D mesh rendering: Set visualization to use wireframe
   - Reduce trajectory length in configuration

### Performance Tips

- **Mesh Caching**: Models are cached after first load
- **Level of Detail**: Complex meshes are simplified for real-time display
- **Selective Rendering**: Only current drone model is rendered

## Dependencies

Required packages for full 3D functionality:
- `trimesh>=3.9.0` - 3D mesh processing
- `matplotlib>=3.5.0` - 3D visualization
- `numpy>=1.21.0` - Mathematical operations

## Future Enhancements

Planned features:
- Import custom 3D models from CAD files
- Animated propellers and control surfaces
- Damage visualization and deformation
- Multi-drone formations with different models
- Real-time model switching in GUI