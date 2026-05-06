# ROS 1 to ROS 2 Conversion Examples

This directory contains examples showing the differences between ROS 1 and ROS 2 URDF files, which can be used for testing conversion agents.

## Files

### Simple Robot Examples
- `simple_robot_ros1.urdf` - Basic ROS 1 URDF without XACRO
- `simple_robot_ros2.urdf` - ROS 2 equivalent with ros2_control
- `simple_robot_ros1.xacro` - ROS 1 XACRO version with macros
- `simple_robot_ros2.xacro` - ROS 2 XACRO version with ros2_control

### Kobuki Examples (from downloaded repositories)
- `../ros1_kobuki_simplified.urdf` - Simplified ROS 1 Kobuki
- `../ros2_kobuki_converted.urdf` - ROS 2 converted version

### Documentation
- `README.md` - Basic conversion guide
- `conversion_guide.md` - Detailed step-by-step conversion process

## Key Conversion Points

1. **Controller Interface**: Replace gazebo_ros_control with ros2_control
2. **Gazebo Plugins**: Update to gz_ros2_control plugins
3. **Launch Files**: Convert from XML to Python-based .launch.py files
4. **Dependencies**: Update package.xml for ROS 2 packages
5. **Parameters**: Use ROS 2 parameter handling

## Using for Agent Testing

These files can be used to test conversion agents by:
1. Providing the ROS 1 version as input
2. Expecting the agent to produce the ROS 2 equivalent
3. Comparing the output with our reference ROS 2 versions
4. Evaluating the completeness and accuracy of the conversion

The examples range from simple to complex, allowing for progressive testing of conversion capabilities.