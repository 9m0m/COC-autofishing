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

# Vùng thanh trượt mini-game kéo cá
SLIDER_REL_X_MIN: float = 0.200
SLIDER_REL_X_MAX: float = 0.710
SLIDER_REL_Y_MIN: float = 0.660
SLIDER_REL_Y_MAX: float = 0.710

# Vị trí nút "Nhận Ngay" & vùng an toàn đóng popup
# (Nằm ngoài popup kỷ lục, trúng nút nhận thưởng cá thường, tuyệt đối không chạm nút X)
CLAIM_REL_X: float = 0.465
CLAIM_REL_Y: float = 0.870

# ==============================================================================
# 2. BÙ SAI SỐ VIỀN CỬA SỔ ĐA GIẢ LẬP (FIX CRITICAL - SIDEBAR OFFSET)
# ==============================================================================
# Mỗi giả lập có thanh tiêu đề (title bar) và thanh công cụ (sidebar) khác nhau.
# Sidebar CÓ THỂ nằm bên TRÁI (LDPlayer, Nox, MEmu) hoặc bên PHẢI (BlueStacks).
# Phải trừ phần sidebar ra trước khi nhân với tọa độ tỉ lệ.
#
# Cấu trúc: (title_bar_px, sidebar_left_px, sidebar_right_px)
# - title_bar_px    : Chiều cao thanh tiêu đề phía trên (px)
# - sidebar_left_px : Chiều rộng thanh công cụ bên TRÁI (px) — LDPlayer, Nox, MEmu
# - sidebar_right_px: Chiều rộng thanh công cụ bên PHẢI (px) — BlueStacks 5
#
# Đo thực nghiệm trên chế độ Portrait 9:16 (720x1280 / 1080x1920).
EMULATOR_VIEWPORT_OFFSETS: dict = {
    # Tên keyword (lowercase): (title_bar_px, sidebar_left_px, sidebar_right_px)
    "bluestacks": (32, 0, 50),   # BlueStacks 5 — sidebar công cụ bên PHẢI ~50px
    "app player": (32, 0, 50),   # BlueStacks App Player (tên cửa sổ thay thế)
    "ldplayer":   (30, 55, 0),   # LDPlayer 9 — sidebar điều khiển bên TRÁI ~55px
    "nox":        (30, 65, 0),   # NoxPlayer — sidebar bên TRÁI ~65px
    "mumu":       (28, 0,  0),   # MuMu Player — không sidebar
    "memu":       (30, 55, 0),   # MEmu — sidebar bên TRÁI ~55px
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
