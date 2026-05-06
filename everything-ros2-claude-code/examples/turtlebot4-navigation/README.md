# Nav2 + SLAM Example

Complete Navigation2 bringup with SLAM for a differential drive robot.
Demonstrates correct Nav2 lifecycle management, parameter structure, and
`nav2_simple_commander` Python API for autonomous navigation.

## File Structure

```
turtlebot4_navigation/
├── package.xml
├── CMakeLists.txt
├── config/
│   ├── nav2_params.yaml         ← Full Nav2 parameter file
│   └── slam_params.yaml         ← SLAM Toolbox parameters
├── launch/
│   ├── navigation.launch.py     ← Nav2 stack bringup
│   ├── slam.launch.py           ← Online SLAM
│   └── localization.launch.py   ← AMCL with saved map
├── maps/
│   └── .gitkeep                 ← Save maps here
└── scripts/
    └── navigate_to_goal.py      ← nav2_simple_commander demo
```

## package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
  schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <n>turtlebot4_navigation</n>
  <version>0.0.1</version>
  <description>Nav2 + SLAM bringup for differential drive robot</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <exec_depend>nav2_bringup</exec_depend>
  <exec_depend>nav2_lifecycle_manager</exec_depend>
  <exec_depend>nav2_map_server</exec_depend>
  <exec_depend>nav2_amcl</exec_depend>
  <exec_depend>nav2_planner</exec_depend>
  <exec_depend>nav2_controller</exec_depend>
  <exec_depend>nav2_bt_navigator</exec_depend>
  <exec_depend>nav2_waypoint_follower</exec_depend>
  <exec_depend>nav2_recoveries</exec_depend>
  <exec_depend>slam_toolbox</exec_depend>
  <exec_depend>nav2_simple_commander</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(turtlebot4_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config maps scripts
  DESTINATION share/${PROJECT_NAME}/)

install(PROGRAMS scripts/navigate_to_goal.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
```

## launch/slam.launch.py

```python
"""Online SLAM with slam_toolbox — builds map while navigating."""
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params  = LaunchConfiguration('slam_params_file')

    pkg_share = get_package_share_directory('turtlebot4_navigation')
    default_slam_params = os.path.join(pkg_share, 'config', 'slam_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('slam_params_file',
                              default_value=default_slam_params),

        # SLAM Toolbox — async mode (better for real robots)
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params, {'use_sim_time': use_sim_time}],
        ),
    ])
```

## launch/navigation.launch.py

```python
"""Full Nav2 stack — requires an active map (from SLAM or map_server)."""
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share    = get_package_share_directory('turtlebot4_navigation')
    nav2_params  = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')

    lifecycle_nodes = [
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'waypoint_follower',
    ]

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),

        Node(package='nav2_controller',
             executable='controller_server', name='controller_server',
             output='screen',
             parameters=[nav2_params, {'use_sim_time': use_sim_time}]),

        Node(package='nav2_planner',
             executable='planner_server', name='planner_server',
             output='screen',
             parameters=[nav2_params, {'use_sim_time': use_sim_time}]),

        Node(package='nav2_behaviors',
             executable='behavior_server', name='behavior_server',
             output='screen',
             parameters=[nav2_params, {'use_sim_time': use_sim_time}]),

        Node(package='nav2_bt_navigator',
             executable='bt_navigator', name='bt_navigator',
             output='screen',
             parameters=[nav2_params, {'use_sim_time': use_sim_time}]),

        Node(package='nav2_waypoint_follower',
             executable='waypoint_follower', name='waypoint_follower',
             output='screen',
             parameters=[nav2_params, {'use_sim_time': use_sim_time}]),

        # Lifecycle manager — configures and activates all Nav2 nodes
        Node(package='nav2_lifecycle_manager',
             executable='lifecycle_manager',
             name='lifecycle_manager_navigation',
             output='screen',
             parameters=[{
                 'use_sim_time': use_sim_time,
                 'autostart': True,
                 'node_names': lifecycle_nodes,
             }]),
    ])
