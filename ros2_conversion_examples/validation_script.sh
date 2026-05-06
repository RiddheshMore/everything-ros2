#!/bin/bash

# Script to validate URDF files for ROS 1 and ROS 2

echo "Validating ROS 1 URDF..."
if command -v check_urdf &> /dev/null; then
    check_urdf /home/ritz/everything-ros2-claude-code/ros2_conversion_examples/simple_robot_ros1.urdf
    if [ $? -eq 0 ]; then
        echo "✓ ROS 1 URDF is valid"
    else
        echo "✗ ROS 1 URDF validation failed"
    fi
else
    echo "⚠ check_urdf command not found. Install with: sudo apt-get install liburdfdom-tools"
fi

echo ""
echo "Validating ROS 2 URDF..."
if command -v check_urdf &> /dev/null; then
    check_urdf /home/ritz/everything-ros2-claude-code/ros2_conversion_examples/simple_robot_ros2.urdf
    if [ $? -eq 0 ]; then
        echo "✓ ROS 2 URDF is valid"
    else
        echo "✗ ROS 2 URDF validation failed"
    fi
else
    echo "⚠ check_urdf command not found. Install with: sudo apt-get install liburdfdom-tools"
fi

echo ""
echo "Checking for ros2_control tags in ROS 2 file..."
if grep -q "<ros2_control" /home/ritz/everything-ros2-claude-code/ros2_conversion_examples/simple_robot_ros2.urdf; then
    echo "✓ Found ros2_control tags in ROS 2 URDF"
else
    echo "✗ Missing ros2_control tags in ROS 2 URDF"
fi

echo ""
echo "Checking for Gazebo plugins..."
if grep -q "<gazebo>" /home/ritz/everything-ros2-claude-code/ros2_conversion_examples/simple_robot_ros2.urdf; then
    echo "✓ Found Gazebo plugin definitions"
else
    echo "✗ Missing Gazebo plugin definitions"
fi

echo ""
echo "Validation complete."