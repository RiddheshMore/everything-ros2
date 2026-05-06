---
name: interface-design
description: ROS 2 custom .msg .srv .action interface design — types, naming, package setup
triggers:
  - .msg
  - .srv
  - .action
  - custom message
  - custom service
  - custom action
  - rosidl
  - interface
---

# ROS 2 Interface Design

## Valid Field Types Quick Reference

```
bool          byte          char
float32       float64       ← NOT 'float' or 'double'
int8          uint8
int16         uint16
int32         uint32
int64         uint64
string        wstring

# Arrays
float64[]          # unbounded dynamic
float64[3]         # fixed-size 3
float64[<=100]     # bounded dynamic (embedded-safe)

# Nested
std_msgs/Header header
geometry_msgs/Pose pose
```

## Message Template

```
# MyData.msg

# Header (include when message needs a timestamp or frame_id)
std_msgs/Header header

# Use descriptive field names with units in name when ambiguous
float64 distance_m           # meters
float64 velocity_mps         # m/s
float64 angle_rad            # radians

# Use constants for enumerated states (ALL_CAPS)
uint8 state
uint8 STATE_IDLE    = 0
uint8 STATE_RUNNING = 1
uint8 STATE_ERROR   = 2

# Arrays
float64[] measurements       # dynamic
string[<=10] labels          # bounded
```

## Service Template

```
# ComputePath.srv

# ------- REQUEST -------
geometry_msgs/PoseStamped start_pose
geometry_msgs/PoseStamped goal_pose
string planner_id
float64 timeout_sec

---
# ------- RESPONSE -------
bool success
string error_message         # human-readable on failure
nav_msgs/Path planned_path
float64 planning_time_s
```

## Action Template

```
# NavigateToGoal.action

# ------- GOAL -------
geometry_msgs/PoseStamped target_pose
float64 speed_limit_mps
bool allow_replanning

---
# ------- RESULT -------
bool success
string error_code
geometry_msgs/Pose final_pose
float64 total_distance_m
float64 total_time_s

---
# ------- FEEDBACK -------
std_msgs/Header header
float64 distance_remaining_m
float64 current_speed_mps
geometry_msgs/Pose current_pose
float32 completion_percent
```

## Package Setup for Interfaces

```xml
<!-- package.xml -->
<package format="3">
  <n>my_interfaces</n>
  <version>0.0.1</version>
  <description>Custom ROS 2 interfaces</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <!-- Add all message packages your interfaces reference -->
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>nav_msgs</depend>

  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.8)
project(my_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SensorReading.msg"
  "msg/RobotStatus.msg"
  "srv/ComputePath.srv"
  "srv/SetMode.srv"
  "action/NavigateToGoal.action"
  DEPENDENCIES std_msgs geometry_msgs nav_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

## Using Custom Interfaces in Another Package

```xml
<!-- package.xml of the consuming package -->
<depend>my_interfaces</depend>
```

```python
# Python
from my_interfaces.msg import SensorReading
from my_interfaces.srv import ComputePath
from my_interfaces.action import NavigateToGoal
```

```cpp
// C++
#include "my_interfaces/msg/sensor_reading.hpp"
#include "my_interfaces/srv/compute_path.hpp"
#include "my_interfaces/action/navigate_to_goal.hpp"
```

```cmake
# CMakeLists.txt of the consuming package
find_package(my_interfaces REQUIRED)
ament_target_dependencies(my_node my_interfaces)
```

## Design Rules

1. **Prefer existing types** — check `common_interfaces` before creating custom ones
2. **Separate interface packages** — don't mix interface definitions with node code
3. **Units in names** — `distance_m`, `angle_rad`, `velocity_mps`, `time_s`
4. **Error info in responses** — always include `bool success` + `string error_message`
5. **Header for sensor data** — include `std_msgs/Header header` for temporal/spatial data
6. **Bounded arrays for embedded** — `float32[<=256]` instead of `float32[]`
7. **Constants for enum-like fields** — use `uint8 STATE_X = N` pattern
