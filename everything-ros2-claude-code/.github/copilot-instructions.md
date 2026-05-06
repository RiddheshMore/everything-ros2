# ROS 2 Copilot Instructions

This is a ROS 2 robotics project. Follow these rules in ALL code suggestions.

## Critical Rules — Never Violate

1. **NEVER use ROS 1 APIs.** No `rospy`, `roscpp`, `roslaunch` XML, `rostopic`, `rospkg`.
   - Python → `rclpy`; C++ → `rclcpp`; Launch → `.launch.py` (Python)

2. **Always declare parameters before getting them.**
   ```python
   self.declare_parameter('my_param', 'default_value')
   self.get_parameter('my_param').get_parameter_value().string_value
   ```

3. **Never hardcode frame IDs** — accept as parameters (`map_frame`, `base_frame`).

4. **Always specify QoS** — use `SensorDataQoS()` for sensor data, explicit profiles for everything else.

5. **Always add dependencies to `package.xml`.** Every import must have a `<depend>` entry.

6. **Use relative topic names** for namespace compatibility.

7. **Never block in callbacks** — no `time.sleep()`, no blocking I/O.

8. **Always support `use_sim_time`** for simulation compatibility.

## Python (rclpy) Conventions

- Use `self.get_logger()` — never `print()`
- Handle `KeyboardInterrupt` and call `destroy_node()` in `finally`
- Use `self.get_clock().now()` — never `time.time()`
- Type hints on all callbacks: `def cb(self, msg: LaserScan) -> None`
- Use `.get_parameter_value().double_value` (not `.value`)
- Prefix private methods: `_callback_name`
- No wildcard imports

## C++ (rclcpp) Conventions

- Use `RCLCPP_INFO/WARN/ERROR` — never `printf` or `std::cout`
- Use `SharedPtr` for message callbacks, `UniquePtr` for composable nodes
- Use `as_double()`, `as_string()` — not `.value()`
- Use `rclcpp::Time` — never `std::chrono` for ROS timestamps
- `#pragma once` for include guards
- C++17 minimum
- Member variables: `trailing_underscore_`

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Node names | `snake_case` | `lidar_processor` |
| Topic names | `snake_case`, relative | `scan_filtered` |
| Package names | `snake_case` | `my_robot_driver` |
| Message types | `CamelCase` | `RobotState.msg` |
| Service types | `CamelCase` | `SetMode.srv` |
| Python classes | `CamelCase` | `LidarProcessor` |
| C++ classes | `CamelCase` | `LidarProcessor` |
| C++ members | `trailing_underscore_` | `pub_`, `timer_` |

## Specialist Agent Reference

This project includes 27 specialist sub-agents for ROS 2 domains. See `AGENTS.md` for the full routing table:

- **URDF/XACRO** → `@urdf-validator`
- **Topic naming** → `@topic-schema-agent`
- **TF2 transforms** → `@tf2-agent`
- **Navigation** → `@nav2-agent`
- **Motion planning** → `@moveit2-agent`
- **QoS policies** → `@qos-agent`
- **Build errors** → `@colcon-agent`
- **Lifecycle nodes** → `@lifecycle-agent`
- **ros2_control** → `@ros2-control-agent`
- **ROS 1 migration** → `@ros1-migrator`
- **DDS tuning** → `@dds-tuner`
- **Security** → `@sros2-secops`

## Distro API Quick Reference

| Feature | Humble | Iron | Jazzy | Kilted/Rolling |
|---|---|---|---|---|
| `moveit_configs_utils` | ❌ | ✅ | ✅ | ✅ |
| Service introspection | ❌ | ✅ | ✅ | ✅ |
| New executor API | ❌ | ❌ | ✅ | ✅ |
| Zenoh RMW | ❌ | ❌ | ✅ | ✅ |
