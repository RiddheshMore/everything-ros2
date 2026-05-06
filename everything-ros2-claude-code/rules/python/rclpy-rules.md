# ROS 2 Python Rules (rclpy)

## Node Structure

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyNode(Node):
    """
    Brief description of what this node does.

    Subscribed topics:
      ~/input (std_msgs/String) RELIABLE depth=10

    Published topics:
      ~/output (std_msgs/String) RELIABLE depth=10

    Parameters:
      max_speed (float64, default=1.0): Maximum speed in m/s
      frame_id (str, default='base_link'): Reference frame ID
    """

    def __init__(self):
        super().__init__('my_node')  # snake_case, no leading slash

        # 1. Declare parameters first
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('frame_id', 'base_link')

        # 2. Read parameters
        self.max_speed = self.get_parameter('max_speed') \
                             .get_parameter_value().double_value
        self.frame_id = self.get_parameter('frame_id') \
                            .get_parameter_value().string_value

        # 3. Create publishers
        self.pub = self.create_publisher(String, 'output', 10)

        # 4. Create subscribers
        self.sub = self.create_subscription(
            String, 'input', self._input_callback, 10)

        # 5. Create timers
        self.timer = self.create_timer(0.5, self._timer_callback)

        self.get_logger().info(f'MyNode started. frame_id={self.frame_id}')

    def _input_callback(self, msg: String) -> None:
        self.get_logger().info(f'Received: {msg.data}')

    def _timer_callback(self) -> None:
        msg = String()
        msg.data = 'Hello'
        self.pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Python Rules

### Always use `self.get_logger()` — never `print()`
```python
# WRONG
print(f"Speed: {speed}")

# CORRECT
self.get_logger().info(f'Speed: {speed:.2f}')
self.get_logger().warn('Something degraded')
self.get_logger().error('Something failed')
self.get_logger().debug('Verbose info')
```

### Always handle KeyboardInterrupt and destroy_node
```python
# WRONG — node not cleaned up on Ctrl+C
rclpy.spin(node)
rclpy.shutdown()

# CORRECT
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.shutdown()
```

### Use `self.get_clock().now()` for timestamps — never `time.time()`
```python
# WRONG
import time
stamp = time.time()

# CORRECT
stamp = self.get_clock().now().to_msg()  # → builtin_interfaces.msg.Time
```

### Always use type hints in ROS 2 callbacks
```python
# WRONG — no type info for readers
def scan_callback(self, msg):
    ...

# CORRECT
from sensor_msgs.msg import LaserScan
def scan_callback(self, msg: LaserScan) -> None:
    ...
```

### Never use `time.sleep()` in callbacks
```python
# WRONG — blocks the executor, starves other callbacks
def timer_callback(self):
    time.sleep(2.0)

# CORRECT — use another timer or async pattern
```

### Prefix private methods with underscore
```python
# Public interface
def get_status(self): ...

# Private/internal callbacks
def _timer_callback(self): ...
def _scan_callback(self, msg): ...
```

### Import style — always explicit, never wildcard
```python
# WRONG
from std_msgs.msg import *

# CORRECT
from std_msgs.msg import String, Float64
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist, PoseStamped
```

### Use f-strings in logger calls (not % formatting)
```python
# WRONG
self.get_logger().info('Speed: %f' % speed)

# CORRECT
self.get_logger().info(f'Speed: {speed:.2f} m/s')
```

### Parameter value access — always use `.get_parameter_value()`
```python
# WRONG — .value is not the typed value on all Python versions
val = self.get_parameter('speed').value

# CORRECT — explicit type
val = self.get_parameter('speed').get_parameter_value().double_value
val = self.get_parameter('name').get_parameter_value().string_value
val = self.get_parameter('flag').get_parameter_value().bool_value
val = self.get_parameter('count').get_parameter_value().integer_value
val = self.get_parameter('points').get_parameter_value().double_array_value
```

## Naming Conventions
- Node class names: `CamelCase` (matching filename in CamelCase)
- Callback methods: `_snake_case` (private, with underscore prefix)
- Files: `snake_case.py`
- Entry point in setup.py: `'my_node = my_pkg.my_node:main'`
