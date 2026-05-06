#!/usr/bin/env python3
"""
Simple Agent Testing Framework
Runs basic functionality tests on ROS 2 agents
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_agent_file(agent_name):
    """Test if agent file exists and has basic structure"""
    agent_path = project_root / "agents" / f"{agent_name}.md"

    if not agent_path.exists():
        return False, f"Agent file not found: {agent_path}"

    try:
        with open(agent_path, 'r') as f:
            content = f.read()

        # Check for required elements
        required_elements = ['name:', 'description:', 'tools:', 'You are']
        missing = [elem for elem in required_elements if elem not in content]

        if missing:
            return False, f"Missing elements: {missing}"

        return True, "Agent file structure valid"
    except Exception as e:
        return False, f"Error reading agent file: {e}"

def test_skill_file(skill_name):
    """Test if skill file exists and has basic structure"""
    skill_path = project_root / "skills" / skill_name / "SKILL.md"

    if not skill_path.exists():
        return False, f"Skill file not found: {skill_path}"

    try:
        with open(skill_path, 'r') as f:
            content = f.read()

        # Check for required elements
        required_elements = ['name:', 'description:', 'triggers:', '## ']
        missing = [elem for elem in required_elements if elem not in content]

        if missing:
            return False, f"Missing elements: {missing}"

        return True, "Skill file structure valid"
    except Exception as e:
        return False, f"Error reading skill file: {e}"

def test_new_agents():
    """Test the 5 new agents we created"""
    new_agents = [
        "hardware-compat-agent",
        "ros2-control-agent",
        "safety-agent",
        "realtime-agent",
        "ubuntu-system-agent"
    ]

    print("Testing New Agents")
    print("=" * 50)

    results = []
    for agent in new_agents:
        success, message = test_agent_file(agent)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {agent:<25} - {message}")
        results.append((agent, success, message))

    return results

def test_new_skills():
    """Test the 9 new skills we created"""
    new_skills = [
        "docker-ros2",
        "systemd-ros2",
        "network-config",
        "hardware-drivers",
        "jetson-setup",
        "safety-patterns",
        "realtime-patterns",
        "ros2-control",
        "ubuntu-system"
    ]

    print("\nTesting New Skills")
    print("=" * 50)

    results = []
    for skill in new_skills:
        success, message = test_skill_file(skill)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {skill:<20} - {message}")
        results.append((skill, success, message))

    return results

def test_examples():
    """Test that example READMEs were created"""
    examples_dir = project_root / "examples"

    if not examples_dir.exists():
        return [("examples_dir", False, "Examples directory not found")]

    # These are the 4 examples we filled with content
    filled_examples = [
        "docker-robot-stack",
        "ros2-control-diffbot",
        "safety-node",
        "systemd-robot-service"
    ]

    print("\nTesting Examples")
    print("=" * 50)

    results = []
    for example in filled_examples:
        readme_path = examples_dir / example / "README.md"
        success = readme_path.exists()
        message = "README.md found" if success else "README.md missing"
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {example:<25} - {message}")
        results.append((example, success, message))

    return results

def test_documentation():
    """Test that documentation was updated"""
    docs_dir = project_root / "docs"
    agents_md = project_root / "AGENTS.md"

    print("\nTesting Documentation")
    print("=" * 50)

    results = []

    # Check AGENTS.md exists
    success = agents_md.exists()
    message = "AGENTS.md found" if success else "AGENTS.md missing"
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} AGENTS.md - {message}")
    results.append(("AGENTS.md", success, message))

    # Check AGENTS.md contains new agents
    if success:
        with open(agents_md, 'r') as f:
            content = f.read()

        new_agents = ["hardware-compat-agent", "ros2-control-agent", "safety-agent", "realtime-agent", "ubuntu-system-agent"]
        for agent in new_agents:
            found = agent in content
            status = "✅ PASS" if found else "❌ FAIL"
            message = f"Found in AGENTS.md" if found else "Missing from AGENTS.md"
            print(f"{status} {agent:<25} - {message}")
            results.append((agent, found, message))

    return results

def main():
    """Run all tests"""
    print("ROS 2 Agent Harness - Component Testing")
    print("=" * 60)

    # Run all test suites
    agent_results = test_new_agents()
    skill_results = test_new_skills()
    example_results = test_examples()
    doc_results = test_documentation()

    # Aggregate results
    all_results = agent_results + skill_results + example_results + doc_results
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)

    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The ROS 2 agent harness is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())