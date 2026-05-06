---
name: lifecycle-node
description: ROS 2 lifecycle node state machine copy-paste patterns
triggers:
  - lifecycle
  - managed node
  - on_configure
  - on_activate
  - LifecycleNode
  - LifecyclePublisher
---

# ROS 2 Lifecycle Node Patterns

## State Machine

```
[Unconfigured] → configure() → [Inactive] → activate() → [Active]
[Active] → deactivate() → [Inactive] → cleanup() → [Unconfigured]
[Any] → shutdown() → [Finalized]
```

## Callback Return Values

```python
TransitionCallbackReturn.SUCCESS   # transition completes
TransitionCallbackReturn.FAILURE   # transition fails, stays in current state
TransitionCallbackReturn.ERROR     # goes to ErrorProcessing state
```

## Python Minimal Template

```python
import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn, State
from std_msgs.msg import String


class MySensorNode(LifecycleNode):
    def __init__(self):
        super().__init__('my_sensor_node')
        self._pub = None
        self._timer = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Configuring...')
        # Create publishers (they start deactivated)
        self._pub = self.create_lifecycle_publisher(String, 'sensor_data', 10)
        # Create timer but cancel it — don't start yet
        self._timer = self.create_timer(0.1, self._publish)
        self._timer.cancel()
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Activating...')
        self._pub.on_activate()   # ← REQUIRED for LifecyclePublisher
        self._timer.reset()
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Deactivating...')
        self._pub.on_deactivate() # ← REQUIRED
        self._timer.cancel()
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Cleaning up...')
        self.destroy_publisher(self._pub)
        self.destroy_timer(self._timer)
        self._pub = None
        self._timer = None
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS

    def _publish(self):
        if not self._pub or not self._pub.is_activated():
            return
        msg = String()
        msg.data = 'sensor reading'
        self._pub.publish(msg)


def main():
    rclpy.init()
    node = MySensorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Lifecycle Manager in Launch

```python
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node

lifecycle_node = LifecycleNode(
    package='my_pkg', executable='my_sensor_node', name='my_sensor_node')

lifecycle_manager = Node(
    package='nav2_lifecycle_manager',
    executable='lifecycle_manager',
    parameters=[{
        'autostart': True,
        'node_names': ['my_sensor_node'],
    }],
)
```

## CLI Transitions

```bash
ros2 lifecycle list
ros2 lifecycle get /my_sensor_node
ros2 lifecycle set /my_sensor_node configure
ros2 lifecycle set /my_sensor_node activate
```
