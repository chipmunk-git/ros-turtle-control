# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist


class TurtlePublisher(Node):

    def __init__(self):
        super().__init__('turtle_publisher')

        # 거북이 이동 명령 Publisher 생성
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()

        # 거북이 이동
        msg.linear.x = 2.0
        msg.angular.z = 2.0

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    turtle_publisher = TurtlePublisher()

    rclpy.spin(turtle_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    turtle_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
