# ROS 2 Project — Gemini Code Assist Context

This is a ROS 2 robotics project with 27 specialist sub-agents for AI-assisted development.

## Project Overview

A comprehensive sub-agentic harness that gives AI coding assistants deep domain knowledge in ROS 2 development. Includes specialist agents for URDF validation, topic naming, distro compatibility, TF2, Nav2, MoveIt2, QoS, lifecycle nodes, ros2_control, DDS tuning, security, testing, and more.

## Critical Rules — Never Violate

1. **NEVER use ROS 1 APIs.** No `rospy`, `roscpp`, `roslaunch` XML, `rostopic`, `rospkg`.
   - Python → `rclpy`; C++ → `rclcpp`; Launch → `.launch.py` (Python)

2. **Always declare parameters before getting them.**
   ```python
   self.declare_parameter('my_param', 'default_value')
   self.get_parameter('my_param').get_parameter_value().string_value
   ```

3. **Never hardcode frame IDs** — always accept as parameters.

4. **Always specify QoS** — use `SensorDataQoS()` for sensor data, explicit profiles for everything else.

5. **Always add dependencies to `package.xml`.** Every import → `<depend>`.

6. **Use relative topic names** for namespace compatibility.

7. **Never block in callbacks** — no `time.sleep()`, no blocking I/O.

8. **Always support `use_sim_time`** for simulation compatibility.

## Tech Stack

- **Framework**: ROS 2 (Humble / Iron / Jazzy / Kilted / Rolling)
- **Languages**: Python 3 (rclpy), C++17 (rclcpp)
- **Build System**: colcon + ament_cmake / ament_python
- **Packages**: package.xml Format 3
- **Launch**: Python-based `.launch.py` files

## Naming Conventions

- Node names: `snake_case` (no leading slash)
- Topic names: `snake_case`, relative
- Package names: `snake_case` (no hyphens)
- Message/Service/Action types: `CamelCase`

## Python (rclpy) Rules

- Use `self.get_logger()` — never `print()`
- Handle `KeyboardInterrupt` + `destroy_node()` in `finally`
- Use `self.get_clock().now()` for timestamps
- Type hints on all callbacks
- Use `.get_parameter_value().double_value` (not `.value`)

## C++ (rclcpp) Rules

- Use `RCLCPP_INFO/WARN/ERROR` — never `printf`/`std::cout`
- Use `SharedPtr` for message callbacks
- Use `as_double()`, `as_string()` for parameter access
- Use `rclcpp::Time` for ROS timestamps
- `#pragma once`; C++17 minimum

## Distro API Reference

| Feature | Humble | Iron | Jazzy | Kilted/Rolling |
|---|---|---|---|---|
| `moveit_configs_utils` | ❌ | ✅ | ✅ | ✅ |
| Service introspection | ❌ | ✅ | ✅ | ✅ |
| New executor API | ❌ | ❌ | ✅ | ✅ |
| Zenoh RMW | ❌ | ❌ | ✅ | ✅ |

## Agent Reference

See `AGENTS.md` for the full routing table of 27 specialist sub-agents.
