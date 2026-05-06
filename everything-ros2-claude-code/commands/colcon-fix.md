# /colcon-fix

Diagnose and fix colcon build errors using @colcon-agent.

## Usage

```
/colcon-fix                          # run colcon build and diagnose failures
/colcon-fix --package my_pkg         # fix specific package
/colcon-fix --error "paste error"    # diagnose a pasted error message
/colcon-fix --dry-run                # show fixes without applying
```

## What It Does

1. Runs `colcon build --packages-select <pkg> --cmake-args -DCMAKE_VERBOSE_MAKEFILE=ON`
2. Captures full build output
3. Identifies the root error (not just the cascade of failures)
4. Applies known fixes:
   - Adds missing `find_package()` calls
   - Adds missing `<depend>` to package.xml
   - Adds missing `install(TARGETS ...)` rules
   - Fixes missing `ament_package()` at end of CMakeLists
   - Adds missing `__init__.py` for Python packages
   - Fixes `setup.py` entry_points

5. Re-runs build to verify fix worked

## Output

```
Colcon Build Diagnosis
======================
Running: colcon build --packages-select my_pkg ...

Build FAILED. Root cause:

  CMake Error: Could not find a package configuration file provided by "nav_msgs"
  → Missing find_package(nav_msgs REQUIRED) in CMakeLists.txt
  → Missing <depend>nav_msgs</depend> in package.xml

  Linker Error: undefined reference to `rclcpp::Node::create_publisher`
  → ament_target_dependencies() missing 'rclcpp'

Applying fixes:
  ✅ Added find_package(nav_msgs REQUIRED) to CMakeLists.txt
  ✅ Added <depend>nav_msgs</depend> to package.xml
  ✅ Added rclcpp to ament_target_dependencies(my_node ...)

Re-running build...
✅ Build succeeded!

Run:
  source install/setup.bash
  ros2 run my_pkg my_node
```
