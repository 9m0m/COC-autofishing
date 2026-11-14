# [COMING SOON] Hướng Dẫn Auto Rally Sa Hải Mê Thành (Tổng Tấn Công)
> ⏳ **TRẠNG THÁI: TÍNH NĂNG ĐANG PHÁT TRIỂN & HOÀN THIỆN (COMING SOON)**  
> Tính năng tự động quét và tham gia các cuộc Tổng Tấn Công (Rally) trong sự kiện Sa Hải Mê Thành hiện đang trong giai đoạn tối ưu hóa thuật toán nhận diện bản đồ đa phe và xử lý tỉ lệ khung hình. Bản phát hành chính thức sẽ ra mắt trong bản cập nhật tới!

---

## 1. Mục Tiêu & Cơ Chế Định Hướng (Thiết Kế Dự Kiến)

Khác với việc theo dõi tin nhắn trong khung Chat (dễ bị trôi tin nhắn khi có 5–6 cuộc Rally liên tục), bot được thiết kế để hoạt động tập trung 100% trên màn hình **Tổng Mapview** (bản đồ bao quát 4 góc phe):

1. **Nhận diện chính xác qua Template Matching đa tỉ lệ**:
   - Quét tiêu đề *"Tổng Tấn Công!"* trên toàn bộ bản đồ tổng với ngưỡng khớp thích ứng.
   - Phân biệt rõ các góc bản đồ (Vàng, Xanh, Đỏ, Tím) để chống nhiễu màu nền.
2. **Quy trình tham gia khép kín**:
   - Phát hiện ô có Rally -> Click vào tâm avatar ô đất.
   - Khi Popup chi tiết mở lên -> Tự động click nút **"Tham gia"** màu xanh lá.
   - Ngay sau đó -> Tự động click nút **Back nhỏ** `↩` ở góc dưới bên trái để hạ popup xuống, đưa màn hình trở về lại Mapview.
3. **Cơ chế chống lặp ô đã đầy (4/4)**:
   - Nếu vào ô đã đủ người (4/4) hoặc ô đã tham gia trước đó, bot tự động nhận diện nút xám, bấm nút Back nhỏ để thoát và khóa bỏ qua ô đó trong 60 giây.
4. **Tự động nhận thưởng kết thúc trận**:
   - Tự động phát hiện bảng thông báo kết quả và click nút **"Xác Nhận"** màu xanh lá để nhận 50 lon thể lực.

---

## 2. Phím Tắt Điều Khiển (Dự Kiến)

| Phím tắt | Trạng thái | Chức năng & Mô tả |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | [Chờ lệnh] / [Tạm dừng] | Bắt đầu hoặc tiếp tục quét Mapview. |
| **`ESC`** | [Đang chạy] | Tạm dừng ngay lập tức và giải phóng chuột. |
| **`ESC` (lần 2)** | [Tạm dừng] | Thoát hoàn toàn chương trình. |

---

## 3. Tiến Độ & Lộ Trình Phát Triển

- [x] Thiết kế cấu trúc máy trạng thái (State Machine).
- [x] Tạo kho mẫu template đa phe Base64 (Vàng, Xanh, Đỏ, Tím).
- [ ] Hoàn thiện thuật toán bù trừ dải đen (Pillarbox) trên các màn hình kéo dãn ngang.
- [ ] Tối ưu hóa tốc độ quét bản đồ và kiểm thử thực tế trên nhiều loại thiết bị.
- [ ] Đóng gói phiên bản thực thi độc lập `.exe` chính thức.

> *Thông tin phát hành chính thức và file chạy `.exe` sẽ được thông báo ngay khi hoàn tất thử nghiệm!*
