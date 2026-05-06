# ROS 2 Development Rules — Windsurf / Cascade

This is a ROS 2 robotics project with 27 specialist sub-agents. Follow these rules for all code generation and review.

## Critical Rules — Never Violate

1. **NEVER use ROS 1 APIs.** No `rospy`, `roscpp`, `roslaunch` XML, `rostopic`, `rospkg`.
   - Python → `rclpy`; C++ → `rclcpp`; Launch → `.launch.py` (Python)

2. **Always declare parameters before getting them.**
   ```python
   self.declare_parameter('my_param', 'default_value')
   self.get_parameter('my_param').get_parameter_value().string_value
   ```

3. **Never hardcode frame IDs** — always accept as parameters.

4. **Always specify QoS** — use `SensorDataQoS()` for sensor data.

5. **Always add dependencies to `package.xml`.** Every import → `<depend>`.

6. **Use relative topic names** for namespace compatibility.

7. **Never block in callbacks** — no `time.sleep()`, no blocking I/O.

8. **Always support `use_sim_time`** for simulation compatibility.

## Python (rclpy) Rules

- Use `self.get_logger()` — never `print()`
- Handle `KeyboardInterrupt` + `destroy_node()` in `finally`
- Use `self.get_clock().now()` — never `time.time()`
- Type hints on all callbacks
- Use `.get_parameter_value().double_value` (not `.value`)
- Prefix private methods: `_callback_name`
- No wildcard imports

## C++ (rclcpp) Rules

- Use `RCLCPP_INFO/WARN/ERROR` — never `printf` or `std::cout`
- Use `SharedPtr` for message callbacks
- Use `as_double()`, `as_string()` — not `.value()`
- Use `rclcpp::Time` for ROS timestamps
- `#pragma once`; C++17 minimum
- Member variables: `trailing_underscore_`

## Naming Conventions

- Node names: `snake_case` (no leading slash)
- Topic names: `snake_case`, relative
- Package names: `snake_case` (no hyphens)
- Message/Service/Action types: `CamelCase`
- Python/C++ classes: `CamelCase`

## Code Review Checklist

- [ ] No ROS 1 APIs
- [ ] Parameters declared before use
- [ ] QoS appropriate for each message type
- [ ] package.xml has all dependencies
- [ ] Relative topic names used
- [ ] No blocking calls in callbacks
- [ ] Lifecycle nodes use LifecyclePublisher

## Agent Reference

See `AGENTS.md` for the full list of 27 specialist sub-agents for URDF, TF2, Nav2, MoveIt2, QoS, lifecycle, ros2_control, DDS, security, testing, and more.
