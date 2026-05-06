# Docker Robot Stack

Multi-container ROS 2 robot stack using docker-compose with GPU access, ROS 1 bridge, and hot-reload development.

## Structure

```
docker-robot-stack/
├── docker-compose.yml        # Full robot stack
├── docker-compose.dev.yml    # Development with hot-reload
├── docker-compose.bridge.yml # ROS 1 + 2 bridge
├── Dockerfile.ros2           # Core ROS 2 image
├── Dockerfile.perception     # GPU perception image
├── .env                     # Environment config
└── entrypoint.sh            # Container startup
```

## Quick Start

```bash
# Build and start full stack
docker compose up -d

# Start development stack with hot-reload
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose logs -f ros2

# Shell into running container
docker exec -it ros2_robot bash
```

## Stack Services

### ros2 (Core)
- Image: `osrf/ros:humble-ros-base`
- Runtime: nvidia (GPU access)
- Network: host (for DDS)
- Mounts: `./ros2_ws:/ros2_ws`

### perception (GPU)
- Image: custom `ros2-perception:latest`
- Runtime: nvidia
- ROS_DOMAIN_ID=1 (isolated from core)
- Mounts: `./perception_ws:/perception_ws`

### dashboard (Web)
- Image: nginx
- Ports: 8080:80
- Serves: `./dashboard:/usr/share/nginx/html`

## Environment Variables

```bash
ROS_DOMAIN_ID=0
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
NVIDIA_VISIBLE_DEVICES=all
```

## Hardware Access

```yaml
# USB devices (LIDAR, IMU)
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0

# GPIO for ESTOP
  - /dev/gpiochip0:/dev/gpiochip0

# CUDA GPU
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
```

## ROS 2 Workspace

Source code lives in `./ros2_ws` mounted at `/ros2_ws` inside container. Use symlink-install:

```bash
colcon build --symlink-install
```

## ROS 1 Bridge

```bash
docker compose -f docker-compose.bridge.yml up -d
# Brings up: ros1 (roscore), ros2 (humble), bridge (dynamic_bridge)
```

## Troubleshooting

```bash
# DDS discovery issues - verify same domain
docker exec ros2_robot bash -c "echo $ROS_DOMAIN_ID"

# GPU not accessible
docker exec ros2_robot nvidia-smi

# Network mode - required for DDS
# Do NOT use bridge networking
network_mode: host
```
