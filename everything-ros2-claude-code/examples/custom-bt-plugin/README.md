# Custom Nav2 Behavior Tree Plugin Example

How to write a custom BehaviorTree.CPP action node for the Nav2 behavior tree navigator.

## What This Shows

- Correct `BT::ActionNodeBase` subclass structure
- Nav2 plugin registration macro
- Package setup for a BT plugin library
- How to load the plugin in `bt_navigator` params

## File Structure

```
custom_bt_plugin/
├── package.xml
├── CMakeLists.txt
├── include/custom_bt_plugin/
│   └── check_battery_condition.hpp
├── src/
│   └── check_battery_condition.cpp
└── config/
    └── my_behavior_tree.xml   ← custom BT using the plugin
```

## The Plugin (C++)

```cpp
// include/custom_bt_plugin/check_battery_condition.hpp
#pragma once

#include "behaviortree_cpp_v3/behavior_tree.h"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/battery_state.hpp"
#include "nav2_behavior_tree/bt_service_node.hpp"

namespace custom_bt_plugin {

/**
 * @brief BT Condition: Returns SUCCESS if battery > threshold, FAILURE otherwise.
 *
 * BT XML usage:
 *   <CheckBatteryLevel battery_topic="/battery_state" min_level="0.2"/>
 */
class CheckBatteryLevel : public BT::ConditionNode {
public:
    CheckBatteryLevel(const std::string& name,
                      const BT::NodeConfiguration& config);

    static BT::PortsList providedPorts() {
        return {
            BT::InputPort<std::string>("battery_topic",
                "/battery_state", "Topic for battery state"),
            BT::InputPort<double>("min_level",
                0.2, "Minimum battery fraction to proceed [0.0–1.0]"),
        };
    }

    BT::NodeStatus tick() override;

private:
    rclcpp::Node::SharedPtr node_;
    rclcpp::Subscription<sensor_msgs::msg::BatteryState>::SharedPtr sub_;
    sensor_msgs::msg::BatteryState::SharedPtr last_msg_;
};

}  // namespace custom_bt_plugin
```

```cpp
// src/check_battery_condition.cpp
#include "custom_bt_plugin/check_battery_condition.hpp"
#include "nav2_behavior_tree/plugins/condition/is_battery_low_condition.hpp"

namespace custom_bt_plugin {

CheckBatteryLevel::CheckBatteryLevel(
    const std::string& name, const BT::NodeConfiguration& config)
    : BT::ConditionNode(name, config)
{
    node_ = rclcpp::Node::make_shared("check_battery_bt_node");

    std::string topic;
    getInput("battery_topic", topic);

    sub_ = node_->create_subscription<sensor_msgs::msg::BatteryState>(
        topic, rclcpp::SensorDataQoS(),
        [this](sensor_msgs::msg::BatteryState::SharedPtr msg) {
            last_msg_ = msg;
        });
}

BT::NodeStatus CheckBatteryLevel::tick() {
    // Spin briefly to process any incoming battery message
    rclcpp::spin_some(node_);

    if (!last_msg_) {
        RCLCPP_WARN(node_->get_logger(),
                    "CheckBatteryLevel: No battery message received yet");
        return BT::NodeStatus::FAILURE;
    }

    double min_level = 0.2;
    getInput("min_level", min_level);

    if (last_msg_->percentage >= static_cast<float>(min_level)) {
        return BT::NodeStatus::SUCCESS;
    }

    RCLCPP_WARN(node_->get_logger(),
                "Battery low: %.1f%% < %.1f%% threshold",
                last_msg_->percentage * 100.0,
                min_level * 100.0);
    return BT::NodeStatus::FAILURE;
}

}  // namespace custom_bt_plugin

// ── Plugin Registration (REQUIRED) ────────────────────────────────────────────
#include "behaviortree_cpp_v3/bt_factory.h"
BT_REGISTER_NODES(factory) {
    factory.registerNodeType<custom_bt_plugin::CheckBatteryLevel>("CheckBatteryLevel");
}
```

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(custom_bt_plugin)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav2_behavior_tree REQUIRED)
find_package(nav2_core REQUIRED)

# Build as SHARED library — required for BT plugins
add_library(${PROJECT_NAME} SHARED
  src/check_battery_condition.cpp)

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

ament_target_dependencies(${PROJECT_NAME}
  rclcpp behaviortree_cpp_v3 sensor_msgs
  nav2_behavior_tree nav2_core)

install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

install(DIRECTORY include/ DESTINATION include/)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME}/)

ament_export_include_directories(include)
ament_export_libraries(${PROJECT_NAME})
ament_export_dependencies(
  rclcpp behaviortree_cpp_v3 sensor_msgs nav2_behavior_tree nav2_core)

ament_package()
```

## package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
  schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <n>custom_bt_plugin</n>
  <version>0.0.1</version>
  <description>Custom Nav2 BehaviorTree condition node</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
  <depend>behaviortree_cpp_v3</depend>
  <depend>sensor_msgs</depend>
  <depend>nav2_behavior_tree</depend>
  <depend>nav2_core</depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Register Plugin in Nav2 Params

```yaml
# nav2_params.yaml — add your plugin library to bt_navigator
bt_navigator:
  ros__parameters:
    plugin_lib_names:
      # ... existing plugins ...
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_follow_path_action_bt_node
      # Add your custom plugin:
      - custom_bt_plugin          # ← matches CMake project name
```

## Custom Behavior Tree XML

```xml
<!-- config/my_behavior_tree.xml -->
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <!-- Check battery before starting navigation -->
      <CheckBatteryLevel
        battery_topic="/battery_state"
        min_level="0.15"/>

      <!-- Normal navigation -->
      <ComputePathToPose
        goal="{goal}"
        path="{path}"
        planner_id="GridBased"/>
      <FollowPath
        path="{path}"
        controller_id="FollowPath"/>
    </Sequence>
  </BehaviorTree>
</root>
```

```yaml
# Point bt_navigator to your custom BT XML
bt_navigator:
  ros__parameters:
    default_nav_to_pose_bt_xml: "path/to/config/my_behavior_tree.xml"
```

## Build and Test

```bash
colcon build --packages-select custom_bt_plugin
source install/setup.bash

# Verify the library was built
ls install/custom_bt_plugin/lib/
# Should show: libcustom_bt_plugin.so

# Test with Nav2 running
ros2 launch nav2_bringup navigation_launch.py \
  params_file:=config/nav2_params.yaml

# Publish a fake battery at 50%
ros2 topic pub /battery_state sensor_msgs/msg/BatteryState \
  '{percentage: 0.5, present: true}' -r 1

# Navigate — the BT will check battery first
ros2 topic pub /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0}}}' --once
```
