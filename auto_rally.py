"""
COC-autorally: Bot tu dong tham gia Rally (Tong Tan Cong) trong su kien Sa Hai Me Thanh (Gold Rush)
cho game Clash of Critters tren cac gia lap Android (BlueStacks 5, LDPlayer 9, MuMu, Nox, MEmu).
"""

import sys
import time
import threading
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
_last_clicked_tile: Optional[Tuple[int, int]] = None
_full_tiles_cooldown: Dict[Tuple[int, int], float] = {}
_recently_joined_tiles: Dict[Tuple[int, int], float] = {}
_last_best_score: float = 0.0

# Template tieu de 'Tong Tan Cong!' tren Mapview
_rally_template = assets.get_rally_template()
_template_th, _template_tw = _rally_template.shape[:2]


def _sleep(seconds: float) -> bool:
    """Tam dung co the huy lap tuc bang ESC."""
    return sleep_check(seconds, _stop_event)


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


def handle_rally_detail_popup(sct: mss.MSS, vp: Tuple[int, int, int, int]) -> Tuple[bool, bool]:
    """
    Xu ly popup chi tiet Rally:
    - Nut xanh ('Tham gia'): bam tham gia -> cho cap nhat -> bam nut Back nho de dong popup.
    - Nut xam ('Da day' / 'Cho chap thuan'): bam nut Back nho thoat & ghi nho cooldown neu da day.
    """
    global _last_clicked_tile, _full_tiles_cooldown, _recently_joined_tiles
    gw_l, gw_t, gw_w, gw_h = vp
    x1 = int(gw_l + gw_w * config.RALLY_MAIN_BTN_REL_X_MIN)
    x2 = int(gw_l + gw_w * config.RALLY_MAIN_BTN_REL_X_MAX)
    y1 = int(gw_t + gw_h * config.RALLY_MAIN_BTN_REL_Y_MIN)
    y2 = int(gw_t + gw_h * config.RALLY_MAIN_BTN_REL_Y_MAX)

    crop = safe_grab(sct, {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1})
    if crop is None:
        return False, False

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(
        hsv,
        np.array(config.HSV_RALLY_GREEN_LOWER, dtype=np.uint8),
        np.array(config.HSV_RALLY_GREEN_UPPER, dtype=np.uint8),
    )
    green_px = int(np.count_nonzero(green_mask))

    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]
    grey_mask = (s_ch < config.RALLY_GREY_SAT_MAX) & (v_ch >= config.RALLY_GREY_VAL_MIN) & (v_ch <= config.RALLY_GREY_VAL_MAX)
    grey_px = int(np.count_nonzero(grey_mask))

    join_x = int(gw_l + gw_w * config.RALLY_POPUP_JOIN_X)
    join_y = int(gw_t + gw_h * config.RALLY_POPUP_JOIN_Y)
    back_x = int(gw_l + gw_w * config.RALLY_POPUP_BACK_X)
    back_y = int(gw_t + gw_h * config.RALLY_POPUP_BACK_Y)

    if green_px > config.RALLY_GREEN_PX_THRESHOLD:
        touch_tap(join_x, join_y)
        _sleep(config.RALLY_DELAY_AFTER_JOIN_CLICK)
        touch_tap(back_x, back_y)
        _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
        if _last_clicked_tile is not None:
            _recently_joined_tiles[_last_clicked_tile] = time.time() + 240.0
            _last_clicked_tile = None
        return True, True

    if grey_px > config.RALLY_GREY_PX_THRESHOLD:
        if _last_clicked_tile is not None:
            _full_tiles_cooldown[_last_clicked_tile] = time.time() + config.RALLY_FULL_TILE_COOLDOWN
            log(f"[RALLY] O ({_last_clicked_tile[0]}, {_last_clicked_tile[1]}) DA DAY (4/4) -> Bo qua {int(config.RALLY_FULL_TILE_COOLDOWN)}s")
            _last_clicked_tile = None
        touch_tap(back_x, back_y)
        _sleep(config.RALLY_DELAY_AFTER_BACK_CLICK)
        return True, False

    return False, False


