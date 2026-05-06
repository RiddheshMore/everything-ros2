---
name: systemd-ros2
description: systemd for ROS 2 — robot services, boot management, logging, restart policies, user setup
triggers:
  - systemd
  - service
  - boot
  - systemctl
  - daemon
  - startup
  - autostart
  - journalctl
---

# systemd for ROS 2 Robots

## Quick-Reference Decision Table

| Scenario | Service Type | Restart Policy | User |
|---------|-------------|----------------|------|
| Robot bringup | oneshot + persistent | no | robot |
| Sensor node | simple | always | robot |
| Camera stream | simple | on-failure | robot |
| Critical safety | oneshot | no | root |
| Development | simple | no | developer |

---

## Complete Copy-Paste Code

### 1. Basic Robot Bringup Service

```ini
# /etc/systemd/system/robot-bringup.service
[Unit]
Description=Robot Bringup Service
After=network-online.target
Wants=network-online.target
# Ensures network is ready before starting

[Service]
Type=oneshot
RemainAfterExit=yes
# "oneshot" = runs once and exits
# "RemainAfterExit=yes" = consider "active" even after exit

# Run as robot user, not root
User=robot
Group=robot

# Environment setup
Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="HOME=/home/robot"

# Working directory
WorkingDirectory=/home/robot/ros2_ws

# Source ROS 2 and launch
# CRITICAL: All in one command with &&
ExecStartPre=/bin/bash -c 'source /opt/ros/${ROS_DISTRO}/setup.bash && source ${HOME}/ros2_ws/install/setup.bash'
ExecStart=/bin/bash -c 'source /opt/ros/${ROS_DISTRO}/setup.bash && source ${HOME}/ros2_ws/install/setup.bash && ros2 launch robot_bringup bringup.launch.py'

# If bringup fails, do NOT restart automatically
Restart=no

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-bringup

[Install]
WantedBy=multi-user.target
# Starts on boot
```

### 2. Persistent Node Service (with auto-restart)

```ini
# /etc/systemd/system/robot-sensor.service
[Unit]
Description=ROS 2 Sensor Node
After=network.target
# Start after network is up

[Service]
Type=simple
# "simple" = runs continuously, monitor by PID

User=robot
Group=robot

Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="LD_LIBRARY_PATH=/opt/ros/humble/lib:$LD_LIBRARY_PATH"

WorkingDirectory=/home/robot/ros2_ws

# Source and run node
ExecStart=/bin/bash -c '\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source ${HOME}/ros2_ws/install/setup.bash && \
    ros2 run sensor_driver lidar_node'

# Auto-restart on failure
Restart=always
RestartSec=5
# "always" = restart immediately after exit (normal or crash)
# "on-failure" = only restart on abnormal exit
# "Sec" = wait 5 seconds before restart (prevents rapid restart loops)

# Prevent rapid restart loops (3 restarts in 60s = stop)
StartLimitInterval=60
StartLimitBurst=3

# Graceful shutdown
TimeoutStopSec=30
KillSignal=SIGINT
# Send SIGINT first, then SIGKILL after 30s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-sensor

[Install]
WantedBy=multi-user.target
```

### 3. Multi-Node Service with Dependencies

```ini
# /etc/systemd/system/robot-control.service
[Unit]
Description=Robot Control System
After=network.target
Wants=network.target

# Dependencies: hardware must be ready
# After=machine-info.target local-fs.target

[Service]
Type=simple
User=robot
Group=robot

Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="RMW_IMPLEMENTATION=rmw_cyclonedds_cpp"

WorkingDirectory=/home/robot/ros2_ws

ExecStart=/bin/bash -c '\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source ${HOME}/ros2_ws/install/setup.bash && \
    ros2 launch robot_control control.launch.py'

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
TimeoutStopSec=30

StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-control

[Install]
WantedBy=multi-user.target
```

### 4. Template Service (Per-User Installed)

```ini
# ~/.config/systemd/user/robot-node.service
[Unit]
Description=ROS 2 Node for %u
# %u = username from instance name (robot-node@username)

After=network.target
DefaultDependencies=no
# For user services, don't wait for system basic.target

[Service]
Type=simple
Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"

# Source workspace
ExecStart=/bin/bash -c '\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source /home/%u/ros2_ws/install/setup.bash && \
    ros2 run my_package my_node'

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-node-%u

[Install]
WantedBy=default.target
# "default.target" = user session target
```

```bash
# Enable for specific user
sudo -u robot systemctl --user enable robot-node.service
sudo -u robot systemctl --user start robot-node.service

# Or enable with template (replace USERNAME)
sudo systemctl enable robot-node@USERNAME.service
sudo systemctl start robot-node@USERNAME.service
```

### 5. Install and Manage Service

```bash
# Install service
sudo cp robot-bringup.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable (start on boot)
sudo systemctl enable robot-bringup.service

# Start now
sudo systemctl start robot-bringup.service

# Check status
sudo systemctl status robot-bringup.service

# View logs
sudo journalctl -u robot-bringup.service -f
sudo journalctl -u robot-bringup.service --since "10 minutes ago"

# Restart
sudo systemctl restart robot-bringup.service

# Stop
sudo systemctl stop robot-bringup.service

# Disable (don't start on boot)
sudo systemctl disable robot-bringup.service

# Remove
sudo systemctl stop robot-bringup.service
sudo systemctl disable robot-bringup.service
sudo rm /etc/systemd/system/robot-bringup.service
sudo systemctl daemon-reload
```

### 6. Log Management

```bash
# View all robot service logs
sudo journalctl -u robot-*

# Limit log size (in /etc/systemd/journald.conf)
[Journal]
SystemMaxUse=500M
MaxFileSec=1week
# Keep last 500MB of logs, rotate weekly

# Clean old logs
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=7days

# Export logs
sudo journalctl -u robot-bringup.service > robot-bringup.log
```

### 7. Service Dependency Debugging

```bash
# Check why service didn't start
systemctl status robot-bringup.service
systemctl list-dependencies robot-bringup.service
systemctl --failed

# Simulate network-online.target
sudo networkctl status

# Check if user services work
sudo -u robot --login systemctl --user status
```

---

## Common Mistakes

### WRONG: Source commands on separate lines

```ini
# ❌ BAD - Each line starts a new shell, only last one applies
ExecStartPre=/bin/bash -c 'source /opt/ros/humble/setup.bash'
ExecStartPre=/bin/bash -c 'source /home/robot/ros2_ws/install/setup.bash'
ExecStart=/bin/bash -c 'ros2 run my_pkg my_node'
# Result: ros2 command not found!
```

### CORRECT: Chain in single command

```ini
# ✅ GOOD - All in one shell
ExecStart=/bin/bash -c '\
    source /opt/ros/humble/setup.bash && \
    source /home/robot/ros2_ws/install/setup.bash && \
    ros2 run my_pkg my_node'
```

### WRONG: No User specified

```ini
# ❌ BAD - Runs as root, breaks /home/robot permissions
```

```ini
# ✅ GOOD
User=robot
Group=robot
```

### WRONG: Restart without delay

```ini
# ❌ BAD - Crash loop destroys hardware
Restart=always
```

```ini
# ✅ GOOD - Delay prevents crash loops
Restart=always
RestartSec=5
StartLimitBurst=3
```

---

## Boot Order Debug

```bash
# Check boot time
systemd-analyze
systemd-analyze blame
# Shows which services take longest to start
```
