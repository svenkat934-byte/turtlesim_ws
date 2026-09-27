

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen
from turtlesim.msg import Pose

import math


class Draw_Aum_Node(Node):

    def __init__(self):
        super().__init__("draw_aum_node")

        # Publisher
        self.cmdvel_pub_ = self.create_publisher(
            Twist, "/turtle1/cmd_vel", 10
        )

        # Pose subscriber
        self.pose_sub_ = self.create_subscription(
            Pose,
            "/turtle1/pose",
            self.callback_turtle_pose,
            10
        )

        # SetPen service client
        self.setpen_client_ = self.create_client(
            SetPen, "/turtle1/set_pen"
        )

        while not self.setpen_client_.wait_for_service(
            timeout_sec=1.0
        ):
            self.get_logger().info("Waiting for SetPen service...")

        # Current turtle pose
        self.x = None
        self.y = None
        self.theta = None

        # Approximate Aum coordinates
        # Each inner list is one continuous stroke

        self.strokes = [

            # Main up and left curve
            [
                (3.0, 6.7),
                (2.8, 7.2),
                (3.2, 7.5),
                (4.5, 7.6),
                (5.3, 7.2),
                (5.6, 6.6),
                (4.5, 5.5),
                (3.5, 5.5),
                (3.6, 5.2),
                (4.3, 5.3),
                (5.1, 5.2),
                (5.8, 4.7),
                (6.1, 3.9),
                (6.0, 3.0),
                (5.4, 2.2),
                (4.5, 1.8),
                (3.5, 1.8),
                (2.5, 2.3),
                (1.5, 3.4),
                (1.0, 4.5),
                (0.8, 4.5),


            ],

            # Right-hand curved stroke
            [
                (4.7, 5.3),
                (5.0, 5.5),
                (6.5, 5.6),
                (7.1, 5.9),
                (7.8, 6.7),
                (8.5, 7.0),
                (9.1, 6.7),
                (9.6, 5.9),
                (9.9, 4.9),
                (9.8, 3.8),
                (9.3, 2.8),
                (8.6, 2.2),
                (7.8, 2.0),
                (7.2, 2.3),
                (6.8, 3.0),
                (6.6, 3.8),
                (6.6, 4.5)
            ],

             # Upper crescent
            [
                (3.8, 9.1),
                (4.5, 8.7),
                (5.4, 8.5),
                (6.2, 8.5),
                (7.0, 8.7),
                (7.2, 9.1)
            ],

            # Upper dot / diamond
            [
                (5.5, 10.5),
                (6.1, 9.95),
                (5.5, 9.4),
                (4.9, 9.95),
                (5.5, 10.5)
            ]
        ]

        self.stroke_index = 0
        self.point_index = 0

        # True when approaching a new stroke with pen off
        self.approaching_start = True

        # Service request state
        self.pen_request_pending = False

        # Controller settings
        self.kp_linear = 1.5
        self.kp_angular = 4.0

        self.distance_tolerance = 0.08
        self.angle_tolerance = 0.15

        self.max_linear_speed = 1.5
        self.max_angular_speed = 2.0

        # Disable pen initially
        self.set_pen(0, 0, 0, 2, 1)

        # Timer runs controller at 10 Hz
        self.timer = self.create_timer(
            0.1, self.move_in_aum
        )

    # ----------------------------------------
    # SetPen service
    # ----------------------------------------

    def set_pen(self, r, g, b, width, off):

        request = SetPen.Request()

        request.r = r
        request.g = g
        request.b = b
        request.width = width
        request.off = off

        future = self.setpen_client_.call_async(request)
        future.add_done_callback(self.callback_turtle_pen)

    def callback_turtle_pen(self, future):

        try:
            future.result()
            self.get_logger().info("Pen service completed")

        except Exception as e:
            self.get_logger().error(
                f"SetPen failed: {e}"
            )

    # ----------------------------------------
    # Pose subscriber
    # ----------------------------------------

    def callback_turtle_pose(self, msg):

        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

    # ----------------------------------------
    # Angle normalization
    # ----------------------------------------

    def normalize_angle(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    # ----------------------------------------
    # Controller
    # ----------------------------------------

    def move_in_aum(self):

        # Wait until first pose is received
        if self.x is None:
            return

        # Stop if all strokes are completed
        if self.stroke_index >= len(self.strokes):

            self.stop_turtle()
            self.get_logger().info("Aum drawing completed!")

            self.timer.cancel()
            return

        # Select current stroke
        stroke = self.strokes[self.stroke_index]

        # Select target waypoint
        if self.approaching_start:
            target_x, target_y = stroke[0]

        else:
            target_x, target_y = stroke[self.point_index]

        # Distance error
        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(dx**2 + dy**2)

        # Desired heading
        target_theta = math.atan2(dy, dx)

        # Angular error
        angle_error = self.normalize_angle(
            target_theta - self.theta
        )

        # --------------------------------
        # Waypoint reached
        # --------------------------------

        if distance < self.distance_tolerance:

            self.stop_turtle()

            # Reached the beginning of a stroke
            if self.approaching_start:

                self.approaching_start = False

                # Enable pen for drawing
                self.set_pen(
                    255, 219, 187, 3, 0
                )

                # First waypoint is already reached
                self.point_index = 1

                return

            # Reached final point of current stroke
            if self.point_index >= len(stroke) - 1:

                # Lift pen before moving to next stroke
                self.set_pen(0, 0, 0, 3, 1)

                self.stroke_index += 1

                self.point_index = 0
                self.approaching_start = True

                return

            # Select next waypoint
            self.point_index += 1

            return

        # --------------------------------
        # Calculate velocity
        # --------------------------------

        twist_msg = Twist()

        # Rotate first if heading error is large
        if abs(angle_error) > self.angle_tolerance:

            twist_msg.linear.x = 0.0

            twist_msg.angular.z = max(
                -self.max_angular_speed,
                min(
                    self.max_angular_speed,
                    self.kp_angular * angle_error
                )
            )

        else:

            twist_msg.angular.z = max(
                -self.max_angular_speed,
                min(
                    self.max_angular_speed,
                    self.kp_angular * angle_error
                )
            )

            twist_msg.linear.x = min(
                self.max_linear_speed,
                self.kp_linear * distance
            )

        # Publish command
        self.cmdvel_pub_.publish(twist_msg)
        #self.get_logger().info(f"here the point:{stroke[self.point_index]}" )



    # ----------------------------------------
    # Stop turtle
    # ----------------------------------------

    def stop_turtle(self):

        twist_msg = Twist()

        twist_msg.linear.x = 0.0
        twist_msg.angular.z = 0.0

        self.cmdvel_pub_.publish(twist_msg)


def main(args=None):

    rclpy.init(args=args)

    node = Draw_Aum_Node()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_turtle()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
