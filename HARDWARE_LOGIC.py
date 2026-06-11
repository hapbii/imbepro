# hardware.py
from gpiozero import MotionSensor, DistanceSensor, Button, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device

class SecurityHardware:
    def __init__(self):
        # 서보모터 떨림 방지 설정
        try:
            Device.pin_factory = PiGPIOFactory()
        except:
            print("WARNING: pigpio 데몬이 켜지지 않았습니다. 'sudo pigpiod'를 입력하세요.")

        # 센서 및 모터 핀 설정
        self.pir = MotionSensor(18)
        self.ultrasonic = DistanceSensor(echo=24, trigger=23, max_distance=2.0)
        self.touch_sensor = Button(17, pull_up=False) 
        
        self.servo = AngularServo(25, min_angle=0, max_angle=180)
        self.servo.angle = 0
        
        self.is_motor_moving = False

    def get_pir_detected(self):
        """PIR 센서 감지 여부 반환"""
        return self.pir.motion_detected

    def get_distance_cm(self):
        """초음파 센서 실시간 거리(cm) 반환"""
        return self.ultrasonic.distance * 100

    def is_touch_pressed(self):
        """터치 센서 눌림 여부 반환"""
        return self.touch_sensor.is_pressed

    def activate_servo(self, root_tk):
        """서보모터를 60도로 회전시키고 2초 뒤 리셋 (GUI의 after 함수 활용)"""
        if not self.is_motor_moving:
            self.is_motor_moving = True
            self.servo.angle = 60
            # 2초(2000ms) 뒤에 reset_servo 호출
            root_tk.after(2000, self.reset_servo)

    def reset_servo(self):
        """서보모터를 원래 위치(0도)로 복귀"""
        self.servo.angle = 0
        self.is_motor_moving = False