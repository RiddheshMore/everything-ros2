# Lifecycle Sensor Driver Example

A complete lifecycle node implementing a sensor driver — the recommended pattern
for any hardware driver in ROS 2.

## File Structure

```
lifecycle_sensor_driver/
├── package.xml
├── CMakeLists.txt
├── include/lifecycle_sensor_driver/
│   └── lidar_driver_node.hpp
├── src/
│   └── lidar_driver_node.cpp
├── launch/
│   └── lidar_driver.launch.py
└── config/
    └── lidar_params.yaml
```

## package.xml

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
  schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <n>lifecycle_sensor_driver</n>
  <version>0.0.1</version>
  <description>Lifecycle node pattern for sensor drivers</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>rclcpp_lifecycle</depend>
  <depend>sensor_msgs</depend>
  <depend>std_msgs</depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(lifecycle_sensor_driver)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(lidar_driver_node src/lidar_driver_node.cpp)
ament_target_dependencies(lidar_driver_node
  rclcpp rclcpp_lifecycle sensor_msgs std_msgs)

install(TARGETS lidar_driver_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}/)

ament_package()
```

## include/lifecycle_sensor_driver/lidar_driver_node.hpp

```cpp
#pragma once
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

namespace lifecycle_sensor_driver {

using CallbackReturn =
    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class LidarDriverNode : public rclcpp_lifecycle::LifecycleNode {
public:
    explicit LidarDriverNode(
        const rclcpp::NodeOptions& options = rclcpp::NodeOptions());

    // Lifecycle callbacks
    CallbackReturn on_configure(const rclcpp_lifecycle::State& state) override;
    CallbackReturn on_activate(const rclcpp_lifecycle::State& state) override;
    CallbackReturn on_deactivate(const rclcpp_lifecycle::State& state) override;
    CallbackReturn on_cleanup(const rclcpp_lifecycle::State& state) override;
    CallbackReturn on_shutdown(const rclcpp_lifecycle::State& state) override;

private:
    void publish_scan();
    bool connect_to_hardware();
    void disconnect_from_hardware();

    // Publisher — LifecyclePublisher auto-activates/deactivates with node state
    rclcpp_lifecycle::LifecyclePublisher<sensor_msgs::msg::LaserScan>::SharedPtr scan_pub_;
    rclcpp::TimerBase::SharedPtr publish_timer_;

    // Parameters (read in on_configure)
    std::string frame_id_{"laser_link"};
    std::string device_port_{"/dev/ttyUSB0"};
    double scan_frequency_{10.0};
    double angle_min_{-M_PI};
    double angle_max_{M_PI};
    int num_readings_{360};

    bool hardware_connected_{false};
};

}  // namespace lifecycle_sensor_driver
```

## src/lidar_driver_node.cpp

```cpp
#include "lifecycle_sensor_driver/lidar_driver_node.hpp"
#include <chrono>
#include <random>

