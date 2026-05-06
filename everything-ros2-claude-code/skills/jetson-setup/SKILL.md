---
name: jetson-setup
description: NVIDIA Jetson setup for ROS 2 — JetPack, CUDA, L4T, edge AI deployment
triggers:
  - jetson
  - jetpack
  - cuda
  - l4t
  - nvidia
  - orin
  - agx
  - nx
  - nano
  - tx2
  - tensorrt
  - deepstream
---

# NVIDIA Jetson Setup for ROS 2

## Quick-Reference: Jetson Model vs ROS 2 Distro

| Jetson Model | L4T Version | JetPack | ROS 2 Distro | Architecture |
|-------------|-------------|---------|--------------|--------------|
| Jetson Nano | L4T 32.x | 4.x-5.x | Humble | ARM64 |
| Jetson TX2 | L4T 32.x | 4.x-5.x | Humble | ARM64 |
| Jetson Xavier NX | L4T 32.x | 5.x | Humble | ARM64 |
| Jetson AGX Xavier | L4T 32.x | 5.x | Humble | ARM64 |
| Jetson Orin Nano | L4T 35.x | 6.x | Jazzy | ARM64 |
| Jetson Orin NX | L4T 35.x | 6.x | Jazzy | ARM64 |
| Jetson AGX Orin | L4T 35.x | 6.x | Jazzy | ARM64 |

---

## Complete Copy-Paste Setup

### 1. Flash Jetson with JetPack (SDK Manager)

```bash
# 1. Download SDK Manager from NVIDIA website
# 2. Connect Jetson to host PC via USB
# 3. Put Jetson in recovery mode:
#    - Nano: Hold REC + PWR, release REC after 2s
#    - Orin: Hold REC + PWR, release REC after 2s

# On host PC:
sdkmanager --install "JetPack 6.0" \
  --target "Jetson AGX Orin" \
  --staystayhere  # interactive mode

# Or use flash.sh for command-line only
sudo ./flash.sh jetson-agx-orin-devkit mmcblk0p1
```

### 2. Initial Ubuntu Setup on Jetson

```bash
# Connect monitor/keyboard or serial console
# Complete Ubuntu setup, create user: robot

# SSH access (for headless)
sudo apt install openssh-server
sudo systemctl enable ssh

# Set static IP (edit netplan)
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
```

```bash
sudo netplan apply
sudo hostnamectl set-hostname robot-jetson
echo "192.168.1.100 robot-jetson" | sudo tee -a /etc/hosts
```

### 3. Install ROS 2 on Jetson

```bash
# Install ROS 2 (Humble for JetPack 5, Jazzy for JetPack 6)
sudo apt update
sudo apt install -y curl
curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=arm64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ros2.list

sudo apt update
sudo apt install -y ros-humble-ros-base  # Minimal install
# Or: sudo apt install -y ros-humble-ros-base ros-humble-launch-files  # More complete

# Add to .bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
```

### 4. Install GPU/AI Stack (JetPack Components)

```bash
# CUDA Toolkit (included in JetPack)
sudo apt install -y nvidia-jetpack
# Or install individually:
sudo apt install -y cuda-toolkit-12-2
sudo apt install -y tensorrt
sudo apt install -y visionworks
sudo apt install -y libnvinfer-plugin-dev

# Verify CUDA
nvcc --version
/usr/local/cuda/bin/nvcc --version

# Verify TensorRT
dpkg -l | grep TensorRT
python3 -c "import tensorrt; print(tensorrt.__version__)"
```

### 5. Install Robotics AI Packages

```bash
# Realsense on Jetson (for D400 series cameras)
sudo apt install -y librealsense2-dev
sudo apt install -y ros-humble-realsense2-camera
# Add udev rules for RealSense
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-realsense.rules
sudo udevadm control --reload-rules

# NVIDIA Isaac ROS packages (Jetson optimized)
cd ~/$ROS_DISTRO_ws/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvengine
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_pipeline
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_depthseg
rosdep install --from-paths ~/ros2_ws/src --ignore-src -r -y
cd ~/ros2_ws && colcon build --symlink-install

# For Jazzy + JetPack 6:
git clone https://github.com/NVIDIA/isaac_ros.git -b release/jazzy
```

---

## Performance Tuning on Jetson

### Clocks and Power Modes

```bash
# Check current power mode
sudo nvpmodel -q

# Available modes (Jetson AGX Orin):
# 0: MAXN  (full performance, 15-30W)
# 1: MODE1 (10W)
# 2: MODE2 (15W)
# 3: MODE3 (default, 25W)

# Set to max performance
sudo nvpmodel -m 0

# Enable max clocks
sudo jetson_clocks

# Verify clock frequencies
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
cat /proc/device-tree/model
```

