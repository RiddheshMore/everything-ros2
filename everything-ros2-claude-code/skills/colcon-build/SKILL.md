---
name: colcon-build
description: colcon build system cheat sheet — common commands, flags, workspace management
triggers:
  - colcon
  - colcon build
  - workspace
  - build error
  - ament
  - overlay
  - underlay
---

# colcon Build Patterns

## Essential Commands

```bash
# Full workspace build
colcon build

# Build with symlink (dev mode — Python changes take effect without rebuild)
colcon build --symlink-install

# Build only specific packages (much faster iteration)
colcon build --packages-select my_pkg

# Build a package and all its dependencies
colcon build --packages-up-to my_pkg

# Build everything EXCEPT certain packages
colcon build --packages-skip slow_pkg another_pkg

# Verbose CMake output (find the actual error)
colcon build --packages-select my_pkg \
  --cmake-args -DCMAKE_VERBOSE_MAKEFILE=ON

# Pass extra CMake flags
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Build with compile_commands.json (for clangd / IDE support)
colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Parallel jobs (default is all cores)
colcon build --parallel-workers 4
```

## Workspace Setup

```
ros2_ws/
├── src/          ← clone your packages here
├── build/        ← colcon output (don't edit)
├── install/      ← sourced by setup.bash
└── log/          ← colcon logs
```

```bash
# Standard workspace bootstrap
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Source underlay (system ROS 2)
source /opt/ros/humble/setup.bash

# Build
colcon build --symlink-install

# Source your workspace overlay
source install/setup.bash

# Tip: add to ~/.bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

## Workspace Layering

```bash
# Underlay → Overlay chain
source /opt/ros/humble/setup.bash          # underlay 1 (ROS 2 base)
source ~/upstream_ws/install/setup.bash    # underlay 2 (third-party)
source ~/my_ws/install/setup.bash          # your overlay

# IMPORTANT: source order matters — last source wins for package lookups
```

## Clean Build

```bash
# Full clean (when things go really wrong)
cd ~/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/humble/setup.bash
colcon build --symlink-install

# Clean only one package
rm -rf build/my_pkg install/my_pkg
colcon build --packages-select my_pkg --symlink-install
```

## Testing

```bash
# Build and run tests
colcon test --packages-select my_pkg

# See test results
colcon test-result --verbose

# Run a specific test file
colcon test --packages-select my_pkg \
  --pytest-args -k test_my_function

# Run tests with output shown
colcon test --packages-select my_pkg --event-handlers console_direct+
```

## colcon.meta — Per-Package Build Options

```json
// colcon.meta — place in workspace root to configure all builds
{
    "names": {
        "my_slow_pkg": {
            "cmake-args": ["-DCMAKE_BUILD_TYPE=Release"]
        },
        "my_debug_pkg": {
            "cmake-args": ["-DCMAKE_BUILD_TYPE=Debug", "-DCMAKE_VERBOSE_MAKEFILE=ON"]
        }
    }
}
```

## Common Build Errors and Fixes

| Error | Fix |
|---|---|
| `Could not find package 'rclcpp'` | `source /opt/ros/<distro>/setup.bash` |
| `ament_target_dependencies: unknown CMake command` | Add `find_package(ament_cmake REQUIRED)` |
| `No module named 'my_pkg'` | Add `touch my_pkg/__init__.py` |
| `install/ missing executable` | Add `install(TARGETS ...)` to CMakeLists |
| Stale build after rename | `rm -rf build/my_pkg install/my_pkg` and rebuild |
| Python node not found | Check `entry_points` in `setup.py` |

## Dependency Resolution

```bash
# Install missing system dependencies automatically
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

# Show what rosdep would install (dry run)
rosdep install --from-paths src --ignore-src -r --simulate

# Update rosdep database
rosdep update
```

## colcon List — Inspect Workspace

```bash
# List all packages in workspace
colcon list

# Show dependency graph
colcon graph

# Show what would be built for a package
colcon build --packages-up-to my_pkg --dry-run
```
