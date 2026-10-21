"""
Công cụ chụp ảnh và kiểm tra khung ngắm toạ độ trên giả lập Android.
Sử dụng cùng logic tính toán viewport với auto_cauca.py.
"""

import sys
import os
import time
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

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

# Thiết lập DPI Awareness cho Windows
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import cv2
import numpy as np
import mss
import pygetwindow as gw

import config

user32 = ctypes.windll.user32


def find_emulator_window() -> Optional[gw.Window]:
    """
    Tự động tìm kiếm cửa sổ của các giả lập Android phổ biến:
    BlueStacks, LDPlayer, NoxPlayer, MuMu Player, MEmu.
    """
    targets = ["BlueStacks", "App Player", "LDPlayer", "Nox", "MuMu", "MEmu"]
    found = []
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
    """Lấy toạ độ thực của toàn bộ cửa sổ (bao gồm cả sidebar/titlebar)."""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def get_game_viewport(hwnd: int, win_title: str) -> Tuple[int, int, int, int]:
    """
    Trả về (game_left, game_top, game_width, game_height) đã loại bỏ
    sidebar & title bar. Dùng cùng logic với auto_cauca.py để đảm bảo
    preview khớp 100% với vị trí bot thực tế.
    """
    if "ldplayer" in win_title.lower():
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
    title_lower = win_title.lower()
    for keyword, (tb, sl, sr) in config.EMULATOR_VIEWPORT_OFFSETS.items():
        if keyword in title_lower:
            title_bar_px     = tb
            sidebar_left_px  = sl
            sidebar_right_px = sr
            break
    game_left = left + sidebar_left_px
    game_top  = top  + title_bar_px
    game_w    = w    - sidebar_left_px - sidebar_right_px
    game_h    = h    - title_bar_px
    return game_left, game_top, game_w, game_h


