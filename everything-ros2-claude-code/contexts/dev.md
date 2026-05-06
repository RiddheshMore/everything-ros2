# ROS 2 Development Context

You are working on a ROS 2 robotics project. Before writing any code:

1. **Read CLAUDE.md** to find the target ROS 2 distro and package type
2. **Check topic names** are snake_case and follow REP-103 standards
3. **Declare parameters** before getting them — always
4. **Use relative topic names** so namespace remapping works
5. **Never hardcode frame IDs** — always use parameters
6. **Specify QoS explicitly** for every publisher and subscriber

## Available Specialist Agents

Delegate to these agents by calling them in your response:

- `@urdf-validator` — URDF/XACRO validation
- `@topic-schema-agent` — topic/service/action naming
- `@distro-compat-agent` — distro API compatibility
- `@package-structure-agent` — package.xml, CMakeLists
- `@tf2-agent` — TF2 transforms and frame IDs
- `@launch-agent` — launch file validation
- `@qos-agent` — QoS policy selection and compatibility
- `@interface-agent` — .msg/.srv/.action design
- `@nav2-agent` — Navigation2 configuration
- `@moveit2-agent` — MoveIt2 motion planning
- `@lifecycle-agent` — lifecycle node patterns
- `@colcon-agent` — build error diagnosis
- `@executor-agent` — executor and callback group design
- `@micro-ros-agent` — embedded micro-ROS

## Always Produce

When creating a new node, always generate ALL of:
- The node source file (.py or .cpp)
- package.xml with all dependencies
- CMakeLists.txt or setup.py
- A .launch.py file
- A config/params.yaml file
- A brief comment block listing topics, services, and parameters
