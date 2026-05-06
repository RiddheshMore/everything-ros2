# ROS 2 Control Diffbot

Full example of a differential drive robot using ros2_control with diff_drive_controller.

## Structure

```
ros2-control-diffbot/
├── README.md
├── urdf/
│   └── diffbot.urdf.xacro    # Robot description with ros2_control
├── config/
│   └── diff_drive.yaml       # Controller parameters
├── launch/
│   └── diffbot.launch.py     # Bringup launch file
├── src/
│   └── diffbot_hardware.cpp  # Custom hardware interface (optional)
└── test/
    └── test_diff_drive.cpp  # Hardware interface tests
```

## URDF ros2_control Block

```xml
<ros2_control name="diffbot_system">
  <hardware>
    <plugin>diff_drive_bot/DiffDriveBotHardware</plugin>
    <param name="left_wheel">left_wheel_joint</param>
    <param name="right_wheel">right_wheel_joint</param>
  </hardware>

  <joint name="left_wheel_joint">
    <param name="min_vel">-10.0</param>
    <param name="max_vel">10.0</param>
    <param name="max_acc">5.0</param>
  </joint>
  <joint name="right_wheel_joint">
    <param name="min_vel">-10.0</param>
    <param name="max_vel">10.0</param>
    <param name="max_acc">5.0</param>
  </joint>
</ros2_control>
```

## Hardware Interface (Minimal)

```cpp
// diffbot_hardware.cpp
#include <ros2_control_test_repo/diff_drive_bot.hpp>

using namespace ros2_control_test_repo;

class DiffDriveBotHardware : public hardware_interface::BaseInterface<hardware_interface::SystemInterface> {
public:
  CallbackReturn on_init(const hardware_interface::HardwareInfo & info) override;
  std::vector<StateInterface> export_state_interfaces() override;
  std::vector<CommandInterface> export_command_interfaces() override;
  CallbackReturn read(const rclcpp::Time & time, const rclcpp::Duration & period) override;
  CallbackReturn write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  double left_wheel_vel_cmd_ = 0.0;
  double right_wheel_vel_cmd_ = 0.0;
  double left_wheel_pos_ = 0.0;
  double right_wheel_pos_ = 0.0;
};
```

## diff_drive_controller Config

```yaml
controller_manager:
  ros__parameters:
    update_rate: 50

diff_drive_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
    wheel_separation: 0.28
    wheel_radius: 0.033

    # Control
    max_velocity: 1.0
    max_acceleration: 5.0

    # Kinematics
    linear.x.max_velocity: 0.5
    linear.x.max_acceleration: 2.0
    angular.z.max_velocity: 2.0
    angular.z.max_acceleration: 5.0

    # Publishing
    odom.publish_offset: 0.1
    odom.frame_id: odom
    base_frame_id: base_footprint
```

## Launch File

```python
# diffbot.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import LoadControllers

def generate_launch_description():
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': open('diffbot.urdf').read()}]
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[{'robot_description': open('diffbot.urdf').read()}]
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '-c', '/controller_manager']
    )

    joint_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager']
    )

    return LaunchDescription([
        robot_state_publisher,
        controller_manager,
        diff_drive_spawner,
        joint_broadcaster_spawner
    ])
```

## Build and Run

```bash
# Build
colcon build --packages-select diff_bot_description diff_bot_control diff_bot_hardware
source install/setup.bash

# Run
ros2 launch diff_bot_control diffbot.launch.py

# Verify
ros2 topic list
ros2 topic echo /diff_drive_controller/odom
ros2 run rqt_robot_steering rqt_robot_steering
```

## Test Commands

```bash
# Send velocity command
ros2 topic pub /diff_drive_controller/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}, angular: {z: 0.0}}' -1

# Check controller status
ros2 control list_controllers
ros2 control view diff_drive_controller

# List hardware interfaces
ros2 control list_hardware_interfaces
```

## Expected Behavior

1. Controller spawns and claims joints
2. `/diff_drive_controller/cmd_vel` accepts Twist messages
3. `/odom` publishes transform and odometry
4. `/joint_states` publishes wheel positions
5. Wheels follow velocity commands proportionally
