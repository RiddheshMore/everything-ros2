#!/usr/bin/env python
"""
ROS1 odometry monitor node (Python).
Subscribes to /odom and logs statistics.
"""
import rospy
import math
from nav_msgs.msg import Odometry


class OdomMonitor:
    def __init__(self):
        rospy.init_node('odom_monitor')
        self.log_rate = rospy.get_param('~log_rate', 1.0)
        self.sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.rate = rospy.Rate(self.log_rate)
        self.last_odom = None
        self.msg_count = 0

    def odom_callback(self, msg):
        self.last_odom = msg
        self.msg_count += 1

    def run(self):
        while not rospy.is_shutdown():
            if self.last_odom:
                x = self.last_odom.pose.pose.position.x
                y = self.last_odom.pose.pose.position.y
                q = self.last_odom.pose.pose.orientation
                yaw = math.atan2(
                    2.0 * (q.w * q.z + q.x * q.y),
                    1.0 - 2.0 * (q.y * q.y + q.z * q.z)
                )
                rospy.loginfo("Pose: x=%.2f y=%.2f yaw=%.2f | msgs=%d",
                              x, y, yaw, self.msg_count)
            self.rate.sleep()


if __name__ == '__main__':
    try:
        monitor = OdomMonitor()
        monitor.run()
    except rospy.ROSInterruptException:
        pass
