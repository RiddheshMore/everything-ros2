---
name: hardware-drivers
description: Robot hardware driver setup — motors, sensors, actuators, CAN, I2C, SPI, GPIO
triggers:
  - motor
  - encoder
  - servo
  - can bus
  - i2c
  - spi
  - gpio
  - encoder
  - pwm
  - hall sensor
  - stepper
  - drv8871
  - l298n
  - esc
  - bltouch
---

# Robot Hardware Driver Patterns

## Quick-Reference Decision Table

| Hardware Type | Interface | ROS 2 Package | Notes |
|--------------|-----------|---------------|-------|
| DC Motor + Encoder | GPIO/PWM + Encoder | ros2-control | Use diff_drive_controller |
| Servo Motor | PWM / I2C | ros2-control | PCA9685 for multiple servos |
| Stepper Motor | SPI / Step-Dir | ros2-control | Requires position feedback |
| CAN Motor Controller | CAN Bus | socketcan | Industrial grade |
| BLDC Motor + ESC | PWM | ros2-control | Electronic Speed Controller |
| IMU (MPU6050) | I2C | imu_tools | 6-DOF accelerometer/gyro |
| LIDAR (RPLidar) | USB Serial | rplidar_ros | 360 laser scanner |
| RealSense | USB3 / CSI | realsense2_camera | Depth + RGB camera |
| Encoder ( quadrature | GPIO + interrupts | encoder_reader | Rotary position |
| Sensor (generic) | I2C / SPI | i2c_tools | ADC, temp, pressure |

---

## Complete Copy-Paste Code

### 1. I2C Device Discovery and Setup

```bash
# Check I2C devices on bus
sudo apt install -y i2c-tools
i2cdetect -y 0   # Bus 0
i2cdetect -y 1   # Bus 1 (most common)

# Common I2C addresses for robotics:
# 0x68 - MPU6050 / MPU9250 (IMU)
# 0x76 - BMP280 (barometer)
# 0x77 - BMP180 (barometer)
# 0x1E - HMC5883L (magnetometer)
# 0x53 - ADXL345 (accelerometer)
# 0x40 - PCA9685 (PWM controller)
# 0x3C - OLED display

# Add user to i2c group
sudo usermod -aG i2c $USER
# Re-login required

# Test I2C device
i2cget -y 1 0x68 0x75  # Read MPU6050 who am I register (should be 0x68)
```

### 2. PCA9685 PWM Controller (16-channel, I2C)

```bash
# Install library
sudo apt install -y python3-pip
pip3 install adafruit-pca9685 adafruit-circuitpython-servokit

# ROS 2 driver for PCA9685
cd ~/ros2_ws/src
git clone https://github.com/KristofRobot/ros2_pca9685
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

```python
#!/usr/bin/env python3
# pca9685_test.py - Test PCA9685 PWM outputs
import Adafruit_PCA9685
import time

pca = Adafruit_PCA9685.PCA9685(address=0x40)
pca.set_pwm_freq(60)  # 60 Hz for servos, 100-1000 Hz for motors

# Servo positions (typical 1-2ms pulse width)
def set_servo(channel, position):  # position: 0.0 to 1.0
    pulse = int(150 + position * 600)  # 150-750 range for 1-2ms
    pca.set_pwm(channel, 0, pulse)

def set_motor(channel, speed):  # speed: -1.0 to 1.0
    if speed < 0:
        pulse = int(375 + speed * 375)  # Reverse: 375-0
    else:
        pulse = int(375 + speed * 375)  # Forward: 375-750
    pca.set_pwm(channel, 0, pulse)

# Example: sweep servo on channel 0
for i in range(100):
    set_servo(0, i/100)
    time.sleep(0.02)
```

### 3. MPU6050 IMU (I2C)

```bash
# ROS 2 IMU publisher
cd ~/ros2_ws/src
git clone https://github.com/KristofRobot/ros2_mpu6050
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install

# Launch
ros2 launch ros2_mpu6050 mpu6050.launch.py
```

```python
#!/usr/bin/env python3
# mpu6050_direct.py - Read MPU6050 without ROS
import smbus2
import time
import math

bus = smbus2.SMBus(1)
MPU6050_ADDR = 0x68

# Initialize MPU6050
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)  # Wake up

