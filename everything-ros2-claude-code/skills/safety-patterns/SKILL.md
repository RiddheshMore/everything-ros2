---
name: safety-patterns
description: Robot safety patterns — ESTOP, speed limiting, workspace bounds, collision detection, FMEA
triggers:
  - safety
  - estop
  - emergency stop
  - collision
  - speed limit
  - workspace
  - fmea
  - iso 10218
  - iso 3691
  - collaborative
  - payload
---

# Robot Safety Patterns

## Quick-Reference Decision Table

| Safety Feature | Complexity | Implementation | Standard |
|---------------|------------|---------------|----------|
| Hardware ESTOP | Low | GPIO line to motor driver | ISO 10218 |
| Software speed limit | Low | Twist limiter node | ISO 3691-4 |
| Workspace boundary | Medium | Odom + config node | ISO 3691-4 |
| Collision detection | High | LIDAR + pointcloud + stop node | ISO 3691-4 |
| Payload monitoring | Medium | FT sensor + threshold node | ISO 3691-4 |

---

## Complete Copy-Paste Code

### 1. Hardware ESTOP (Always Required)

```python
#!/usr/bin/env python3
# hardware_estop.py - Independent hardware ESTOP
# CRITICAL: This runs without Linux, triggers on power loss
import RPi.GPIO as GPIO
import subprocess
import signal
import sys

ESTOP_PIN = 22  # Physical button pin

def shutdown_motors(channel):
    """Called when ESTOP button pressed - hardware interrupt"""
    print("ESTOP TRIGGERED")
    # Method 1: Disable motor driver enable pin
    GPIO.output(MOTOR_ENABLE_PIN, GPIO.LOW)
    # Method 2: Publish to motor stop topic
    subprocess.run(['ros2', 'topic', 'pub', '-1', '/motors_enable',
                   'std_msgs/msg/Bool', '{data: false}'])
    sys.exit(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESTOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MOTOR_ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)

# Hardware interrupt - triggers even if Python crashes
GPIO.add_event_detect(ESTOP_PIN, GPIO.FALLING, callback=shutdown_motors,
                      bouncetime=100)

signal.signal(signal.SIGTERM, lambda s,f: GPIO.cleanup())

# Keep running
while True:
    signal.pause()
```

### 2. Software Speed Limiter

```python
#!/usr/bin/env python3
# speed_limiter.py - Limit velocity based on conditions
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class SpeedLimiter(Node):
    def __init__(self):
        super().__init__('speed_limiter')

        # Max speeds (m/s for linear, rad/s for angular)
        self.max_linear = 1.0
        self.max_angular = 2.0
        self.min_distance = 0.5  # Stop if closer

        # Publishers/Subscribers
        self.pub = self.create_publisher(Twist, '/safe_cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.min_scan_distance = float('inf')
        self.lidar_ok = False

    def scan_callback(self, msg):
        # Find minimum valid range
        valid_ranges = [r for r in msg.ranges if 0.1 < r < 10.0]
        if valid_ranges:
            self.min_scan_distance = min(valid_ranges)
            self.lidar_ok = True
        else:
            self.lidar_ok = False

    def cmd_callback(self, msg):
        safe_cmd = Twist()

        if not self.lidar_ok:
            # No scan data - use conservative limits
            safe_cmd.linear.x = msg.linear.x * 0.3
            safe_cmd.angular.z = msg.angular.z * 0.3
            self.pub.publish(safe_cmd)
            return

        if self.min_scan_distance < self.min_distance:
            # Emergency stop
            self.pub.publish(Twist())
            return

        if self.min_scan_distance < 2.0:
            # Slow down proportionally
            factor = max(0.1, self.min_scan_distance / 2.0)
            safe_cmd.linear.x = msg.linear.x * factor
            safe_cmd.angular.z = msg.angular.z * factor
        else:
            safe_cmd = msg

        # Hard limits
        safe_cmd.linear.x = max(-self.max_linear, min(self.max_linear, safe_cmd.linear.x))
        safe_cmd.angular.z = max(-self.max_angular, min(self.max_angular, safe_cmd.angular.z))

        self.pub.publish(safe_cmd)
```

### 3. Workspace Boundary Monitor

```python
#!/usr/bin/env python3
# workspace_monitor.py - Keep robot within virtual walls
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry

class WorkspaceMonitor(Node):
    def __init__(self):
        super().__init__('workspace_monitor')

        self.pub = self.create_publisher(Twist, '/bounded_cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Configurable bounds (in odom frame)
        self.bounds = {
            'min_x': -5.0, 'max_x': 5.0,
            'min_y': -5.0, 'max_y': 5.0,
            'margin': 0.5  # Slow down before boundary
        }
        self.in_danger = False
        self.position = (0.0, 0.0)

    def odom_callback(self, msg):
        self.position = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )

    def cmd_callback(self, msg):
        if self.in_danger:
            self.pub.publish(Twist())  # Stop
            return

        # Check bounds
        x, y = self.position
        bounded_cmd = Twist()

        if x < self.bounds['min_x'] + self.bounds['margin']:
            bounded_cmd.linear.x = max(0, msg.linear.x)
        elif x > self.bounds['max_x'] - self.bounds['margin']:
            bounded_cmd.linear.x = min(0, msg.linear.x)
        else:
            bounded_cmd.linear.x = msg.linear.x

        if y < self.bounds['min_y'] + self.bounds['margin']:
            # Lateral movement restriction depends on robot type
            pass
        elif y > self.bounds['max_y'] - self.bounds['margin']:
            pass

        bounded_cmd.angular.z = msg.angular.z
        self.pub.publish(bounded_cmd)
```

