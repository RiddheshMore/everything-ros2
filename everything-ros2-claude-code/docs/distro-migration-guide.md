# ROS 2 Distro Migration Guide

A practical guide for migrating ROS 2 projects between distributions.

---

## Humble → Jazzy (LTS to LTS — most common migration)

### Breaking Changes

#### Python: `ament_python.packages` is `ament_python.packages`
No change — still the same import.

#### MoveIt2: New recommended pattern
```python
# Humble: use MoveGroupInterface directly
from moveit.planning import MoveGroupInterface

# Jazzy: use moveit_configs_utils (much simpler)
from moveit_configs_utils import MoveItConfigsBuilder
```

#### Nav2: New Docking Server (Jazzy+)
```python
# Jazzy: new docking action available
from nav2_msgs.action import DockRobot, UndockRobot
```

#### Nav2: Route Server (Kilted+)
```python
from nav2_msgs.action import FollowRoute  # Kilted+ only
```

#### Executors: New EventsExecutor (Jazzy+)
```cpp
// Jazzy: new high-performance executor
#include "rclcpp/executors/events_executor/events_executor.hpp"
rclcpp::executors::EventsExecutor executor;
```

#### RMW: Zenoh available (Jazzy+)
```bash
# Jazzy: can use rmw_zenoh for WAN/multi-network
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
```

### Step-by-Step Migration

```bash
# 1. Update distro in all places
sed -i 's/humble/jazzy/g' Dockerfile
sed -i 's/ros:humble/ros:jazzy/g' Dockerfile

# 2. Update apt sources
echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list
sudo apt update

# 3. Install Jazzy
sudo apt install ros-jazzy-desktop

# 4. Re-run rosdep
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y

# 5. Build and check for errors
colcon build 2>&1 | grep -E "error:|warning:" | head -30

# 6. Run /distro-check --from humble --to jazzy in Claude Code
```

---

## Humble → Iron (not recommended — Iron is EOL)

Skip this migration. Go directly to Jazzy.

---

## Iron → Jazzy

Same as Humble → Jazzy plus:

```python
# Iron had service introspection — still works in Jazzy
# Iron had type description — still works in Jazzy
# No breaking changes from Iron → Jazzy for most code
```

---

## API Differences Quick Reference

### rclcpp differences

| Code | Humble | Jazzy |
|---|---|---|
| `EventsExecutor` | ❌ | ✅ |
| `TypeAdapter` | ✅ | ✅ |
| Service introspection | ❌ | ✅ |

### rclpy differences

| Code | Humble | Jazzy |
|---|---|---|
| `rclpy.spin` | ✅ | ✅ |
| `rclpy.executors.MultiThreadedExecutor` | ✅ | ✅ |
| Type description service | ❌ | ✅ |

### Nav2 differences

| Feature | Humble | Jazzy |
|---|---|---|
| `DockRobot` action | ❌ | ✅ |
| MPPI controller | ✅ | ✅ (improved) |
| Smac Hybrid A* | ✅ | ✅ |
| Groot2 BT monitoring | ❌ | ✅ |
| `nav2_simple_commander` | ✅ | ✅ |

### MoveIt2 differences

| Feature | Humble | Iron | Jazzy |
|---|---|---|---|
| `moveit_configs_utils` | ❌ | ✅ | ✅ |
| `MoveItPy` (Python) | ❌ | ✅ | ✅ |
| Drake integration | ❌ | ❌ | ✅ |

---

## Dockerfile Template (Multi-Distro)

```dockerfile
# ARG for distro — default to humble (LTS), override for jazzy
ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}-ros-base

ENV ROS_DISTRO=${ROS_DISTRO}
ENV DEBIAN_FRONTEND=noninteractive

# Install workspace dependencies
COPY src/ /ros2_ws/src/
WORKDIR /ros2_ws

RUN apt-get update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build --symlink-install

# Source in every shell
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /etc/bash.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> /etc/bash.bashrc

CMD ["/bin/bash"]
```

```bash
# Build for Humble
docker build --build-arg ROS_DISTRO=humble -t myrobot:humble .

# Build for Jazzy
docker build --build-arg ROS_DISTRO=jazzy -t myrobot:jazzy .
```

---

## CI Matrix (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: ROS 2 CI

on: [push, pull_request]

jobs:
  build-and-test:
    strategy:
      matrix:
        ros_distro: [humble, jazzy]
        os: [ubuntu-22.04]

    runs-on: ${{ matrix.os }}
    container:
      image: ros:${{ matrix.ros_distro }}-ros-base

    steps:
      - uses: actions/checkout@v4
        with:
          path: ros2_ws/src/my_pkg

      - name: Install dependencies
        run: |
          apt-get update
          rosdep update
          rosdep install --from-paths ros2_ws/src --ignore-src -r -y

      - name: Build
        run: |
          . /opt/ros/${{ matrix.ros_distro }}/setup.sh
          cd ros2_ws
          colcon build --symlink-install

      - name: Test
        run: |
          . /opt/ros/${{ matrix.ros_distro }}/setup.sh
          . ros2_ws/install/setup.sh
          cd ros2_ws
          colcon test
          colcon test-result --verbose
```
