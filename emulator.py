"""
Mô-đun giao tiếp và điều khiển giả lập Android trên Windows (Win32 API).
Hỗ trợ: BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu.
"""

import sys
import os
import time
import threading
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple, Any

import cv2
import numpy as np
import mss
import pyautogui
import pygetwindow as gw
import keyboard

import config

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True


def setup_windows_environment() -> None:
    """Thiết lập môi trường UTF-8, DPI-awareness và tắt QuickEdit console."""
    if sys.platform.startswith("win"):
        try:
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # DPI Awareness: Đọc toạ độ 1:1 chuẩn xác trên màn hình Windows
    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            user32.SetProcessDPIAware()

    # Tắt QuickEdit của Windows Console để chuột click không làm treo tiến trình
    try:
        h_stdin = kernel32.GetStdHandle(-10)
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode)):
            new_mode = (mode.value & ~0x0040) | 0x0080
            kernel32.SetConsoleMode(h_stdin, new_mode)
    except Exception:
        pass


def log(msg: str) -> None:
    """In thông báo log kèm mốc thời gian thực."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def safe_unhook_hotkeys() -> None:
    """Gỡ bỏ an toàn tất cả hotkey khi tắt chương trình."""
    try:
        if hasattr(keyboard, "_listener") and hasattr(keyboard._listener, "blocking_hotkeys"):
            keyboard.remove_all_hotkeys()
    except Exception:
        pass


def sleep_check(seconds: float, stop_event: threading.Event) -> bool:
    """
    Nghỉ trong `seconds` giây.
    Trả về True ngay lập tức nếu phím ESC (stop_event) được nhấn để thoát sớm.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if stop_event.is_set():
            return True
        time.sleep(0.02)
    return False


EMULATOR_PROCESS_KEYWORDS = [
    "nemuplayer", "mumuplayer", "mumu", "nemu",      # MuMu Player
    "hd-player", "bluestacks",                        # BlueStacks 5
    "dnplayer", "ldplayer", "ldboxplayer",            # LDPlayer
    "nox",                                            # NoxPlayer
    "memu",                                           # MEmu
]

EMULATOR_TITLE_KEYWORDS = [
    "bluestacks", "app player",
    "ldplayer",
    "nox",
    "mumu", "nemu",
    "memu",
    "clash of critters", "critters", "coc",
]


