#!/usr/bin/env python3
"""
ROS2 Humble — migrated from ROS1 odom_publisher.py (rospy)

Migration map:
  rospy.init_node('odom_monitor')         → super().__init__('odom_monitor')
  rospy.get_param('~log_rate', 1.0)       → declare_parameter + get_parameter
  rospy.Subscriber(...)                    → self.create_subscription(...)
  rospy.Rate(hz) + rate.sleep()           → self.create_timer(period, callback)
  rospy.loginfo(...)                       → self.get_logger().info(...)
  rospy.is_shutdown()                      → not rclpy.ok()
  rospy.ROSInterruptException              → KeyboardInterrupt + try/finally
"""
import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdomMonitor(Node):
    def __init__(self):
        super().__init__('odom_monitor')

        # Declare parameter before reading (ROS2 requirement)
        self.declare_parameter('log_rate', 1.0)
        log_rate = self.get_parameter('log_rate').get_parameter_value().double_value

        self.last_odom = None
        self.msg_count = 0

        # Subscription replaces rospy.Subscriber
        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10  # QoS depth
        )

        # Timer replaces rospy.Rate + rate.sleep() loop
        # period = 1.0 / log_rate seconds between log prints
        self.create_timer(1.0 / log_rate, self.log_callback)

        self.get_logger().info(
            f'OdomMonitor started. log_rate={log_rate:.1f} Hz'
        )

    def odom_callback(self, msg: Odometry):
        self.last_odom = msg
        self.msg_count += 1

    def log_callback(self):
        """Called at log_rate Hz — replaces the rospy.Rate spin loop."""
        if self.last_odom is None:
            return

        x = self.last_odom.pose.pose.position.x
        y = self.last_odom.pose.pose.position.y
        q = self.last_odom.pose.pose.orientation

        # Quaternion → yaw (same formula, but using self.get_logger())
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        self.get_logger().info(
            f'Pose: x={x:.2f} y={y:.2f} yaw={yaw:.2f} | msgs={self.msg_count}'
        )


def main():
    rclpy.init()
    node = OdomMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
