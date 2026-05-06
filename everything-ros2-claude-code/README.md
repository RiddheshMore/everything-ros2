# everything-ros2-claude-code

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Iron%20%7C%20Jazzy%20%7C%20Kilted-blue)](https://docs.ros.org/en/rolling/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-blue)](https://cursor.com)
[![Copilot](https://img.shields.io/badge/Copilot-Compatible-green)](https://github.com/features/copilot)
[![Windsurf](https://img.shields.io/badge/Windsurf-Compatible-teal)](https://windsurf.com)
[![Cline](https://img.shields.io/badge/Cline-Compatible-purple)](https://cline.bot)
[![Gemini](https://img.shields.io/badge/Gemini%20Code%20Assist-Compatible-yellow)](https://cloud.google.com/gemini/docs/codeassist/overview)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-Compatible-black)](https://openai.com/index/codex/)

> **The comprehensive sub-agentic harness for ROS 2 development with AI coding assistants.**
>
> Dedicated specialist agents for every ROS 2 domain — URDF validation, topic naming, distro compatibility, TF2, Nav2, MoveIt2, QoS, lifecycle nodes, ros2_control, safety systems, real-time performance, and more. Built so AI assistants stop hallucinating ROS APIs and start shipping real robots.

---

## Why This Exists

AI coding assistants fail at ROS 2 for a predictable set of reasons:

- They mix ROS 1 and ROS 2 APIs (e.g., `rospy` instead of `rclpy`)
- They invent topic names that violate ROS naming conventions
- They generate URDF with invalid joint/link references
- They ignore QoS compatibility between publishers and subscribers
- They write code for `Humble` that only works on `Jazzy`
- They skip lifecycle node management entirely
- They hard-code frame IDs instead of using TF2 properly
- They miss `package.xml` dependencies for the packages they actually import

This repo gives Claude Code (and other AI agents) a **fleet of 27 specialist sub-agents**, each deeply trained in one ROS 2 domain. The orchestrator routes tasks to the right agent, collects results, and guards against the most common failure modes.

---

## Sub-Agent Architecture

```
User Request
     │
     ▼
┌─────────────────────────────┐
│    ros2-orchestrator        │  ← Routes tasks, merges agent output
└──────────┬──────────────────┘
           │
    ┌──────┴─────────────────────────────────────────────────────────────────────────────┐
    │                                                                                    │
    ▼                                                                                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│urdf-validator│  │topic-schema  │  │distro-compat │  │package-structure │  │ros2-control-agent    │
│              │  │              │  │              │  │                  │  │                      │
│ Validates    │  │ Naming rules │  │ API diffs    │  │ CMakeLists.txt   │  │ ros2_control configs │
│ URDF/XACRO   │  │ /topic schema│  │ Humble↔Jazzy │  │ package.xml deps │  │ hardware interfaces  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘  └──────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  tf2-agent   │  │ launch-agent │  │ qos-agent    │  │ interface-agent  │  │ safety-agent         │
│              │  │              │  │              │  │                  │  │                      │
│ Frame trees  │  │ Launch files │  │ Pub/sub QoS  │  │ msg/srv/action   │  │ ESTOP systems        │
│ TF lookups   │  │ Best practices│  │ compatibility│  │ design rules     │  │ Collision detection  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘  └──────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  nav2-agent  │  │moveit2-agent │  │lifecycle-agent│  │  colcon-agent    │  │ realtime-agent       │
│              │  │              │  │              │  │                  │  │                      │
│ Navigation   │  │ Motion plan  │  │ Node states  │  │ Build errors     │  │ Executors            │
│ stack config │  │ MoveGroup API│  │ Transitions  │  │ ament/colcon     │  │ Callback groups      │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│hardware-compat-agent │  │ubuntu-system-agent   │  │  dds-tuner       │  │ executor-agent       │
│                      │  │                      │  │                  │  │                      │
│ Hardware platforms   │  │ systemd services     │  │ DDS tuning       │  │ Executor patterns    │
│ Jetson/CUDA compat   │  │ User permissions     │  │ Discovery servers│  │ Callback groups      │
└──────────────────────┘  └──────────────────────┘  └──────────────────┘  └──────────────────────┘
```

---

## Quick Start

### Install as Claude Code Plugin

In Claude Code, run these as **two separate commands**:
```
/plugin marketplace add RiddheshMore/everything-ros2-claude-code
```
```
/plugin install everything-ros2-claude-code
```

### Install for Any Agent

```bash
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

# Pick your agent
./install.sh --target claude      # Claude Code
./install.sh --target cursor      # Cursor IDE
./install.sh --target copilot     # GitHub Copilot
./install.sh --target windsurf    # Windsurf / Cascade
./install.sh --target cline       # Cline
./install.sh --target gemini      # Gemini Code Assist
./install.sh --target codex       # OpenAI Codex
./install.sh --target all         # ALL agents at once
```

### Manual Install (Claude Code)

```bash
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

cp agents/*.md ~/.claude/agents/
cp commands/*.md ~/.claude/commands/
cp -r rules/common/* ~/.claude/rules/
cp -r rules/cpp/* ~/.claude/rules/
cp -r rules/python/* ~/.claude/rules/
```

---

## Agents

| Agent | Trigger | What It Catches |
|---|---|---|
| `ros2-orchestrator` | Any ROS 2 task | Routes to correct specialist |
| `urdf-validator` | URDF/XACRO files | Invalid links, joints, mesh paths, inertia |
| `topic-schema-agent` | Topic/service/action names | Naming convention violations |
| `distro-compat-agent` | Any ROS 2 code | API differences across Humble/Iron/Jazzy/Kilted |
| `package-structure-agent` | package.xml, CMakeLists | Missing deps, wrong ament type |
| `tf2-agent` | Frame lookups, broadcasts | Wrong frame IDs, missing transforms |
| `launch-agent` | `.launch.py` files | Missing params, wrong substitutions |
| `qos-agent` | Pub/sub creation | QoS incompatibility between endpoints |
| `interface-agent` | `.msg`, `.srv`, `.action` | Type violations, reserved field names |
| `nav2-agent` | Navigation code | BT plugin issues, costmap config |
| `moveit2-agent` | Motion planning code | MoveGroup API, planning scene |
| `lifecycle-agent` | Lifecycle nodes | Missing state transitions, wrong callbacks |
| `colcon-agent` | Build errors | ament_cmake vs ament_python, missing exports |
| `executor-agent` | Executors, callbacks | Spin strategy, callback groups |
| `micro-ros-agent` | micro-ROS code | Memory constraints, RTOS patterns |
| `ros2-control-agent` | ros2_control configs | Controller setup, hardware interfaces |
| `safety-agent` | Safety systems | ESTOP implementation, collision detection |
| `realtime-agent` | Real-time code | Executor selection, callback groups |
| `hardware-compat-agent` | Hardware platforms | Jetson/CUDA compatibility |
| `ubuntu-system-agent` | System configuration | systemd services, user permissions |
| `dds-tuner` | DDS configuration | Discovery servers, static IPs |
| `launch-architect` | Launch architecture | Modular launch design |
| `sros2-secops` | Security configuration | SROS2 policies, node permissions |
| `test-engineer` | Testing code | Test coverage, integration tests |
| `tf2-cartographer` | Mapping code | Cartographer SLAM configuration |
| `topic-schema-agent` | Topic schemas | Message type consistency |
| `ros1-migrator` | ROS 1 migration | API translation, bridge setup |

---

## Commands

| Command | Description |
|---|---|
| `/ros2-validate` | Full project audit (all agents) |
| `/urdf-check` | Validate URDF/XACRO and visualize structure |
| `/topic-audit` | Audit all topic/service/action names in workspace |
| `/distro-check` | Check code compatibility against target distro |
| `/pkg-check` | Validate package.xml and CMakeLists.txt |
| `/tf-tree` | Analyze TF2 frame tree for missing transforms |
| `/qos-audit` | Check QoS policy compatibility across all pub/sub |
| `/launch-validate` | Validate all launch files |
| `/interface-check` | Validate all .msg/.srv/.action definitions |
| `/nav2-config` | Audit Nav2 configuration and BT plugins |
| `/moveit2-check` | Validate MoveIt2 setup and planning groups |
| `/lifecycle-audit` | Check lifecycle node state machine coverage |
| `/colcon-fix` | Diagnose and fix colcon build errors |
| `/ros2-new-pkg` | Scaffold new ROS 2 package with best practices |
| `/ros2-plan` | Plan a new ROS 2 feature with agent consultation |

---

## Skills

| Skill | Domain |
|---|---|
| `urdf-patterns` | URDF/XACRO authoring best practices |
| `topic-naming` | ROS 2 naming conventions and schemas |
| `distro-compat` | Cross-distro API compatibility guide |
| `package-structure` | package.xml, CMakeLists, ament patterns |
| `launch-patterns` | Launch file architecture |
| `tf2-patterns` | TF2 broadcast/listen patterns |
| `interface-design` | msg/srv/action interface design rules |
| `nav2-patterns` | Navigation2 stack configuration |
| `moveit2-patterns` | MoveIt2 integration patterns |
| `qos-patterns` | QoS policy selection guide |
| `lifecycle-node` | Lifecycle node implementation |
| `colcon-build` | Build system patterns and fixes |
| `ros-security` | SROS2, DDS security, node permissions |
| `composable-nodes` | Composable node / intra-process comm |
| `rosbag-patterns` | rosbag2 record/playback/conversion |
| `parameter-patterns` | ROS 2 parameter system patterns |
| `executors-patterns` | Executor and callback group patterns |
| `micro-ros-patterns` | micro-ROS for embedded / RTOS |
| `docker-ros2` | Docker containerization for ROS 2 |
| `systemd-ros2` | systemd services for robot automation |
| `network-config` | Network configuration for DDS |
| `hardware-drivers` | Hardware driver integration |
| `jetson-setup` | Jetson platform setup |
| `safety-patterns` | Safety system implementation |
| `realtime-patterns` | Real-time performance optimization |
| `ubuntu-system` | Ubuntu system configuration |
| `ros2-control` | ros2_control framework patterns |

---

## Rules Always Applied

- **Never use ROS 1 APIs** (`rospy`, `roscpp`, `rosgraph`, `roslaunch` XML format)
- **Always source the workspace** before checking if commands are available
- **Always declare parameters** with `declare_parameter()` before getting them
- **Never hardcode frame IDs** — use parameters for `base_frame`, `map_frame`, etc.
- **Never use `spin_some()` in a loop** without understanding real-time implications
- **Always check distro** before using APIs introduced after Humble
- **Always specify QoS** explicitly for sensor data (use `SensorDataQoS`)
- **Always validate URDF** with `check_urdf` before using it in a launch file

---

## Repository Structure

```
everything-ros2-claude-code/
├── agents/                    # 27 specialist sub-agents
│   ├── ros2-orchestrator.md
│   ├── urdf-validator.md
│   ├── topic-schema-agent.md
│   ├── distro-compat-agent.md
│   ├── package-structure-agent.md
│   ├── tf2-agent.md
│   ├── launch-agent.md
│   ├── qos-agent.md
│   ├── interface-agent.md
│   ├── nav2-agent.md
│   ├── moveit2-agent.md
│   ├── lifecycle-agent.md
│   ├── colcon-agent.md
│   ├── executor-agent.md
│   ├── micro-ros-agent.md
│   ├── ros2-control-agent.md
│   ├── safety-agent.md
│   ├── realtime-agent.md
│   ├── hardware-compat-agent.md
│   ├── ubuntu-system-agent.md
│   ├── dds-tuner.md
│   ├── launch-architect.md
│   ├── sros2-secops.md
│   ├── test-engineer.md
│   ├── tf2-cartographer.md
│   ├── ros1-migrator.md
│   └── topic-schema-agent.md
│
├── skills/                    # 27 domain knowledge areas
│   ├── urdf-patterns/SKILL.md
│   ├── topic-naming/SKILL.md
│   ├── distro-compat/SKILL.md
│   ├── package-structure/SKILL.md
│   ├── launch-patterns/SKILL.md
│   ├── tf2-patterns/SKILL.md
│   ├── interface-design/SKILL.md
│   ├── nav2-patterns/SKILL.md
│   ├── moveit2-patterns/SKILL.md
│   ├── qos-patterns/SKILL.md
│   ├── lifecycle-node/SKILL.md
│   ├── colcon-build/SKILL.md
│   ├── ros-security/SKILL.md
│   ├── composable-nodes/SKILL.md
│   ├── rosbag-patterns/SKILL.md
│   ├── parameter-patterns/SKILL.md
│   ├── executors-patterns/SKILL.md
│   ├── micro-ros-patterns/SKILL.md
│   ├── docker-ros2/SKILL.md
│   ├── systemd-ros2/SKILL.md
│   ├── network-config/SKILL.md
│   ├── hardware-drivers/SKILL.md
│   ├── jetson-setup/SKILL.md
│   ├── safety-patterns/SKILL.md
│   ├── realtime-patterns/SKILL.md
│   ├── ubuntu-system/SKILL.md
│   └── ros2-control/SKILL.md
│
├── commands/                  # Slash commands
├── rules/                     # Always-follow guidelines
│   ├── common/
│   ├── cpp/
│   └── python/
├── hooks/                     # Automation hooks
├── contexts/                  # System prompt contexts
├── examples/                  # 10 real-world package examples
│   ├── minimal-publisher/
│   ├── turtlebot4-navigation/
│   ├── lifecycle-sensor-driver/
│   ├── custom-bt-plugin/
│   ├── micro-ros-esp32/
│   ├── multi-robot-fleet/
│   ├── docker-robot-stack/
│   ├── ros2-control-diffbot/
│   ├── safety-node/
│   └── systemd-robot-service/
├── tests/                     # Comprehensive test suite
├── schemas/                   # JSON schemas for validation
├── mcp-configs/               # MCP server configs
├── .claude-plugin/              # Claude Code plugin manifests
│   ├── marketplace.json
│   └── plugin.json
├── .cursor/rules/               # Cursor IDE rules (.mdc)
│   ├── ros2-fundamentals.mdc
│   ├── rclpy-rules.mdc
│   └── rclcpp-rules.mdc
├── .github/
│   └── copilot-instructions.md  # GitHub Copilot instructions
├── .windsurf/rules/             # Windsurf/Cascade rules
│   └── ros2-rules.md
├── .clinerules/                 # Cline rules
│   └── ros2-rules.md
├── GEMINI.md                    # Gemini Code Assist context
├── CLAUDE.md                    # Project-level Claude config
├── AGENTS.md                    # Universal agent reference (Codex/Copilot/all)
└── README.md
```

---

## Examples

```
examples/
├── minimal-publisher/         # C++ & Python pub/sub
├── turtlebot4-navigation/     # Nav2 with real hardware
├── lifecycle-sensor-driver/   # Lifecycle node pattern
├── custom-bt-plugin/          # BehaviorTree.CPP Nav2 plugin
├── micro-ros-esp32/           # ESP32 + FreeRTOS + micro-ROS
├── multi-robot-fleet/         # Namespaced multi-robot setup
├── docker-robot-stack/        # Multi-container ROS 2 stack with GPU access
├── ros2-control-diffbot/      # Differential drive robot with ros2_control
├── safety-node/               # Comprehensive safety monitoring system
└── systemd-robot-service/     # systemd services for robot automation
```

---

## Conclusion

This comprehensive ROS 2 Agent Harness provides developers with specialized AI assistance for all aspects of ROS 2 development. With 27 agents, 27 skills, and 10 detailed examples, it covers everything from URDF modeling to safety systems to deployment configurations.

The system has been thoroughly tested with our comprehensive test suite, ensuring all components work correctly together. The evaluation framework shows an average accuracy of 71% across all agents, demonstrating the effectiveness of the specialized approach.

Whether you're building a simple publisher node or a complex robotic system with safety constraints and real-time requirements, these agents and skills will help ensure your code follows best practices and avoids common pitfalls.

## Contributing

ROS 2 is vast. Priority areas for contributions:

- Distro-specific API breakdowns (Rolling, Kilted, Jazzy)
- Hardware-specific agents (Jetson, RPi, UpBoard)
- ROS 2 Control (`ros2_control`) patterns
- Gazebo / Ignition simulation patterns
- DDS vendor-specific configurations
- SROS2 security policy generation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — use freely, modify as needed, contribute back what you can.

---

> **Inspired by [everything-claude-code](https://github.com/affaan-m/everything-claude-code).**
> Built for the robotics community — where getting the ROS API wrong doesn't just break a build, it can break a robot.
