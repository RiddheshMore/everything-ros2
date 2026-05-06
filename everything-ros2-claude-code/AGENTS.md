# AGENTS.md — ROS 2 Sub-Agent Reference

This file is auto-detected by Claude Code, Cursor, Codex, and OpenCode.
It defines the specialist sub-agents available for ROS 2 development.

## Orchestrator

### ros2-orchestrator
Routes any ROS 2 task to the appropriate specialist agent.
Invoked automatically for any ROS 2 development task.
Merges outputs from multiple agents into a coherent response.

**Delegates to:**
- `@urdf-validator` for any `.urdf` or `.xacro` file
- `@topic-schema-agent` for any topic/service/action naming question
- `@distro-compat-agent` when target distro is mentioned or API version matters
- `@package-structure-agent` for `package.xml` or `CMakeLists.txt`
- `@tf2-agent` for frame transforms or TF2 lookups
- `@launch-agent` for `.launch.py` files
- `@qos-agent` when creating publishers or subscribers
- `@interface-agent` for `.msg`, `.srv`, `.action` files
- `@nav2-agent` for navigation, path planning, costmaps
- `@moveit2-agent` for MoveIt2, motion planning, robot arms
- `@lifecycle-agent` for lifecycle nodes and managed states
- `@colcon-agent` for build failures or `colcon build` issues
- `@executor-agent` for executor configuration and callback groups
- `@micro-ros-agent` for micro-ROS on embedded systems

---

## Specialist Agents

### urdf-validator
**When to use:** Any task involving URDF or XACRO files.
**Tools:** Read, Bash, Grep
**Checks:**
- All `<link>` names referenced in `<joint>` tags exist
- Inertia matrices are valid (positive definite)
- Mesh file paths exist on disk
- No duplicate link or joint names
- `<robot>` name attribute is set
- XACRO macros resolve without undefined args
- Visual and collision geometries are present

### topic-schema-agent
**When to use:** Creating publishers, subscribers, services, actions, or naming anything in ROS 2.
**Tools:** Read, Grep, Bash
**Enforces:**
- Topic names: `snake_case`, start with `/`, no double slashes
- Node names: `snake_case`, no leading slash
- Namespace convention: `/<robot_name>/<subsystem>/<topic>`
- Standard topic names used (e.g. `/scan`, `/cmd_vel`, `/odom`, `/tf`, `/tf_static`)
- Service naming: `snake_case` with verb (e.g. `set_mode`, `get_state`)
- Action naming: verb_noun pattern (e.g. `navigate_to_pose`, `follow_path`)

### distro-compat-agent
**When to use:** Any code that needs to run on a specific ROS 2 distribution.
**Tools:** Read, Grep, WebSearch
**Knows:**
- Humble (LTS, EOL 2027): baseline API
- Iron (EOL 2024): type_description, service introspection
- Jazzy (LTS, EOL 2029): new executor API, improved QoS
- Kilted (May 2025): latest stable
- Rolling: bleeding edge, may be unstable
**Checks:**
- `#ifdef` or conditional imports for distro-specific APIs
- Deprecated API usage
- Build flag requirements per distro

### package-structure-agent
**When to use:** Creating or editing `package.xml`, `CMakeLists.txt`, or `setup.py`.
**Tools:** Read, Bash
**Validates:**
- `package.xml` format version (use format 3)
- All imported C++ headers have `<depend>` entries
- All Python imports have `<exec_depend>` entries
- `ament_cmake` vs `ament_python` vs `ament_cmake_python` used correctly
- `install()` rules cover all nodes, launch files, and config files
- `ament_export_*` calls for library packages
- `package.xml` `<build_export_depend>` for interface packages

### tf2-agent
**When to use:** Any TF2 broadcast, lookup, or frame ID usage.
**Tools:** Read, Grep
**Validates:**
- `base_link` → `odom` → `map` chain exists
- Static transforms declared in launch or broadcaster node
- `lookup_transform` calls have timeout set
- Frame IDs are parameterizable, not hardcoded
- `TransformBroadcaster` and `StaticTransformBroadcaster` used correctly
- No TF loops (parent-child cycles)

### launch-agent
**When to use:** Creating or reviewing `.launch.py` files.
**Tools:** Read, Bash
**Validates:**
- All `Node()` executables reference real package/executable pairs
- Parameters loaded from YAML, not hardcoded inline for large configs
- Substitutions used for environment-specific paths
- `LaunchDescription` returns a list, not individual items
- `IncludeLaunchDescription` paths exist
- Lifecycle nodes use `LifecycleNode` + configurator pattern
- `use_sim_time` propagated correctly

### qos-agent
**When to use:** Creating any Publisher, Subscription, Service, or Action.
**Tools:** Read, Grep
**Validates:**
- Pub and sub QoS are compatible (reliability + durability combination)
- Sensor data uses `SensorDataQoS()` (best effort, volatile)
- State/map data uses reliable + transient_local (for late-joining subscribers)
- History depth is not 0
- No mixed reliable publisher with best-effort subscriber for critical data

