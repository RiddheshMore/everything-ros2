---
name: docker-ros2
description: Docker for ROS 2 — containerization, compose, GPU access (nvidia-docker), cross-compilation, development workflows
triggers:
  - docker
  - container
  - nvidia-docker
  - docker-compose
  - image
  - containerize
  - buildx
---

# Docker for ROS 2

## Quick-Reference Decision Table

| Use Case | Image | GPU Access | Notes |
|----------|-------|-----------|-------|
| Humble base | osrf/ros:humble-ros-base | nvidia-docker | Minimal |
| Humble desktop | osrf/ros:humble-desktop | nvidia-docker | Full GUI tools |
| Jazzy base | osrf/ros:jazzy-ros-base | nvidia-docker | Minimal |
| Cross-compile | ros-tooling/cross_compile | None | Multi-arch |
| Custom ROS1+2 | custom Dockerfile | nvidia-docker | Bridge mode |

---

## Complete Copy-Paste Code

### 1. Basic ROS 2 Dockerfile

```dockerfile
# Dockerfile.ros2
FROM osrf/ros:humble-ros-base

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install common tools
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-rosdep \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install ROS 2 packages
RUN apt-get update && apt-get install -y \
    ros-humble-ros2cli \
    ros-humble-ros2run \
    ros-humble-ros2launch \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
RUN mkdir -p /ros2_ws/src
WORKDIR /ros2_ws

# Copy source
COPY src /ros2_ws/src

# Build
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Source workspace in shell
RUN echo "source /ros2_ws/install/setup.sh" >> /root/.bashrc
```

### 2. Docker with NVIDIA GPU

```dockerfile
# Dockerfile.ros2-gpu
FROM osrf/ros:humble-ros-base

# Install NVIDIA container toolkit
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3c3c1ece0a23b1564a6b5fc2b0a1e2a8/CUDA-GPG-KEY | \
       gpg --dearmor -o /usr/share/keyrings/nvidia-driver-535.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nvidia-driver-535.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" > /etc/apt/sources.list.d/cuda.list && \
    apt-get update && apt-get install -y \
    nvidia-container-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Set NVIDIA runtime as default
RUN nvidia-ctk runtime configure --runtime=docker --set-as-default
RUN echo '{"default-runtime":"nvidia"}' > /etc/docker/daemon.json && \
    systemctl restart docker
```

```bash
# Test GPU access in container
docker run --rm --gpus all osrf/ros:humble-ros-base \
    nvidia-smi
```

### 3. docker-compose.yml for Robot Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  ros2:
    image: ros:humble-ros-base
    container_name: ros2_robot
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - ROS_DOMAIN_ID=0
      - RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    volumes:
      - ./ros2_ws:/ros2_ws
      - /tmp/robot_logs:/root/.ros/log
    network_mode: host
    privileged: true  # For GPIO, USB access
    command: >
      bash -c "source /opt/ros/humble/setup.sh &&
               source /ros2_ws/install/setup.sh &&
               ros2 launch robot_bringup bringup.launch.py"

  # Separate container for heavy computation (e.g., perception)
  perception:
    image: ros:humble-perception:latest
    runtime: nvidia
    environment:
      - ROS_DOMAIN_ID=1  # Separate domain for performance
    volumes:
      - ./perception_ws:/perception_ws
    network_mode: host
    depends_on:
      - ros2
    command: >
      bash -c "source /opt/ros/humble/setup.sh &&
               ros2 run tensorrt_yolo yolo_node"

  # Web dashboard
  dashboard:
    image: public.ecr.aws/nginx/nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./dashboard:/usr/share/nginx/html
    network_mode: host
```

### 4. Cross-Compilation with docker-buildx

```bash
# Install docker-buildx
docker install docker-buildx-plugin

# Create builder
docker buildx create --name ros-cross
docker buildx use ros-cross

# Bootstrap qemu for ARM emulation (for cross-compile to ARM64)
docker run --rm --privileged tonistiigi/binfmt:latest --install all
```

```dockerfile
# dockerfile.aarch64
FROM --platform=linux/arm64 osrf/ros:humble-ros-base

