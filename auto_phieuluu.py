"""
COC-autophieuluu: Bot tu dong di su kien Phieu Luu Co Vat (Relic Adventure)
cho game Clash of Critters tren cac trinh gia lap Android (BlueStacks 5, LDPlayer 9, MuMu, Nox, MEmu).

Quy trinh tu dong:
1. Sảnh chính (Lobby): Tu dong bam 'Bat Dau Phieu Luu!'.
2. Trong me cung (Dungeon): Bam 'Tien Len' va cho ~2s hoat anh di chuyen moi buoc.
3. Nhan Bao Vat / Co Vat (Relic Popup tier thap & cao):
   Cho 1s theo dung timing game de hien chu 'Cham diem bat ki de tiep tuc', sau do cham dong popup.
4. Gap quai vat chan duong (Monster):
   Co 2 lua chon 'Rut Lui' va 'Chien Dau' -> Luon luon chon 'Chien Dau' (mac ke ti le thang).
5. Ket toan / That bai (Settlement):
   Bam 'Chap Nhan', cho 2s thoat ra sanh chinh va lap lai vong di tu dau.
6. He thong chong treo (Watchdog / Anti-stuck) da tang:
   - Tu dong cham an toan neu bi ket man hinh la / hoat anh qua 3.5s.
   - Tu dong kich hoat lai cua so gia lap neu mat focus qua 8s.
   - Phat hien ket cung 1 trang thai (vi du: het duoc, lag mang).
7. Phim tat:
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

# Quan ly trang thai
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
_last_vp_width: int = 0
_scaled_templates: Dict[str, np.ndarray] = {}

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
    """
    global _effective_vp, _last_raw_vp, _last_pillarbox_check
    now = time.time()
    if not force_check and _effective_vp is not None and raw_vp == _last_raw_vp and (now - _last_pillarbox_check < 10.0):
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
        log(f"[PILLARBOX] Dai den phat hien: Le trai {offset_x}px, Rong thuc {real_w}px (Goc {gw_w}px)")
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


def get_scaled_template(name: str, current_vp_w: int) -> Optional[np.ndarray]:
    """
    Tu dong tinh ti le va co dan template phu hop voi chieu rong viewport cua gia lap.
    Chuan goc: Viewport rong ~405px.
    """
    global _last_vp_width, _scaled_templates
    base_tpls = load_templates()
    if name not in base_tpls or base_tpls[name] is None:
        return None

    if current_vp_w != _last_vp_width:
        _scaled_templates.clear()
        _last_vp_width = current_vp_w

    if name in _scaled_templates:
        return _scaled_templates[name]

    scale = max(0.4, min(3.0, current_vp_w / 405.0))
    base = base_tpls[name]
    if abs(scale - 1.0) < 0.03:
        _scaled_templates[name] = base
    else:
        new_w = max(5, int(base.shape[1] * scale))
        new_h = max(5, int(base.shape[0] * scale))
        interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
        _scaled_templates[name] = cv2.resize(base, (new_w, new_h), interpolation=interp)

    return _scaled_templates[name]


