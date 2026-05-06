---
name: realtime-patterns
description: Real-time ROS 2 — executor types, callback groups, CPU isolation, scheduling priority, DDS tuning
triggers:
  - realtime
  - latency
  - executor
  - callback
  - priority
  - scheduling
  - cyclonedds
  - fastrtps
  - thread
  - mutex
  - zero-copy
---

# Real-Time ROS 2 Patterns

## Quick-Reference Decision Table

| Requirement | Executor | Callback Group | DDS |
|------------|----------|---------------|-----|
| Simple node | SingleThreaded | Default | FastRTPS |
| Max latency | StaticSingleThreaded | MutuallyExclusive | CycloneDDS |
| Max throughput | MultiThreaded | Reentrant | CycloneDDS |
| Deterministic | StaticSingleThreaded | MutuallyExclusive | CycloneDDS + SHM |

---

## Complete Copy-Paste Code

### 1. Static Single-Threaded Executor (Lowest Latency)

```python
#!/usr/bin/env python3
# static_executor_node.py
import rclpy
from rclpy.node import Node
from rclpy.executors import StaticSingleThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # Static executor - no dynamic callbacks
        self._executor = StaticSingleThreadedExecutor()

        # Mutually exclusive groups prevent parallel execution
        self._control_group = MutuallyExclusiveCallbackGroup()
        self._sensor_group = MutuallyExclusiveCallbackGroup()

        # 1kHz control loop
        self.create_timer(0.001, self.control_loop, callback_group=self._control_group)

        # Sensor subscription
        self.create_subscription(
            sensor_msgs.msg.JointState,
            '/joint_states',
            self.joint_callback,
            10,
            callback_group=self._sensor_group
        )

        # Add node to executor
        self._executor.add_node(self)
        # IMPORTANT: spin() is blocking
        self._executor.spin()

    def control_loop(self):
        # Deterministic execution - no parallel callbacks
        pass

    def joint_callback(self):
        # Will not run concurrently with control_loop
        pass
```

### 2. Multi-Threaded with Reentrant Callback Group

```python
#!/usr/bin/env python3
# parallel_node.py
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import threading

class ParallelNode(Node):
    def __init__(self):
        super().__init__('parallel_node')

        # Reentrant = callbacks can run in parallel
        self._reentrant_group = ReentrantCallbackGroup()

        # Multiple parallel timers
        for i in range(4):
            self.create_timer(0.01, self.process_callback,
                            callback_group=self._reentrant_group)

        # Parallel subscriptions
        self.create_subscription(PointCloud2, '/lidar',
                                self.lidar_callback, 10,
                                callback_group=self._reentrant_group)
        self.create_subscription(Image, '/camera',
                                self.camera_callback, 10,
                                callback_group=self._reentrant_group)

        # CRITICAL: Lock for shared state
        self._lock = threading.Lock()
        self._shared_state = {}

        # Use all available cores
        cpu_count = os.cpu_count() or 4
        self._executor = MultiThreadedExecutor(num_threads=cpu_count)
        self._executor.add_node(self)
        self._executor.spin()

    def lidar_callback(self, msg):
        # Safe: each callback has its own execution context
        with self._lock:
            self._shared_state['lidar'] = process_lidar(msg)

    def camera_callback(self, msg):
        with self._lock:
            self._shared_state['camera'] = process_camera(msg)
```

### 3. Timer Latency Benchmark

```python
#!/usr/bin/env python3
# timer_benchmark.py
import rclpy
from rclpy.node import Node
import numpy as np

class TimerBenchmark(Node):
    def __init__(self):
        super().__init__('timer_benchmark')

        self.period_ms = 10.0  # Target period
        self.latencies_ns = []

        self.last_call = self.get_clock().now()
        self.create_timer(self.period_ms / 1000.0, self.timer_callback)

        self.create_timer(5.0, self.report)  # Report every 5s

    def timer_callback(self):
        now = self.get_clock().now()
        actual_ns = (now - self.last_call).nanoseconds
        expected_ns = self.period_ms * 1_000_000
        latency = actual_ns - expected_ns

        self.latencies_ns.append(latency)
        if len(self.latencies_ns) > 10000:
            self.latencies_ns.pop(0)

        self.last_call = now

    def report(self):
        if not self.latencies_ns:
            return

        latencies_ms = np.array(self.latencies_ns) / 1_000_000
        self.get_logger().info(
            f"Timer latency (n={len(latencies_ms)}): "
            f"mean={latencies_ms.mean():.3f}ms, "
            f"std={latencies_ms.std():.3f}ms, "
            f"max={latencies_ms.max():.3f}ms, "
            f"p99={np.percentile(latencies_ms, 99):.3f}ms"
        )
```

### 4. CPU Isolation Setup

```bash
# /etc/default/grub - Add to GRUB_CMDLINE_LINUX_DEFAULT
# For Ubuntu 22.04 with kernel 5.15+
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash mitigations=off \
    isolcpus=1,2,3 \
    nohz_full=1,2,3 \
    rcu_nocbs=1,2,3 \
    intel_pstate=driver"

sudo update-grub
sudo reboot
```

