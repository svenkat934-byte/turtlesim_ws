#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
from turtlesim.msg import Pose
from turtlesim.srv import SetPen
from geometry_msgs.msg import Twist
import math
from random import randint
    
    
class TurtleControllerFollowerNode(Node): 
    def __init__(self):
        super().__init__("turtle_controller_follower_node") 
        # passing default values of x and y for turtle spawn
        self.declare_parameter("x_posn", 3.0)
        self.declare_parameter("y_posn", 3.0)
        self.declare_parameter("theta", 0.95 )
        self.declare_parameter("name", "turtle2")
        # if user wants to pass parameters of x and y values 
        self.x_posn = self.get_parameter("x_posn").value
        self.y_posn = self.get_parameter("y_posn").value
        self.theta = self.get_parameter("theta").value
        self.name = self.get_parameter("name").value
        # creating turtle spawn
        self.turtleSpawner(self.x_posn, self.y_posn, self.theta, self.name )

        # creating subcription for main turtle
        self.pose_sub_main_ = self.create_subscription(Pose, "turtle1/pose", self.callback_pose, 10)

        # creating publisher and subscription for turtle that spawned
        self.pose_pub_turtle_ = self.create_publisher(Twist, f"{self.name}/cmd_vel", 10)
        self.pose_sub_turtle_ = self.create_subscription(Pose, f"{self.name}/pose", self.callback_turtle_pose, 10)

        # storing position of turtle1
        self.current_posn_turtle1 = []
        # storing turtle spawn position
        self.current_posn_spawnturtle = []

        self.setpen_client_ = self.create_client(SetPen, f"{self.name}/set_pen")
        while not self.setpen_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Turtlesim_Node_SetPen ......")
        

    # creating turtle spwaner method
    def turtleSpawner(self, x_pos , y_pos, theta, name):
        # creating a client for spawn turtle
        self.spawn_client_ =  self.create_client(Spawn, "spawn")
        # checking server is available or not
        while not self.spawn_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Turtlesim_Node_Spawn .....")

        request = Spawn.Request()
        request.x = x_pos
        request.y = y_pos
        request.theta = theta
        request.name = name

        future = self.spawn_client_.call_async(request)
        future.add_done_callback(self.callback_turtleSpawner)

    def callback_turtleSpawner(self, future):
        respone = future.result()
        self.get_logger().info(f"Successfully Spawned:= {respone.name}")
        


    # creating method for main turtle pose
    def callback_pose(self, msg):
        current_x = msg.x
        current_y = msg.y
        current_theta = msg.theta
        current_Lin_Vel = msg.linear_velocity
        current_Ang_Vel = msg.angular_velocity

        self.current_posn_turtle1 = [current_x, current_y, current_theta, current_Lin_Vel, current_Ang_Vel]



    # creating method for Spawn turtle pose
    def callback_turtle_pose(self, msg):
        current_x = msg.x
        current_y = msg.y
        current_theta = msg.theta
        current_Lin_Vel = msg.linear_velocity
        current_Ang_Vel = msg.angular_velocity

        self.current_posn_spawnturtle = [current_x, current_y, current_theta, current_Lin_Vel, current_Ang_Vel]
        

        self.move_spawnturtle_with_main_turtle()


    # move spawn turtle
    def move_spawnturtle_with_main_turtle(self):
        # proptoinal value of linear and angular
        kp_linear = 2.0
        kp_angular = 6.0

        target_x = self.current_posn_turtle1[0]
        target_y = self.current_posn_turtle1[1]

        current_x = self.current_posn_spawnturtle[0]
        current_y = self.current_posn_spawnturtle[1]
        current_theta = self.current_posn_spawnturtle[2]

        # calculating Euclidean  distance between two coordinates
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx**2 + dy**2)

        # caluating Angle 
        angle_to_target = math.atan2(dy, dx)

        # Angular control rotate towards target point
        angular_error = angle_to_target - current_theta
        if(angular_error > math.pi):
            angular_error -= 2*math.pi
        elif(angular_error < -math.pi):
            angular_error += 2*math.pi


        angular_velocity = kp_angular * angular_error

        linear_velocity = kp_linear * distance

        # Publishing the velocites
        twist_msg = Twist()
        twist_msg.linear.x = linear_velocity
        twist_msg.angular.z = angular_velocity
        self.pose_pub_turtle_.publish(twist_msg)
        self.randomclor()
       

        # Stop the turtle when it's close enough to target
        if distance < 1.0:
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.pose_pub_turtle_.publish(twist_msg)
            #self.get_logger().info("Target reached!")
        
    def randomclor(self):
           red = randint(0, 255)
           blue = randint(0, 255)
           green = randint(0, 255)
           width = 4
           self.set_color_spwan_turtle(red, blue, green, width)

        

    def set_color_spwan_turtle(self, r, b, g, width):
       
      

        request = SetPen.Request()
        request.r = r
        request.b = b
        request.g = g
        request.width = width
        request.off = 0

        future = self.setpen_client_.call_async(request)
        future.add_done_callback(self.callback_turtle_pen)

    def callback_turtle_pen(self, future):
        respone = future.result()
        #self.get_logger().info(f"Successfully color SetPen done ")
        
    

def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerFollowerNode() 
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
    
if __name__ == "__main__":
    main()