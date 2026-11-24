"""
COC-autorally: Bot tu dong tham gia Rally (Tong Tan Cong) trong su kien Sa Hai Me Thanh (Gold Rush)
cho game Clash of Critters tren cac gia lap Android (BlueStacks 5, LDPlayer 9, MuMu, Nox, MEmu).
"""

import sys
import time
import threading
import itertools
from typing import Optional, Tuple, Dict, List

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
_last_esc_time: float = 0.0
_last_clicked_tile: Optional[Tuple[int, int]] = None
_full_tiles_cooldown: Dict[Tuple[int, int], float] = {}
_recently_joined_tiles: Dict[Tuple[int, int], float] = {}
_last_best_score: float = 0.0
_effective_vp: Optional[Tuple[int, int, int, int]] = None
_last_raw_vp: Optional[Tuple[int, int, int, int]] = None
_last_pillarbox_check: float = 0.0
_last_logged_pillarbox: Optional[Tuple[int, int]] = None

# He thong Template tieu de 'Tong Tan Cong!' cho 4 phe dia hinh (Vang, Xanh, Do, Tim) tren Mapview
_rally_templates = assets.get_rally_templates()
_timer_template = assets.get_rally_timer_template()


def detect_pillarbox(crop: np.ndarray, black_thresh: Optional[float] = None, min_margin: Optional[int] = None) -> Tuple[int, int]:
    """
    Xac dinh do rong dai den (pillarbox) hai ben mep cua so neu bi keo dan ngang.
    Hoat dong chinh xac 100% tren moi gia lap (BlueStacks, LDPlayer, MuMu, Nox, MEmu),
    khong bi danh lua boi vien cua so 1px hoac thanh cong cu sidebar ben phai.
    Tra ve: (offset_x, real_w) tinh theo pixel trong crop.
    """
    if crop is None or crop.size == 0:
        return 0, 0
    if black_thresh is None:
        black_thresh = getattr(config, "PILLARBOX_BLACK_THRESHOLD", 12.0)
    if min_margin is None:
        min_margin = getattr(config, "PILLARBOX_MIN_MARGIN", 15)

    h, w = crop.shape[:2]
    # Lay 60% dai giua theo chieu doc de tranh cac thanh tieu de/tab/thanh dieu huong
    mid_crop = crop[int(h * 0.20):int(h * 0.80), :]
    gray = cv2.cvtColor(mid_crop, cv2.COLOR_BGR2GRAY)
    col_means = np.mean(gray, axis=0)
    is_black = (col_means <= black_thresh)

    # Tim cac khoi cot den lien tiep (runs)
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
    Lay toa do viewport thuc te cua game sau khi loai tru dai den hai ben suon (Pillarbox).
    Neu cua so bi keo dan ngang hon ty le 9:16 cua mobile, ham se thu hep ve dung vung game.
    """
    global _effective_vp, _last_raw_vp, _last_pillarbox_check, _last_logged_pillarbox
    now = time.time()
    if not force_check and _effective_vp is not None and raw_vp == _last_raw_vp and (now - _last_pillarbox_check < 10.0):
        return _effective_vp

    gw_l, gw_t, gw_w, gw_h = raw_vp
    _last_raw_vp = raw_vp
    _last_pillarbox_check = now

    # Lay mau dai giua man hinh de kiem tra dai den
    sample_y = int(gw_t + gw_h * 0.35)
    sample_h = max(10, int(gw_h * 0.30))
    sample = safe_grab(sct, {"left": gw_l, "top": sample_y, "width": gw_w, "height": sample_h})
    if sample is None:
        _effective_vp = raw_vp
        return raw_vp

    offset_x, real_w = detect_pillarbox(sample)
    if offset_x > 0 or real_w < gw_w:
        _effective_vp = (gw_l + offset_x, gw_t, real_w, gw_h)
        if _last_logged_pillarbox != (offset_x, real_w):
            log(f"[PILLARBOX] Phat hien dai den: Le trai {offset_x}px, Rong thuc {real_w}px (Viewport goc {gw_w}px)")
            _last_logged_pillarbox = (offset_x, real_w)
    else:
        _effective_vp = raw_vp
        _last_logged_pillarbox = (0, gw_w)
    return _effective_vp


def _sleep(seconds: float) -> bool:
    """Tam dung co the huy lap tuc khi nguoi dung bam ESC hoac tam dung bot."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        if _stop_event.is_set() or _is_paused:
            return True
        time.sleep(0.02)
    return False


