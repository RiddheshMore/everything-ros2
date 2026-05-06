---
name: ros2-control
description: ros2_control framework — controllers, hardware interfaces, joints, system_mode
triggers:
  - ros2_control
  - controller_manager
  - hardware_interface
  - diff_drive
  - joint_trajectory
  - ethercat
  - canopen
  - system_mode
---

# ros2_control Framework

## Quick-Reference Decision Table

| Use Case | Controller | Command Interface | State Interface |
|----------|-----------|-----------------|----------------|
| Differential drive | diff_drive_controller | velocity | position, velocity |
| 4-wheel Mecanum | mecanum_drive_controller | velocity | position, velocity |
| Robotic arm | joint_trajectory_controller | position/effort | position, velocity |
| Position only | position_controllers | position | position |
| Velocity only | velocity_controllers | velocity | velocity |

---

## Complete Copy-Paste Code

### 1. URDF ros2_control Block

```xml
<!-- In your robot.urdf.xacro -->
<ros2_control name="RobotHardware" type="system">
  <hardware>
    <!-- Simulated (for testing) -->
    <plugin>mock_components/GenericSystem</plugin>

    <!-- OR real hardware examples: -->
    <!-- <plugin> raspimouse/RaspimouseHardware </plugin> -->
    <!-- <plugin> canopen_bridge/CanopenHardware </plugin> -->
  </hardware>

  <!-- Differential drive wheels -->
  <joint name="wheel_left_joint">
    <command_interface name="velocity"/>
    <state_interface name="velocity"/>
    <state_interface name="position"/>
  </joint>

  <joint name="wheel_right_joint">
    <command_interface name="velocity"/>
    <state_interface name="velocity"/>
    <state_interface name="position"/>
  </joint>

  <!-- Sensor example -->
  <sensor name="imu_sensor">
    <state_interface name="orientation"/>
    <state_interface name="angular_velocity"/>
    <state_interface name="linear_acceleration"/>
    <plugin>imu_sensor_broadcaster/IMUSensorBroadcaster</plugin>
    <param name="frame_id">imu_link</param>
  </sensor>

  <!-- Force/torque sensor -->
  <sensor name="ft_sensor">
    <state_interface name="force.x"/>
    <state_interface name="force.y"/>
    <state_interface name="force.z"/>
    <state_interface name="torque.x"/>
    <state_interface name="torque.y"/>
    <state_interface name="torque.z"/>
    <plugin>force_torque_sensor_broadcaster/ForceTorqueSensorBroadcaster</plugin>
    <param name="frame_id">wrist_3_link</param>
    <param name="sensor_name">ft_sensor</param>
  </sensor>
</ros2_control>
```

### 2. diff_drive_controller Config

```yaml
# config/diff_drive.yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

diff_drive_controller:
  ros__parameters:
    left_wheel_names: [wheel_left_joint]
    right_wheel_names: [wheel_right_joint]

    wheel_separation: 0.4
    wheel_radius: 0.05

    # Publishing
    publish_rate: 50
    odom_frame_id: odom
    base_frame_id: base_link
    publish_cmd: true
    publish_odom: true

    # Velocity limits
    linear:
      x:
        max_velocity: 2.0
        min_velocity: -2.0
        max_acceleration: 5.0
    angular:
      z:
        max_velocity: 3.14
        min_velocity: -3.14
        max_acceleration: 5.0

    # Use TwistStamped (false) or Twist (true)
    use_stamped_vel: false
```

### 3. Joint Trajectory Controller Config

```yaml
# config/arm_controller.yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

arm_controller:
  ros__parameters:
    joints: [joint1, joint2, joint3, joint4, joint5, joint6]

    command_interfaces:
      - position

    state_interfaces:
      - position
      - velocity

    # Trajectory constraints
    constraints:
      stopped_velocity_tolerance: 0.05
      goal_time: 0.6
      joint1:
        tolerance: 0.001
      joint2:
        tolerance: 0.001
```

### 4. Hardware Interface (C++ Template)

