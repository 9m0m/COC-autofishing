"""
COC-autofishing: Bot tu dong cau ca cho game Clash of Critters tren gia lap Android.
Ho tro: BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.

Co che dieu khien:
1. Nhan dien trang thai nut cau qua khong gian mau HSV:
   - Xanh la (green_px > 400): Nut san sang -> Quang can xuong nuoc.
   - Xam (grey_px > 600): Can dang duoi nuoc -> Doi ca can, khong click nham.
   - Tim (purple_px > 700): Ca can cau -> Giat can tuc thi va quet minigame.
   - Toi / Popup: Nhan thuong tai toa do an toan (Rel Y = 0.870).
2. Quet minigame thanh truot toc do cao (100+ FPS) bang MSS + OpenCV.
3. Tu dong bu tru vien cua so va thanh cong cu theo tung gia lap.
4. Nhan Ctrl+Q de BAT / RESUME | Nhan ESC de TAM DUNG (nhan tiep de THOAT).
"""

import sys
import os
import time
import threading
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

# Cau hinh UTF-8 cho console Windows
if sys.platform.startswith("win"):
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# DPI Awareness de toa do chuot va cua so chuan xac 100%
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

# Tat QuickEdit cua Windows Console de tranh boi den chu lam treo bot
try:
    kernel32 = ctypes.windll.kernel32
    hStdin = kernel32.GetStdHandle(-10)
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(hStdin, ctypes.byref(mode))
    # 0x0040: ENABLE_QUICK_EDIT_MODE, 0x0080: ENABLE_EXTENDED_FLAGS (bat buoc de thay doi QuickEdit)
    new_mode = (mode.value & ~0x0040) | 0x0080
    kernel32.SetConsoleMode(hStdin, new_mode)
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

# Event dung bot - set() khi nguoi dung nhan ESC
_stop_event = threading.Event()


def log(msg: str) -> None:
    """In log kem moc thoi gian thuc."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def safe_unhook_hotkeys() -> None:
    """Go bo an toan tat ca hotkey, tranh loi noi bo cua thu vien keyboard tren Windows khi chua co hotkey nao."""
    try:
        if hasattr(keyboard, "_listener") and hasattr(keyboard._listener, "blocking_hotkeys"):
            keyboard.remove_all_hotkeys()
    except Exception:
        pass


def sleep_check(seconds: float) -> bool:
    """
    Sleep trong `seconds` giay.
    Tra ve True ngay lap tuc neu ESC duoc nhan (de thoat vong lap som).
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if _stop_event.is_set():
            return True
        time.sleep(0.02)
    return False


EMULATOR_PROCESS_KEYWORDS = [
    "nemuplayer", "mumuplayer", "mumu", "nemu",      # MuMu Player 12 / 6 / X
    "hd-player", "bluestacks",                        # BlueStacks 5
    "dnplayer", "ldplayer", "ldboxplayer",            # LDPlayer 9 / 5 / 4
    "nox",                                            # NoxPlayer
    "memu",                                           # MEmu
]

EMULATOR_TITLE_KEYWORDS = [
    "bluestacks", "app player",
    "ldplayer",
    "nox",
    "mumu", "nemu",
    "memu",
    "clash of critters", "critters",
]


def get_process_name_by_hwnd(hwnd: int) -> str:
    """Lay ten file thuc thi (.exe) cua process so huu cua so (chu thuong)."""
    try:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""
        h_proc = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h_proc:
            return ""
        buf = ctypes.create_unicode_buffer(512)
        size = wintypes.DWORD(512)
        exe_name = ""
        if kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size)):
            exe_name = os.path.basename(buf.value).lower()
        kernel32.CloseHandle(h_proc)
        return exe_name
    except Exception:
        return ""


