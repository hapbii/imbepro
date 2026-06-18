# main.py
import tkinter as tk
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

# 하드웨어 및 시스템 상태 제어 변수
hw = SecurityHardware()
is_system_on = False  
is_popup_open = False    # 경고 창이 화면에 이미 열려 있는지 확인하는 플래그
is_alert_muted = False   # [신규] 사용자가 해제를 눌러 경고를 임시 무시(뮤트)했는지 여부

def toggle_system():
    """시스템 전체를 ON/OFF 토글하는 함수"""
    global is_system_on, is_alert_muted
    if not is_system_on:
        is_system_on = True
        toggle_btn.config(text="⚙️ SYSTEM: ACTIVE (ON)", bg=COLOR_SUCCESS, fg="#0D1117")
    else:
        is_system_on = False
        is_alert_muted = False # 시스템 끌 때 뮤트도 초기화
        toggle_btn.config(text="🔒 SYSTEM: DISABLED (OFF)", bg="#21262D", fg=TEXT_MUTED)
        pir_status_label.config(text="❌ 시스템이 꺼져 있습니다.", fg=TEXT_MUTED)
        distance_label.config(text="-- cm", fg=TEXT_MUTED)
        warning_label.config(text="STANDBY", fg=TEXT_MUTED)
        touch_sensor_label.config(text="⚪ 장치 비활성화 상태", fg=TEXT_MUTED)
        distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
        draw_radar(999)
        hw.reset_servo()

def open_warning_popup():
    """30cm 이내 접근 시 새로운 경고 창을 띄우는 함수"""
    global is_popup_open, is_alert_muted
    
    # 이미 창이 열려 있거나, 사용자가 이미 '해제'를 눌렀다면 창을 열지 않음
    if is_popup_open or is_alert_muted: 
        return  
        
    is_popup_open = True
    
    # 새로운 서브 창(Toplevel) 생성
    popup = tk.Toplevel(root)
    popup.title("⚠️ 보안 경고")
    popup.geometry("350x200")
    popup.configure(bg=CARD_BG)
    
    popup.transient(root)
    popup.attributes("-topmost", True)
    
    # 사용자가 우측 상단 X 버튼으로 창을 닫았을 때 처리 (해제 안 함과 동일 취급)
    def on_close_by_x():
        global is_popup_open
        is_popup_open = False
        popup.grab_release()
        popup.destroy()
        
    popup.protocol("WM_DELETE_WINDOW", on_close_by_x)

    # [해제] 버튼을 눌렀을 때 실행되는 함수
    def on_click_clear():
        global is_popup_open, is_alert_muted
        is_alert_muted = True  # 🔥 거리가 30cm 바깥으로 나갈 때까지 경고창 무한 생성 방지!
        is_popup_open = False
        popup.grab_release()
        popup.destroy()

    # [해제 안함] 버튼을 눌렀을 때 실행되는 함수
    def on_click_keep():
        global is_popup_open
        is_popup_open = False # 뮤트(is_alert_muted)하지 않으므로 다음 루프(0.1초 뒤)에 다시 창이 뜸
        popup.grab_release()
        popup.destroy()

    # 경고 문구 레이블
    lbl = tk.Label(popup, text="🚨 경고: 물체가 30cm 이내로\n접근했습니다!\n\n경고를 해제하시겠습니까?", 
                   font=("Arial", 12, "bold"), bg=CARD_BG, fg=TEXT_MAIN, justify="center")
    lbl.pack(pady=20)
    
    # 버튼 프레임
    btn_frame = tk.Frame(popup, bg=CARD_BG)
    btn_frame.pack(pady=10)
    
    # [해제] 버튼 -> 클릭 시 창이 꺼지고 무한 생성 멈춤
    btn_clear = tk.Button(btn_frame, text="해제", font=("Arial", 11, "bold"), bg=COLOR_SUCCESS, fg="#0D1117",
                          bd=0, relief="flat", width=10, command=on_click_clear)
    btn_clear.pack(side="left", padx=15, ipady=5)
    
    # [해제 안함] 버튼 -> 클릭 시 창은 닫히지만 잠시 후 다시 생성됨
    btn_keep = tk.Button(btn_frame, text="해제 안함", font=("Arial", 11, "bold"), bg=COLOR_WARN, fg="#FFFFFF",
                         bd=0, relief="flat", width=10, command=on_click_keep)
    btn_keep.pack(side="right", padx=15, ipady=5)

    popup.update()
    popup.grab_set()


