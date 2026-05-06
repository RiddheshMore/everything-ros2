// ROS2 Humble — migrated from ROS1 roscpp diff_drive.cpp
// Migration: ros::NodeHandle → rclcpp::Node subclass
//            ros::param::get → declare_parameter + get_parameter
//            ros::Publisher/Subscriber → create_publisher / create_subscription
//            tf::TransformBroadcaster → tf2_ros::TransformBroadcaster
//            tf::quaternionTFToMsg → tf2::toMsg + tf2::Quaternion
//            ROS_INFO → RCLCPP_INFO
//            ros::spin() → rclcpp::spin()

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/float64.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <cmath>

class DiffDriveNode : public rclcpp::Node
{
public:
  DiffDriveNode()
  : Node("diff_drive_node"),
    x_(0.0), y_(0.0), theta_(0.0)
  {
    // Declare parameters with defaults (ROS2 requires declaration before use)
    this->declare_parameter("wheel_separation", 0.4);
    this->declare_parameter("wheel_radius", 0.05);

    wheel_separation_ = this->get_parameter("wheel_separation").get_parameter_value().get<double>();
    wheel_radius_      = this->get_parameter("wheel_radius").get_parameter_value().get<double>();

    // Create publisher (replaces nh_.advertise<T>)
    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/odom", 10);
    left_wheel_pub_  = this->create_publisher<std_msgs::msg::Float64>("/left_wheel_velocity", 10);
    right_wheel_pub_ = this->create_publisher<std_msgs::msg::Float64>("/right_wheel_velocity", 10);

    // Create subscription (replaces nh_.subscribe)
    cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel", 10,
      std::bind(&DiffDriveNode::cmdVelCallback, this, std::placeholders::_1));

    // TF2 broadcaster (replaces tf::TransformBroadcaster)
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

    last_time_ = this->get_clock()->now();

    RCLCPP_INFO(this->get_logger(),
      "DiffDrive node started. wheel_sep=%.2f wheel_rad=%.2f",
      wheel_separation_, wheel_radius_);
  }

private:
  void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    double linear  = msg->linear.x;
    double angular = msg->angular.z;

    // Differential drive kinematics
    double v_left  = (linear - angular * wheel_separation_ / 2.0) / wheel_radius_;
    double v_right = (linear + angular * wheel_separation_ / 2.0) / wheel_radius_;

    auto now = this->get_clock()->now();
    double dt = (now - last_time_).seconds();
    last_time_ = now;

    // Simple odometry integration
    double v     = (v_left + v_right) / 2.0 * wheel_radius_;
    double omega = (v_right - v_left) * wheel_radius_ / wheel_separation_;
    theta_ += omega * dt;
    x_ += v * std::cos(theta_) * dt;
    y_ += v * std::sin(theta_) * dt;

    // Build quaternion from yaw (replaces tf::Quaternion + setRPY)
    tf2::Quaternion q;
    q.setRPY(0.0, 0.0, theta_);

    // Publish odometry
    auto odom = nav_msgs::msg::Odometry();
    odom.header.stamp    = now.operator builtin_interfaces::msg::Time();
    odom.header.frame_id = "odom";
    odom.child_frame_id  = "base_link";
    odom.pose.pose.position.x    = x_;
    odom.pose.pose.position.y    = y_;
    odom.pose.pose.orientation   = tf2::toMsg(q);
    odom.twist.twist.linear.x    = v;
    odom.twist.twist.angular.z   = omega;
    odom_pub_->publish(odom);

    // Publish TF odom → base_link (replaces tf::TransformBroadcaster)
    geometry_msgs::msg::TransformStamped odom_tf;
    odom_tf.header.stamp    = odom.header.stamp;
    odom_tf.header.frame_id = "odom";
    odom_tf.child_frame_id  = "base_link";
    odom_tf.transform.translation.x = x_;
    odom_tf.transform.translation.y = y_;
    odom_tf.transform.translation.z = 0.0;
    odom_tf.transform.rotation       = tf2::toMsg(q);
    tf_broadcaster_->sendTransform(odom_tf);

    // Publish wheel velocities
    auto lv = std_msgs::msg::Float64();
    auto rv = std_msgs::msg::Float64();
    lv.data = v_left;
    rv.data = v_right;
    left_wheel_pub_->publish(lv);
    right_wheel_pub_->publish(rv);

    // Throttled log (replaces ROS_INFO_THROTTLE)
    static rclcpp::Time last_log = now;
    if ((now - last_log).seconds() >= 1.0) {
      RCLCPP_INFO(this->get_logger(),
        "cmd_vel: linear=%.2f angular=%.2f | wheels: L=%.2f R=%.2f",
        linear, angular, v_left, v_right);
      last_log = now;
    }
  }

  // Publishers
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr  left_wheel_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr  right_wheel_pub_;

  // Subscriber
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;

  // TF2
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

  // Parameters
  double wheel_separation_;
  double wheel_radius_;

  // Odometry state
  double x_, y_, theta_;
  rclcpp::Time last_time_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<DiffDriveNode>();
  try {
    rclcpp::spin(node);
  } catch (const std::exception & e) {
    RCLCPP_ERROR(node->get_logger(), "Exception: %s", e.what());
  }
  rclcpp::shutdown();
  return 0;
}
