---
name: package-structure
description: ROS 2 package.xml, CMakeLists.txt, and ament build system patterns
triggers:
  - new package
  - package.xml
  - CMakeLists
  - setup.py
  - ament_cmake
  - ament_python
  - colcon build
---

# ROS 2 Package Structure Patterns

## Package Types

### ament_cmake (C++ or mixed)
```
my_cpp_pkg/
├── CMakeLists.txt
├── package.xml
├── include/my_cpp_pkg/
│   └── my_node.hpp
├── src/
│   └── my_node.cpp
├── launch/
│   └── my_node.launch.py
└── config/
    └── params.yaml
```

### ament_python (Python-only)
```
my_python_pkg/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/my_python_pkg   ← empty file, required
├── my_python_pkg/
│   ├── __init__.py
│   └── my_node.py
├── launch/
│   └── my_node.launch.py
└── config/
    └── params.yaml
```

### ament_cmake_python (both C++ and Python)
```
my_mixed_pkg/
├── CMakeLists.txt
├── package.xml
├── setup.py
├── setup.cfg
├── resource/my_mixed_pkg
├── src/               ← C++ nodes
├── my_mixed_pkg/      ← Python modules
│   ├── __init__.py
│   └── utils.py
└── launch/
```

## Minimal CMakeLists.txt (C++ Node)

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_cpp_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
# Add all packages you #include here ↑

add_executable(my_node src/my_node.cpp)
ament_target_dependencies(my_node rclcpp std_msgs)

install(TARGETS my_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}/)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

## Minimal package.xml (Format 3)

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
  schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <n>my_cpp_pkg</n>
  <version>0.0.1</version>
  <description>Brief description here</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

## Dependency Tag Guide

| Tag | When to Use |
|---|---|
| `<depend>` | Both build and runtime dependency |
| `<build_depend>` | Only needed to compile |
| `<exec_depend>` | Only needed at runtime (Python imports) |
| `<build_export_depend>` | Needed by packages that depend on yours |
| `<test_depend>` | Only for tests |
| `<buildtool_depend>` | Build tools (ament_cmake, rosidl_default_generators) |