def get_process_name_by_hwnd(hwnd: int) -> str:
    """Lấy tên file thực thi (.exe) của tiến trình sở hữu cửa sổ."""
    try:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""
        h_proc = kernel32.OpenProcess(0x1000, False, pid.value)
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
    Tìm kiếm cửa sổ của các trình giả lập Android phổ biến đang mở.
    Ưu tiên 1: Cửa sổ giả lập đang được người dùng click/focus (Foreground Window).
    Ưu tiên 2: Cửa sổ có diện tích hiển thị lớn nhất và đang hiển thị trên màn hình.
    """
    candidates = []
    fore_hwnd = user32.GetForegroundWindow()
    try:
        for w in gw.getAllWindows():
            hwnd = w._hWnd
            if user32.IsIconic(hwnd):
                continue

            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            left = rect.left
            top = rect.top
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            if left < -10000 or top < -10000:
                continue

            if (width < 250 or height < 350) and (height < 250 or width < 350):
                continue

            title = (w.title or "").strip()
            title_lower = title.lower()
            proc_name = get_process_name_by_hwnd(hwnd)

            title_matched = any(k in title_lower for k in EMULATOR_TITLE_KEYWORDS)
            proc_matched = any(k in proc_name for k in EMULATOR_PROCESS_KEYWORDS)

            if title_matched or proc_matched:
                area = width * height
                is_foreground = 1 if (hwnd == fore_hwnd) else 0
                candidates.append((is_foreground, area, w, proc_name, title))
    except Exception:
        pass

    if not candidates:
        return None

    # Sắp xếp: Ưu tiên Foreground Window (đang click), sau đó đến diện tích lớn nhất
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if len(candidates) > 1:
        titles_str = ", ".join([f"'{c[4]}' ({c[3]})" for c in candidates])
        chosen = candidates[0]
        status_note = " (Dang Focus)" if chosen[0] == 1 else ""
        log(f"[PHAT HIEN {len(candidates)} GIA LAP] Danh sach: [{titles_str}] -> Uu tien: '{chosen[4]}'{status_note}")

    return candidates[0][2]


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """
    Lấy tọa độ thực (Physical Screen Pixels) của cửa sổ: left, top, width, height.
    Ưu tiên DwmGetWindowAttribute (DWMWA_EXTENDED_FRAME_BOUNDS = 9) để đạt độ chính xác 100%
    trên mọi màn hình (Multi-monitor, 100%, 125%, 150% DPI), loại bỏ hoàn toàn sai số ảo hoá DPI.
    """
    rect = wintypes.RECT()
    try:
        hr = ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect)  # 9 = DWMWA_EXTENDED_FRAME_BOUNDS
        )
        if hr == 0 and (rect.right - rect.left) > 100 and (rect.bottom - rect.top) > 100:
            return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
    except Exception:
        pass

    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def get_game_viewport(hwnd: int, win_title: str) -> Tuple[int, int, int, int]:
    """
    Tính tọa độ vùng hiển thị game thực tế sau khi trừ thanh tiêu đề và thanh công cụ.
    Tự động tìm kiếm RenderWindow của LDPlayer để đạt độ chuẩn xác 100%.
    """
    proc_name = get_process_name_by_hwnd(hwnd)
    title_lower = win_title.lower()

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

    # Tu dong can chinh ti le vien offset neu cua so phong to / thu nho hoac DPI > 100%
    if w > 480 or h > 820:
        scale = max(w / 443.0, h / 761.0)
        tb_adj = int(title_bar_px * scale)
        sl_adj = int(sidebar_left_px * scale)
        sr_adj = int(sidebar_right_px * scale)
        game_left = left + sl_adj
        game_top = top + tb_adj
        game_w = w - sl_adj - sr_adj
        game_h = h - tb_adj

    return game_left, game_top, game_w, game_h


def safe_grab(sct: Any, region: dict) -> Optional[np.ndarray]:
    """Chụp ảnh một vùng màn hình từ VRAM vào RAM dạng mảng BGR."""
    try:
        raw = sct.grab(region)
        if raw is None:
            return None
        img = np.array(raw)
        if img.size == 0:
            return None
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    except Exception as e:
        log(f"[CANH BAO] Loi chup man hinh ({e}).")
        time.sleep(0.3)
        return None


def grab_roi(
    sct: Any,
    gw_box: dict,
    rel_x1: float,
    rel_y1: float,
    rel_x2: float,
    rel_y2: float,
) -> Tuple[Optional[np.ndarray], Tuple[int, int, int, int]]:
    """
    Chụp một vùng ảnh theo tỉ lệ tương đối (RelX, RelY) của Game Viewport.
    Trả về: (ảnh BGR hoặc None, (abs_x1, abs_y1, width, height)).
    """
    gw_left = gw_box["left"]
    gw_top = gw_box["top"]
    gw_w = gw_box["width"]
    gw_h = gw_box["height"]

    abs_x1 = int(gw_left + gw_w * rel_x1)
    abs_y1 = int(gw_top + gw_h * rel_y1)
    abs_x2 = int(gw_left + gw_w * rel_x2)
    abs_y2 = int(gw_top + gw_h * rel_y2)
    width = max(1, abs_x2 - abs_x1)
    height = max(1, abs_y2 - abs_y1)

    crop = safe_grab(sct, {"left": abs_x1, "top": abs_y1, "width": width, "height": height})
    return crop, (abs_x1, abs_y1, width, height)


def activate_window(hwnd: int) -> None:
    """Kích hoạt và đưa cửa sổ giả lập lên phía trước để nhận tương tác mượt mà."""
    try:
        if hwnd and user32.GetForegroundWindow() != hwnd:
            cur_tid = kernel32.GetCurrentThreadId()
            fore_hwnd = user32.GetForegroundWindow()
            fore_tid = user32.GetWindowThreadProcessId(fore_hwnd, None)
            if fore_tid and fore_tid != cur_tid:
                user32.AttachThreadInput(cur_tid, fore_tid, True)
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(cur_tid, fore_tid, False)
            else:
                user32.ShowWindow(hwnd, 9)
                user32.SetForegroundWindow(hwnd)
            time.sleep(0.04)
    except Exception:
        pass


def touch_tap(x: int, y: int, desc: str = "", hold_sec: float = 0.08, restore_cursor: bool = True) -> None:
    """
    Mô phỏng thao tác chạm cảm ứng Android trực tiếp qua Win32 API.
    Hỗ trợ 2 màn hình: tự động lưu và trả chuột về vị trí cũ trên màn hình chính
    để người dùng tiếp tục lướt web/xem video mà không bị giật chuột.
    """
    x, y = int(x), int(y)
    if desc:
        log(f"-> {desc} ({x}, {y})")

    orig_pt = wintypes.POINT()
    saved = False
    if restore_cursor:
        try:
            user32.GetCursorPos(ctypes.byref(orig_pt))
            saved = True
        except Exception:
            pass

    user32.SetCursorPos(x, y)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    time.sleep(hold_sec)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP

    if saved and (orig_pt.x != x or orig_pt.y != y):
        time.sleep(0.02)
        user32.SetCursorPos(orig_pt.x, orig_pt.y)
