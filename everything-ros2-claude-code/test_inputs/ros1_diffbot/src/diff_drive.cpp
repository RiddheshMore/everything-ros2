#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <nav_msgs/Odometry.h>
#include <tf/transform_broadcaster.h>
#include <std_msgs/Float64.h>

class DiffDriveNode {
public:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    ros::Subscriber cmd_vel_sub_;
    ros::Publisher odom_pub_;
    ros::Publisher left_wheel_pub_;
    ros::Publisher right_wheel_pub_;
    tf::TransformBroadcaster tf_broadcaster_;

    double wheel_separation_;
    double wheel_radius_;
    double x_, y_, theta_;
    ros::Time last_time_;

    DiffDriveNode() : nh_private_("~"), x_(0.0), y_(0.0), theta_(0.0) {
        // ROS1 private params
        nh_private_.param("wheel_separation", wheel_separation_, 0.4);
        nh_private_.param("wheel_radius", wheel_radius_, 0.05);

        cmd_vel_sub_ = nh_.subscribe("/cmd_vel", 10, &DiffDriveNode::cmdVelCallback, this);
        odom_pub_ = nh_.advertise<nav_msgs::Odometry>("/odom", 10);
        left_wheel_pub_ = nh_.advertise<std_msgs::Float64>("/left_wheel_velocity", 10);
        right_wheel_pub_ = nh_.advertise<std_msgs::Float64>("/right_wheel_velocity", 10);

        last_time_ = ros::Time::now();
        ROS_INFO("DiffDrive node started. wheel_sep=%.2f wheel_rad=%.2f",
                 wheel_separation_, wheel_radius_);
    }

    void cmdVelCallback(const geometry_msgs::Twist::ConstPtr& msg) {
        double linear = msg->linear.x;
        double angular = msg->angular.z;

        // Differential drive kinematics
        double v_left = (linear - angular * wheel_separation_ / 2.0) / wheel_radius_;
        double v_right = (linear + angular * wheel_separation_ / 2.0) / wheel_radius_;

        ros::Time now = ros::Time::now();
        double dt = (now - last_time_).toSec();
        last_time_ = now;

        // Simple odometry integration
        double v = (v_left + v_right) / 2.0 * wheel_radius_;
        double omega = (v_right - v_left) * wheel_radius_ / wheel_separation_;
        theta_ += omega * dt;
        x_ += v * cos(theta_) * dt;
        y_ += v * sin(theta_) * dt;

        // Publish odometry
        nav_msgs::Odometry odom;
        odom.header.stamp = now;
        odom.header.frame_id = "odom";
        odom.child_frame_id = "base_link";
        odom.pose.pose.position.x = x_;
        odom.pose.pose.position.y = y_;
        odom.twist.twist.linear.x = v;
        odom.twist.twist.angular.z = omega;
        odom_pub_.publish(odom);

        // Publish TF odom → base_link (ROS1 way)
        geometry_msgs::TransformStamped odom_tf;
        odom_tf.header.stamp = now;
        odom_tf.header.frame_id = "odom";
        odom_tf.child_frame_id = "base_link";
        odom_tf.transform.translation.x = x_;
        odom_tf.transform.translation.y = y_;
        tf::Quaternion q;
        q.setRPY(0, 0, theta_);
        tf::quaternionTFToMsg(q, odom_tf.transform.rotation);
        tf_broadcaster_.sendTransform(odom_tf);

        // Publish wheel velocities
        std_msgs::Float64 lv, rv;
        lv.data = v_left;
        rv.data = v_right;
        left_wheel_pub_.publish(lv);
        right_wheel_pub_.publish(rv);

        ROS_INFO_THROTTLE(1.0, "cmd_vel: linear=%.2f angular=%.2f | wheels: L=%.2f R=%.2f",
                   linear, angular, v_left, v_right);
    }
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "diff_drive_node");
    DiffDriveNode node;
    ros::spin();
    return 0;
}