### Swap Configuration

```bash
# Check and add swap (Jetson has limited RAM)
free -h
swapon --show

# Add 8GB swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Thermal Management

```bash
# Check temperature
cat /sys/class/thermal/thermal_zone*/temp
watch -n 1 "cat /sys/class/thermal/thermal_zone*/temp"

# Check if throttling occurring
dmesg | grep -i "thermal\|throttle"
# Look for: "cpu0: CPU0: Temperature above threshold"

# Set fan speed (if supported)
sudo sh -c 'echo 255 > /sys/kernel/debug/tegra_fan/target_pwm'
```

---

## Multi-Camera Setup (GMSL/CSI)

### CSI Camera Connection (Jetson Nano/NX)

```bash
# Check connected CSI cameras
v4l2-ctl --list-devices
nvgstcapture-1.0 --help  # With NVIDIA gst pipeline

# libcamera for Jetson (JetPack 5+)
sudo apt install -y libcamera-apps
libcamera-hello  # Test camera
libcamera-still -o test.jpg

# Enable CSI port in DT (device tree) overlay
sudo nano /boot/extlinux/extlinux.conf
# Add: FDT /boot/kernel_choices/${KERNEL Choice}/device-tree/platform/t186ref/tegra234-p3768-0000+p3767-0005.dtb
```

### GMSL2 Camera Adapters (Industrial)

| Adapter | Cameras | ROS Driver | Notes |
|---------|---------|------------|-------|
| Leopard Imaging LI-IMX477 | 1-4 | leopard_imaging | IMX477 HQ camera |
| Allied Vision Ala-IPC | 1-4 | aravis | GigE/CSI2 |
| Stereolabs ZED | 1-2 | ZED SDK | Depth + AI |

---

## Network Setup for Fleet

```bash
# Ethernet (primary for control)
cat /etc/netplan/01-netcfg.yaml

# WiFi (for mobile)
sudo nmcli device wifi rescan
sudo nmcli device wifi connect "Robot_WiFi" password "password"

# DDS Fast DDS Discovery Server (for multi-robot on WiFi)
export ROS_DISCOVERY_SERVER=192.168.1.1:11811
export FASTRTPS_DEFAULT_PROFILES_FILE=~/ros2_ws/fast_dds_discovery.xml

# Create fast_dds_discovery.xml:
cat > ~/ros2_ws/fast_dds_discovery.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<dds>
  <profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPSProf">
    <transport_descriptors>
      <transport_descriptor>
        <transport_id>CustomUDPTransport</transport_id>
        <type>UDPv4</type>
        <maxInitialPeersRange>50</maxInitialPeersRange>
        <transport_socket_buffer_size>65536</transport_socket_buffer_size>
      </transport_descriptor>
    </transport_descriptors>
  </profiles>
</dds>
EOF
```

---

## Docker on Jetson (for Isolation)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Use NVIDIA Container Runtime for GPU access in Docker
sudo apt install -y nvidia-container-runtime
sudo systemctl restart docker

# docker-compose.yml for ROS 2 + CUDA
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  ros2:
    image: ros:humble-ros-base-jammy
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - ROS_DOMAIN_ID=0
    volumes:
      - ./ros2_ws:/ros2_ws
    network_mode: host
    command: bash -c "source /opt/ros/humble/setup.bash && ros2 run demo_nodes_cpp talker"
EOF

# Run with:
docker-compose run --rm ros2
```

---

## Common Jetson Issues

### Issue: apt install fails on JetPack

```bash
# Fix sources
sudo sh -c 'echo "deb https://repo.download.nvidia.com/jetson/common r35.3 main" > /etc/apt/sources.list.d/nvidia-l4t-apt.list'
sudo apt update
```

### Issue: ROS 2 packages missing ARM64 builds

```bash
# Use ros_rockchip instead (community)
# Or build from source:
cd ~/ros2_ws/src
vcs import --recursive < ros2.repos
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install --cmake-clean-cache
```

### Issue: Camera framerate drops under load

```bash
# Check CPU/GPU thermal throttling
sudo jetson_clocks --show
# If clocks are below max, thermal issue - improve cooling

# Undervolt (AGX Orin only, use with caution)
sudo nvpmodel -m 0
sudo jetson_clocks
```

---

## CLI Debug Commands

```bash
# Full system info
jtop  # Best tool - install: sudo pip3 install jetson-stats

# Manual checks
cat /proc/device-tree/model
head -5 /etc/nv_tegra_release
nvcc --version
nvidia-smi
lsusb | grep -i nvidia
cat /sys/class/gpio/gpio*/device/name
```
