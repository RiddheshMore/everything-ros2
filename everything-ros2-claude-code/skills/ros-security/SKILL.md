---
name: ros-security
description: SROS2 security, DDS security, node permissions, and secure communication in ROS 2
triggers:
  - security
  - sros2
  - DDS security
  - access control
  - encryption
  - keystore
  - permissions
  - SROS
---

# ROS 2 Security (SROS2)

## Overview

ROS 2 uses DDS Security to provide:
- **Authentication**: PKI-based node identity
- **Encryption**: RTPS traffic encrypted with AES-256-GCM
- **Access Control**: Per-node publish/subscribe/call permissions

## Setup SROS2 Keystore

```bash
# Install SROS2 tools
sudo apt install ros-humble-sros2

# Create keystore (do this once per system/project)
ros2 security create_keystore ~/ros2_security_keystore

# Create keys for each node
ros2 security create_enclave ~/ros2_security_keystore /my_robot/talker
ros2 security create_enclave ~/ros2_security_keystore /my_robot/listener
ros2 security create_enclave ~/ros2_security_keystore /my_robot/controller
```

## Permissions File (XML)

```xml
<!-- policies/policy.xml -->
<policy version="0.2.0">
  <enclaves>
    <!-- Talker node can only publish to /chatter -->
    <enclave path="/my_robot/talker">
      <profiles>
        <profile ns="/" node="talker">
          <topics publish="ALLOW" subscribe="DENY">
            <topic>chatter</topic>
          </topics>
          <services reply="DENY" request="DENY">
            <service>*</service>
          </services>
          <actions call="DENY" execute="DENY">
            <action>*</action>
          </actions>
        </profile>
      </profiles>
    </enclave>

    <!-- Listener can only subscribe -->
    <enclave path="/my_robot/listener">
      <profiles>
        <profile ns="/" node="listener">
          <topics publish="DENY" subscribe="ALLOW">
            <topic>chatter</topic>
          </topics>
          <services reply="DENY" request="DENY">
            <service>*</service>
          </services>
          <actions call="DENY" execute="DENY">
            <action>*</action>
          </actions>
        </profile>
      </profiles>
    </enclave>
  </enclaves>
</policy>
```

```bash
# Generate security files from policy
ros2 security create_permission ~/ros2_security_keystore \
  /my_robot/talker policies/policy.xml
ros2 security create_permission ~/ros2_security_keystore \
  /my_robot/listener policies/policy.xml
```

## Environment Variables for Secure Launch

```bash
export ROS_SECURITY_KEYSTORE=~/ros2_security_keystore
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce  # or "Permissive" for testing

# Run node with security
ros2 run my_pkg my_node --ros-args \
  --enclave /my_robot/talker
```

## Secure Launch File

```python
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    keystore = os.environ.get('ROS_SECURITY_KEYSTORE',
                              os.path.expanduser('~/ros2_security_keystore'))

    security_env = {
        'ROS_SECURITY_KEYSTORE': keystore,
        'ROS_SECURITY_ENABLE': 'true',
        'ROS_SECURITY_STRATEGY': 'Enforce',
    }

    return LaunchDescription([
        Node(
            package='my_pkg',
            executable='talker',
            name='talker',
            namespace='my_robot',
            additional_env=security_env,
            arguments=['--ros-args', '--enclave', '/my_robot/talker'],
        ),
        Node(
            package='my_pkg',
            executable='listener',
            name='listener',
            namespace='my_robot',
            additional_env=security_env,
            arguments=['--ros-args', '--enclave', '/my_robot/listener'],
        ),
    ])
```

## Network Isolation with DDS

```xml
<!-- fastdds_profile.xml — restrict DDS to specific network interface -->
<?xml version="1.0" encoding="UTF-8"?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <profiles>
    <transport_descriptors>
      <transport_descriptor>
        <transport_id>udp_lan</transport_id>
        <type>UDPv4</type>
        <interfaceWhiteList>
          <address>192.168.1.0/24</address>
        </interfaceWhiteList>
      </transport_descriptor>
    </transport_descriptors>
    <participant profile_name="default_profile" is_default_profile="true">
      <rtps>
        <userTransports>
          <transport_id>udp_lan</transport_id>
        </userTransports>
        <useBuiltinTransports>false</useBuiltinTransports>
      </rtps>
    </participant>
  </profiles>
</dds>
```

```bash
export FASTRTPS_DEFAULT_PROFILES_FILE=fastdds_profile.xml
```

## ROS_DOMAIN_ID Isolation

```bash
# Isolate robot from other ROS 2 systems on same network
# Use unique domain IDs (0-232) per robot/project
export ROS_DOMAIN_ID=42

# In launch file
Node(
    ...
    additional_env={'ROS_DOMAIN_ID': '42'},
)
```

## Security Checklist

```
□ Each node has its own enclave (not shared keys)
□ permissions.xml uses DENY by default, ALLOW only needed topics
□ ROS_SECURITY_STRATEGY=Enforce in production (not Permissive)
□ Keystore NOT checked into version control (.gitignore it)
□ ROS_DOMAIN_ID set to non-default (not 0) in production
□ DDS traffic restricted to internal network interface
□ Keystore permissions: chmod 700 ~/ros2_security_keystore
□ Certificate rotation plan documented
□ Logging of security violations enabled
```

## Checking Security Status

```bash
# Verify security is active
ros2 security list_enclaves ~/ros2_security_keystore

# Check node is using security
ros2 node info /my_robot/talker  # should show encrypted endpoint

# Test without security (Permissive mode for dev)
export ROS_SECURITY_STRATEGY=Permissive
```
