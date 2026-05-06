cmake_minimum_required(VERSION 2.8.3)
project(test_robot)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  nav_msgs
)

catkin_package(
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs geometry_msgs nav_msgs
)

include_directories(${catkin_INCLUDE_DIRS})

add_executable(diff_drive src/diff_drive.cpp)
target_link_libraries(diff_drive ${catkin_LIBRARIES})

add_executable(odom_publisher src/odom_publisher.cpp)
target_link_libraries(odom_publisher ${catkin_LIBRARIES})

install(TARGETS diff_drive odom_publisher
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch urdf config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
