# COC-autofishing

Công cụ tự động câu cá cho sự kiện Câu cá trong game Clash of Critters trên các trình giả lập Android (BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu).

---

## Tải về bản chạy ngay (.exe)

Nếu không muốn cài đặt Python hay thao tác dòng lệnh, bạn có thể tải bản đóng gói sẵn:

> **[Tải file auto_cauca.exe tại GitHub Releases](https://github.com/9m0m/COC-autofishing/releases/latest)**

---

## Hướng dẫn sử dụng nhanh

Để bot nhận diện toạ độ chính xác, hãy làm theo đúng thứ tự 3 bước sau:

### Bước 1: Chuẩn bị giả lập và game
1. Cài đặt độ phân giải giả lập về chế độ **Điện thoại (Portrait / 9:16)**, ví dụ `720x1280` hoặc `1080x1920`. DPI khuyến nghị: `240` hoặc `320`.
2. Mở game Clash of Critters và vào giao diện sự kiện **Câu cá**.

### Bước 2: Mở bot
- **Nếu dùng file `.exe`:** Nhấp đúp vào file `auto_cauca.exe`.
- **Nếu chạy từ mã nguồn Python:** Nhấp đúp vào file `run_auto.bat` (hoặc gõ `python auto_cauca.py`).

Bot sẽ tự động kết nối với cửa sổ giả lập và ở trạng thái chờ sẵn sàng.

### Bước 3: Điều khiển bằng phím tắt
- **Bắt đầu câu:** Nhấn phím **`Q`** (hoặc phím Space) để bot bắt đầu quăng cần và câu cá tự động.
- **Dừng bot:** Nhấn phím **`ESC`** bất kỳ lúc nào để dừng bot ngay lập tức (bấm ở bất kỳ đâu, không cần bấm vào cửa sổ dòng lệnh).

---

## Cơ chế hoạt động

Bot theo dõi màu sắc của nút câu cá ở góc dưới màn hình để tự động xử lý:

- **Nút Xanh lá (Sẵn sàng):** Quăng cần xuống nước.
- **Nút Xám (Đang thả mồi):** Bot giữ yên lặng chờ cá cắn, tuyệt đối không click nhầm làm giật cần hỏng mồi.
- **Nút Tím (Cá cắn câu):** Giật cần ngay lập tức và bật chế độ quét thanh trượt minigame 100+ FPS. Khi phao đỏ chạy trúng dải vàng, bot nhấp tức thì để đạt nhịp Hoàn Hảo.
- **Màn hình tối (Bảng nhận cá):** Tự động chạm nhận thưởng tại toạ độ an toàn (`Rel Y = 0.870`), tránh hoàn toàn nút X thoát sự kiện ở đáy màn hình.

Nếu game bị giật lag hoặc kẹt bảng thông báo quá 2.5 giây, bot tự động chạm giải phóng màn hình để tiếp tục vòng câu mới.

---

## Chạy từ mã nguồn Python (Dành cho lập trình viên)

Yêu cầu môi trường: **Python 3.10** trở lên trên Windows.

```bash
# 1. Tải mã nguồn về máy
git clone https://github.com/9m0m/COC-autofishing.git
cd COC-autofishing

# 2. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 3. (Tuỳ chọn) Kiểm tra khung ngắm toạ độ trước khi câu
python test_preview.py

# 4. Khởi động bot câu cá
python auto_cauca.py
```

---

## Cấu trúc thư mục

```text
├── auto_cauca.py          # Mã nguồn điều khiển chính (State Machine V12.1)
├── config.py              # Toạ độ tỉ lệ, ngưỡng màu HSV và bù viền giả lập
├── test_preview.py        # Công cụ chụp và kiểm tra khung ngắm trực quan
├── requirements.txt       # Danh sách thư viện phụ thuộc
├── cai_dat.bat            # Script 1-click cài đặt thư viện tự động
├── run_auto.bat           # Script 1-click khởi động bot
├── kiem_tra_vi_tri.bat    # Script 1-click kiểm tra toạ độ
└── HUONG_DAN.md           # Hướng dẫn chi tiết bằng tiếng Việt
```