```python
#!/usr/bin/env python3
# cpu_isolated_thread.py
import os
import threading
import subprocess

def pin_to_isolated_cpu(cpu_id=1):
    """Pin current process to isolated CPU"""
    pid = os.getpid()

    # Verify CPU is isolated
    with open('/sys/devices/system/cpu/cpu{}/online'.format(cpu_id)) as f:
        if f.read().strip() == '0':
            raise RuntimeError(f"CPU {cpu_id} is not online")

    # Check isolcpus
    with open('/sys/devices/system/cpu/isolated') as f:
        if str(cpu_id) not in f.read():
            print(f"WARNING: CPU {cpu_id} not in isolcpus list")

    # Pin process
    subprocess.run(['taskset', '-p', '-c', str(cpu_id), str(pid)])
    print(f"Pinned to CPU {cpu_id}")

    # Pin current thread
    os.sched_setaffinity(0, {cpu_id})
```

### 5. Real-Time Scheduler

```python
#!/usr/bin/env python3
# realtime_scheduler.py
import os
import rclpy
from rclpy.node import Node

class RealtimeNode(Node):
    def __init__(self):
        super().__init__('realtime_node')

        # Set SCHED_FIFO (requires root/CAP_SYS_NICE)
        self.set_realtime_priority()

        # Create timer
        self.create_timer(0.001, self.control_loop)

    def set_realtime_priority(self):
        # Get max priority for SCHED_FIFO
        max_prio = os.sched_get_priority_max(os.SCHED_FIFO)

        param = os.sched_param(max_prio - 5)  # 5 below max

        try:
            os.sched_setscheduler(0, os.SCHED_FIFO, param)
            self.get_logger().info(f'Real-time priority set: {max_prio - 5}')
        except PermissionError:
            self.get_logger().warn('Cannot set SCHED_FIFO - try: sudo setcap cap_sys_nice+ep this_binary')

        # Or use nice for soft real-time
        os.nice(-10)

    def control_loop(self):
        start = self.get_clock().now()
        # Do work
        elapsed = (self.get_clock().now() - start).nanoseconds / 1e6
        if elapsed > 1.0:
            self.get_logger().error(f'Deadline missed: {elapsed:.2f}ms')
```

### 6. CycloneDDS Zero-Copy Configuration

```xml
<!-- /etc/cyclonedds/config.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<cyclonedds xmlns="https://cyclonedds.io/xsd/1.11.1">
  <domain id="any">
    <discovery>
      <SPDPDomain/>
    </discovery>

    <transport_builtin>
      <!-- Use UDP for local only -->
      < 仅 type>UDPv4</ 仅 type>
    </transport_builtin>

    <general>
      <!-- Shared memory for zero-copy between processes -->
      <MaxNetworkSocketReceiveBufferSize>2097152</MaxNetworkSocketReceiveBufferSize>
      <MaxMessageSize>65500</MaxMessageSize>
    </general>

    <internal>
      <!-- High water marks for large data -->
      <Watermarks>
        <WhcHigh>100MB</WhcHigh>
        <WhcLow>50MB</WhcLow>
      </Watermarks>

      <Scheduling>
        <!-- Thread priorities -->
        <ThreadPoolSchedulingPolicy>FIFO</ThreadPoolSchedulingPolicy>
      </Scheduling>
    </internal>
  </domain>
</cyclonedds>
```

```bash
# Use this config
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///etc/cyclonedds/config.xml

# Or inline:
export CYCLONEDDS_URI='<cyclonedds><domain id="any"><general><MaxMessageSize>65500</MaxMessageSize></general></domain></cyclonedds>'
```

### 7. Callback Timing Guard

```python
#!/usr/bin/env python3
# callback_guard.py
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
import threading
import time

class CallbackGuard(Node):
    def __init__(self):
        super().__init__('callback_guard')

        self._group = MutuallyExclusiveCallbackGroup()

        # Guard: track if callback is already running
        self._callback_running = False
        self._lock = threading.Lock()

        self.create_timer(0.01, self.guarded_callback,
                         callback_group=self._group)

    def guarded_callback(self):
        with self._lock:
            if self._callback_running:
                self.get_logger().warn('Callback overrun - skipping this cycle')
                return
            self._callback_running = True

        try:
            # Do work
            time.sleep(0.005)  # Simulate work
        finally:
            with self._lock:
                self._callback_running = False
```

---

## CLI Debug Commands

```bash
# Check timer latency
ros2 run rclcpp --timer_latency

# DDS statistics
export RCLCPP_LOGGING_USE_IMMUTABLE_TOPICS=1
ros2 topic echo /rt/log/...  # DDS internal stats

# CPU scheduling
chrt -p 0 $$  # Show current scheduler
chrt -f 50 command  # Run with FIFO scheduler

# CPU isolation
cat /sys/devices/system/cpu/isolated
cat /sys/kernel/debug/tracing/trace  # Check for timer tick migration

# Thread CPU affinity
ps -eLo pid,lwp,psr,comm | grep ros2

# CycloneDDS discovery
export CYCLONEDDS_TRACE=Discovery
ros2 topic list
```

---

## Latency Targets

| Operation | Target | Acceptable | Critical |
|-----------|--------|------------|----------|
| Timer callback | < 0.1ms | < 1ms | > 2ms |
| Subscription receive | < 0.5ms | < 2ms | > 5ms |
| DDS round-trip | < 1ms | < 5ms | > 10ms |
| Control loop | < 1ms | < 5ms | > 10ms |
