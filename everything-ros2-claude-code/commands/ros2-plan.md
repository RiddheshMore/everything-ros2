# /ros2-plan

Plan a new ROS 2 feature with consultation from specialist agents before writing code.

## Usage

```
/ros2-plan "Add a LiDAR-based obstacle detector that publishes PointCloud2 and stops the robot"
/ros2-plan "Migrate my rospy talker/listener to ROS 2 humble"
/ros2-plan "Add MoveIt2 pick-and-place to my UR5 arm setup"
```

## What Happens

1. **`@ros2-orchestrator`** reads the request and identifies all domains involved
2. Calls relevant specialist agents to surface constraints:
   - `@distro-compat-agent` — what APIs are available for your target distro
   - `@qos-agent` — what QoS profiles the new topics need
   - `@tf2-agent` / `@tf2-cartographer` — what frames are needed
   - `@package-structure-agent` — what dependencies will be required
   - `@interface-agent` — if new message types are needed
3. Returns a **structured implementation plan** before any code is written

## Output Format

```
ROS 2 Implementation Plan
=========================
Feature: LiDAR obstacle detector

Target Distro: humble
Package Type: ament_cmake (C++)

New Nodes:
  obstacle_detector_node
    Subscribes: /scan (LaserScan, qos_profile_sensor_data)
    Publishes:  /obstacles (sensor_msgs/PointCloud2, RELIABLE)
                /obstacle_detected (std_msgs/Bool, RELIABLE)
    Parameters: min_distance (float64, default: 0.3)
                scan_angle_range (float64, default: 1.5707)
                base_frame (string, default: 'base_link')

TF2 Frames Needed:
  - Lookup: base_link → laser_link (for projecting scan to robot frame)

Package Dependencies:
  - sensor_msgs
  - std_msgs
  - rclcpp
  - tf2_ros
  - tf2_geometry_msgs

QoS Plan:
  /scan subscriber: BEST_EFFORT (sensor data)
  /obstacles publisher: RELIABLE, depth=5
  /obstacle_detected: RELIABLE, depth=10

New Interfaces: None needed (using existing sensor_msgs/PointCloud2)

Estimated Files:
  src/obstacle_detector_node.cpp
  include/obstacle_detector/obstacle_detector_node.hpp
  launch/obstacle_detector.launch.py
  config/obstacle_detector_params.yaml
  package.xml, CMakeLists.txt

Proceed? Run /ros2-new-pkg obstacle_detector --type cpp --distro humble
then implement based on this plan.
```
