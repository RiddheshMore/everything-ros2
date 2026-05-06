# /distro-check

Check all code for compatibility with the target ROS 2 distribution.
Reads ROS_DISTRO from CLAUDE.md. Delegates to @distro-compat-agent.

## Usage

```
/distro-check                    # use distro from CLAUDE.md
/distro-check --distro jazzy     # override target distro
/distro-check --from humble --to jazzy  # migration path
```

## Output

```
Distro Compatibility Check
===========================
Target distro: humble
Scanned: 6 Python files, 4 C++ files

my_arm_pkg/arm_controller.py:
  ❌ from moveit_configs_utils import MoveItConfigsBuilder
     → Not available in Humble. Use MoveGroupInterface directly.
  ❌ from moveit.core.robot_state import RobotState
     → MoveItPy not available in Humble.
  ✅ import rclpy — OK
  ✅ from rclpy.lifecycle import LifecycleNode — OK in Humble

my_nav_pkg/navigator.py:
  ⚠️  from nav2_msgs.action import DockRobot
     → Docking server not in Humble. Available from Jazzy.

Total: 2 errors, 1 warning
Recommended action: either upgrade target to Jazzy or use Humble-compatible alternatives.
```
