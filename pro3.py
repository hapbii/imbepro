import tkinter as tk
from gpiozero import MotionSensor, DistanceSensor, Button, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device

# --- 서보모터 떨림 방지 설정 ---
try:
    Device.pin_factory = PiGPIOFactory()
except:
    print("pigpio 데몬이 켜지지 않았습니다. 'sudo pigpiod'를 필수 입력해주세요!")

# --- 하드웨어 설정 ---
pir = MotionSensor(18)
ultrasonic = DistanceSensor(echo=24, trigger=23, max_distance=2.0)
touch_sensor = Button(17, pull_up=False) 

# 서보 모터 설정 (초기 위치 0도)
servo = AngularServo(25, min_angle=0, max_angle=180)
servo.angle = 0

# --- 상태 관리 변수 ---
WARNING_DISTANCE = 30.0 
is_motor_moving = False  # 모터가 이미 동작 중인지 체크하는 플래그


# --- 서보모터 동작 제어 함수 ---
def reset_servo():
    """ 2초 후에 서보모터를 다시 0도로 돌려놓는 함수 """
    global is_motor_moving
    servo.angle = 0
    is_motor_moving = False # 모터 동작 완료 상태로 변경


# --- 메인 감시 함수 ---
def monitor_sensors():
    global is_motor_moving
    
    # 1. PIR 센서 감지 여부 확인
    if pir.motion_detected:
        pir_status_label.config(text="PIR 상태: 감지됨", fg="green")
        
        # 초음파 센서 거리 측정
        distance_cm = ultrasonic.distance * 100
        distance_label.config(text=f"현재 거리: {distance_cm:.1f} cm")
        
        if distance_cm <= WARNING_DISTANCE:
            warning_label.config(text="⚠️ 경고: 접근 감지! ⚠️", fg="red")
        else:
            warning_label.config(text="안전함", fg="blue")
            
        # [조건 추가] PIR이 감지된 상태에서만 터치 센서 작동 조건 검사
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="터치 센서: 인식됨", fg="orange")
            
            # 모터가 현재 움직이는 중이 아닐 때만 처음 한 번 실행
            if not is_motor_moving:
                is_motor_moving = True
                servo.angle = 60 # 60도로 회전
                # 2000ms(2초) 후에 reset_servo 함수를 호출해 0도로 복귀
                root.after(2000, reset_servo)
        else:
            touch_sensor_label.config(text="터치 센서: 인식 안됨", fg="black")
            
    else:
        # PIR 센서에 아무것도 감지되지 않은 경우
        pir_status_label.config(text="PIR 상태: 대기 중", fg="black")
        distance_label.config(text="현재 거리: -- cm")
        warning_label.config(text="-", fg="black")
        
        # PIR이 미감지 상태면 터치 센서 가독성 업데이트만 하고 모터는 절대 안 움직임
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="터치 센서: 인식됨 (PIR 대기중으로 모터 작동 제한)", fg="red")
        else:
            touch_sensor_label.config(text="터치 센서: 인식 안됨", fg="black")

    # 0.1초마다 반복 실행
    root.after(100, monitor_sensors)


# --- GUI 창 설정 ---
root = tk.Tk()
root.title("센서 모니터링 시스템")
root.geometry("450x400")

title_label = tk.Label(root, text="🚨 실시간 보안 시스템 🚨", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

pir_status_label = tk.Label(root, text="PIR 상태: 대기 중", font=("Arial", 12))
pir_status_label.pack(pady=10)

distance_label = tk.Label(root, text="현재 거리: -- cm", font=("Arial", 12))
distance_label.pack(pady=10)

warning_label = tk.Label(root, text="-", font=("Arial", 14, "bold"))
warning_label.pack(pady=10)

touch_sensor_label = tk.Label(root, text="터치 센서: 인식 안됨", font=("Arial", 12))
touch_sensor_label.pack(pady=10)

exit_button = tk.Button(root, text="시스템 종료", font=("Arial", 12, "bold"), bg="red", fg="white", command=root.destroy)
exit_button.pack(pady=15)

# 루프 시작
root.after(100, monitor_sensors)
root.mainloop()