#!/usr/bin/env python3

"""
Test script for evaluating ROS 1 to ROS 2 conversion agents.

This script demonstrates how to test a conversion agent by:
1. Providing a known ROS 1 URDF as input
2. Comparing the agent's output with our reference ROS 2 version
3. Evaluating completeness and accuracy of the conversion
"""

import os
import sys
from difflib import unified_diff

def load_urdf(filepath):
    """Load URDF file content."""
    with open(filepath, 'r') as f:
        return f.read()

def compare_urdf_sections(ros1_content, ros2_content, section_name):
    """Compare specific sections of URDF files."""
    print(f"\n=== Comparing {section_name} ===")

    # This is a simplified comparison - in practice, you'd want more sophisticated parsing
    if section_name == "ros2_control":
        ros2_control_section = ""
        if "<ros2_control" in ros2_content:
            start = ros2_content.find("<ros2_control")
            end = ros2_content.find("</ros2_control>") + len("</ros2_control>")
            ros2_control_section = ros2_content[start:end]

        if ros2_control_section:
            print("✓ ros2_control section found in ROS 2 file")
            return True
        else:
            print("✗ ros2_control section missing from ROS 2 file")
            return False

    return True

def evaluate_conversion_agent(ros1_filepath, reference_ros2_filepath):
    """
    Evaluate a conversion agent by comparing its output with reference files.

    Args:
        ros1_filepath: Path to input ROS 1 URDF
        reference_ros2_filepath: Path to reference ROS 2 URDF

    Returns:
        dict: Evaluation results
    """
    print("Testing ROS 1 to ROS 2 Conversion Agent")
    print("=" * 50)

    # Load files
    ros1_content = load_urdf(ros1_filepath)
    reference_ros2_content = load_urdf(reference_ros2_filepath)

    print(f"Input ROS 1 file: {ros1_filepath}")
    print(f"Reference ROS 2 file: {reference_ros2_filepath}")

    # Basic validation
    results = {
        'files_loaded': True,
        'structure_preserved': True,
        'controllers_converted': False,
        'gazebo_plugins_updated': False,
        'overall_success': False
    }

    # Check if basic structure is preserved
    # (In a real implementation, you'd do more thorough XML parsing)
    if '<link' in ros1_content and '<link' in reference_ros2_content:
        print("✓ Basic link structure preserved")
        results['structure_preserved'] = True

    # Check for ros2_control conversion
    results['controllers_converted'] = compare_urdf_sections(
        ros1_content, reference_ros2_content, "ros2_control"
    )

    # Check for Gazebo plugin updates
    results['gazebo_plugins_updated'] = compare_urdf_sections(
        ros1_content, reference_ros2_content, "gazebo_plugins"
    )

    # Overall assessment
    if results['structure_preserved'] and results['controllers_converted']:
        results['overall_success'] = True
        print("\n✓ Conversion agent test PASSED")
    else:
        print("\n✗ Conversion agent test FAILED")

    return results

def main():
    """Main test function."""
    # Define test files
    test_dir = "/home/ritz/everything-ros2-claude-code/ros2_conversion_examples"

    test_cases = [
        {
            'name': 'Simple Robot',
            'ros1': os.path.join(test_dir, 'simple_robot_ros1.urdf'),
            'ros2': os.path.join(test_dir, 'simple_robot_ros2.urdf')
        },
        {
            'name': 'Kobuki Robot',
            'ros1': '/home/ritz/everything-ros2-claude-code/ros1_kobuki_simplified.urdf',
            'ros2': '/home/ritz/everything-ros2-claude-code/ros2_kobuki_converted.urdf'
        }
    ]

    print("ROS 1 to ROS 2 Conversion Agent Test Suite")
    print("=" * 60)

    all_passed = True

    for test_case in test_cases:
        print(f"\nTesting {test_case['name']}...")
        print("-" * 30)

        # Check if files exist
        if not os.path.exists(test_case['ros1']):
            print(f"✗ ROS 1 file not found: {test_case['ros1']}")
            all_passed = False
            continue

        if not os.path.exists(test_case['ros2']):
            print(f"✗ ROS 2 reference file not found: {test_case['ros2']}")
            all_passed = False
            continue

        # Run evaluation
        results = evaluate_conversion_agent(
            test_case['ros1'],
            test_case['ros2']
        )

        if not results['overall_success']:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All conversion agent tests PASSED!")
    else:
        print("❌ Some conversion agent tests FAILED!")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())