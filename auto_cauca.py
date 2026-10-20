"""
AUTO CÂU CÁ BLUESTACKS - BẢN V11 (KHÓA CHẶT MINI-GAME, CHỐNG THOÁT SỚM 100%)
Cải tiến bước ngoặt:
1. KHÓA CHẶT MINI-GAME: Giữ trạng thái kéo cá chừng nào nút bấm ở đáy còn màu TÍM (> 700 px).
   - Tuyệt đối không bao giờ thoát sớm khi chữ 'Rất tuyệt!' hay 'Hoàn hảo!' lóe sáng.
   - Kéo trọn vẹn từng con cá khó tính nhất (kể cả thời gian kéo dài 15-20s).
2. TỰ ĐỘNG PHỤC HỒI NHỊP: Nếu đang ở READY_TO_CAST mà thấy nút còn tím -> Tự quay lại mini-game ngay lập tức.
3. TẮT POPUP CHUẨN XÁC: Chạm 2 nhịp vào vị trí nút Nhận Ngay (Rel Y = 0.870), tuyệt đối không bấm nút X thoát game.
Nhấn giữ phím 'q' để DỪNG AUTO bất kỳ lúc nào.
"""

import sys
import ctypes
from ctypes import wintypes

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

try:
    kernel32 = ctypes.windll.kernel32
    hStdin = kernel32.GetStdHandle(-10)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(hStdin, ctypes.byref(mode))
    mode.value &= ~0x0040
    kernel32.SetConsoleMode(hStdin, mode)
except Exception:
    pass

import time
import cv2
import numpy as np
import mss
import pyautogui
import pygetwindow as gw
import keyboard
import config

user32 = ctypes.windll.user32
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def find_emulator_window():
    """
    Tự động tìm kiếm cửa sổ của các giả lập Android phổ biến:
    BlueStacks, LDPlayer, NoxPlayer, MuMu Player, MEmu.
    """
    targets = ["BlueStacks", "App Player", "LDPlayer", "Nox", "MuMu", "MEmu"]
    try:
        for w in gw.getAllWindows():
            title = w.title
            if not title:
                continue
            for t in targets:
                if t.lower() in title.lower():
                    rect = wintypes.RECT()
                    user32.GetWindowRect(w._hWnd, ctypes.byref(rect))
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    if width > 250 and height > 400:
                        return w
    except Exception:
        pass

    # Dự phòng tìm theo getWindowsWithTitle
    for t in targets:
        try:
            wins = gw.getWindowsWithTitle(t)
            if wins:
                return wins[0]
        except Exception:
            pass

    return None

