import rclpy
from rclpy.node import Node

from std_srvs.srv import Empty


class TurtleReset(Node):

    def __init__(self):
        super().__init__('turtle_reset')

        # Reset 서비스 Client 생성
        self.client = self.create_client(Empty, '/reset')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Reset 서비스를 기다리는 중...')

    def reset_turtle(self):
        request = Empty.Request()

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)


def main(args=None):
    rclpy.init(args=args)

    turtle_reset = TurtleReset()
    turtle_reset.reset_turtle()

    turtle_reset.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