def read_imu():
    # Read accelerometer and gyroscope
    raw = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 14)
    ax = (raw[0] << 8) | raw[1]
    ay = (raw[2] << 8) | raw[3]
    az = (raw[4] << 8) | raw[5]
    temp = (raw[6] << 8) | raw[7]
    gx = (raw[8] << 8) | raw[9]
    gy = (raw[10] << 8) | raw[11]
    gz = (raw[12] << 8) | raw[13]
    
    # Convert to physical units
    ax_g = ax / 16384.0
    ay_g = ay / 16384.0
    az_g = az / 16384.0
    gx_dps = gx / 131.0
    gy_dps = gy / 131.0
    gz_dps = gz / 131.0
    
    return ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps

while True:
    print(read_imu())
    time.sleep(0.1)
```

### 4. CAN Bus Motor Controller

```bash
# Setup SocketCAN
sudo apt install -y can-utils

# Connect Peak CAN adapter and find interface
ip link show
# Usually: can0

# Configure CAN bus
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0

# Test CAN communication
candump can0 &
cansend can0 123#DEADBEEF  # Send test frame

# Install ROS 2 socketcan
sudo apt install -y ros-humble-socketcan-interfaces
```

```python
#!/usr/bin/env python3
# can_motor_control.py - Send velocity commands via CAN
import can

bus = can.interface.Bus(channel='can0', bustype='socketcan')

# Motor controller CAN IDs (example: Roboteq)
# 0x01 - Motor 1 velocity command
# 0x02 - Motor 2 velocity command
# 0x05 - Emergency stop

def send_motor_command(motor_id, velocity_rpm):
    # Convert RPM to motor command (-1000 to 1000)
    cmd = int(max(-1000, min(1000, velocity_rpm)) )
    data = [(cmd >> 8) & 0xFF, cmd & 0xFF, 0, 0, 0, 0, 0, 0]
    msg = can.Message(arbitration_id=motor_id, data=data, is_extended_id=False)
    bus.send(msg)

# Example: Run motor at 500 RPM
send_motor_command(0x01, 500)
```

### 5. Quadrature Encoder (GPIO Interrupts)

```bash
# ROS 2 encoder driver
cd ~/ros2_ws/src
git clone https://github.com/KristofRobot/ros2_encoder
rosdep install --from-paths . --ignore-src -r -y
colcon build --symlink-install
```

```python
#!/usr/bin/env python3
# encoder_counter.py - Count quadrature encoder pulses
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
A_PIN = 17  # Encoder channel A
B_PIN = 27  # Encoder channel B

counter = 0
last_state = 0

def encoder_callback(channel):
    global counter, last_state
    a_state = GPIO.input(A_PIN)
    b_state = GPIO.input(B_PIN)
    current_state = (a_state << 1) | b_state
    # Determine direction from state transition
    if (last_state == 0 and current_state == 1) or \
       (last_state == 2 and current_state == 3) or \
       (last_state == 3 and current_state == 2):
        counter += 1
    else:
        counter -= 1
    last_state = current_state

GPIO.setup(A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(A_PIN, GPIO.BOTH, callback=encoder_callback)

try:
    while True:
        print(f"Pulses: {counter}, Position: {counter / 4} rev")
        time.sleep(1)
finally:
    GPIO.cleanup()
```

### 6. DRV8871 DC Motor Driver (PWM)

```bash
# GPIO setup for motor driver
# DRV8871 connections:
#   IN1 -> GPIO17 (PWM)
#   IN2 -> GPIO27 (PWM or GND for coast)
#   VMOT -> Motor power (6.5-45V)
#   GND -> Common ground
```

```python
#!/usr/bin/env python3
# motor_pwm.py - Control DRV8871 with PWM
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
IN1 = 17
IN2 = 27

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Create PWM instances at 1kHz
pwm1 = GPIO.PWM(IN1, 1000)
pwm2 = GPIO.PWM(IN2, 1000)
pwm1.start(0)
pwm2.start(0)

def set_motor_speed(speed):  # speed: -1.0 to 1.0
    duty = abs(speed) * 100
    if speed > 0:
        pwm1.ChangeDutyCycle(duty)
        pwm2.ChangeDutyCycle(0)  # Coast
    elif speed < 0:
        pwm1.ChangeDutyCycle(0)  # Coast
        pwm2.ChangeDutyCycle(duty)
    else:
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)

