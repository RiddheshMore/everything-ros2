---
name: qos-patterns
description: ROS 2 Quality of Service policy selection and compatibility guide
triggers:
  - creating a publisher
  - creating a subscriber
  - qos
  - quality of service
  - message not received
  - topic not working
---

# ROS 2 QoS Patterns

## Quick Selection Guide

```
Is data high-frequency (>10 Hz) sensor data?
  YES → BEST_EFFORT + VOLATILE
  NO  → Does a late subscriber need past data (like /map)?
          YES → RELIABLE + TRANSIENT_LOCAL + depth=1
          NO  → RELIABLE + VOLATILE + depth=10
```

## Copy-Paste QoS Profiles (Python)

```python
from rclpy.qos import (
    QoSProfile, ReliabilityPolicy, HistoryPolicy,
    DurabilityPolicy, LivelinessPolicy
)

# Sensor data (LiDAR, camera, IMU)
SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=5,
    durability=DurabilityPolicy.VOLATILE,
)

# Latched / map data (late subscribers get last value)
LATCH_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
)

# Standard reliable (commands, odometry, joint states)
RELIABLE_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
    durability=DurabilityPolicy.VOLATILE,
)
```

## Copy-Paste QoS Profiles (C++)

```cpp
#include "rclcpp/qos.hpp"

// Sensor data
auto sensor_qos = rclcpp::SensorDataQoS();

// Latched
auto latch_qos = rclcpp::QoS(rclcpp::KeepLast(1))
    .reliable()
    .transient_local();

// Reliable
auto reliable_qos = rclcpp::QoS(rclcpp::KeepLast(10)).reliable();
```

## Debug QoS Mismatch

```bash
# See all publishers and subscribers with their QoS
ros2 topic info /my_topic --verbose

# Look for "Incompatible QoS" messages  
ros2 topic echo /rosout 2>&1 | grep -i "incompatible\|qos"

# Check if topic has subscribers
ros2 topic info /my_topic
```