def find_emulator_window() -> Optional[gw.Window]:
    """
    Tim kiem cua so cua cac gia lap Android pho bien (BlueStacks, LDPlayer, Nox, MuMu, MEmu).
    Ket hop ca nhan dien tieu de (Title) va tien trinh (.exe) de ho tro moi phien ban (ke ca tab MuMu/Android).
    Loc bo triet de cac cua so thu nho (minimized), cua so an hoac toa do am (-32000).
    """
    candidates = []
    try:
        for w in gw.getAllWindows():
            hwnd = w._hWnd
            # 1. Bo qua cua so dang bi thu nho (Minimized / IsIconic)
            if user32.IsIconic(hwnd):
                continue

            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            left = rect.left
            top = rect.top
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            # 2. Bo qua cua so ngoai man hinh hoac toa do am thu nho cua Windows (-32000)
            if left < -10000 or top < -10000:
                continue

            # 3. Kich thuoc toi thieu cua man hinh gia lap (loai bo cua so dummy 199x4 hoac notification)
            if (width < 250 or height < 350) and (height < 250 or width < 350):
                continue

            title = (w.title or "").strip()
            title_lower = title.lower()
            proc_name = get_process_name_by_hwnd(hwnd)

            title_matched = any(k in title_lower for k in EMULATOR_TITLE_KEYWORDS)
            proc_matched = any(k in proc_name for k in EMULATOR_PROCESS_KEYWORDS)

            if title_matched or proc_matched:
                area = width * height
                candidates.append((area, w, proc_name, title))
    except Exception:
        pass

    if not candidates:
        return None

    # Sap xep uu tien cua so co dien tich thuc te lon nhat (man hinh choi game that)
    candidates.sort(key=lambda x: x[0], reverse=True)

    if len(candidates) > 1:
        log(f"[CANH BAO] Phat hien {len(candidates)} cua so gia lap. Uu tien dung: '{candidates[0][3]}' ({candidates[0][2]})")

    return candidates[0][1]


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Lay toa do thuc cua cua so: left, top, width, height."""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def get_game_viewport(hwnd: int, win_title: str) -> Tuple[int, int, int, int]:
    """
    Tinh toa do vung hien thi game thuc te (game_left, game_top, game_width, game_height)
    sau khi tru thanh tieu de va thanh cong cu cua tung gia lap.
    Uu tien tu dong lay RenderWindow cua LDPlayer de dat do chinh xac 100%.
    """
    proc_name = get_process_name_by_hwnd(hwnd)
    title_lower = win_title.lower()

    # Uu tien tim cua so con RenderWindow cua LDPlayer
    if ("ldplayer" in title_lower) or ("dnplayer" in proc_name):
        try:
            render_hwnd = user32.FindWindowExW(hwnd, None, "RenderWindow", None)
            if render_hwnd:
                rect = wintypes.RECT()
                user32.GetWindowRect(render_hwnd, ctypes.byref(rect))
                rw = rect.right - rect.left
                rh = rect.bottom - rect.top
                if rw > 200 and rh > 350:
                    return rect.left, rect.top, rw, rh
        except Exception:
            pass

    left, top, w, h = get_window_rect(hwnd)
    title_bar_px, sidebar_left_px, sidebar_right_px = 0, 0, 0
    for keyword, (tb, sl, sr) in config.EMULATOR_VIEWPORT_OFFSETS.items():
        if (keyword in title_lower) or (keyword in proc_name):
            title_bar_px = tb
            sidebar_left_px = sl
            sidebar_right_px = sr
            break
    game_left = left + sidebar_left_px
    game_top = top + title_bar_px
    game_w = w - sidebar_left_px - sidebar_right_px
    game_h = h - title_bar_px
    return game_left, game_top, game_w, game_h


def safe_grab(sct, region: dict) -> Optional[np.ndarray]:
    """
    Chup anh man hinh trong vung chi dinh.
    Tra ve anh BGR, hoac None neu cua so bi che khuat / minimize.
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
        log(f"[CANH BAO] Loi chup man hinh ({e}). Gia lap bi minimize?")
        time.sleep(0.5)
        return None


def touch_tap(x: int, y: int, desc: str = "") -> None:
    """Cham cam ung giu 60ms bang Win32 API mo phong tay cham Android."""
    if desc:
        log(f"-> {desc} ({x}, {y})")
    user32.SetCursorPos(x, y)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    time.sleep(0.06)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP


def fast_tap(x: int, y: int) -> None:
    """Bam sieu toc mili-giay qua Win32 mouse_event truc tiep, khong do tre."""
    user32.SetCursorPos(x, y)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    time.sleep(0.02)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP


def analyze_button_colors(btn_bgr: np.ndarray) -> Tuple[int, int, int]:
    """
    Phan tich so luong pixel tuong ung voi cac trang thai nut:
    - green_px:  Nut san sang tren bo.
    - grey_px:   Can dang duoi nuoc cho ca dop.
    - purple_px: Ca can cau & tran keo ca.
    """
    hsv = cv2.cvtColor(btn_bgr, cv2.COLOR_BGR2HSV)

    green_mask = cv2.inRange(
        hsv,
        np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
        np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
    )
    green_px = int(np.count_nonzero(green_mask))

    purple_mask = cv2.inRange(
        hsv,
        np.array(config.HSV_BITE_PURPLE_LOWER, dtype=np.uint8),
        np.array(config.HSV_BITE_PURPLE_UPPER, dtype=np.uint8),
    )
    purple_px = int(np.count_nonzero(purple_mask))

    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    grey_mask = (s_channel < config.GREY_SATURATION_MAX) & (
        v_channel >= config.GREY_VALUE_MIN
    ) & (v_channel <= config.GREY_VALUE_MAX)
    grey_px = int(np.count_nonzero(grey_mask))

    return green_px, grey_px, purple_px


