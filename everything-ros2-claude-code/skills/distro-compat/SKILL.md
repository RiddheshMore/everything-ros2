---
name: distro-compat
description: ROS 2 distribution API compatibility quick reference
triggers:
  - humble
  - jazzy
  - kilted
  - rolling
  - distro
  - distribution
  - API version
  - not available
---

# ROS 2 Distro Compatibility Cheat Sheet

## Supported Distros (2026)

| Distro | Status | EOL |
|---|---|---|
| Humble | ✅ Active LTS | May 2027 |
| Iron | ❌ EOL | Nov 2024 |
| Jazzy | ✅ Active LTS | May 2029 |
| Kilted | ✅ Active | Nov 2026 |
| Rolling | 🔄 Dev | ongoing |

## Key API Differences

### Only in Jazzy+
- `rclcpp::executors::EventsExecutor`
- `moveit_configs_utils.MoveItConfigsBuilder` (actually Iron+)
- `MoveItPy` Python bindings (Iron+)
- Service introspection (`ServiceIntrospectionState`)
- Zenoh RMW (`rmw_zenoh_cpp`)
- Nav2 Docking Server (`DockRobot` action)
- Groot2 BT monitoring

### Only in Kilted+
- Nav2 Route Server
- `generate_parameter_library` widely adopted

### In All Supported Distros (Humble+)
- `rclpy`, `rclcpp` core APIs
- `rclcpp_lifecycle`
- `nav2_simple_commander`
- `ros2_control`
- SLAM Toolbox, Nav2, AMCL
- `rclcpp::QoS`, `SensorDataQoS`
- `tf2_ros` full API

## Check Your Target Distro

```bash
# What distro is installed?
echo $ROS_DISTRO

# What distro does this package target?
cat CLAUDE.md | grep ROS_DISTRO
```

## Conditional Compilation (C++)

```cpp
#include <rclcpp/rclcpp.hpp>

#if RCLCPP_VERSION_GTE(21, 0, 0)  // Jazzy+
  // Use new API
#else
  // Use Humble-compatible API
#endif
```

## Conditional Import (Python)

```python
import rclpy
from packaging import version

if version.parse(rclpy.__version__) >= version.parse('3.3.0'):
    # Jazzy+ feature
    pass
else:
    # Humble fallback
    pass
```
