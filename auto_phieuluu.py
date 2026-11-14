"""
COC-autophieuluu: Bot tu dong di su kien Phieu Luu Co Vat (Relic Adventure)
cho game Clash of Critters tren cac trinh gia lap Android (BlueStacks 5, LDPlayer 9, MuMu, Nox, MEmu).

Co che hoat dong (chuan 100% tuong tu auto_cauca):
1. Khoi dong an toan:
   - Khi mo tool se o trang thai [CHO LENH] / [TAM DUNG].
   - Nhan [Ctrl + Q] de BAT DAU / TIEP TUC (Resume).
   - Nhan [ESC] khi dang chay de TAM DUNG ngay lap tuc (Pause) va giai phong chuot.
   - Nhan [ESC] khi dang tam dung de THOAT HAN chuong trinh.
2. Quet FLEX da ti le & da tang (Multi-scale Flex Matching):
   - Tu dong quet ti le cua so thuc te (ho tro moi kich co to/nho, 720p/1080p).
   - Tich hop phan tich dải màu HSV contour du phong de khong bao gio bo sot nut 'Tien Len'.
   - Bấm trực tiếp vào tâm nút thực tế (Flex Click) thay vì toạ độ cố định.
3. Quy trinh su kien:
   - Sảnh chính: Tự tìm nút và bấm 'Bắt Đầu Phiêu Lưu!'.
   - Trong mê cung: Tự tìm nút 'Tiến Lên', bấm và chờ 2.0s hoạt ảnh bước đi.
   - Nhận bảo vật (Tier thấp/cao): Chờ đúng 1.0s timing hoạt ảnh rồi mới chạm đóng popup.
   - Gặp quái vật: Luôn luôn chọn 'Chiến Đấu' (bỏ qua tỉ lệ thắng/thua).
   - Kết toán thất bại: Bấm 'Chấp Nhận', chờ 2.0s thoát ra sảnh chính và lặp lại từ đầu.
4. Chống chiếm chuột:
   - Chỉ chạm chuột ~0.08s rồi ngay lập tức hoàn trả con trỏ chuột về toạ độ cũ để bạn thoải mái lướt web.
5. Chống treo (Watchdog):
   - Tự động chạm an toàn giải phóng màn hình nếu kẹt lạ quá 3.5s.
   - Tự động kích hoạt lại cửa sổ nếu mất tiêu điểm quá 8s.
"""

import sys
import os
import time
import threading
from typing import Optional, Tuple, Dict, Any

import cv2
import numpy as np
import mss
import pyautogui
import keyboard

import config
import assets
from emulator import (
    setup_windows_environment,
    log,
    safe_unhook_hotkeys,
    sleep_check,
    find_emulator_window,
    get_game_viewport,
    safe_grab,
    touch_tap,
    activate_window,
    user32,
)

# Thiet lap Windows Console & DPI Awareness
setup_windows_environment()

# Quan ly trang thai (Khoi tao o che do tam dung, giong auto_cauca)
_stop_event = threading.Event()
_stop_event.set()

# Thong ke hoat dong
_stats = {
    "runs_started": 0,
    "advances": 0,
    "relics_collected": 0,
    "fights": 0,
    "settlements": 0,
    "start_time": time.time(),
}

# Cache template da giai ma trong RAM
_templates: Optional[Dict[str, np.ndarray]] = None

# Viewport hieu dung
_effective_vp: Optional[Tuple[int, int, int, int]] = None
_last_raw_vp: Optional[Tuple[int, int, int, int]] = None
_last_pillarbox_check: float = 0.0


