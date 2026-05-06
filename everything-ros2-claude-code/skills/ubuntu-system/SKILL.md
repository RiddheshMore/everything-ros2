---
name: ubuntu-system
description: Ubuntu system configuration for ROS 2 — shell setup, udev rules, systemd services, permissions
triggers:
  - ubuntu
  - setup.bash
  - source
  - permission denied
  - /dev/ttyUSB
  - systemd
  - udev
  - dialout
  - /opt/ros
---

# Ubuntu System Setup for ROS 2

## Quick-Reference Decision Table

| Problem | Check | Solution |
|---------|-------|----------|
| `ros2: command not found` | `echo $ROS_DISTRO` | Source `/opt/ros/*/setup.bash` |
| `Permission denied: /dev/ttyUSB0` | `groups $USER` | `sudo usermod -aG dialout $USER` |
| Package not found after build | `echo $AMENT_PREFIX_PATH` | Source workspace `install/setup.bash` |
| Service fails on boot | `systemctl status my.service` | Check User=, Environment=, ExecStart= |
| Serial device keeps changing | `ls -la /dev/serial/by-id/` | Use /dev/serial/by-id/ symlinks |

---

## Complete Copy-Paste Code

### 1. ~/.bashrc ROS 2 Setup (CORRECT ORDER)

```bash
# At the BOTTOM of ~/.bashrc:

# ROS 2 distribution - change for Jazzy, etc.
export ROS_DISTRO=humble

# Source ROS 2 underlay FIRST
source /opt/ros/${ROS_DISTRO}/setup.bash

# Source workspace overlay SECOND (if exists)
if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
    source $HOME/ros2_ws/install/setup.bash
fi

# Colcon aliases for convenience
alias cb='colcon build --symlink-install'
alias cbs='colcon build --symlink-install && source install/setup.bash'

# ROS 2 domain (for multi-robot)
export ROS_DOMAIN_ID=0

# DDS implementation (optional tuning)
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

**Verify:**
```bash
source ~/.bashrc
echo $ROS_DISTRO  # Should print: humble
which ros2        # Should print: /opt/ros/humble/bin/ros2
```

---

### 2. Ubuntu ↔ ROS 2 Compatibility Table

| Your Ubuntu | Available ROS 2 | Recommended |
|-------------|----------------|-------------|
| 24.04 LTS | Jazzy, Kilted, Rolling | Jazzy (LTS until May 2029) |
| 22.04 LTS | Humble, Iron | Humble (LTS until May 2027) |
| 20.04 LTS | Foxy, Galactic | ⚠️ EOL - migrate to 22.04 |
| 18.04 LTS | Crystal, Dashing, Eloquent | ❌ EOL - do not use |

**Check your versions:**
```bash
lsb_release -a          # Ubuntu version
echo $ROS_DISTRO        # ROS distro (if sourced)
apt list --installed | grep ros-  # Installed ROS packages
```

---

### 3. udev Rules for Robot USB Devices

Create `/etc/udev/rules.d/99-robot-serial.rules`:

```bash
# FTDI-based devices (common)
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout", SYMLINK+="ttyFTDI"

# CP2102 (Silicon Labs) - RPLidar, many controllers
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout", SYMLINK+="ttyLIDAR"

# CH340 (common cheap USB-serial)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout", SYMLINK+="ttyCH340"

# Arduino / Teensy
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", MODE="0666", GROUP="dialout"

# Intel RealSense (if using USB for firmware)
SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b3a", MODE="0666", GROUP="plugdev"

# STM32 Virtual COM Port (many motor controllers)
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666", GROUP="dialout", SYMLINK+="ttySTM32"
```

**Apply rules:**
```bash
sudo cp 99-robot-serial.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
# Unplug and replug device, or reboot
```

**Verify:**
```bash
ls -la /dev/ttyFTDI  # Should exist and point to ttyUSB*
ls -la /dev/ttyUSB*  # Should have dialout group
```

---

### 4. systemd Service Template for ROS 2 Node

Create `/etc/systemd/system/my_robot.service`:

```ini
[Unit]
Description=My ROS 2 Robot Application
After=network.target
Wants=network.target

[Service]
Type=simple
# CRITICAL: Run as your user, not root!
User=%I
Group=%I