# Cross-compile from AMD64 to ARM64
# Build on host with:
# docker buildx build --platform linux/arm64 -t my_robot/ros2:aarch64 .
```

```bash
# Build for ARM64 on x86_64 host
docker buildx build \
    --platform linux/arm64 \
    --tag my_robot/ros2:aarch64 \
    --push \
    .
```

### 5. Development Container with Volume Mounts

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  dev:
    image: ros:humble-ros-base
    container_name: ros2_dev
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - DISPLAY=${DISPLAY}
      - ROS_DOMAIN_ID=0
    volumes:
      # Mount source code (symlink-install ready)
      - ~/robot/ros2_ws:/ros2_ws
      # Share X11 for GUI tools (rviz, rqt)
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ${XAUTHORITY}:/root/.Xauthority:ro
      # USB devices
      - /dev/bus/usb:/dev/bus/usb
    network_mode: host
    working_dir: /ros2_ws
    command: >
      bash -c "source /opt/ros/humble/setup.sh &&
               colcon build --symlink-install &&
               bash"
```

```bash
# Run development container
xhost +local:docker  # Allow local X connections
docker compose -f docker-compose.dev.yml up -d
docker exec -it ros2_dev bash
```

### 6. ROS 1 + ROS 2 Bridge in Docker

```yaml
# docker-compose.bridge.yml
version: '3.8'

services:
  ros1:
    image: osrf/ros:noetic-ros-core
    container_name: ros1_bridge_ros1
    network_mode: host
    environment:
      - ROS_MASTER_URI=http://localhost:11311
    command: >
      bash -c "source /opt/ros/noetic/setup.sh &&
               roscore"

  ros2:
    image: osrf/ros:humble-ros-base
    container_name: ros2_bridge_ros2
    network_mode: host
    environment:
      - ROS_DOMAIN_ID=0
    command: >
      bash -c "source /opt/ros/humble/setup.sh &&
               while ! ros2 topic list &>/dev/null; do sleep 1; done &&
               ros2 run ros1_bridge dynamic_bridge"

  bridge:
    image: osrf/ros:humble-ros-base
    container_name: ros1_bridge
    network_mode: host
    environment:
      - ROS_MASTER_URI=http://localhost:11311
      - ROS_DOMAIN_ID=0
    depends_on:
      - ros1
      - ros2
    command: >
      bash -c "source /opt/ros/noetic/setup.sh &&
               source /opt/ros/humble/setup.sh &&
               export LD_LIBRARY_PATH=/opt/ros/noetic/lib:$LD_LIBRARY_PATH &&
               ros2 run ros1_bridge dynamic_bridge --bridge-all-topics"
```

---

## CLI Commands

```bash
# Build image
docker build -t ros2_robot:v1 .

# Run container
docker run --rm --network host ros2_robot:v1

# Run with GPU
docker run --rm --gpus all -it ros2_robot:v1 bash

# Run with USB devices
docker run --rm --device /dev/ttyUSB0:/dev/ttyUSB0 ros2_robot:v1

# Copy files in/out
docker cp container:/ros2_ws/src ./src
docker cp ./config container:/ros2_ws/config

# Inspect running container
docker exec -it container bash

# View logs
docker logs -f container

# Multi-platform build
docker buildx build --platform linux/arm64,linux/amd64 -t my/ros2:multi .
```

---

## Common Issues

### USB device not accessible
```bash
# Add --device flag
docker run --device /dev/ttyUSB0:/dev/ttyUSB0 ...

# Or expose all USB
docker run --privileged ...
```

### X11/GUI apps not working
```bash
# On host: allow X connections from docker
xhost +local:docker

# In docker-compose, mount X11 socket
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:rw
  - ${XAUTHORITY}:/root/.Xauthority:ro

# Inside container: allow X connections
export DISPLAY=${DISPLAY}
xhost +local:container
```

### Network/Discovery issues
```bash
# Use host network for full connectivity
network_mode: host

# Or explicitly map ports for DDS
ports:
  - "7400:7400/udp"
  - "7410:7410/udp"
  - "11811:11811"
```
