---
name: network-config
description: ROS 2 network configuration — DDS discovery, Fast DDS, CycloneDDS, WiFi, Ethernet, multi-robot
triggers:
  - network
  - dds
  - fastrtps
  - cyclonedds
  - discovery
  - wifi
  - ethernet
  - domain
  - multicast
  - firewall
---

# ROS 2 Network Configuration

## Quick-Reference Decision Table

| Setup | DDS | Discovery | Use Case |
|-------|-----|-----------|----------|
| Single robot | FastRTPS | Auto | Default |
| Multi-robot (WiFi) | CycloneDDS | Server | Reduce broadcast |
| Lab with wired | CycloneDDS | Static | Deterministic |
| Cloud bridging | FastRTPS | Server | ROS1 bridge |

---

## Complete Copy-Paste Code

### 1. Fast DDS Configuration (Default)

```xml
<!-- fastrtps.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS/1.0/xs">
  <participant profile_name="default_x86_64" is_default_profile="true">
    <rtps>
      <name>RobotParticipant</name>

      <builtinEntities>
        <discovery_config>
          <discoveryProtocol>FULL</discoveryProtocol>
          <leaseDuration>DDS::Time_t {5, 0}</leaseDuration>
          <leaseDurationAnnouncement>DDS::Time_t {1, 0}</leaseDurationAnnouncement>
        </discovery_config>
      </builtinEntities>

      <port>
        <portBase>7400</portBase>
        <domainIdLow>0</domainIdLow>
        <domainIdHigh>230</domainIdHigh>
      </port>

      <throughputController>
        <controllerBandwidthWidth>0</controllerBandwidthWidth>
      </throughputController>
    </rtps>
  </participant>

  <transport_descriptors>
    <transport_descriptor>
      <transport_id>UDPv4Transport</transport_id>
      <type>UDPv4</type>
      <maxMessageSize>65500</maxMessageSize>
      <maxInitialPeersRange>50</maxInitialPeersRange>
    </transport_descriptor>
  </transport_descriptors>
</profiles>
```

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/fastrtps.xml
```

### 2. CycloneDDS Configuration (Better for Multi-Robot)

```xml
<!-- /etc/cyclonedds/config.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<cyclonedds xmlns="https://cyclonedds.io/xsd/1.11.1">
  <domain id="any">
    <discovery>
      <SPDPDomain>
        <!-- Use multicast only on wired networks -->
        <MinMulticastAnnouncementInterval>1</MinMulticastAnnouncementInterval>
        <MaxMulticastAnnouncementInterval>5</MaxMulticastAnnouncementInterval>
      </SPDPDomain>
    </discovery>

    <internal>
      <!-- Higher queue sizes for large sensor data -->
      <Watermarks>
        <WhcHigh>500MB</WhcHigh>
      </Watermarks>

      <!-- Thread pool tuning -->
      <Scheduling>
        <ThreadPoolSchedulingPolicy>FIFO</ThreadPoolSchedulingPolicy>
      </Scheduling>
    </internal>
  </domain>
</cyclonedds>
```

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///etc/cyclonedds/config.xml
```

### 3. DDS Discovery Server (Multi-Robot via WiFi)

```bash
# Terminal 1: Start discovery server
ros2 run fastdds discovery-server --server-id 1 \
    --port 11811 \
    --output-limit 5000000

# Or use YAML config:
ros2 run fastdds discovery-server \
    -c /path/to/discovery_server.yaml
```

```yaml
# discovery_server.yaml
version: 1
servers:
  - id: "1"
    address:
      - hostname: "192.168.1.1"
        port: 11811
```

```bash
# On each robot: configure to use discovery server
export ROS_DISCOVERY_SERVER=192.168.1.1:11811

# Or in code:
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/robot_profiles.xml
```

```xml
<!-- robot_profiles.xml with discovery server -->
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS/1.0/xs">
  <participant profile_name="robot_participant">
    <rtps>
      <builtin>
        <discovery_config>
          <discoveryProtocol>CLIENT</discoveryProtocol>
          <discoveryServer_locators>
            <locator>
              <udpv4 address="192.168.1.1" port="11811"/>
            </locator>
          </discoveryServer_locators>
        </discovery_config>
      </builtin>
    </rtps>
  </participant>
</profiles>
```

