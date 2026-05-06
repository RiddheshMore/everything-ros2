---
name: rosbag-patterns
description: rosbag2 record, playback, conversion, and programmatic access patterns
triggers:
  - rosbag
  - rosbag2
  - bag file
  - record topics
  - play back
  - mcap
  - sqlite3
---

# rosbag2 Patterns

## CLI — Recording

```bash
# Record all topics
ros2 bag record -a

# Record specific topics
ros2 bag record /scan /odom /cmd_vel /tf /tf_static

# Record with compression (recommended for storage)
ros2 bag record -a --compression-mode file --compression-format zstd

# Record with MCAP format (default in Jazzy+, better tooling)
ros2 bag record -a --storage mcap

# Record for a fixed duration (seconds)
ros2 bag record -a --duration 30

# Record with max bag size (bytes) — splits into multiple files
ros2 bag record -a --max-bag-size 1000000000  # 1 GB

# Record with custom output directory and name
ros2 bag record -a -o my_session_2024_01_01
```

## CLI — Playback

```bash
# Play a bag
ros2 bag play my_bag/

# Play at 2x speed
ros2 bag play my_bag/ --rate 2.0

# Loop playback
ros2 bag play my_bag/ --loop

# Play only specific topics
ros2 bag play my_bag/ --topics /scan /odom

# Pause/resume: press Space during playback

# Start at an offset (seconds)
ros2 bag play my_bag/ --start-offset 10.0

# Remap topic during playback
ros2 bag play my_bag/ --remap /scan:=/laser

# Play bag and publish clock (for use_sim_time nodes)
ros2 bag play my_bag/ --clock
```

## CLI — Inspection

```bash
# Bag info
ros2 bag info my_bag/

# List topics and message counts
ros2 bag info my_bag/ --verbose

# Convert bag format (sqlite3 → mcap or vice versa)
ros2 bag convert -i my_bag/ -o my_bag_mcap/ --output-options '{"output_bags": [{"uri": "my_bag_mcap", "storage_id": "mcap"}]}'
```

## Programmatic Recording (Python)

```python
import rclpy
from rclpy.node import Node
from rosbag2_py import SequentialWriter, StorageOptions, ConverterOptions
from rclpy.serialization import serialize_message
from sensor_msgs.msg import LaserScan

class BagWriter(Node):
    def __init__(self):
        super().__init__('bag_writer')

        writer = SequentialWriter()

        storage_options = StorageOptions(uri='my_programmatic_bag', storage_id='mcap')
        converter_options = ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr'
        )
        writer.open(storage_options, converter_options)

        # Create topic
        topic_info = rosbag2_py.TopicMetadata(
            name='/scan',
            type='sensor_msgs/msg/LaserScan',
            serialization_format='cdr'
        )
        writer.create_topic(topic_info)

        # Write a message
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        writer.write('/scan', serialize_message(msg),
                     self.get_clock().now().nanoseconds)

        writer.close()
```

## Programmatic Reading (Python)

```python
import rclpy
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
from rosidl_runtime_py.utilities import get_message

def read_bag(bag_path: str):
    reader = SequentialReader()
    storage_options = StorageOptions(uri=bag_path, storage_id='mcap')
    converter_options = ConverterOptions('', '')
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {t.name: t.type for t in topic_types}

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic == '/scan':
            msg_type = get_message(type_map[topic])
            msg = deserialize_message(data, msg_type)
            print(f't={timestamp} angle_min={msg.angle_min:.2f}')

if __name__ == '__main__':
    read_bag('./my_bag')
```

## Storage Format Comparison

| Format | Extension | Default In | Pros | Cons |
|---|---|---|---|---|
| SQLite3 | `.db3` | Humble, Iron | Simple, readable | Slow for large bags |
| MCAP | `.mcap` | Jazzy+ | Fast, seekable, compressed | Newer tooling |

## Filtering During Playback (Python Node)

```python
# Subscribe to bag topics and filter/republish
class BagFilter(Node):
    def __init__(self):
        super().__init__('bag_filter')
        # Subscribe to raw bag topic
        self.sub = self.create_subscription(
            LaserScan, '/scan', self.scan_cb,
            rclpy.qos.qos_profile_sensor_data)
        # Publish filtered
        self.pub = self.create_publisher(LaserScan, '/scan_filtered', 10)

    def scan_cb(self, msg):
        # Filter ranges < 0.5m
        import copy
        filtered = copy.deepcopy(msg)
        filtered.ranges = [r if r > 0.5 else float('inf') for r in msg.ranges]
        self.pub.publish(filtered)
```

## record_bag.launch.py

```python
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record',
                 '/scan', '/odom', '/tf', '/tf_static',
                 '--storage', 'mcap',
                 '-o', 'session_bags/run_001'],
            output='screen'
        ),
    ])
```
