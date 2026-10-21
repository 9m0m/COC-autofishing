"""
Cấu hình toạ độ và thông số nhận diện cho Auto Câu Cá Đa Giả Lập.
Đo đạc chính xác theo tỉ lệ chuẩn màn hình dọc (Portrait 9:16) trên BlueStacks, LDPlayer, Nox, MuMu.
- Nút câu cá: Rel X = 0.406, Rel Y = 0.814 (Tâm nút câu)
- Nút Nhận Ngay: Rel X = 0.465, Rel Y = 0.870 (Nút nhận thưởng an toàn, tránh nút X)
- Thanh trượt minigame: X [0.200 -> 0.710], Y [0.660 -> 0.710]
"""

# ==============================================================================
# 1. TOẠ ĐỘ TỈ LỆ (THEO CHIỀU RỘNG & CAO CỦA CỬA SỔ GIẢ LẬP)
# ==============================================================================
# Tâm nút câu cá (Trên bờ / Dưới nước / Khi cá cắn)
BUTTON_REL_X: float = 0.406
BUTTON_REL_Y: float = 0.814

# Vùng thanh trượt mini-game kéo cá (Bao trọn 100% thanh trượt, đường ray và phao câu)
SLIDER_REL_X_MIN: float = 0.165
SLIDER_REL_X_MAX: float = 0.835
SLIDER_REL_Y_MIN: float = 0.605
SLIDER_REL_Y_MAX: float = 0.730

# Vị trí nút "Nhận Ngay" & vùng an toàn đóng popup
# (Nằm ngoài popup kỷ lục, trúng nút nhận thưởng cá thường, tuyệt đối không chạm nút X)
CLAIM_REL_X: float = 0.465
CLAIM_REL_Y: float = 0.870

# Vị trí tâm thẻ bài (Đóng popup "Kỷ Lục Đội Mới", "Cá Mới", "Kỷ Lục Cá Nhân")
CARD_REL_X: float = 0.500
CARD_REL_Y: float = 0.480

# ==============================================================================
# 2. BÙ SAI SỐ VIỀN CỬA SỔ THEO TỪNG GIẢ LẬP
# ==============================================================================
# Thông số bù trừ viền: (title_bar_px, sidebar_left_px, sidebar_right_px)
# Tất cả các giả lập Android phổ biến trên Windows đều đặt thanh công cụ ở bên PHẢI (bên trái = 0px).
EMULATOR_VIEWPORT_OFFSETS: dict = {
    "bluestacks": (32, 0, 50),   # BlueStacks 5: thanh công cụ nằm bên phải ~50px
    "app player": (32, 0, 50),   # BlueStacks App Player
    "hd-player":  (32, 0, 50),   # BlueStacks 5 process
    "ldplayer":   (34, 0, 44),   # LDPlayer 9: thanh công cụ nằm bên phải ~44px
    "dnplayer":   (34, 0, 44),   # LDPlayer process
    "nox":        (32, 0, 46),   # NoxPlayer: thanh công cụ nằm bên phải ~46px
    "mumu":       (32, 0,  0),   # MuMu Player: không có sidebar cố định, thanh tab ~32px
    "nemu":       (32, 0,  0),   # MuMu Player process (NemuPlayer)
    "memu":       (32, 0, 44),   # MEmu: thanh công cụ nằm bên phải ~44px
}

# ==============================================================================
# 3. DẢI MÀU HSV & NGƯỠNG NHẬN DIỆN
# ==============================================================================
# Trạng thái 1: Nút xanh lá sẵn sàng thả cần (Trên bờ)
HSV_READY_GREEN_LOWER = [35, 70, 70]
HSV_READY_GREEN_UPPER = [85, 255, 255]
GREEN_PX_THRESHOLD: int = 400

# Trạng thái 2: Nút xám dưới nước (Cần đã thả, đang chờ cá đớp)
# Màu xám có độ bão hòa rất thấp (S < 50) và độ sáng vừa phải (80 <= V <= 220)
GREY_SATURATION_MAX: int = 50
GREY_VALUE_MIN: int = 80
GREY_VALUE_MAX: int = 220
GREY_PX_THRESHOLD: int = 600

# Trạng thái 3: Nút tím rực khi cá cắn câu thật sự & trong trận kéo cá
HSV_BITE_PURPLE_LOWER = [125, 70, 90]
HSV_BITE_PURPLE_UPPER = [175, 255, 255]
PURPLE_PX_THRESHOLD: int = 700

# Trạng thái 4: Ô vàng mục tiêu trên thanh trượt
HSV_YELLOW_LOWER = [15, 70, 90]
HSV_YELLOW_UPPER = [38, 255, 255]
YELLOW_MAX_WIDTH: int = 130  # Nếu rộng hơn 130px là chữ 'Hoàn hảo!' lóe sáng

# Phao đỏ di chuyển trên thanh trượt (quét 2 dải đỏ của HSV)
HSV_RED_LOWER1 = [0, 90, 90]
HSV_RED_UPPER1 = [12, 255, 255]
HSV_RED_LOWER2 = [168, 90, 90]
HSV_RED_UPPER2 = [180, 255, 255]

# ==============================================================================
# 4. GIỚI HẠN THỜI GIAN AN TOÀN
# ==============================================================================
# Timeout tối đa cho 1 ván kéo cá (MINIGAME_SLIDER).
# Nếu vượt quá giới hạn này mà vẫn chưa kết thúc -> tự reset vòng câu mới.
# Giá trị 45s đủ cho cả cá kỷ lục lớn nhất.
MINIGAME_MAX_DURATION: int = 45
