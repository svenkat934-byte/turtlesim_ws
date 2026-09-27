#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class Draw_Spiral_Node(Node):
    def __init__(self):
        super().__init__("Draw_Spiral_Node")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        timer_period = 0.1
        self.counter = 0.0
        self.timer = self.create_timer(timer_period, self.move_in_circle)

    def move_in_circle(self):
        msg = Twist()
        msg.linear.x = 0.5 + self.counter
        msg.angular.z = 3.0
        self.publisher.publish(msg)
        self.get_logger().info("Drawing a Spiral...")
        self.counter += 0.05
        


def main(args=None):
    rclpy.init(args=args)
    node = Draw_Spiral_Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
