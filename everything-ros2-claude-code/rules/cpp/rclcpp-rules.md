# ROS 2 C++ Rules (rclcpp)

## Node Structure

```cpp
// Always use this structure
#include "rclcpp/rclcpp.hpp"

class MyNode : public rclcpp::Node {
public:
    explicit MyNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
        : Node("my_node", options)  // snake_case node name, no leading slash
    {
        // Declare parameters FIRST
        declare_parameter("max_speed", 1.0);
        declare_parameter("frame_id", std::string("base_link"));

        // Create pub/sub after parameters
        pub_ = create_publisher<std_msgs::msg::String>("output", 10);
        sub_ = create_subscription<std_msgs::msg::String>(
            "input", 10,
            std::bind(&MyNode::topic_callback, this, std::placeholders::_1));

        timer_ = create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&MyNode::timer_callback, this));
    }

private:
    void topic_callback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(get_logger(), "Received: '%s'", msg->data.c_str());
    }

    void timer_callback() {
        auto msg = std_msgs::msg::String();
        msg.data = "Hello";
        pub_->publish(msg);
    }

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MyNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

## C++ Rules

### Always use `RCLCPP_INFO` — never `printf` or `std::cout`
```cpp
// WRONG
std::cout << "Speed: " << speed << std::endl;
printf("Error: %s\n", msg.c_str());

// CORRECT
RCLCPP_INFO(get_logger(), "Speed: %.2f", speed);
RCLCPP_ERROR(get_logger(), "Error: %s", msg.c_str());
RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 1000, "Throttled warning");
```

### Always use `SharedPtr` for message callbacks
```cpp
// WRONG — copies the whole message
void callback(const sensor_msgs::msg::LaserScan msg) { }

// CORRECT — shared ownership, no copy
void callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) { }

// BEST for composable nodes — unique ownership, zero-copy intra-process
void callback(sensor_msgs::msg::LaserScan::UniquePtr msg) { }
```

### Always declare parameters before getting them
```cpp
// WRONG — throws ParameterNotDeclaredException
double speed = get_parameter("speed").as_double();

// CORRECT
declare_parameter("speed", 1.0);
double speed = get_parameter("speed").as_double();
```

### Use `as_double()`, `as_string()`, etc. — not `.value()`
```cpp
double val = get_parameter("speed").as_double();
std::string s = get_parameter("name").as_string();
bool b = get_parameter("enabled").as_bool();
int64_t n = get_parameter("count").as_int();
```

### Use `rclcpp::Time` — never `std::chrono` for ROS timestamps
```cpp
// WRONG
auto now = std::chrono::system_clock::now();

// CORRECT
rclcpp::Time now = this->now();
auto stamp = now.to_msg();   // → builtin_interfaces::msg::Time
```

### Include guards use `#pragma once`
```cpp
#pragma once   // preferred over #ifndef guards in ROS 2 C++
#include "rclcpp/rclcpp.hpp"
```

### CMakeLists: use C++17 minimum
```cmake
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
```

### Never use `using namespace std;` in header files

### Naming Conventions
- Classes: `CamelCase`
- Member variables: `trailing_underscore_`
- Functions/methods: `snake_case`
- Constants: `kCamelCase` or `ALL_CAPS`
- Files: `snake_case.hpp`, `snake_case.cpp`

## Logger Severity Levels
```cpp
RCLCPP_DEBUG(get_logger(), "Debug: %s", data.c_str());   // verbose dev info
RCLCPP_INFO(get_logger(), "Info: %s", data.c_str());     // normal operation
RCLCPP_WARN(get_logger(), "Warn: %s", data.c_str());     // degraded but ok
RCLCPP_ERROR(get_logger(), "Error: %s", data.c_str());   // recoverable error
RCLCPP_FATAL(get_logger(), "Fatal: %s", data.c_str());   // unrecoverable
```
