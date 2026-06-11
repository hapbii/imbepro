import tkinter as tk
import math
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
WARNING_DISTANCE = 15.0    # 15cm 이하 최종 경고 및 모터 작동
POPUP_DISTANCE = 30.0      # 30cm 이하 최상단 팝업
is_motor_moving = False  

# 테마 색상 (Cyberpunk / SF 스타일 다크 테마)
BG_COLOR = "#0D1117"       # 매우 어두운 회색
CARD_BG = "#161B22"        # 카드 배경
TEXT_MAIN = "#C9D1D9"      # 기본 글자
TEXT_MUTED = "#8B949E"     # 대기 상태 글자
COLOR_ACCENT = "#58A6FF"   # 사이버 블루
COLOR_WARN = "#FF7B72"     # 경고 레드
COLOR_SUCCESS = "#7EE787"  # 성공 그린
COLOR_TOUCH = "#D2A8FF"    # 터치 퍼플

def reset_servo():
    global is_motor_moving
    servo.angle = 0
    is_motor_moving = False 

def draw_radar(distance):
    """ 캔버스에 부채꼴 레이더 그래픽을 실시간으로 그리는 함수 """
    canvas.delete("radar") # 이전 그래픽 삭제
    
    # 중심점 및 반지름 설정
    cx, cy = 200, 220
    r = 180
    
    # 1. 기본 부채꼴 배경 가이드라인 (외곽선 및 격자선)
    canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=45, extent=90, fill="#1F242C", outline="#30363D", width=2, tags="radar")
    canvas.create_arc(cx-(r*0.6), cy-(r*0.6), cx+(r*0.6), cy+(r*0.6), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    canvas.create_arc(cx-(r*0.3), cy-(r*0.3), cx+(r*0.3), cy+(r*0.3), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    
    # 센터선(초음파 중심 라인)
    canvas.create_line(cx, cy, cx, cy-r, fill="#30363D", dash=(4, 4), tags="radar")
    
    # 2. 실시간 거리 데이터 시각화
    # 초음파 센서의 최대 거리를 200cm(2.0m)로 가정하고 픽셀 매핑
    max_sensor_dist = 100.0 # 시각적으로 잘 보이게 100cm 기준으로 스케일링
    if distance > max_sensor_dist:
        distance = max_sensor_dist
        
    # 거리가 가까울수록 채워지는 부채꼴 반지름 계산 (역산하여 가까울수록 꽉 차게 표현하거나, 실제 거리 비율 매핑)
    # 여기서는 직관적으로 물체 위치를 나타내는 붉은색 파동(호)으로 표현
    if distance < max_sensor_dist:
        # 실제 거리에 따른 픽셀 반지름
        object_r = (distance / max_sensor_dist) * r
        # 거리에 따라 색상 변경 (경고 거리 이내면 빨간색, 안전하면 파란색/초록색)
        wave_color = COLOR_WARN if distance <= WARNING_DISTANCE else COLOR_ACCENT
        
        # 물체가 있는 위치에 호 그리기
        canvas.create_arc(cx-object_r, cy-object_r, cx+object_r, cy+object_r, start=45, extent=90, fill="", outline=wave_color, width=5, style="arc", tags="radar")
        # 물체 지점 음영 채우기
        canvas.create_arc(cx-object_r, cy-object_r, cx+object_r, cy+object_r, start=45, extent=90, fill=wave_color, stipple="gray25", style="pieslice", tags="radar")

def monitor_sensors():
    global is_motor_moving
    
    # 1. PIR & 초음파 센서 영역
    if pir.motion_detected:
        pir_status_label.config(text="🟢 PIR 상태: 움직임 감지됨!!", fg=COLOR_SUCCESS)
        
        distance_cm = ultrasonic.distance * 100
        distance_label.config(text=f"{distance_cm:.1f} cm", fg="#FFFFFF")
        
        # 레이더 그래픽 업데이트
        draw_radar(distance_cm)
        
        # 30cm 이내 최상단 팝업 트리거
        if distance_cm <= POPUP_DISTANCE:
            root.attributes("-topmost", True)
            root.attributes("-topmost", False)
            root.lift()
        
        # 15cm 이하 최종 경고 조건문
        if distance_cm <= WARNING_DISTANCE:
            warning_label.config(text="🚨 경고: 위험 구역 침입 감지! 🚨", fg=COLOR_WARN)
            distance_card.config(highlightbackground=COLOR_WARN, highlightcolor=COLOR_WARN)
        else:
            warning_label.config(text="🔵 안전: 물체 접근 중", fg=COLOR_ACCENT)
            distance_card.config(highlightbackground=COLOR_ACCENT, highlightcolor=COLOR_ACCENT)
            
        # PIR 감지 시에만 터치 센서 및 모터 작동 (15cm 이하 조건)
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="🔮 터치 센서: 인증 성공 [모터 작동]", fg=COLOR_TOUCH)
            if not is_motor_moving:
                is_motor_moving = True
                servo.angle = 60
                root.after(2000, reset_servo)
        else:
            touch_sensor_label.config(text="⚪ 터치 센서: 생체 인증 대기 중", fg=TEXT_MAIN)
            
    else:
        # PIR 미감지 시
        pir_status_label.config(text="⚫ PIR 상태: 주변 탐색 중...", fg=TEXT_MUTED)
        distance_label.config(text="-- cm", fg=TEXT_MUTED)
        warning_label.config(text="✅ 시스템 안전 보장됨", fg=TEXT_MUTED)
        distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
        
        # PIR 미감지 시 레이더도 공백 스캔 상태로 표현
        draw_radar(999) 
        
        if touch_sensor.is_pressed:
            touch_sensor_label.config(text="🔒 모터 거부 (PIR 감지 선행 필요)", fg=COLOR_WARN)
        else:
            touch_sensor_label.config(text="⚪ 터치 센서: 대기 중", fg=TEXT_MUTED)

    root.after(100, monitor_sensors)

# --- GUI 레이아웃 구성 ---
root = tk.Tk()
root.title("ADVANCED RADAR SECURITY SYSTEM")
root.geometry("600x850") # 레이더가 들어가서 세로를 조금 더 늘렸습니다.
root.configure(bg=BG_COLOR) 

# 1. 상단 제목
title_label = tk.Label(root, text="📡 RADAR MONITORING SYSTEM", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg="#FFFFFF")
title_label.pack(pady=30)

# 2. PIR 상태 표시줄 (아이콘 스타일화)
pir_status_label = tk.Label(root, text="⚫ PIR 상태: 주변 탐색 중...", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
pir_status_label.pack(pady=5)

# 3. [신규 추가] 부채꼴 레이더 화면을 그릴 캔버스 영역
canvas = tk.Canvas(root, width=400, height=260, bg=BG_COLOR, bd=0, relief="flat", highlightthickness=0)
canvas.pack(pady=10)
draw_radar(999) # 초기 빈 레이더 그리기

# 4. 거리 표시 대형 카드
distance_card = tk.LabelFrame(root, text=" 🎯 TARGET DISTANCE ", font=("Arial", 10, "bold"), bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", highlightthickness=2, highlightbackground=CARD_BG)
distance_card.pack(pady=20, padx=60, fill="x")

distance_label = tk.Label(distance_card, text="-- cm", font=("Arial", 42, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
distance_label.pack(pady=20)

# 5. 경고 메시지 표시줄
warning_label = tk.Label(root, text="✅ 시스템 안전 보장됨", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
warning_label.pack(pady=15)

# 6. 터치 센서 상태 표시줄
touch_sensor_label = tk.Label(root, text="⚪ 터치 센서: 대기 중", font=("Arial", 13), bg=BG_COLOR, fg=TEXT_MUTED)
touch_sensor_label.pack(pady=15)

# 7. 하단 종료 버튼
exit_button = tk.Button(root, text="❌ 시 스 템  종 료", font=("Arial", 13, "bold"), bg="#21262D", fg=COLOR_WARN, bd=0, relief="flat", activebackground=COLOR_WARN, activeforeground="#FFFFFF", cursor="hand2", command=root.destroy)
exit_button.pack(pady=30, ipady=12, ipadx=40)

root.after(100, monitor_sensors)
root.mainloop()