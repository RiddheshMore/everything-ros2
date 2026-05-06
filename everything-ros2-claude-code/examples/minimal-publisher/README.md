# Minimal Publisher / Subscriber Example

A complete, working ROS 2 Python package demonstrating:
- Correct node structure with parameters
- Proper QoS for publisher and subscriber
- Correct package.xml and setup.py

## File Structure

```
minimal_pubsub/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/minimal_pubsub       ← empty marker file
├── minimal_pubsub/
│   ├── __init__.py
│   ├── talker.py
│   └── listener.py
├── launch/
│   └── demo.launch.py
└── config/
    └── params.yaml
```

## package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
  schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <n>minimal_pubsub</n>
  <version>0.0.1</version>
  <description>Minimal ROS 2 publisher/subscriber example</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## setup.py

```python
from setuptools import setup
import os
from glob import glob

package_name = 'minimal_pubsub'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            glob('launch/*.launch.py')),
        ('share/' + package_name + '/config',
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Minimal ROS 2 publisher/subscriber example',
    license='MIT',
    entry_points={
        'console_scripts': [
            'talker   = minimal_pubsub.talker:main',
            'listener = minimal_pubsub.listener:main',
        ],
    },
)
```

## setup.cfg

```ini
[develop]
script_dir=$base/lib/minimal_pubsub

[install]
install_scripts=$base/lib/minimal_pubsub
```

## minimal_pubsub/talker.py

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """
    Publishes a string message on a timer.

    Published topics:
      ~/chatter (std_msgs/String) RELIABLE depth=10

    Parameters:
      publish_rate (float64, default=1.0): Publishing frequency in Hz
      message    (str,     default='Hello, ROS 2!'): Message to publish
    """

    def __init__(self):
        super().__init__('talker')

        # Declare parameters before getting them
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('message', 'Hello, ROS 2!')

        rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self._message = self.get_parameter('message').get_parameter_value().string_value

        # Use relative topic name for namespace compatibility
        self._pub = self.create_publisher(String, 'chatter', 10)
        self._timer = self.create_timer(1.0 / rate, self._timer_callback)
        self._count = 0

        self.get_logger().info(f'Talker started at {rate} Hz')

    def _timer_callback(self) -> None:
        msg = String()
        msg.data = f'{self._message} (count: {self._count})'
        self._pub.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self._count += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## minimal_pubsub/listener.py

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """
    Subscribes to string messages and logs them.

    Subscribed topics:
      ~/chatter (std_msgs/String) RELIABLE depth=10

    Parameters:
      log_level (str, default='info'): Logging level (debug/info/warn/error)
    """

    def __init__(self):
        super().__init__('listener')
        self.declare_parameter('log_level', 'info')

        self._sub = self.create_subscription(
            String, 'chatter', self._chatter_callback, 10)

        self.get_logger().info('Listener ready')

    def _chatter_callback(self, msg: String) -> None:
        self.get_logger().info(f'Heard: "{msg.data}"')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## launch/demo.launch.py

```python
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('minimal_pubsub'),
        'config', 'params.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation clock'
        ),

        Node(
            package='minimal_pubsub',
            executable='talker',
            name='talker',
            parameters=[config, {'use_sim_time': use_sim_time}],
            output='screen',
        ),
        Node(
            package='minimal_pubsub',
            executable='listener',
            name='listener',
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])
```

## config/params.yaml

```yaml
talker:
  ros__parameters:
    publish_rate: 2.0
    message: "Hello from ROS 2!"

listener:
  ros__parameters:
    log_level: "info"
```

## Build and Run

```bash
# From workspace root
cd ~/ros2_ws
colcon build --packages-select minimal_pubsub --symlink-install
source install/setup.bash

# Run separately
ros2 run minimal_pubsub talker
ros2 run minimal_pubsub listener

# Or with launch
ros2 launch minimal_pubsub demo.launch.py

# With namespace
ros2 launch minimal_pubsub demo.launch.py use_sim_time:=false
```
