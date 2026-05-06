# ROS 2 Debugging Guide

The essential CLI commands and diagnostic patterns for debugging ROS 2 systems.

---

## Node Diagnostics

```bash
# List all running nodes
ros2 node list

# Detailed info: topics, services, actions, parameters
ros2 node info /my_node

# Check if a node is alive
ros2 node list | grep my_node

# Kill a node (sends SIGTERM)
ros2 lifecycle set /my_node shutdown  # for lifecycle nodes
kill $(pgrep -f my_node_executable)   # nuclear option
```

---

## Topic Diagnostics

```bash
# List all topics
ros2 topic list

# List with types
ros2 topic list -t

# Show publishers and subscribers + their QoS
ros2 topic info /scan --verbose

# Echo messages (Ctrl+C to stop)
ros2 topic echo /scan
ros2 topic echo /scan --once          # one message
ros2 topic echo /scan --no-arr        # skip array fields for readability

# Check publish rate
ros2 topic hz /scan
ros2 topic hz /scan --window 10       # average over last 10 messages

# Check bandwidth
ros2 topic bw /camera/image_raw

# Publish a message from CLI
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}'

ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.0}, angular: {z: 0.0}}' --once  # stop command
```

---

## QoS Mismatch Debugging

```bash
# #1 cause of silent topic failure — check this first
ros2 topic info /map --verbose
# Look for: "Reliability: RELIABLE" vs "BEST_EFFORT"
# Publisher and subscriber must be compatible

# Check /rosout for QoS incompatibility messages
ros2 topic echo /rosout | grep -i "qos\|incompatible"

# If a subscriber isn't receiving: check topic info
ros2 topic info /my_topic
# Counts under "Subscription count" should be > 0
```

---

## TF2 Diagnostics

```bash
# View the full TF tree (generates /tmp/frames.pdf)
ros2 run tf2_tools view_frames
evince /tmp/frames.pdf  # or open frames.pdf

# Echo a specific transform
ros2 run tf2_ros tf2_echo map base_link

# Check if a transform exists (with timeout)
ros2 run tf2_ros tf2_echo odom base_link --timeout 5.0

# Static transforms currently published
ros2 topic echo /tf_static --once

# Check TF publication rate
ros2 topic hz /tf
```

---

## Parameter Diagnostics

```bash
# List all parameters of a node
ros2 param list /my_node

# Get a specific parameter value
ros2 param get /my_node max_speed

# Set a parameter at runtime
ros2 param set /my_node max_speed 2.0

# Dump all params (useful for creating a params.yaml)
ros2 param dump /my_node

# Load params from YAML
ros2 param load /my_node config/params.yaml

# Describe a parameter (type, range, description)
ros2 param describe /my_node max_speed
```

---

## Service Diagnostics

```bash
# List all services
ros2 service list

# List with types
ros2 service list -t

# Call a service (example: clear costmap)
ros2 service call /global_costmap/clear_entirely_global_costmap \
  nav2_msgs/srv/ClearEntireCostmap '{}'

# Call a custom service
ros2 service call /set_mode my_interfaces/srv/SetMode \
  '{mode: 1, description: "auto"}'

# Check if a service exists
ros2 service list | grep my_service
```

---

## Action Diagnostics

```bash
# List all action servers
ros2 action list

# List with types
ros2 action list -t

# Send a Nav2 goal from CLI
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  '{pose: {header: {frame_id: "map"}, pose: {position: {x: 1.0, y: 0.0}, \
  orientation: {w: 1.0}}}}'

# Watch action feedback
ros2 action send_goal --feedback /navigate_to_pose \
  nav2_msgs/action/NavigateToPose \
  '{pose: {header: {frame_id: "map"}, pose: {position: {x: 1.0}}}}'
```

---

## Lifecycle Node Diagnostics

```bash
# Get current state
ros2 lifecycle get /my_lifecycle_node
# Returns: unconfigured | inactive | active | finalized

# List all lifecycle nodes
ros2 lifecycle nodes

# Force state transitions
ros2 lifecycle set /my_lifecycle_node configure
ros2 lifecycle set /my_lifecycle_node activate
ros2 lifecycle set /my_lifecycle_node deactivate
ros2 lifecycle set /my_lifecycle_node cleanup
ros2 lifecycle set /my_lifecycle_node shutdown

# List available transitions from current state
ros2 lifecycle get /my_lifecycle_node  # shows available transitions
```

---

## Build & Workspace Diagnostics

```bash
# List all packages in workspace
colcon list

# Find what package provides a command
ros2 pkg executables | grep my_executable

# Check if a package is installed
ros2 pkg list | grep nav2_bringup

# Find package share directory
ros2 pkg prefix nav2_bringup
# → /opt/ros/humble

# Find a specific launch file
find $(ros2 pkg prefix nav2_bringup) -name "*.launch.py"

# Check package dependencies
ros2 pkg xml nav2_bringup | grep depend

# Verify node can be found before launching
ros2 pkg executables my_pkg
```

---

## Performance Profiling

```bash
# CPU usage per node (rough)
top -p $(pgrep -d, -f "ros2|my_node")

# Memory usage
ps aux | grep ros2

# Topic latency (time from publish to receipt)
ros2 topic delay /my_topic

# DDS traffic statistics (FastDDS)
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/profile.xml  # with stats enabled
ros2 run fastrtps_monitor monitor

# ROS 2 perf tool
ros2 run ros2perf ros2perf
```

---

## Common Error Messages and Fixes

| Error | Cause | Fix |
|---|---|---|
| `[WARN] [xxx]: Could not transform` | TF lookup failed | Start tf2 broadcaster, check frame names |
| `[ERROR] [xxx]: ParameterNotDeclaredException` | Getting undeclared param | `declare_parameter()` before `get_parameter()` |
| Topic rate = 0 Hz | QoS mismatch | `ros2 topic info --verbose`, fix durability/reliability |
| `package 'X' not found` | Not installed or not sourced | `apt install ros-<distro>-X` and `source setup.bash` |
| Node disappears from list | Crashed | Check stderr, look for segfault or uncaught exception |
| `[WARN] TF_REPEATED_DATA` | Publishing transforms too fast | Reduce TF publish rate to 50–100 Hz max |
| `LIFECYCLE_TRANSITION_FAILED` | on_configure returned FAILURE | Check hardware connection, parameters, and logs |