```cpp
// robot_hardware.cpp
#include <hardware_interface/system_interface.hpp>
#include <rclcpp_lifecycle/state.hpp>
#include <rclcpp_lifecycle/transition.hpp>
#include <vector>

class RobotHardware : public hardware_interface::SystemInterface
{
public:
  CallbackReturn on_init(const hardware_interface::HardwareInfo & info) override
  {
    if (SystemInterface::on_init(info) != CallbackReturn::SUCCESS)
      return CallbackReturn::ERROR;

    // Get joint names from URDF
    for (const auto & joint : info_.joints)
    {
      joint_names_.push_back(joint.name);
      // Allocate state/command buffers
      hw_position_states_.push_back(0.0);
      hw_velocity_states_.push_back(0.0);
      hw_position_commands_.push_back(0.0);
    }

    return CallbackReturn::SUCCESS;
  }

  std::vector<StateInterface> export_state_interfaces() override
  {
    std::vector<StateInterface> state_interfaces;
    for (size_t i = 0; i < joint_names_.size(); ++i)
    {
      state_interfaces.emplace_back(joint_names_[i], "position", &hw_position_states_[i]);
      state_interfaces.emplace_back(joint_names_[i], "velocity", &hw_velocity_states_[i]);
    }
    return state_interfaces;
  }

  std::vector<CommandInterface> export_command_interfaces() override
  {
    std::vector<CommandInterface> command_interfaces;
    for (size_t i = 0; i < joint_names_.size(); ++i)
    {
      command_interfaces.emplace_back(joint_names_[i], "velocity", &hw_velocity_commands_[i]);
    }
    return command_interfaces;
  }

  CallbackReturn on_activate(const rclcpp_lifecycle::State &) override
  {
    // Start hardware communication
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State &) override
  {
    // Stop hardware communication, disable motors
    return CallbackReturn::SUCCESS;
  }

  return_type read(const rclcpp::Time &, const rclcpp::Duration &) override
  {
    // Read encoder values from motor controller
    return return_type::OK;
  }

  return_type write(const rclcpp::Time &, const rclcpp::Duration &) override
  {
    // Send velocity commands to motor controller
    return return_type::OK;
  }

private:
  std::vector<std::string> joint_names_;
  std::vector<double> hw_position_states_;
  std::vector<double> hw_velocity_states_;
  std::vector<double> hw_position_commands_;
  std::vector<double> hw_velocity_commands_;
};

// Register the plugin
#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(RobotHardware, hardware_interface::SystemInterface)
```

### 5. Launch Controllers

```python
# launch/control.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Robot description (generated by xacro)
    robot_desc = {'robot_description': open('/path/to/robot.urdf').read()}

    # Controller manager
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_desc],
        output='screen',
    )

    # Spawner for diff drive
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
    )

    # Spawner for joint state
    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    return LaunchDescription([
        controller_manager,
        joint_state_spawner,
        diff_drive_spawner,
    ])
```

### 6. System Mode Switching

```yaml
# config/robot_system_modes.yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    # Define system modes
    default_mode: active
    available_modes: [inactive, active, emergency_stop]

    # Controllers per mode
    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController
      default_modes:
        inactive: []
        active: [diff_drive_controller]
        emergency_stop: []
```

---

## CLI Debug Commands

```bash
# List available controllers
ros2 control list_controllers

# Load and start controller
ros2 run controller_manager spawner.py diff_drive_controller

# Switch controller mode
ros2 param set /controller_manager default_mode active

# View controller state
ros2 control list_hardware_components

# Check interfaces
ros2 topic echo /dynamic_join_states

# Reload controllers
ros2 run controller_manager ament_cpp_macro_templates
```

---

## Common Issues

### Controller won't load
```bash
# Check: missing dependency
ros2 pkg list | grep ros2_controllers
# Install:
sudo apt install ros-humble-ros2-controllers

# Check: joint name mismatch
# URDF joint names must match controller config
```

### Joints not moving
```bash
# Check: command interface missing
ros2 control list_hardware_components
# Verify: velocity command interface exists

# Check: controller active
ros2 control list_controllers
# Should show: diff_drive_controller: active

# Check: hardware read/write working
ros2 topic echo /dynamic_joint_states
# Should show position changing
```
