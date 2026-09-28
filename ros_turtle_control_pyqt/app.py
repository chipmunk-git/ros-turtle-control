import signal
import sys

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_srvs.srv import Empty
from turtlesim.msg import Pose

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton

from db_helper import DB, DB_CONFIG


class TurtleControl(Node):

    def __init__(self):
        super().__init__('turtle_pyqt')

        # 거북이 이동 명령 Publisher 생성
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 거북이 위치 Subscriber 생성
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Reset 서비스 Client 생성
        self.client = self.create_client(
            Empty,
            '/reset'
        )

        # 현재 거북이 위치
        self.current_pose = None

        # 데이터베이스 객체 생성
        self.db = DB(**DB_CONFIG)

    def pose_callback(self, msg):
        self.current_pose = msg

    def move_turtle(self, linear_x, angular_z):
        msg = Twist()

        msg.linear.x = linear_x
        msg.angular.z = angular_z

        self.publisher_.publish(msg)

    def stop_turtle(self):
        self.move_turtle(0.0, 0.0)

    def reset_turtle(self):
        if not self.client.service_is_ready():
            self.get_logger().info('Reset 서비스를 찾을 수 없습니다.')
            return

        request = Empty.Request()
        self.client.call_async(request)

    def save_pose(self):
        if self.current_pose is None:
            self.get_logger().info('현재 위치를 아직 수신하지 못했습니다.')
            return

        x = self.current_pose.x
        y = self.current_pose.y
        theta = self.current_pose.theta

        if self.db.insert_pose(x, y, theta):
            self.get_logger().info(
                '저장 완료 - x: %.2f, y: %.2f, theta: %.2f'
                % (x, y, theta)
            )

        else:
            self.get_logger().info('데이터베이스 저장 실패')


class Window(QWidget):

    def __init__(self, turtle_control):
        super().__init__()

        self.turtle_control = turtle_control

        self.setWindowTitle('Turtle Control')
        self.resize(300, 250)

        layout = QGridLayout()

        # 방향 버튼
        self.btn_up = QPushButton('↑')
        self.btn_down = QPushButton('↓')
        self.btn_left = QPushButton('←')
        self.btn_right = QPushButton('→')

        # 기능 버튼
        self.btn_reset = QPushButton('Reset')
        self.btn_save = QPushButton('Save Position')

        # 버튼 배치
        layout.addWidget(self.btn_up, 0, 1)
        layout.addWidget(self.btn_left, 1, 0)
        layout.addWidget(self.btn_right, 1, 2)
        layout.addWidget(self.btn_down, 2, 1)
        layout.addWidget(self.btn_reset, 3, 0)
        layout.addWidget(self.btn_save, 3, 1, 1, 2)

        self.setLayout(layout)

        # 마우스 입력 상태
        self.mouse_state = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False
        }

        # 키보드 입력 상태
        self.keyboard_state = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False
        }

        # 버튼이 키보드 포커스를 가져가지 않도록 설정
        self.btn_up.setFocusPolicy(Qt.NoFocus)
        self.btn_down.setFocusPolicy(Qt.NoFocus)
        self.btn_left.setFocusPolicy(Qt.NoFocus)
        self.btn_right.setFocusPolicy(Qt.NoFocus)
        self.btn_reset.setFocusPolicy(Qt.NoFocus)
        self.btn_save.setFocusPolicy(Qt.NoFocus)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # 방향 버튼 입력
        self.btn_up.pressed.connect(
            lambda: self.set_mouse_state('forward', True)
        )
        self.btn_up.released.connect(
            lambda: self.set_mouse_state('forward', False)
        )

        self.btn_down.pressed.connect(
            lambda: self.set_mouse_state('backward', True)
        )
        self.btn_down.released.connect(
            lambda: self.set_mouse_state('backward', False)
        )

        self.btn_left.pressed.connect(
            lambda: self.set_mouse_state('left', True)
        )
        self.btn_left.released.connect(
            lambda: self.set_mouse_state('left', False)
        )

        self.btn_right.pressed.connect(
            lambda: self.set_mouse_state('right', True)
        )
        self.btn_right.released.connect(
            lambda: self.set_mouse_state('right', False)
        )

        # Reset 및 현재 위치 저장
        self.btn_reset.clicked.connect(
            self.turtle_control.reset_turtle
        )
        self.btn_save.clicked.connect(
            self.turtle_control.save_pose
        )

        # 누르고 있는 동안 이동 명령 반복 전송
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.publish_move)

        # ROS2 callback 처리
        self.ros_timer = QTimer()
        self.ros_timer.timeout.connect(self.spin_ros)
        self.ros_timer.start(10)

    def set_mouse_state(self, direction, state):
        self.mouse_state[direction] = state
        self.update_move()

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        if event.key() == Qt.Key_W:
            self.keyboard_state['forward'] = True

        elif event.key() == Qt.Key_S:
            self.keyboard_state['backward'] = True

        elif event.key() == Qt.Key_A:
            self.keyboard_state['left'] = True

        elif event.key() == Qt.Key_D:
            self.keyboard_state['right'] = True

        elif event.key() == Qt.Key_R:
            self.turtle_control.reset_turtle()
            return

        elif event.key() == Qt.Key_P:
            self.turtle_control.save_pose()
            return

        else:
            return

        self.update_move()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        if event.key() == Qt.Key_W:
            self.keyboard_state['forward'] = False

        elif event.key() == Qt.Key_S:
            self.keyboard_state['backward'] = False

        elif event.key() == Qt.Key_A:
            self.keyboard_state['left'] = False

        elif event.key() == Qt.Key_D:
            self.keyboard_state['right'] = False

        else:
            return

        self.update_move()

    def update_move(self):
        self.publish_move()

        linear_x, angular_z = self.get_velocity()

        if linear_x != 0.0 or angular_z != 0.0:
            if not self.move_timer.isActive():
                self.move_timer.start(50)

        else:
            self.move_timer.stop()

    def get_velocity(self):
        forward = (
            int(self.mouse_state['forward'])
            + int(self.keyboard_state['forward'])
        )

        backward = (
            int(self.mouse_state['backward'])
            + int(self.keyboard_state['backward'])
        )

        left = (
            int(self.mouse_state['left'])
            + int(self.keyboard_state['left'])
        )

        right = (
            int(self.mouse_state['right'])
            + int(self.keyboard_state['right'])
        )

        linear_x = 2.0 * (forward - backward)
        angular_z = 2.0 * (left - right)

        return linear_x, angular_z

    def publish_move(self):
        linear_x, angular_z = self.get_velocity()

        self.turtle_control.move_turtle(
            linear_x,
            angular_z
        )

    def spin_ros(self):
        rclpy.spin_once(
            self.turtle_control,
            timeout_sec=0.0
        )


if __name__ == '__main__':
    rclpy.init()

    print('W: 전진 | S: 후진 | A: 왼쪽 회전 | D: 오른쪽 회전')
    print('R: Reset | P: 현재 위치 저장')
    print('마우스와 키보드 같은 방향 동시 입력: 속도 2배')
    print('종료: Ctrl+C')

    app = QApplication(sys.argv)

    turtle_control = TurtleControl()

    window = Window(turtle_control)
    window.show()

    # Ctrl+C로 정상 종료
    signal.signal(
        signal.SIGINT,
        lambda sig, frame: app.quit()
    )

    result = app.exec_()

    # 종료 전 거북이 정지
    turtle_control.stop_turtle()

    turtle_control.destroy_node()
    rclpy.shutdown()

    sys.exit(result)
