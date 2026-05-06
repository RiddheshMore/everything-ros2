# Multi-Robot Fleet Example

Demonstrates correct namespace isolation for multi-robot ROS 2 systems.

## The Pattern

Each robot gets its own namespace. All topics, services, and actions live
under `/<robot_name>/...`. The launch file is parameterized by robot name.

## Launch File

```python
# multi_robot_bringup.launch.py
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot1_group = GroupAction([
        PushRosNamespace('robot1'),
        Node(package='my_pkg', executable='base_controller',
             parameters=[{'use_sim_time': use_sim_time}]),
        Node(package='my_pkg', executable='lidar_driver',
             parameters=[{'use_sim_time': use_sim_time,
                          'frame_id': 'robot1/laser_link'}]),
    ])

    robot2_group = GroupAction([
        PushRosNamespace('robot2'),
        Node(package='my_pkg', executable='base_controller',
             parameters=[{'use_sim_time': use_sim_time}]),
        Node(package='my_pkg', executable='lidar_driver',
             parameters=[{'use_sim_time': use_sim_time,
                          'frame_id': 'robot2/laser_link'}]),
    ])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        robot1_group,
        robot2_group,
    ])
```

## Resulting Topic Tree

```
/robot1/cmd_vel          (geometry_msgs/Twist)
/robot1/odom             (nav_msgs/Odometry)
/robot1/scan             (sensor_msgs/LaserScan)
/robot1/map              (nav_msgs/OccupancyGrid)

/robot2/cmd_vel          (geometry_msgs/Twist)
/robot2/odom             (nav_msgs/Odometry)
/robot2/scan             (sensor_msgs/LaserScan)
/robot2/map              (nav_msgs/OccupancyGrid)
```

## TF Tree for Multi-Robot

```
map
├── robot1/odom
│   └── robot1/base_link
│       ├── robot1/laser_link
│       └── robot1/imu_link
└── robot2/odom
    └── robot2/base_link
        ├── robot2/laser_link
        └── robot2/imu_link
```

## Frame ID Parameterization in Node Code

```python
class BaseController(Node):
    def __init__(self):
        super().__init__('base_controller')

        # Frame IDs must be parameterized — never hardcoded
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('odom_frame', 'odom')

        self.base_frame = self.get_parameter('base_frame') \
                              .get_parameter_value().string_value
        self.odom_frame = self.get_parameter('odom_frame') \
                              .get_parameter_value().string_value

        # Use relative topic names — namespace is applied by launch
        self.cmd_sub = self.create_subscription(
            Twist, 'cmd_vel', self._cmd_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
```

## Fleet Coordinator Node

```python
class FleetCoordinator(Node):
    """Monitors all robots and assigns tasks."""

    def __init__(self):
        super().__init__('fleet_coordinator')
        self.declare_parameter('robot_names', ['robot1', 'robot2'])

        robot_names = self.get_parameter('robot_names') \
                          .get_parameter_value().string_array_value

        self._odom_subs = {}
        self._cmd_pubs = {}

        for name in robot_names:
            # Subscribe to each robot's odom
            self._odom_subs[name] = self.create_subscription(
                Odometry,
                f'/{name}/odom',
                lambda msg, n=name: self._odom_callback(msg, n),
                10
            )
            # Publisher for each robot's cmd_vel
            self._cmd_pubs[name] = self.create_publisher(
                Twist, f'/{name}/cmd_vel', 10)

    def _odom_callback(self, msg: Odometry, robot_name: str) -> None:
        self.get_logger().debug(
            f'{robot_name} at ({msg.pose.pose.position.x:.2f}, '
            f'{msg.pose.pose.position.y:.2f})'
        )
```

## Running

```bash
# Launch all robots
ros2 launch my_bringup multi_robot_bringup.launch.py

# Send command to specific robot
ros2 topic pub /robot1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.5}, angular: {z: 0.0}}' --once

# Check robot1 topics
ros2 topic list | grep robot1

# Check robot2 scan
ros2 topic echo /robot2/scan --once
```
