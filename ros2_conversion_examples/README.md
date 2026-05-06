# ROS 1 to ROS 2 URDF Conversion Guide

This guide explains the key differences between ROS 1 and ROS 2 URDF files and how to convert from one to the other.

## Key Differences

### 1. ros2_control Integration
ROS 2 uses the `ros2_control` tag to define hardware interfaces instead of the ROS 1 controller_manager approach:

**ROS 1:**
```xml
<gazebo>
  <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
    <!-- Controller parameters -->
  </plugin>
</gazebo>
```

**ROS 2:**
```xml
<ros2_control name="robot_system" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="wheel_joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
</ros2_control>
```

### 2. Gazebo Plugin Updates
ROS 2 uses different plugins for Gazebo simulation:

**ROS 1:**
```xml
<gazebo>
  <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
    <!-- Parameters -->
  </plugin>
</gazebo>
```

**ROS 2:**
```xml
<gazebo>
  <plugin name="gz_ros2_control" filename="libgz_ros2_control-system.so">
    <parameters>/path/to/controllers.yaml</parameters>
  </plugin>
</gazebo>
```

### 3. Launch Files
ROS 2 uses Python-based launch files instead of XML:

**ROS 1 (.launch):**
```xml
<launch>
  <param name="robot_description" textfile="$(find package)/urdf/robot.urdf" />
</launch>
```

**ROS 2 (.launch.py):**
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('package_name')
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file]
        )
    ])
```

## Conversion Checklist

- [ ] Replace Gazebo plugins with ros2_control
- [ ] Update hardware interface definitions
- [ ] Convert launch files from XML to Python
- [ ] Update package.xml to include ROS 2 dependencies
- [ ] Add QoS settings for topics
- [ ] Parameterize frame IDs
- [ ] Validate URDF with `check_urdf`

## Example Files

- `simple_robot_ros1.urdf`: Original ROS 1 version
- `simple_robot_ros2.urdf`: Converted ROS 2 version

The main structural changes are in the addition of `<ros2_control>` tags and updated Gazebo plugins.