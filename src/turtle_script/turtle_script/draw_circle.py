#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class Draw_Circle_Node(Node):
    def __init__(self):
        super().__init__("draw_circle_node")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.move_in_circle)

    def move_in_circle(self):
        msg = Twist()
        msg.linear.x = 0.5 
        msg.angular.z = 1.0
        self.publisher.publish(msg)
        self.get_logger().info("Drawing a circle...")
        


def main(args=None):
    rclpy.init(args=args)
    node = Draw_Circle_Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