def match_template_score(gray_roi: np.ndarray, tpl: np.ndarray) -> float:
    """Tinh do khop chuan hoa (Normalized Cross-Correlation) giua ROI va Template."""
    if gray_roi is None or tpl is None:
        return 0.0
    if len(tpl.shape) == 3:
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
    else:
        tpl_gray = tpl

    rh, rw = gray_roi.shape[:2]
    th, tw = tpl_gray.shape[:2]
    if rh < th or rw < tw:
        return 0.0

    res = cv2.matchTemplate(gray_roi, tpl_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return float(max_val)


def classify_screen(vp_img: np.ndarray) -> Tuple[str, float]:
    """
    Phan loai chinh xac 100% trang thai hien tai cua game:
    - 'SETTLEMENT'  : Man ket toan that bai (Hình 7 - nut Chap Nhan)
    - 'MONSTER'     : Gap quai vat chan duong (Hình 2 - the Chien Dau)
    - 'POPUP_RELIC' : Popup nhan co vat tier cao/thap (Hình 1, 5, 8, 9 - Cham de tiep tuc)
    - 'LOBBY'       : Sanh khoi dau (Hình 6 - nut Bat Dau Phieu Luu!)
    - 'IN_DUNGEON'  : Trong me cung (Hình 3, 4 - nut Tien Len san sang)
    - 'UNKNOWN'     : Hoat anh dang chuyen canh / loading
    """
    if vp_img is None or vp_img.size == 0:
        return "UNKNOWN", 0.0

    vh, vw = vp_img.shape[:2]
    gray = cv2.cvtColor(vp_img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(vp_img, cv2.COLOR_BGR2HSV)

    # 1. Kiem tra Man Ket Toan / That Bai (Hình 7)
    # Vung nut 'Chap Nhan' o day man hinh (Rel Y: 0.80 -> 1.00, Rel X: 0.20 -> 0.80)
    tpl_chap_nhan = get_scaled_template("chap_nhan", vw)
    if tpl_chap_nhan is not None:
        roi_settle = gray[int(vh * 0.80):, int(vw * 0.20):int(vw * 0.80)]
        score_settle = match_template_score(roi_settle, tpl_chap_nhan)
        if score_settle >= 0.75:
            return "SETTLEMENT", score_settle

    # 2. Kiem tra Quai Vat Chan Duong (Hình 2)
    # The 'Chien Dau' ben phai (Rel Y: 0.60 -> 0.95, Rel X: 0.48 -> 0.95)
    tpl_chien_dau = get_scaled_template("chien_dau", vw)
    if tpl_chien_dau is not None:
        roi_fight = gray[int(vh * 0.60):int(vh * 0.95), int(vw * 0.48):]
        score_fight = match_template_score(roi_fight, tpl_chien_dau)
        if score_fight >= 0.75:
            return "MONSTER", score_fight

    # 3. Kiem tra Popup Co Vat / Bao Vat (Hình 1, 5, 8, 9)
    # Dong chu 'Cham diem bat ki de tiep tuc' o day popup (Rel Y: 0.85 -> 1.00, Rel X: 0.10 -> 0.90)
    tpl_cham_tiep_tuc = get_scaled_template("cham_tiep_tuc", vw)
    if tpl_cham_tiep_tuc is not None:
        roi_popup = gray[int(vh * 0.85):, int(vw * 0.10):int(vw * 0.90)]
        score_popup = match_template_score(roi_popup, tpl_cham_tiep_tuc)
        if score_popup >= 0.75:
            return "POPUP_RELIC", score_popup

    # 4. Kiem tra Sanh Chinh (Hình 6)
    # Nut cam 'Bat Dau Phieu Luu!' (Rel Y: 0.75 -> 0.95, Rel X: 0.30 -> 0.80)
    tpl_bat_dau = get_scaled_template("bat_dau", vw)
    if tpl_bat_dau is not None:
        roi_lobby = gray[int(vh * 0.75):int(vh * 0.95), int(vw * 0.30):int(vw * 0.80)]
        score_lobby = match_template_score(roi_lobby, tpl_bat_dau)
        if score_lobby >= 0.75:
            return "LOBBY", score_lobby

    # 5. Kiem tra Trong Me Cung - Nut 'Tien Len' (Hình 3, 4)
    # Nut tron mau xanh ngoc + duoc lua (Rel Y: 0.70 -> 0.95, Rel X: 0.30 -> 0.70)
    tpl_tien_len = get_scaled_template("tien_len", vw)
    if tpl_tien_len is not None:
        roi_advance = gray[int(vh * 0.70):int(vh * 0.95), int(vw * 0.30):int(vw * 0.70)]
        score_advance = match_template_score(roi_advance, tpl_tien_len)
        # Kiem tra mau xanh ngoc tren nut de loai tru truong hop nut bi lam toi do popup
        roi_cyan = hsv[int(vh * 0.75):int(vh * 0.88), int(vw * 0.38):int(vw * 0.62)]
        mask_cyan = cv2.inRange(roi_cyan, np.array([65, 80, 100]), np.array([100, 255, 255]))
        cyan_px = int(np.count_nonzero(mask_cyan))
        # Nguong pixel xanh ngoc chuan hoa theo ti le kich thuoc
        min_cyan = int(2000 * ((vw / 405.0) ** 2))
        if score_advance >= 0.75 and cyan_px >= min_cyan:
            return "IN_DUNGEON", score_advance

    return "UNKNOWN", 0.0


def print_banner() -> None:
    """Hien thi banner giao dien khoi dong bot tren terminal."""
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 65)
    print("   AUTO PHIEU LUU CO VAT (RELIC ADVENTURE) - CLASH OF CRITTERS   ")
    print("=" * 65)
    print("  Quy trinh tu dong hoan toan:")
    print("    1. [Sanh Chinh]    : Bam 'Bat Dau Phieu Luu!'")
    print("    2. [Trong Me Cung] : Bam 'Tien Len' + Cho 2s buoc di")
    print("    3. [Nhan Bao Vat]  : Cho 1s timing hoat anh roi cham tiep tuc")
    print("    4. [Gap Quai Vat]  : Luon luon chon 'Chien Dau' (mac ke ti le)")
    print("    5. [Ket Toan Thua] : Bam 'Chap Nhan' + Cho 2s reset loop sảnh")
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
    status = "DANG CHAY (RUNNING)" if not _is_paused else "TAM DUNG (PAUSED)"
    log(f"=== TRANG THAI BOT: {status} ===")


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

    # Bat dau o trang thai chay ngay lap tuc
    _is_paused = False
    _stats["start_time"] = time.time()
    log("=== BOT BAT DAU HOAT DONG NGAY LAP TUC (Ctrl+Q de tam dung, ESC de thoat) ===")

    # Bien kiem soat chong treo
    last_known_state = "UNKNOWN"
    last_known_state_time = time.time()
    same_state_count = 0
    last_action_time = time.time()

    with mss.mss() as sct:
        while not _stop_event.is_set():
            # Neu dang tam dung
            if _is_paused:
                if _sleep(0.3):
                    break
                continue

            # Kiem tra cua so hop le
            if not user32.IsWindow(hwnd):
                log("[CANH BAO] Cua so gia lap da bi dong! Dang thu tim lai...")
                win = find_emulator_window()
                if not win:
                    if _sleep(1.0):
                        break
                    continue
                hwnd = win._hWnd
                win_title = win.title

            # Lay game viewport va xu ly dai den (Pillarbox)
            raw_vp = get_game_viewport(hwnd, win_title)
            if raw_vp[2] < 200 or raw_vp[3] < 300:
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

            # Nhan dien trang thai man hinh
            state, score = classify_screen(vp_img)
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
            # THUC THI HANH DONG THEO TUNG TRANG THAI
            # ------------------------------------------------------------------

            if state == "LOBBY":
                # SANH CHINH: Bam 'Bat Dau Phieu Luu!'
                log(f"[SANH CHINH] Phat hien nut 'Bat Dau Phieu Luu!' (Do khop: {score:.2f}) -> Bam bat dau")
                cx = int(gw_l + gw_w * config.PHIEULUU_START_REL_X)
                cy = int(gw_t + gw_h * config.PHIEULUU_START_REL_Y)
                activate_window(hwnd)
                touch_tap(cx, cy, desc="Nut 'Bat Dau Phieu Luu!'")
                _stats["runs_started"] += 1
                log_stats()
                # Cho hoat anh vao man me cung
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

                log(f"[ME CUNG] San sang buoc tiep -> Bam nut 'Tien Len' (Do khop: {score:.2f})")
                cx = int(gw_l + gw_w * config.PHIEULUU_ADVANCE_REL_X)
                cy = int(gw_t + gw_h * config.PHIEULUU_ADVANCE_REL_Y)
                touch_tap(cx, cy, desc="Nut 'Tien Len'")
                _stats["advances"] += 1

                # Theo yeu cau: "trong qua trinh di thi se ton tam 2s gi do de di tien len nen la co spam nut tien len cung khong lam no nhanh hon"
                if _sleep(config.PHIEULUU_DELAY_AFTER_ADVANCE):
                    break

            elif state == "POPUP_RELIC":
                # NHAN CO VAT / BAO VAT (Tier thap hoac cao deu co 'Cham diem bat ki de tiep tuc')
                # Theo yeu cau: "ca 2 pop khi nhan do tier thap hay cao deu can la timing 1s de no bao la cham vao man hinh de tiep tuc"
                log(f"[BAO VAT] Xuat hien phan thuong co vat (Do khop: {score:.2f}) -> Cho 1.0s timing hoat anh...")
                if _sleep(config.PHIEULUU_DELAY_POPUP_TIMING):
                    break

                # Sau khi du timing 1s, cham vao diem an toan tren man hinh de dong popup
                cx = int(gw_l + gw_w * config.PHIEULUU_DISMISS_REL_X)
                cy = int(gw_t + gw_h * config.PHIEULUU_DISMISS_REL_Y)
                touch_tap(cx, cy, desc="Cham man hinh dong popup bao vat")
                _stats["relics_collected"] += 1
                log(f"-> Da dong popup nhan thuong (Tong co vat da nhan: {_stats['relics_collected']})")

                if _sleep(config.PHIEULUU_DELAY_AFTER_DISMISS):
                    break

            elif state == "MONSTER":
                # GAP QUAI VAT CHAN DUONG
                # Theo yeu cau: "nhu hinh 2 la luon chon chien dau nhung co ti le thoi (mac ke ti le thua cu chon chien dau giup toi)"
                log(f"[QUAI VAT] Xuat hien quai vat chan duong (Do khop: {score:.2f}) -> LUON CHON CHIEN DAU!")
                cx = int(gw_l + gw_w * config.PHIEULUU_FIGHT_REL_X)
                cy = int(gw_t + gw_h * config.PHIEULUU_FIGHT_REL_Y)
                touch_tap(cx, cy, desc="The 'Chien Dau'")
                _stats["fights"] += 1

                # Cho tran danh hoan tat
                if _sleep(config.PHIEULUU_DELAY_AFTER_FIGHT):
                    break

            elif state == "SETTLEMENT":
                # MAN KET TOAN / THAT BAI
                # Theo yeu cau: "neu chien dau ma that bai thi se hien ra man ket toan va can bam nut xac nhan nhu hinh 7... bam xac nhan xong ra ngoai cho 2s reset loop di lai tu dau nhu cu"
                log(f"[KET TOAN] Phieu luu ket thuc (Do khop: {score:.2f}) -> Bam 'Chap Nhan'")
                cx = int(gw_l + gw_w * config.PHIEULUU_SETTLE_REL_X)
                cy = int(gw_t + gw_h * config.PHIEULUU_SETTLE_REL_Y)
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
                    # Cham nhe trung tam
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
