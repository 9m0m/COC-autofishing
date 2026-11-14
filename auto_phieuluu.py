"""
COC-autophieuluu: Bot tu dong di su kien Phieu Luu Co Vat (Relic Adventure)
cho game Clash of Critters tren cac trinh gia lap Android (BlueStacks 5, LDPlayer 9, MuMu, Nox, MEmu).

Quy trinh tu dong:
1. Cho lenh khoi dong: Khi mo tool len se o trang thai TAM DUNG, doi nguoi dung bam Ctrl+Q de bat dau.
2. Quet FLEX da ti le: Tu dong quet tim vi tri nut thuc te tren man hinh (ho tro moi kich thuoc cua so to/nho).
   Click truc tiep vao dung tam nut duoc phat hien thay vi dung toa do co dinh.
3. Trong me cung (Dungeon): Bam 'Tien Len' va cho ~2s hoat anh di chuyen moi buoc (khong spam).
4. Nhan Bao Vat / Co Vat (Relic Popup tier thap & cao):
   Cho 1s theo dung timing game de hien chu 'Cham diem bat ki de tiep tuc', sau do cham dong popup.
5. Gap quai vat chan duong (Monster):
   Co 2 lua chon 'Rut Lui' va 'Chien Dau' -> Luon luon chon 'Chien Dau' (mac ke ti le thang).
6. Ket toan / That bai (Settlement):
   Bam 'Chap Nhan', cho 2s thoat ra sanh chinh va lap lai vong di tu dau.
7. He thong chong treo (Watchdog / Anti-stuck) da tang:
   - Tu dong cham an toan neu bi ket man hinh la / hoat anh qua 3.5s.
   - Tu dong kich hoat lai cua so gia lap neu mat focus qua 8s.
   - Phat hien ket cung 1 trang thai (vi du: het duoc, lag mang).
8. Khong chiem chuot 100%: Tu dong nho va hoan tra con tro chuot ve vi tri cu ngay lap tuc de thoai mai luot web.
9. Phim tat:
   - Ctrl + Q : Bat / Tam dung (Pause / Resume)
   - ESC      : Dung va thoat ngay lap tuc
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

# Quan ly trang thai (Bat dau o trang thai TAM DUNG cho nguoi dung bam Ctrl+Q)
_stop_event = threading.Event()
_is_paused = True

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


def get_effective_viewport(sct: mss.MSS, raw_vp: Tuple[int, int, int, int], force_check: bool = False) -> Tuple[int, int, int, int]:
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
    """Tam dung co the huy lap tuc bang ESC."""
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
    thresh: float = 0.70,
) -> Optional[Tuple[float, Tuple[int, int, int, int]]]:
    """
    Quet FLEX da ti le tim template trong vung ROI tuong doi cua Game Viewport:
    - roi_rel: (x1_ratio, y1_ratio, x2_ratio, y2_ratio)
    - Tu dong quet qua cac ti le co dan (0.7x -> 1.4x) quanh ti le chuan.
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

    # Ti le co dan uoc tinh theo chieu rong viewport
    est_scale = vw / 405.0
    scale_factors = [1.0, 0.92, 1.08, 0.82, 1.22, 0.70, 1.40]

    best_score = 0.0
    best_match: Optional[Tuple[int, int, int, int]] = None

    for f in scale_factors:
        cur_sc = est_scale * f
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

        # Neu dat do khop rat cao thi dung som de tiet kiem CPU
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
        m = find_template_flex(gray, tpls["chap_nhan"], (0.10, 0.70, 0.90, 0.98), thresh=0.70)
        if m:
            score, (cx, cy, tw, th) = m
            return "SETTLEMENT", score, (cx, cy)

    # 2. Kiem tra Quai Vat Chan Duong (Hình 2 - the Chien Dau)
    if "chien_dau" in tpls:
        m = find_template_flex(gray, tpls["chien_dau"], (0.45, 0.55, 0.98, 0.98), thresh=0.70)
        if m:
            score, (cx, cy, tw, th) = m
            return "MONSTER", score, (cx, cy)

    # 3. Kiem tra Popup Co Vat / Bao Vat (Hình 1, 5, 8, 9 - Cham de tiep tuc)
    if "cham_tiep_tuc" in tpls:
        m = find_template_flex(gray, tpls["cham_tiep_tuc"], (0.05, 0.75, 0.95, 1.00), thresh=0.75)
        if m:
            score, (cx, cy, tw, th) = m
            return "POPUP_RELIC", score, (cx, cy)

    # 4. Kiem tra Sanh Chinh (Hình 6 - nut Bat Dau Phieu Luu!)
    if "bat_dau" in tpls:
        m = find_template_flex(gray, tpls["bat_dau"], (0.15, 0.70, 0.85, 0.98), thresh=0.72)
        if m:
            score, (cx, cy, tw, th) = m
            return "LOBBY", score, (cx, cy)

    # 5. Kiem tra Trong Me Cung - Nut 'Tien Len' (Hình 3, 4)
    if "tien_len" in tpls:
        m = find_template_flex(gray, tpls["tien_len"], (0.20, 0.65, 0.80, 0.98), thresh=0.72)
        if m:
            score, (cx, cy, tw, th) = m
            # Kiem tra pixel mau xanh ngoc trong vung nut de tranh truong hop nut bi lam toi do popup
            y1 = max(0, cy - th // 2)
            y2 = min(vh, cy + th // 2)
            x1 = max(0, cx - tw // 2)
            x2 = min(vw, cx + tw // 2)
            roi_cyan = hsv[y1:y2, x1:x2]
            mask_cyan = cv2.inRange(roi_cyan, np.array([65, 80, 100]), np.array([100, 255, 255]))
            cyan_px = int(np.count_nonzero(mask_cyan))
            min_cyan = int(1200 * ((vw / 405.0) ** 2))
            if cyan_px >= min_cyan:
                return "IN_DUNGEON", score, (cx, cy)

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
    print("  Phim tat dieu khien:")
    print("    [Ctrl + Q] : BAT / TAM DUNG (Pause / Resume)")
    print("    [ESC]      : DUNG BOT VA THOAT")
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


def on_hotkey_toggle() -> None:
    """Xu ly phim Ctrl + Q de Bat / Tam dung."""
    global _is_paused
    _is_paused = not _is_paused
    if not _is_paused:
        _stats["start_time"] = time.time()
        log("=== TRANG THAI BOT: DANG CHAY (RUNNING) ===")
    else:
        log("=== TRANG THAI BOT: TAM DUNG (PAUSED) ===")


def on_hotkey_stop() -> None:
    """Xu ly phim ESC de thoat bot."""
    log("=== NHAN ESC: DANG DUNG BOT VA THOAT AN TOAN ===")
    _stop_event.set()


def main() -> None:
    """Vong lap chinh cua Auto Phieu Luu Co Vat."""
    global _is_paused, _stats

    print_banner()

    # Dang ky hotkeys
    try:
        keyboard.add_hotkey("ctrl+q", on_hotkey_toggle)
        keyboard.add_hotkey("esc", on_hotkey_stop)
    except Exception as e:
        log(f"[CANH BAO] Khong the dang ky phim tat keyboard ({e}).")

    # Tim cua so gia lap
    log("[KHOI TAO] Dang tim kiem cua so gia lap Android (BlueStacks, LDPlayer, MuMu, Nox, MEmu)...")
    win = find_emulator_window()
    if not win:
        log("[LOI] Khong tim thay cua so gia lap Android nao dang mo!")
        log("Vui long mo gia lap va dang nhap game Clash of Critters truoc khi chay tool.")
        safe_unhook_hotkeys()
        return

    hwnd = win._hWnd
    win_title = win.title or "Gia lap"
    log(f"[KET NOI] Da ket noi cua so: '{win_title}' (HWND: {hwnd})")

    # Bat dau o trang thai TAM DUNG cho nguoi dung bam Ctrl+Q
    _is_paused = True
    log("[CHO LENH] Bot dang o trang thai TAM DUNG de ban chuan bi san sang.")
    log("👉 Nhan [Ctrl + Q] de BAT DAU tu dong!")
    log("👉 Nhan [ESC] de THOAT chuong trinh.")

    # Bien kiem soat chong treo
    last_known_state = "UNKNOWN"
    last_known_state_time = time.time()
    same_state_count = 0

    mss_factory = getattr(mss, "MSS", mss.mss)
    with mss_factory() as sct:
        while not _stop_event.is_set():
            # Neu dang tam dung: khong click bat ky thu gi
            if _is_paused:
                if _sleep(0.2):
                    break
                continue

            # Kiem tra cua so con ton tai khong
            if not user32.IsWindow(hwnd):
                log("[CANH BAO] Cua so gia lap da bi dong! Dang thu tim lai...")
                win = find_emulator_window()
                if not win:
                    if _sleep(1.0):
                        break
                    continue
                hwnd = win._hWnd
                win_title = win.title

            # Lay toan bo kich thuoc game viewport moi nhat (Flex theo cua so thuc)
            raw_vp = get_game_viewport(hwnd, win_title)
            if raw_vp[2] < 150 or raw_vp[3] < 200:
                if _sleep(0.5):
                    break
                continue

            vp = get_effective_viewport(sct, raw_vp)
            gw_l, gw_t, gw_w, gw_h = vp

            # Chup anh viewport hien tai
            vp_img = safe_grab(sct, {"left": gw_l, "top": gw_t, "width": gw_w, "height": gw_h})
            if vp_img is None:
                if _sleep(0.2):
                    break
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

                log(f"[SANH CHINH] Phat hien 'Bat Dau Phieu Luu!' (Do khop: {score:.2f}) -> Flex Click ({cx}, {cy})")
                activate_window(hwnd)
                touch_tap(cx, cy, desc="Nut 'Bat Dau Phieu Luu!'")
                _stats["runs_started"] += 1
                log_stats()
                if _sleep(config.PHIEULUU_DELAY_AFTER_START):
                    break

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
                        break
                    continue

                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_ADVANCE_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_ADVANCE_REL_Y)

                log(f"[ME CUNG] San sang buoc tiep -> Flex Click nut 'Tien Len' ({cx}, {cy}) (Do khop: {score:.2f})")
                touch_tap(cx, cy, desc="Nut 'Tien Len'")
                _stats["advances"] += 1

                # Theo yeu cau: "trong qua trinh di thi se ton tam 2s gi do de di tien len"
                if _sleep(config.PHIEULUU_DELAY_AFTER_ADVANCE):
                    break

            elif state == "POPUP_RELIC":
                # NHAN CO VAT / BAO VAT
                # Theo yeu cau: "ca 2 pop khi nhan do tier thap hay cao deu can la timing 1s de no bao la cham vao man hinh de tiep tuc"
                log(f"[BAO VAT] Xuat hien phan thuong co vat (Do khop: {score:.2f}) -> Cho 1.0s timing hoat anh...")
                if _sleep(config.PHIEULUU_DELAY_POPUP_TIMING):
                    break

                # Chon vi tri cham dong popup: Uu tien vi tri chu 'Cham de tiep tuc' hoac day popup
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_DISMISS_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_DISMISS_REL_Y)

                log(f"-> Cham dong popup bao vat tai ({cx}, {cy})")
                touch_tap(cx, cy, desc="Dong popup bao vat")
                _stats["relics_collected"] += 1
                log(f"-> Da dong popup (Tong co vat da nhan: {_stats['relics_collected']})")

                if _sleep(config.PHIEULUU_DELAY_AFTER_DISMISS):
                    break

            elif state == "MONSTER":
                # GAP QUAI VAT CHAN DUONG
                # Theo yeu cau: "nhu hinh 2 la luon chon chien dau nhung co ti le thoi (mac ke ti le thua cu chon chien dau giup toi)"
                if center_pt is not None:
                    cx = gw_l + center_pt[0]
                    cy = gw_t + center_pt[1]
                else:
                    cx = int(gw_l + gw_w * config.PHIEULUU_FIGHT_REL_X)
                    cy = int(gw_t + gw_h * config.PHIEULUU_FIGHT_REL_Y)

                log(f"[QUAI VAT] Xuat hien quai vat chan duong (Do khop: {score:.2f}) -> LUON CHON CHIEN DAU! Flex Click ({cx}, {cy})")
                touch_tap(cx, cy, desc="The 'Chien Dau'")
                _stats["fights"] += 1

                # Cho tran danh hoan tat
                if _sleep(config.PHIEULUU_DELAY_AFTER_FIGHT):
                    break

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
                    break

            else:
                # TRANG THAI LA / LOADING / CHUA XAC DINH -> CO CHE CHONG TREO (WATCHDOG)
                unknown_duration = now - last_known_state_time

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
                    break

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
