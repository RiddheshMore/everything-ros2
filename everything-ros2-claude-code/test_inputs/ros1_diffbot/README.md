# ROS1 Migration Test Input: `ros1_diffbot`

This package is a realistic ROS1 differential drive robot, intentionally written in ROS1 style.

## Files

```
ros1_diffbot/
├── package.xml           ← Format 1 (catkin, run_depend)
├── CMakeLists.txt        ← catkin_package(), catkin_LIBRARIES
├── launch/
│   └── robot.launch      ← XML format with <node>, <param>, <remap>, <include>
├── src/
│   ├── diff_drive.cpp    ← roscpp: NodeHandle, ros::param, tf::TransformBroadcaster
│   └── odom_publisher.py ← rospy: rospy.init_node, rospy.get_param, rospy.Rate
└── urdf/
    └── (use test_ros1_robot.urdf from workspace root)
```

## Known ROS1 Patterns to Migrate

- `catkin` → `ament_cmake`
- `ros::NodeHandle nh_` → inherit `rclcpp::Node`
- `nh_private_.param(...)` → `declare_parameter + get_parameter`
- `ros::Publisher/Subscriber` → `create_publisher/create_subscription`
- `tf::TransformBroadcaster` → `tf2_ros::TransformBroadcaster`
- `tf::quaternionTFToMsg` → `tf2::toMsg` + `tf2::Quaternion`
- `ROS_INFO` / `ROS_INFO_THROTTLE` → `get_logger().info()`
- `rospy.init_node` → `super().__init__()`
- `rospy.get_param` → `declare_parameter + get_parameter`
- `rospy.Rate + sleep` → `create_timer(callback)`
- `rospy.ROSInterruptException` → `rclpy.ok()` loop with `try/finally`
- XML launch → `.launch.py` Python

## Migration Goal

Produce a complete ROS2 Humble package:
1. `package.xml` Format 3
2. `CMakeLists.txt` with `ament_cmake`  
3. `src/diff_drive.cpp` → `rclcpp::Node` subclass
4. `src/odom_publisher.py` → `rclpy.Node` subclass
5. `launch/robot.launch.py` → Python launch
6. Add `<ros2_control>` URDF section for `diff_drive_controller`
7. `config/diff_drive_controller.yaml`
