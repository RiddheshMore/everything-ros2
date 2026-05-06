# /urdf-check

Validate a URDF or XACRO file using the @urdf-validator agent.

## Usage

```
/urdf-check
/urdf-check path/to/robot.urdf.xacro
/urdf-check --visualize     # launch RViz after validation
/urdf-check --expand-only   # just expand XACRO without validating
```

## What It Does

1. Finds all `.urdf` and `.xacro` files in the workspace
2. Expands XACRO to plain URDF (`xacro file.xacro > /tmp/expanded.urdf`)
3. Runs `check_urdf` on each expanded file
4. Validates:
   - Link/joint graph integrity (no broken references, no cycles)
   - Inertia matrix validity (positive-definite)
   - Mesh file paths existence
   - Joint limits for revolute/prismatic joints
   - XACRO macro argument completeness
5. Optionally launches RViz with `urdf_tutorial display.launch.py`

## Output

```
URDF Validation Report
======================
Found 2 URDF/XACRO files:
  src/my_robot_description/urdf/robot.urdf.xacro
  src/my_robot_description/urdf/arm.xacro

robot.urdf.xacro:
  ✅ XACRO expanded OK → /tmp/robot_expanded.urdf
  ✅ XML parse: OK
  ✅ Link/joint graph: 14 links, 13 joints, root=base_link
  ❌ Link 'gripper_left': missing <inertial> (required for simulation)
  ⚠️  Mesh path uses relative path — use package:// URI
  ✅ All joint limits present

arm.xacro:
  ✅ All checks passed (6 links, 5 joints)

Errors: 1  Warnings: 1
```
