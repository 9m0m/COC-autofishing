# COC-autofishing

Công cụ tự động câu cá cho game Clash of Critters trên các trình giả lập Android (BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu) sử dụng thị giác máy tính thời gian thực (Computer Vision 100+ FPS).

---

## Tải về bản chạy ngay (.exe)

Nếu không muốn cài đặt Python hay thao tác dòng lệnh, bạn có thể tải bản đóng gói sẵn:

> **[Tải file auto_cauca.exe tại GitHub Releases](https://github.com/9m0m/COC-autofishing/releases/latest)**

---

## Hướng dẫn sử dụng nhanh

Để bot nhận diện toạ độ chính xác, hãy làm theo đúng thứ tự 3 bước sau:

### Bước 1: Chuẩn bị giả lập và game
1. Cài đặt độ phân giải giả lập về chế độ **Điện thoại (Portrait / 9:16)**, ví dụ `720x1280` hoặc `1080x1920`. DPI khuyến nghị: `240` hoặc `320`.
2. Mở game Clash of Critters và di chuyển nhân vật đến vị trí hồ câu cá.

### Bước 2: Chạy bot
- **Nếu dùng file `.exe`:** Nhấp đúp vào file `auto_cauca.exe`.
- **Nếu chạy từ mã nguồn Python:** Nhấp đúp vào file `run_auto.bat` (hoặc gõ `python auto_cauca.py`).

Bot sẽ tự động quét và kết nối với cửa sổ giả lập đang mở, tính toán phần viền/thanh công cụ và bắt đầu câu cá tự động.

### Bước 3: Dừng bot khi cần
- Bất kỳ lúc nào muốn dừng, hãy **nhấn giữ phím `q`** trên bàn phím. Bot sẽ dừng an toàn và thông báo tổng số cá đã câu.

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

## Nguyên lý hoạt động

Bot vận hành dựa trên máy trạng thái 4 pha (Button State Machine) kết hợp quét dải màu HSV và định vị phao:

1. **Trên bờ (Nút xanh lá):** Bot bấm quăng cần câu xuống nước.
2. **Dưới nước (Nút xám):** Cần đang thả chờ cá đớp. Bot giữ yên lặng tuyệt đối, không click nhầm làm giật cần hỏng mồi.
3. **Cá cắn câu (Nút tím):** Bot giật cần lập tức và chuyển sang chế độ quét thanh trượt minigame tốc độ cao (100+ FPS). Phao đỏ chạm ô vàng sẽ bấm chuẩn xác nhịp Hoàn Hảo.
4. **Nhận quà (Popup kết quả):** Bot tự động bấm nhận thưởng tại toạ độ an toàn (`Rel Y = 0.870`), hoàn toàn cách xa nút X thoát game ở đáy màn hình.

Nếu game bị lag hoặc kẹt bảng thông báo quá 2.5 giây, bot có cơ chế tự giải cứu để tiếp tục vòng câu mới mà không cần can thiệp thủ công.

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
├── HUONG_DAN.md           # Hướng dẫn chi tiết bằng tiếng Việt
└── LICENSE                # Giấy phép mã nguồn mở MIT
```

---

## Giấy phép

Dự án được phân phối theo giấy phép [MIT License](LICENSE).