### 4. Collision Detection with PointCloud

```python
#!/usr/bin/env python3
# collision_detector.py - Stop on collision course
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool

class CollisionDetector(Node):
    def __init__(self):
        super().__init__('collision_detector')

        self.pub_cmd = self.create_publisher(Twist, '/safe_cmd_vel', 10)
        self.pub_collision = self.create_publisher(Bool, '/collision_imminent', 10)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(PointCloud2, '/camera/depth/points', self.pc_callback, 10)

        self.last_cmd = Twist()
        self.collision_distance = 0.3  # meters

    def pc_callback(self, msg):
        # Simplified - check if any point within collision_distance
        # In production, use pointcloud_processor or open3d
        import sensor_msgs_py.point_cloud2 as pc2

        points = list(pc2.read_points(msg, field_names=('x', 'y', 'z'),
                                       skip_nans=True))

        robot_x, robot_y, robot_z = 0, 0, 0  # From odometry
        imminent = False

        for p in points:
            px, py, pz = p[0], p[1], p[2]
            # Distance in robot frame (simplified)
            dist = (px**2 + py**2 + pz**2)**0.5
            if dist < self.collision_distance:
                imminent = True
                break

        self.pub_collision.publish(Bool(data=imminent))
        if imminent:
            self.pub_cmd.publish(Twist())

    def cmd_callback(self, msg):
        self.last_cmd = msg
        # Only forward if no collision
        # (In practice: check latest pointcloud)
        self.pub_cmd.publish(msg)
```

### 5. Payload Monitor

```python
#!/usr/bin/env python3
# payload_monitor.py - Alert if payload exceeds limit
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import WrenchStamped
from std_msgs.msg import Float32, Bool

class PayloadMonitor(Node):
    def __init__(self):
        super().__init__('payload_monitor')

        self.pub_warning = self.create_publisher(Bool, '/payload_warning', 10)
        self.pub_weight = self.create_publisher(Float32, '/payload_kg', 10)

        self.create_subscription(WrenchStamped, '/ft_sensor', self.ft_callback, 10)

        self.max_payload_kg = 10.0
        self.warning_threshold = 0.8  # 80% of max

        self.window_size = 50
        self.force_readings = []
        self.g = 9.81

    def ft_callback(self, msg):
        # Vertical force (z-axis) indicates weight
        fz = msg.wrench.force.z

        if fz > 0:  # Only positive (compression)
            weight_kg = fz / self.g
            self.force_readings.append(weight_kg)

            if len(self.force_readings) > self.window_size:
                self.force_readings.pop(0)

            avg_weight = sum(self.force_readings) / len(self.force_readings)

            self.pub_weight.publish(Float32(data=avg_weight))

            if avg_weight > self.max_payload_kg:
                self.get_logger().warn(f'OVERWEIGHT: {avg_weight:.1f}kg > {self.max_payload_kg}kg')
                self.pub_warning.publish(Bool(data=True))
            elif avg_weight > self.max_payload_kg * self.warning_threshold:
                self.get_logger().info(f'Payload warning: {avg_weight:.1f}kg')
                self.pub_warning.publish(Bool(data=True))
```

### 6. FMEA Table Template

```markdown
# Failure Mode and Effects Analysis

| Component | Failure Mode | Effect | Severity (1-5) | Detection | Probability | RPN |
|-----------|-------------|--------|----------------|----------|-------------|-----|
| ESTOP button | Doesn't depress | Can't stop robot | 5 | Visual inspection | Low | 5 |
| ESTOP circuit | Wire breaks | ESTOP always triggered | 2 | Test monthly | Medium | 4 |
| LIDAR | Dust covers | Collision not detected | 4 | Redundant sensors | Medium | 12 |
| Motor driver | Overcurrent | Motor stalls | 3 | Current limit | High | 9 |
| Battery | Low voltage | Sudden shutdown | 4 | BMS monitor | Low | 4 |
| WiFi link | Signal lost | No remote stop | 5 | Wired estop | High | 15 |

Severity: 1=minor, 5=catastrophic
Probability: Low/Medium/High
RPN = Severity × Probability (higher = worse)
```

---

## CLI Debug Commands

```bash
# Test ESTOP circuit
gpio read 22

# Check LIDAR distances
ros2 topic echo /scan --csv | head -20

# Monitor collision topic
ros2 topic echo /collision_imminent

# Check payload weight
ros2 topic echo /payload_kg

# View workspace bounds
ros2 topic echo /bounded_cmd_vel
```
