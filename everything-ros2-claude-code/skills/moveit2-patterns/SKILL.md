---
name: moveit2-patterns
description: MoveIt2 integration patterns for robot arm motion planning
triggers:
  - moveit
  - moveit2
  - MoveGroupInterface
  - motion planning
  - robot arm
  - planning scene
  - SRDF
  - kinematics
  - trajectory
---

# MoveIt2 Patterns

## MoveGroupInterface — C++ (Humble)

```cpp
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <geometry_msgs/msg/pose.hpp>
#include <rclcpp/rclcpp.hpp>

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("moveit2_demo",
        rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));

    // Spin node in background thread (required for MoveGroupInterface)
    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    auto spinner = std::thread([&executor]() { executor.spin(); });

    const std::string PLANNING_GROUP = "arm";
    moveit::planning_interface::MoveGroupInterface move_group(node, PLANNING_GROUP);
    moveit::planning_interface::PlanningSceneInterface planning_scene_interface;

    // Set planning parameters
    move_group.setPlanningTime(5.0);
    move_group.setMaxVelocityScalingFactor(0.5);
    move_group.setMaxAccelerationScalingFactor(0.5);

    // --- Joint goal ---
    moveit::core::RobotStatePtr current_state = move_group.getCurrentState(10);
    std::vector<double> joint_group_positions;
    current_state->copyJointGroupPositions(
        current_state->getJointModelGroup(PLANNING_GROUP),
        joint_group_positions);
    joint_group_positions[0] = 1.57;  // radians
    move_group.setJointValueTarget(joint_group_positions);

    moveit::planning_interface::MoveGroupInterface::Plan plan;
    bool success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
    if (success) move_group.execute(plan);

    // --- Pose goal ---
    geometry_msgs::msg::Pose target_pose;
    target_pose.orientation.w = 1.0;
    target_pose.position.x = 0.28;
    target_pose.position.y = -0.2;
    target_pose.position.z = 0.5;
    move_group.setPoseTarget(target_pose);

    success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
    if (success) move_group.execute(plan);

    // --- Named target (defined in SRDF) ---
    move_group.setNamedTarget("home");
    success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
    if (success) move_group.execute(plan);

    // --- Cartesian path ---
    std::vector<geometry_msgs::msg::Pose> waypoints;
    geometry_msgs::msg::Pose start_pose = move_group.getCurrentPose().pose;
    waypoints.push_back(start_pose);
    start_pose.position.z -= 0.2;
    waypoints.push_back(start_pose);
    start_pose.position.y -= 0.2;
    waypoints.push_back(start_pose);

    moveit_msgs::msg::RobotTrajectory trajectory;
    const double jump_threshold = 0.0;
    const double eef_step = 0.01;
    double fraction = move_group.computeCartesianPath(
        waypoints, eef_step, jump_threshold, trajectory);
    RCLCPP_INFO(node->get_logger(), "Cartesian path: %.2f%% achieved", fraction * 100.0);

    rclcpp::shutdown();
    spinner.join();
    return 0;
}
```

## MoveItPy — Python (Iron+ only)

```python
# MoveItPy is NOT available in Humble — use C++ or action clients instead
import rclpy
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy

def main():
    rclpy.init()
    moveit = MoveItPy(node_name="moveit_py_demo")
    arm = moveit.get_planning_component("arm")

    # Set goal state by named config
    arm.set_start_state_to_current_state()
    arm.set_goal_state(configuration_name="ready")
    plan_result = arm.plan()
    if plan_result:
        moveit.execute(plan_result.trajectory, controllers=[])

    rclpy.shutdown()
```

## Adding Collision Objects (C++)

```cpp
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>

// Add a box obstacle to the planning scene
moveit_msgs::msg::CollisionObject collision_object;
collision_object.header.frame_id = move_group.getPlanningFrame();
collision_object.id = "box1";

shape_msgs::msg::SolidPrimitive primitive;
primitive.type = primitive.BOX;
primitive.dimensions.resize(3);
primitive.dimensions[0] = 0.1;  // x
primitive.dimensions[1] = 0.1;  // y
primitive.dimensions[2] = 0.5;  // z

geometry_msgs::msg::Pose box_pose;
box_pose.orientation.w = 1.0;
box_pose.position.x = 0.48;
box_pose.position.y = 0.0;
box_pose.position.z = 0.25;

collision_object.primitives.push_back(primitive);
collision_object.primitive_poses.push_back(box_pose);
collision_object.operation = collision_object.ADD;

std::vector<moveit_msgs::msg::CollisionObject> collision_objects;
collision_objects.push_back(collision_object);
planning_scene_interface.addCollisionObjects(collision_objects);
```

## SRDF Named States Pattern

```xml
<!-- robot.srdf — defines planning groups and named states -->
<robot name="my_arm">
  <group name="arm">
    <chain base_link="base_link" tip_link="tool0"/>
  </group>
  <group name="gripper">
    <joint name="finger_joint_1"/>
    <joint name="finger_joint_2"/>
  </group>

  <!-- Named ready states for quick access -->
  <group_state name="home" group="arm">
    <joint name="joint_1" value="0"/>
    <joint name="joint_2" value="-1.57"/>
    <joint name="joint_3" value="0"/>
    <joint name="joint_4" value="-1.57"/>
    <joint name="joint_5" value="0"/>
    <joint name="joint_6" value="0"/>
  </group_state>

  <group_state name="ready" group="arm">
    <joint name="joint_1" value="0"/>
    <joint name="joint_2" value="-0.785"/>
    <joint name="joint_3" value="0"/>
    <joint name="joint_4" value="-2.356"/>
    <joint name="joint_5" value="0"/>
    <joint name="joint_6" value="1.571"/>
  </group_state>

  <!-- End-effector -->
  <end_effector name="gripper_eef" parent_link="tool0"
                group="gripper" parent_group="arm"/>

  <!-- Self-collision allowed between these links -->
  <disable_collisions link1="base_link" link2="link1" reason="Adjacent"/>
  <disable_collisions link1="link1" link2="link2" reason="Adjacent"/>
</robot>
```

## moveit_configs_utils (Iron+ / Jazzy recommended)

```python
# Jazzy+ launch pattern using moveit_configs_utils
from moveit_configs_utils import MoveItConfigsBuilder
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("my_robot", package_name="my_robot_moveit_config")
        .robot_description(file_path="config/my_robot.urdf.xacro")
        .robot_description_semantic(file_path="config/my_robot.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(
            pipelines=["ompl", "stomp", "pilz_industrial_motion_planner"]
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    return LaunchDescription([move_group_node])
```

## Kinematics Plugin Selection

```yaml
# kinematics.yaml
arm:
  kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
  kinematics_solver_search_resolution: 0.005
  kinematics_solver_timeout: 0.005

# Better options:
# kinematics_solver: pick_ik/PickIkPlugin          # best general purpose (Humble+)
# kinematics_solver: trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin  # fast IK
# kinematics_solver: bio_ik/BioIKKinematicsPlugin  # redundancy resolution
```

## MoveIt2 package.xml Dependencies

```xml
<depend>moveit_ros_planning_interface</depend>
<depend>moveit_ros_move_group</depend>
<depend>moveit_core</depend>
<depend>moveit_msgs</depend>
<!-- Humble only needs above. Iron+ can also use: -->
<depend>moveit_configs_utils</depend>  <!-- Iron+ -->
```
