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

# ==============================================================================
# 5. TOẠ ĐỘ & CẤU HÌNH CHO AUTO RALLY (SA HẢI MÊ THÀNH - GOLDRUSH)
# ==============================================================================
# A. Toạ độ tỉ lệ trong Popup Chi Tiết Rally ("Đơn Vị Tiêu Chuẩn / Xung Kích")
# Tâm nút lớn "Tham gia" ở đáy màn hình
RALLY_POPUP_JOIN_X: float = 0.580
RALLY_POPUP_JOIN_Y: float = 0.940

# Tâm nút Back nhỏ kế bên nút tham gia (góc dưới bên trái) để đóng popup về Mapview (tránh xa nút X ở giữa)
RALLY_POPUP_BACK_X: float = 0.085
RALLY_POPUP_BACK_Y: float = 0.940

# Vùng kiểm tra nút lớn ở đáy popup: (Rel X: 0.20 -> 0.95, Rel Y: 0.90 -> 0.97)
RALLY_MAIN_BTN_REL_X_MIN: float = 0.200
RALLY_MAIN_BTN_REL_X_MAX: float = 0.950
RALLY_MAIN_BTN_REL_Y_MIN: float = 0.900
RALLY_MAIN_BTN_REL_Y_MAX: float = 0.970

# B. Toạ độ tỉ lệ Popup Nhận Quà ("Tổng Tấn Công đã hoàn tất!")
# Tâm nút "Xác Nhận" màu xanh lá
RALLY_CLAIM_REWARD_X: float = 0.500
RALLY_CLAIM_REWARD_Y: float = 0.838

# Vùng kiểm tra nút "Xác Nhận" nhận quà
RALLY_REWARD_BTN_REL_X_MIN: float = 0.350
RALLY_REWARD_BTN_REL_X_MAX: float = 0.650
RALLY_REWARD_BTN_REL_Y_MIN: float = 0.800
RALLY_REWARD_BTN_REL_Y_MAX: float = 0.880

# C. Toạ độ tỉ lệ Màn hình Chat Phe Vàng
# Vùng quét các nút "Tham gia" màu xanh lá trong khung chat
CHAT_MESSAGES_REL_X_MIN: float = 0.320
CHAT_MESSAGES_REL_X_MAX: float = 0.900
CHAT_MESSAGES_REL_Y_MIN: float = 0.150
CHAT_MESSAGES_REL_Y_MAX: float = 0.820

# Nút mũi tên tím cuộn xuống tin nhắn mới nhất trong Chat (góc dưới phải)
CHAT_SCROLL_BOTTOM_X: float = 0.915
CHAT_SCROLL_BOTTOM_Y: float = 0.772

# D. Dải màu & ngưỡng nhận diện cho Rally
# Nút "Tham gia" màu xanh lá (Nút thật có > 12.000 px, ngưỡng 2500 loại bỏ 100% icon Mapview)
HSV_RALLY_GREEN_LOWER = [35, 70, 70]
HSV_RALLY_GREEN_UPPER = [85, 255, 255]
RALLY_GREEN_PX_THRESHOLD: int = 2500

# Nút xám "Chờ chấp thuận" / "Đã tham gia" / "Đã đầy" (Nút thật có > 11.000 px, ngưỡng 2500 loại bỏ 100% bóng mờ Mapview)
RALLY_GREY_SAT_MAX: int = 50
RALLY_GREY_VAL_MIN: int = 70
RALLY_GREY_VAL_MAX: int = 210
RALLY_GREY_PX_THRESHOLD: int = 2500

# Dòng chữ xanh lá "Đã tham gia" trên avatar ở Map
HSV_RALLY_JOINED_GREEN_LOWER = [35, 90, 90]
HSV_RALLY_JOINED_GREEN_UPPER = [85, 255, 255]
RALLY_JOINED_PX_THRESHOLD: int = 60

# E. Cấu hình thời gian chờ (Delays - Đơn vị: Giây)
# Thời gian giữ phím chuột (chạm cảm ứng Android an toàn)
RALLY_DELAY_TAP_HOLD: float = 0.08

# Thời gian chờ sau khi bấm nút "Tham gia" trong popup (đợi server phản hồi đổi màu nút)
RALLY_DELAY_AFTER_JOIN_CLICK: float = 0.80

# Thời gian chờ sau khi bấm nút Back nhỏ để đóng popup (đợi hoạt ảnh hạ popup)
RALLY_DELAY_AFTER_BACK_CLICK: float = 0.70

# Thời gian chờ sau khi bấm "Xác Nhận" nhận quà (đợi đóng bảng kết quả)
RALLY_DELAY_AFTER_CLAIM_REWARD: float = 0.80

# Thời gian chờ sau khi bấm "Tham gia" trong Chat (đợi game tải và mở popup)
RALLY_DELAY_AFTER_CHAT_CLICK: float = 0.90

# Thời gian chờ sau khi click Avatar trên Map (đợi tải dữ liệu ô trên map)
RALLY_DELAY_AFTER_MAP_CLICK: float = 0.90

# Thời gian chờ sau khi bấm nút cuộn tin mới trong Chat
RALLY_DELAY_AFTER_SCROLL_CLICK: float = 0.40

# Thời gian nghỉ giữa các lần quét khi ở trạng thái chờ
RALLY_DELAY_IDLE_SLEEP: float = 0.40

# Thời gian khóa bỏ qua ô đã đầy (4/4) trên Mapview
RALLY_FULL_TILE_COOLDOWN: float = 60.0

# Chế độ hoạt động: False = Focus 100% Tổng Mapview (Khuyên dùng); True = Quét cả Chat
RALLY_ENABLE_CHAT_SCAN: bool = False

