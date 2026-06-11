import tkinter as tk
from gpiozero import MotionSensor, DistanceSensor, Button, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device
from time import sleep

# --- 서보모터 떨림 방지 및 부드러운 제어 설정 ---
try:
    Device.pin_factory = PiGPIOFactory()
except:
    print("pigpio 데몬이 켜지지 않았습니다. 'sudo pigpiod'를 터미널에 입력하면 모터가 더 안정적입니다.")

# --- 하드웨어 설정 ---
pir = MotionSensor(18)
ultrasonic = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# 터치 센서 (GPIO 17) - 기본 상태로 선언
touch_sensor = Button(17, pull_up=False) 

# 서보 모터 (GPIO 25)
servo = AngularServo(25, min_angle=0, max_angle=180)
servo.angle = 0 # 시작할 때 초기 각도는 0도

# --- 전역 변수 ---
WARNING_DISTANCE = 30.0 # 경고 기준 거리 (cm)


# --- 메인 감시 함수 ---
def monitor_sensors():
    
    # 1. PIR 센서 및 초음파 센서 로직
    if pir.motion_detected:
        pir_status_label.config(text="PIR 상태: 감지됨", fg="green")
        
        distance_cm = ultrasonic.distance * 100
        distance_label.config(text=f"현재 거리: {distance_cm:.1f} cm")
        
        if distance_cm <= WARNING_DISTANCE:
            warning_label.config(text="⚠️ 경고: 접근 감지! ⚠️", fg="red")
        else:
            warning_label.config(text="안전함", fg="blue")
    else:
        pir_status_label.config(text="PIR 상태: 대기 중", fg="black")
        distance_label.config(text="현재 거리: -- cm")
        warning_label.config(text="-", fg="black")

    # 2. 터치 센서 및 서보모터 로직 (정반대로 움직이던 부분 수정!)
    # 터치했을 때 '.is_pressed'가 True가 되는 기본 센서 기준입니다.
    if touch_sensor.is_pressed:
        touch_sensor_label.config(text="터치 센서: 인식됨", fg="orange")
        servo.angle = 60  # 터치하면 60도로 회전
    else:
        touch_sensor_label.config(text="터치 센서: 인식 안됨", fg="black")
        servo.angle = 0   # 터치 안 하면 0도로 대기

    # 0.1초마다 반복 실행
    root.after(100, monitor_sensors)


# --- GUI 창 설정 ---
root = tk.Tk()
root.title("센서 모니터링 시스템")
root.geometry("400x400")

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

# 종료 버튼 추가
exit_button = tk.Button(root, text="시스템 종료", font=("Arial", 12, "bold"), bg="red", fg="white", command=root.destroy)
exit_button.pack(pady=15)

# 루프 시작
root.after(100, monitor_sensors)
root.mainloop()