namespace lifecycle_sensor_driver {

LidarDriverNode::LidarDriverNode(const rclcpp::NodeOptions& options)
    : LifecycleNode("lidar_driver_node", options)
{
    // Declare ALL parameters in constructor — safe before any state transition
    declare_parameter("frame_id",      std::string("laser_link"));
    declare_parameter("device_port",   std::string("/dev/ttyUSB0"));
    declare_parameter("scan_frequency", 10.0);
    declare_parameter("angle_min",     -M_PI);
    declare_parameter("angle_max",      M_PI);
    declare_parameter("num_readings",   360);

    RCLCPP_INFO(get_logger(), "LidarDriverNode constructed");
}

// ── on_configure: allocate resources, open hardware connection ─────────────
CallbackReturn LidarDriverNode::on_configure(const rclcpp_lifecycle::State&) {
    RCLCPP_INFO(get_logger(), "Configuring...");

    // Read parameters
    frame_id_      = get_parameter("frame_id").as_string();
    device_port_   = get_parameter("device_port").as_string();
    scan_frequency_ = get_parameter("scan_frequency").as_double();
    angle_min_     = get_parameter("angle_min").as_double();
    angle_max_     = get_parameter("angle_max").as_double();
    num_readings_  = static_cast<int>(get_parameter("num_readings").as_int());

    // Create lifecycle publisher (inactive until on_activate)
    scan_pub_ = create_lifecycle_publisher<sensor_msgs::msg::LaserScan>("scan", 10);

    // Connect to hardware
    if (!connect_to_hardware()) {
        RCLCPP_ERROR(get_logger(), "Failed to connect to LiDAR on %s",
                     device_port_.c_str());
        return CallbackReturn::FAILURE;  // → stays UNCONFIGURED
    }

    RCLCPP_INFO(get_logger(), "Configured. frame_id=%s, port=%s",
                frame_id_.c_str(), device_port_.c_str());
    return CallbackReturn::SUCCESS;
}

// ── on_activate: start timers, begin publishing ────────────────────────────
CallbackReturn LidarDriverNode::on_activate(const rclcpp_lifecycle::State& state) {
    RCLCPP_INFO(get_logger(), "Activating...");

    // IMPORTANT: call super first to activate lifecycle publishers
    LifecycleNode::on_activate(state);

    auto period = std::chrono::duration<double>(1.0 / scan_frequency_);
    publish_timer_ = create_wall_timer(period,
        std::bind(&LidarDriverNode::publish_scan, this));

    RCLCPP_INFO(get_logger(), "Active — publishing /scan at %.1f Hz", scan_frequency_);
    return CallbackReturn::SUCCESS;
}

// ── on_deactivate: stop timers, stop publishing ────────────────────────────
CallbackReturn LidarDriverNode::on_deactivate(const rclcpp_lifecycle::State& state) {
    RCLCPP_INFO(get_logger(), "Deactivating...");

    publish_timer_.reset();

    // Call super to deactivate lifecycle publishers
    LifecycleNode::on_deactivate(state);

    return CallbackReturn::SUCCESS;
}

// ── on_cleanup: release resources, disconnect hardware ─────────────────────
CallbackReturn LidarDriverNode::on_cleanup(const rclcpp_lifecycle::State&) {
    RCLCPP_INFO(get_logger(), "Cleaning up...");

    disconnect_from_hardware();
    scan_pub_.reset();

    return CallbackReturn::SUCCESS;
}

// ── on_shutdown: final cleanup ──────────────────────────────────────────────
CallbackReturn LidarDriverNode::on_shutdown(const rclcpp_lifecycle::State&) {
    RCLCPP_INFO(get_logger(), "Shutting down...");

    publish_timer_.reset();
    disconnect_from_hardware();
    scan_pub_.reset();

    return CallbackReturn::SUCCESS;
}

void LidarDriverNode::publish_scan() {
    if (!scan_pub_ || !scan_pub_->is_activated()) return;

    // Build a LaserScan message (replace with real hardware reads)
    auto msg = sensor_msgs::msg::LaserScan();
    msg.header.stamp    = now();
    msg.header.frame_id = frame_id_;
    msg.angle_min       = static_cast<float>(angle_min_);
    msg.angle_max       = static_cast<float>(angle_max_);
    msg.angle_increment = static_cast<float>((angle_max_ - angle_min_) / num_readings_);
    msg.time_increment  = 0.0f;
    msg.scan_time       = static_cast<float>(1.0 / scan_frequency_);
    msg.range_min       = 0.15f;
    msg.range_max       = 12.0f;
    msg.ranges.resize(num_readings_, 1.0f);  // placeholder — replace with hardware data
    msg.intensities.resize(num_readings_, 100.0f);

    scan_pub_->publish(msg);
}

bool LidarDriverNode::connect_to_hardware() {
    RCLCPP_INFO(get_logger(), "Connecting to hardware on %s...", device_port_.c_str());
    // Replace with real serial/USB connection code
    hardware_connected_ = true;
    return true;
}

void LidarDriverNode::disconnect_from_hardware() {
    if (hardware_connected_) {
        RCLCPP_INFO(get_logger(), "Disconnecting from hardware...");
        hardware_connected_ = false;
    }
}

}  // namespace lifecycle_sensor_driver

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<lifecycle_sensor_driver::LidarDriverNode>();
    rclcpp::spin(node->get_node_base_interface());
    rclcpp::shutdown();
    return 0;
}
```

## launch/lidar_driver.launch.py

```python
import os
from ament_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('lifecycle_sensor_driver'),
        'config', 'lidar_params.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    lidar_driver = LifecycleNode(
        package='lifecycle_sensor_driver',
        executable='lidar_driver_node',
        name='lidar_driver_node',
        namespace='',
        output='screen',
        parameters=[config, {'use_sim_time': use_sim_time}],
    )

    # Automatically configure and activate the lifecycle node
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_sensor',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['lidar_driver_node'],
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        lidar_driver,
        lifecycle_manager,
    ])
```

## config/lidar_params.yaml

```yaml
lidar_driver_node:
  ros__parameters:
    frame_id: "laser_link"
    device_port: "/dev/ttyUSB0"
    scan_frequency: 10.0
    angle_min: -3.14159
    angle_max:  3.14159
    num_readings: 360
```

## Build and Run

```bash
colcon build --packages-select lifecycle_sensor_driver --symlink-install
source install/setup.bash

# With lifecycle manager (auto-configures and activates)
ros2 launch lifecycle_sensor_driver lidar_driver.launch.py

# Manual control (no lifecycle manager)
ros2 run lifecycle_sensor_driver lidar_driver_node
ros2 lifecycle set /lidar_driver_node configure
ros2 lifecycle set /lidar_driver_node activate
ros2 topic echo /scan
ros2 lifecycle set /lidar_driver_node deactivate
ros2 lifecycle set /lidar_driver_node cleanup
```
