# /ros1-to-ros2

Migrate a ROS 1 package to ROS 2. Uses @ros1-migrator agent exclusively.
Output is always pure ROS 2. Any ROS 1 API remaining is a failure.

## Usage

```
/ros1-to-ros2                        # migrate entire workspace
/ros1-to-ros2 --file src/my_node.py  # migrate single file
/ros1-to-ros2 --distro humble        # target distro (default: humble)
/ros1-to-ros2 --check                # audit only, don't modify
```

## Process

1. Scans for all ROS 1 patterns (rospy, roscpp, catkin, XML launch)
2. Reports all items requiring migration before changing anything
3. Applies translations in order: package.xml → CMakeLists → source → launch
4. Runs `@package-structure-agent` to verify new package.xml
5. Runs `@topic-schema-agent` to verify no name convention violations
6. Shows full diff of changes

---

# /dds-debug

Debug DDS communication issues. Uses @dds-tuner agent.

## Usage

```
/dds-debug                   # full DDS audit
/dds-debug --topic /scan     # focus on a specific topic
/dds-debug --fleet           # multi-robot discovery audit
```

## Checks

1. QoS compatibility between all publishers and subscribers
2. RMW implementation and version
3. Discovery mode (multicast vs Discovery Server)
4. Network interface binding
5. Socket buffer sizes for high-bandwidth topics
6. ROS_DOMAIN_ID consistency

---

# /sros2-setup

Generate SROS2 security keystore and access control policies.
Uses @sros2-secops agent.

## Usage

```
/sros2-setup --robot my_robot --nodes sensor_driver,navigation,controller
/sros2-setup --validate          # validate existing keystore
/sros2-setup --rotate-certs      # regenerate expiring certificates
```

## Output

Generates:
- Keystore at `./ros2_security_keystore/`
- Enclave for each named node
- `permissions.xml` with least-privilege topic access per node
- Signed `permissions.p7s`
- Launch file additions for security environment variables
- `.gitignore` entry for keystore directory

---

# /tf-audit

Audit the TF2 transform tree for a ROS 2 system.
Uses @tf2-cartographer agent.

## Usage

```
/tf-audit                        # full audit
/tf-audit --frame laser_link     # check specific frame exists
/tf-audit --rep105               # check REP-105 compliance
```

## Checks

1. REP-105 chain completeness (map → odom → base_link)
2. All sensor frames declared as static transforms
3. No hardcoded frame IDs in source code
4. All `lookup_transform()` calls have timeouts
5. Euler-to-quaternion conversions use `tf_transformations` library
6. No TF loops in the frame tree
7. Camera optical frame conventions correct

---

# /test-ros2

Generate and run tests for a ROS 2 package.
Uses @test-engineer agent.

## Usage

```
/test-ros2                         # generate tests for current package
/test-ros2 --node my_node          # test specific node
/test-ros2 --type integration      # launch_testing integration test
/test-ros2 --type unit             # GTest or pytest unit test
/test-ros2 --lint                  # run ament_lint only
```

## Output

- `test/test_<node>.launch.py` — integration test with ReadyToTest
- `test/test_<node>_unit.cpp` or `.py` — unit tests
- CMakeLists.txt additions for test targets
- package.xml test dependencies
- `colcon test` command to run them
