---
name: composable-nodes
description: ROS 2 composable nodes and intra-process communication for zero-copy pipelines
triggers:
  - composable
  - component
  - intra-process
  - ComponentManager
  - ComposableNode
  - rclcpp_components
  - zero-copy
  - NodeOptions
---

# Composable Nodes (Components)

## Why Composable Nodes?

- **Zero-copy intra-process**: publish a `std::unique_ptr` instead of copying the message
- **Reduced overhead**: skip serialization/deserialization between nodes in same process
- **Flexible deployment**: run as separate processes in debug, compose for production
- **Camera pipelines, sensor fusion** — the primary use case

## Creating a Composable Node (C++)

```cpp
// my_composable_node.hpp
#pragma once
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"

namespace my_pkg {

class MyComposableNode : public rclcpp::Node {
public:
    // Constructor MUST take NodeOptions — this is what makes it composable
    explicit MyComposableNode(const rclcpp::NodeOptions& options);

private:
    void image_callback(sensor_msgs::msg::Image::UniquePtr msg);
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_;
};

}  // namespace my_pkg
```

```cpp
// my_composable_node.cpp
#include "my_pkg/my_composable_node.hpp"
#include "rclcpp_components/register_node_macro.hpp"

namespace my_pkg {

MyComposableNode::MyComposableNode(const rclcpp::NodeOptions& options)
    : Node("my_composable_node", options)
{
    // Enable intra-process communication for this node
    // (also set in NodeOptions from launch file)
    auto qos = rclcpp::QoS(10);

    sub_ = create_subscription<sensor_msgs::msg::Image>(
        "image_raw", qos,
        // Use UniquePtr for zero-copy intra-process
        [this](sensor_msgs::msg::Image::UniquePtr msg) {
            image_callback(std::move(msg));
        });

    pub_ = create_publisher<sensor_msgs::msg::Image>("image_processed", qos);
}

void MyComposableNode::image_callback(sensor_msgs::msg::Image::UniquePtr msg) {
    // Process the image (msg is owned here — no copy if intra-process)
    // Publish as unique_ptr for zero-copy to next composable node
    pub_->publish(std::move(msg));
}

}  // namespace my_pkg

// Register this as a component — required for composition
RCLCPP_COMPONENTS_REGISTER_NODE(my_pkg::MyComposableNode)
```

## CMakeLists.txt for Components

```cmake
find_package(rclcpp_components REQUIRED)

# Build as a shared library (NOT an executable!)
add_library(my_composable_node SHARED src/my_composable_node.cpp)
ament_target_dependencies(my_composable_node
  rclcpp rclcpp_components sensor_msgs)

# Register the component
rclcpp_components_register_nodes(my_composable_node
  "my_pkg::MyComposableNode")

# Also build a standalone executable for debugging
add_executable(my_composable_node_exe src/main.cpp)
target_link_libraries(my_composable_node_exe my_composable_node)

install(TARGETS my_composable_node my_composable_node_exe
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
```

## package.xml for Components

```xml
<depend>rclcpp</depend>
<depend>rclcpp_components</depend>
<depend>sensor_msgs</depend>
```

## Launch: Composing Multiple Nodes in One Container

```python
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    container = ComposableNodeContainer(
        name='image_pipeline_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            ComposableNode(
                package='my_pkg',
                plugin='my_pkg::CameraDriverNode',
                name='camera_driver',
                parameters=[{'frame_id': 'camera_link'}],
                extra_arguments=[{'use_intra_process_comms': True}],
            ),
            ComposableNode(
                package='my_pkg',
                plugin='my_pkg::ImageProcessorNode',
                name='image_processor',
                extra_arguments=[{'use_intra_process_comms': True}],
            ),
            ComposableNode(
                package='my_pkg',
                plugin='my_pkg::ImagePublisherNode',
                name='image_publisher',
                extra_arguments=[{'use_intra_process_comms': True}],
            ),
        ],
        output='screen',
    )

    return LaunchDescription([container])
```

## Intra-Process Zero-Copy Rules

For zero-copy to work between two composable nodes:
1. Both nodes must be in the **same container** process
2. Both must have `use_intra_process_comms: True`
3. Publisher must publish `std::unique_ptr<MsgT>`, **not** a copy
4. Subscriber callback must accept `MsgT::UniquePtr`
5. QoS history must be `KEEP_LAST` (not `KEEP_ALL`)

```cpp
// Zero-copy publish — transfers ownership, no copy
auto msg = std::make_unique<sensor_msgs::msg::Image>();
// ... fill message ...
pub_->publish(std::move(msg));  // ← std::move, not msg directly
```

## Loading Components at Runtime (CLI)

```bash
# Start a component manager
ros2 run rclcpp_components component_container

# Load a component into the running manager
ros2 component load /ComponentManager my_pkg my_pkg::MyComposableNode

# List loaded components
ros2 component list

# Unload a component
ros2 component unload /ComponentManager 1
```

## Standalone Executable (for Debugging)

```cpp
// main.cpp — run as regular node for debugging
#include "my_pkg/my_composable_node.hpp"
int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::NodeOptions options;
    auto node = std::make_shared<my_pkg::MyComposableNode>(options);
    rclcpp::spin(node);
    rclcpp::shutdown();
}
```
