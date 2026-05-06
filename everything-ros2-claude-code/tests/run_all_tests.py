#!/usr/bin/env python3
"""
Comprehensive Test Runner for ROS 2 Agent Harness
Runs all validation and functionality tests
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test_script(script_name):
    """Run a test script and return success/failure"""
    try:
        result = subprocess.run([sys.executable, script_name],
                              cwd=str(project_root / "tests"),
                              capture_output=True,
                              text=True,
                              timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out"
    except Exception as e:
        return False, "", str(e)

def main():
    """Run all test suites"""
    print("ROS 2 Agent Harness - Comprehensive Test Suite")
    print("=" * 60)

    # Test scripts to run
    test_scripts = [
        ("Component Tests", "run_agent_tests.py"),
        ("Orchestrator Tests", "test_orchestrator.py"),
        ("Validation Tests", "test_agent_skill_validation.py"),
        ("Functionality Tests", "test_agents_skills_functionality.py")
    ]

    results = []

    for test_name, script_name in test_scripts:
        print(f"\nRunning {test_name} ({script_name})...")
        print("-" * 40)

        success, stdout, stderr = run_test_script(script_name)

        if success:
            print("✅ PASSED")
            # Print brief output
            if stdout.strip():
                lines = stdout.strip().split('\n')
                for line in lines[-5:]:  # Show last 5 lines
                    print(f"  {line}")
        else:
            print("❌ FAILED")
            if stderr.strip():
                print(f"  Error: {stderr.strip()}")
            elif stdout.strip():
                lines = stdout.strip().split('\n')
                for line in lines[-3:]:  # Show last 3 lines
                    print(f"  {line}")

        results.append((test_name, success))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUITE SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 All test suites passed! The ROS 2 agent harness is working correctly.")
        return 0
    else:
        print("\n❌ Some test suites failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())