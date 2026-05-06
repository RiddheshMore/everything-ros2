# everything-ros2-claude-code

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Iron%20%7C%20Jazzy%20%7C%20Kilted-blue)](https://docs.ros.org/en/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-blue)](https://cursor.com)
[![Copilot](https://img.shields.io/badge/Copilot-Compatible-green)](https://github.com/features/copilot)
[![Windsurf](https://img.shields.io/badge/Windsurf-Compatible-teal)](https://windsurf.com)
[![Cline](https://img.shields.io/badge/Cline-Compatible-purple)](https://cline.bot)
[![Gemini](https://img.shields.io/badge/Gemini%20Code%20Assist-Compatible-yellow)](https://cloud.google.com/gemini/docs/codeassist/overview)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-Compatible-black)](https://openai.com/index/codex/)

> **The comprehensive sub-agentic harness for ROS 2 development with AI coding assistants.**

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

This repo gives AI coding assistants (Claude Code, Cursor, Copilot, Windsurf, Cline, Gemini, Codex) a **fleet of 27 specialist sub-agents**, each deeply trained in one ROS 2 domain. The orchestrator routes tasks to the right agent, collects results, and guards against the most common failure modes.

---

## Quick Start Guide

### Prerequisites

- **ROS 2** (Humble, Iron, Jazzy, Kilted, or Rolling)
- **Python 3.8+**
- **Your AI coding assistant** (Claude Code, Cursor, Copilot, or any tool supporting .md agent files)
- **Git**

### Installation

#### Method 1: Claude Code Plugin (Recommended for Claude Code)

In Claude Code, run these as **two separate commands**:
```
/plugin marketplace add RiddheshMore/everything-ros2-claude-code
```
```
/plugin install everything-ros2-claude-code
```

#### Method 2: Install Script (Recommended for all other agents)

```bash
# Clone this repository
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

# Install for your AI coding agent
./install.sh --target claude      # Claude Code
./install.sh --target cursor      # Cursor IDE
./install.sh --target copilot     # GitHub Copilot
./install.sh --target windsurf    # Windsurf / Cascade
./install.sh --target cline       # Cline
./install.sh --target gemini      # Gemini Code Assist
./install.sh --target codex       # OpenAI Codex
./install.sh --target all         # Install for ALL agents

# Preview what will be installed without writing files
./install.sh --target cursor --dry-run
```

#### Method 3: Manual Installation

```bash
# Clone the repository
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

# For Claude Code users
cp -r agents ~/.claude/agents/
cp -r skills ~/.claude/skills/
cp -r commands ~/.claude/commands/
cp -r rules/common ~/.claude/rules/common
cp -r rules/cpp ~/.claude/rules/cpp
cp -r rules/python ~/.claude/rules/python

# For Cursor users — copy .mdc rules to your project
cp -r .cursor/rules/*.mdc /path/to/your/project/.cursor/rules/
cp AGENTS.md /path/to/your/project/

# For GitHub Copilot users
cp .github/copilot-instructions.md /path/to/your/project/.github/
cp AGENTS.md /path/to/your/project/

# For Windsurf users
cp -r .windsurf/rules/ /path/to/your/project/.windsurf/rules/
cp AGENTS.md /path/to/your/project/

# For Cline users
cp -r .clinerules/ /path/to/your/project/.clinerules/
cp AGENTS.md /path/to/your/project/

# For Gemini Code Assist users
cp GEMINI.md /path/to/your/project/
cp AGENTS.md /path/to/your/project/

# For OpenAI Codex users
cp AGENTS.md /path/to/your/project/
```

---

## Usage

### Supported AI Coding Assistants

| Assistant | Config Format | Auto-Detected |
|-----------|--------------|---------------|
| **Claude Code** | `.claude-plugin/plugin.json` + `agents/` + `skills/` | ✅ Plugin system |
| **Cursor** | `.cursor/rules/*.mdc` | ✅ Glob + always-on |
| **GitHub Copilot** | `.github/copilot-instructions.md` + `AGENTS.md` | ✅ Auto-injected |
| **Windsurf** | `.windsurf/rules/ros2-rules.md` | ✅ Cascade reads rules |
| **Cline** | `.clinerules/ros2-rules.md` | ✅ System prompt injection |
| **Gemini Code Assist** | `GEMINI.md` | ✅ Project context |
| **OpenAI Codex** | `AGENTS.md` | ✅ Native support |

### Basic Workflow

1. **Start your AI coding assistant** in your ROS 2 project directory
2. **Make a request** - e.g., "Create a new ROS 2 publisher node"
3. **The orchestrator agent** routes your request to the appropriate specialist agent
4. **Specialist agents** analyze and validate the code against ROS 2 best practices
5. **Results** are returned with validation checks and fixes

### Available Slash Commands

| Command | Description |
|---------|-------------|
| `/ros2-validate` | Full project audit (runs all agents) |
| `/urdf-check` | Validate URDF/XACRO files and visualize structure |
| `/topic-audit` | Audit all topic/service/action names |
| `/distro-check` | Check code compatibility against target ROS 2 distro |
| `/pkg-check` | Validate package.xml and CMakeLists.txt |
| `/tf-tree` | Analyze TF2 frame tree for missing transforms |
| `/qos-audit` | Check QoS policy compatibility |
| `/launch-validate` | Validate launch files |
| `/interface-check` | Validate message/service/action definitions |
| `/nav2-config` | Audit Nav2 configuration and BT plugins |
| `/moveit2-check` | Validate MoveIt2 setup and planning groups |
| `/lifecycle-audit` | Check lifecycle node state machine coverage |
| `/colcon-fix` | Diagnose and fix colcon build errors |
| `/ros2-new-pkg` | Scaffold new ROS 2 package with best practices |
| `/ros2-plan` | Plan a new ROS 2 feature with agent consultation |

### Agent Reference

| Agent | Purpose |
|-------|---------|
| `ros2-orchestrator` | Routes tasks to specialist agents |
| `urdf-validator` | Validates URDF/XACRO files |
| `topic-schema-agent` | Enforces topic naming conventions |
| `distro-compat-agent` | Checks API compatibility across distros |
| `package-structure-agent` | Validates package.xml and CMakeLists.txt |
| `tf2-agent` | Validates TF2 frame lookups |
| `launch-agent` | Validates launch files |
| `qos-agent` | Checks QoS policy compatibility |
| `interface-agent` | Validates message/service/action definitions |
| `nav2-agent` | Navigation2 stack configuration |
| `moveit2-agent` | MoveIt2 motion planning |
| `lifecycle-agent` | Lifecycle node state transitions |
| `colcon-agent` | Build system diagnostics |
| `executor-agent` | Executor and callback group patterns |
| `micro-ros-agent` | micro-ROS for embedded systems |
| `ros2-control-agent` | ros2_control configurations |
| `safety-agent` | Safety system implementation |
| `realtime-agent` | Real-time performance optimization |
| `hardware-compat-agent` | Hardware platform compatibility |
| `ubuntu-system-agent` | Ubuntu system configuration |
| `dds-tuner` | DDS configuration tuning |
| `launch-architect` | Launch file architecture |
| `sros2-secops` | Security policy configuration |
| `test-engineer` | Testing strategy and coverage |
| `tf2-cartographer` | Cartographer SLAM configuration |
| `ros1-migrator` | ROS 1 to ROS 2 migration |

---

## Project Structure

```
everything-ros2-claude-code/
├── agents/                    # 27 specialist sub-agents
│   ├── ros2-orchestrator.md
│   ├── urdf-validator.md
│   └── ... (25 more agents)
├── skills/                    # 27 domain knowledge areas
│   ├── urdf-patterns/SKILL.md
│   ├── topic-naming/SKILL.md
│   └── ... (25 more skills)
├── commands/                  # Slash commands for AI assistants
├── rules/                     # Always-follow guidelines
│   ├── common/               # Language-agnostic rules
│   ├── cpp/                  # C++ specific rules
│   └── python/               # Python specific rules
├── hooks/                     # Automation hooks (PostToolUse, PreToolUse)
├── contexts/                  # System prompt contexts
├── examples/                  # 10 real-world package examples
│   ├── minimal-publisher/    # C++ & Python pub/sub
│   ├── turtlebot4-navigation/ # Nav2 with real hardware
│   ├── lifecycle-sensor-driver/ # Lifecycle node pattern
│   ├── custom-bt-plugin/     # BehaviorTree.CPP Nav2 plugin
│   ├── micro-ros-esp32/      # ESP32 + FreeRTOS + micro-ROS
│   ├── multi-robot-fleet/    # Namespaced multi-robot setup
│   ├── docker-robot-stack/   # Multi-container ROS 2 stack
│   ├── ros2-control-diffbot/ # Differential drive with ros2_control
│   ├── safety-node/          # Safety monitoring system
│   └── systemd-robot-service/ # systemd services for robots
├── test_inputs/              # Test fixtures (ROS 1 examples)
├── test_outputs/             # Expected outputs (ROS 2 conversions)
├── tests/                    # Agent test suite
└── scripts/                  # Helper scripts
```

---

## Configuration

### Target ROS 2 Distro

Set your target distro in your AI assistant's settings:

**Claude Code** (`~/.claude/settings.json`):
```json
{
  "globalEnvironmentVariables": {
    "ROS_DISTRO": "humble"
  }
}
```

**Cursor** (`.cursor/settings.json`):
```json
{
  "env": {
    "ROS_DISTRO": "humble"
  }
}
```

Supported distros: `humble`, `iron`, `jazzy`, `kilted`, `rolling`

### Custom Agent Configuration

Create a custom settings file in your agent config directory:

```markdown
# Custom ROS 2 Settings

## Frame IDs
- base_frame: base_link
- map_frame: map
- odom_frame: odom

## Default QoS
- Sensor data: SensorDataQoS
- Parameters: ParametersQoS

## Topic Naming Convention
- Pub/Sub: /{component}/{verb}
- Services: /{component}/{noun}
```

---

## Examples

### Example 1: Creating a New Node

```
User: Create a Python ROS 2 node that publishes sensor data

Orchestrator -> distro-compat -> interface -> code-reviewer -> security-reviewer

Result: Validated Python node with proper rclpy imports, QoS, and parameters
```

### Example 2: URDF Validation

```
User: Validate this URDF for a differential drive robot

Orchestrator -> urdf-validator -> tf2-agent -> ros2-control-agent

Result: URDF validated with correct joint/hardware interface definitions
```

### Example 3: Migration from ROS 1

```
User: Convert this ROS 1 package to ROS 2

Orchestrator -> ros1-migrator -> colcon-agent -> distro-compat

Result: Converted CMakeLists.txt, package.xml, and launch files
```

### Example 4: Topic Naming Audit

```
User: /topic-audit

Result: Finds non-conpliant topic names like "/sensors" (should be "/sensor_data")
```

---

## Development

### Running Tests

```bash
cd tests
python -m pytest test_agents_skills_functionality.py
python -m pytest test_orchestrator.py
```

### Adding a New Agent

1. Create `agents/your-agent.md` with the agent definition
2. Add command in `commands/your-command.md`
3. Add skill in `skills/your-skill/SKILL.md`
4. Update the AGENTS.md summary file

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Troubleshooting

### Agent Not Found

```bash
# Reinstall for your specific assistant
./install.sh --target claude     # Claude Code
./install.sh --target cursor     # Cursor
./install.sh --target copilot    # Copilot
./install.sh --target windsurf   # Windsurf
./install.sh --target cline      # Cline
./install.sh --target gemini     # Gemini
./install.sh --target codex      # Codex

# Or reinstall for ALL agents
./install.sh --target all

# Restart your AI assistant after installation
```

### Build Errors

Use `/colcon-fix` command to diagnose and fix build issues.

### Distro API Mismatch

Use `/distro-check` command to verify API compatibility with your ROS 2 distro.

### Topic Naming Issues

Use `/topic-audit` to identify non-conpliant topic names in your workspace.

---

## License

MIT — use freely, modify as needed, contribute back what you can.

---

## Acknowledgments

- Inspired by [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
- Built for the robotics community
