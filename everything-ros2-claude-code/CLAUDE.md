# CLAUDE.md — ROS 2 Project Configuration

This is a ROS 2 project. You are working with the Robot Operating System 2.

## Critical Rules — Never Violate These

1. **NEVER use ROS 1 APIs.** `rospy`, `roscpp`, `roslaunch` (XML), `rostopic`, `rospkg` are all ROS 1.
   - ROS 2 Python: `rclpy`
   - ROS 2 C++: `rclcpp`
   - ROS 2 launch: Python-based `.launch.py`

2. **Always declare parameters before getting them.**
   ```python
   # WRONG
   self.get_parameter('my_param')
   
   # CORRECT
   self.declare_parameter('my_param', 'default_value')
   self.get_parameter('my_param').get_parameter_value().string_value
   ```

3. **Never hardcode frame IDs.** Always accept them as parameters.

4. **Always validate URDF** with `check_urdf` before using in launch files.

5. **Check target distro before using any API.** APIs differ between Humble, Jazzy, and Rolling.

6. **Always specify QoS** for publishers and subscribers. Never rely on defaults for sensor data.

7. **Always add dependencies to package.xml.** If you import it, it must be in `<depend>`.

## Target ROS 2 Distro

<!-- Set this to your project's target distro -->
<!-- Options: humble | iron | jazzy | kilted | rolling -->
ROS_DISTRO: humble

## Package Type

<!-- ament_cmake | ament_python | ament_cmake_python -->
PACKAGE_TYPE: ament_cmake

## When in Doubt — Use These Agents

- URDF issues → `@urdf-validator`
- Topic/service naming → `@topic-schema-agent`
- Build failures → `@colcon-agent`
- Distro API question → `@distro-compat-agent`
- TF2 issues → `@tf2-agent`
- QoS errors → `@qos-agent`
- Navigation → `@nav2-agent`
- Motion planning → `@moveit2-agent`
- Lifecycle issues → `@lifecycle-agent`
