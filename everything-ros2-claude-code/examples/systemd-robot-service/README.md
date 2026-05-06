# systemd Robot Service

systemd services for ROS 2 robot bringup, auto-restart, user isolation, and boot management.

## Structure

```
systemd-robot-service/
├── README.md
├── robot-bringup.service    # Oneshot bringup service
├── robot-sensor.service     # Persistent sensor with auto-restart
├── robot-control.service    # Control system with dependencies
├── robot-node@.service     # Template for per-user nodes
├── scripts/
│   └── setup-services.sh   # Service installation script
└── logrotate.conf          # Log rotation config
```

## Robot Bringup Service

```ini
# robot-bringup.service
[Unit]
Description=Robot Bringup Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=robot
Group=robot

Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="HOME=/home/robot"

WorkingDirectory=/home/robot/ros2_ws

ExecStartPre=/bin/bash -c 'source /opt/ros/${ROS_DISTRO}/setup.bash && source ${HOME}/ros2_ws/install/setup.bash'
ExecStart=/bin/bash -c 'source /opt/ros/${ROS_DISTRO}/setup.bash && source ${HOME}/ros2_ws/install/setup.bash && ros2 launch robot_bringup bringup.launch.py'

Restart=no

StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-bringup

[Install]
WantedBy=multi-user.target
```

## Persistent Sensor Service (Auto-Restart)

```ini
# robot-sensor.service
[Unit]
Description=ROS 2 Sensor Node
After=network.target

[Service]
Type=simple
User=robot
Group=robot

Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="LD_LIBRARY_PATH=/opt/ros/humble/lib:$LD_LIBRARY_PATH"

WorkingDirectory=/home/robot/ros2_ws

ExecStart=/bin/bash -c '\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source ${HOME}/ros2_ws/install/setup.bash && \
    ros2 run sensor_driver lidar_node'

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
TimeoutStopSec=30
KillSignal=SIGINT

StandardOutput=journal
StandardError=journal
SyslogIdentifier=robot-sensor

[Install]
WantedBy=multi-user.target
```

## Control System Service (Multi-Dependency)

```ini
# robot-control.service
[Unit]
Description=Robot Control System
After=network.target
Wants=network.target

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

## Per-User Node Template

```ini
# robot-node@.service
[Unit]
Description=ROS 2 Node for %u
After=network.target
DefaultDependencies=no

[Service]
Type=simple
Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"

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
```

## Installation Script

```bash
#!/bin/bash
# setup-services.sh

set -e

SERVICE_DIR="/etc/systemd/system"
USER="robot"

# Install services
sudo cp robot-bringup.service ${SERVICE_DIR}/
sudo cp robot-sensor.service ${SERVICE_DIR}/
sudo cp robot-control.service ${SERVICE_DIR}/

# Create symlink for template
sudo ln -sf robot-node@.service /etc/systemd/system/multi-user.target.wants/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable robot-bringup.service
sudo systemctl enable robot-sensor.service
sudo systemctl enable robot-control.service

echo "Services installed and enabled"
```

## Log Management

```bash
# View all robot logs
sudo journalctl -u robot-*

# View with filter
sudo journalctl -u robot-sensor.service -f
sudo journalctl -u robot-bringup.service --since "1 hour ago"

# Log rotation (add to /etc/logrotate.d/robot)
/var/log/robot/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 0644 robot robot
}
```

## Service Management

```bash
# Start/stop
sudo systemctl start robot-bringup.service
sudo systemctl stop robot-sensor.service

# Check status
sudo systemctl status robot-sensor.service

# Restart
sudo systemctl restart robot-control.service

# Disable (don't start on boot)
sudo systemctl disable robot-sensor.service

# Remove
sudo systemctl stop robot-sensor.service
sudo systemctl disable robot-sensor.service
sudo rm /etc/systemd/system/robot-sensor.service
sudo systemctl daemon-reload
```

## Debugging

```bash
# Why service didn't start
systemctl status robot-bringup.service
systemctl list-dependencies robot-bringup.service
systemctl --failed

# Boot time analysis
systemd-analyze
systemd-analyze blame

# Simulate network-online.target
sudo networkctl status

# Test as user
sudo -u robot --login systemctl --user status
```

## Common Issues

### WRONG: Source on separate lines
```ini
# ❌ BAD - Each line starts new shell, only last applies
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

### CORRECT: Explicit User/Group
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

### CORRECT: Delay prevents crash loops
```ini
# ✅ GOOD
Restart=always
RestartSec=5
StartLimitBurst=3
```

## Run

```bash
# Install services
sudo bash scripts/setup-services.sh

# Check status
sudo systemctl status robot-bringup.service

# View logs
sudo journalctl -u robot-bringup.service -f
```
