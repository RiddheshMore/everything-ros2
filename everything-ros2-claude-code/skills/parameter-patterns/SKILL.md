---
name: parameter-patterns
description: ROS 2 parameter system patterns — declaration, getting, setting, callbacks, YAML
triggers:
  - parameter
  - declare_parameter
  - get_parameter
  - set_parameter
  - parameter callback
  - params.yaml
  - generate_parameter_library
---

# ROS 2 Parameter Patterns

## Basic Parameter Usage (Python)

```python
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')

        # Declare ALL parameters before getting them
        self.declare_parameter('robot_name', 'my_robot')
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('sensor_enabled', True)
        self.declare_parameter('waypoints', [0.0, 1.0, 2.0])  # list param
        self.declare_parameter('frame_id', 'base_link')

        # Read values
        self.robot_name = self.get_parameter('robot_name') \
                              .get_parameter_value().string_value
        self.max_speed  = self.get_parameter('max_speed') \
                              .get_parameter_value().double_value
        self.enabled    = self.get_parameter('sensor_enabled') \
                              .get_parameter_value().bool_value
        self.waypoints  = self.get_parameter('waypoints') \
                              .get_parameter_value().double_array_value

        self.get_logger().info(f'Robot: {self.robot_name}, max_speed: {self.max_speed}')
```

## Parameter Type Reference

```python
# Getter methods per type
.get_parameter_value().bool_value         # bool
.get_parameter_value().integer_value      # int64
.get_parameter_value().double_value       # float64
.get_parameter_value().string_value       # string
.get_parameter_value().byte_array_value   # List[int]
.get_parameter_value().bool_array_value   # List[bool]
.get_parameter_value().integer_array_value # List[int64]
.get_parameter_value().double_array_value # List[float64]
.get_parameter_value().string_array_value # List[str]
```

## Parameter Change Callback (Python)

```python
from rcl_interfaces.msg import SetParametersResult

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.declare_parameter('max_speed', 1.0)

        # Register callback — called when any parameter changes
        self.add_on_set_parameters_callback(self._param_callback)

    def _param_callback(self, params):
        for param in params:
            if param.name == 'max_speed':
                if param.value < 0.0 or param.value > 5.0:
                    return SetParametersResult(
                        successful=False,
                        reason='max_speed must be in [0.0, 5.0]'
                    )
                self.max_speed = param.value
                self.get_logger().info(f'max_speed updated to {param.value}')
        return SetParametersResult(successful=True)
```

## Parameter Change Callback (C++)

```cpp
#include "rcl_interfaces/msg/set_parameters_result.hpp"

class MyNode : public rclcpp::Node {
public:
    MyNode() : Node("my_node") {
        declare_parameter("max_speed", 1.0);

        // Register callback
        param_callback_handle_ = add_on_set_parameters_callback(
            [this](const std::vector<rclcpp::Parameter>& params) {
                rcl_interfaces::msg::SetParametersResult result;
                result.successful = true;
                for (const auto& param : params) {
                    if (param.get_name() == "max_speed") {
                        if (param.as_double() < 0.0 || param.as_double() > 5.0) {
                            result.successful = false;
                            result.reason = "max_speed must be in [0.0, 5.0]";
                            return result;
                        }
                        max_speed_ = param.as_double();
                    }
                }
                return result;
            });
    }

private:
    double max_speed_{1.0};
    rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr param_callback_handle_;
};
```

## params.yaml Structure

```yaml
# config/params.yaml
# Must match the node's name or namespace/name

my_node:
  ros__parameters:                 # ← required key in ROS 2
    robot_name: "my_robot"
    max_speed: 1.5
    sensor_enabled: true
    waypoints: [0.0, 1.0, 2.0, 3.0]
    frame_id: "base_link"

# For namespaced node: /robot1/my_node
robot1:
  my_node:
    ros__parameters:
      robot_name: "robot1"
```

```python
# Load in launch file
from ament_python.packages import get_package_share_directory
import os

config = os.path.join(get_package_share_directory('my_pkg'), 'config', 'params.yaml')

Node(
    package='my_pkg',
    executable='my_node',
    parameters=[config],
)
```

## generate_parameter_library (Type-Safe Params, Humble+)

```yaml
# config/my_node_params.yaml — schema definition
my_node:
  max_speed:
    type: double
    default_value: 1.0
    min_value: 0.0
    max_value: 5.0
    description: "Maximum robot speed in m/s"
  robot_name:
    type: string
    default_value: "my_robot"
    description: "Robot identifier"
  sensor_enabled:
    type: bool
    default_value: true
```

```cmake
# CMakeLists.txt
find_package(generate_parameter_library REQUIRED)
generate_parameter_library(my_node_parameters config/my_node_params.yaml)
target_link_libraries(my_node my_node_parameters)
```

```cpp
// Usage — type-safe, auto-updating
#include "my_pkg/my_node_parameters.hpp"

class MyNode : public rclcpp::Node {
    MyNode() : Node("my_node") {
        param_listener_ = std::make_shared<my_node::ParamListener>(
            get_node_parameters_interface());
        params_ = param_listener_->get_params();

        // Access type-safely
        double speed = params_.max_speed;
        std::string name = params_.robot_name;
    }
    std::shared_ptr<my_node::ParamListener> param_listener_;
    my_node::Params params_;
};
```

## Async Parameter Client (Python)

```python
from rclpy.parameter import Parameter
from rcl_interfaces.msg import Parameter as ParameterMsg

# Set parameters on another node
param_client = self.create_client(SetParameters, '/other_node/set_parameters')
param_client.wait_for_service()

req = SetParameters.Request()
req.parameters = [
    Parameter(name='speed', value=2.0).to_parameter_msg()
]
future = param_client.call_async(req)
```

## CLI Commands

```bash
# List all parameters of a node
ros2 param list /my_node

# Get a specific parameter
ros2 param get /my_node max_speed

# Set a parameter at runtime
ros2 param set /my_node max_speed 2.0

# Dump all params to YAML
ros2 param dump /my_node

# Load params from file
ros2 param load /my_node config/params.yaml
```
