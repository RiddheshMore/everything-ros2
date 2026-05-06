# /ros2-validate

Run a full ROS 2 project audit using all specialist sub-agents.

## What This Command Does

1. **@package-structure-agent** — scans all package.xml and CMakeLists.txt files
2. **@topic-schema-agent** — audits all topic/service/action names in source code
3. **@distro-compat-agent** — checks for distro incompatibilities (reads ROS_DISTRO from CLAUDE.md)
4. **@qos-agent** — reviews all publisher/subscriber QoS configurations
5. **@tf2-agent** — validates frame ID usage and transform tree
6. **@launch-agent** — validates all `.launch.py` files
7. **@urdf-validator** — if any URDF/XACRO files are found, validates them
8. **@interface-agent** — validates all custom .msg/.srv/.action files

## Usage

```
/ros2-validate
/ros2-validate --package my_pkg
/ros2-validate --agent urdf     # run only urdf-validator
/ros2-validate --distro jazzy   # override target distro
```

## Output

Produces a consolidated report:
```
ROS 2 Project Audit
===================
Packages found: 3
Target distro: humble

Package Structure:     2 errors, 0 warnings
Topic Schema:          0 errors, 3 warnings
Distro Compatibility:  1 error, 0 warnings
QoS Configuration:     0 errors, 2 warnings
TF2 Frames:            0 errors, 1 warning
Launch Files:          0 errors, 0 warnings
URDF/XACRO:            1 error, 0 warnings
Custom Interfaces:     0 errors, 0 warnings

Total: 4 errors, 6 warnings

Critical errors must be fixed before deployment.
Run /colcon-fix for build system errors.
```