def get_window_rect(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top

def touch_tap(x, y, desc=""):
    """Chạm cảm ứng giữ 70ms mô phỏng tay chạm Android"""
    log(f"-> [CHẠM] {desc} tại toạ độ ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0.02)
    pyautogui.mouseDown(x, y)
    time.sleep(0.07)
    pyautogui.mouseUp(x, y)

def rapid_tap(x, y):
    """Bấm siêu tốc phản xạ mili-giây cho thanh trượt"""
    pyautogui.mouseDown(x, y)
    time.sleep(0.04)
    pyautogui.mouseUp(x, y)

def detect_yellow_and_bobber(roi_img):
    """
    Quét ô vàng và phao trên thanh trượt.
    Chỉ chấp nhận ô vàng có độ rộng hợp lý (<= 130px).
    """
    hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
    
    lower_yellow = np.array(config.HSV_YELLOW_LOWER, dtype=np.uint8)
    upper_yellow = np.array(config.HSV_YELLOW_UPPER, dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    y_points = np.where(yellow_mask > 0)[1]
    
    if len(y_points) < 5:
        return None, None
        
    yellow_start = int(np.percentile(y_points, 5))
    yellow_end = int(np.percentile(y_points, 95))
    yellow_width = yellow_end - yellow_start
    
    # Nếu vùng vàng quá to (> 130px), đây là chữ Hoàn Hảo hoặc nền thẻ vàng -> Không coi là ô vàng bấm
    if yellow_width > 130:
        return None, None
        
    lower_red1 = np.array(config.HSV_RED_LOWER1, dtype=np.uint8)
    upper_red1 = np.array(config.HSV_RED_UPPER1, dtype=np.uint8)
    lower_red2 = np.array(config.HSV_RED_LOWER2, dtype=np.uint8)
    upper_red2 = np.array(config.HSV_RED_UPPER2, dtype=np.uint8)
    
    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    red_points = np.where(red_mask > 0)[1]
    
    if len(red_points) == 0:
        return (yellow_start, yellow_end), None
        
    bobber_x = int(np.median(red_points))
    return (yellow_start, yellow_end), bobber_x

def main():
    print("=" * 65)
    print("   AUTO CÂU CÁ BLUESTACKS (BẢN V11 - KHÓA CHẶT MINI-GAME)")
    print("=" * 65)
    print("(*) Nhấn giữ phím 'q' bất cứ lúc nào để DỪNG AUTO.")
    print("(*) Không bao giờ thoát sớm mini-game khi nút đáy còn màu tím.")
    print("(*) Tự động phục hồi nhịp kéo cá nếu bị nhảy state.")
    print("-" * 65)
    
    win = find_emulator_window()
    if not win:
        log("[LỖI] Không tìm thấy cửa sổ giả lập (BlueStacks, LDPlayer, Nox, MuMu, MEmu). Vui lòng mở game trước!")
        return
        
    hwnd = win._hWnd
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    left, top, w, h = get_window_rect(hwnd)
    log(f"[KẾT NỐI] Cửa sổ: '{win.title}'")
    log(f"[TOẠ ĐỘ] Left={left}, Top={top}, Width={w}, Height={h}")
    
    btn_screen_x = int(left + w * config.BUTTON_REL_X)
    btn_screen_y = int(top + h * config.BUTTON_REL_Y)
    
    # Toạ độ nút "Nhận Ngay" (Rel X = 0.465, Rel Y = 0.870)
    # Cá thường: Chạm trực tiếp nút Nhận Ngay.
    # Cá kỷ lục/team: Vị trí này nằm ngoài popup -> Tắt popup an toàn TUYỆT ĐỐI KHÔNG chạm nút X thoát game!
    claim_screen_x = int(left + w * config.CLAIM_REL_X)
    claim_screen_y = int(top + h * config.CLAIM_REL_Y)
    
    btn_box = {
        "top": btn_screen_y - 30,
        "left": btn_screen_x - 30,
        "width": 60,
        "height": 60
    }
    
    slider_left = int(left + w * config.SLIDER_REL_X_MIN)
    slider_right = int(left + w * config.SLIDER_REL_X_MAX)
    slider_top = int(top + h * config.SLIDER_REL_Y_MIN)
    slider_bottom = int(top + h * config.SLIDER_REL_Y_MAX)
    
    slider_box = {
        "top": slider_top,
        "left": slider_left,
        "width": slider_right - slider_left,
        "height": slider_bottom - slider_top
    }
    
    sct = mss.MSS() if hasattr(mss, 'MSS') else mss.mss()
    fish_count = 0
    state = "READY_TO_CAST"
    last_heartbeat = 0
    wait_ready_start = time.time()
    
    log("[BẮT ĐẦU] Khởi động vòng lặp câu cá...")
    
    while True:
        if keyboard.is_pressed('q'):
            log("\n[DỪNG] Người dùng đã nhấn phím 'q'. Thoát bot an toàn!")
            break
            
        now = time.time()
        
        # =============================================================
        # BƯỚC 1: SẴN SÀNG THẢ CẦN (READY_TO_CAST)
        # =============================================================
        if state == "READY_TO_CAST":
            btn_img = np.array(sct.grab(btn_box))
            bgr = cv2.cvtColor(btn_img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            
            green_mask = cv2.inRange(hsv, np.array(config.HSV_READY_GREEN_LOWER), np.array(config.HSV_READY_GREEN_UPPER))
            green_px = np.count_nonzero(green_mask)
            
            if now - last_heartbeat > 1.0:
                log(f"[Chờ nút sẵn sàng] Màu xanh nút: {green_px} px (Cần > 400 px)")
                last_heartbeat = now
                
            # Phục hồi nếu game vẫn đang trong mini-game kéo cá (nút còn tím rực > 700 px)
            purple_mask = cv2.inRange(hsv, np.array(config.HSV_BITE_PURPLE_LOWER), np.array(config.HSV_BITE_PURPLE_UPPER))
            purple_px = np.count_nonzero(purple_mask)
            if purple_px > 700:
                log(f"[PHỤC HỒI NHỊP KÉO CÁ] Phát hiện game vẫn đang kéo cá ({purple_px} px tím) -> Quay lại thanh trượt ngay!")
                state = "MINIGAME_SLIDER"
                continue

            # Khi thấy nút câu cá màu xanh lá sẵn sàng trên bờ
            if green_px > 400:
                log(f"[1/4] Thấy nút sẵn sàng ({green_px} px xanh) -> TIẾN HÀNH THẢ CẦN!")
                touch_tap(btn_screen_x, btn_screen_y, desc="Nút quăng cần câu")
                time.sleep(1.4)  # Đợi cần quăng xuống nước
                
                # Xác nhận lại xem cần đã rơi xuống nước chưa
                check_img = np.array(sct.grab(btn_box))
                c_hsv = cv2.cvtColor(cv2.cvtColor(check_img, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)
                c_green = np.count_nonzero(cv2.inRange(c_hsv, np.array(config.HSV_READY_GREEN_LOWER), np.array(config.HSV_READY_GREEN_UPPER)))
                
                if c_green < 250:
                    log("[2/4] Cần đã xuống nước thành công! Chuyển sang chờ cá cắn...")
                    state = "WAITING_BITE"
                    last_heartbeat = time.time()
                else:
                    log("[THỬ LẠI] Cú chạm chưa ăn (nút vẫn xanh) -> Thử chạm lại...")
                    time.sleep(0.2)
                    continue
            else:
                # Nếu sau 4.5 giây mà thực sự chưa thấy nút xanh, chạm vị trí Nhận Ngay để giải phóng bảng tồn dư
                if now - wait_ready_start > 4.5:
                    log("[GIẢI PHÓNG MÀN HÌNH] Chạm vị trí Nhận Ngay để giải phóng bảng tồn dư...")
                    touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (ngoài thẻ)")
                    time.sleep(1.0)
                    wait_ready_start = time.time()
                else:
                    time.sleep(0.2)
                    
        # =============================================================
        # BƯỚC 2: CHỜ CÁ CẮN CÂU (WAITING_BITE)
        # =============================================================
        elif state == "WAITING_BITE":
            btn_img = np.array(sct.grab(btn_box))
            bgr = cv2.cvtColor(btn_img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            
            # Phục hồi nếu cần chưa thả (nút vẫn còn xanh lá)
            green_mask = cv2.inRange(hsv, np.array(config.HSV_READY_GREEN_LOWER), np.array(config.HSV_READY_GREEN_UPPER))
            green_px = np.count_nonzero(green_mask)
            if green_px > 400:
                log(f"[PHỤC HỒI NHỊP] Cần câu vẫn ở trên bờ (nút còn {green_px} px xanh) -> Thả cần lại ngay!")
                state = "READY_TO_CAST"
                continue
                
            purple_mask = cv2.inRange(hsv, np.array(config.HSV_BITE_PURPLE_LOWER), np.array(config.HSV_BITE_PURPLE_UPPER))
            purple_px = np.count_nonzero(purple_mask)
            
            if now - last_heartbeat > 2.0:
                log(f"[Đang thả câu dưới nước] Nút xám (Tím: {purple_px} px, cần > 700 px) -> Đang chờ cá đớp...")
                last_heartbeat = now
                
            # Chỉ giật khi cá cắn thật (Tím > 700 px, thực tế 1500-1600 px)
            if purple_px > 700:
                log(f"[2/4] >> CÁ ĐÃ CẮN CÂU THỰC SỰ! ({purple_px} px tím) -> GIẬT CẦN LẬP TỨC! <<")
                rapid_tap(btn_screen_x, btn_screen_y)
                time.sleep(0.35)
                state = "MINIGAME_SLIDER"
                log("[3/4] BẬT CHẾ ĐỘ QUÉT THANH TRƯỢT SIÊU TỐC (100+ FPS)...")
            else:
                time.sleep(0.015)
                
        # =============================================================
        # BƯỚC 3: MINI-GAME THANH TRƯỢT (MINIGAME_SLIDER)
        # =============================================================
        elif state == "MINIGAME_SLIDER":
            minigame_start = time.time()
            no_slider_since = 0
            last_hit_time = 0
            hit_count = 0
            
            while True:
                if keyboard.is_pressed('q'):
                    return
                    
                cur_t = time.time()
                slider_img = np.array(sct.grab(slider_box))
                s_bgr = cv2.cvtColor(slider_img, cv2.COLOR_BGRA2BGR)
                
                yellow_range, bobber_x = detect_yellow_and_bobber(s_bgr)
                
                if yellow_range is None:
                    # Kiểm tra nút câu cá ở đáy xem còn màu TÍM (lưỡi câu dưới nước) không
                    btn_img = np.array(sct.grab(btn_box))
                    b_hsv = cv2.cvtColor(cv2.cvtColor(btn_img, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)
                    purple_px = np.count_nonzero(cv2.inRange(b_hsv, np.array(config.HSV_BITE_PURPLE_LOWER), np.array(config.HSV_BITE_PURPLE_UPPER)))
                    
                    if purple_px > 700:
                        # Nút vẫn TÍM -> Game VẪN ĐANG TRONG TRẬN CÂU CÁ (chưa kết thúc)!
                        # Có thể chữ 'Rất tuyệt!' hay 'Hoàn hảo!' đang che hoặc ô vàng đang đổi vị trí
                        no_slider_since = 0
                        time.sleep(0.01)
                        continue
                    else:
                        # Nút tím đã biến mất hẳn (< 700 px) -> Cá đã lên bờ hoặc chuyển sang nhận quà!
                        if no_slider_since == 0:
                            no_slider_since = cur_t
                        if cur_t - no_slider_since > 0.8:
                            log(f"[3/4] Kéo cá hoàn tất (Đã đạt {hit_count} nhịp Hoàn Hảo)! Chuyển sang nhận quà.")
                            state = "CLAIM_REWARD"
                            break
                        time.sleep(0.015)
                        continue
                else:
                    no_slider_since = 0
                    
                if bobber_x is not None:
                    ystart, yend = yellow_range
                    if (ystart - 5) <= bobber_x <= (yend + 5):
                        if cur_t - last_hit_time > 0.16:
                            rapid_tap(btn_screen_x, btn_screen_y)
                            hit_count += 1
                            log(f"  -> [HOÀN HẢO #{hit_count}] Phao ({bobber_x}) trúng ô vàng [{ystart}, {yend}]")
                            last_hit_time = cur_t
                            
        # =============================================================
        # BƯỚC 4: NHẬN QUÀ / ĐÓNG POPUP (CLAIM_REWARD)
        # CHẠM 2 NHỊP CHẬM RÃI VÀO VỊ TRÍ NÚT "NHẬN NGAY" (Rel Y = 0.870)
        # TUYỆT ĐỐI KHÔNG CHẠM VÀO NÚT "X" Ở ĐÁY ĐỂ TRÁNH THOÁT GAME!
        # =============================================================
        elif state == "CLAIM_REWARD":
            log("[4/4] Chờ hoạt ảnh cá nhảy & bảng quà xuất hiện ổn định (2.2s)...")
            time.sleep(2.2)
            
            # Chạm nhịp 1 vào vị trí Nhận Ngay (ngoài thẻ kỷ lục / trúng nút cá thường)
            touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (Nhịp 1)")
            
            # Độ trễ giữa 2 lần click chậm hơn (1.1s) để tránh xung đột
            time.sleep(1.1)
            
            # Chạm nhịp 2 để xác nhận đóng hoàn toàn
            touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (Nhịp 2 - Xác nhận)")
            
            fish_count += 1
            log(f"[HOÀN TẤT] >> Bạn đã câu thành công chú cá #{fish_count}! <<")
            
            # Khoảng trễ 1.5s để game đóng hẳn bảng quà và nút xanh sẵn sàng ổn định
            time.sleep(1.5)
            
            state = "READY_TO_CAST"
            wait_ready_start = time.time()
            log("=" * 45)
            log("[VÒNG MỚI] Đang chờ nút câu cá sẵn sàng...")
            last_heartbeat = time.time()

if __name__ == "__main__":
    main()