def detect_pillarbox(crop: np.ndarray, black_thresh: Optional[float] = None, min_margin: Optional[int] = None) -> Tuple[int, int]:
    """
    Xac dinh do rong dai den (pillarbox) hai ben mep neu cua so bi keo dan ngang.
    Tra ve: (offset_x, real_w) tinh theo pixel trong crop.
    """
    if crop is None or crop.size == 0:
        return 0, 0
    if black_thresh is None:
        black_thresh = getattr(config, "PILLARBOX_BLACK_THRESHOLD", 12.0)
    if min_margin is None:
        min_margin = getattr(config, "PILLARBOX_MIN_MARGIN", 15)

    h, w = crop.shape[:2]
    mid_crop = crop[int(h * 0.20):int(h * 0.80), :]
    gray = cv2.cvtColor(mid_crop, cv2.COLOR_BGR2GRAY)
    col_means = np.mean(gray, axis=0)
    is_black = (col_means <= black_thresh)

    import itertools
    runs = []
    idx = 0
    for is_b, g in itertools.groupby(is_black):
        count = len(list(g))
        runs.append((bool(is_b), idx, idx + count - 1, count))
        idx += count

    left_black_end = 0
    for is_b, start_c, end_c, count in runs:
        if is_b and count >= min_margin and start_c < w * 0.45:
            left_black_end = end_c + 1

    right_black_start = w
    for is_b, start_c, end_c, count in runs[::-1]:
        if is_b and count >= min_margin and end_c > w * 0.55:
            right_black_start = start_c

    offset_x = left_black_end
    real_w = max(10, right_black_start - left_black_end)
    return offset_x, real_w


def get_effective_viewport(sct: Any, raw_vp: Tuple[int, int, int, int], force_check: bool = False) -> Tuple[int, int, int, int]:
    """
    Lay toa do viewport thuc te cua game sau khi loai tru dai den hai ben suon.
    Tu dong do lai neu kich thuoc hoac vi tri cua so thay doi.
    """
    global _effective_vp, _last_raw_vp, _last_pillarbox_check
    now = time.time()
    if not force_check and _effective_vp is not None and raw_vp == _last_raw_vp and (now - _last_pillarbox_check < 4.0):
        return _effective_vp

    gw_l, gw_t, gw_w, gw_h = raw_vp
    _last_raw_vp = raw_vp
    _last_pillarbox_check = now

    sample_y = int(gw_t + gw_h * 0.35)
    sample_h = max(10, int(gw_h * 0.30))
    sample = safe_grab(sct, {"left": gw_l, "top": sample_y, "width": gw_w, "height": sample_h})
    if sample is None:
        _effective_vp = raw_vp
        return raw_vp

    offset_x, real_w = detect_pillarbox(sample)
    if offset_x > 0 or real_w < gw_w:
        _effective_vp = (gw_l + offset_x, gw_t, real_w, gw_h)
    else:
        _effective_vp = raw_vp
    return _effective_vp


def _sleep(seconds: float) -> bool:
    """Tam dung co the huy lap tuc bang ESC hoac _stop_event."""
    return sleep_check(seconds, _stop_event)


def load_templates() -> Dict[str, np.ndarray]:
    """Nap va cache cac template goc tu assets."""
    global _templates
    if _templates is None:
        _templates = assets.get_phieuluu_templates()
    return _templates


