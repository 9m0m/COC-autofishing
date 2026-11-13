# Hướng Dẫn Sử Dụng Auto Rally (Tổng Tấn Công)
> **Sự kiện Sa Hải Mê Thành (Gold Rush) - Game Clash of Critters**  
> Hỗ trợ mọi trình giả lập Android: BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu.

---

## 1. Cơ Chế Hoạt Động (Focus 100% Tổng Mapview)

Khác với việc theo dõi tin nhắn trong khung Chat (dễ bị trôi tin nhắn khi có 5–6 cuộc Rally liên tục), bot hoạt động tập trung 100% trên màn hình **Tổng Mapview** (bản đồ bao quát 4 góc phe):

1. **Nhận diện chính xác 100% qua Template Matching đa tỉ lệ**:
   - Quét tiêu đề *"Tổng Tấn Công!"* trên toàn bộ bản đồ tổng với ngưỡng khớp `>= 0.72`.
   - Loại bỏ triệt để các nhận diện sai từ icon Mạng Hạ Gục, avatar tuyển thủ, danh hiệu, khung viền hay hiệu ứng ngọn lửa.
2. **Quy trình tham gia khép kín**:
   - Phát hiện ô có Rally -> Click vào tâm avatar ô đất.
   - Khi Popup chi tiết mở lên -> Tự động click nút **"Tham gia"** màu xanh lá.
   - Ngay sau đó -> Tự động click nút **Back nhỏ** `↩` (`Rel X: 0.105, Rel Y: 0.935`) ở góc dưới bên trái để hạ popup xuống, đưa màn hình trở về lại Mapview.
3. **Cơ chế chống lặp ô đã đầy (4/4)**:
   - Nếu vào ô đã đủ người (4/4) hoặc ô đã tham gia trước đó, bot tự động nhận diện nút xám, bấm nút Back nhỏ để thoát và khóa bỏ qua ô đó trong **60 giây**.
4. **Hỗ trợ ô có nhiều cuộc tấn công**:
   - Tự động nhận diện danh sách 2–3 cuộc tấn công trên cùng 1 ô đất và click tham gia lần lượt từ trên xuống dưới.
5. **Tự động nhận thưởng kết thúc trận**:
   - Tự động phát hiện bảng thông báo kết quả và click nút **"Xác Nhận"** màu xanh lá để nhận 50 lon thể lực.

---

## 2. Phím Tắt Điều Khiển

Bot sử dụng cơ chế công tắc lật (Toggle Switch) thông qua phím tắt toàn cục (Global Hotkeys):

| Phím tắt | Chức năng | Mô tả |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | **Bắt đầu / Tạm dừng** | - Khi vừa bật tool: Bot ở trạng thái `[TẠM DỪNG]` để bạn chuẩn bị.<br>- Bấm `Ctrl + Q`: Bot chuyển sang `[ĐANG CHẠY]` và quét Mapview.<br>- Bấm `Ctrl + Q` lần nữa: Tạm dừng ngay lập tức, giải phóng chuột để bạn tự do thao tác.<br>- Bấm `Ctrl + Q` tiếp: Tiếp tục chạy bình thường. |
| **`ESC`** | **Dừng và Thoát** | Hủy toàn bộ hotkey, xuất tổng kết số Rally đã vào và thoát an toàn. |

---

## 3. Các Cách Khởi Chạy

### Cách 1: Chạy file thực thi độc lập (Khuyên dùng)
Chạy trực tiếp file `dist/auto_rally.exe` (không cần cài đặt môi trường Python).

### Cách 2: Chạy nhanh qua file Batch
Nhấp đúp chuột vào file `run_rally.bat` trong thư mục gốc dự án.

### Cách 3: Chạy qua dòng lệnh Python
```bash
python auto_rally.py
```

---

## 4. Thiết Lập Màn Hình Tối Ưu (Đa Nhiệm / Lướt Web)

Bot sử dụng chuột thật của Windows (`user32.SetCursorPos`) để gửi thao tác chạm cảm ứng. Phiên bản mới đã được tích hợp cơ chế **tự động lưu và trả chuột về vị trí cũ**:

### Lưu ý quan trọng cho BlueStacks (Tránh bị khựng hình khi chạy ngầm):
- **Tắt chế độ Tiết kiệm tài nguyên (Eco Mode)**: Nhấn tổ hợp phím **`Ctrl + Shift + F`** trên BlueStacks hoặc bấm vào biểu tượng công tơ mét trên thanh công cụ bên phải để tắt chế độ tiết kiệm.
- **Tốc độ khung hình khi chạy ngầm**: Vào Cài đặt BlueStacks -> Hiệu năng (Performance) -> Đảm bảo khung hình đạt 60 FPS để giả lập không tự động giảm xuống 1 FPS khi bạn đang lướt web trên màn hình chính.

### Thiết lập 2 màn hình (Lý tưởng nhất):
- Kéo cửa sổ BlueStacks / LDPlayer sang **Màn hình phụ** và mở sẵn màn hình Tổng Mapview.
- Trên **Màn hình chính**, bạn có thể lướt web, làm việc hoặc xem YouTube thoải mái.
- **Cơ chế tự động trả chuột**: Khi phát hiện có Rally, bot tự động kích hoạt cửa sổ giả lập, di chuyển chuột sang click trong khoảng **1.5 giây**, sau đó **ngay lập tức trả chuột về đúng vị trí cũ trên Màn hình chính** cho bạn tiếp tục làm việc.

### Thiết lập 1 màn hình:
- **Chia đôi màn hình**: Trình duyệt để nửa bên trái, giả lập để nửa bên phải.
- **Không để cửa sổ khác che khuất hoàn toàn giả lập**: Bot cần chụp màn hình nhìn thấy bản đồ game để quét.
- Khi bot đang thực hiện click Rally (~1.5 giây), thả lỏng chuột một thoáng để bot click xong. Tránh giằng chuột vào sát 4 góc viền màn hình để không kích hoạt ngắt an toàn (`FailSafeException`).

---

## 5. Cấu Trúc Mã Nguồn & Tự Đóng Gói (Build)

Dự án được thiết kế theo kiến trúc module hóa sạch sẽ:
- `emulator.py`: Tầng giao tiếp Win32 API, phát hiện cửa sổ giả lập, tính toán Game Viewport, DPI awareness, chuột và chụp màn hình.
- `assets.py`: Quản lý hình ảnh mẫu tiêu đề Rally nhúng dạng Base64 và bộ nhớ đệm RAM.
- `config.py`: Lưu trữ hằng số toạ độ tỉ lệ, ngưỡng màu HSV và các khoảng thời gian chờ (delay).
- `auto_rally.py`: Kịch bản điều khiển máy trạng thái Rally chính.

### Đóng gói lại file thực thi `.exe`:
Chạy file script đóng gói tự động:
```bash
build_rally.bat
```
Hoặc dùng lệnh PyInstaller:
```bash
pyinstaller auto_rally.spec --noconfirm
```
File thực thi hoàn chỉnh sẽ được xuất ra thư mục `dist/auto_rally.exe`.
