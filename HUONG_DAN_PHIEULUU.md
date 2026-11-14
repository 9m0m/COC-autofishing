# Hướng Dẫn Sử Dụng Auto Phiêu Lưu Cổ Vật (Relic Adventure)
> **Sự kiện Phiêu Lưu Cổ Vật - Game Clash of Critters**  
> Hỗ trợ mọi trình giả lập Android: BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu.  
> Tương thích hoàn hảo Windows 10/11, đa màn hình và các mức DPI Scaling (100%, 125%, 150%).

---

## 1. Cơ Chế Hoạt Động & Quy Trình Khép Kín

Bot vận hành theo một vòng lặp máy trạng thái (State Machine) thông minh khép kín, nhận diện 100% qua thị giác máy tính OpenCV (Multi-scale Flex Matching kết hợp dải màu HSV và mẫu ảnh template):

1. **Khởi đầu màn (Sảnh chính - Hình 6)**:
   - Tự động nhận diện nút màu cam **"Bắt Đầu Phiêu Lưu!"**.
   - Bấm nút và chờ 2.0 giây để tải vào màn mê cung (Hình 3).

2. **Di chuyển trong mê cung (Hình 3, 4, 10, 12, 14, 15)**:
   - Tự động nhận diện nút tròn xanh ngọc **"Tiến Lên"** (kèm icon ngọn đuốc) trên mọi chặng hành trình:
     - Chặng sơ cấp (1, 2): Chỉ có nút Tiến Lên ở giữa.
     - Chặng nâng cao (11+): Xuất hiện thêm nút **"Ba Lô"** bên trái, nút **"Lv.1"** bên phải và số lượng đuốc tiêu hao tăng lên (12, 40, 50 đuốc...).
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
   - **Chờ đúng 2.0 giây** để game thoát hẳn ra sảnh chính, sau đó tự động bắt đầu lại vòng lặp mới từ đầu đến vô tận.

6. **Tự động khôi phục từ Menu Thoát / Tạm dừng ngoài ý muốn (Hình 11)**:
   - Nếu bảng tạm dừng *"Kết Thúc Lượt / Tiếp Tục / Lưu & Rời Đi"* vô tình bị mở ra, bot tự động nhận diện và bấm ngay nút **"Tiếp Tục"** để trở lại mê cung mà không bao giờ bị dừng cuộc chơi.

7. **Hệ thống Chống Treo đa tầng (Multi-layer Watchdog)**:
   - **Điểm chạm an toàn tuyệt đối**: Điểm chạm giải phóng popup và watchdog chống treo được đặt cố định tại **bức tường đá góc trên bên trái** $(X = 0.15, Y = 0.35)$, tuyệt đối không chạm vào nút "X" màu trắng ở đáy màn hình $(X = 0.50, Y = 0.95)$, loại bỏ hoàn toàn nguy cơ vô tình kích hoạt menu thoát trận.
   - **Kẹt màn hình lạ > 3.5s**: Tự động chạm nhẹ vào điểm an toàn trên tường đá để giải phóng mọi dialog thông báo, cấp độ mới hoặc quà tặng đột xuất.
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

### Cách 1: Chạy file đóng gói sẵn (Khuyên dùng - Tiện lợi nhất)
Chạy trực tiếp file:
```
dist\auto_phieuluu.exe
```
*(Chạy độc lập 100%, không cần cài đặt Python hay bất kỳ thư viện nào).*

### Cách 2: Khởi chạy nhanh qua file Batch
Nhấp đúp chuột vào file:
```
run_phieuluu.bat
```

### Cách 3: Khởi chạy bằng lệnh Python (Dành cho lập trình viên)
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
PHIEULUU_DISMISS_REL_X = 0.150   # Điểm an toàn đóng popup & chống treo (tường đá góc trên)
PHIEULUU_DISMISS_REL_Y = 0.350

# Thời gian chờ (giây):
PHIEULUU_DELAY_AFTER_ADVANCE = 2.00   # Hoạt ảnh bước đi
PHIEULUU_DELAY_POPUP_TIMING  = 1.05   # Timing 1s chờ trước khi đóng popup bảo vật
PHIEULUU_DELAY_AFTER_RESET   = 2.00   # Chờ 2s thoát sảnh bắt đầu loop mới
```

---

## 5. Các Công Nghệ & Tối Ưu Nổi Bật

- **Không chiếm chuột 100% (`restore_cursor=True`)**: Bot chỉ mượn chuột khoảng 0.08 giây để click bằng Win32 API rồi trả ngay về vị trí ban đầu của bạn. Bạn thoải mái lướt web, làm việc, xem phim mà không lo bị chuột giật hay kẹt vào game.
- **Tương thích Đa Màn Hình & DPI Scaling**: Tích hợp chế độ `Per-Monitor V2 DPI Awareness` cùng API `DwmGetWindowAttribute (DWMWA_EXTENDED_FRAME_BOUNDS)`, đảm bảo chụp trọn vẹn 100% pixel vật lý của cửa sổ giả lập trên mọi màn hình phụ (kể cả khi màn hình đặt tỉ lệ phóng to 125% hoặc 150%), triệt tiêu hoàn toàn lỗi cắt cụt đáy màn hình.
- **Quét FLEX đa tỉ lệ**: Tự động đo đạc kích thước thực tế của cửa sổ game, nhận diện tâm nút thực tế và click chính xác dù bạn phóng to hay thu nhỏ cửa sổ.
