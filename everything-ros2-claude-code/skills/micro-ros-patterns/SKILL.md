---
name: micro-ros-patterns
description: micro-ROS for embedded systems — ESP32, STM32, Raspberry Pi Pico, FreeRTOS, Zephyr
triggers:
  - micro-ros
  - microros
  - micro_ros
  - ESP32
  - STM32
  - embedded ros
  - FreeRTOS
  - RTOS
  - microcontroller
---

# micro-ROS Patterns

## Architecture Overview

```
┌──────────────────────┐        Serial/UDP/USB       ┌───────────────────┐
│  Microcontroller     │ ◄──────────────────────────► │  micro-ROS Agent  │
│  (ESP32/STM32/Pico)  │                              │  (on host PC/RPi) │
│                      │                              │                   │
│  micro-ROS client    │                              │  Bridges to ROS 2 │
│  FreeRTOS/Zephyr     │                              │  DDS network      │
└──────────────────────┘                              └───────────────────┘
```

## Host: Start micro-ROS Agent

```bash
# Install micro-ROS agent
pip install micro-ros-agent   # or build from source

# Serial transport (most common for ESP32/STM32)
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200

# UDP transport (ESP32 over WiFi)
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888

# USB transport (RP2040 / Pico)
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyACM0
```

## ESP32 — Publisher (Arduino / ESP-IDF)

```cpp
// ESP32 + FreeRTOS + micro-ROS (Arduino framework)
#include <micro_ros_arduino.h>
#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int32.h>

// Error checking macros — always use these
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; \
  if ((temp_rc != RCL_RET_OK)) { error_loop(); } }
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; \
  if ((temp_rc != RCL_RET_OK)) {} }

rcl_publisher_t publisher;
std_msgs__msg__Int32 msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rcl_timer_t timer;

void error_loop() {
    while (1) {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        delay(100);
    }
}

void timer_callback(rcl_timer_t* timer, int64_t last_call_time) {
    RCLC_UNUSED(last_call_time);
    if (timer != NULL) {
        RCSOFTCHECK(rcl_publish(&publisher, &msg, NULL));
        msg.data++;
    }
}

void setup() {
    // Set up micro-ROS transport (Serial)
    set_microros_transports();

    delay(2000);  // Wait for agent to be ready

    allocator = rcl_get_default_allocator();

    // Create init options and support
    RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

    // Create node
    RCCHECK(rclc_node_init_default(&node, "micro_ros_esp32_node", "", &support));

    // Create publisher
    RCCHECK(rclc_publisher_init_default(
        &publisher,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
        "micro_ros_esp32_topic"));

    // Create timer (500ms period)
    const unsigned int timer_timeout = 500;
    RCCHECK(rclc_timer_init_default(&timer, &support,
        RCL_MS_TO_NS(timer_timeout), timer_callback));

    // Create executor — number = total callbacks (timer + subscribers)
    RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
    RCCHECK(rclc_executor_add_timer(&executor, &timer));

    msg.data = 0;
}

void loop() {
    delay(100);
    RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
}
```

## ESP32 — Subscriber

```cpp
#include <micro_ros_arduino.h>
#include <std_msgs/msg/string.h>

rcl_subscription_t subscriber;
std_msgs__msg__String recv_msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

// Static buffer for string data — NO heap allocation
char string_buffer[64];

void subscription_callback(const void* msgin) {
    const std_msgs__msg__String* msg = (const std_msgs__msg__String*)msgin;
    // Use msg->data.data (char*) and msg->data.size (size_t)
    Serial.print("Received: ");
    Serial.println(msg->data.data);
}

void setup() {
    Serial.begin(115200);
    set_microros_transports();
    delay(2000);

    allocator = rcl_get_default_allocator();
    RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
    RCCHECK(rclc_node_init_default(&node, "micro_sub_node", "", &support));

    RCCHECK(rclc_subscription_init_default(
        &subscriber, &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),
        "micro_cmd_topic"));

    // Init string with static buffer — NEVER use dynamic allocation
    recv_msg.data.data = string_buffer;
    recv_msg.data.capacity = sizeof(string_buffer);
    recv_msg.data.size = 0;

    RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
    RCCHECK(rclc_executor_add_subscription(&executor, &subscriber,
        &recv_msg, &subscription_callback, ON_NEW_DATA));
}

void loop() {
    RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
    delay(100);
}
```

## Memory Rules for Embedded

```cpp
// RULE 1: NEVER use std::string or std::vector in micro-ROS callbacks
// RULE 2: Declare ALL message buffers as static/global — no stack allocation in callbacks
// RULE 3: Use rosidl_runtime_c__String with static char arrays
// RULE 4: Set .capacity before any string operation
// RULE 5: Use RCCHECK not raw function calls — agent disconnect causes RCL_RET_ERROR

// WRONG
void callback(const void* msg) {
    std::string s = "hello";  // ← heap allocation — may crash on low-RAM MCU
}

// CORRECT
static char static_buf[64];
void callback(const void* msg) {
    strncpy(static_buf, "hello", sizeof(static_buf));
}
```

## FreeRTOS Task Pattern

```cpp
// Dedicated FreeRTOS task for micro-ROS
void micro_ros_task(void* arg) {
    rcl_allocator_t allocator = rcl_get_default_allocator();
    rclc_support_t support;
    rcl_node_t node;
    rclc_executor_t executor;
    rcl_publisher_t publisher;
    std_msgs__msg__Float32 msg;

    rclc_support_init(&support, 0, NULL, &allocator);
    rclc_node_init_default(&node, "freertos_node", "", &support);
    rclc_publisher_init_default(&publisher, &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32), "sensor_value");

    rclc_executor_init(&executor, &support.context, 0, &allocator);

    for (;;) {
        msg.data = read_sensor();
        rcl_publish(&publisher, &msg, NULL);
        vTaskDelay(pdMS_TO_TICKS(100));  // 10 Hz
    }
}

// In app_main() / setup():
xTaskCreate(micro_ros_task, "micro_ros_task",
    16000,    // Stack size in words — 16KB minimum for micro-ROS
    NULL, 5, NULL);
```

## Limitations vs Full ROS 2

| Feature | micro-ROS | Notes |
|---|---|---|
| Topics | ✅ | Publish + subscribe |
| Services | ✅ | Limited concurrency |
| Actions | ✅ | Since micro-ROS Humble |
| Parameters | ⚠️ | Limited, no callbacks |
| Lifecycle nodes | ❌ | Not supported |
| TF2 | ⚠️ | Publish only, no lookups |
| Dynamic types | ❌ | Types fixed at compile time |
| Logging (RCUTILS) | ✅ | Severity levels |
| Clock (ROS time) | ✅ | Agent time sync |

## Troubleshooting

```bash
# No connection: check baud rate matches firmware
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200 -v6

# Check if agent sees the node
ros2 node list  # should show /micro_ros_esp32_node

# Check topic
ros2 topic echo /micro_ros_esp32_topic

# If node disappears: MCU restarted or serial buffer overflow
# Increase serial buffer in firmware or reduce publish rate
```