### interface-agent
**When to use:** Creating `.msg`, `.srv`, or `.action` files.
**Tools:** Read, Bash
**Validates:**
- Valid ROS 2 field types (no `float` — use `float32` or `float64`)
- No reserved field names (`header`, `type`, `data` need special care)
- `std_msgs/Header` included for timestamped messages
- Array bounds for embedded systems
- Action has goal, result, and feedback sections
- No circular dependencies between interface packages
- Naming: `CamelCase.msg`, `CamelCase.srv`, `CamelCase.action`

### nav2-agent
**When to use:** Navigation2 stack configuration, behavior trees, costmaps.
**Tools:** Read, Bash
**Knows:**
- Nav2 parameter YAML structure for all major plugins
- BehaviorTree.CPP plugin registration
- Costmap2D layer configuration
- Global vs local planner selection
- Lifecycle manager dependencies
- `navigate_to_pose` vs `navigate_through_poses` action servers
- Recovery behaviors and their parameters

### moveit2-agent
**When to use:** MoveIt2, robot arm motion planning, kinematics.
**Tools:** Read, Bash
**Knows:**
- `MoveGroupInterface` API (new async API in Humble+)
- SRDF setup assistant output validation
- `moveit_configs_utils` Python helper (Jazzy+)
- Planning pipeline: OMPL, STOMP, PILZ
- Kinematics plugin selection (KDL, TRAC-IK, BioIK)
- Collision object management in `PlanningScene`
- Controller interface between MoveIt2 and `ros2_control`

### lifecycle-agent
**When to use:** Lifecycle nodes (managed nodes).
**Tools:** Read, Grep
**Validates:**
- `on_configure`, `on_activate`, `on_deactivate`, `on_cleanup`, `on_shutdown` all implemented
- Heavy resource allocation in `on_configure`, not constructor
- Publishers/subscribers created in `on_configure` or `on_activate` per pattern
- `LifecyclePublisher` used instead of regular `Publisher` in lifecycle nodes
- `LifecycleManager` or external configurator present in launch file
- Error state handling: what returns `TRANSITION_CALLBACK_FAILURE`

### colcon-agent
**When to use:** Any `colcon build` failure, CMake error, ament error.
**Tools:** Read, Bash
**Fixes:**
- Missing `find_package(ament_cmake REQUIRED)` or `ament_package()`
- Missing `rosidl_generate_interfaces()` for custom interfaces
- Incorrect `ament_target_dependencies()` calls
- Python package not found: missing `setup.cfg` or `setup.py`
- Overlay workspace not sourced: underlay missing
- `PYTHONPATH` issues for Python nodes
- Symlink install vs regular install confusion

### executor-agent
**When to use:** Designing the spin architecture of a node or multi-node system.
**Tools:** Read, Grep
**Guides:**
- `SingleThreadedExecutor` vs `MultiThreadedExecutor` vs `StaticSingleThreadedExecutor`
- `ReentrantCallbackGroup` vs `MutuallyExclusiveCallbackGroup`
- When to use `spin_once()` vs `spin()` vs `spin_until_future_complete()`
- Avoiding deadlocks in callback groups
- Node composition with a shared executor
- Real-time executor considerations

### tf2-cartographer
**When to use:** Any TF2 math, quaternion calculation, sensor fusion, MessageFilter, REP-105 compliance.
**Tools:** Read, Bash, Grep
**Specializes in:**
- Enforces quaternion-only internal calculations (never raw Euler math)
- REP-105 frame naming (`base_link`, `map`, `odom` — not custom names)
- MessageFilter for time-synchronized multi-sensor fusion
- Runs `ros2 run tf2_tools view_frames` to audit live TF tree
- Detects TF loops, duplicate broadcasters, missing frame chain

### sros2-secops
**When to use:** Production deployment, DDS security, node access control, certificate management.
**Tools:** Read, Bash, Grep
**Handles:**
- Generating SROS2 keystores and X.509 node certificates
- Writing XML access control policies (per-node pub/sub permissions)
- Configuring `ROS_SECURITY_ENABLE`, `ROS_SECURITY_STRATEGY`, `ROS_SECURITY_KEYSTORE`
- Validating certificates with openssl and signed permissions
- Diagnosing silent auth failures in secure DDS communication

