# /qos-audit

Audit all publisher and subscriber QoS configurations using @qos-agent.

## Usage

```
/qos-audit
/qos-audit --package my_pkg
/qos-audit --live           # check live QoS on running system
```

## What It Does

**Static analysis:**
- Finds every `create_publisher` and `create_subscription` call
- Extracts message type and QoS profile
- Cross-references pub/sub QoS pairs on the same topic
- Checks data type → QoS recommendations (sensor data should be BEST_EFFORT)
- Detects TRANSIENT_LOCAL vs VOLATILE mismatch (silent failure)

**Live analysis (`--live`):**
- Calls `ros2 topic info <topic> --verbose` for all active topics
- Reports actual QoS incompatibilities from running DDS

## Output

```
QoS Audit Report
================
Scanned: 6 publisher/subscriber pairs

Topic: /scan (sensor_msgs/LaserScan)
  Publisher  → RELIABLE, KEEP_LAST(10), VOLATILE
  ⚠️  Recommend BEST_EFFORT for high-frequency sensor data
  Subscriber → BEST_EFFORT, KEEP_LAST(5)
  ✅ Compatible (reliable→best_effort is OK)

Topic: /map (nav_msgs/OccupancyGrid)
  Publisher  → RELIABLE, KEEP_LAST(1), TRANSIENT_LOCAL  (map_server)
  Subscriber → RELIABLE, KEEP_LAST(1), VOLATILE          (my_costmap_node)
  ❌ INCOMPATIBLE: map_server uses TRANSIENT_LOCAL but subscriber uses VOLATILE
     Late-joining subscriber will NEVER receive the map.
     Fix: Add DurabilityPolicy.TRANSIENT_LOCAL to subscriber QoS

Topic: /cmd_vel (geometry_msgs/Twist)
  Publisher  → RELIABLE, KEEP_LAST(10)
  Subscriber → RELIABLE, KEEP_LAST(10)
  ✅ Compatible

Total: 1 error, 1 warning
```
