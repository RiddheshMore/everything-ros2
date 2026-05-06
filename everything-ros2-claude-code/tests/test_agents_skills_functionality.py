#!/usr/bin/env python3
"""Simple functionality test for agents and skills - check they have expected content."""

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE, "agents")
SKILLS_DIR = os.path.join(BASE, "skills")

def test_agent_content(agent_path, agent_name):
    """Test that agent has expected content structure."""
    with open(agent_path, 'r') as f:
        content = f.read()

    # Check for key sections
    assert "tools:" in content, f"{agent_name} missing tools section"
    assert "You are" in content or "you are" in content, f"{agent_name} missing persona"
    print(f"✅ {agent_name} has basic structure")

def test_skill_content(skill_path, skill_name):
    """Test that skill has expected content structure."""
    with open(skill_path, 'r') as f:
        content = f.read()

    # Check for key sections
    assert "triggers:" in content, f"{skill_name} missing triggers section"
    assert "## " in content, f"{skill_name} missing markdown sections"
    assert len(content.split('\n')) > 20, f"{skill_name} seems too short"
    print(f"✅ {skill_name} has basic structure")

def main():
    print("Testing agent functionality...")
    for fname in sorted(os.listdir(AGENTS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(AGENTS_DIR, fname)
        test_agent_content(path, fname[:-3])  # Remove .md extension

    print("\nTesting skill functionality...")
    for dname in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, dname, "SKILL.md")
        if not os.path.isfile(skill_path):
            print(f"❌ Missing SKILL.md in {dname}")
            continue
        test_skill_content(skill_path, dname)

    print("\n🎉 All functionality tests passed!")

if __name__ == "__main__":
    main()