def draw_radar(distance):
    """캔버스에 부채꼴 레이더 그래픽을 그리는 함수"""
    canvas.delete("radar")
    cx, cy = 200, 220
    r = 180
    
    canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=45, extent=90, fill="#1F242C", outline="#30363D", width=2, tags="radar")
    canvas.create_arc(cx-(r*0.6), cy-(r*0.6), cx+(r*0.6), cy+(r*0.6), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    canvas.create_arc(cx-(r*0.3), cy-(r*0.3), cx+(r*0.3), cy+(r*0.3), start=45, extent=90, fill="", outline="#30363D", style="arc", tags="radar")
    canvas.create_line(cx, cy, cx, cy-r, fill="#30363D", dash=(4, 4), tags="radar")
    
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
    global is_alert_muted
    
    if is_system_on:
        if hw.get_pir_detected():
            pir_status_label.config(text="🟢 PIR 상태: 움직임 감지됨!!", fg=COLOR_SUCCESS)
            
            distance_cm = hw.get_distance_cm()
            distance_label.config(text=f"{distance_cm:.1f} cm", fg="#FFFFFF")
            
            draw_radar(distance_cm)
            
            # --- 30cm 이내 거리 판정 조건구간 ---
            if distance_cm <= POPUP_DISTANCE:
                open_warning_popup()
            else:
                # 🔥 [핵심 수정] 거리가 30cm 바깥으로 나가면 뮤트(해제 상태)를 리셋합니다.
                # 이 처리 덕분에 밖으로 나갔다가 다시 들어오면 경고창이 새로 뜹니다!
                is_alert_muted = False
            
            # 15cm 이하 최종 경고 및 처리
            if distance_cm <= WARNING_DISTANCE:
                warning_label.config(text="🚨 경고: 위험 구역 침입 감지! 🚨", fg=COLOR_WARN)
                distance_card.config(highlightbackground=COLOR_WARN, highlightcolor=COLOR_WARN)
            else:
                warning_label.config(text="🔵 안전: 물체 접근 중", fg=COLOR_ACCENT)
                distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
                
            if hw.is_touch_pressed():
                touch_sensor_label.config(text="🔮 터치 센서: 인증 성공 [모터 작동]", fg=COLOR_TOUCH)
                hw.activate_servo(root)
            else:
                touch_sensor_label.config(text="⚪ 터치 센서: 생체 인증 대기 중", fg=TEXT_MAIN)
                
        else:
            pir_status_label.config(text="⚫ PIR 상태: 주변 탐색 중...", fg=TEXT_MUTED)
            distance_label.config(text="-- cm", fg=TEXT_MUTED)
            warning_label.config(text="✅ 시스템 안전 보장됨", fg=TEXT_MUTED)
            distance_card.config(highlightbackground=CARD_BG, highlightcolor=CARD_BG)
            
            draw_radar(999) 
            
            # PIR 감지가 해제된 경우에도 사람이 멀어진 것이므로 경고 뮤트 상태를 리셋해 줍니다.
            is_alert_muted = False
            
            if hw.is_touch_pressed():
                touch_sensor_label.config(text="🔒 모터 거부 (PIR 감지 선행 필요)", fg=COLOR_WARN)
            else:
                touch_sensor_label.config(text="⚪ 터치 센서: 대기 중", fg=TEXT_MUTED)

    root.after(100, monitor_sensors)

# --- GUI 레이아웃 구성 ---
root = tk.Tk()
root.title("ADVANCED RADAR SECURITY SYSTEM")
root.geometry("600x900") 
root.configure(bg=BG_COLOR) 

title_label = tk.Label(root, text="📡 RADAR MONITORING SYSTEM", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg="#FFFFFF")
title_label.pack(pady=25)

toggle_btn = tk.Button(root, text="🔒 SYSTEM: DISABLED (OFF)", font=("Arial", 13, "bold"), bg="#21262D", fg=TEXT_MUTED, bd=0, relief="flat", cursor="hand2", activebackground=COLOR_SUCCESS, command=toggle_system)
toggle_btn.pack(pady=15, ipady=10, ipadx=30)

pir_status_label = tk.Label(root, text="❌ 시스템이 꺼져 있습니다.", font=("Arial", 14, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
pir_status_label.pack(pady=10)

canvas = tk.Canvas(root, width=400, height=260, bg=BG_COLOR, bd=0, relief="flat", highlightthickness=0)
canvas.pack(pady=5)
draw_radar(999) 

distance_card = tk.LabelFrame(root, text=" 🎯 TARGET DISTANCE ", font=("Arial", 10, "bold"), bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", highlightthickness=2, highlightbackground=CARD_BG)
distance_card.pack(pady=15, padx=60, fill="x")

distance_label = tk.Label(distance_card, text="-- cm", font=("Arial", 42, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
distance_label.pack(pady=15)

warning_label = tk.Label(root, text="STANDBY", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_MUTED)
warning_label.pack(pady=10)

touch_sensor_label = tk.Label(root, text="⚪ 장치 비활성화 상태", font=("Arial", 13), bg=BG_COLOR, fg=TEXT_MUTED)
touch_sensor_label.pack(pady=10)

exit_button = tk.Button(root, text="❌ 시 스 템  종 료", font=("Arial", 13, "bold"), bg="#21262D", fg=COLOR_WARN, bd=0, relief="flat", activebackground=COLOR_WARN, activeforeground="#FFFFFF", cursor="hand2", command=root.destroy)
exit_button.pack(pady=25, ipady=12, ipadx=40)

root.after(100, monitor_sensors)
root.mainloop()