### 4. Network Interface Configuration (Static IP)

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      # For wired robot network
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
      # QoS for ROS 2 traffic
      # (netplan doesn't support per-port QoS directly)

    wlan0:
      # For mobile WiFi connection
      dhcp4: true
      dhcp4-overrides:
        route-metric: 100  # Lower priority than eth0
      access-points:
        "RobotWiFi":
          password: "password"
```

```bash
sudo netplan apply
ip addr show
```

### 5. Firewall Configuration (ROS 2 Ports)

```bash
# ROS 2 uses these UDP ports by default:
# 7410 - participant announcement (multicast)
# 7400 - base port for RTPS
# 11811 - discovery server (if used)

# Ubuntu ufw commands:
sudo ufw allow 7410/udp comment 'ROS2 Discovery'
sudo ufw allow 7400:7500/udp comment 'ROS2 RTPS'
sudo ufw allow 11811/tcp comment 'ROS2 Discovery Server'

# Or for development:
sudo ufw disable  # NOT for production!
```

```bash
# iptables rules:
# ROS 2 UDP discovery
sudo iptables -A INPUT -p udp --dport 7410 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 7400:7500 -j ACCEPT

# ROS 2 TCP (bridges, services)
sudo iptables -A INPUT -p tcp --dport 11811 -j ACCEPT
```

### 6. Multi-Robot Domain Separation

```bash
# Robot 1: Domain 0
export ROS_DOMAIN_ID=0

# Robot 2: Domain 1
export ROS_DOMAIN_ID=1

# Robot 3: Domain 2
export ROS_DOMAIN_ID=2

# DDS traffic is isolated between domains
# Topics /scan in domain 0 ≠ /scan in domain 1
```

### 7. WiFi Performance Tuning for ROS 2

```bash
# /etc/modprobe.d/iwlwifi.conf (Intel WiFi cards)
# Reduce power management interference
options iwlwifi power_save=0
options iwlwifi 11n_disable=1  # Disable N for stability

# Or for robot's dedicated WiFi adapter:
# Use 5GHz band only (less interference than 2.4GHz)
# Use WPA2 enterprise or strong WPA2-PSK
```

```bash
# Check WiFi signal quality
iwconfig wlan0
watch -n 1 "cat /proc/net/wireless"

# Prioritize ROS 2 traffic (QoS)
# In /etc/network/interfaces or netplan:
# Not directly supported - use switch with QoS or separate VLAN
```

### 8. ROS 2 over VPN (for remote debugging)

```bash
# Assumes VPN creates tun0 interface
# Use ROS_DOMAIN_ID for isolation

# Increase DDS buffer sizes for VPN latency
export FASTRTPS_PROPERTIES_FILE=/path/to/vpn_profiles.xml
```

```xml
<!-- vpn_profiles.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS/1.0/xs">
  <participant profile_name="vpn_participant">
    <rtps>
      <builtin>
        <discovery_config>
          <leaseDuration>DDS::Time_t {20, 0}</leaseDuration>
          <leaseDurationAnnouncement>DDS::Time_t {5, 0}</leaseDurationAnnouncement>
        </discovery_config>
      </builtin>
    </rtps>
  </participant>
</profiles>
```

---

## CLI Debug Commands

```bash
# Check DDS configuration
ros2 doctor --report

# List discovered participants
ros2 topic echo /rt/dds_discovery/*

# Check domain
echo $ROS_DOMAIN_ID

# List all topics
ros2 topic list

# Check connectivity
ping 192.168.1.x

# Check ports
sudo netstat -ulnp | grep -E '(7410|7400|11811)'

# DDS statistics
export RCLCPP_LOGGING_USE_IMMUTABLE_TOPICS=1
ros2 topic echo /rt/ddsParticipantDiscovery/*

# Test with manually specified peer
export FASTRTPS_PROFILES_FILE=participant_profiles.xml
# Where participant_profiles.xml lists specific peer addresses
```

---

## Common Issues

### Topics not discovered across machines
```bash
# Check 1: Same domain
echo $ROS_DOMAIN_ID  # Must match

# Check 2: Firewall
sudo ufw status

# Check 3: Same subnet
ip addr show
ping other_robot

# Check 4: DDS config
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 topic list  # Should show remote topics
```

### High latency on WiFi
```bash
# Switch to 5GHz channel
# Use wired connection for control topics
# Reduce message frequency
# Use compressed image transport
```