def disable_quickedit():
    """Vo hieu hoa che do QuickEdit cua Windows Console de tranh viec click chuot vao cmd lam treo chuong trinh."""
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        h_stdin = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode)):
            ENABLE_QUICK_EDIT_MODE = 0x0040
            ENABLE_EXTENDED_FLAGS = 0x0080
            new_mode = (mode.value & ~ENABLE_QUICK_EDIT_MODE) | ENABLE_EXTENDED_FLAGS
            kernel32.SetConsoleMode(h_stdin, new_mode)
    except Exception:
        pass


def detect_yellow_and_bobber(roi_img: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
    """
    Quet o vang muc tieu va phao do tren thanh truot mini-game bang contour & morphology.
    - Ho tro ca o vang sieu hep cua ca quy hiem / ca ky luc.
    - Tu dong ghep noi neu phao do che doi o vang o giua.
    - Bo qua cac vien mep ngoai cung de tranh nhan nham text / UI ngoai thanh truot.
    """
    hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
    kernel_yellow = np.ones((3, 1), np.uint8)
    kernel_red = np.ones((3, 3), np.uint8)
    rh, rw = roi_img.shape[:2]

    # 1. Quet o vang muc tieu (Dung kernel doc 3x1 de giu tron ven o vang sieu hep 2-5px cua ca xin)
    lower_yellow = np.array(config.HSV_YELLOW_LOWER, dtype=np.uint8)
    upper_yellow = np.array(config.HSV_YELLOW_UPPER, dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    clean_yellow = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel_yellow)

    yellow_range = None
    contours, _ = cv2.findContours(clean_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_yellows = []
    for c in contours:
        area = cv2.contourArea(c)
        if area >= 8:  # Nguong sieu nhay de khong bo sot o vang hep khi gap ca hiem / ca ky luc
            x, y, w, h = cv2.boundingRect(c)
            # CO LAP KHONG GIAN RANH TRUOT:
            # O vang muc tieu luon nam co dinh trong ranh truot (0.25 <= Y <= 0.78 trong ROI)
            # Loai bo 100% chu 'Hoan hao!' va cac tia sang lap lanh bay o phia tren ranh truot (Y < 0.25)
            if y < int(0.25 * rh) or (y + h) > int(0.78 * rh):
                continue
            # Loai bo can cau ben mep trai (x < 12) hoac nut icon chat ben mep phai
            if x < 12 or (x + w) > rw - 8:
                continue
            # Chieu cao toi thieu cua o vang trong ranh phai >= 10px (loai bo tia sang vun)
            if h >= 10 and w <= config.YELLOW_MAX_WIDTH:
                valid_yellows.append((x, x + w, area))

    if valid_yellows:
        if len(valid_yellows) == 1:
            yellow_range = (valid_yellows[0][0], valid_yellows[0][1])
        else:
            # Sap xep theo dien tich giam dan de uu tien manh vang chinh
            valid_yellows.sort(key=lambda item: item[2], reverse=True)
            main_box = valid_yellows[0]
            second_box = valid_yellows[1]
            left_box = min(main_box, second_box, key=lambda b: b[0])
            right_box = max(main_box, second_box, key=lambda b: b[0])
            gap = right_box[0] - left_box[1]
            merged_width = right_box[1] - left_box[0]
            # Chi ghep neu khoang cach <= 26px (kich thuoc phao che doi o vang) va tong rong <= 130px
            # Tranh viec ghep noi voi hat nhieu o xa lam o vang bi phong to gia tao
            if gap <= 26 and merged_width <= config.YELLOW_MAX_WIDTH:
                yellow_range = (left_box[0], right_box[1])
            else:
                yellow_range = (main_box[0], main_box[1])

    # 2. Quet phao do (bobber)
    lower_red1 = np.array(config.HSV_RED_LOWER1, dtype=np.uint8)
    upper_red1 = np.array(config.HSV_RED_UPPER1, dtype=np.uint8)
    lower_red2 = np.array(config.HSV_RED_LOWER2, dtype=np.uint8)
    upper_red2 = np.array(config.HSV_RED_UPPER2, dtype=np.uint8)

    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    clean_red = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_red)

    bobber_x = None
    r_contours, _ = cv2.findContours(clean_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_reds = []
    for c in r_contours:
        area = cv2.contourArea(c)
        # Phao do that luon co dien tich >= 50px va kich thuoc w >= 10px, h >= 10px
        # Loai bo 100% phao hoa giay confetti mau hong/do roi tren the bai (thuong chi 7x4px, area ~16px)
        if area >= 50:
            x, y, w, h = cv2.boundingRect(c)
            if w < 10 or h < 10:
                continue
            # Loai bo chu 'Hoan hao!' co vien do/cam phia tren va can cau o mep trai
            if y < int(0.15 * rh) or (y + h) > int(0.85 * rh):
                continue
            if x < 12 or (x + w) > rw - 8:
                continue
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
            else:
                rx, _, rw_c, _ = cv2.boundingRect(c)
                cx = rx + rw_c // 2
            valid_reds.append((cx, area))

    if valid_reds:
        valid_reds.sort(key=lambda item: item[1], reverse=True)
        bobber_x = valid_reds[0][0]

    return yellow_range, bobber_x


def main():
    disable_quickedit()
    print("=" * 50)
    print("   COC-AUTOFISHING V12.4")
    print("=" * 50)
    print("Ho tro: BlueStacks 5, LDPlayer 9, Nox, MuMu, MEmu")
    print("[PHIM TAT] Ctrl+Q = BAT / RESUME | ESC = TAM DUNG (Nhan ESC lan 2 de Thoat)")
    print("-" * 50)

    # Tim gia lap
    win = find_emulator_window()
    if not win:
        log("[CHO] Chua tim thay cua so gia lap...")
        log("[HUONG DAN] Mo gia lap va vao game, bot se tu nhan dien.")
        log("Nhan ESC de thoat.")
        while not win:
            time.sleep(1.2)
            if keyboard.is_pressed("esc"):
                log("[THOAT] Nguoi dung huy.")
                return
            win = find_emulator_window()

    hwnd = win._hWnd
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    left, top, w, h = 0, 0, 0, 0
    btn_screen_x, btn_screen_y = 0, 0
    claim_screen_x, claim_screen_y = 0, 0
    card_screen_x, card_screen_y = 0, 0
    btn_box = {}
    claim_box = {}
    slider_box = {}

    def sync_viewport(force: bool = False) -> bool:
        """Tu dong dong bo lai toa do neu cua so gia lap bi di chuyen hoac thay doi kich thuoc."""
        nonlocal left, top, w, h, btn_screen_x, btn_screen_y, claim_screen_x, claim_screen_y
        nonlocal card_screen_x, card_screen_y, btn_box, claim_box, slider_box
        try:
            cur_left, cur_top, cur_w, cur_h = get_game_viewport(hwnd, win.title)
            if force or (cur_left, cur_top, cur_w, cur_h) != (left, top, w, h):
                left, top, w, h = cur_left, cur_top, cur_w, cur_h
                btn_screen_x = int(left + w * config.BUTTON_REL_X)
                btn_screen_y = int(top + h * config.BUTTON_REL_Y)
                claim_screen_x = int(left + w * config.CLAIM_REL_X)
                claim_screen_y = int(top + h * config.CLAIM_REL_Y)
                card_screen_x = int(left + w * config.CARD_REL_X)
                card_screen_y = int(top + h * config.CARD_REL_Y)
                btn_box = {
                    "top": btn_screen_y - 30,
                    "left": btn_screen_x - 30,
                    "width": 60,
                    "height": 60,
                }
                claim_box = {
                    "top": claim_screen_y - 15,
                    "left": claim_screen_x - 30,
                    "width": 60,
                    "height": 30,
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
                return True
        except Exception:
            pass
        return False

    sync_viewport(force=True)
    proc_name = get_process_name_by_hwnd(hwnd)
    display_title = f"'{win.title}' ({proc_name})" if proc_name else f"'{win.title}'"
    log(f"[KET NOI] {display_title} | Game: {w}x{h} tai ({left}, {top})")
    print("*" * 50)
    log("[CHU Y] Hay kiem tra dong [KET NOI] ben tren xem da DUNG gia lap ban choi chua!")
    log("[CHU Y] Khong di chuyen cua so gia lap khi tool dang cau de tranh lech chuot.")
    log("[CHU Y] (Neu lo di chuyen: Nhan ESC tam dung roi nhan Ctrl+Q de dong bo lai).")
    print("*" * 50)

    sct = mss.MSS() if hasattr(mss, "MSS") else mss.mss()
    fish_count = 0
    state = "READY_TO_CAST"
    last_heartbeat = 0
    wait_ready_start = time.time()
    bite_wait_start = time.time()
    no_rod_start = 0.0
    last_claim_check_waiting = 0.0

    # Khoi tao trang thai: bat dau o che do cho lenh
    _stop_event.set()

    try:
        while True:
            # =========================================================
            # XU LY TRANG THAI TAM DUNG / CHO LENH (PAUSED STATE)
            # =========================================================
            if _stop_event.is_set():
                # Go bo hotkey esc de tra lai phim ESC 100% cho cac ung dung khac tren Windows
                safe_unhook_hotkeys()
                _stop_event.clear()

                # Doi nguoi dung nha cac phim dang giu
                while keyboard.is_pressed("esc") or keyboard.is_pressed("ctrl+q") or (keyboard.is_pressed("ctrl") and keyboard.is_pressed("q")):
                    time.sleep(0.05)

                if last_heartbeat == 0:
                    print("-" * 50)
                    log("[CHO LENH] Mo su kien Cau ca tren gia lap.")
                    log("[CHU Y] Kiem tra log [KET NOI] ben tren xem da dung gia lap chua.")
                    log("[CHO LENH] Nhan Ctrl+Q de BAT DAU | Nhan ESC de THOAT...")
                    print("-" * 50)
                else:
                    print("-" * 50)
                    log("[TAM DUNG] Da tam dung auto. Chuot da duoc giai phong!")
                    log(f"[TAM DUNG] Tong so ca da cau: {fish_count}")
                    log("[CHU Y] Neu ban da di chuyen cua so, tool se tu dong bo lai toa do khi Resume.")
                    log("[CHO LENH] Nhan Ctrl+Q de TIEP TUC (Resume)...")
                    log("[CHO LENH] Nhan ESC de THOAT HAN tool...")
                    print("-" * 50)

                should_exit = False
                while True:
                    # Chi tiep tuc khi bam to hop phim an toan Ctrl+Q (tranh bi bam nham khi chat Zalo/Word/Discord)
                    if keyboard.is_pressed("ctrl+q") or (keyboard.is_pressed("ctrl") and keyboard.is_pressed("q")):
                        break
                    if keyboard.is_pressed("esc"):
                        should_exit = True
                        break
                    time.sleep(0.05)

                if should_exit:
                    log("[THOAT] Nguoi dung nhan ESC de thoat.")
                    break

                # Debounce phim truoc khi vao lai vong lap
                while keyboard.is_pressed("ctrl") or keyboard.is_pressed("q"):
                    time.sleep(0.05)
                time.sleep(0.2)

                # Dang ky lai hotkey ESC de bat tam dung khi dang chay
                _stop_event.clear()
                keyboard.add_hotkey("esc", _stop_event.set, suppress=True)

                if sync_viewport():
                    log(f"[DONG BO] Cua so da di chuyen -> Cap nhat toa do moi: {w}x{h} tai ({left}, {top})")

                if last_heartbeat == 0:
                    log("[KHOI DONG] Auto bat dau! Nhan ESC bat cu luc nao de TAM DUNG.\n")
                else:
                    log("[TIEP TUC] Auto tiep tuc hoat dong! Nhan ESC bat cu luc nao de TAM DUNG.\n")

                state = "READY_TO_CAST"
                wait_ready_start = time.time()
                last_heartbeat = time.time()
                bite_wait_start = time.time()
                no_rod_start = 0.0
                last_claim_check_waiting = 0.0
                continue

            now = time.time()

            # =========================================================
            # BUOC 1: CHUAN BI QUANG CAN (READY_TO_CAST)
            # =========================================================
            if state == "READY_TO_CAST":
                sync_viewport()
                # 1. Uu tien kiem tra va giai phong nut "Nhan Ngay" truoc de khong quang can de len popup
                claim_bgr = safe_grab(sct, claim_box)
                if claim_bgr is not None:
                    c_hsv = cv2.cvtColor(claim_bgr, cv2.COLOR_BGR2HSV)
                    c_green = cv2.inRange(
                        c_hsv,
                        np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
                        np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
                    )
                    if np.count_nonzero(c_green) > 300:
                        log(f"[PHUC HOI] Phat hien nut Nhan Ngay ({np.count_nonzero(c_green)}px xanh). Tien hanh nhan thuong!")
                        state = "CLAIM_REWARD"
                        continue

                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    if sleep_check(0.5):
                        continue
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                if purple_px > config.PURPLE_PX_THRESHOLD:
                    log(f"[PHUC HOI] Ca dang can ({purple_px}px tim) -> GIAT CAN NGAY!")
                    fast_tap(btn_screen_x, btn_screen_y)
                    if sleep_check(0.35):
                        continue
                    state = "MINIGAME_SLIDER"
                    log("[3/4] Quet thanh truot...")
                    continue

                if grey_px > config.GREY_PX_THRESHOLD:
                    log(f"[PHUC HOI] Can dang duoi nuoc ({grey_px}px xam) -> Cho ca can...")
                    state = "WAITING_BITE"
                    bite_wait_start = time.time()
                    no_rod_start = 0.0
                    last_claim_check_waiting = 0.0
                    last_heartbeat = now
                    continue

                if green_px > config.GREEN_PX_THRESHOLD:
                    log(f"[1/4] Tha can ({green_px}px xanh)...")
                    touch_tap(btn_screen_x, btn_screen_y, desc="Nut quang can")
                    if sleep_check(1.5):
                        continue
                    state = "WAITING_BITE"
                    bite_wait_start = time.time()
                    no_rod_start = 0.0
                    last_claim_check_waiting = 0.0
                    last_heartbeat = time.time()
                    continue

                if now - last_heartbeat > 1.2:
                    log(f"[Cho] Xanh: {green_px} | Xam: {grey_px} | Tim: {purple_px}")
                    last_heartbeat = now

                if now - wait_ready_start > 2.5:
                    log("[GIAI PHONG] Cham giai phong the bai / popup ton du...")
                    touch_tap(card_screen_x, card_screen_y, desc="Giai phong the bai")
                    time.sleep(0.3)
                    touch_tap(claim_screen_x, claim_screen_y, desc="Giai phong Nhan Ngay")
                    if sleep_check(0.8):
                        continue
                    wait_ready_start = time.time()
                else:
                    if sleep_check(0.15):
                        continue

            # =========================================================
            # BUOC 2: CHO CA CAN CAU (WAITING_BITE)
            # =========================================================
            elif state == "WAITING_BITE":
                # 1. Kiem tra dinh ky nut Nhan Ngay (tranh ket neu popup phan thuong/ky luc hien bat ngo)
                if now - last_claim_check_waiting > 0.35:
                    last_claim_check_waiting = now
                    claim_bgr = safe_grab(sct, claim_box)
                    if claim_bgr is not None:
                        c_hsv = cv2.cvtColor(claim_bgr, cv2.COLOR_BGR2HSV)
                        c_green = cv2.inRange(
                            c_hsv,
                            np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
                            np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
                        )
                        if np.count_nonzero(c_green) > 300:
                            log(f"[PHUC HOI] Phat hien nut Nhan Ngay ({np.count_nonzero(c_green)}px xanh) khi dang cho ca can! Tien hanh nhan thuong...")
                            state = "CLAIM_REWARD"
                            continue

                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    if sleep_check(0.5):
                        continue
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                # Can chi thuc su tren bo khi nut XANH va nut XAM da bien mat han (< 300)
                if green_px > config.GREEN_PX_THRESHOLD and grey_px < 300:
                    log(f"[PHUC HOI] Can tren bo ({green_px}px xanh) -> Tha can lai!")
                    state = "READY_TO_CAST"
                    wait_ready_start = time.time()
                    continue

                if now - last_heartbeat > 2.0:
                    log(f"[2/4] Dang cho... Xam: {grey_px} | Tim: {purple_px}")
                    last_heartbeat = now

                # 2. Phat hien ca can
                if purple_px > config.PURPLE_PX_THRESHOLD:
                    log(f"[2/4] CA CAN! ({purple_px}px tim) -> GIAT CAN!")
                    fast_tap(btn_screen_x, btn_screen_y)
                    if sleep_check(0.35):
                        continue
                    state = "MINIGAME_SLIDER"
                    log("[3/4] Quet thanh truot...")
                    continue

                # 3. Kiem tra bat thuong: Khong co can duoi nuoc (Xam < 100 va Tim < 100)
                # Neu keo dai > 3s -> Co the popup phan thuong/the bai dang che hoac click tha can bi hut
                if grey_px < 100 and purple_px < 100:
                    if no_rod_start == 0.0:
                        no_rod_start = now
                    elif now - no_rod_start > 3.0:
                        log(f"[GIAI PHOI] Khong co can duoi nuoc (Xam: {grey_px}, Tim: {purple_px}) > 3s -> Tu giai thoat popup/the bai...")
                        touch_tap(card_screen_x, card_screen_y, desc="Giai phong the bai")
                        time.sleep(0.3)
                        touch_tap(claim_screen_x, claim_screen_y, desc="Giai phong Nhan Ngay")
                        state = "READY_TO_CAST"
                        wait_ready_start = time.time()
                        no_rod_start = 0.0
                        if sleep_check(0.8):
                            continue
                        continue
                else:
                    no_rod_start = 0.0

                # 4. Timeout an toan: Neu cho ca can > 18s ma van chua can -> Tu dong giai phong va tha lai can
                if now - bite_wait_start > 18.0:
                    log("[TIMEOUT] Cho ca can > 18s -> Tu dong giai phong va thu tha lai can...")
                    touch_tap(card_screen_x, card_screen_y, desc="Dong the ton du")
                    time.sleep(0.3)
                    touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay ton du")
                    state = "READY_TO_CAST"
                    wait_ready_start = time.time()
                    no_rod_start = 0.0
                    if sleep_check(0.8):
                        continue
                    continue

                if sleep_check(0.015):
                    continue

            # =========================================================
            # BUOC 3: MINI-GAME THANH TRUOT (MINIGAME_SLIDER)
            # =========================================================
            elif state == "MINIGAME_SLIDER":
                no_slider_since = 0.0
                last_hit_time = 0.0
                hit_count = 0
                minigame_start = time.time()
                last_bobber_seen = time.time()
                last_claim_check = 0.0
                prev_bobber_x = None

                # Co che 2 pha chuan:
                # 1. SEARCH_BOX: Cho game xoa hieu ung cu va sinh o vang moi -> Khoa vi tri
                # 2. WAIT_HIT: Giu nguyen toa do da khoa, cho phao do toi de click (khong so phao che khuat)
                slider_phase = "SEARCH_BOX"
                locked_yellow = None

                while True:
                    if _stop_event.is_set():
                        break

                    cur_t = time.time()

                    if cur_t - minigame_start > config.MINIGAME_MAX_DURATION:
                        log(f"[TIMEOUT] Minigame > {config.MINIGAME_MAX_DURATION}s -> Reset...")
                        state = "READY_TO_CAST"
                        wait_ready_start = time.time()
                        break

                    s_bgr = safe_grab(sct, slider_box)
                    if s_bgr is None:
                        time.sleep(0.01)
                        continue

                    yellow_range, bobber_x = detect_yellow_and_bobber(s_bgr)

                    # 1. Cap nhat thoi gian nhin thay phao do & kiem tra nut Nhan Ngay neu mat phao
                    if bobber_x is not None:
                        last_bobber_seen = cur_t
                    else:
                        # Khi khong thay phao do, kiem tra ngay nut "Nhan Ngay" da hien chua (nhu khi ca nho chi can 2 nhip)
                        if cur_t - last_claim_check > 0.12:
                            last_claim_check = cur_t
                            claim_bgr = safe_grab(sct, claim_box)
                            if claim_bgr is not None:
                                c_hsv = cv2.cvtColor(claim_bgr, cv2.COLOR_BGR2HSV)
                                c_green = cv2.inRange(
                                    c_hsv,
                                    np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
                                    np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
                                )
                                if np.count_nonzero(c_green) > 300:
                                    log(f"[3/4] Phat hien nut Nhan Ngay ({np.count_nonzero(c_green)}px xanh). Ket thuc minigame!")
                                    state = "CLAIM_REWARD"
                                    break

                    # 2. Neu minigame da chay > 0.4s ma khong he thay phao do > 0.65s -> Tran da ket thuc!
                    if (cur_t - minigame_start > 0.4) and (cur_t - last_bobber_seen > 0.65):
                        log(f"[3/4] Keo ca hoan tat ({hit_count} Hoan Hao, phao bien mat). Nhan thuong...")
                        state = "CLAIM_REWARD"
                        break

                    # 3. Kiem tra mat thanh truot
                    if yellow_range is None and locked_yellow is None:
                        if no_slider_since == 0.0:
                            no_slider_since = cur_t
                        slider_timeout = 0.35 if hit_count >= 2 else 0.85
                        if cur_t - no_slider_since > slider_timeout:
                            log(f"[3/4] Keo ca hoan tat ({hit_count} Hoan Hao). Nhan thuong...")
                            state = "CLAIM_REWARD"
                            break
                    else:
                        no_slider_since = 0.0

                    # -----------------------------------------------------------------
                    # PHA 1: SEARCH_BOX - Cho game sinh o vang moi & khoa toa do
                    # -----------------------------------------------------------------
                    if slider_phase == "SEARCH_BOX":
                        # Sau moi cu click, cho 0.20s de game xoa hieu ung Hoan Hao/tia sang cu
                        # Tuyet doi khong click trong khoang thoi gian chuyen tiep nay (tranh bi click hut tru 2s)
                        if cur_t - last_hit_time < 0.20:
                            prev_bobber_x = bobber_x
                            continue

                        # Khi het thoi gian cooldown chuyen tiep, bat dau tim o vang moi
                        if yellow_range is not None:
                            ystart, yend = yellow_range
                            y_width = yend - ystart
                            # O vang moi hop le phai co do rong >= 8px
                            if y_width >= 8:
                                locked_yellow = (ystart, yend)
                                slider_phase = "WAIT_HIT"
                                prev_bobber_x = bobber_x

                    # -----------------------------------------------------------------
                    # PHA 2: WAIT_HIT - O vang da khoa, theo doi phao do de bam Hoan Hao
                    # -----------------------------------------------------------------
                    elif slider_phase == "WAIT_HIT":
                        if locked_yellow is None:
                            slider_phase = "SEARCH_BOX"
                            continue

                        l_start, l_end = locked_yellow

                        # Neu frame hien tai quet duoc o vang o cung vi tri,
                        # cap nhat mo rong bien do de giu do rong lon nhat (tranh bi teo nho khi phao de len)
                        if yellow_range is not None:
                            c_start, c_end = yellow_range
                            c_center = (c_start + c_end) / 2
                            l_center = (l_start + l_end) / 2
                            if abs(c_center - l_center) < 30:
                                locked_yellow = (min(l_start, c_start), max(l_end, c_end))
                                l_start, l_end = locked_yellow

                        y_width = l_end - l_start

                        if bobber_x is not None:
                            # Kiem tra truc tiep: Phao nam trong o vang da khoa
                            inside = (l_start <= bobber_x <= l_end)

                            # Continuous Sweep: Quet doan duong di chuyen giua 2 frame (gioi han buoc nhay <= 35px)
                            if prev_bobber_x is not None and abs(bobber_x - prev_bobber_x) <= 35:
                                move_min = min(prev_bobber_x, bobber_x)
                                move_max = max(prev_bobber_x, bobber_x)
                                crossed = max(move_min, l_start) <= min(move_max, l_end)
                            else:
                                crossed = False

                            if inside or crossed:
                                fast_tap(btn_screen_x, btn_screen_y)
                                hit_count += 1
                                last_hit_time = cur_t
                                log(f"  -> [HOAN HAO #{hit_count}] Phao ({bobber_x}) trung o vang [{l_start}, {l_end}] (Rong: {y_width}px)")
                                # Reset ngay lap tuc de chuyen sang Pha 1 cho o vang tiep theo
                                locked_yellow = None
                                prev_bobber_x = None
                                slider_phase = "SEARCH_BOX"
                                continue

                            prev_bobber_x = bobber_x

                # Thoat minigame som do ESC
                if _stop_event.is_set():
                    continue

            # =========================================================
            # BUOC 4: NHAN QUA / DONG POPUP (CLAIM_REWARD)
            # =========================================================
            elif state == "CLAIM_REWARD":
                log("[4/4] Cho hoat anh ca (0.6s)...")
                if sleep_check(0.6):
                    continue

                # Nhip 1: Cham truc tiep vao tam the (Rel Y = 0.480) de dong the "Ky Luc Doi Moi", "Ca Moi"
                touch_tap(card_screen_x, card_screen_y, desc="Dong the ky luc (Nhip 1)")
                if sleep_check(0.35):
                    continue

                # Nhip 2: Cham nut "Nhan Ngay" (Rel Y = 0.870) cua man hinh ca thuong
                touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay (Nhip 2)")
                if sleep_check(0.35):
                    continue

                # Nhip 3: Xac nhan dong - neu nut Nhan Ngay van con thi bam tiep den khi dong han
                for retry in range(3):
                    claim_bgr = safe_grab(sct, claim_box)
                    if claim_bgr is not None:
                        c_hsv = cv2.cvtColor(claim_bgr, cv2.COLOR_BGR2HSV)
                        c_green = cv2.inRange(
                            c_hsv,
                            np.array(config.HSV_READY_GREEN_LOWER, dtype=np.uint8),
                            np.array(config.HSV_READY_GREEN_UPPER, dtype=np.uint8),
                        )
                        if np.count_nonzero(c_green) > 300:
                            log(f"  -> Popup van con ({np.count_nonzero(c_green)}px xanh), bam tiep lan {retry + 1}...")
                            touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay bo sung")
                            if sleep_check(0.35):
                                break
                        else:
                            break

                fish_count += 1
                log(f"[4/4] Nhan thuong thanh cong! Ca thu: {fish_count}")

                if sleep_check(0.4):
                    continue

                state = "READY_TO_CAST"
                wait_ready_start = time.time()
                log("=" * 30)
                log("[VONG MOI] Chuan bi tha moi...")
                last_heartbeat = time.time()

    except pyautogui.FailSafeException:
        log("\n[AN TOAN] Di chuot vao goc man hinh -> Dung bot an toan!")
    except KeyboardInterrupt:
        log("\n[AN TOAN] Ctrl+C -> Thoat bot.")
    except Exception as e:
        log(f"\n[LOI] {type(e).__name__}: {e}")
        log("[GOI Y] Hay bao loi nay cho tac gia de duoc ho tro.")
    finally:
        safe_unhook_hotkeys()
        log(f"[TONG KET] Tong so ca: {fish_count}")
        log("[KET THUC] Bot da dung.")
        if getattr(sys, "frozen", False):
            print("\nNhan Enter de dong cua so...")
            try:
                input()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[LOI KHOI DONG] {e}")
        if getattr(sys, "frozen", False):
            print("Nhan Enter de dong cua so...")
            try:
                input()
            except Exception:
                pass
