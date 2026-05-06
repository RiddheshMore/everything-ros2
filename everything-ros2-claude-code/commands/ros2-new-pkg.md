# /ros2-new-pkg

Scaffold a new ROS 2 package with best practices baked in.

## Usage

```
/ros2-new-pkg my_robot_controller --type cpp --distro humble
/ros2-new-pkg my_sensor_driver --type python --distro jazzy
/ros2-new-pkg my_interface_pkg --type interfaces
/ros2-new-pkg my_nav_pkg --type cpp --with-lifecycle --with-nav2
```

## Options

| Option | Values | Description |
|---|---|---|
| `--type` | `cpp`, `python`, `interfaces`, `mixed` | Package type |
| `--distro` | `humble`, `jazzy`, `kilted`, `rolling` | Target distro |
| `--with-lifecycle` | flag | Include lifecycle node boilerplate |
| `--with-nav2` | flag | Add Nav2 dependency and simple commander |
| `--with-moveit` | flag | Add MoveIt2 dependency boilerplate |
| `--with-tf2` | flag | Add TF2 broadcaster/listener boilerplate |
| `--namespace` | string | Default node namespace |

## What Gets Generated

For `--type cpp`:
- `package.xml` (format 3, with all common deps)
- `CMakeLists.txt` (with install rules)
- `src/my_pkg_node.cpp` (node with parameters, pub/sub, timer)
- `include/my_pkg/my_pkg_node.hpp`
- `launch/my_pkg.launch.py` (with YAML params)
- `config/params.yaml`
- `README.md`

For `--type python`:
- `package.xml`
- `setup.py` + `setup.cfg`
- `resource/<pkg_name>` (empty marker file)
- `<pkg_name>/__init__.py`
- `<pkg_name>/my_node.py` (node with parameters, pub/sub)
- `launch/my_node.launch.py`
- `config/params.yaml`

For `--type interfaces`:
- `package.xml` (with rosidl dependencies)
- `CMakeLists.txt` (with rosidl_generate_interfaces)
- `msg/MyMessage.msg`
- `srv/MyService.srv`
- `action/MyAction.action`

## After Scaffolding

```bash
cd <your_ws>/src
/ros2-new-pkg my_pkg --type cpp --distro humble

# Build
cd ..
colcon build --packages-select my_pkg --symlink-install

# Source and run
source install/setup.bash
ros2 run my_pkg my_pkg_node

# Or with launch
ros2 launch my_pkg my_pkg.launch.py
```