def handle_multi_rally_selection(sct: mss.MSS, vp: Tuple[int, int, int, int]) -> bool:
    """Xu ly popup danh sach 2-3 cuoc Rally tren cung 1 o dat."""
    gw_l, gw_t, gw_w, gw_h = vp
    x1 = int(gw_l + gw_w * 0.15)
    x2 = int(gw_l + gw_w * 0.85)
    y1 = int(gw_t + gw_h * 0.25)
    y2 = int(gw_t + gw_h * 0.75)

    crop = safe_grab(sct, {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1})
    if crop is None:
        return False

    buttons = _find_green_buttons(crop, min_w_ratio=0.18)
    if buttons:
        buttons.sort(key=lambda b: b[1])
        bx, by, bw, bh = buttons[0]
        touch_tap(int(x1 + bx + bw // 2), int(y1 + by + bh // 2))
        _sleep(config.RALLY_DELAY_AFTER_CHAT_CLICK)
        return True
    return False


def scan_and_join_map_rallies(sct: mss.MSS, vp: Tuple[int, int, int, int], hwnd: Optional[int] = None) -> Optional[str]:
    """
    Quet Tong Mapview tim tieu de 'Tong Tan Cong!' qua Template Matching da ty le.
    Ho tro luoi ty le mo rong (0.88 -> 1.12) va nguong 0.66 de bat nhay 100% tren moi do phan giai.
    """
    global _last_clicked_tile, _full_tiles_cooldown, _recently_joined_tiles, _last_best_score
    gw_l, gw_t, gw_w, gw_h = vp

    now = time.time()
    _full_tiles_cooldown = {p: exp for p, exp in _full_tiles_cooldown.items() if exp > now}
    _recently_joined_tiles = {p: exp for p, exp in _recently_joined_tiles.items() if exp > now}

    my1 = int(gw_t + gw_h * 0.12)
    my2 = int(gw_t + gw_h * 0.82)
    map_crop = safe_grab(sct, {"left": gw_l, "top": my1, "width": gw_w, "height": my2 - my1})
    if map_crop is None:
        return None

    scale = gw_w / 415.0
    matches = []
    scale_factors = getattr(config, "RALLY_SCALE_FACTORS", [1.00, 0.96, 1.04, 0.92, 1.08, 0.88, 1.12])
    match_thresh = getattr(config, "RALLY_MATCH_THRESHOLD", 0.66)

    best_val = 0.0
    for factor in scale_factors:
        cur_sc = scale * factor
        cur_tw = max(10, int(_template_tw * cur_sc))
        cur_th = max(10, int(_template_th * cur_sc))
        scaled_temp = cv2.resize(
            _rally_template,
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
            if not any(abs(m[0] - x) < cur_tw * 0.6 and abs(m[1] - y) < cur_th * 0.6 for m in matches):
                matches.append((x, y, cur_tw, cur_th))
        if matches:
            break

    _last_best_score = best_val

    for x, y, cur_tw, cur_th in matches:
        click_x = int(gw_l + x + cur_tw // 2)
        click_y = int(my1 + y + cur_th + int(cur_th * 0.7))
        tile = (click_x, click_y)

        if _is_tile_in_dict(tile, _recently_joined_tiles) or _is_tile_in_dict(tile, _full_tiles_cooldown):
            continue

        ay1 = y + cur_th
        ay2 = min(map_crop.shape[0], y + cur_th + int(gw_h * 0.08))
        ax1 = max(0, x - 10)
        ax2 = min(map_crop.shape[1], x + cur_tw + 10)
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
        log(f"[MAPVIEW] Phat hien Rally tai ({click_x}, {click_y}) -> Mo Popup")

        # Kich hoat cua so gia lap tren man hinh phu de nhan click ngay lap tuc
        if hwnd:
            activate_window(hwnd)

        touch_tap(click_x, click_y)
        _sleep(config.RALLY_DELAY_AFTER_MAP_CLICK)

        # 1. Neu la o co nhieu cuoc Rally -> Click chon cuoc dau tien
        handle_multi_rally_selection(sct, vp)

        # 2. Xu ly Popup chi tiet Rally (Tham gia hoac Back nho de ve Mapview)
        is_pop, is_join = handle_rally_detail_popup(sct, vp)
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
    print("=" * 60)
    print(" AUTO RALLY - Clash of Critters (Sa Hai Me Thanh)")
    print(" Phim tat: [Ctrl+Q] Bat dau / Tam dung  |  [ESC] Thoat")
    print("=" * 60)

    def on_toggle_pause():
        global _is_paused
        _is_paused = not _is_paused
        if not _is_paused:
            log("[HOTKEY] [DANG CHAY] Bat dau quet Mapview")
            activate_window(hwnd)
        else:
            log("[HOTKEY] [TAM DUNG] Da tam dung bot")

    def on_stop():
        log("[HOTKEY] Da bam ESC -> Dang dung bot...")
        _stop_event.set()

    keyboard.add_hotkey("ctrl+q", on_toggle_pause)
    keyboard.add_hotkey("esc", on_stop)

    win = find_emulator_window()
    if not win:
        log("[LOI] Khong tim thay cua so gia lap Android (BlueStacks / LDPlayer / MuMu / Nox / MEmu)!")
        time.sleep(3)
        return

    hwnd = win._hWnd
    win_title = win.title
    gw_left, gw_top, gw_w, gw_h = get_game_viewport(hwnd, win_title)
    log(f"[KET NOI] {win_title} | Viewport: {gw_w}x{gw_h} tai ({gw_left}, {gw_top})")
    log("[SAN SANG] Trang thai: [TAM DUNG]. Chuyen ve Tong Mapview roi bam [Ctrl+Q] de chay.")

    sct = mss.MSS()
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

                vp = (gw_left, gw_top, gw_w, gw_h)

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

                # 3. Kiem tra popup ton dong (chi kich hoat neu dung nut popup that >= 2500px)
                is_popup, is_joined = handle_rally_detail_popup(sct, vp)
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
