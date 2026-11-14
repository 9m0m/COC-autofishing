# Hướng Dẫn Sử Dụng Auto Phiêu Lưu Cổ Vật (Relic Adventure)
> **Sự kiện Phiêu Lưu Cổ Vật - Game Clash of Critters**  
> Hỗ trợ mọi trình giả lập Android: BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu.

---

## 1. Cơ Chế Hoạt Động & Quy Trình Khép Kín

Bot vận hành theo một vòng lặp máy trạng thái (State Machine) thông minh khép kín, nhận diện 100% qua thị giác máy tính OpenCV (Template Matching đa tỉ lệ kết hợp dải màu HSV):

1. **Khởi đầu màn (Hình 6 - Sảnh chính)**:
   - Tự động nhận diện nút màu cam **"Bắt Đầu Phiêu Lưu!"**.
   - Bấm nút và chờ 2.0 giây để tải vào màn mê cung (Hình 3).

2. **Di chuyển trong mê cung (Hình 3 & Hình 4)**:
   - Tự động nhận diện nút tròn xanh ngọc **"Tiến Lên"** (kèm icon đuốc).
   - Bấm "Tiến Lên" và **chờ đúng 2.0 giây** cho nhân vật thực hiện hoạt ảnh bước đi (tránh spam phím vô ích gây giật lag).

3. **Thu thập bảo vật / cổ vật (Hình 1, 5, 8, 9)**:
   - Dù là đồ tier thấp (D, C) hay tier cao (B, A, Cổ vật siêu hiếm / Huyền thoại), popup đều hiển thị dòng chữ *"Chạm điểm bất kì để tiếp tục"*.
   - Bot **chờ đúng 1.0 giây** theo cơ chế timing của game (game khoá cảm ứng trong 1s đầu) rồi mới chạm nhẹ vào điểm an toàn trên màn hình để đóng popup mượt mà.

4. **Gặp quái vật chắn đường (Hình 2)**:
   - Khi xuất hiện bảng *"Zobo Thủy Thủ chắn đường!"* với 2 lựa chọn **Rút Lui** và **Chiến Đấu**:
   - Bot **luôn luôn chọn Chiến Đấu** (bấm thẻ bên phải có biểu tượng 2 thanh kiếm bắt chéo) bất kể tỉ lệ thắng là bao nhiêu, đúng như bạn yêu cầu.
   - Chờ 1.8 giây cho hoạt ảnh trận đánh diễn ra.

5. **Kết toán & Reset vòng lặp (Hình 7)**:
   - Nếu chiến đấu thất bại, màn hình kết quả *"Phiêu Lưu Kết Thúc"* xuất hiện.
   - Bot tự động bấm nút màu xanh lá **"Chấp Nhận"**.
   - **Chờ đúng 2.0 giây** để game thoát hẳn ra sảnh chính, sau đó tự động bắt đầu lại vòng lặp mới từ đầu.

6. **Hệ thống Chống Treo đa tầng (Multi-layer Watchdog)**:
   - **Kẹt màn hình lạ > 3.5s**: Tự động chạm nhẹ vào điểm an toàn giữa màn hình để giải phóng mọi dialog thông báo, cấp độ mới hoặc quà tặng đột xuất.
   - **Kẹt quá 8.0s**: Tự động kích hoạt lại cửa sổ giả lập (`activate_window`), quét lại toạ độ Game Viewport.
   - **Bảo vệ kẹt cùng một trạng thái**: Nếu bấm "Tiến Lên" quá 4 lần liên tiếp mà cảnh không đổi (ví dụ: đã hết Đuốc / Lửa hoặc game mất mạng), bot sẽ phát cảnh báo trên màn hình console và thử giải phóng trung tâm.

---

## 2. Phím Tắt Điều Khiển (Chuẩn 100% Giống Auto Câu Cá)

| Phím tắt | Trạng thái | Chức năng & Hành vi |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | Khi đang **[CHỜ LỆNH]** / **[TẠM DÙNG]** | **BẮT ĐẦU / TIẾP TỤC (Resume)**: Bot tự động đồng bộ lại toạ độ cửa sổ mới nhất và tiếp tục chạy vòng lặp phiêu lưu. |
| **`ESC`** | Khi đang **[CHẠY]** | **TẠM DỪNG (Pause)**: Dừng quét ngay lập tức, giải phóng chuột hoàn toàn để bạn chat/làm việc. |
| **`ESC`** | Khi đang **[TẠM DỪNG]** | **THOÁT HẲN**: Tắt tool an toàn và in bảng tổng kết số bảo vật / bước đi. |

> [!TIP]
> **Hỗ trợ chạy nhiều giả lập cùng lúc (`coc1`, `coc2`, `coc3`)**:  
> Trước khi nhấn `Ctrl + Q`, bạn chỉ cần click chuột vào cửa sổ giả lập muốn chạy để Active/Focus. Bot sẽ tự động nhận diện cửa sổ đang được chọn làm mục tiêu ưu tiên!

---

## 3. Cách Khởi Chạy

### Cách 1: Khởi chạy nhanh qua file Batch (Khuyên dùng)
Nhấp đúp chuột vào file:
```
run_phieuluu.bat
```

### Cách 2: Khởi chạy bằng lệnh Python
Mở Terminal hoặc PowerShell tại thư mục này và gõ:
```bash
python auto_phieuluu.py
```

---

## 4. Tùy Chỉnh Toạ Độ & Thời Gian (Nếu Cần)

Tất cả các thông số toạ độ tỉ lệ và thời gian chờ đều nằm tập trung tại file `config.py` (Mục số 6):

```python
# Toạ độ tỉ lệ chuẩn:
PHIEULUU_START_REL_X   = 0.570   # Nút "Bắt Đầu Phiêu Lưu!"
PHIEULUU_START_REL_Y   = 0.855
PHIEULUU_ADVANCE_REL_X = 0.505   # Nút "Tiến Lên"
PHIEULUU_ADVANCE_REL_Y = 0.820
PHIEULUU_FIGHT_REL_X   = 0.700   # Nút "Chiến Đấu" (bên phải)
PHIEULUU_FIGHT_REL_Y   = 0.795
PHIEULUU_SETTLE_REL_X  = 0.500   # Nút "Chấp Nhận" kết toán
PHIEULUU_SETTLE_REL_Y  = 0.925

# Thời gian chờ (giây):
PHIEULUU_DELAY_AFTER_ADVANCE = 2.00   # Hoạt ảnh bước đi
PHIEULUU_DELAY_POPUP_TIMING  = 1.05   # Timing 1s chờ trước khi đóng popup bảo vật
PHIEULUU_DELAY_AFTER_RESET   = 2.00   # Chờ 2s thoát sảnh bắt đầu loop mới
```

---

## 5. Lưu Ý Tối Ưu

- **Chế độ đa nhiệm**: Bot tự động lưu vị trí con trỏ chuột và trả chuột về vị trí cũ trên màn hình Windows (`restore_cursor=True`), giúp bạn thoải mái lướt web, xem video mà không bị giật chuột.
- **Tỉ lệ khung hình giả lập**: Khuyến nghị giữ cửa sổ giả lập ở tỉ lệ dọc chuẩn (Portrait 9:16). Nếu bạn kéo dãn ngang, bot có sẵn thuật toán phát hiện và loại trừ dải đen hai bên (`Pillarbox`) để toạ độ luôn chính xác 100%.
