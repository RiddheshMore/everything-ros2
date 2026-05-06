# everything-ros2-claude-code

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Iron%20%7C%20Jazzy%20%7C%20Kilted-blue)](https://docs.ros.org/en/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-orange)](https://docs.anthropic.com/en/docs/claude-code)

> **The comprehensive sub-agentic harness for ROS 2 development with AI coding assistants.**

> Dedicated specialist agents for every ROS 2 domain — URDF validation, topic naming, distro compatibility, TF2, Nav2, MoveIt2, QoS, lifecycle nodes, ros2_control, safety systems, real-time performance, and more. Built so AI assistants stop hallucinating ROS APIs and start shipping real robots.

---

## Quick Start Guide

### Prerequisites

- **ROS 2** (Humble, Iron, Jazzy, Kilted, or Rolling)
- **Python 3.8+**
- **Claude Code** (desktop or CLI)
- **Git**

### Installation

#### Method 1: Install Script (Recommended)

```bash
# Clone this repository
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

# Run the install script
./install.sh

# Or install specific components
./install.sh agents      # Install only agents
./install.sh skills      # Install only skills
./install.sh commands    # Install only commands
```

#### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/RiddheshMore/everything-ros2-claude-code.git
cd everything-ros2-claude-code

# Copy agents to Claude
cp -r agents ~/.claude/agents/

# Copy skills to Claude
cp -r skills ~/.claude/skills/

# Copy commands to Claude
cp -r commands ~/.claude/commands/

# Copy rules to Claude (language-specific)
cp -r rules/common ~/.claude/rules/common
cp -r rules/cpp ~/.claude/rules/cpp      # For C++ ROS 2 nodes
cp -r rules/python ~/.claude/rules/python  # For Python ROS 2 nodes
```

#### Method 3: Claude Code Marketplace

In Claude Code, run:
```
/plugin marketplace add RiddheshMore/everything-ros2-claude-code
/plugin install everything-ros2-claude-code
```

---

## Usage

### Basic Workflow

1. **Start Claude Code** in your ROS 2 project directory
2. **Make a request** - e.g., "Create a new ROS 2 publisher node"
3. **The orchestrator agent** routes your request to the appropriate specialist agent
4. **Specialist agents** analyze and validate the code against ROS 2 best practices
5. **Results** are returned with validation checks and fixes

### Available Commands

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
| `/nav2-config` | Audit Nav2 configuration |
| `/moveit2-check` | Validate MoveIt2 setup |
| `/lifecycle-audit` | Check lifecycle node state machine |
| `/colcon-fix` | Diagnose and fix build errors |
| `/ros2-new-pkg` | Scaffold a new ROS 2 package |
| `/ros2-plan` | Plan a new feature with agent consultation |

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
├── commands/                  # Slash commands for Claude
├── rules/                     # Always-follow guidelines
│   ├── common/               # Language-agnostic rules
│   ├── cpp/                  # C++ specific rules
│   └── python/               # Python specific rules
├── hooks/                     # Automation hooks (PostToolUse, PreToolUse)
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
├── test_inputs/              # Test fixtures (ROS 1 examples)
├── test_outputs/             # Expected outputs (ROS 2 conversions)
├── tests/                    # Agent test suite
└── scripts/                  # Helper scripts
```

---

## Configuration

### Target ROS 2 Distro

Edit `~/.claude/settings.json` to set your target distro:

```json
{
  "globalEnvironmentVariables": {
    "ROS_DISTRO": "humble"
  }
}
```

Supported distros: `humble`, `iron`, `jazzy`, `kilted`, `rolling`

### Custom Agent Configuration

Create `~/.claude/agents/custom-ros2-settings.md`:

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
# Reinstall agents
cp -r agents ~/.claude/agents/
# Restart Claude Code
```

### Build Errors

Use `/colcon-fix` command to diagnose and fix build issues.

### Distro API Mismatch

Use `/distro-check` command to verify API compatibility with your ROS 2 distro.

---

## License

MIT — use freely, modify as needed, contribute back what you can.

---

## Acknowledgments

- Inspired by [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
- Built for the robotics community
