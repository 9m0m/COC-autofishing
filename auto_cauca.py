"""
COC-autofishing: Bot tự động câu cá cho game Clash of Critters trên giả lập Android.
Hỗ trợ: BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.

Cơ chế điều khiển:
1. Nhận diện trạng thái nút câu qua không gian màu HSV:
   - Xanh lá (green_px > 400): Nút sẵn sàng -> Quăng cần xuống nước.
   - Xám (grey_px > 600): Cần đang dưới nước -> Đợi cá cắn, không click nhầm.
   - Tím (purple_px > 700): Cá cắn câu -> Giật cần tức thì và quét minigame.
   - Tối / Popup: Nhận thưởng tại toạ độ an toàn (Rel Y = 0.870), tránh nút X ở đáy.
2. Quét minigame thanh trượt tốc độ cao (100+ FPS) bằng MSS + OpenCV.
3. Tự động bù trừ viền cửa sổ và thanh công cụ theo từng giả lập.
4. Nhấn giữ phím 'q' ở bất kỳ đâu để dừng bot an toàn.
"""

import sys
import os
import time
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

# Thiết lập DPI Awareness cho Windows để toạ độ chuột và cửa sổ chuẩn xác 100%
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

# Tắt chế độ QuickEdit của Windows Console để tránh việc người dùng bôi đen chữ làm treo bot
try:
    kernel32 = ctypes.windll.kernel32
    hStdin = kernel32.GetStdHandle(-10)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(hStdin, ctypes.byref(mode))
    mode.value &= ~0x0040
    kernel32.SetConsoleMode(hStdin, mode)
except Exception:
    pass

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


def log(msg: str) -> None:
    """In log kèm mốc thời gian thời gian thực"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def find_emulator_window() -> Optional[gw.Window]:
    """
    Tự động tìm kiếm cửa sổ của các giả lập Android phổ biến:
    BlueStacks, LDPlayer, NoxPlayer, MuMu Player, MEmu.
    Cảnh báo nếu phát hiện nhiều cửa sổ giả lập cùng lúc.
    """
    targets = ["BlueStacks", "App Player", "LDPlayer", "Nox", "MuMu", "MEmu"]
    found: list = []
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
                    # Kiểm tra kích thước hợp lệ của cửa sổ giả lập (tránh các cửa sổ chạy ngầm)
                    if width > 250 and height > 400:
                        found.append(w)
                        break  # Không đếm trùng 1 cửa sổ nhiều lần
    except Exception:
        pass

    if len(found) > 1:
        log(f"[CẢNH BÁO] Phát hiện {len(found)} cửa sổ giả lập đang chạy!")
        log(f"[CẢNH BÁO] Bot sẽ dùng cửa sổ đầu tiên: '{found[0].title}'")
        log("[CẢNH BÁO] Nếu muốn dùng cửa sổ khác, hãy đóng bớt các giả lập còn lại.")
    if found:
        return found[0]

    # Dự phòng tìm theo getWindowsWithTitle
    for t in targets:
        try:
            wins = gw.getWindowsWithTitle(t)
            if wins:
                return wins[0]
        except Exception:
            pass

    return None


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Lấy toạ độ thực của cửa sổ bao gồm left, top, width, height"""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def get_game_viewport(hwnd: int, win_title: str) -> Tuple[int, int, int, int]:
    """
    Tính toạ độ vùng hiển thị game thực tế (game_left, game_top, game_width, game_height)
    sau khi trừ đi thanh tiêu đề (title bar) và thanh công cụ (sidebar) của từng giả lập.
    """
    left, top, w, h = get_window_rect(hwnd)
    title_bar_px, sidebar_left_px, sidebar_right_px = 0, 0, 0
    title_lower = win_title.lower()
    for keyword, (tb, sl, sr) in config.EMULATOR_VIEWPORT_OFFSETS.items():
        if keyword in title_lower:
            title_bar_px  = tb
            sidebar_left_px  = sl
            sidebar_right_px = sr
            break
    game_left = left + sidebar_left_px
    game_top  = top  + title_bar_px
    game_w    = w    - sidebar_left_px - sidebar_right_px
    game_h    = h    - title_bar_px
    return game_left, game_top, game_w, game_h


