# Contributing to everything-ros2-claude-code

Contributions are welcome and encouraged. ROS 2 is vast — no single person
can cover every distro, platform, and subsystem. If you've hit a problem
that the AI missed, add an agent or skill for it.

---

## What to Contribute

### High Priority

| Area | Specific Gaps |
|---|---|
| `ros2_control` | Hardware interfaces, controllers, broadcaster patterns |
| Gazebo / Ignition | Simulation world setup, sensor plugins, ros_gz_bridge |
| SLAM toolboxes | slam_toolbox, cartographer, rtabmap configuration |
| Sensor drivers | Camera (image_transport, v4l2_camera), IMU, GPS |
| Hardware-specific | Jetson Orin/AGX, RPi 5, UpBoard, STM32 with micro-ROS |
| DDS configuration | Per-vendor FastDDS/CycloneDDS tuning, WAN bridging |
| Testing | launch_testing patterns, node mocking, rosbag playback tests |
| ROS 2 Control | controller_manager, joint_trajectory_controller, effort controllers |
| Action patterns | Action server/client with preemption, nested actions |
| Behavior Trees | BehaviorTree.CPP node authoring, Groot2 integration |

### Always Welcome
- Distro-specific API additions to `distro-compat-agent.md`
- New URDF/XACRO patterns (prismatic actuators, parallel mechanisms)
- Real-world package examples (hardware drivers, navigation configs)
- Bug fixes to existing agents (wrong API, outdated example)
- Additional hook scripts (detect hardcoded IP addresses, etc.)

---

## Agent Contribution Template

Create `agents/my-new-agent.md`:

```markdown
---
name: my-new-agent
description: >
  One sentence: what problem does this agent solve?
  Two sentences: what specific failures does it prevent?
  Three: when should the orchestrator delegate to it?
tools:
  - Read
  - Bash    (only if it runs CLI commands)
  - Grep
model: haiku  (haiku for pattern checking, sonnet for reasoning, opus for complex)
---

You are a ROS 2 [domain] specialist. Your job is to [prevent what failures].

## Validation Steps

### Step 1: [Name]
[What to check and how]

## Common [Domain] Mistakes

### Mistake 1: [Title]
```[language]
# WRONG
...

# CORRECT
...
```

## Output Format

```
[Domain] Report
===============
File: example.py

✅ [what passed]
❌ [what failed]: [why it's wrong]
   Fix: [exact change needed]
⚠️  [warning]: [why it might be a problem]
```
```

---

## Skill Contribution Template

Create `skills/my-skill-name/SKILL.md`:

```markdown
---
name: my-skill-name
description: Brief description of domain covered
triggers:
  - keyword1
  - keyword2
  - "phrase that triggers this skill"
---

# My Skill Title

## Quick Reference

[Table or decision tree for the most common question]

## Copy-Paste Patterns

[The patterns developers actually need, complete and runnable]

## Common Mistakes

[What the AI (and humans) typically get wrong here]

## Debug Commands

[CLI commands to diagnose issues in this domain]
```

---

## Example Contribution Template

Create `examples/my-example/README.md` with:

1. **Full file tree** showing the package structure
2. **Complete file contents** — all files, copy-paste ready
3. **Build and run instructions** tested on at least one distro
4. **What it demonstrates** — the ROS 2 patterns it teaches

---

## Pull Request Process

1. **Fork** the repo and create a branch: `git checkout -b feat/ros2-control-agent`

2. **Test your agent** — run it on at least one real ROS 2 issue it should catch

3. **Update `README.md`** — add your agent/skill/command to the relevant table

4. **Update `AGENTS.md`** — add an entry if it's a new agent

5. **PR title format:**
   ```
   feat(agent): Add ros2_control hardware interface validator
   feat(skill): Add ros2_control patterns skill
   feat(example): Add UR5e + MoveIt2 + ros2_control example
   fix(agent): Fix URDF validator mesh path check on macOS
   ```

6. **PR description** must include:
   - What ROS 2 failure this prevents
   - Which distros it was tested on
   - Example of a bug it would have caught

---

## Agent Naming Conventions

| Suffix | Meaning | Tools |
|---|---|---|
| `-agent` | Validates and catches errors | Read, Grep |
| `-validator` | Deep file validation | Read, Bash, Grep |
| `-architect` | Design decisions, structure | Read |
| `-migrator` | Code migration between versions | Read |
| `-tuner` | Performance configuration | Read, Bash |
| `-secops` | Security audit | Read, Grep |
| `-engineer` | Generates test code | Read, Bash |

---

## Local Testing

```bash
# Install deps (hook scripts only)
npm install

# Test hook scripts
node scripts/hooks/check-ros1-apis.js examples/bad_ros1_node.py

# Dry-run install
./install.sh --dry-run

# Full install to test
./install.sh --target claude
```

---

## License

By contributing, you agree your contributions are licensed under MIT.