try:
    # Test: ramp up forward, then reverse
    for s in [0.25, 0.5, 0.75, 1.0, 0, -0.5, -1.0]:
        set_motor_speed(s)
        time.sleep(2)
finally:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
```

### 7. BLDC Motor + ESC (PWM)

```bash
# Electronic Speed Controller (ESC) setup
# Most ESCs use standard PWM: 1ms (0%) to 2ms (100%) at 50-400 Hz
# Neutral (stop) is 1.5ms
```

```python
#!/usr/bin/env python3
# esc_control.py - Control BLDC ESC
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
ESC_PIN = 18  # GPIO18 supports PWM

GPIO.setup(ESC_PIN, GPIO.OUT)
pwm = GPIO.PWM(ESC_PIN, 50)  # 50 Hz for most ESCs
pwm.start(0)

def set_esc throttle(throttle):  # throttle: -1.0 to 1.0
    # Map -1..1 to 1ms..2ms pulse width
    # duty = 1.5ms / 20ms * 100 = 7.5% center
    duty = 7.5 + throttle * 2.5  # 5% to 10% range
    duty = max(5, min(10, duty))
    pwm.ChangeDutyCycle(duty)

# Arm the ESC (per ESC-specific procedure)
print("Arming ESC...")
pwm.ChangeDutyCycle(5)
time.sleep(2)
pwm.ChangeDutyCycle(10)
time.sleep(2)
pwm.ChangeDutyCycle(7.5)
time.sleep(1)

# Test throttle
print("Testing throttle...")
set_esc_throttle(0.5)
time.sleep(2)
set_esc_throttle(0)
pwm.stop()
GPIO.cleanup()
```

---

## ros2_control Hardware Interface

```bash
# Install ros2_control
sudo apt install -y ros-humble-ros2-control
sudo apt install -y ros-humble-ros2-controllers

# Common hardware interfaces:
# - diff_drive_controller (for 2-wheel differential drive)
# - joint_trajectory_controller (for robotic arms)
# - imu_sensor_broadcaster
# - forward_command_controller (simple position/speed control)
```

```yaml
# diff_drive_controller.yaml
controller_manager:
  ros__parameters:
    update_rate: 50

    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names: [wheel_left_joint]
    right_wheel_names: [wheel_right_joint]
    wheel_separation: 0.4
    wheel_radius: 0.05
    max_wheel_acceleration: 1.0
    max_wheel_jerk: 5.0
    publish_rate: 50.0
    odom_frame_id: odom
    base_frame_id: base_link
    publish_cmd: true
    use_stamped_vel: false
```

---

## udev Rules for USB Serial Devices

```bash
# /etc/udev/rules.d/99-robot-serial.rules
# Name USB serial devices by their unique ID (persistent across reboots)

# Find device serial
ls -la /dev/serial/by-id/

# Example entries:
# Motor controller
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A700eqJA", SYMLINK+="ttyMotorController", MODE="0666", GROUP="dialout"

# GPS
SUBSYSTEM=="tty", ATTRS{idVendor}=="1546", ATTRS{idProduct}=="01a", SYMLINK+="ttyGPS", MODE="0666", GROUP="dialout"

# Apply
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -la /dev/ttyMotorController
```

---

## CLI Debug Commands

```bash
# I2C
i2cdetect -y 1
i2cget -y 1 0x68 0x75
i2cdump -y 1 0x68

# SPI
ls -la /dev/spidev*
spi-config --device=/dev/spidev0.0 --mode=3 --speed=1000000

# GPIO
gpio readall
cat /sys/class/gpio/gpio*/direction

# CAN
ip link show can0
candump can0
cansend can0 123#DEADBEEF
canfdtest -g can0 -c can0

# PWM
cat /sys/class/pwm/pwmchip0/export
cat /sys/class/pwm/pwmchip0/pwm0/period
```
