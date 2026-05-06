# /tf-tree

Analyze the TF2 frame tree in the workspace using @tf2-agent.

## Usage

```
/tf-tree                    # scan source code for frame ID usage
/tf-tree --live             # query running system (ros2 run tf2_tools view_frames)
/tf-tree --check-rep105     # verify REP-105 compliance (map→odom→base_link)
```

## What It Does

**Static analysis (default):**
- Scans all source files for hardcoded frame ID strings
- Finds `StaticTransformBroadcaster` and `TransformBroadcaster` calls
- Finds `lookup_transform` calls and checks for timeout argument
- Checks that frame IDs are parameterized, not hardcoded
- Detects missing `map → odom → base_link` chain declarations

**Live analysis (`--live`):**
- Runs `ros2 run tf2_tools view_frames` on the running system
- Parses the generated PDF/dot graph
- Reports orphan frames (no parent in the tree)
- Reports stale transforms (not updated in >1s for dynamic frames)

## Output

```
TF2 Frame Analysis
==================
Scanned: 5 source files

my_robot_driver/odom_publisher.py:
  ✅ Broadcasts: base_link → odom (dynamic, 50Hz)
  ❌ Hardcoded frame ID: 'map' (line 34) — use parameter instead
  ❌ lookup_transform called without timeout (line 67) — add timeout=Duration(seconds=1.0)

my_robot_description/robot_state_publisher:
  ✅ Broadcasts all links from URDF (static chain)

REP-105 Chain:
  ✅ map frame: published by map_server (static)
  ✅ odom frame: published by my_robot_driver
  ✅ base_link frame: published by robot_state_publisher
  ✅ base_link → odom → map chain complete

Issues: 2 errors, 0 warnings
```
