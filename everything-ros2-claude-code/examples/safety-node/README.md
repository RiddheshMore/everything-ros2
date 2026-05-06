# Safety Node

Comprehensive safety monitoring for ROS 2 robots: hardware ESTOP, speed limiting, workspace boundaries, and collision detection.

## Structure

```
safety-node/
├── README.md
├── src/
│   ├── hardware_estop.py      # Hardware ESTOP GPIO monitor
│   ├── speed_limiter.py       # Velocity limiter with LIDAR
│   ├── workspace_monitor.py   # Virtual boundary enforcement
│   └── collision_detector.py   # PointCloud collision detection
├── config/
│   └── safety_limits.yaml     # Safety parameters
├── launch/
│   └── safety.launch.py       # Safety node bringup
├── test/
│   └── test_safety.py         # Safety node tests
└── scripts/
    └── fmea_template.md       # FMEA documentation template
```

## Architecture

```
                    ┌─────────────────┐
                    │  Safety Core    │
                    │  (supervisor)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ Hardware ESTOP│  │  Speed Limiter  │  │ Workspace Monitor │
│   (GPIO)      │  │   (LIDAR)      │  │    (Odometry)    │
└───────────────┘  └─────────────────┘  └──────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Safe Cmd Vel   │
                    │  /safe_cmd_vel │
                    └─────────────────┘
```

## Hardware ESTOP Node

```python
# hardware_estop.py
import RPi.GPIO as GPIO
import subprocess
import signal
import sys

ESTOP_PIN = 22  # Physical button pin
MOTOR_ENABLE_PIN = 23  # Motor driver enable

def shutdown_motors(channel):
    print("ESTOP TRIGGERED")
    GPIO.output(MOTOR_ENABLE_PIN, GPIO.LOW)  # Cut motor power
    subprocess.run(['ros2', 'topic', 'pub', '-1', '/motors_enable',
                   'std_msgs/msg/Bool', '{data: false}'])
    sys.exit(1)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESTOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MOTOR_ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.add_event_detect(ESTOP_PIN, GPIO.FALLING, callback=shutdown_motors, bouncetime=100)

signal.signal(signal.SIGTERM, lambda s, f: GPIO.cleanup())
while True:
    signal.pause()
```

## Speed Limiter Node

```python
# speed_limiter.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class SpeedLimiter(Node):
    def __init__(self):
        super().__init__('speed_limiter')
        self.max_linear = 1.0
        self.max_angular = 2.0
        self.min_distance = 0.5  # Stop if closer

        self.pub = self.create_publisher(Twist, '/safe_cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.min_scan_distance = float('inf')
        self.lidar_ok = False

    def scan_callback(self, msg):
        valid_ranges = [r for r in msg.ranges if 0.1 < r < 10.0]
        if valid_ranges:
            self.min_scan_distance = min(valid_ranges)
            self.lidar_ok = True

    def cmd_callback(self, msg):
        safe_cmd = Twist()
        if not self.lidar_ok:
            safe_cmd.linear.x = msg.linear.x * 0.3
            safe_cmd.angular.z = msg.angular.z * 0.3
            self.pub.publish(safe_cmd)
            return

        if self.min_scan_distance < self.min_distance:
            self.pub.publish(Twist())  # Emergency stop
            return

        if self.min_scan_distance < 2.0:
            factor = max(0.1, self.min_scan_distance / 2.0)
            safe_cmd.linear.x = msg.linear.x * factor
            safe_cmd.angular.z = msg.angular.z * factor
        else:
            safe_cmd = msg

        safe_cmd.linear.x = max(-self.max_linear, min(self.max_linear, safe_cmd.linear.x))
        safe_cmd.angular.z = max(-self.max_angular, min(self.max_angular, safe_cmd.angular.z))
        self.pub.publish(safe_cmd)
```

## Workspace Monitor Node

```python
# workspace_monitor.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class WorkspaceMonitor(Node):
    def __init__(self):
        super().__init__('workspace_monitor')
        self.pub = self.create_publisher(Twist, '/bounded_cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.bounds = {
            'min_x': -5.0, 'max_x': 5.0,
            'min_y': -5.0, 'max_y': 5.0,
            'margin': 0.5
        }
        self.in_danger = False
        self.position = (0.0, 0.0)

    def odom_callback(self, msg):
        self.position = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    def cmd_callback(self, msg):
        if self.in_danger:
            self.pub.publish(Twist())
            return
        x, y = self.position
        bounded_cmd = Twist()
        if x < self.bounds['min_x'] + self.bounds['margin']:
            bounded_cmd.linear.x = max(0, msg.linear.x)
        elif x > self.bounds['max_x'] - self.bounds['margin']:
            bounded_cmd.linear.x = min(0, msg.linear.x)
        else:
            bounded_cmd.linear.x = msg.linear.x
        bounded_cmd.angular.z = msg.angular.z
        self.pub.publish(bounded_cmd)
```

## Safety Launch File

```python
# safety.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='safety_node', executable='hardware_estop', name='estop'),
        Node(package='safety_node', executable='speed_limiter', name='speed_limiter'),
        Node(package='safety_node', executable='workspace_monitor', name='workspace_monitor'),
        Node(package='safety_node', executable='collision_detector', name='collision_detector'),
    ])
```

## Safety Parameters

```yaml
# safety_limits.yaml
speed_limiter:
  ros__parameters:
    max_linear_velocity: 1.0
    max_angular_velocity: 2.0
    min_safe_distance: 0.5
    slow_down_distance: 2.0
    conservative_factor: 0.3

workspace_monitor:
  ros__parameters:
    min_x: -5.0
    max_x: 5.0
    min_y: -5.0
    max_y: 5.0
    margin: 0.5

collision_detector:
  ros__parameters:
    collision_distance: 0.3
    enabled: true
```

## FMEA Table

```markdown
| Component | Failure Mode | Effect | Severity | Detection | Probability | RPN |
|-----------|-------------|--------|----------|----------|-------------|-----|
| ESTOP button | Doesn't depress | Can't stop robot | 5 | Visual inspection | Low | 5 |
| ESTOP circuit | Wire breaks | ESTOP always triggered | 2 | Test monthly | Medium | 4 |
| LIDAR | Dust covered | Collision not detected | 4 | Redundant sensors | Medium | 12 |
| Motor driver | Overcurrent | Motor stalls | 3 | Current limit | High | 9 |
| Battery | Low voltage | Sudden shutdown | 4 | BMS monitor | Low | 4 |
| WiFi link | Signal lost | No remote stop | 5 | Wired estop | High | 15 |
```

## Testing

```bash
# Test ESTOP simulation
ros2 topic pub /hardware_estop/trigger std_msgs/msg/Empty '{}' -1

# Test speed limiter
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}}' -1
ros2 topic echo /safe_cmd_vel

# Test workspace boundary
ros2 topic pub /odom nav_msgs/msg/Odometry '{pose: {pose: {position: {x: 10.0}}}}' -1

# Verify safety chain
ros2 topic echo /collision_imminent
```

## Run

```bash
# Build
colcon build --packages-select safety_node
source install/setup.bash

# Launch safety stack
ros2 launch safety_node safety.launch.py

# Or run individual nodes
ros2 run safety_node speed_limiter
```
