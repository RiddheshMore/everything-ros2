# ROS 1 to ROS 2 URDF Conversion Process

## Overview
Converting a robot model from ROS 1 to ROS 2 involves more than just updating the URDF file. While the core URDF structure remains largely the same, several key components need to be updated for ROS 2 compatibility.

## Key Components to Update

### 1. Controller Definitions
**ROS 1 Approach:**
- Uses `gazebo_ros_control` plugin in URDF
- Controllers defined in separate YAML files
- Loaded via `rosparam` and `node` tags in launch files

**ROS 2 Approach:**
- Uses `ros2_control` tag directly in URDF
- Hardware interface defined with plugin specifications
- Command and state interfaces explicitly declared

### 2. Gazebo Integration
**ROS 1:**
```xml
<gazebo>
  <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
    <legacyMode>false</legacyMode>
    <publishWheelTF>true</publishWheelTF>
    <publishOdomTF>true</publishOdomTF>
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

<gazebo>
  <plugin name="gz_ros2_control" filename="libgz_ros2_control-system.so">
    <parameters>/path/to/controllers.yaml</parameters>
  </plugin>
</gazebo>
```

### 3. Launch Files Migration
**ROS 1 (.launch):**
```xml
<launch>
  <param name="robot_description" textfile="$(find package)/urdf/robot.urdf" />
  <node name="joint_state_publisher" pkg="joint_state_publisher" type="joint_state_publisher" />
  <node name="robot_state_publisher" pkg="robot_state_publisher" type="robot_state_publisher" />
</launch>
```

**ROS 2 (.launch.py):**
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file]
        ),
        # Additional nodes...
    ])
```

## Step-by-Step Conversion Process

### Step 1: Analyze Existing URDF
- Identify joints that need control interfaces
- Note existing Gazebo plugins
- Document sensor definitions

### Step 2: Add ros2_control Tags
- Define hardware interface plugin
- Add command/state interfaces for each controllable joint
- Remove old Gazebo controller plugins

### Step 3: Update Gazebo Plugins
- Replace with ROS 2 compatible gz_ros2_control plugin
- Specify path to controller configuration file

### Step 4: Create Controller Configuration
Create a YAML file defining the controllers:
```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz
    
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
      
    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    publish_rate: 50.0
    pose_covariance_diagonal: [0.001, 0.001, 0.001, 0.001, 0.001, 0.03]
    twist_covariance_diagonal: [0.001, 0.001, 0.001, 0.001, 0.001, 0.03]
```

### Step 5: Update Package Dependencies
Modify `package.xml` to include ROS 2 dependencies:
```xml
<depend>rclcpp</depend>
<depend>rclpy</depend>
<depend>ros2_control</depend>
<depend>ros2_controllers</depend>
<depend>gz_ros2_control</depend>
```

## Common Conversion Issues

1. **Plugin Names**: Many Gazebo plugins have different names in ROS 2
2. **Parameter Names**: Some parameters have changed between versions
3. **Frame Conventions**: ROS 2 uses different naming conventions for some frames
4. **QoS Settings**: ROS 2 requires explicit QoS settings for reliable communication

## Validation
After conversion, validate your URDF:
```bash
# Check URDF syntax
check_urdf robot.urdf

# View in RViz2
ros2 launch urdf_tutorial display.launch.py model:=robot.urdf
```

## Example Files in This Repository
- `simple_robot_ros1.urdf`: Basic ROS 1 robot model
- `simple_robot_ros2.urdf`: Converted ROS 2 version with ros2_control
- `README.md`: This documentation file

The key takeaway is that while the structural aspects of URDF remain the same, the control and simulation integration layers have been completely redesigned for ROS 2.