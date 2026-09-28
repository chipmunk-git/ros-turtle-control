import select
import sys
import termios
import tty

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from turtlesim.msg import Pose


class TurtleKeyboard(Node):

    def __init__(self):
        super().__init__('turtle_keyboard')

        # 거북이 이동 명령 Publisher 생성
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 거북이 위치 Subscriber 생성
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)

        # Reset 서비스 Client 생성
        self.client = self.create_client(Empty, '/reset')

        # 현재 거북이 위치
        self.current_pose = None

    def pose_callback(self, msg):
        self.current_pose = msg

    def move_turtle(self, linear_x, angular_z):
        msg = Twist()

        msg.linear.x = linear_x
        msg.angular.z = angular_z

        self.publisher_.publish(msg)

    def reset_turtle(self):
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Reset 서비스를 찾을 수 없습니다.')
            return

        request = Empty.Request()
        self.client.call_async(request)

    def print_pose(self):
        if self.current_pose is None:
            self.get_logger().info('현재 위치를 아직 수신하지 못했습니다.')
            return

        self.get_logger().info(
            'x: %.2f, y: %.2f, theta: %.2f'
            % (
                self.current_pose.x,
                self.current_pose.y,
                self.current_pose.theta
            )
        )

    def keyboard_input(self, key):
        if key == 'w':
            self.move_turtle(2.0, 0.0)

        elif key == 's':
            self.move_turtle(-2.0, 0.0)

        elif key == 'a':
            self.move_turtle(0.0, 2.0)

        elif key == 'd':
            self.move_turtle(0.0, -2.0)

        elif key == 'r':
            self.reset_turtle()

        elif key == 'p':
            self.print_pose()


def main(args=None):
    rclpy.init(args=args)

    turtle_keyboard = TurtleKeyboard()

    terminal_settings = termios.tcgetattr(sys.stdin)

    print('W: 전진 | S: 후진 | A: 왼쪽 회전 | D: 오른쪽 회전')
    print('R: Reset | P: 현재 위치 출력')
    print('종료: Ctrl+C')

    try:
        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():
            rclpy.spin_once(turtle_keyboard, timeout_sec=0.0)

            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).lower()
                turtle_keyboard.keyboard_input(key)

    except KeyboardInterrupt:
        pass

    finally:
        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            terminal_settings
        )

        turtle_keyboard.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
