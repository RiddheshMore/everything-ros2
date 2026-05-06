---
name: urdf-patterns
description: URDF and XACRO authoring best practices and copy-paste templates
triggers:
  - urdf
  - xacro
  - robot_description
  - link
  - joint
  - inertia
  - mesh
---

# URDF / XACRO Patterns

## Minimal Valid Link

```xml
<link name="my_link">
  <visual>
    <geometry>
      <box size="0.1 0.1 0.1"/>
    </geometry>
    <material name="grey">
      <color rgba="0.5 0.5 0.5 1.0"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.1 0.1 0.1"/>  <!-- use primitives for collision, not meshes -->
    </geometry>
  </collision>
  <inertial>
    <mass value="0.5"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
  </inertial>
</link>
```

## Revolute Joint (with limits)

```xml
<joint name="shoulder_joint" type="revolute">
  <parent link="base_link"/>
  <child link="upper_arm_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>  <!-- rotation axis -->
  <limit lower="-3.14" upper="3.14" effort="100" velocity="1.0"/>
  <dynamics damping="0.1" friction="0.0"/>
</joint>
```

## Continuous Joint (wheels)

```xml
<joint name="left_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="left_wheel"/>
  <origin xyz="0 0.15 0" rpy="-1.5707 0 0"/>
  <axis xyz="0 0 1"/>
  <limit effort="10" velocity="5.0"/>
</joint>
```

## Mesh Link

```xml
<link name="arm_link">
  <visual>
    <geometry>
      <mesh filename="package://my_robot_description/meshes/arm.STL"
            scale="0.001 0.001 0.001"/>  <!-- STL in mm → scale to meters -->
    </geometry>
  </visual>
  <collision>
    <!-- Use a simple primitive for collision, not the mesh -->
    <geometry><cylinder radius="0.03" length="0.2"/></geometry>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
  </collision>
  <inertial>
    <mass value="0.3"/>
    <origin xyz="0 0 0.1"/>
    <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.0003"/>
  </inertial>
</link>
```

## XACRO Macro Pattern

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:property name="wheel_radius" value="0.05"/>
  <xacro:property name="wheel_width" value="0.03"/>

  <xacro:macro name="wheel" params="side x_pos y_pos">
    <link name="${side}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.2"/>
        <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0002"/>
      </inertial>
    </link>
    <joint name="${side}_wheel_joint" type="continuous">
      <parent link="base_link"/>
      <child link="${side}_wheel"/>
      <origin xyz="${x_pos} ${y_pos} 0" rpy="-1.5707 0 0"/>
      <axis xyz="0 0 1"/>
      <limit effort="10" velocity="5.0"/>
    </joint>
  </xacro:macro>

  <!-- Instantiate macro -->
  <xacro:wheel side="left"  x_pos="0" y_pos=" 0.15"/>
  <xacro:wheel side="right" x_pos="0" y_pos="-0.15"/>

</robot>
```

## Validate

```bash
# Expand XACRO
xacro my_robot.urdf.xacro > /tmp/expanded.urdf

# Check URDF structure
check_urdf /tmp/expanded.urdf

# Visualize in rviz
ros2 launch urdf_tutorial display.launch.py model:=/tmp/expanded.urdf
```

## Inertia Calculator (solid primitives)

```
Box (x, y, z, m):     Ixx = m/12*(y²+z²), Iyy = m/12*(x²+z²), Izz = m/12*(x²+y²)
Cylinder (r, h, m):   Ixx = Iyy = m/12*(3r²+h²), Izz = m/2*r²
Sphere (r, m):        Ixx = Iyy = Izz = 2/5*m*r²
```