def main():
    print("=" * 65)
    print("   KIEM TRA CAN CHINH TOA DO GIA LAP (TEST PREVIEW)")
    print("=" * 65)
    print("Đang tìm cửa sổ giả lập (BlueStacks, LDPlayer, Nox, MuMu, MEmu)...")

    win = find_emulator_window()
    if not win:
        print("\n[LỖI] Không tìm thấy cửa sổ giả lập nào đang chạy!")
        print("-> Hãy mở BlueStacks / LDPlayer và vào game trước, sau đó chạy lại.")
        return

    hwnd = win._hWnd
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    # Lấy toàn bộ cửa sổ để chụp ảnh đầy đủ
    raw_left, raw_top, raw_w, raw_h = get_window_rect(hwnd)
    # Lấy vùng game thực sự (đã trừ sidebar/titlebar) để vẽ tọa độ đúng
    game_left, game_top, game_w, game_h = get_game_viewport(hwnd, win.title)

    print(f"\n[OK] Đã kết nối với: '{win.title}'")
    print(f"[CỬA SỔ THỰC]  Left={raw_left}, Top={raw_top}, Width={raw_w}, Height={raw_h}")
    print(f"[VÙNG GAME]    Left={game_left}, Top={game_top}, Width={game_w}, Height={game_h}")
    print(f"[BÙ VIỀN]      Sidebar trái={game_left - raw_left}px | "
          f"Sidebar phải={raw_w - game_w - (game_left - raw_left)}px | "
          f"Title bar={game_top - raw_top}px")

    # Chụp toàn bộ cửa sổ (để người dùng thấy context đầy đủ kể cả sidebar)
    with mss.mss() as sct:
        monitor = {"left": raw_left, "top": raw_top, "width": raw_w, "height": raw_h}
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # Tọa độ vẽ trên ảnh = tọa độ tuyệt đối - tọa độ góc trên trái ảnh (raw_left, raw_top)
    # Vùng game trên ảnh bắt đầu tại:
    gx = game_left - raw_left   # offset ngang của vùng game trong ảnh
    gy = game_top  - raw_top    # offset dọc của vùng game trong ảnh

    # ---------------------------------------------------------------
    # 0. Vẽ khung tím bao quanh VÙNG GAME THỰC SỰ (sau khi trừ sidebar)
    # ---------------------------------------------------------------
    cv2.rectangle(img, (gx, gy), (gx + game_w, gy + game_h), (180, 0, 180), 2)
    cv2.putText(img, "VUNG GAME THUC SU",
                (gx + 4, gy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 0, 180), 1)

    # ---------------------------------------------------------------
    # 1. Tâm nút câu cá (Vòng tròn xanh lá) — tính trên vùng game
    # ---------------------------------------------------------------
    btn_x = gx + int(game_w * config.BUTTON_REL_X)
    btn_y = gy + int(game_h * config.BUTTON_REL_Y)
    cv2.circle(img, (btn_x, btn_y), 28, (0, 255, 0), 2)
    cv2.circle(img, (btn_x, btn_y), 4, (0, 255, 0), -1)
    cv2.putText(img, "NUT CAU CA",
                (btn_x - 55, btn_y - 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    # ---------------------------------------------------------------
    # 2. Khung thanh trượt minigame (Khung vàng) — tính trên vùng game
    # ---------------------------------------------------------------
    sx1 = gx + int(game_w * config.SLIDER_REL_X_MIN)
    sx2 = gx + int(game_w * config.SLIDER_REL_X_MAX)
    sy1 = gy + int(game_h * config.SLIDER_REL_Y_MIN)
    sy2 = gy + int(game_h * config.SLIDER_REL_Y_MAX)
    cv2.rectangle(img, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
    cv2.putText(img, "THANH TRUOT MINIGAME",
                (sx1, sy1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    # ---------------------------------------------------------------
    # 3. Tâm nút nhận quà (Vòng tròn đỏ) — tính trên vùng game
    # ---------------------------------------------------------------
    cx = gx + int(game_w * config.CLAIM_REL_X)
    cy = gy + int(game_h * config.CLAIM_REL_Y)
    cv2.circle(img, (cx, cy), 18, (0, 0, 255), 2)
    cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
    cv2.putText(img, "<- DIEM NHAN THUONG (AN TOAN)",
                (cx + 25, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # ---------------------------------------------------------------
    # 3b. Tâm đóng thẻ kỷ lục (Vòng tròn xanh dương)
    # ---------------------------------------------------------------
    card_x = gx + int(game_w * config.CARD_REL_X)
    card_y = gy + int(game_h * config.CARD_REL_Y)
    cv2.circle(img, (card_x, card_y), 18, (255, 120, 0), 2)
    cv2.circle(img, (card_x, card_y), 3, (255, 120, 0), -1)
    cv2.putText(img, "<- DIEM DONG THE KY LUC / CA MOI",
                (card_x + 25, card_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 120, 0), 2)

    # ---------------------------------------------------------------
    # 4. Vạch cảnh báo nút X (tính trên vùng game)
    # ---------------------------------------------------------------
    danger_y = gy + int(game_h * 0.950)
    cv2.line(img, (gx + 20, danger_y), (gx + game_w - 20, danger_y),
             (0, 165, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "[CANH BAO] NUT X THOAT GAME TAI DAY (BOT DA NE TRANH)",
                (gx + 30, danger_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1)

    output_path = "preview_can_chinh.png"
    cv2.imwrite(output_path, img)
    print(f"\n[THÀNH CÔNG] Đã xuất ảnh kiểm tra: {os.path.abspath(output_path)}")
    print("-> Đang tự động mở ảnh để bạn xem trước...")
    print()
    print("HƯỚNG DẪN ĐỌC ẢNH:")
    print("  - Khung TÍM      : Vùng game thực sự (đã loại bỏ sidebar/titlebar)")
    print("  - Vòng XANH LÁ   : Tâm nút câu cá -> Phải nằm đúng trên nút trong game")
    print("  - Khung VÀNG     : Vùng quét thanh trượt minigame")
    print("  - Vòng ĐỎ        : Vị trí bấm Nhận Ngay (cách xa nút X)")
    print("  - Vạch CAM       : Vị trí nút X nguy hiểm (bot né an toàn)")

    try:
        os.startfile(output_path)
    except Exception:
        pass


if __name__ == "__main__":
    main()

