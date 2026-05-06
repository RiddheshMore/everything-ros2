# /launch-validate

Validate all .launch.py files using @launch-agent.

## Usage

```
/launch-validate
/launch-validate path/to/specific.launch.py
/launch-validate --dry-run      # parse only, don't check executables
```

## What It Does

- Finds all `*.launch.py` files in the workspace
- Checks `generate_launch_description()` returns `LaunchDescription([...])`
- Verifies all `Node()` package/executable pairs exist
- Flags hardcoded absolute paths (use `get_package_share_directory`)
- Checks `use_sim_time` is declared and propagated
- Validates `IncludeLaunchDescription` paths resolve
- Detects lifecycle nodes without a lifecycle manager

## Output

```
Launch File Validation
======================
Found 4 launch files

bringup.launch.py:
  ✅ LaunchDescription([...]) structure correct
  ✅ use_sim_time declared and propagated to 3 nodes
  ❌ Hardcoded path: '/home/user/ros2_ws/src/my_pkg/config/nav2_params.yaml'
     Fix: os.path.join(get_package_share_directory('my_pkg'), 'config', 'nav2_params.yaml')
  ⚠️  Node 'map_server' is lifecycle but no lifecycle_manager found in launch

robot.launch.py:
  ✅ All checks passed

nav2.launch.py:
  ❌ IncludeLaunchDescription: package 'nav2_bringup' not found on this system
     Fix: sudo apt install ros-humble-nav2-bringup

slam.launch.py:
  ✅ All checks passed

Total: 2 errors, 1 warning
```
