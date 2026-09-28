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

from turtlesim.msg import Pose


class TurtleSubscriber(Node):

    def __init__(self):
        super().__init__('turtle_subscriber')

        # 거북이 위치 Subscriber 생성
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(
            'x: %.2f, y: %.2f, theta: %.2f'
            % (msg.x, msg.y, msg.theta)
        )


def main(args=None):
    rclpy.init(args=args)

    turtle_subscriber = TurtleSubscriber()

    rclpy.spin(turtle_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    turtle_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
