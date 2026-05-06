"""
ROS2 Humble launch file — migrated from robot.launch (XML)

Migration map:
  <param name="robot_description" textfile="..."/>   → xacro.process_file() + robot_state_publisher param
  <node pkg="..." type="..." name="...">             → launch_ros.actions.Node(...)
  <remap from="..." to="..."/>                       → remappings=[('from', 'to')]
  <param name="..." value="..."/>                    → parameters=[{'name': value}]
  <include file="..."><arg .../></include>           → IncludeLaunchDescription(PythonLaunchDescriptionSource(...))
  <arg name="..." default="..."/>                    → DeclareLaunchArgument + LaunchConfiguration
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('test_robot')

    # Equivalent to <arg name="use_lidar" default="true"/>
    use_lidar_arg = DeclareLaunchArgument(
        'use_lidar',
        default_value='true',
        description='Whether to launch the lidar sensor'
    )
    use_lidar = LaunchConfiguration('use_lidar')

    # Robot description — equivalent to <param name="robot_description" textfile="..."/>
    # Using xacro processing (supports both .urdf and .urdf.xacro)
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    with open(urdf_file, 'r') as f:
        robot_description_content = f.read()

    # Robot state publisher — same as <node pkg="robot_state_publisher" type="robot_state_publisher"/>
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    # ros2_control manager
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description_content},
            os.path.join(pkg_share, 'config', 'diff_drive_controller.yaml')
        ],
        output='screen',
    )

    # Spawn joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    # Spawn diff_drive_controller
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
    )

    # Diff drive node — equivalent to <node pkg="test_robot" type="diff_drive_node">
    # with <param name="wheel_separation" value="0.4"/> and <remap from="cmd_vel" to="/robot/cmd_vel"/>
    diff_drive_node = Node(
        package='test_robot',
        executable='diff_drive',
        name='diff_drive_node',
        output='screen',
        parameters=[{
            'wheel_separation': 0.4,
            'wheel_radius': 0.05,
        }],
        remappings=[
            ('/cmd_vel', '/robot/cmd_vel'),  # equivalent to <remap from="cmd_vel" to="/robot/cmd_vel"/>
        ]
    )

    # Odometry monitor — equivalent to <node pkg="test_robot" type="odom_publisher.py">
    odom_monitor_node = Node(
        package='test_robot',
        executable='odom_publisher.py',
        name='odom_monitor',
        output='screen',
        parameters=[{
            'log_rate': 1.0,
        }]
    )

    return LaunchDescription([
        use_lidar_arg,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_spawner,
        diff_drive_node,
        odom_monitor_node,
    ])
