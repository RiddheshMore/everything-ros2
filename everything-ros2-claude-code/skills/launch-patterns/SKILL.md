---
name: launch-patterns
description: ROS 2 launch file architecture and best practices
triggers:
  - launch file
  - .launch.py
  - LaunchDescription
  - Node()
  - IncludeLaunchDescription
---

# ROS 2 Launch File Patterns

## Minimal Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_pkg',
            executable='my_node',
            name='my_node',
            output='screen',
            parameters=[{
                'param_name': 'param_value',
            }],
        ),
    ])
```

## With YAML Parameters

```python
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('my_pkg'),
        'config', 'params.yaml'
    )

    return LaunchDescription([
        Node(
            package='my_pkg',
            executable='my_node',
            name='my_node',
            parameters=[config],
            output='screen',
        ),
    ])
```

## With Arguments and Substitutions

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        Node(
            package='my_pkg',
            executable='my_node',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
        ),
    ])
```

## Including Other Launch Files

```python
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        FindPackageShare('other_pkg'), '/launch/other.launch.py'
    ]),
    launch_arguments={
        'use_sim_time': 'true',
    }.items(),
)
```

## Lifecycle Node with Manager

```python
from launch_ros.actions import LifecycleNode
from launch.actions import EmitEvent, RegisterEventHandler
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition

LifecycleNode(
    package='my_pkg',
    executable='my_lifecycle_node',
    name='my_lifecycle_node',
    namespace='',
    output='screen',
)
```

## Namespace and Remapping

```python
Node(
    package='my_pkg',
    executable='my_node',
    namespace='robot1',           # all topics become /robot1/...
    remappings=[
        ('cmd_vel', '/cmd_vel'),  # remap input to absolute topic
        ('odom', 'wheel_odom'),   # remap output to different name
    ],
)
```

## Common Mistakes

```python
# WRONG — LaunchDescription takes a list
return LaunchDescription(
    Node(...)  # ← not a list!
)

# CORRECT
return LaunchDescription([
    Node(...),
])

# WRONG — hardcoded path
parameters=['/home/user/ws/src/my_pkg/config/params.yaml']

# CORRECT — portable path
from ament_python.packages import get_package_share_directory
config = os.path.join(get_package_share_directory('my_pkg'), 'config', 'params.yaml')
parameters=[config]
```
