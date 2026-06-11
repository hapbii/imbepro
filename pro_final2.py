import tkinter as tk
from gpiozero import MotionSensor, DistanceSensor, Button, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device

# --- 서보모터 설정 ---
try:
    Device.pin_factory = PiGPIOFactory()
except:
    print("pigpio 데몬 확인 필요!")

# --- 하드웨어 설정 ---
pir = MotionSensor(18)
ultrasonic = DistanceSensor(echo=24, trigger=23, max_distance=2.0)
touch_sensor = Button(17, pull_up=False) 
servo = AngularServo(25, min_angle=0, max_angle=180)
servo.angle = 0

# --- 상태 및 디자인 색상 정의 ---
WARNING_DISTANCE = 15.0    # 15cm 이하일 때 최종 경고 및 모터 작동 가능
POPUP_DISTANCE = 30.0      # 30cm 이하로 들어오면 창을 맨 앞으로 올림
is_motor_moving = False  

BG_COLOR = "#1A1B26"       
CARD_BG = "#24283B"        
TEXT_MAIN = "#A9B1D6"      
TEXT_MUTED = "#565F89"     
COLOR_ACCENT = "#7AA2F7"   
COLOR_WARN = "#F7768E"     
COLOR_SUCCESS = "#9ECE6A"  
COLOR_TOUCH = "#E0AF68"    

def reset_servo():
    global is_motor_moving
    servo.angle = 0
    is_motor_moving = False 

def monitor_sensors():
    global is_motor_moving
    
    # 1. PIR & 초음파 센서 영역
    if pir.motion_detected:
        pir_status_label.config(text="● PIR 센서: 움직임 감지됨", fg=COLOR_SUCCESS)
        
        distance_cm = ultrasonic.distance * 100
        distance_label.config(text=f"{distance_cm:.1f} cm", fg="#FFFFFF")
        
        # [새로운 기능] 30cm 이내로 들어오면 창을 화면 맨 위로 강제 팝업
        if distance_cm <= POPUP_DISTANCE:
            root.attributes("-topmost", True)   # 최상단 고정 활성화
            root.attributes("-topmost", False)  # 연속 팝업을 위해 즉시 해제 (창은 앞에 유지됨)
            root.lift()                         # 창을 레이어 맨 위로 올림
        
        # 15cm 이하 최종 경고 조건문
        if distance_cm <= WARNING_DISTANCE:
            warning_label.config(text="⚠️ 위험: 구역 내 접근 감지! ⚠️", fg=COLOR_WARN)
            distance_card.config(highlightbackground=COLOR_WARN, highlightcolor=COLOR_WARN)
        else:
            warning_label.config(text="안전함 (접근 물체 없음)", fg=COLOR_ACCENT)
            distance_card.config(highlightbackground=COLOR_ACCENT, highlightcolor=COLOR_ACCENT)
            
        # PIR 감지 시에만 터치 센서 및 모터 작동 (15cm 이하 조건)
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="● 터치 센서: 입력 확인 (모터 구동)", fg=COLOR_TOUCH)
            if not is_motor_moving:
                is_motor_moving = True
                servo.angle = 60
                root.after(2000, reset_servo)
        else:
            touch_sensor_label.config(text="○ 터치 센서: 대기 중", fg=TEXT_MAIN)
            
    else:
        # PIR 미감지 시
        pir_status_label.config(text="○ PIR 센서: 감시 모드 작동 중", fg=TEXT_MUTED)
        distance_label.config(text="-- cm", fg=TEXT_MUTED)
        warning_label.config(text="안전 상태 유지 중", fg=TEXT_MUTED)
        distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
        
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="🔒 모터 잠금 (PIR 감지가 필요합니다)", fg=COLOR_WARN)
        else:
            touch_sensor_label.config(text="○ 터치 센서: 대기 중", fg=TEXT_MUTED)

    root.after(100, monitor_sensors)

# --- GUI 레이아웃 구성 ---
root = tk.Tk()
root.title("보안 제어 시스템")
root.geometry("600x700")
root.configure(bg=BG_COLOR) 

# 1. 상단 제목
title_label = tk.Label(root, text="SECURITY SYSTEM", font=("Helvetica", 24, "bold"), bg=BG_COLOR, fg="#FFFFFF")
title_label.pack(pady=40)

# 2. PIR 상태 표시줄
pir_status_label = tk.Label(root, text="○ PIR 센서: 감시 모드 작동 중", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
pir_status_label.pack(pady=10)

# 3. 거리 표시 대형 카드
distance_card = tk.LabelFrame(root, text=" 실시간 거리 측정 ", font=("Arial", 12), bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", highlightthickness=3, highlightbackground=CARD_BG)
distance_card.pack(pady=30, padx=60, fill="x")

distance_label = tk.Label(distance_card, text="-- cm", font=("Arial", 48, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
distance_label.pack(pady=30)

# 4. 경고 메시지 표시줄
warning_label = tk.Label(root, text="안전 상태 유지 중", font=("Arial", 18, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
warning_label.pack(pady=20)

# 5. 터치 센서 상태 표시줄
touch_sensor_label = tk.Label(root, text="○ 터치 센서: 대기 중", font=("Arial", 14), bg=BG_COLOR, fg=TEXT_MUTED)
touch_sensor_label.pack(pady=20)

# 6. 하단 종료 버튼
exit_button = tk.Button(root, text="시 스 템  종 료", font=("Arial", 14, "bold"), bg="#2F3446", fg=COLOR_WARN, bd=0, relief="flat", activebackground=COLOR_WARN, activeforeground="#FFFFFF", cursor="hand2", command=root.destroy)
exit_button.pack(pady=40, ipady=12, ipadx=40)

root.after(100, monitor_sensors)
root.mainloop()