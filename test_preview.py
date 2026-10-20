"""
CÔNG CỤ KIỂM TRA & CĂN CHỈNH TOẠ ĐỘ TRỰC QUAN (TEST PREVIEW)
Hỗ trợ: BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.

Công dụng:
- Chụp ảnh màn hình cửa sổ giả lập hiện tại.
- Vẽ các khung nhận diện:
  + VÒNG TRÒN XANH LÁ: Vị trí tâm nút câu cá (Trên bờ / Dưới nước / Cá cắn).
  + KHUNG CHỮ NHẬT VÀNG: Vị trí thanh trượt mini-game câu cá.
  + VÒNG TRÒN ĐỎ: Vị trí bấm nút Nhận Ngay (Rel Y = 0.870) an toàn.
  + ĐƯỜNG KẺ GẠCH ĐỎ (Y = 0.950): Vị trí nút X thoát game (Đã né tránh an toàn 100%).
- Tự động mở ảnh xem trước ngay lập tức để người dùng kiểm tra bằng mắt trong 5 giây.
"""

import sys
import os
import time
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

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


def main():
    print("=" * 65)
    print("   🔍 KIỂM TRA CĂN CHỈNH TOẠ ĐỘ GIẢ LẬP (TEST PREVIEW)")
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

    left, top, w, h = get_window_rect(hwnd)
    print(f"\n[OK] Đã kết nối với: '{win.title}'")
    print(f"[THÔNG SỐ] Left={left}, Top={top}, Width={w}, Height={h}")

    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": w, "height": h}
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 1. Tâm nút câu cá (Vòng tròn xanh lá)
    btn_x = int(w * config.BUTTON_REL_X)
    btn_y = int(h * config.BUTTON_REL_Y)
    cv2.circle(img, (btn_x, btn_y), 28, (0, 255, 0), 2)
    cv2.circle(img, (btn_x, btn_y), 4, (0, 255, 0), -1)
    cv2.putText(
        img,
        "NUT CAU CA",
        (btn_x - 55, btn_y - 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2,
    )

    # 2. Khung thanh trượt minigame (Khung vàng)
    sx1 = int(w * config.SLIDER_REL_X_MIN)
    sx2 = int(w * config.SLIDER_REL_X_MAX)
    sy1 = int(h * config.SLIDER_REL_Y_MIN)
    sy2 = int(h * config.SLIDER_REL_Y_MAX)
    cv2.rectangle(img, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
    cv2.putText(
        img,
        "THANH TRUOT MINIGAME",
        (sx1, sy1 - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
    )

    # 3. Tâm nút nhận quà (Vòng tròn đỏ)
    cx = int(w * config.CLAIM_REL_X)
    cy = int(h * config.CLAIM_REL_Y)
    cv2.circle(img, (cx, cy), 18, (0, 0, 255), 2)
    cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)
    cv2.putText(
        img,
        "<- DIEM NHAN THUONG (AN TOAN)",
        (cx + 25, cy + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2,
    )

    # 4. Vạch cảnh báo nút X (Tuyệt đối né tránh)
    danger_y = int(h * 0.950)
    cv2.line(img, (20, danger_y), (w - 20, danger_y), (0, 165, 255), 1, cv2.LINE_AA)
    cv2.putText(
        img,
        "[CANH BAO] NUT X THOAT GAME TAI DAY (BOT DA NE TRANH)",
        (30, danger_y - 6),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 165, 255),
        1,
    )

    output_path = "preview_can_chinh.png"
    cv2.imwrite(output_path, img)
    print(f"\n[THÀNH CÔNG] Đã xuất ảnh kiểm tra: {os.path.abspath(output_path)}")
    print("-> Đang tự động mở ảnh để bạn xem trước...")

    # Tự động mở ảnh xem trước bằng trình xem ảnh mặc định của Windows
    try:
        os.startfile(output_path)
    except Exception:
        pass


if __name__ == "__main__":
    main()
