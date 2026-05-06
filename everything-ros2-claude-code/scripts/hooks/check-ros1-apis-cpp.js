#!/usr/bin/env node
/**
 * Hook: Check for ROS 1 API usage in C++ files.
 */

const fs = require('fs');
const path = require('path');

const filePath = process.argv[2];
if (!filePath || !fs.existsSync(filePath)) process.exit(0);

const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split('\n');

const ROS1_CPP_PATTERNS = [
  { pattern: /#include\s+["<]ros\/ros\.h[">]/,         msg: 'ROS 1: #include <ros/ros.h> → #include "rclcpp/rclcpp.hpp"' },
  { pattern: /#include\s+["<]roscpp\//,                msg: 'ROS 1: roscpp header → use rclcpp headers' },
  { pattern: /ros::init\(/,                             msg: 'ROS 1: ros::init() → rclcpp::init(argc, argv)' },
  { pattern: /ros::NodeHandle/,                        msg: 'ROS 1: ros::NodeHandle → class MyNode : public rclcpp::Node' },
  { pattern: /ros::Publisher/,                         msg: 'ROS 1: ros::Publisher → rclcpp::Publisher<T>::SharedPtr' },
  { pattern: /ros::Subscriber/,                        msg: 'ROS 1: ros::Subscriber → rclcpp::Subscription<T>::SharedPtr' },
  { pattern: /ros::ServiceServer/,                     msg: 'ROS 1: ros::ServiceServer → rclcpp::Service<T>::SharedPtr' },
  { pattern: /ros::ServiceClient/,                     msg: 'ROS 1: ros::ServiceClient → rclcpp::Client<T>::SharedPtr' },
  { pattern: /ros::spin\(\)/,                          msg: 'ROS 1: ros::spin() → rclcpp::spin(node)' },
  { pattern: /ros::spinOnce\(\)/,                      msg: 'ROS 1: ros::spinOnce() → executor.spin_some()' },
  { pattern: /ros::Rate/,                              msg: 'ROS 1: ros::Rate → create_wall_timer() with callback' },
  { pattern: /ROS_INFO\s*\(/,                          msg: 'ROS 1: ROS_INFO() → RCLCPP_INFO(get_logger(), ...)' },
  { pattern: /ROS_WARN\s*\(/,                          msg: 'ROS 1: ROS_WARN() → RCLCPP_WARN(get_logger(), ...)' },
  { pattern: /ROS_ERROR\s*\(/,                         msg: 'ROS 1: ROS_ERROR() → RCLCPP_ERROR(get_logger(), ...)' },
  { pattern: /ROS_DEBUG\s*\(/,                         msg: 'ROS 1: ROS_DEBUG() → RCLCPP_DEBUG(get_logger(), ...)' },
  { pattern: /nh\.param\(/,                            msg: 'ROS 1: nh.param() → declare_parameter() + get_parameter()' },
  { pattern: /nh\.advertise\(/,                        msg: 'ROS 1: nh.advertise() → create_publisher<T>(topic, depth)' },
  { pattern: /nh\.subscribe\(/,                        msg: 'ROS 1: nh.subscribe() → create_subscription<T>(topic, depth, cb)' },
];

let found = false;
lines.forEach((line, i) => {
  ROS1_CPP_PATTERNS.forEach(({ pattern, msg }) => {
    if (pattern.test(line)) {
      if (!found) {
        process.stderr.write(`\n[ROS 2 Hook] ⚠️  ROS 1 C++ API detected in ${path.basename(filePath)}:\n`);
        found = true;
      }
      process.stderr.write(`  Line ${i + 1}: ${msg}\n`);
    }
  });
});

if (found) {
  process.stderr.write(`\nSee rules/cpp/rclcpp-rules.md for correct ROS 2 C++ patterns.\n\n`);
}

process.exit(0);
