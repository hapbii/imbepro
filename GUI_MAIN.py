# main.py
import tkinter as tk
# 우리가 만든 hardware.py에서 SecurityHardware 클래스를 가져옵니다.
from hardware import SecurityHardware

# --- 설정 및 색상 정의 ---
WARNING_DISTANCE = 15.0    
POPUP_DISTANCE = 30.0      

BG_COLOR = "#0D1117"       
CARD_BG = "#161B22"        
TEXT_MAIN = "#C9D1D9"      
TEXT_MUTED = "#8B949E"     
COLOR_ACCENT = "#58A6FF"   
COLOR_WARN = "#FF7B72"     
COLOR_SUCCESS = "#7EE787"  
COLOR_TOUCH = "#D2A8FF"    

# 하드웨어 객체 생성
hw = SecurityHardware()

def draw_radar(distance):
    """캔버스에 부채꼴 레이더 그래픽을 그리는 함수"""
    canvas.delete("radar")
    cx, cy = 200, 220
    r = 180
    
    # 기본 레이더 그리드 배경
    canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=45, extent=90, fill="#1F242C", outline="#30363D", width=2, tags="radar")
    canvas.create_arc(cx-(r*0.6), cy-(r*0.6), cx+(r*0.6), cy+(r*0.6), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    canvas.create_arc(cx-(r*0.3), cy-(r*0.3), cx+(r*0.3), cy+(r*0.3), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    canvas.create_line(cx, cy, cx, cy-r, fill="#30363D", dash=(4, 4), tags="radar")
    
    # 물체 감지 시 시각화 스케일링 (100cm 기준)
    max_sensor_dist = 100.0
    if distance > max_sensor_dist:
        distance = max_sensor_dist
        
    if distance < max_sensor_dist:
        object_r = (distance / max_sensor_dist) * r
        wave_color = COLOR_WARN if distance <= WARNING_DISTANCE else COLOR_ACCENT
        
        canvas.create_arc(cx-object_r, cy-object_r, cx+object_r, cy+object_r, start=45, extent=90, fill="", outline=wave_color, width=5, style="arc", tags="radar")
        canvas.create_arc(cx-object_r, cy-object_r, cx+object_r, cy+object_r, start=45, extent=90, fill=wave_color, stipple="gray25", style="pieslice", tags="radar")

def monitor_sensors():
    """주기적으로 센서 값을 확인하고 화면을 갱신하는 코어 루프"""
    
    # 1. PIR 센서 감지 상태 확인
    if hw.get_pir_detected():
        pir_status_label.config(text="🟢 PIR 상태: 움직임 감지됨!!", fg=COLOR_SUCCESS)
        
        # 초음파 거리 획득
        distance_cm = hw.get_distance_cm()
        distance_label.config(text=f"{distance_cm:.1f} cm", fg="#FFFFFF")
        
        # 레이더 UI 업데이트
        draw_radar(distance_cm)
        
        # 30cm 이내 상단 팝업 조치
        if distance_cm <= POPUP_DISTANCE:
            root.attributes("-topmost", True)
            root.attributes("-topmost", False)
            root.lift()
        
        # 15cm 이하 최종 경고 및 처리
        if distance_cm <= WARNING_DISTANCE:
            warning_label.config(text="⚠️ 위험: 구역 내 접근 감지! ⚠️", fg=COLOR_WARN)
            distance_card.config(highlightbackground=COLOR_WARN, highlightcolor=COLOR_WARN)
        else:
            warning_label.config(text="🔵 안전: 물체 접근 중", fg=COLOR_ACCENT)
            distance_card.config(highlightbackground=COLOR_ACCENT, highlightcolor=COLOR_ACCENT)
            
        # 터치 센서 확인 및 서보모터 구동 제어
        if hw.is_touch_pressed():
            touch_sensor_label.config(text="🔮 터치 센서: 인증 성공 [모터 작동]", fg=COLOR_TOUCH)
            hw.activate_servo(root) # 모터 작동 함수 실행 (root 전달)
        else:
            touch_sensor_label.config(text="⚪ 터치 센서: 생체 인증 대기 중", fg=TEXT_MAIN)
            
    else:
        # PIR 센서 미감지 상태
        pir_status_label.config(text="⚫ PIR 상태: 주변 탐색 중...", fg=TEXT_MUTED)
        distance_label.config(text="-- cm", fg=TEXT_MUTED)
        warning_label.config(text="✅ 시스템 안전 보장됨", fg=TEXT_MUTED)
        distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
        
        draw_radar(999) # 레이더 공백 처리
        
        if hw.is_touch_pressed():
            touch_sensor_label.config(text="🔒 모터 거부 (PIR 감지 선행 필요)", fg=COLOR_WARN)
        else:
            touch_sensor_label.config(text="⚪ 터치 센서: 대기 중", fg=TEXT_MUTED)

    # 0.1초 반복 실행
    root.after(100, monitor_sensors)

# --- GUI 레이아웃 구성 ---
root = tk.Tk()
root.title("ADVANCED RADAR SECURITY SYSTEM")
root.geometry("600x850")
root.configure(bg=BG_COLOR) 

title_label = tk.Label(root, text="📡 RADAR MONITORING SYSTEM", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg="#FFFFFF")
title_label.pack(pady=30)

pir_status_label = tk.Label(root, text="⚫ PIR 상태: 주변 탐색 중...", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
pir_status_label.pack(pady=5)

canvas = tk.Canvas(root, width=400, height=260, bg=BG_COLOR, bd=0, relief="flat", highlightthickness=0)
canvas.pack(pady=10)
draw_radar(999) 

distance_card = tk.LabelFrame(root, text=" 🎯 TARGET DISTANCE ", font=("Arial", 10, "bold"), bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", highlightthickness=2, highlightbackground=CARD_BG)
distance_card.pack(pady=20, padx=60, fill="x")

distance_label = tk.Label(distance_card, text="-- cm", font=("Arial", 42, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
distance_label.pack(pady=20)

warning_label = tk.Label(root, text="✅ 시스템 안전 보장됨", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
warning_label.pack(pady=15)

touch_sensor_label = tk.Label(root, text="⚪ 터치 센서: 대기 중", font=("Arial", 13), bg=BG_COLOR, fg=TEXT_MUTED)
touch_sensor_label.pack(pady=15)

exit_button = tk.Button(root, text="❌ 시 스 템  종 료", font=("Arial", 13, "bold"), bg="#21262D", fg=COLOR_WARN, bd=0, relief="flat", activebackground=COLOR_WARN, activeforeground="#FFFFFF", cursor="hand2", command=root.destroy)
exit_button.pack(pady=30, ipady=12, ipadx=40)

# 초기 루프 구동
root.after(100, monitor_sensors)
root.mainloop()