"""
Script kiểm tra vị trí nhận diện trên cửa sổ BlueStacks.
Đã thu nhỏ tâm điểm và dời chữ để bạn thấy rõ khoảng cách an toàn với nút X.
"""

import ctypes
from ctypes import wintypes
import time
import cv2
import numpy as np
import mss
import pygetwindow as gw
import config

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

user32 = ctypes.windll.user32

def find_bluestacks_window():
    windows = gw.getWindowsWithTitle("BlueStacks")
    if not windows:
        windows = gw.getWindowsWithTitle("App Player")
    if windows:
        return windows[0]
    return None

def get_window_rect(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top

def main():
    print("Đang tìm cửa sổ BlueStacks...")
    win = find_bluestacks_window()
    if not win:
        print("[LỖI] Không tìm thấy cửa sổ BlueStacks. Vui lòng mở game trước!")
        return

    hwnd = win._hWnd
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    left, top, w, h = get_window_rect(hwnd)
    print(f"[OK] Cửa sổ: '{win.title}'")
    print(f"Toạ độ thực: Left={left}, Top={top}, Width={w}, Height={h}")

    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": w, "height": h}
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 1. Tâm nút câu cá (Điểm xanh)
    btn_x = int(w * config.BUTTON_REL_X)
    btn_y = int(h * config.BUTTON_REL_Y)
    cv2.circle(img, (btn_x, btn_y), 25, (0, 255, 0), 2)
    cv2.circle(img, (btn_x, btn_y), 3, (0, 255, 0), -1)  # Chấm tâm
    cv2.putText(img, "NUT CAU CA", (btn_x - 55, btn_y - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    # 2. Khung thanh trượt (Khung vàng)
    sx1 = int(w * config.SLIDER_REL_X_MIN)
    sx2 = int(w * config.SLIDER_REL_X_MAX)
    sy1 = int(h * config.SLIDER_REL_Y_MIN)
    sy2 = int(h * config.SLIDER_REL_Y_MAX)
    cv2.rectangle(img, (sx1, sy1), (sx2, sy2), (0, 255, 255), 2)
    cv2.putText(img, "THANH TRUOT", (sx1, sy1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    # 3. Tâm nút nhận quà (Thu nhỏ lại thành điểm ngắm chính xác, không đè nút X)
    cx = int(w * config.CLAIM_REL_X)
    cy = int(h * config.CLAIM_REL_Y)
    # Vẽ chấm tròn nhỏ gọn (bán kính 15px)
    cv2.circle(img, (cx, cy), 15, (0, 0, 255), 2)
    cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)  # Chấm tâm
    # Dời nhãn chữ sang bên PHẢI để KHÔNG che nút X ở dưới
    cv2.putText(img, "<- DIEM NHAN QUA", (cx + 25, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    output_path = "preview_bluestacks.png"
    cv2.imwrite(output_path, img)
    print(f"\n[THÀNH CÔNG] Đã lưu ảnh kiểm tra: {output_path}")

if __name__ == "__main__":
    main()