def find_template_flex(
    gray_vp: np.ndarray,
    tpl: np.ndarray,
    roi_rel: Tuple[float, float, float, float],
    thresh: float = 0.68,
) -> Optional[Tuple[float, Tuple[int, int, int, int]]]:
    """
    Quet FLEX da ti le tim template trong vung ROI tuong doi cua Game Viewport:
    - roi_rel: (x1_ratio, y1_ratio, x2_ratio, y2_ratio)
    - Tu dong quet qua cac ti le co dan quanh ti le thuc cua man hinh.
    Tra ve: (best_score, (center_x, center_y, box_w, box_h)) hoac None neu khong tim thay.
    """
    if gray_vp is None or tpl is None:
        return None

    if len(tpl.shape) == 3:
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
    else:
        tpl_gray = tpl

    vh, vw = gray_vp.shape[:2]
    rx1 = int(vw * roi_rel[0])
    ry1 = int(vh * roi_rel[1])
    rx2 = int(vw * roi_rel[2])
    ry2 = int(vh * roi_rel[3])

    sub = gray_vp[ry1:ry2, rx1:rx2]
    if sub.shape[0] < 15 or sub.shape[1] < 15:
        return None

    # Ti le co dan uoc tinh theo chieu rong chuan (405px)
    est_scale = vw / 405.0
    fine_factors = [1.0, 0.96, 1.04, 0.92, 1.08, 0.88, 1.12, 0.84, 1.16, 0.80, 1.22, 1.30, 0.70, 1.40]
    scales = []
    seen = set()
    for sc in [1.0] + [est_scale * f for f in fine_factors]:
        sc_r = round(sc, 3)
        if 0.35 <= sc_r <= 2.5 and sc_r not in seen:
            seen.add(sc_r)
            scales.append(sc_r)

    best_score = 0.0
    best_match: Optional[Tuple[int, int, int, int]] = None

    for cur_sc in scales:
        tw = int(tpl_gray.shape[1] * cur_sc)
        th = int(tpl_gray.shape[0] * cur_sc)
        if tw >= sub.shape[1] or th >= sub.shape[0] or tw < 10 or th < 10:
            continue

        interp = cv2.INTER_AREA if cur_sc < 1.0 else cv2.INTER_LINEAR
        cur_tpl = cv2.resize(tpl_gray, (tw, th), interpolation=interp)

        res = cv2.matchTemplate(sub, cur_tpl, cv2.TM_CCOEFF_NORMED)
        _, max_v, _, max_l = cv2.minMaxLoc(res)

        if max_v > best_score:
            best_score = float(max_v)
            cx = rx1 + max_l[0] + tw // 2
            cy = ry1 + max_l[1] + th // 2
            best_match = (cx, cy, tw, th)

        if max_v >= 0.88:
            break

    if best_score >= thresh and best_match is not None:
        return best_score, best_match

    return None