def safe_grab(sct, region: dict) -> Optional[np.ndarray]:
    """
    Chụp ảnh màn hình trong vùng chỉ định.
    Trả về ảnh BGR, hoặc None nếu cửa sổ bị che khuất/minimize để tránh crash bot.
    """
    try:
        raw = sct.grab(region)
        if raw is None:
            return None
        img = np.array(raw)
        if img.size == 0:
            return None
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    except Exception as e:
        log(f"[CẢNH BÁO] Lỗi chụp màn hình ({e}). Giả lập bị minimize? Bot đang thử lại...")
        time.sleep(0.5)
        return None


def touch_tap(x: int, y: int, desc: str = "") -> None:
    """Chạm cảm ứng giữ 70ms mô phỏng ngón tay người bấm trên Android"""
    if desc:
        log(f"-> [CHẠM] {desc} tại toạ độ ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0.02)
    pyautogui.mouseDown(x, y)
    time.sleep(0.07)
    pyautogui.mouseUp(x, y)


def rapid_tap(x: int, y: int) -> None:
    """Bấm siêu tốc phản xạ mili-giây cho thanh trượt và giật cần"""
    pyautogui.mouseDown(x, y)
    time.sleep(0.04)
    pyautogui.mouseUp(x, y)


def analyze_button_colors(btn_bgr: np.ndarray) -> Tuple[int, int, int]:
    """
    Phân tích số lượng pixel tương ứng với các trạng thái:
    - green_px: Pixel màu xanh lá (Nút sẵn sàng trên bờ)
    - grey_px:  Pixel màu xám (Cần đang dưới nước chờ cá đớp)
    - purple_px: Pixel màu tím (Cá cắn câu & trận kéo cá)
    """
    hsv = cv2.cvtColor(btn_bgr, cv2.COLOR_BGR2HSV)

    # 1. Quét màu xanh lá
    green_mask = cv2.inRange(
        hsv,
        np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
        np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
    )
    green_px = int(np.count_nonzero(green_mask))

    # 2. Quét màu tím
    purple_mask = cv2.inRange(
        hsv,
        np.array(config.HSV_BITE_PURPLE_LOWER, dtype=np.uint8),
        np.array(config.HSV_BITE_PURPLE_UPPER, dtype=np.uint8),
    )
    purple_px = int(np.count_nonzero(purple_mask))

    # 3. Quét màu xám (S thấp, V trung bình)
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    grey_mask = (s_channel < config.GREY_SATURATION_MAX) & (
        v_channel >= config.GREY_VALUE_MIN
    ) & (v_channel <= config.GREY_VALUE_MAX)
    grey_px = int(np.count_nonzero(grey_mask))

    return green_px, grey_px, purple_px


def detect_yellow_and_bobber(roi_img: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
    """
    Quét ô vàng mục tiêu và phao đỏ trên thanh trượt mini-game.
    Loại trừ trường hợp chữ 'Hoàn hảo!' lóe sáng làm mở rộng dải vàng quá mức (> 130px).
    """
    hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)

    # Quét ô vàng
    lower_yellow = np.array(config.HSV_YELLOW_LOWER, dtype=np.uint8)
    upper_yellow = np.array(config.HSV_YELLOW_UPPER, dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    y_points = np.where(yellow_mask > 0)[1]

    if len(y_points) < 5:
        return None, None

    yellow_start = int(np.percentile(y_points, 5))
    yellow_end = int(np.percentile(y_points, 95))
    yellow_width = yellow_end - yellow_start

    # Nếu vùng vàng quá to (> 130px), đây là hiệu ứng chữ 'Hoàn hảo!' hoặc nền thẻ
    if yellow_width > config.YELLOW_MAX_WIDTH:
        return None, None

    # Quét phao đỏ
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
    print("=" * 68)
    print("   AUTO CAU CA DA GIA LAP (BAN V12.1 - STATE MACHINE CHUAN XAC)")
    print("=" * 68)
    print("(*) Hỗ trợ: BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.")
    print("(*) Nhấn giữ phím 'q' trên bàn phím để DỪNG AUTO an toàn.")
    print("(*) Phân biệt chính xác: Trên bờ (Xanh) - Dưới nước (Xám) - Cá cắn (Tím).")
    print("-" * 68)

    win = find_emulator_window()
    if not win:
        log("[CHỜ ĐỢI] Chưa phát hiện cửa sổ giả lập nào (BlueStacks, LDPlayer, Nox, MuMu, MEmu)...")
        log("[HƯỚNG DẪN] Bạn hãy mở giả lập và vào game, bot sẽ tự động nhận diện và kết nối!")
        log("(*) Hoặc nhấn giữ phím 'q' để huỷ bỏ.")
        while not win:
            time.sleep(1.2)
            if keyboard.is_pressed("q"):
                log("\n[DỪNG] Người dùng đã huỷ bỏ tìm kiếm.")
                return
            win = find_emulator_window()

    hwnd = win._hWnd
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    # Bù viền cửa sổ và thanh công cụ theo từng giả lập trước khi tính toạ độ tương đối
    left, top, w, h = get_game_viewport(hwnd, win.title)
    raw_left, raw_top, raw_w, raw_h = get_window_rect(hwnd)
    log(f"[KẾT NỐI] Cửa sổ: '{win.title}'")
    log(f"[CỬA SỔ THỰC]  Left={raw_left}, Top={raw_top}, Width={raw_w}, Height={raw_h}")
    log(f"[VÙNG GAME]    Left={left}, Top={top}, Width={w}, Height={h}  (đã bù sidebar/titlebar)")

    btn_screen_x = int(left + w * config.BUTTON_REL_X)
    btn_screen_y = int(top + h * config.BUTTON_REL_Y)

    # Toạ độ nút "Nhận Ngay" (Rel X = 0.465, Rel Y = 0.870)
    # Vị trí này nằm ngoài modal kỷ lục và trúng nút Nhận Ngay cá thường. Tuyệt đối tránh nút X ở Y=0.950.
    claim_screen_x = int(left + w * config.CLAIM_REL_X)
    claim_screen_y = int(top + h * config.CLAIM_REL_Y)

    btn_box = {
        "top": btn_screen_y - 30,
        "left": btn_screen_x - 30,
        "width": 60,
        "height": 60,
    }

    slider_left = int(left + w * config.SLIDER_REL_X_MIN)
    slider_right = int(left + w * config.SLIDER_REL_X_MAX)
    slider_top = int(top + h * config.SLIDER_REL_Y_MIN)
    slider_bottom = int(top + h * config.SLIDER_REL_Y_MAX)

    slider_box = {
        "top": slider_top,
        "left": slider_left,
        "width": slider_right - slider_left,
        "height": slider_bottom - slider_top,
    }

    sct = mss.MSS() if hasattr(mss, "MSS") else mss.mss()
    fish_count = 0
    state = "READY_TO_CAST"
    last_heartbeat = 0
    wait_ready_start = time.time()

    log("[BẮT ĐẦU] Khởi động vòng lặp câu cá tự động...")

    # Bọc vòng lặp chính để xử lý an toàn ngoại lệ FailSafe và KeyboardInterrupt
    try:
        while True:
            if keyboard.is_pressed("q"):
                log("\n[DỪNG KHẨN CẤP] Người dùng đã nhấn phím 'q'. Thoát bot an toàn!")
                break

            now = time.time()

            # Trạng thái 1: Chuẩn bị quăng cần
            if state == "READY_TO_CAST":
                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    time.sleep(0.5)
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                # Ưu tiên 1: Cá cắn câu ngay trong lúc chờ -> Giật cần tức thì
                if purple_px > config.PURPLE_PX_THRESHOLD:
                    log(f"[PHỤC HỒI NHANH] Cá đang cắn ({purple_px} px tím) -> GIẬT CẦN NGAY!")
                    rapid_tap(btn_screen_x, btn_screen_y)
                    time.sleep(0.35)
                    state = "MINIGAME_SLIDER"
                    log("[3/4] BẬT CHẾ ĐỘ QUÉT THANH TRƯỢT SIÊU TỐC (100+ FPS)...")
                    continue

                # Ưu tiên 2: Cần câu đã ở dưới nước -> Giữ yên lặng chờ cá cắn
                if grey_px > config.GREY_PX_THRESHOLD:
                    log(f"[PHỤC HỒI NHANH] Phát hiện cần câu đang ở dưới nước ({grey_px} px xám) -> Chuyển sang chờ cá cắn!")
                    state = "WAITING_BITE"
                    last_heartbeat = now
                    continue

                # Ưu tiên 3: Nút xanh lá trên bờ -> Quăng cần
                if green_px > config.GREEN_PX_THRESHOLD:
                    log(f"[1/4] Thấy nút sẵn sàng ({green_px} px xanh) -> TIẾN HÀNH THẢ CẦN!")
                    touch_tap(btn_screen_x, btn_screen_y, desc="Nút quăng cần câu")
                    time.sleep(1.2)

                    # Xác nhận cần đã chạm nước bằng cả hai chỉ số màu
                    c_bgr = safe_grab(sct, btn_box)
                    if c_bgr is not None:
                        c_green, c_grey, _ = analyze_button_colors(c_bgr)
                        if c_green < 250 and c_grey > 300:
                            log("[2/4] Cần đã xuống nước thành công! Chuyển sang chờ cá cắn...")
                            state = "WAITING_BITE"
                            last_heartbeat = time.time()
                        else:
                            log("[THỬ LẠI] Cú chạm chưa ăn (nút vẫn xanh) -> Thử chạm lại...")
                            time.sleep(0.2)
                    continue

                # In nhịp tim mỗi 1.2s để theo dõi trạng thái
                if now - last_heartbeat > 1.2:
                    log(f"[Chờ sẵn sàng] Xanh: {green_px} px | Xám: {grey_px} px | Tím: {purple_px} px")
                    last_heartbeat = now

                # Ưu tiên 4: Màn hình bị kẹt bảng popup tồn dư (các màu đều < 200) quá 2.5s -> Chạm giải phóng
                if now - wait_ready_start > 2.5:
                    log("[GIẢI PHÓNG MÀN HÌNH] Chạm vị trí Nhận Ngay để giải phóng popup tồn dư...")
                    touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (ngoài thẻ)")
                    time.sleep(0.8)
                    wait_ready_start = time.time()
                else:
                    time.sleep(0.15)

            # =============================================================
            # BƯỚC 2: CHỜ CÁ CẮN CÂU (WAITING_BITE)
            # =============================================================
            elif state == "WAITING_BITE":
                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    time.sleep(0.5)
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                # Trường hợp cần bị thu về bờ (nút lại xanh > 400 px) -> Quay lại thả cần
                if green_px > config.GREEN_PX_THRESHOLD:
                    log(f"[PHỤC HỒI NHỊP] Cần câu đã ở trên bờ (nút còn {green_px} px xanh) -> Thả cần lại ngay!")
                    state = "READY_TO_CAST"
                    wait_ready_start = time.time()
                    continue

                # In log trạng thái mỗi 2 giây
                if now - last_heartbeat > 2.0:
                    log(f"[Đang thả câu dưới nước] Nút xám: {grey_px} px (Tím: {purple_px} px, cần > 700 px) -> Đang chờ cá đớp...")
                    last_heartbeat = now

                # CÁ ĐÃ CẮN CÂU THỰC SỰ! (Nút đổi sang màu tím rực rỡ > 700 px)
                if purple_px > config.PURPLE_PX_THRESHOLD:
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
                no_slider_since = 0.0
                last_hit_time = 0.0
                hit_count = 0
                # Giới hạn thời gian minigame để tự phục hồi nếu giả lập bị treo
                minigame_start = time.time()

                while True:
                    if keyboard.is_pressed("q"):
                        return

                    cur_t = time.time()

                    # Thoát minigame khi vượt quá thời gian tối đa
                    if cur_t - minigame_start > config.MINIGAME_MAX_DURATION:
                        log(f"[TIMEOUT] Minigame vượt quá {config.MINIGAME_MAX_DURATION}s -> Tự reset vòng câu mới...")
                        state = "READY_TO_CAST"
                        wait_ready_start = time.time()
                        break

                    s_bgr = safe_grab(sct, slider_box)
                    if s_bgr is None:
                        time.sleep(0.05)
                        continue

                    yellow_range, bobber_x = detect_yellow_and_bobber(s_bgr)

                    if yellow_range is None:
                        # Kiểm tra nút câu cá ở đáy xem còn màu TÍM (lưỡi câu dưới nước) không
                        b_bgr = safe_grab(sct, btn_box)
                        if b_bgr is None:
                            time.sleep(0.05)
                            continue
                        _, _, purple_px = analyze_button_colors(b_bgr)

                        if purple_px > config.PURPLE_PX_THRESHOLD:
                            # Nút vẫn TÍM -> Game VẪN ĐANG TRONG TRẬN CÂU CÁ (chưa kết thúc)!
                            # Chữ 'Hoàn hảo!' hoặc ô vàng đang dịch chuyển nên thanh trượt tạm ẩn
                            no_slider_since = 0.0
                            time.sleep(0.01)
                            continue
                        else:
                            # Nút tím đã biến mất hẳn (< 700 px) -> Cá đã được kéo lên bờ thành công!
                            if no_slider_since == 0.0:
                                no_slider_since = cur_t
                            if cur_t - no_slider_since > 0.8:
                                log(f"[3/4] Kéo cá hoàn tất (Đã đạt {hit_count} nhịp Hoàn Hảo)! Chuyển sang nhận quà.")
                                state = "CLAIM_REWARD"
                                break
                            time.sleep(0.015)
                            continue
                    else:
                        no_slider_since = 0.0

                    # Nhấp chuột siêu tốc khi phao trúng ô vàng
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
                log("[4/4] Chờ hoạt ảnh cá nhảy & bảng quà xuất hiện ổn định (1.6s)...")
                time.sleep(1.6)

                # Chạm nhịp 1 vào vị trí Nhận Ngay (ngoài thẻ kỷ lục / trúng nút cá thường)
                touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (Nhịp 1)")

                # Khoảng trễ giữa 2 lần click (0.9s)
                time.sleep(0.9)

                # Chạm nhịp 2 để xác nhận đóng hoàn toàn
                touch_tap(claim_screen_x, claim_screen_y, desc="Chạm vị trí Nhận Ngay (Nhịp 2 - Xác nhận)")

                fish_count += 1
                log(f"[HOÀN TẤT] >> Bạn đã câu thành công chú cá #{fish_count}! <<")

                # Khoảng trễ 1.0s để game đóng hẳn bảng quà và nút xanh sẵn sàng ổn định (Tổng chu trình đúng 3.5s)
                time.sleep(1.0)

                state = "READY_TO_CAST"
                wait_ready_start = time.time()
                log("=" * 45)
                log("[VÒNG MỚI] Đang chờ nút câu cá sẵn sàng...")
                last_heartbeat = time.time()

    except pyautogui.FailSafeException:
        log("\n[AN TOÀN] Di chuột vào góc màn hình -> Dừng bot an toàn! (FailSafe kích hoạt)")
    except KeyboardInterrupt:
        log("\n[AN TOÀN] Ctrl+C -> Thoát bot.")
    except Exception as e:
        log(f"\n[LỖI BẤT NGỜ] {type(e).__name__}: {e}")
        log("[GỢI Ý] Hãy báo lỗi này cho tác giả để được hỗ trợ.")
    finally:
        log("[KẾT THÚC] Bot đã dừng hoàn toàn.")
        # Nếu chạy dạng file .exe độc lập, giữ màn hình để người dùng đọc thông tin
        if getattr(sys, "frozen", False):
            print("\nNhấn Enter để đóng cửa sổ...")
            try:
                input()
            except Exception:
                pass
