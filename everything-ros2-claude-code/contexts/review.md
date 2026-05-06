# ROS 2 Code Review Context

You are reviewing ROS 2 code for quality, correctness, and safety.
Run ALL of these checks before approving any PR:

## Pre-Review Agent Dispatch

Automatically run:
- `@topic-schema-agent` — naming conventions
- `@qos-agent` — QoS compatibility
- `@distro-compat-agent` — target distro APIs
- `@package-structure-agent` — package.xml completeness
- `@tf2-agent` — frame ID usage

If the PR touches URDF/XACRO: also run `@urdf-validator`
If the PR touches launch files: also run `@launch-agent`
If the PR touches .msg/.srv/.action: also run `@interface-agent`

## Review Checklist

### Safety
- [ ] No `time.sleep()` or blocking calls inside ROS callbacks
- [ ] No hardcoded frame IDs
- [ ] Error states handled (TF exceptions, service timeouts)
- [ ] No unbounded spin loops (`while True: spin_some()`)

### Correctness
- [ ] Parameters declared before getting them
- [ ] QoS appropriate for each message type
- [ ] No ROS 1 APIs (`rospy`, `roscpp`)
- [ ] Relative topic names used (for namespace compatibility)
- [ ] `use_sim_time` parameter supported

### Completeness
- [ ] package.xml has all dependencies
- [ ] Launch file exists and installs correctly
- [ ] Node documented (topics, services, parameters, TF frames)
- [ ] Unit tests present

### Lifecycle Nodes (if applicable)
- [ ] Resources allocated in `on_configure`, not constructor
- [ ] Timers created in `on_activate`, cancelled in `on_deactivate`
- [ ] `super().on_activate(state)` called for lifecycle publishers

## Report Format

```
ROS 2 Code Review
=================
PR: [title]
Target distro: humble

BLOCKING issues (must fix):
  ❌ ...

NON-BLOCKING (should fix):
  ⚠️  ...

APPROVED items:
  ✅ ...
```
