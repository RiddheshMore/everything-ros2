# micro-ROS ESP32 Example

Complete micro-ROS setup for ESP32 with FreeRTOS, publishing IMU-style data
and subscribing to LED commands over serial transport.

## What This Demonstrates

- Correct static memory allocation (no heap in ROS callbacks)
- Publisher + subscriber in one node with shared executor
- `RCCHECK` / `RCSOFTCHECK` error handling pattern
- Reconnection loop when micro-ROS agent disconnects
- FreeRTOS task sizing for micro-ROS

## Arduino Framework Code (ESP32)

```cpp
// micro_ros_esp32_pubsub.ino
// Platform: ESP32 + Arduino framework
// micro-ROS library: micro_ros_arduino

#include <micro_ros_arduino.h>
#include <stdio.h>
#include <math.h>

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/bool.h>
#include <sensor_msgs/msg/imu.h>

// ── Error Macros ──────────────────────────────────────────────────────────────
// RCCHECK: hard fail — stop if critical init fails
#define RCCHECK(fn) {                                       \
  rcl_ret_t temp_rc = fn;                                   \
  if ((temp_rc != RCL_RET_OK)) {                            \
    Serial.printf("[ERROR] %s:%d rc=%d\n",                  \
                  __FILE__, __LINE__, (int)temp_rc);         \
    error_loop();                                           \
  }                                                         \
}

// RCSOFTCHECK: soft fail — log but continue (used in spin)
#define RCSOFTCHECK(fn) {                                   \
  rcl_ret_t temp_rc = fn;                                   \
  if ((temp_rc != RCL_RET_OK)) {                            \
    Serial.printf("[WARN]  %s:%d rc=%d\n",                  \
                  __FILE__, __LINE__, (int)temp_rc);         \
  }                                                         \
}

// ── ROS Entities ─────────────────────────────────────────────────────────────
rcl_publisher_t    imu_publisher;
rcl_subscription_t led_subscriber;
rclc_executor_t    executor;
rclc_support_t     support;
rcl_allocator_t    allocator;
rcl_node_t         node;
rcl_timer_t        imu_timer;

// ── Messages — STATIC allocation, never use dynamic strings/vectors ──────────
sensor_msgs__msg__Imu imu_msg;
std_msgs__msg__Bool   led_msg;

// ── State ────────────────────────────────────────────────────────────────────
bool led_state = false;
const int LED_PIN = 2;      // built-in LED on most ESP32 boards
float sim_angle = 0.0f;     // simulated rotation angle

// ── Error Handler ─────────────────────────────────────────────────────────────
void error_loop() {
  // Fast blink on error — do NOT call any ROS functions here
  while (true) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(50);
  }
}

// ── Timer Callback: publish IMU data ─────────────────────────────────────────
void imu_timer_callback(rcl_timer_t* timer, int64_t /*last_call_time*/) {
  if (timer == NULL) return;

  // Simulate IMU — replace with real MPU6050/ICM42688 reads
  sim_angle += 0.05f;

  // Stamp — use CLOCK_REALTIME from micro-ROS agent sync
  int64_t now_ns = rmw_uros_epoch_nanos();
  imu_msg.header.stamp.sec     = (int32_t)(now_ns / 1000000000LL);
  imu_msg.header.stamp.nanosec = (uint32_t)(now_ns % 1000000000LL);

  // Simulated orientation as quaternion (pure yaw rotation)
  imu_msg.orientation.x = 0.0;
  imu_msg.orientation.y = 0.0;
  imu_msg.orientation.z = sinf(sim_angle / 2.0f);
  imu_msg.orientation.w = cosf(sim_angle / 2.0f);

  // Angular velocity (rad/s)
  imu_msg.angular_velocity.x = 0.0;
  imu_msg.angular_velocity.y = 0.0;
  imu_msg.angular_velocity.z = 0.05f;

  // Linear acceleration (m/s^2) — gravity on Z
  imu_msg.linear_acceleration.x = 0.0;
  imu_msg.linear_acceleration.y = 0.0;
  imu_msg.linear_acceleration.z = 9.81;

  RCSOFTCHECK(rcl_publish(&imu_publisher, &imu_msg, NULL));
}

// ── Subscription Callback: receive LED command ────────────────────────────────
void led_subscription_callback(const void* msgin) {
  const std_msgs__msg__Bool* msg = (const std_msgs__msg__Bool*)msgin;
  led_state = msg->data;
  digitalWrite(LED_PIN, led_state ? HIGH : LOW);
  Serial.printf("[ROS] LED set to: %s\n", led_state ? "ON" : "OFF");
}

// ── Initialize ROS ────────────────────────────────────────────────────────────
bool init_ros() {
  allocator = rcl_get_default_allocator();

  // Create init options — serial transport
  rcl_init_options_t init_options = rcl_get_zero_initialized_init_options();
  RCCHECK(rcl_init_options_init(&init_options, allocator));

  if (rclc_support_init_with_options(&support, 0, NULL,
                                     &init_options, &allocator) != RCL_RET_OK) {
    return false;  // Agent not available yet
  }

  // Node
  RCCHECK(rclc_node_init_default(&node, "esp32_imu_node", "", &support));

  // Publisher: /imu/data (sensor_msgs/Imu) — 20 Hz
  RCCHECK(rclc_publisher_init_default(
    &imu_publisher, &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, Imu),
    "imu/data"));

  // Subscriber: /led_cmd (std_msgs/Bool)
  RCCHECK(rclc_subscription_init_default(
    &led_subscriber, &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Bool),
    "led_cmd"));

  // Timer: 50ms period = 20 Hz
  RCCHECK(rclc_timer_init_default(
    &imu_timer, &support,
    RCL_MS_TO_NS(50),
    imu_timer_callback));

  // Executor: 2 handles (1 timer + 1 subscriber)
  RCCHECK(rclc_executor_init(&executor, &support.context, 2, &allocator));
  RCCHECK(rclc_executor_add_timer(&executor, &imu_timer));
  RCCHECK(rclc_executor_add_subscription(&executor, &led_subscriber,
                                         &led_msg,
                                         &led_subscription_callback,
                                         ON_NEW_DATA));

  // Sync time with agent
  RCCHECK(rmw_uros_sync_session(1000));

  // Init IMU message header frame_id (static buffer!)
  static char frame_id_buf[32];
  strncpy(frame_id_buf, "imu_link", sizeof(frame_id_buf));
  imu_msg.header.frame_id.data     = frame_id_buf;
  imu_msg.header.frame_id.size     = strlen(frame_id_buf);
  imu_msg.header.frame_id.capacity = sizeof(frame_id_buf);

  return true;
}

// ── Teardown ROS (on disconnect) ──────────────────────────────────────────────
void destroy_ros() {
  rmw_context_t* rmw_context = rcl_context_get_rmw_context(&support.context);
  (void)rmw_uros_set_context_entity_destroy_session_timeout(rmw_context, 0);

  rcl_publisher_fini(&imu_publisher, &node);
  rcl_subscription_fini(&led_subscriber, &node);
  rcl_timer_fini(&imu_timer);
  rclc_executor_fini(&executor);
  rcl_node_fini(&node);
  rclc_support_fini(&support);
}

// ── Arduino Setup ─────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  // Use Serial transport to micro-ROS agent
  set_microros_serial_transports(Serial);

  Serial.println("[ESP32] micro-ROS node starting...");
}

// ── Arduino Loop — reconnection pattern ───────────────────────────────────────
enum class AgentState { WAITING, CONNECTED, ERROR };
AgentState agent_state = AgentState::WAITING;

void loop() {
  switch (agent_state) {

    case AgentState::WAITING:
      // Ping the agent every 500ms until available
      if (rmw_uros_ping_agent(500, 1) == RCL_RET_OK) {
        if (init_ros()) {
          agent_state = AgentState::CONNECTED;
          Serial.println("[ESP32] Connected to micro-ROS agent!");
        } else {
          agent_state = AgentState::ERROR;
        }
      }
      break;

    case AgentState::CONNECTED:
      // Spin executor — process one pending callback
      if (rmw_uros_ping_agent(100, 1) == RCL_RET_OK) {
        RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10)));
      } else {
        // Agent disconnected
        Serial.println("[ESP32] Agent disconnected — waiting for reconnect...");
        destroy_ros();
        agent_state = AgentState::WAITING;
      }
      break;

    case AgentState::ERROR:
      Serial.println("[ESP32] Init error — retrying in 2s...");
      delay(2000);
      agent_state = AgentState::WAITING;
      break;
  }
}
```

