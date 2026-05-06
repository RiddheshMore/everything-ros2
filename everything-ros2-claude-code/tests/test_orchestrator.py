#!/usr/bin/env python3
"""
Test the ros2-orchestrator agent routing
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_orchestrator_delegation():
    """Test that orchestrator has delegation rules for new agents"""
    orchestrator_path = project_root / "agents" / "ros2-orchestrator.md"

    if not orchestrator_path.exists():
        print("❌ ros2-orchestrator.md not found")
        return False

    with open(orchestrator_path, 'r') as f:
        content = f.read()

    # Check for delegation rules for new agents
    delegation_rules = [
        "Hardware compatibility or drivers → delegate to @hardware-compat-agent",
        "ros2_control framework → delegate to @ros2-control-agent",
        "Safety systems (ESTOP, collision detection) → delegate to @safety-agent",
        "Real-time performance tuning → delegate to @realtime-agent",
        "Ubuntu system configuration → delegate to @ubuntu-system-agent"
    ]

    print("Testing Orchestrator Delegation Rules")
    print("=" * 50)

    all_found = True
    for rule in delegation_rules:
        found = rule in content
        status = "✅ PASS" if found else "❌ FAIL"
        print(f"{status} {rule}")
        if not found:
            all_found = False

    return all_found

def test_orchestrator_structure():
    """Test basic orchestrator structure"""
    orchestrator_path = project_root / "agents" / "ros2-orchestrator.md"

    if not orchestrator_path.exists():
        print("❌ ros2-orchestrator.md not found")
        return False

    with open(orchestrator_path, 'r') as f:
        content = f.read()

    required_elements = [
        "name: ros2-orchestrator",
        "description:",
        "tools:",
        "You are the ROS 2 master orchestrator"
    ]

    print("\nTesting Orchestrator Structure")
    print("=" * 50)

    all_found = True
    for element in required_elements:
        found = element in content
        status = "✅ PASS" if found else "❌ FAIL"
        print(f"{status} Contains '{element}'")
        if not found:
            all_found = False

    return all_found

def main():
    """Run orchestrator tests"""
    print("Testing ROS 2 Orchestrator")
    print("=" * 60)

    structure_ok = test_orchestrator_structure()
    delegation_ok = test_orchestrator_delegation()

    if structure_ok and delegation_ok:
        print(f"\n{'='*60}")
        print("🎉 Orchestrator tests passed!")
        return 0
    else:
        print(f"\n{'='*60}")
        print("❌ Some orchestrator tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())