```

## config/slam_params.yaml

```yaml
slam_toolbox:
  ros__parameters:
    # Plugin params
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None

    # ROS params
    odom_frame: odom
    map_frame: map
    base_frame: base_footprint      # ← use base_footprint for ground robots
    scan_topic: /scan
    use_map_saver: true
    mode: mapping                   # mapping | localization

    # If you have a bad odometry source, increase this
    tf_buffer_duration: 30.0

    # Map params
    map_file_name: ""
    map_start_pose: [0.0, 0.0, 0.0]
    map_update_interval: 5.0
    resolution: 0.05
    max_laser_range: 20.0
    minimum_travel_distance: 0.5
    minimum_travel_heading: 0.5

    # Loop closure
    do_loop_closing: true
    loop_search_space_dimension: 8.0
    loop_search_maximum_distance: 3.0
    loop_match_minimum_response_fine: 0.45
```

## scripts/navigate_to_goal.py

```python
#!/usr/bin/env python3
"""
Demonstrates nav2_simple_commander for autonomous point-to-point navigation.
Usage: ros2 run turtlebot4_navigation navigate_to_goal.py
"""
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import tf_transformations
import sys


def make_pose(navigator: BasicNavigator, x: float, y: float,
              yaw_deg: float) -> PoseStamped:
    """Create a PoseStamped in the map frame."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y

    q = tf_transformations.quaternion_from_euler(0.0, 0.0,
                                                 yaw_deg * 3.14159 / 180.0)
    pose.pose.orientation.x = q[0]
    pose.pose.orientation.y = q[1]
    pose.pose.orientation.z = q[2]
    pose.pose.orientation.w = q[3]
    return pose


def main() -> None:
    rclpy.init()
    navigator = BasicNavigator()

    # Wait until Nav2 is fully active
    navigator.waitUntilNav2Active()

    # ── Single goal navigation ────────────────────────────────────────────
    goal = make_pose(navigator, x=2.0, y=1.5, yaw_deg=90.0)
    navigator.goToPose(goal)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            dist = feedback.distance_remaining
            navigator.get_logger().info(f'Distance remaining: {dist:.2f} m')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        navigator.get_logger().info('✅ Goal reached!')
    elif result == TaskResult.CANCELED:
        navigator.get_logger().warn('⚠️  Goal canceled.')
    elif result == TaskResult.FAILED:
        navigator.get_logger().error('❌ Goal failed.')
        sys.exit(1)

    # ── Waypoint following ────────────────────────────────────────────────
    waypoints = [
        make_pose(navigator, 0.0,  0.0,   0.0),
        make_pose(navigator, 2.0,  0.0,  90.0),
        make_pose(navigator, 2.0,  2.0, 180.0),
        make_pose(navigator, 0.0,  2.0, 270.0),
        make_pose(navigator, 0.0,  0.0,   0.0),  # back to start
    ]

    navigator.get_logger().info('Following square waypoint path...')
    navigator.followWaypoints(waypoints)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            idx = feedback.current_waypoint
            navigator.get_logger().info(f'At waypoint {idx + 1}/{len(waypoints)}')

    if navigator.getResult() == TaskResult.SUCCEEDED:
        navigator.get_logger().info('✅ Waypoint tour complete!')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Build and Run

```bash
colcon build --packages-select turtlebot4_navigation --symlink-install
source install/setup.bash

# Terminal 1: Start SLAM (builds map as robot drives)
ros2 launch turtlebot4_navigation slam.launch.py

# Terminal 2: Start Nav2 (requires active TF and /scan)
ros2 launch turtlebot4_navigation navigation.launch.py

# Terminal 3: Send a goal programmatically
ros2 run turtlebot4_navigation navigate_to_goal.py

# Save the map when done
ros2 run nav2_map_server map_saver_cli -f maps/my_map

# Visualize in RViz
ros2 launch nav2_bringup rviz_launch.py
```

## Common Issues

| Problem | Fix |
|---|---|
| `map → odom` transform missing | Start SLAM or localization before Nav2 |
| Costmap not updating | Check `/scan` QoS — must be BEST_EFFORT |
| Robot not moving | Check `/cmd_vel` subscriber exists on your robot driver |
| AMCL not localizing | Set initial pose in RViz with "2D Pose Estimate" |
| Nav2 nodes not activating | Check lifecycle_manager node_names list matches node names exactly |