## Host Setup

```bash
# Install micro-ROS agent
pip install micro-ros-agent

# Or build from source for latest features
# See: https://micro.ros.org/docs/tutorials/core/first_application_linux/

# Start agent on the serial port the ESP32 is connected to
ros2 run micro_ros_agent micro_ros_agent serial \
  --dev /dev/ttyUSB0 \
  -b 115200 \
  -v4   # verbose level 4 shows connection events

# Flash ESP32 first, then verify node appears
ros2 node list
# Should show: /esp32_imu_node

# Check IMU topic
ros2 topic echo /imu/data

# Check publish rate
ros2 topic hz /imu/data
# Should be ~20 Hz

# Send LED command
ros2 topic pub /led_cmd std_msgs/msg/Bool '{data: true}' --once
ros2 topic pub /led_cmd std_msgs/msg/Bool '{data: false}' --once
```

## Arduino Library Dependencies

In `platformio.ini` or Arduino IDE:

```ini
; platformio.ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    https://github.com/micro-ROS/micro_ros_arduino
board_microros_transport = serial
board_microros_distro = humble   ; or jazzy
```

## Memory Budget (ESP32 with 520KB SRAM)

| Component | Usage |
|---|---|
| FreeRTOS kernel | ~10 KB |
| micro-ROS client | ~80 KB |
| DDS middleware | ~50 KB |
| Node + executor | ~20 KB |
| Message buffers | ~5 KB |
| Application | ~5 KB |
| **Total** | **~170 KB** |
| **Available** | **~350 KB remaining** |

> For ESP32-S3 (8MB PSRAM): much more headroom, can run multiple nodes.

## Troubleshooting

| Problem | Fix |
|---|---|
| Node doesn't appear in `ros2 node list` | Wrong `/dev/ttyUSB0` or baud rate mismatch |
| `RCCHECK` triggers immediately | Agent not running or wrong transport |
| IMU rate is wrong | Check timer period: `RCL_MS_TO_NS(50)` = 20 Hz |
| Reconnect loop | Normal — unplug/replug USB or restart agent |
| Stack overflow crash | Increase FreeRTOS task stack: `xTaskCreate(..., 16000, ...)` |