def classify_screen_flex(vp_img: np.ndarray) -> Tuple[str, float, Optional[Tuple[int, int]]]:
    """
    Phan loai trang thai man hinh va lay toa do TAM NUT THUC TE (FLEX Scanning):
    - Tra ve: (state_name, score, (center_x, center_y))
    Toa do (center_x, center_y) nam trong he toa do Game Viewport (0..vw, 0..vh).
    """
    if vp_img is None or vp_img.size == 0:
        return "UNKNOWN", 0.0, None

    vh, vw = vp_img.shape[:2]
    gray = cv2.cvtColor(vp_img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(vp_img, cv2.COLOR_BGR2HSV)
    tpls = load_templates()

    # 1. Kiem tra Man Ket Toan / That Bai (Hình 7 - nut Chap Nhan)
    if "chap_nhan" in tpls:
        m = find_template_flex(gray, tpls["chap_nhan"], (0.10, 0.70, 0.90, 0.98), thresh=0.68)
        if m:
            score, (cx, cy, tw, th) = m
            return "SETTLEMENT", score, (cx, cy)

    # 2. Kiem tra Quai Vat Chan Duong (Hình 2 - the Chien Dau)
    if "chien_dau" in tpls:
        m = find_template_flex(gray, tpls["chien_dau"], (0.45, 0.55, 0.98, 0.98), thresh=0.68)
        if m:
            score, (cx, cy, tw, th) = m
            return "MONSTER", score, (cx, cy)

    # 3. Kiem tra Popup Co Vat / Bao Vat (Hình 1, 5, 8, 9 - Cham de tiep tuc)
    if "cham_tiep_tuc" in tpls:
        m = find_template_flex(gray, tpls["cham_tiep_tuc"], (0.05, 0.75, 0.95, 1.00), thresh=0.72)
        if m:
            score, (cx, cy, tw, th) = m
            return "POPUP_RELIC", score, (cx, cy)

    # 4. Kiem tra Sanh Chinh (Hình 6 - nut Bat Dau Phieu Luu!)
    if "bat_dau" in tpls:
        m = find_template_flex(gray, tpls["bat_dau"], (0.15, 0.70, 0.85, 0.98), thresh=0.70)
        if m:
            score, (cx, cy, tw, th) = m
            return "LOBBY", score, (cx, cy)

    # 5. Kiem tra Trong Me Cung - Nut 'Tien Len' (Hình 3, 4)
    if "tien_len" in tpls:
        m = find_template_flex(gray, tpls["tien_len"], (0.20, 0.60, 0.80, 0.98), thresh=0.68)
        if m:
            score, (cx, cy, tw, th) = m
            y1 = max(0, cy - th // 2)
            y2 = min(vh, cy + th // 2)
            x1 = max(0, cx - tw // 2)
            x2 = min(vw, cx + tw // 2)
            roi_cyan = hsv[y1:y2, x1:x2]
            mask_cyan = cv2.inRange(roi_cyan, np.array([65, 80, 100]), np.array([100, 255, 255]))
            cyan_px = int(np.count_nonzero(mask_cyan))
            min_cyan = int(800 * ((vw / 405.0) ** 2))
            if cyan_px >= min_cyan:
                return "IN_DUNGEON", score, (cx, cy)
        else:
            # Fallback mau sac: Phat hien contour vong tron xanh ngoc cua nut Tien Len
            roi_y1 = int(vh * 0.65)
            roi_y2 = int(vh * 0.95)
            roi_x1 = int(vw * 0.20)
            roi_x2 = int(vw * 0.80)
            roi_hsv = hsv[roi_y1:roi_y2, roi_x1:roi_x2]
            mask_cyan = cv2.inRange(roi_hsv, np.array([70, 80, 100]), np.array([95, 255, 255]))
            cnts, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_dim = int(35 * (vw / 405.0))
            for c in cnts:
                bx, by, bw, bh = cv2.boundingRect(c)
                if bw >= min_dim and bh >= min_dim and abs(bw - bh) < int(35 * (vw / 405.0)):
                    cx = roi_x1 + bx + bw // 2
                    cy = roi_y1 + by + bh // 2
                    return "IN_DUNGEON", 0.90, (cx, cy)

    return "UNKNOWN", 0.0, None


def print_banner() -> None:
    """Hien thi banner giao dien khoi dong bot tren terminal."""
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 65)
    print("   AUTO PHIEU LUU CO VAT (RELIC ADVENTURE) - CLASH OF CRITTERS   ")
    print("=" * 65)
    print("  Quy trinh tu dong hoan toan (FLEX da ti le theo man hinh):")
    print("    1. [Sanh Chinh]    : Tu tim nut & bam 'Bat Dau Phieu Luu!'")
    print("    2. [Trong Me Cung] : Tu tim nut 'Tien Len' + Cho 2s buoc di")
    print("    3. [Nhan Bao Vat]  : Cho 1s timing hoat anh roi cham tiep tuc")
    print("    4. [Gap Quai Vat]  : Luon luon chon 'Chien Dau' (mac ke ti le)")
    print("    5. [Ket Toan Thua] : Bam 'Chap Nhan' + Cho 2s reset loop sanh")
    print("    6. [Chong Treo]    : Tu dong giai phong khi ket la > 3.5s")
    print("-" * 65)
    print("  Phim tat dieu khien (Giong Auto Cau Ca):")
    print("    - [Ctrl + Q] : BAT DAU / TIEP TUC (Resume)")
    print("    - [ESC]      : TAM DUNG (Pause) - Nhan lan 2 de THOAT HAN")
    print("=" * 65)
    print()


def log_stats() -> None:
    """In bang thong ke hoat dong thuc te."""
    elapsed = int(time.time() - _stats["start_time"])
    m, s = divmod(elapsed, 60)
    h, m = divmod(m, 60)
    time_str = f"{h:02d}:{m:02d}:{s:02d}"
    print(
        f"[THONG KE {time_str}] Vong choi: {_stats['runs_started']} | "
        f"Buoc di: {_stats['advances']} | "
        f"Bao vat: {_stats['relics_collected']} | "
        f"Chien dau: {_stats['fights']} | "
        f"Ket toan: {_stats['settlements']}",
        flush=True,
    )


def main() -> None:
    """Vong lap chinh cua Auto Phieu Luu Co Vat (chuan theo co che auto_cauca)."""
    global _stats

    print_banner()

    # Tim cua so gia lap
    log("[KHOI TAO] Dang tim kiem cua so gia lap Android (BlueStacks, LDPlayer, MuMu, Nox, MEmu)...")
    win = find_emulator_window()
    if not win:
        log("[LOI] Khong tim thay cua so gia lap Android nao dang mo!")
        log("Vui long mo gia lap va vao game truoc khi chay tool.")
        return

    hwnd = win._hWnd
    win_title = win.title or "Gia lap"
    left, top, w, h = get_game_viewport(hwnd, win_title)
    log(f"[KET NOI] '{win_title}' | Game: {w}x{h} tai ({left}, {top})")
    print("*" * 55)
    log("[CHU Y] Hay kiem tra log [KET NOI] ben tren xem da DUNG gia lap ban muon choi chua!")
    log("[CHU Y] Neu dang mo nhieu gia lap (coc1, coc2, coc3), hay click chuot vao gia lap muon chay de bot uu tien.")
    print("*" * 55)

    mss_factory = getattr(mss, "MSS", None)
    if mss_factory is None:
        mss_factory = getattr(mss, "mss")

    is_first_start = True

    # Bien kiem soat chong treo
    last_known_state = "UNKNOWN"
    last_known_state_time = time.time()
    last_scan_log_time = 0.0
    same_state_count = 0

    with mss_factory() as sct:
        while True:
            # =========================================================
            # XU LY TRANG THAI TAM DUNG / CHO LENH (PAUSED STATE)
            # (Hoan toan giong 100% auto_cauca: Ctrl+Q de Resume, ESC de Thoat)
            # =========================================================
            if _stop_event.is_set():
                safe_unhook_hotkeys()
                _stop_event.clear()

                # Doi nha cac phim dang giu
                while keyboard.is_pressed("esc") or keyboard.is_pressed("ctrl+q") or (keyboard.is_pressed("ctrl") and keyboard.is_pressed("q")):
                    time.sleep(0.05)

                print("-" * 55)
                if is_first_start:
                    log("[CHO LENH] Mo su kien Phieu Luu Co Vat tren gia lap.")
                    log(f"[CHU Y] Dang ket noi voi: '{win_title}'.")
                    log("[CHO LENH] Nhan Ctrl+Q de BAT DAU | Nhan ESC de THOAT HAN...")
                else:
                    log("[TAM DUNG] Da tam dung auto. Chuot da duoc giai phong!")
                    log_stats()
                    log("[CHU Y] Neu ban di chuyen hoac zoom man hinh, tool se tu dong bo lai khi Resume.")
                    log("[CHO LENH] Nhan Ctrl+Q de TIEP TUC (Resume)...")
                    log("[CHO LENH] Nhan ESC de THOAT HAN tool...")
                print("-" * 55)

                should_exit = False
                while True:
                    if keyboard.is_pressed("ctrl+q") or (keyboard.is_pressed("ctrl") and keyboard.is_pressed("q")):
                        break
                    if keyboard.is_pressed("esc"):
                        should_exit = True
                        break
                    time.sleep(0.05)

                if should_exit:
                    log("[THOAT] Nguoi dung nhan ESC de thoat han.")
                    break

                # Debounce phim
                while keyboard.is_pressed("ctrl") or keyboard.is_pressed("q"):
                    time.sleep(0.05)
                time.sleep(0.2)

                # DANG KY LAI HOTKEY ESC DE BAT TAM DUNG KHI DANG CHAY
                _stop_event.clear()
                keyboard.add_hotkey("esc", _stop_event.set, suppress=True)

                # Khi Resume: Dong bo lai toan bo toa do viewport moi nhat
                win = find_emulator_window()
                if win:
                    hwnd = win._hWnd
                    win_title = win.title or win_title
                raw_vp = get_game_viewport(hwnd, win_title)
                vp = get_effective_viewport(sct, raw_vp, force_check=True)
                gw_l, gw_t, gw_w, gw_h = vp

                if is_first_start:
                    log(f"[KHOI DONG] Auto bat dau tren '{win_title}' ({gw_w}x{gw_h})! Nhan ESC bat cu luc nao de TAM DUNG.\n")
                    is_first_start = False
                else:
                    log(f"[TIEP TUC] Auto tiep tuc tren '{win_title}' ({gw_w}x{gw_h})! Nhan ESC bat cu luc nao de TAM DUNG.\n")

                _stats["start_time"] = time.time()
                last_known_state_time = time.time()
                last_scan_log_time = time.time()
                same_state_count = 0
                continue

            # =========================================================
            # VONG LAP CHINH DANG CHAY (RUNNING)
            # =========================================================
            if _stop_event.is_set():
                continue

            # Kiem tra cua so con ton tai khong
            if not user32.IsWindow(hwnd):
                log("[CANH BAO] Cua so gia lap da bi dong! Dang thu tim lai...")
                win = find_emulator_window()
                if not win:
                    if _sleep(1.0):
                        continue
                    continue
                hwnd = win._hWnd
                win_title = win.title

            # Lay toan bo kich thuoc game viewport moi nhat
            raw_vp = get_game_viewport(hwnd, win_title)
            if raw_vp[2] < 150 or raw_vp[3] < 200:
                if _sleep(0.3):
                    continue
                continue

            vp = get_effective_viewport(sct, raw_vp)
            gw_l, gw_t, gw_w, gw_h = vp

            # Chup anh viewport hien tai
            vp_img = safe_grab(sct, {"left": gw_l, "top": gw_t, "width": gw_w, "height": gw_h})
            if vp_img is None:
                if _sleep(0.2):
                    continue
                continue

            # Nhan dien trang thai va lay toa do TAM NUT THUC TE (FLEX)
            state, score, center_pt = classify_screen_flex(vp_img)
            now = time.time()

            # Quan ly trang thai chong treo
            if state != "UNKNOWN":
                last_known_state_time = now
                if state == last_known_state:
                    same_state_count += 1
                else:
                    same_state_count = 1
                    last_known_state = state
            else:
                same_state_count = 0

            # ------------------------------------------------------------------
            # THUC THI HANH DONG THEO TUNG TRANG THAI (FLEX CLICK TOA DO THUC)
            # ------------------------------------------------------------------

            if state == "LOBBY":
                # SANH CHINH: Bam 'Bat Dau Phieu Luu!'
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_START_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_START_REL_Y)

                log(f"[SANH CHINH] Phat hien 'Bat Dau Phieu Luu!' tai tam ({cx}, {cy}) (Do khop: {score:.2f}) -> Flex Click")
                activate_window(hwnd)
                touch_tap(cx, cy, desc="Nut 'Bat Dau Phieu Luu!'")
                _stats["runs_started"] += 1
                log_stats()
                if _sleep(config.PHIEULUU_DELAY_AFTER_START):
                    continue

            elif state == "IN_DUNGEON":
                # TRONG ME CUNG: Bam 'Tien Len'
                if same_state_count > config.PHIEULUU_SAME_STATE_MAX_RETRIES:
                    log(f"[CANH BAO] Da bam 'Tien Len' {same_state_count} lan lien tiep ma chua doi canh.")
                    log("[CHONG TREO] Co the DA HET DUOC hoac game dang bi lag -> Cham nhe trung tam man hinh...")
                    cx = int(gw_l + gw_w * config.PHIEULUU_CENTER_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_CENTER_REL_Y)
                    touch_tap(cx, cy, desc="Cham trung tam giai phong")
                    same_state_count = 0
                    if _sleep(1.0):
                        continue
                    continue

                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_ADVANCE_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_ADVANCE_REL_Y)

                log(f"[ME CUNG] Phat hien nut 'Tien Len' tai tam ({cx}, {cy}) (Do khop: {score:.2f}) -> Flex Click buoc di")
                touch_tap(cx, cy, desc="Nut 'Tien Len'")
                _stats["advances"] += 1

                # Theo yeu cau: "trong qua trinh di thi se ton tam 2s gi do de di tien len"
                if _sleep(config.PHIEULUU_DELAY_AFTER_ADVANCE):
                    continue

            elif state == "POPUP_RELIC":
                # NHAN CO VAT / BAO VAT
                # Theo yeu cau: "ca 2 pop khi nhan do tier thap hay cao deu can la timing 1s de no bao la cham vao man hinh de tiep tuc"
                log(f"[BAO VAT] Xuat hien phan thuong co vat (Do khop: {score:.2f}) -> Cho 1.0s timing hoat anh...")
                if _sleep(config.PHIEULUU_DELAY_POPUP_TIMING):
                    continue

                # Chon vi tri cham dong popup: Uu tien vi tri chu 'Cham de tiep tuc' hoac day popup
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_DISMISS_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_DISMISS_REL_Y)

                log(f"-> Cham dong popup bao vat tai tam ({cx}, {cy})")
                touch_tap(cx, cy, desc="Dong popup bao vat")
                _stats["relics_collected"] += 1
                log(f"-> Da dong popup (Tong co vat da nhan: {_stats['relics_collected']})")

                if _sleep(config.PHIEULUU_DELAY_AFTER_DISMISS):
                    continue

            elif state == "MONSTER":
                # GAP QUAI VAT CHAN DUONG
                # Theo yeu cau: "nhu hinh 2 la luon chon chien dau nhung co ti le thoi (mac ke ti le thua cu chon chien dau giup toi)"
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_FIGHT_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_FIGHT_REL_Y)

                log(f"[QUAI VAT] Phat hien quai vat chan duong (Do khop: {score:.2f}) -> LUON CHON CHIEN DAU! Flex Click ({cx}, {cy})")
                touch_tap(cx, cy, desc="The 'Chien Dau'")
                _stats["fights"] += 1

                # Cho tran danh hoan tat
                if _sleep(config.PHIEULUU_DELAY_AFTER_FIGHT):
                    continue

            elif state == "SETTLEMENT":
                # MAN KET TOAN / THAT BAI
                # Theo yeu cau: "neu chien dau ma that bai thi se hien ra man ket toan va can bam nut xac nhan... bam xac nhan xong ra ngoai cho 2s reset loop"
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_SETTLE_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_SETTLE_REL_Y)

                log(f"[KET TOAN] Phieu luu ket thuc (Do khop: {score:.2f}) -> Flex Click 'Chap Nhan' ({cx}, {cy})")
                touch_tap(cx, cy, desc="Nut 'Chap Nhan'")
                _stats["settlements"] += 1
                log_stats()

                log(f"[RESET LOOP] Cho {config.PHIEULUU_DELAY_AFTER_RESET}s thoat ra sanh chinh de lap lai tu dau...")
                if _sleep(config.PHIEULUU_DELAY_AFTER_RESET):
                    continue

            else:
                # TRANG THAI LA / LOADING / CHUA XAC DINH -> CO CHE CHONG TREO (WATCHDOG)
                unknown_duration = now - last_known_state_time

                if unknown_duration >= 1.5 and (now - last_scan_log_time >= 2.5):
                    last_scan_log_time = now
                    log(f"[DANG QUET] Dang theo doi man hinh game '{win_title}' ({gw_w}x{gw_h})...")

                if unknown_duration >= config.PHIEULUU_WATCHDOG_ACTIVATE_TIMEOUT:
                    log(f"[CHONG TREO] Khong ro trang thai qua {unknown_duration:.1f}s -> Kich hoat lai cua so gia lap...")
                    activate_window(hwnd)
                    cx = int(gw_l + gw_w * config.PHIEULUU_CENTER_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_CENTER_REL_Y)
                    touch_tap(cx, cy, desc="Cham trung tam chong treo (10s)")
                    last_known_state_time = now - (config.PHIEULUU_WATCHDOG_UNKNOWN_TIMEOUT)

                elif unknown_duration >= config.PHIEULUU_WATCHDOG_UNKNOWN_TIMEOUT:
                    log(f"[CHONG TREO] Hoat anh dang doi hoac pop-up la qua {unknown_duration:.1f}s -> Cham nhe diem an toan...")
                    cx = int(gw_l + gw_w * config.PHIEULUU_DISMISS_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_DISMISS_REL_Y)
                    touch_tap(cx, cy, desc="Cham an toan chong treo (3.5s)")
                    last_known_state_time = now - 1.5

                if _sleep(0.35):
                    continue

    safe_unhook_hotkeys()
    log("=== BOT DA KET THUC HOAT DONG AN TOAN. TAM BIET! ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_unhook_hotkeys()
        log("Nhan Ctrl+C: Thoat chuong trinh.")
    except Exception as e:
        safe_unhook_hotkeys()
        log(f"[LOI HE THONG] {e}")
        import traceback
        traceback.print_exc()
