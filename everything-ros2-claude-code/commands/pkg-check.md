# /pkg-check

Validate package.xml and CMakeLists.txt / setup.py using @package-structure-agent.

## Usage

```
/pkg-check
/pkg-check --package my_pkg
/pkg-check --fix             # attempt to auto-add missing dependencies
```

## What It Does

1. **package.xml checks:**
   - Format version is 3 (not 2 or 1)
   - All `#include` (C++) and `import`/`from X import` (Python) have matching `<depend>` tags
   - `<buildtool_depend>` includes `ament_cmake` or `rosidl_default_generators` as needed
   - `<member_of_group>rosidl_interface_packages</member_of_group>` present for interface packages
   - No typos in package names (checks against known ROS 2 packages)

2. **CMakeLists.txt checks (ament_cmake):**
   - `cmake_minimum_required(VERSION 3.8)` present
   - `find_package(ament_cmake REQUIRED)` present
   - `ament_package()` is the LAST call
   - All `ament_target_dependencies` packages also in `find_package`
   - `install(TARGETS ...)` rule exists for every executable
   - `install(DIRECTORY launch config ...)` for non-code assets

3. **setup.py checks (ament_python):**
   - `entry_points['console_scripts']` has an entry for each node executable
   - `data_files` includes `package.xml` and resource marker
   - `setup.cfg` exists

## Output

```
Package Structure Audit
=======================
Package: my_robot_controller (ament_cmake)

package.xml:
  ❌ Missing dependency: 'nav_msgs' — imported in controller.cpp line 3
  ❌ Missing dependency: 'tf2_ros' — imported in controller.cpp line 7
  ✅ rclcpp declared
  ✅ std_msgs declared
  ✅ Format 3

CMakeLists.txt:
  ✅ cmake_minimum_required(3.8)
  ✅ find_package(ament_cmake REQUIRED)
  ❌ install(TARGETS) missing for 'controller_node'
  ⚠️  No install(DIRECTORY launch ...) — launch files won't be installed
  ✅ ament_package() is last call

Auto-fix available with /pkg-check --fix
```
