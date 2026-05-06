---
name: tf2-patterns
description: TF2 broadcast, lookup, and MessageFilter copy-paste patterns
triggers:
  - tf2
  - transform
  - frame
  - lookup_transform
  - broadcaster
  - quaternion
---

# TF2 Patterns

## Quaternion from Euler (always use library)

```python
from tf_transformations import quaternion_from_euler

q = quaternion_from_euler(roll=0.0, pitch=0.0, yaw=1.5707)
# Returns [x, y, z, w]

t.transform.rotation.x = q[0]
t.transform.rotation.y = q[1]
t.transform.rotation.z = q[2]
t.transform.rotation.w = q[3]
```

```cpp
#include <tf2/LinearMath/Quaternion.h>
tf2::Quaternion q;
q.setRPY(0, 0, M_PI_2);
auto q_msg = tf2::toMsg(q);
```

## Dynamic Broadcaster

```python
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

self.tf_broadcaster = TransformBroadcaster(self)

t = TransformStamped()
t.header.stamp = self.get_clock().now().to_msg()
t.header.frame_id = 'odom'
t.child_frame_id = 'base_link'
t.transform.translation.x = x
t.transform.translation.y = y
t.transform.translation.z = 0.0
t.transform.rotation.w = 1.0  # identity

self.tf_broadcaster.sendTransform(t)
```

## Static Broadcaster (in launch file — preferred)

```python
Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    arguments=['0.1', '0', '0.2', '0', '0', '0', 'base_link', 'laser_link'],
)
```

## Safe Lookup

```python
import tf2_ros
from rclpy.duration import Duration

self.tf_buffer = tf2_ros.Buffer()
self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

try:
    t = self.tf_buffer.lookup_transform(
        'map', 'base_link',
        rclpy.time.Time(),
        timeout=Duration(seconds=1.0)  # ALWAYS set timeout
    )
except (tf2_ros.LookupException,
        tf2_ros.ConnectivityException,
        tf2_ros.ExtrapolationException) as e:
    self.get_logger().warn(f'TF error: {e}')
    return
```

## REP-105 Frame Chain

```
map → odom → base_link → [sensor frames]
```

- `map`: globally consistent, can jump (SLAM resets)
- `odom`: locally consistent, never jumps
- `base_link`: robot body center
- `laser_link`, `camera_link`: sensor mounts

## Debug

```bash
ros2 run tf2_tools view_frames          # generates frames.pdf
ros2 run tf2_ros tf2_echo map base_link # live transform
```