### dds-tuner
**When to use:** Network issues, silent topic drops, large fleet discovery, bandwidth problems.
**Tools:** Read, Bash, Grep
**Handles:**
- Diagnosing QoS incompatibility (the #1 silent failure in ROS 2)
- Configuring Fast DDS Discovery Server for fleets > 5 robots
- Fast DDS and Cyclone DDS XML profile tuning
- Zenoh RMW setup for WAN/cloud deployments (Jazzy+)
- OS socket buffer tuning for PointCloud2 / image topics
- Network interface isolation to prevent multi-NIC confusion

### test-engineer
**When to use:** Writing or reviewing ROS 2 test code.
**Tools:** Read, Bash, Grep
**Handles:**
- `launch_testing` integration tests with `ReadyToTest()` barrier
- GTest C++ unit tests with `ament_add_gtest`
- pytest Python unit tests for node logic
- `ament_lint` compliance (cpplint, flake8, pep257, copyright)
- Post-shutdown assertions for process exit codes
- Test patterns: fake publishers, service call tests, topic assertion

### ros1-migrator
**When to use:** Porting ROS 1 code to ROS 2. Input is ROS 1, output MUST be pure ROS 2.
**Tools:** Read, Grep, Bash
**Translates:**
- `rospy` → `rclpy` (complete API table)
- `roscpp` → `rclcpp` (complete API table)
- `package.xml` Format 1 → Format 3
- `catkin_make` CMakeLists → `ament_cmake`
- XML `.launch` files → Python `.launch.py`
- `rospy.get_param` → `declare_parameter` + `get_parameter`
- `ros::Rate` + `sleep` → `create_timer` + callback

### launch-architect
**When to use:** Advanced launch patterns beyond simple `Node()` declarations.
**Tools:** Read, Bash, Grep
**Handles:**
- `OpaqueFunction` for dynamic launch logic (runtime argument evaluation)
- `RegisterEventHandler` + `OnProcessStart`/`OnProcessExit` for conditional startup
- `IfCondition` / `UnlessCondition` for conditional includes
- `Command()` substitution for xacro expansion at launch time
- `GroupAction` + `PushRosNamespace` for multi-robot namespacing
- Format selection: Python (complex logic) vs XML (simple static launches)
- `TimerAction` for delayed node startup

### micro-ros-agent
**When to use:** micro-ROS on microcontrollers (ESP32, STM32, Raspberry Pi Pico).
**Tools:** Read, Bash
**Knows:**
- Static memory allocation patterns (no heap in ROS callbacks)
- `RCCHECK` and `RCSOFTCHECK` macros
- Executor types for RTOS (default, polling)
- Transport layer: serial, UDP, USB
- micro-ROS agent setup on host machine
- Limitations: no parameters in default, no lifecycle, no actions on all platforms
- FreeRTOS task sizing for micro-ROS stack

### hardware-compat-agent
**When to use:** Checking hardware compatibility for ROS 2 deployment (CPU, GPU, Jetson, ARM).
**Tools:** Read, Bash, Grep, WebSearch
**Validates:**
- CPU architecture support (x86_64, ARM64, ARM32)
- GPU compatibility (CUDA, OpenGL, Vulkan) for perception nodes
- NVIDIA Jetson platform support (JetPack, L4T versions)
- Memory requirements for real-time systems
- Storage I/O for rosbag recording and large datasets
- Power consumption profiles for mobile robots

### ros2-control-agent
**When to use:** ros2_control framework, hardware interfaces, controllers, joint management.
**Tools:** Read, Bash, Grep
**Knows:**
- Controller types: diff_drive_controller, joint_trajectory_controller, effort_controllers
- Hardware interface plugins (SystemInterface, SensorInterface, ActuatorInterface)
- URDF ros2_control tags and parameter loading
- Controller manager lifecycle and spawner commands
- Real-time constraints for hardware interfaces
- CANopen, EtherCAT, and serial protocol integration

### safety-agent
**When to use:** Robot safety systems (ESTOP, collision detection, speed limiting, workspace bounds).
**Tools:** Read, Bash, Grep
**Handles:**
- Hardware ESTOP circuit design and GPIO monitoring
- Software safety nodes with watchdog timers
- Collision detection using PointCloud2 and bounding boxes
- Speed limiting based on proximity sensors
- Virtual workspace boundaries with odometry monitoring
- Fault tree analysis and safety system design patterns

### realtime-agent
**When to use:** Real-time performance tuning, executor selection, CPU isolation, deterministic timing.
**Tools:** Read, Bash, Grep
**Specializes in:**
- StaticSingleThreadedExecutor vs MultiThreadedExecutor selection
- CPU affinity and isolation for real-time threads
- Priority inheritance and scheduler settings (SCHED_FIFO)
- Callback group design to prevent priority inversion
- Timer jitter analysis and deterministic loop rates
- Lock-free data structures for real-time safe communication

### ubuntu-system-agent
**When to use:** Ubuntu system configuration for ROS 2 robots (services, permissions, network, users).
**Tools:** Read, Bash, Grep
**Manages:**
- systemd service configuration for robot bringup
- User permissions and groups for hardware access (gpio, dialout, video)
- Network configuration (static IPs, firewall, DDS discovery)
- Time synchronization (chrony, GPS) for multi-robot systems
- Log rotation and system monitoring for long-term deployments
- Package management and security updates for robot fleets
