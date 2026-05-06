#!/usr/bin/env node
/**
 * Hook: Check for ROS 1 API usage in Python files.
 * Warns when rospy, roscpp, roslaunch XML patterns, or other ROS 1 imports found.
 */

const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];
if (!filePath || !fs.existsSync(filePath)) process.exit(0);

const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split('\n');

const ROS1_PATTERNS = [
  { pattern: /import rospy/,        msg: "ROS 1: 'import rospy' → use 'import rclpy'" },
  { pattern: /from rospy/,          msg: "ROS 1: 'from rospy ...' → use 'from rclpy...'" },
  { pattern: /import rospkg/,       msg: "ROS 1: 'import rospkg' → use 'ament_index_python.packages'" },
  { pattern: /import rosgraph/,     msg: "ROS 1: 'import rosgraph' → no equivalent, use ros2 CLI tools" },
  { pattern: /rospy\.init_node/,    msg: "ROS 1: rospy.init_node() → class MyNode(Node): super().__init__('node_name')" },
  { pattern: /rospy\.Publisher/,    msg: "ROS 1: rospy.Publisher → self.create_publisher(MsgType, 'topic', depth)" },
  { pattern: /rospy\.Subscriber/,   msg: "ROS 1: rospy.Subscriber → self.create_subscription(MsgType, 'topic', cb, depth)" },
  { pattern: /rospy\.spin\(\)/,     msg: "ROS 1: rospy.spin() → rclpy.spin(node)" },
  { pattern: /rospy\.Rate/,         msg: "ROS 1: rospy.Rate → self.create_timer(period, callback)" },
  { pattern: /rospy\.sleep/,        msg: "ROS 1: rospy.sleep() → use timer callbacks, never sleep in ROS 2" },
  { pattern: /rospy\.loginfo/,      msg: "ROS 1: rospy.loginfo() → self.get_logger().info()" },
  { pattern: /rospy\.logerr/,       msg: "ROS 1: rospy.logerr() → self.get_logger().error()" },
  { pattern: /rospy\.logwarn/,      msg: "ROS 1: rospy.logwarn() → self.get_logger().warn()" },
  { pattern: /rospy\.get_param/,    msg: "ROS 1: rospy.get_param() → self.get_parameter('name').get_parameter_value()..." },
  { pattern: /get_package_share_directory.*rospkg/, msg: "ROS 1: Use ament_index_python instead of rospkg" },
];

let found = false;
lines.forEach((line, i) => {
  ROS1_PATTERNS.forEach(({ pattern, msg }) => {
    if (pattern.test(line)) {
      if (!found) {
        process.stderr.write(`\n[ROS 2 Hook] ⚠️  ROS 1 API detected in ${path.basename(filePath)}:\n`);
        found = true;
      }
      process.stderr.write(`  Line ${i + 1}: ${msg}\n`);
    }
  });
});

if (found) {
  process.stderr.write(`\nThis project uses ROS 2. See rules/common/ros2-fundamentals.md for correct APIs.\n\n`);
}

process.exit(0); // Non-blocking — warn only, don't fail
