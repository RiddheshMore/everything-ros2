# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in everything-ros2-claude-code, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, create a private security advisory or contact the maintainers directly.

Please include:

- A description of the vulnerability
- Steps to reproduce
- The affected version(s)
- Any potential impact assessment

You can expect:

- **Acknowledgment** within 48 hours
- **Status update** within 7 days
- **Fix or mitigation** within 30 days for critical issues

If the vulnerability is accepted, we will:

- Credit you in the release notes (unless you prefer anonymity)
- Fix the issue in a timely manner
- Coordinate disclosure timing with you

If the vulnerability is declined, we will explain why and provide guidance on whether it should be reported elsewhere.

## Scope

This policy covers:

- All agents in the `agents/` directory
- All skills in the `skills/` directory
- Hook scripts in the `hooks/` directory
- Install/uninstall lifecycle scripts
- MCP configurations shipped with this project

## Security Resources

- **SROS2 Documentation**: [ROS 2 Security](https://docs.ros.org/en/humble/Tutorials/Security/Introducing-ros2-security.html)
- **ROS 2 Security Best Practices**: Refer to the `sros2-secops` agent
- **OWASP Top 10**: [owasp.org](https://owasp.org/www-project-top-ten/)

## Security in ROS 2 Development

When using these agents for ROS 2 development, always follow security best practices:

1. **Never hardcode secrets** in URDF, launch files, or code
2. **Use SROS2** for encrypted communications in production
3. **Validate all inputs** before processing
4. **Use parameter files** instead of hardcoded values
5. **Enable security logging** for audit trails
6. **Review generated code** before deployment to robots

The `sros2-secops` agent can help you implement these practices in your ROS 2 projects.
