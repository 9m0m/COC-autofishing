"""
Cấu hình toạ độ và thông số nhận diện cho Auto Câu Cá BlueStacks.
Đã đo đạc chính xác tâm điểm theo cả 3 bức ảnh thực tế:
- Nút câu cá: Rel X = 0.406, Rel Y = 0.814 (Chính giữa tâm nút)
- Nút Nhận Ngay: Rel X = 0.465, Rel Y = 0.870 (Chính giữa nút Nhận Ngay)
"""

# Tỉ lệ vị trí tâm nút câu cá (Chính xác tâm 100%)
BUTTON_REL_X = 0.406
BUTTON_REL_Y = 0.814

# Tỉ lệ thanh trượt mini-game
SLIDER_REL_X_MIN = 0.200
SLIDER_REL_X_MAX = 0.710
SLIDER_REL_Y_MIN = 0.660
SLIDER_REL_Y_MAX = 0.710

# Tỉ lệ nút "Nhận Ngay" ở đáy
CLAIM_REL_X = 0.465
CLAIM_REL_Y = 0.870

# Dải màu HSV
HSV_READY_GREEN_LOWER = [35, 70, 70]
HSV_READY_GREEN_UPPER = [85, 255, 255]

HSV_BITE_PURPLE_LOWER = [125, 70, 90]
HSV_BITE_PURPLE_UPPER = [175, 255, 255]

# Dải màu vàng thanh trượt
HSV_YELLOW_LOWER = [15, 70, 90]
HSV_YELLOW_UPPER = [38, 255, 255]

HSV_RED_LOWER1 = [0, 90, 90]
HSV_RED_UPPER1 = [12, 255, 255]
HSV_RED_LOWER2 = [168, 90, 90]
HSV_RED_UPPER2 = [180, 255, 255]