# Working directory for relative paths
WorkingDirectory=/home/%I/ros2_ws

# Environment setup - CRITICAL for ROS 2
Environment="ROS_DISTRO=humble"
Environment="ROS_DOMAIN_ID=0"
Environment="RMW_IMPLEMENTATION=rmw_fastrtps_cpp"
Environment="HOME=/home/%I"

# Source and run - MUST be in one command
ExecStart=/bin/bash -c '\
    source /opt/ros/humble/setup.bash && \
    source /home/%I/ros2_ws/install/setup.bash && \
    ros2 launch my_robot_bringup robot.launch.py'

# Restart policy - CRITICAL for production
Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# Graceful shutdown
TimeoutStopSec=30
KillSignal=SIGINT

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=my_robot

[Install]
WantedBy=multi-user.target
```

**Enable service (replace USERNAME with actual username):**
```bash
sudo systemctl daemon-reload
sudo systemctl enable my_robot@USERNAME.service
sudo systemctl start my_robot@USERNAME.service
sudo systemctl status my_robot@USERNAME.service
```

---

### 5. Permission Fix Patterns

```bash
# Serial ports - add user to dialout
sudo usermod -aG dialout $USER
sudo usermod -aG tty $USER     # For some serial adapters

# Camera devices (USB cameras)
sudo usermod -aG video $USER

# GPIO access (Raspberry Pi)
sudo usermod -aG gpio $USER

# RealSense (if not using udev)
sudo usermod -aG plugdev $USER

# Apply (log out and back in, or)
su - $USER  # Re-login to apply groups
```

---

### 6. Network Configuration for Robot

```bash
# Static IP via netplan (Ubuntu 22.04+)
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

```bash
sudo netplan apply
```

**Hostname for multi-robot:**
```bash
sudo hostnamectl set-hostname robot01
# Edit /etc/hosts to add: 127.0.1.1 robot01
```

---

### 7. Swap/Memory Tuning for Robot Computers

```bash
# Check current swap
free -h
swapon --show

# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Memory tuning for ROS 2
sudo sysctl -w vm.swappiness=10  # Prefer RAM over swap
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## Common Mistakes

### WRONG: Multiple source commands in different lines

```bash
# ❌ BAD - Only last source applies
ExecStartPre=/bin/bash -c 'source /opt/ros/humble/setup.bash'
ExecStartPre=/bin/bash -c 'source /home/robot/ros2_ws/install/setup.bash'
ExecStart=/bin/bash -c 'ros2 run my_pkg my_node'
# Result: ros2 command not found!
```

### CORRECT: Source in ONE command

```bash
# ✅ GOOD - All environments loaded
ExecStart=/bin/bash -c '\
    source /opt/ros/humble/setup.bash && \
    source /home/robot/ros2_ws/install/setup.bash && \
    ros2 run my_pkg my_node'
```

---

### WRONG: Running systemd service as root

```ini
# ❌ BAD - Root runs ROS, breaks permissions
# (no User= line defaults to root)
```

### CORRECT: Explicit user

```ini
# ✅ GOOD - Run as robot user
User=robot
Group=robot
```

---

### WRONG: No restart on failure

```ini
# ❌ BAD - Node crashes, service stops forever
Restart=no
```

### CORRECT: Always restart with delay

```ini
# ✅ GOOD - Auto-recovery
Restart=always
RestartSec=5
```

---

## CLI Debug Commands

```bash
# Check what ROS packages are available
ros2 pkg list | grep my

# Verify environment sourcing
echo $AMENT_PREFIX_PATH  # Should show underlay + overlay

# Check systemd service logs
sudo journalctl -u my_robot@$USER.service -f

# View udev events in real-time
sudo udevadm monitor

# Check serial device attributes (for udev rules)
udevadm info --name=/dev/ttyUSB0 --attribute-walk | grep -E "(idVendor|idProduct|serial)"

# Verify group membership
groups $USER
id $USER

# Check which setup files are sourced
grep -n "setup.bash" ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null

# Test systemd service without enabling
sudo systemd-run --unit=test_robot --user=$USER /bin/bash -c 'source /opt/ros/humble/setup.bash && ros2 doctor'
```
