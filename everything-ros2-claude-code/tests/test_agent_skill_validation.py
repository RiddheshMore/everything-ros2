#!/usr/bin/env python3
"""Validate all agent and skill markdown files have proper frontmatter and content."""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)
AGENTS_DIR = os.path.join(BASE, "agents")
SKILLS_DIR = os.path.join(BASE, "skills")
EXAMPLES_DIR = os.path.join(BASE, "examples")

def validate_frontmatter(path):
    """Check file has valid YAML frontmatter."""
    with open(path) as f:
        content = f.read()
    if not content.startswith("---"):
        return False, "Missing frontmatter"
    parts = content[3:].split("---", 1)
    if len(parts) < 2:
        return False, "Unclosed frontmatter"
    return True, "OK"

def validate_agent(path):
    """Validate an agent file."""
    with open(path) as f:
        content = f.read()

    issues = []
    if not re.search(r"^name:", content, re.M):
        issues.append("Missing 'name:' field")
    if not re.search(r"^description:", content, re.M):
        issues.append("Missing 'description:' field")
    if not re.search(r"^tools:", content, re.M):
        issues.append("Missing 'tools:' field")
    if len(content) < 200:
        issues.append("Content too short (<200 chars)")
    return issues

def validate_skill(path):
    """Validate a skill file."""
    with open(path) as f:
        content = f.read()

    issues = []
    if not re.search(r"^name:", content, re.M):
        issues.append("Missing 'name:' field")
    if not re.search(r"^description:", content, re.M):
        issues.append("Missing 'description:' field")
    if not re.search(r"^triggers:", content, re.M):
        issues.append("Missing 'triggers:' field")
    if not re.search(r"## ", content):
        issues.append("Missing '##' headers (no sections)")
    if len(content) < 300:
        issues.append("Content too short (<300 chars)")
    return issues

def validate_example(path):
    """Validate an example README."""
    with open(path) as f:
        content = f.read()

    issues = []
    if len(content) < 100:
        issues.append("Content too short (<100 chars)")
    if not re.search(r"^# ", content, re.M):
        issues.append("Missing H1 title")
    return issues

def main():
    passed = 0
    failed = 0
    errors = []

    # Test agents
    for fname in sorted(os.listdir(AGENTS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(AGENTS_DIR, fname)
        fm_ok, fm_msg = validate_frontmatter(path)
        if not fm_ok:
            errors.append(f"AGENT {fname}: {fm_msg}")
            failed += 1
            continue
        issues = validate_agent(path)
        if issues:
            for issue in issues:
                errors.append(f"AGENT {fname}: {issue}")
            failed += 1
        else:
            passed += 1

    # Test skills
    for dname in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, dname, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        fm_ok, fm_msg = validate_frontmatter(skill_path)
        if not fm_ok:
            errors.append(f"SKILL {dname}: {fm_msg}")
            failed += 1
            continue
        issues = validate_skill(skill_path)
        if issues:
            for issue in issues:
                errors.append(f"SKILL {dname}: {issue}")
            failed += 1
        else:
            passed += 1

    # Test examples
    for dname in sorted(os.listdir(EXAMPLES_DIR)):
        readme_path = os.path.join(EXAMPLES_DIR, dname, "README.md")
        if not os.path.isfile(readme_path):
            errors.append(f"EXAMPLE {dname}: Missing README.md")
            failed += 1
            continue
        issues = validate_example(readme_path)
        if issues:
            for issue in issues:
                errors.append(f"EXAMPLE {dname}: {issue}")
            failed += 1
        else:
            passed += 1

    print(f"=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if errors:
        print("=== Errors ===")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
