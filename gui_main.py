def open_warning_popup():
    """30cm 이내 접근 시 새로운 경고 창을 띄우는 함수 (초점 및 레이어 꼬임 해결 버전)"""
    global is_popup_open
    if is_popup_open: 
        return  # 이미 창이 열려 있다면 중복해서 열지 않음
        
    is_popup_open = True
    
    # 새로운 서브 창(Toplevel) 생성 및 부모 창 지정
    popup = tk.Toplevel(root)
    popup.title("⚠️ 보안 경고")
    popup.geometry("350x200")
    popup.configure(bg=CARD_BG)
    
    # 🔥 [핵심 수정 1] 이 경고창을 메인 창(root)의 종속 창으로 설정
    # 이렇게 하면 메인 창이 어디에 있든 이 경고창이 항상 메인 창 바로 위에 붙어 나옵니다.
    popup.transient(root)
    
    # 팝업창을 모든 창의 최상단 레이어로 설정
    popup.attributes("-topmost", True)
    
    # 팝업창이 닫힐 때 실행할 함수 지정 (플래그 리셋)
    def on_close():
        global is_popup_open
        is_popup_open = False
        popup.grab_release() # 독점 해제
        popup.destroy()
        
    popup.protocol("WM_DELETE_WINDOW", on_close)

    # 경고 문구 레이블
    lbl = tk.Label(popup, text="🚨 경고: 물체가 30cm 이내로\n접근했습니다!\n\n경고를 해제하시겠습니까?", 
                   font=("Arial", 12, "bold"), bg=CARD_BG, fg=TEXT_MAIN, justify="center")
    lbl.pack(pady=20)
    
    # 버튼들을 한 줄에 배치하기 위한 프레임
    btn_frame = tk.Frame(popup, bg=CARD_BG)
    btn_frame.pack(pady=10)
    
    # [해제] 버튼
    btn_clear = tk.Button(btn_frame, text="해제", font=("Arial", 11, "bold"), bg=COLOR_SUCCESS, fg="#0D1117",
                          bd=0, relief="flat", width=10, command=on_close)
    btn_clear.pack(side="left", padx=15, ipady=5)
    
    # [해제 안함] 버튼
    btn_keep = tk.Button(btn_frame, text="해제 안함", font=("Arial", 11, "bold"), bg=COLOR_WARN, fg="#FFFFFF",
                         bd=0, relief="flat", width=10, command=on_close)
    btn_keep.pack(side="right", padx=15, ipady=5)

    # 🔥 [핵심 수정 2] 프로그램의 초점과 마우스 이벤트를 이 팝업창으로 강제 집중
    popup.update() # 창 그리기를 즉시 완료한 후
    popup.grab_set() # 입력 독점권 발동