def _is_tile_in_dict(tile: Tuple[int, int], target_dict: Dict[Tuple[int, int], float], threshold: int = 35) -> bool:
    """Kiem tra xem toa do co nam gan toa do nao trong danh sach khong."""
    tx, ty = tile
    return any(abs(tx - cx) < threshold and abs(ty - cy) < threshold for cx, cy in target_dict.keys())


def _find_green_buttons(crop: np.ndarray, min_w_ratio: float = 0.20) -> List[Tuple[int, int, int, int]]:
    """Tim cac hop bao quanh nut mau xanh la cay trong mot vung anh."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array(config.HSV_RALLY_GREEN_LOWER, dtype=np.uint8),
        np.array(config.HSV_RALLY_GREEN_UPPER, dtype=np.uint8),
    )
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_w = int(crop.shape[1] * min_w_ratio)
    buttons = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w >= min_w and 15 <= h <= 60:
            buttons.append((x, y, w, h))
    return buttons


def check_and_claim_reward(sct: mss.MSS, vp: Tuple[int, int, int, int], hwnd: Optional[int] = None) -> bool:
    """Kiem tra va bam 'Xac Nhan' nhan qua sau khi tran Rally ket thuc."""
    gw_l, gw_t, gw_w, gw_h = vp
    x1 = int(gw_l + gw_w * config.RALLY_REWARD_BTN_REL_X_MIN)
    x2 = int(gw_l + gw_w * config.RALLY_REWARD_BTN_REL_X_MAX)
    y1 = int(gw_t + gw_h * config.RALLY_REWARD_BTN_REL_Y_MIN)
    y2 = int(gw_t + gw_h * config.RALLY_REWARD_BTN_REL_Y_MAX)

    crop = safe_grab(sct, {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1})
    if crop is None:
        return False

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.array(config.HSV_RALLY_GREEN_LOWER, dtype=np.uint8),
        np.array(config.HSV_RALLY_GREEN_UPPER, dtype=np.uint8),
    )
    if int(np.count_nonzero(mask)) > 300:
        if hwnd:
            activate_window(hwnd)
        cx = int(gw_l + gw_w * config.RALLY_CLAIM_REWARD_X)
        cy = int(gw_t + gw_h * config.RALLY_CLAIM_REWARD_Y)
        touch_tap(cx, cy)
        _sleep(config.RALLY_DELAY_AFTER_CLAIM_REWARD)
        return True
    return False


def handle_rally_detail_popup(sct: mss.MSS, vp: Tuple[int, int, int, int], hwnd: Optional[int] = None) -> Tuple[bool, bool]:
    """
    Xu ly popup Rally sau khi click vao o dat tren Mapview:
    1. Type A: Popup danh sach 'Tong Tan Cong' (co cac the card rally, dong bang cach click vung tren y = 0.12).
    2. Type B: Popup chi tiet Rally le 'Don Vi Tieu Chuan' (co nut Back ↩ goc trai, nut hanh dong o goc phai).
       - Neu nut XANH ('Tham gia'): bam tham gia -> bam Back de ve Mapview.
       - Neu nut XAM ('Cho chap thuan' / 'Da day' / 'Da tham gia'): danh dau cooldown tranh spam -> bam Back.
    3. Type C: Bang Tan Cong o dat (co nut VANG 'Tan Cong' > 2500px): bam Back ve Mapview.
    4. Type D: Bang thong tin o dat: click tren cao (0.50, 0.20) de bo chon.
    """
    global _last_clicked_tile, _full_tiles_cooldown, _recently_joined_tiles
    if _is_paused or _stop_event.is_set():
        return False, False

    gw_l, gw_t, gw_w, gw_h = vp

    screen_crop = safe_grab(sct, {"left": gw_l, "top": gw_t, "width": gw_w, "height": gw_h})
    if screen_crop is None:
        return False, False

    # 1. KIEM TRA TYPE A: POPUP DANH SACH 'TONG TAN CONG' (Hinh 1, Hinh 4, Hinh 5)
    tab = screen_crop[int(gw_h * 0.15):int(gw_h * 0.22), int(gw_w * 0.03):int(gw_w * 0.40)]
    top_dim = screen_crop[int(gw_h * 0.09):int(gw_h * 0.14), int(gw_w * 0.20):int(gw_w * 0.80)]
    is_multi_sheet = (tab.size > 0 and top_dim.size > 0 and np.mean(tab) < 75.0 and np.mean(top_dim) < 70.0)

    if is_multi_sheet:
        bx1, bx2 = int(gw_w * 0.55), int(gw_w * 0.95)
        by1, by2 = int(gw_h * 0.22), int(gw_h * 0.85)
        card_crop = screen_crop[by1:by2, bx1:bx2]
        hsv_cards = cv2.cvtColor(card_crop, cv2.COLOR_BGR2HSV)

        # Tim nut xanh 'Tham gia'
        green_mask = cv2.inRange(hsv_cards, np.array([35, 100, 100]), np.array([85, 255, 255]))
        contours_g, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_btns = []
        min_btn_w = int(gw_w * 0.16)
        for c in contours_g:
            cx, cy, bw, bh = cv2.boundingRect(c)
            if bw >= min_btn_w and 18 <= bh <= 55:
                green_btns.append((bx1 + cx + bw // 2, by1 + cy + bh // 2))
        green_btns.sort(key=lambda b: b[1])

        joined_any = False
        if green_btns:
            btn_x, btn_y = green_btns[0]
            if hwnd:
                activate_window(hwnd)
            touch_tap(gw_l + btn_x, gw_t + btn_y)
            joined_any = True
            if _last_clicked_tile is not None:
                _recently_joined_tiles[_last_clicked_tile] = time.time() + 240.0
            if _sleep(0.4):
                return True, True
        else:
            if _last_clicked_tile is not None:
                _full_tiles_cooldown[_last_clicked_tile] = time.time() + config.RALLY_FULL_TILE_COOLDOWN
                log(f"[RALLY] O ({_last_clicked_tile[0]}, {_last_clicked_tile[1]}) khong con cuoc Rally kha dung (Da day / Dang cho) -> Bo qua {int(config.RALLY_FULL_TILE_COOLDOWN)}s")

        # Dong popup bang cach click khoang trong phia tren (0.50, 0.12)
        safe_close_x = int(gw_l + gw_w * 0.50)
        safe_close_y = int(gw_t + gw_h * 0.12)
        touch_tap(safe_close_x, safe_close_y)
        _sleep(0.35)
        check_after = safe_grab(sct, {"left": int(gw_l + gw_w * 0.03), "top": int(gw_t + gw_h * 0.15), "width": int(gw_w * 0.37), "height": int(gw_h * 0.07)})
        if check_after is not None and np.mean(check_after) < 75.0:
            touch_tap(safe_close_x, safe_close_y)
            _sleep(0.25)

        _last_clicked_tile = None
        return True, joined_any

    # 2. KIEM TRA TYPE B & C: CO NUT BACK `↩` O GOC DUOI BEN TRAI (0.085, 0.940)
    back_x = int(gw_l + gw_w * config.RALLY_POPUP_BACK_X)
    back_y = int(gw_t + gw_h * config.RALLY_POPUP_BACK_Y)
    crop_back = screen_crop[max(0, int(gw_h * 0.91)):min(gw_h, int(gw_h * 0.97)), max(0, int(gw_w * 0.04)):min(gw_w, int(gw_w * 0.14))]
    w_mask = (crop_back[:, :, 0] > 180) & (crop_back[:, :, 1] > 180) & (crop_back[:, :, 2] > 180)
    has_back_btn = (int(np.count_nonzero(w_mask)) >= 80)

    if has_back_btn:
        bx1, bx2 = int(gw_w * 0.52), int(gw_w * 0.92)
        by1, by2 = int(gw_h * 0.88), int(gw_h * 0.97)
        btn_crop = screen_crop[by1:by2, bx1:bx2]
        hsv_btn = cv2.cvtColor(btn_crop, cv2.COLOR_BGR2HSV)

        yellow_px = int(np.count_nonzero(cv2.inRange(hsv_btn, (15, 100, 100), (35, 255, 255))))
        green_px = int(np.count_nonzero(cv2.inRange(hsv_btn, (35, 100, 100), (85, 255, 255))))
        grey_px = int(np.count_nonzero(cv2.inRange(hsv_btn, (0, 0, 100), (180, 40, 210))))

        # A) Neu la nut VANG 'Tan Cong' (Hinh 2 tu turn 1) -> Day la bang danh o dat, khong phai Rally!
        if yellow_px > 2500:
            log("[MAPVIEW] Mo nham bang Tan Cong o dat -> Dong bang ve Map")
            touch_tap(back_x, back_y)
            _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
            _last_clicked_tile = None
            return False, False

        # B) Neu la nut XANH 'Tham gia' -> Day la RALLY LE KHA DUNG, THAM GIA NGAY!
        if green_px > 1500:
            join_btn_x = int(gw_l + gw_w * 0.72)
            join_btn_y = int(gw_t + gw_h * 0.93)
            if hwnd:
                activate_window(hwnd)
            touch_tap(join_btn_x, join_btn_y)
            if _last_clicked_tile is not None:
                _recently_joined_tiles[_last_clicked_tile] = time.time() + 240.0
            _sleep(0.4)
            touch_tap(back_x, back_y)
            _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
            _last_clicked_tile = None
            return True, True

        # C) Neu la nut XAM 'Cho chap thuan' / 'Da day' / 'Da tham gia' (Hinh 2 moi) -> Rally le da day/cho!
        if grey_px > 2000:
            if _last_clicked_tile is not None:
                _full_tiles_cooldown[_last_clicked_tile] = time.time() + config.RALLY_FULL_TILE_COOLDOWN
                log(f"[RALLY] Rally le tai ({_last_clicked_tile[0]}, {_last_clicked_tile[1]}) da day hoac cho chap thuan -> Bo qua {int(config.RALLY_FULL_TILE_COOLDOWN)}s")
            touch_tap(back_x, back_y)
            _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
            _last_clicked_tile = None
            return True, False

    # 3. KIEM TRA BANG THONG TIN O DAT (Hinh Mo Vang Nho / Dong Bang khong co nut)
    crop_pill = screen_crop[int(gw_h * 0.61):int(gw_h * 0.66), int(gw_w * 0.03):int(gw_w * 0.30)]
    if crop_pill.size > 0 and np.mean(crop_pill) < 90.0:
        log("[MAPVIEW] Mo nham bang thong tin o dat -> Bo chon ve Map")
        touch_tap(int(gw_l + gw_w * 0.50), int(gw_t + gw_h * 0.20))
        _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
        _last_clicked_tile = None
        return False, False

    return False, False


def _detect_faction_name(crop: np.ndarray) -> str:
    """Xac dinh ten phe dua tren mau sac dia hinh/vien huy hieu quanh banner."""
    if crop is None or crop.size == 0:
        return "Yellow"
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hues = hsv[:, :, 0]
    sats = hsv[:, :, 1]
    valid = sats > 50
    yellow_count = int(np.count_nonzero((hues >= 15) & (hues <= 35) & valid))
    blue_count = int(np.count_nonzero((hues >= 90) & (hues <= 130) & valid))
    red_count = int(np.count_nonzero(((hues < 15) | (hues >= 165)) & valid))
    purple_count = int(np.count_nonzero((hues >= 130) & (hues < 165) & valid))
    counts = {"Yellow": yellow_count, "Blue": blue_count, "Red": red_count, "Purple": purple_count}
    best = max(counts, key=counts.get)
    return best if counts[best] > 200 else "Yellow"


def scan_and_join_map_rallies(sct: mss.MSS, vp: Tuple[int, int, int, int], hwnd: Optional[int] = None) -> Optional[str]:
    """
    Quet Tong Mapview tim tieu de 'Tong Tan Cong!' qua Template Matching da ty le va da mua.
    Ho tro Grayscale matching da mua giup nhan dien chinh xac tren moi loai dia hinh,
    va click truc tiep vao tam tieu de Rally de tranh cham lech vao o dat.
    """
    global _last_clicked_tile, _full_tiles_cooldown, _recently_joined_tiles, _last_best_score, _effective_vp
    if _is_paused or _stop_event.is_set():
        return None

    gw_l, gw_t, gw_w, gw_h = vp

    now = time.time()
    _full_tiles_cooldown = {p: exp for p, exp in _full_tiles_cooldown.items() if exp > now}
    _recently_joined_tiles = {p: exp for p, exp in _recently_joined_tiles.items() if exp > now}

    my1 = int(gw_t + gw_h * 0.12)
    my2 = int(gw_t + gw_h * 0.82)
    map_crop = safe_grab(sct, {"left": gw_l, "top": my1, "width": gw_w, "height": my2 - my1})
    if map_crop is None:
        return None

    map_gray = cv2.cvtColor(map_crop, cv2.COLOR_BGR2GRAY)

    candidates: List[Tuple[int, int, Tuple[int, int], str, float]] = []
    scale_factors = getattr(config, "RALLY_SCALE_FACTORS", [1.00, 1.04, 0.96, 1.08, 0.92, 1.12, 0.88, 0.84, 0.80, 0.72, 0.67, 1.20, 1.28])
    match_thresh = getattr(config, "RALLY_MATCH_THRESHOLD", 0.52)
    best_val = 0.0

    # 1. ENGINE 1: Universal Timer Pill (Đa ngôn ngữ 100%: Bắt các số mm:ss trên nền đen viền vàng)
    timer_tpl = _timer_template if _timer_template is not None else assets.get_rally_timer_template()
    if timer_tpl is not None:
        t_th, t_tw = timer_tpl.shape[:2]
        timer_thresh = getattr(config, "RALLY_TIMER_MATCH_THRESHOLD", 0.52)
        avatar_offset_ratio = getattr(config, "RALLY_TIMER_AVATAR_OFFSET_Y", 0.85)

        for cur_sc in scale_factors:
            cur_tw = max(15, int(t_tw * cur_sc))
            cur_th = max(10, int(t_th * cur_sc))
            if cur_tw >= map_crop.shape[1] or cur_th >= map_crop.shape[0]:
                continue

            scaled_timer = cv2.resize(
                timer_tpl,
                (cur_tw, cur_th),
                interpolation=cv2.INTER_AREA if cur_sc < 1.0 else cv2.INTER_LINEAR,
            )
            res_timer = cv2.matchTemplate(map_crop, scaled_timer, cv2.TM_CCOEFF_NORMED)
            _, max_t, _, _ = cv2.minMaxLoc(res_timer)
            if max_t > best_val:
                best_val = float(max_t)

            locs_timer = np.where(res_timer >= timer_thresh)
            for pt in zip(*locs_timer[::-1]):
                tx, ty = int(pt[0]), int(pt[1])
                score = float(res_timer[ty, tx])

                # Click rơi thẳng vào TÂM AVATAR (dịch ngược lên trên thanh timer)
                click_x = int(gw_l + tx + cur_tw // 2)
                click_y = int(my1 + ty - int(cur_th * avatar_offset_ratio))
                tile = (click_x, click_y)

                # NMS lọc trùng: nếu ô avatar này đã được thêm trong bán kính 35px thì bỏ qua
                if not any(abs(c[0] - click_x) < 35 and abs(c[1] - click_y) < 35 for c in candidates):
                    candidates.append((click_x, click_y, tile, f"TimerPill_{cur_sc:.2f}", score))

    # 2. ENGINE 2: Banner Text Templates (Dự phòng bổ trợ cho Tiếng Việt)
    for tname, tpl in _rally_templates:
        is_clean = ("clean" in tname)
        tpl_th, tpl_tw = tpl.shape[:2]
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY) if is_clean else None

        for cur_sc in scale_factors:
            cur_tw = max(10, int(tpl_tw * cur_sc))
            cur_th = max(10, int(tpl_th * cur_sc))
            if cur_tw >= map_crop.shape[1] or cur_th >= map_crop.shape[0]:
                continue

            if is_clean:
                scaled_temp = cv2.resize(
                    tpl_gray,
                    (cur_tw, cur_th),
                    interpolation=cv2.INTER_AREA if cur_sc < 1.0 else cv2.INTER_LINEAR,
                )
                res = cv2.matchTemplate(map_gray, scaled_temp, cv2.TM_CCOEFF_NORMED)
            else:
                scaled_temp = cv2.resize(
                    tpl,
                    (cur_tw, cur_th),
                    interpolation=cv2.INTER_AREA if cur_sc < 1.0 else cv2.INTER_LINEAR,
                )
                res = cv2.matchTemplate(map_crop, scaled_temp, cv2.TM_CCOEFF_NORMED)

            min_v, max_v, _, _ = cv2.minMaxLoc(res)
            if max_v > best_val:
                best_val = float(max_v)

            locs = np.where(res >= match_thresh)
            for pt in zip(*locs[::-1]):
                x, y = int(pt[0]), int(pt[1])
                score = float(res[y, x])
                click_x = int(gw_l + x + cur_tw // 2)
                click_y = int(my1 + y + int(cur_th * 1.85))
                tile = (click_x, click_y)

                # NMS lọc trùng: nếu đã được phát hiện bởi Engine 1 (Timer) hoặc template khác trong 35px thì bỏ qua
                if not any(abs(c[0] - click_x) < 35 and abs(c[1] - click_y) < 35 for c in candidates):
                    candidates.append((click_x, click_y, tile, tname, score))

    _last_best_score = best_val
    candidates.sort(key=lambda c: c[4], reverse=True)

    for click_x, click_y, tile, faction, score in candidates:
        if _is_paused or _stop_event.is_set():
            return None

        if _is_tile_in_dict(tile, _recently_joined_tiles) or _is_tile_in_dict(tile, _full_tiles_cooldown):
            continue

        rel_click_x = click_x - gw_l
        rel_click_y = click_y - my1
        ay1 = max(0, rel_click_y - 20)
        ay2 = min(map_crop.shape[0], rel_click_y + 20)
        ax1 = max(0, rel_click_x - 30)
        ax2 = min(map_crop.shape[1], rel_click_x + 30)
        avatar_crop = map_crop[ay1:ay2, ax1:ax2]

        if avatar_crop.size > 0:
            a_hsv = cv2.cvtColor(avatar_crop, cv2.COLOR_BGR2HSV)
            joined_mask = cv2.inRange(
                a_hsv,
                np.array(config.HSV_RALLY_JOINED_GREEN_LOWER, dtype=np.uint8),
                np.array(config.HSV_RALLY_JOINED_GREEN_UPPER, dtype=np.uint8),
            )
            joined_px = int(np.count_nonzero(joined_mask))
            if joined_px >= config.RALLY_JOINED_PX_THRESHOLD:
                log(f"[MAPVIEW] O ({click_x}, {click_y}) da co huy hieu 'Da tham gia' ({joined_px}px) -> Bo qua")
                _recently_joined_tiles[tile] = time.time() + 240.0
                continue

        _last_clicked_tile = tile
        log(f"[MAPVIEW] Phat hien Rally (Phe {faction.capitalize()}) tai ({click_x}, {click_y}) do khop {score:.2f} -> Mo Popup")

        # Kich hoat cua so gia lap tren man hinh phu de nhan click ngay lap tuc
        if hwnd:
            activate_window(hwnd)

        touch_tap(click_x, click_y)
        if _sleep(config.RALLY_DELAY_AFTER_MAP_CLICK):
            return None

        # Xu ly Popup chi tiet Rally (Tham gia hoac dong ve Mapview)
        is_pop, is_join = handle_rally_detail_popup(sct, vp, hwnd=hwnd)
        if is_pop:
            return "JOINED" if is_join else "FULL"
        return "CLICKED"
    return None


def scan_and_join_chat_rallies(sct: mss.MSS, vp: Tuple[int, int, int, int]) -> bool:
    """Quet cac thong bao 'Tham gia' trong khung Chat Phe Vang (chi khi duoc bat)."""
    gw_l, gw_t, gw_w, gw_h = vp

    sx = int(gw_l + gw_w * config.CHAT_SCROLL_BOTTOM_X)
    sy = int(gw_t + gw_h * config.CHAT_SCROLL_BOTTOM_Y)
    scrop = safe_grab(sct, {"left": sx - 15, "top": sy - 15, "width": 30, "height": 30})
    if scrop is not None:
        s_hsv = cv2.cvtColor(scrop, cv2.COLOR_BGR2HSV)
        purple_mask = cv2.inRange(s_hsv, np.array([125, 70, 90]), np.array([170, 255, 255]))
        if np.count_nonzero(purple_mask) > 120:
            touch_tap(sx, sy)
            _sleep(config.RALLY_DELAY_AFTER_SCROLL_CLICK)

    cx1 = int(gw_l + gw_w * config.CHAT_MESSAGES_REL_X_MIN)
    cx2 = int(gw_l + gw_w * config.CHAT_MESSAGES_REL_X_MAX)
    cy1 = int(gw_t + gw_h * config.CHAT_MESSAGES_REL_Y_MIN)
    cy2 = int(gw_t + gw_h * config.CHAT_MESSAGES_REL_Y_MAX)

    chat_crop = safe_grab(sct, {"left": cx1, "top": cy1, "width": cx2 - cx1, "height": cy2 - cy1})
    if chat_crop is None:
        return False

    buttons = _find_green_buttons(chat_crop, min_w_ratio=0.30)
    if buttons:
        buttons.sort(key=lambda b: b[1], reverse=True)
        bx, by, bw, bh = buttons[0]
        touch_tap(cx1 + bx + bw // 2, cy1 + by + bh // 2)
        _sleep(config.RALLY_DELAY_AFTER_CHAT_CLICK)
        return True
    return False


def main():
    global _is_paused
    hwnd = None
    print("=" * 60)
    print(" AUTO RALLY - Clash of Critters (Sa Hai Me Thanh)")
    print(" Phim tat: [Ctrl+Q] Bat dau / Tam dung  |  [ESC] Tam dung / Thoat")
    print("=" * 60)

    def on_toggle_pause():
        global _is_paused
        _is_paused = not _is_paused
        if not _is_paused:
            log("[HOTKEY] [DANG CHAY] Bat dau quet Mapview")
            try:
                if hwnd:
                    activate_window(hwnd)
            except Exception:
                pass
        else:
            log("[HOTKEY] [TAM DUNG] Da tam dung bot")

    def on_esc():
        global _is_paused, _last_esc_time
        now = time.time()
        # Cooldown debounce: tranh key-repeat hoac double-tap ESC lam thoat nham
        if now - _last_esc_time < 0.8:
            return
        _last_esc_time = now

        if not _is_paused:
            _is_paused = True
            log("[HOTKEY] [TAM DUNG] Da bam ESC -> Tam dung bot an toan.")
            log("[HOTKEY] -> Bam [Ctrl+Q] de chay tiep, hoac bam [ESC] lan nua de THOAT han.")
        else:
            log("[HOTKEY] [THOAT] Da bam ESC khi dang tam dung -> Dang thoat bot...")
            _stop_event.set()

    keyboard.add_hotkey("ctrl+q", on_toggle_pause)
    keyboard.add_hotkey("esc", on_esc)

    win = find_emulator_window()
    if not win:
        log("[LOI] Khong tim thay cua so gia lap Android (BlueStacks / LDPlayer / MuMu / Nox / MEmu)!")
        time.sleep(3)
        return

    hwnd = win._hWnd
    win_title = win.title
    gw_left, gw_top, gw_w, gw_h = get_game_viewport(hwnd, win_title)
    sct = mss.MSS()
    eff_vp = get_effective_viewport(sct, (gw_left, gw_top, gw_w, gw_h), force_check=True)
    log(f"[KET NOI] {win_title} | Viewport: {gw_w}x{gw_h} (Game thuc: {eff_vp[2]}x{eff_vp[3]}) tai ({eff_vp[0]}, {eff_vp[1]})")
    log("[SAN SANG] Trang thai: [TAM DUNG]. Chuyen ve Tong Mapview roi bam [Ctrl+Q] de chay.")

    rally_join_count = 0
    reward_count = 0
    last_heartbeat = time.time()

    try:
        while not _stop_event.is_set():
            if _is_paused:
                time.sleep(0.1)
                cur_t = time.time()
                if cur_t - last_heartbeat >= 30.0:
                    log("[CHO LENH] Bot dang TAM DUNG. Bam [Ctrl+Q] tren ban phim de BAT DAU.")
                    last_heartbeat = cur_t
                continue

            try:
                cur_t = time.time()
                if cur_t - last_heartbeat >= 20.0:
                    log(f"[STATUS] Dang quet Mapview (Do khop: {_last_best_score:.2f}) | Da tham gia: {rally_join_count} | Nhan qua: {reward_count}")
                    last_heartbeat = cur_t

                if not user32.IsIconic(hwnd):
                    nl, nt, nw, nh = get_game_viewport(hwnd, win_title)
                    if (nl, nt, nw, nh) != (gw_left, gw_top, gw_w, gw_h) and nw > 200 and nh > 350:
                        gw_left, gw_top, gw_w, gw_h = nl, nt, nw, nh
                        global _effective_vp
                        _effective_vp = None

                vp = get_effective_viewport(sct, (gw_left, gw_top, gw_w, gw_h))

                # 1. Kiem tra nhan thuong ket thuc Rally
                if check_and_claim_reward(sct, vp, hwnd):
                    reward_count += 1
                    log(f"[REWARD] Nhan thuong Rally #{reward_count}")
                    _sleep(0.4)
                    continue

                # 2. Quet Tong Mapview va xu ly Rally truc tiep (Trong tam 100%)
                map_res = scan_and_join_map_rallies(sct, vp, hwnd)
                if map_res:
                    if map_res == "JOINED":
                        rally_join_count += 1
                        log(f"[RALLY] Tham gia thanh cong #{rally_join_count}")
                    _sleep(0.4)
                    continue

                # 3. Kiem tra popup ton dong
                is_popup, is_joined = handle_rally_detail_popup(sct, vp, hwnd=hwnd)
                if is_popup:
                    if is_joined:
                        rally_join_count += 1
                        log(f"[RALLY] Tham gia thanh cong #{rally_join_count}")
                    _sleep(0.4)
                    continue

                # 4. Quet tin nhan Chat Phe Vang (Chi khi duoc bat trong config)
                if getattr(config, "RALLY_ENABLE_CHAT_SCAN", False):
                    if scan_and_join_chat_rallies(sct, vp):
                        _sleep(0.4)
                        continue

                time.sleep(config.RALLY_DELAY_IDLE_SLEEP)
            except (pyautogui.FailSafeException, KeyboardInterrupt):
                raise
            except Exception as e:
                log(f"[CANH BAO] {type(e).__name__}: {e}")
                time.sleep(0.5)

    except pyautogui.FailSafeException:
        log("[AN TOAN] Chuot di vao goc man hinh -> Dung bot.")
    except KeyboardInterrupt:
        log("[AN TOAN] Ctrl+C -> Dung bot.")
    except Exception as e:
        log(f"[LOI] {type(e).__name__}: {e}")
    finally:
        safe_unhook_hotkeys()
        log(f"[TONG KET] Da tham gia: {rally_join_count} | Nhan qua: {reward_count}")
        log("[KET THUC] Bot da dung an toan.")
        if getattr(sys, "frozen", False):
            print("\nNhan Enter de thoat...")
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
            print("Nhan Enter de thoat...")
            try:
                input()
            except Exception:
                pass
