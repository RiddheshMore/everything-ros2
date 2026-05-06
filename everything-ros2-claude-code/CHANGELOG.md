# Changelog

## 1.0.0 - 2026-04-06

### Highlights

- Initial release of everything-ros2-claude-code with 25+ specialized agents for ROS 2 development
- Complete agent ecosystem covering navigation, manipulation, real-time, embedded, and simulation
- Hardware abstraction layer with support for Jetson, Raspberry Pi, and industrial controllers
- Safety-first architecture with dedicated safety and SROS2 agents

### New Agents

- `ros2-orchestrator` — Routes any ROS 2 task to appropriate specialist agents
- `urdf-validator` — Validates URDF/XACRO files for syntax and semantic correctness
- `nav2-agent` — Navigation2 configuration and behavior tree design
- `moveit2-agent` — Motion planning and MoveIt2 configuration
- `ros2-control-agent` — Hardware interface and controller configuration
- `lifecycle-agent` — Managed lifecycle nodes and state transitions
- `realtime-agent` — Real-time performance optimization (PREEMPT_RT)
- `micro-ros-agent` — Micro-ROS for embedded systems (ESP32, STM32)
- `colcon-agent` — Build troubleshooting and colcon workflows
- `tf2-agent` — Frame transformations and TF2 debugging
- `qos-agent` — Quality of Service configuration and debugging
- `launch-agent` — Python-based launch file architecture
- `distro-compat-agent` — Multi-distro API compatibility checking
- `hardware-compat-agent` — Hardware driver compatibility and abstraction
- `safety-agent` — Safety-critical system design and SGS compliance
- `sros2-secops` — Security operations and encryption
- `executor-agent` — Multi-threaded executor configuration
- `interface-agent` — Custom message/service/action interfaces
- `package-structure-agent` — Package.xml and CMakeLists.txt validation
- `topic-schema-agent` — Topic naming conventions and validation
- `launch-architect` — Multi-robot fleet launch coordination
- `tf2-cartographer` — SLAM and cartographer integration
- `test-engineer` — Testing strategies and continuous integration
- `dds-tuner` — DDS configuration and network optimization
- `ros1-migrator` — ROS 1 to ROS 2 migration assistance
- `ubuntu-system-agent` — Ubuntu system configuration for ROS 2

### New Skills

- `hardware-drivers` — Lidar, camera, IMU integration patterns
- `ros2-control` — Hardware interfaces and controller configuration
- `safety-patterns` — Safety function implementation (EN ISO 13849)
- `realtime-patterns` — Real-time safe patterns and PREEMPT_RT setup
- `docker-ros2` — Containerization best practices
- `systemd-ros2` — Auto-start services and daemon management
- `network-config` — DDS tuning and multi-machine setup
- `nav2-patterns` — Navigation configuration and behavior trees
- `moveit2-patterns` — Motion planning and trajectory execution
- `micro-ros-patterns` — Embedded ROS 2 development
- `lifecycle-node` — Managed node patterns
- `tf2-patterns` — Frame transformation best practices
- `qos-patterns` — Quality of Service configuration
- `composable-nodes` — Component container patterns
- `parameter-patterns` — ROS 2 parameter handling
- `launch-patterns` — Python launch file patterns
- `rosbag-patterns` — Data recording and playback
- `distro-compat` — Multi-distro compatibility patterns
- `interface-design` — Message/service/action design
- `package-structure` — ROS 2 package organization
- `colcon-build` — Build system optimization
- `executors-patterns` — Callback group configuration
- `topic-naming` — Naming conventions and best practices
- `urdf-patterns` — Robot description patterns
- `ros-security` — SROS2 and security best practices
- `jetson-setup` — NVIDIA Jetson configuration
- `ubuntu-system` — Ubuntu system preparation

### Commands

- `/ros2-plan` — Generate implementation plan with PRD, architecture, tech doc
- `/ros2-new-pkg` — Create ROS 2 package with proper structure
- `/colcon-fix` — Diagnose and fix build failures
- `/urdf-check` — Validate URDF with detailed reporting
- `/distro-check` — Validate API compatibility across distros
- `/pkg-check` — Audit package.xml and CMakeLists.txt
- `/qos-audit` — Review QoS settings for all topics
- `/topic-audit` — Check topic naming conventions
- `/tf-tree` — Visualize TF tree and detect issues
- `/launch-validate` — Validate launch files
- `/interface-check` — Check message/service definitions
- `/ros2-validate` — Comprehensive validation across all aspects
- `/specialized-agents` — List available specialist agents

### Examples

- `ros2-control-diffbot` — Differential drive robot with ros2_control
- `docker-robot-stack` — Multi-container robot deployment
- `lifecycle-sensor-driver` — Managed lifecycle sensor implementation
- `micro-ros-esp32` — ESP32 micro-ROS example
- `multi-robot-fleet` — Fleet coordination patterns
- `safety-node` — Safety function implementation
- `systemd-robot-service` — Auto-start robot services
- `turtlebot4-navigation` — Complete navigation stack
- `custom-bt-plugin` — Custom behavior tree nodes
- `minimal-publisher` — Basic ROS 2 node patterns

### Rules

- `ros2-fundamentals` — Core ROS 2 principles and patterns
- `rclpy-rules` — Python client library best practices
- `rclcpp-rules` — C++ client library best practices

### Documentation

- `AGENTS.md` — Complete agent reference
- `CLAUDE.md` — Project configuration for Claude Code
- `CONTRIBUTING.md` — Contribution guidelines
- `README.md` — Getting started guide
- `docs/debugging-guide.md` — ROS 2 debugging techniques
- `docs/distro-migration-guide.md` — Migrating between ROS 2 distros

### Testing

- `tests/evaluation_framework.py` — Agent evaluation framework
- `tests/run_agent_tests.py` — Run agent validation tests
- `tests/test_orchestrator.py` — Orchestrator unit tests
- `tests/test_agent_skill_validation.py` — Agent/skill validation
- `tests/test_agents_skills_functionality.py` — Functionality tests

### Installation

- `install.sh` — Unix/Linux installation script
- Supports selective installation of agents, skills, and rules
- Manifest-driven pipeline with SQLite state store

### Security

- SROS2 integration for encrypted communications
- PKI infrastructure support
- Secret management via environment variables
- Audit logging for security compliance

### Known Issues

- Some agents require ROS 2 distro-specific API knowledge
- Real-time agent requires PREEMPT_RT kernel
- Micro-ROS agent requires specific MCU toolchain setup

### Contributors

- Initial implementation and agent design
- Testing and validation across multiple ROS 2 distros
- Documentation and example contributions
