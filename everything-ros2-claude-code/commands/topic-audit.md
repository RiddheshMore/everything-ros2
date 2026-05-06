# /topic-audit

Audit all topic, service, and action names in the workspace using @topic-schema-agent.

## Usage

```
/topic-audit
/topic-audit --package my_pkg
/topic-audit --live          # audit running system with ros2 topic list
```

## What It Does

Scans all `.py` and `.cpp` files for:
- `create_publisher(MsgType, 'topic_name', ...)`
- `create_subscription(MsgType, 'topic_name', ...)`
- `create_client(SrvType, 'service_name')`
- `create_service(SrvType, 'service_name', ...)`
- `ActionClient(node, ActionType, 'action_name')`
- `ActionServer(node, ActionType, 'action_name', ...)`

Checks against:
- ROS 2 naming convention (snake_case, no double slashes)
- REP-103 standard topic names (warns when non-standard name used for common data types)
- Verb patterns for services and actions

## Output

```
Topic Schema Audit
==================
Scanned: 8 source files across 3 packages

my_sensor_pkg/sensor_node.py:
  ✅ /scan (LaserScan) — standard REP-103 name
  ⚠️  /LaserData (LaserScan) — use /scan per REP-103 convention
  ✅ /imu/data (Imu) — standard name

my_controller_pkg/controller.py:
  ❌ /CmdVelocity (Twist) — CamelCase not allowed; use /cmd_vel
  ✅ cmd_vel (Twist) — relative name, correct
  ❌ //base/odom — double slash in topic name

Services:
  ✅ set_speed — verb-based, snake_case
  ❌ VelocityLimit — missing verb, CamelCase not allowed

Actions:
  ✅ navigate_to_pose — verb_noun, correct
  ❌ GoTo — CamelCase, missing noun

Total: 3 errors, 1 warning
```
