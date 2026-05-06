---
name: topic-naming
description: ROS 2 topic, service, and action naming conventions reference
triggers:
  - topic name
  - service name
  - action name
  - naming convention
  - snake_case
  - namespace
---

# ROS 2 Topic / Service / Action Naming

## Rules Summary

- All names: `snake_case` (no CamelCase, no hyphens, no spaces)
- Topics: relative by default (no leading `/` in node code)
- Absolute topics: only when intentional (breaks namespacing)
- Max 255 characters, alphanumeric + underscore + `/`

## Standard Topics (REP-103)

| Topic | Type | Notes |
|---|---|---|
| `cmd_vel` | `geometry_msgs/Twist` | Velocity command |
| `odom` | `nav_msgs/Odometry` | Odometry |
| `scan` | `sensor_msgs/LaserScan` | 2D LiDAR |
| `points` | `sensor_msgs/PointCloud2` | 3D LiDAR |
| `joint_states` | `sensor_msgs/JointState` | Joint positions |
| `map` | `nav_msgs/OccupancyGrid` | 2D map |
| `camera/image_raw` | `sensor_msgs/Image` | Camera |
| `camera/camera_info` | `sensor_msgs/CameraInfo` | Intrinsics |
| `imu/data` | `sensor_msgs/Imu` | IMU |
| `battery_state` | `sensor_msgs/BatteryState` | Battery |
| `diagnostics` | `diagnostic_msgs/DiagnosticArray` | Health |

## Service Name Pattern: `verb_noun`

```
✅ set_velocity_limit
✅ get_robot_state
✅ reset_odometry
✅ trigger_calibration
✅ compute_path

❌ velocity_limit  (no verb)
❌ SetVelocity     (CamelCase)
❌ velocity-limit  (hyphen)
```

## Action Name Pattern: `verb_noun`

```
✅ navigate_to_pose
✅ follow_path
✅ pick_object
✅ dock_to_charger
✅ move_arm_to_joint_goal

❌ NavigateToPose   (CamelCase)
❌ go-to            (hyphen)
❌ target_pose      (no verb)
```

## Namespace Convention

```
/<robot_name>/<subsystem>/<topic>

Examples:
/robot1/arm/joint_states
/robot1/base/cmd_vel
/robot1/camera/image_raw
/fleet/robot_status
```

## Relative vs Absolute

```python
# RELATIVE — resolves to /<node_namespace>/my_topic
# Namespace remapping works correctly
self.create_publisher(String, 'my_topic', 10)

# ABSOLUTE — always /global_topic, namespace remapping SKIPPED
self.create_publisher(String, '/global_topic', 10)
# Only use absolute when intentionally bypassing namespace (e.g. /tf, /clock)
```
