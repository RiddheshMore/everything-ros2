# ROS 2 Common Rules

These rules apply to ALL ROS 2 development regardless of language or package type.

## Core Principles

### 1. Never Use ROS 1 APIs
- ❌ `rospy`, `roscpp`, `roslaunch`, `rospkg`, `rosgraph`, `rostopic`, `rosnode`
- ✅ `rclpy`, `rclcpp`, `.launch.py`, `ament_index_python.packages`

### 2. Always Declare Parameters First
```python
# WRONG — will throw ParameterNotDeclaredException
val = self.get_parameter('speed').value

# CORRECT
self.declare_parameter('speed', 1.0)
val = self.get_parameter('speed').get_parameter_value().double_value
```

### 3. Never Hardcode Frame IDs
```python
# WRONG
tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())

# CORRECT — accept as parameters
self.declare_parameter('map_frame', 'map')
self.declare_parameter('base_frame', 'base_link')
```

### 4. Always Specify QoS Explicitly
```python
# WRONG for sensor data
self.create_subscription(LaserScan, '/scan', cb, 10)

# CORRECT
from rclpy.qos import qos_profile_sensor_data
self.create_subscription(LaserScan, '/scan', cb, qos_profile_sensor_data)
```

### 5. Use Relative Topic Names (for Namespace Compatibility)
```python
# WRONG — breaks namespace remapping
self.create_publisher(String, '/my_topic', 10)

# CORRECT — resolves to /<namespace>/my_topic
self.create_publisher(String, 'my_topic', 10)
```

### 6. Always Add Dependencies to package.xml
Every `#include`, `import`, `from X import Y` must have a corresponding `<depend>` in package.xml.

### 7. Check Target Distro for Every New API
Before using any API not in Humble, verify it exists in the project's target distro.
Check CLAUDE.md for `ROS_DISTRO`.

### 8. Use use_sim_time Parameter
All time-related code must support simulation:
```python
self.declare_parameter('use_sim_time', False)
# rclpy automatically handles this when the parameter is declared
```

### 9. Never Block in Callbacks
```python
# WRONG — blocks the executor, prevents other callbacks from running
def timer_callback(self):
    time.sleep(5)  # ← NEVER do this in a ROS callback

# CORRECT — use a separate thread or async approach
```

### 10. Use rclpy.shutdown() and Cleanup
```python
def main():
    rclpy.init()
    node = MyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Naming Conventions

- Node names: `snake_case`
- Topic names: `snake_case`, relative unless explicitly absolute
- Package names: `snake_case` with underscores (no hyphens)
- Message types: `CamelCase.msg`
- Service types: `CamelCase.srv`
- Action types: `CamelCase.action`
- C++ classes: `CamelCase`
- Python classes: `CamelCase`

## Code Organization

- One node per file (unless composable)
- Node class name = filename in CamelCase
- `main()` function at bottom
- Parameters declared in `__init__` or `on_configure` for lifecycle nodes
- Publishers/subscribers created in `__init__` or `on_activate` for lifecycle nodes

## Testing

- Use `launch_testing` for integration tests
- Use `unittest` + `rclpy` for unit tests of node logic
- Always test with `colcon test` not just `colcon build`

## Documentation

- Every node must have a docstring listing:
  - Subscribed topics + types + QoS
  - Published topics + types + QoS
  - Services offered
  - Actions offered
  - Parameters with defaults
  - TF frames broadcast/listened
