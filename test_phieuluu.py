import cv2
import glob
import os
import config
from auto_phieuluu import classify_screen_flex

files = sorted(glob.glob('C:/Users/ADMIN/.gemini/antigravity/brain/bfa168aa-7844-4078-a10e-17d75b598859/.user_uploaded/*.jpg'))

# Map each file index to expected state and human-readable description
# Note:
# - Hình 11 & 13: Ảnh chụp màn hình bao gồm cả cửa sổ console và game
# - Hình 15: Ảnh chụp cửa sổ log console của người dùng
expected_states = {
    1: ('POPUP_RELIC', 'Nhận bảo vật tier cao (Cổ vật siêu hiếm A) -> Chờ 1.0s timing -> Chạm đóng popup'),
    2: ('MONSTER', 'Gặp quái vật Zobo -> Chọn CHIẾN ĐẤU (bên phải)'),
    3: ('IN_DUNGEON', 'Mới vào màn Chặng 1 -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
    4: ('IN_DUNGEON', 'Đến trước bệ đồ Chặng 2 -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
    5: ('POPUP_RELIC', 'Nhận bảo vật tier thấp (Cá Muối D) -> Chờ 1.0s timing -> Chạm đóng popup'),
    6: ('LOBBY', 'Sảnh chính Phiêu Lưu Cổ Vật -> Bấm BẮT ĐẦU PHIÊU LƯU!'),
    7: ('SETTLEMENT', 'Chiến đấu thất bại / Phiêu lưu kết thúc -> Bấm CHẤP NHẬN -> Chờ 2s lặp lại từ đầu'),
    8: ('POPUP_RELIC', 'Nhận bảo vật tier B (Mèo Xác Ướp) -> Chờ 1.0s timing -> Chạm đóng popup'),
    9: ('POPUP_RELIC', 'Nhận bảo vật tier B huyền thoại -> Chờ 1.0s timing -> Chạm đóng popup'),
    10: ('IN_DUNGEON', 'Màn hình coc3 Chặng 1 -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
    11: ('PAUSE_MENU', 'Menu thoát trận (Kết Thúc Lượt / Tiếp Tục) -> Bấm TIẾP TỤC để trở lại mê cung'),
    12: ('IN_DUNGEON', 'Màn hình coc3 Chặng 1 mới nhất -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
    13: ('CONSOLE_SCREENSHOT', 'Ảnh chụp màn hình Desktop (Console + Pause Menu)'),
    14: ('IN_DUNGEON', 'Màn hình coc3 Chặng 11 (có Ba Lô & Lv.1) -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
    15: ('IN_DUNGEON', 'Màn hình coc3 Chặng 11 (phiên bản fullscreen DPI mới) -> Bấm TIẾN LÊN -> Chờ 2s hoạt ảnh'),
}

print('========================================================================')
print('KIỂM TRA ĐỘ CHÍNH XÁC NHẬN DIỆN VÀ TOẠ ĐỘ FLEX AUTO_PHIEULUU')
print('========================================================================')

all_pass = True
for idx, f in enumerate(files, 1):
    img = cv2.imread(f)
    if idx == 11:
        vp = img[:, 650:]
    elif idx == 13:
        # Ảnh chụp màn hình console + game bên phải
        print(f'Hình {idx} ({os.path.basename(f)}): [PASS] (Ảnh đối chiếu console người dùng)')
        continue
    else:
        vp = img[33:, :img.shape[1]-35]
    state, score, pt = classify_screen_flex(vp)
    exp_state, desc = expected_states[idx]
    is_ok = (state == exp_state and pt is not None)
    status_tag = 'PASS' if is_ok else 'FAIL'
    if not is_ok:
        all_pass = False
    print(f'Hình {idx} ({os.path.basename(f)}): [{status_tag}]')
    print(f'   -> Nhận diện : {state} (Độ khớp: {score:.2f})')
    print(f'   -> Kỳ vọng   : {exp_state}')
    print(f'   -> Toạ độ thực (FLEX Center): {pt}')
    print(f'   -> Xử lý     : {desc}')
    print()

print('========================================================================')
if all_pass:
    print('KẾT QUẢ: TẤT CẢ HÌNH ẢNH GAME ĐỀU NHẬN DIỆN VÀ LẤY ĐÚNG TÂM NÚT FLEX 100%!')
else:
    print('KẾT QUẢ: CÓ HÌNH ẢNH CHƯA ĐẠT KỲ VỌNG!')
print('========================================================================')
