---
name: executors-patterns
description: ROS 2 executor and callback group patterns — spin strategy, threading, deadlock prevention
triggers:
  - executor
  - MultiThreadedExecutor
  - SingleThreadedExecutor
  - callback group
  - ReentrantCallbackGroup
  - MutuallyExclusiveCallbackGroup
  - spin_once
  - deadlock
  - spin_until_future_complete
---

# Executors and Callback Groups

## Executor Selection Guide

```
Is real-time performance required?
  YES → StaticSingleThreadedExecutor (no dynamic allocation after spin start)
  NO  → Do any callbacks need to run concurrently?
          NO  → SingleThreadedExecutor (default, simple)
          YES → MultiThreadedExecutor (specify num_threads)
```

## SingleThreadedExecutor (Default)

```python
import rclpy
from rclpy.executors import SingleThreadedExecutor

def main():
    rclpy.init()
    node = MyNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
```

## MultiThreadedExecutor

```python
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup

class MyNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('my_node')

        # Reentrant: multiple callbacks from this group can run simultaneously
        self.reentrant_group = ReentrantCallbackGroup()

        # MutuallyExclusive: only one callback from this group at a time
        self.exclusive_group = MutuallyExclusiveCallbackGroup()

        # Fast sensor subscriber — can overlap with timer
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_cb, 10,
            callback_group=self.reentrant_group)

        # Slow planning timer — must not overlap with itself
        self.plan_timer = self.create_timer(
            1.0, self.plan_callback,
            callback_group=self.exclusive_group)

        # Service client callbacks — separate group to avoid deadlock
        self.service_group = MutuallyExclusiveCallbackGroup()
        self.client = self.create_client(
            MySrv, 'my_service',
            callback_group=self.service_group)

def main():
    rclpy.init()
    node = MyNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
```

## CRITICAL: Service Call Deadlock Prevention

```python
# DEADLOCK — calling a service from within the same executor thread
# that processes service responses — executor is blocked waiting for itself

# WRONG — in SingleThreadedExecutor
def timer_callback(self):
    future = self.client.call_async(request)
    rclpy.spin_until_future_complete(self, future)  # ← deadlock!

# CORRECT — use a separate callback group in MultiThreadedExecutor
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.cb_group = MutuallyExclusiveCallbackGroup()
        self.client = self.create_client(MySrv, 'my_service',
                                         callback_group=self.cb_group)
        self.timer = self.create_timer(1.0, self.timer_cb,
                                       callback_group=MutuallyExclusiveCallbackGroup())

    def timer_cb(self):
        future = self.client.call_async(MySrv.Request())
        # Don't block — add a done callback instead
        future.add_done_callback(self.service_response_cb)

    def service_response_cb(self, future):
        result = future.result()
        self.get_logger().info(f'Got result: {result}')
```

## C++ Executor Patterns

```cpp
// MultiThreadedExecutor with callback groups
#include "rclcpp/rclcpp.hpp"

class MyNode : public rclcpp::Node {
public:
    MyNode() : Node("my_node") {
        auto reentrant_group = create_callback_group(
            rclcpp::CallbackGroupType::Reentrant);
        auto exclusive_group = create_callback_group(
            rclcpp::CallbackGroupType::MutuallyExclusive);

        rclcpp::SubscriptionOptions sub_opts;
        sub_opts.callback_group = reentrant_group;
        scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
            "scan", rclcpp::SensorDataQoS(),
            std::bind(&MyNode::scan_cb, this, std::placeholders::_1),
            sub_opts);

        timer_ = create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&MyNode::timer_cb, this),
            exclusive_group);
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    void scan_cb(const sensor_msgs::msg::LaserScan::SharedPtr) {}
    void timer_cb() {}
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MyNode>();
    rclcpp::executors::MultiThreadedExecutor executor(
        rclcpp::ExecutorOptions(), 4);  // 4 threads
    executor.add_node(node);
    executor.spin();
    rclcpp::shutdown();
}
```

## Multiple Nodes in One Executor

```python
# Run multiple nodes in one process (efficient for composable nodes)
def main():
    rclpy.init()
    node1 = SensorNode()
    node2 = ProcessorNode()
    node3 = PublisherNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node1)
    executor.add_node(node2)
    executor.add_node(node3)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        for node in [node1, node2, node3]:
            node.destroy_node()
        rclpy.shutdown()
```

## spin_until_future_complete (Safe Pattern)

```python
# Safe usage: only in scripts/main(), not inside callbacks
def main():
    rclpy.init()
    node = rclpy.create_node('script_node')
    client = node.create_client(MySrv, 'my_service')
    client.wait_for_service(timeout_sec=5.0)

    req = MySrv.Request()
    future = client.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=10.0)

    if future.done():
        result = future.result()
    node.destroy_node()
    rclpy.shutdown()
```

## StaticSingleThreadedExecutor (Real-Time)

```cpp
// Best for real-time: no dynamic allocation after spin() starts
rclcpp::executors::StaticSingleThreadedExecutor executor;
executor.add_node(node);
executor.spin();  // all callbacks pre-allocated
```

## Callback Group Rules

| Scenario | Use |
|---|---|
| Timer + fast subscriber, can overlap | `ReentrantCallbackGroup` |
| Service server — must not reenter | `MutuallyExclusiveCallbackGroup` |
| Service client call in timer | Separate `MutuallyExclusiveCallbackGroup` per type |
| Action server | `MutuallyExclusiveCallbackGroup` |
| Multiple independent subscribers | Same `ReentrantCallbackGroup` |
| Default (no group specified) | `MutuallyExclusiveCallbackGroup` (all in one) |
