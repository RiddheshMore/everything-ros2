# /interface-check

Validate all .msg, .srv, and .action files using @interface-agent.

## Usage

```
/interface-check
/interface-check --package my_interfaces
```

## What It Does

- Finds all `.msg`, `.srv`, `.action` files in the workspace
- Validates field types (catches `float`, `double`, `int` — ROS 2 uses `float32`, `float64`, `int32`)
- Checks file naming convention (`CamelCase.msg`)
- Validates action file has exactly 3 sections (goal/result/feedback separated by `---`)
- Validates service file has exactly 2 sections (request/response separated by `---`)
- Checks nested type packages are in `DEPENDENCIES` list of `rosidl_generate_interfaces`
- Warns when sensor data missing `std_msgs/Header`

## Output

```
Interface Validation
====================
Found: 3 msg, 2 srv, 1 action

msg/SensorData.msg:
  ❌ Line 2: field type 'float' invalid — use 'float32' or 'float64'
  ❌ Line 4: field type 'int' invalid — use 'int8', 'int16', 'int32', or 'int64'
  ⚠️  No std_msgs/Header — add if this message needs a timestamp

msg/RobotStatus.msg:
  ✅ All field types valid
  ✅ Constants use ALL_CAPS naming

srv/SetMode.srv:
  ✅ Two sections separated by ---
  ✅ Response includes 'bool success'

action/Navigate.action:
  ✅ Three sections (goal/result/feedback)
  ⚠️  Feedback missing std_msgs/Header — consider adding for timestamped pose feedback

CMakeLists.txt:
  ❌ 'geometry_msgs' used in Navigate.action but missing from DEPENDENCIES list

Total: 3 errors, 2 warnings
```
