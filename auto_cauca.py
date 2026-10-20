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
4. Nhan Q de BAT auto | Nhan ESC de DUNG auto ngay lap tuc.
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

# Event dung bot - set() khi nguoi dung nhan ESC
_stop_event = threading.Event()


def log(msg: str) -> None:
    """In log kem moc thoi gian thuc."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


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


def find_emulator_window() -> Optional[gw.Window]:
    """
    Tim kiem cua so cua cac gia lap Android pho bien.
    Canh bao neu phat hien nhieu cua so gia lap cung luc.
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
                    if width > 250 and height > 400:
                        found.append(w)
                        break
    except Exception:
        pass

    if len(found) > 1:
        log(f"[CANH BAO] Phat hien {len(found)} cua so gia lap dang chay!")
        log(f"[CANH BAO] Bot dung cua so dau tien: '{found[0].title}'")
        log("[CANH BAO] De dung cua so khac, hay dong bot cac gia lap con lai.")
    if found:
        return found[0]

    for t in targets:
        try:
            wins = gw.getWindowsWithTitle(t)
            if wins:
                return wins[0]
        except Exception:
            pass

    return None


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Lay toa do thuc cua cua so: left, top, width, height."""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def get_game_viewport(hwnd: int, win_title: str) -> Tuple[int, int, int, int]:
    """
    Tinh toa do vung hien thi game thuc te (game_left, game_top, game_width, game_height)
    sau khi tru thanh tieu de va thanh cong cu cua tung gia lap.
    """
    left, top, w, h = get_window_rect(hwnd)
    title_bar_px, sidebar_left_px, sidebar_right_px = 0, 0, 0
    title_lower = win_title.lower()
    for keyword, (tb, sl, sr) in config.EMULATOR_VIEWPORT_OFFSETS.items():
        if keyword in title_lower:
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
    """Cham cam ung giu 70ms mo phong ngon tay nguoi bam tren Android."""
    if desc:
        log(f"-> {desc} ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0.02)
    pyautogui.mouseDown(x, y)
    time.sleep(0.07)
    pyautogui.mouseUp(x, y)


def rapid_tap(x: int, y: int) -> None:
    """Bam sieu toc phan xa mili-giay cho thanh truot va giat can."""
    pyautogui.mouseDown(x, y)
    time.sleep(0.04)
    pyautogui.mouseUp(x, y)


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


def detect_yellow_and_bobber(roi_img: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
    """
    Quet o vang muc tieu va phao do tren thanh truot mini-game.
    Loai tru truong hop chu 'Hoan hao!' loe sang lam mo rong dai vang qua muc (> 130px).
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

    if yellow_width > config.YELLOW_MAX_WIDTH:
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
    print("=" * 50)
    print("   COC-AUTOFISHING V12.1")
    print("=" * 50)
    print("Ho tro: BlueStacks 5, LDPlayer 9, Nox, MuMu, MEmu")
    print("[PHIM TAT] Q = BAT AUTO | ESC = DUNG AUTO")
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

    left, top, w, h = get_game_viewport(hwnd, win.title)
    log(f"[KET NOI] '{win.title}' | Game: {w}x{h} tai ({left}, {top})")

    btn_screen_x = int(left + w * config.BUTTON_REL_X)
    btn_screen_y = int(top + h * config.BUTTON_REL_Y)

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

    # Dam bao Q va Space da duoc nha truoc khi vao che do cho
    while keyboard.is_pressed("q") or keyboard.is_pressed("space"):
        time.sleep(0.05)

    print("-" * 50)
    log("[CHO LENH] Mo su kien Cau ca tren gia lap.")
    log("[CHO LENH] Nhan Q (hoac Space) de bat dau...")
    print("-" * 50)

    # Cho nguoi dung nhan Q hoac Space de bat dau
    while True:
        if keyboard.is_pressed("q") or keyboard.is_pressed("space"):
            break
        if keyboard.is_pressed("esc"):
            log("[THOAT] Nguoi dung nhan ESC.")
            return
        time.sleep(0.05)

    # Debounce: doi nha phim hoan toan truoc khi vao vong lap chinh
    while keyboard.is_pressed("q") or keyboard.is_pressed("space"):
        time.sleep(0.05)
    time.sleep(0.3)

    # Dang ky ESC de dung bot ngay lap tuc (chay tren luong nen)
    _stop_event.clear()
    keyboard.add_hotkey("esc", _stop_event.set, suppress=True)

    log("[KHOI DONG] Auto bat dau!")
    log("Nhan ESC bat cu luc nao de dung.\n")

    try:
        while True:
            # Kiem tra lenh dung tu ESC
            if _stop_event.is_set():
                log(f"\n[DUNG] Da dung auto.")
                break

            now = time.time()

            # =========================================================
            # BUOC 1: CHUAN BI QUANG CAN (READY_TO_CAST)
            # =========================================================
            if state == "READY_TO_CAST":
                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    if sleep_check(0.5):
                        break
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                if purple_px > config.PURPLE_PX_THRESHOLD:
                    log(f"[PHUC HOI] Ca dang can ({purple_px}px tim) -> GIAT CAN NGAY!")
                    rapid_tap(btn_screen_x, btn_screen_y)
                    if sleep_check(0.35):
                        break
                    state = "MINIGAME_SLIDER"
                    log("[3/4] Quet thanh truot...")
                    continue

                if grey_px > config.GREY_PX_THRESHOLD:
                    log(f"[PHUC HOI] Can dang duoi nuoc ({grey_px}px xam) -> Cho ca can...")
                    state = "WAITING_BITE"
                    last_heartbeat = now
                    continue

                if green_px > config.GREEN_PX_THRESHOLD:
                    log(f"[1/4] Tha can ({green_px}px xanh)...")
                    touch_tap(btn_screen_x, btn_screen_y, desc="Nut quang can")
                    if sleep_check(1.2):
                        break

                    c_bgr = safe_grab(sct, btn_box)
                    if c_bgr is not None:
                        c_green, c_grey, _ = analyze_button_colors(c_bgr)
                        if c_green < 250 and c_grey > 300:
                            log("[2/4] Can xuong nuoc. Cho ca can...")
                            state = "WAITING_BITE"
                            last_heartbeat = time.time()
                        else:
                            log("[THU LAI] Nut van xanh -> Thu lai...")
                            if sleep_check(0.2):
                                break
                    continue

                if now - last_heartbeat > 1.2:
                    log(f"[Cho] Xanh: {green_px} | Xam: {grey_px} | Tim: {purple_px}")
                    last_heartbeat = now

                if now - wait_ready_start > 2.5:
                    log("[GIAI PHONG] Cham vi tri Nhan Ngay de giai phong popup...")
                    touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay (giai phong)")
                    if sleep_check(0.8):
                        break
                    wait_ready_start = time.time()
                else:
                    if sleep_check(0.15):
                        break

            # =========================================================
            # BUOC 2: CHO CA CAN CAU (WAITING_BITE)
            # =========================================================
            elif state == "WAITING_BITE":
                bgr = safe_grab(sct, btn_box)
                if bgr is None:
                    if sleep_check(0.5):
                        break
                    continue
                green_px, grey_px, purple_px = analyze_button_colors(bgr)

                if green_px > config.GREEN_PX_THRESHOLD:
                    log(f"[PHUC HOI] Can tren bo ({green_px}px xanh) -> Tha can lai!")
                    state = "READY_TO_CAST"
                    wait_ready_start = time.time()
                    continue

                if now - last_heartbeat > 2.0:
                    log(f"[2/4] Dang cho... Xam: {grey_px} | Tim: {purple_px}")
                    last_heartbeat = now

                if purple_px > config.PURPLE_PX_THRESHOLD:
                    log(f"[2/4] CA CAN! ({purple_px}px tim) -> GIAT CAN!")
                    rapid_tap(btn_screen_x, btn_screen_y)
                    if sleep_check(0.35):
                        break
                    state = "MINIGAME_SLIDER"
                    log("[3/4] Quet thanh truot...")
                else:
                    if sleep_check(0.015):
                        break

            # =========================================================
            # BUOC 3: MINI-GAME THANH TRUOT (MINIGAME_SLIDER)
            # =========================================================
            elif state == "MINIGAME_SLIDER":
                no_slider_since = 0.0
                last_hit_time = 0.0
                hit_count = 0
                minigame_start = time.time()

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
                        time.sleep(0.05)
                        continue

                    yellow_range, bobber_x = detect_yellow_and_bobber(s_bgr)

                    if yellow_range is None:
                        b_bgr = safe_grab(sct, btn_box)
                        if b_bgr is None:
                            time.sleep(0.05)
                            continue
                        _, _, purple_px = analyze_button_colors(b_bgr)

                        if purple_px > config.PURPLE_PX_THRESHOLD:
                            no_slider_since = 0.0
                            time.sleep(0.01)
                            continue
                        else:
                            if no_slider_since == 0.0:
                                no_slider_since = cur_t
                            if cur_t - no_slider_since > 0.8:
                                log(f"[3/4] Keo ca hoan tat ({hit_count} Hoan Hao). Nhan thuong...")
                                state = "CLAIM_REWARD"
                                break
                            time.sleep(0.015)
                            continue
                    else:
                        no_slider_since = 0.0

                    if bobber_x is not None:
                        ystart, yend = yellow_range
                        if (ystart - 5) <= bobber_x <= (yend + 5):
                            if cur_t - last_hit_time > 0.16:
                                rapid_tap(btn_screen_x, btn_screen_y)
                                hit_count += 1
                                log(f"  -> [HOAN HAO #{hit_count}] Phao ({bobber_x}) trung o vang [{ystart}, {yend}]")
                                last_hit_time = cur_t

                # Thoat minigame som do ESC
                if _stop_event.is_set():
                    log(f"\n[DUNG] Da dung auto.")
                    break

            # =========================================================
            # BUOC 4: NHAN QUA / DONG POPUP (CLAIM_REWARD)
            # =========================================================
            elif state == "CLAIM_REWARD":
                log("[4/4] Cho hoat anh ca (1.6s)...")
                if sleep_check(1.6):
                    break

                touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay (Nhip 1)")

                if sleep_check(0.9):
                    break

                touch_tap(claim_screen_x, claim_screen_y, desc="Nhan Ngay (Nhip 2)")

                fish_count += 1
                log(f"[4/4] Nhan thuong thanh cong! Ca thu: {fish_count}")

                if sleep_check(1.0):
                    break

                state = "READY_TO_CAST"
                wait_ready_start = time.time()
                log("=" * 30)
                log("[VONG MOI] Chuan bi thả moi...")
                last_heartbeat = time.time()

    except pyautogui.FailSafeException:
        log("\n[AN TOAN] Di chuot vao goc man hinh -> Dung bot an toan!")
    except KeyboardInterrupt:
        log("\n[AN TOAN] Ctrl+C -> Thoat bot.")
    except Exception as e:
        log(f"\n[LOI] {type(e).__name__}: {e}")
        log("[GOI Y] Hay bao loi nay cho tac gia de duoc ho tro.")
    finally:
        keyboard.remove_all_hotkeys()
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
