# 🎣 AutoFishing-Android (Auto Câu Cá Siêu Tốc Đa Giả Lập)

> **Hệ thống tự động câu cá thông minh dựa trên thị giác máy tính thời gian thực (Computer Vision 100+ FPS) dành cho BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.**

---

## 🌟 Tính Năng Nổi Bật

- 📱 **Hỗ trợ đa giả lập Android:** Tự động phát hiện và kết nối với **BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu**.
- ⚡ **Thị giác máy tính tốc độ cao (100+ FPS):** Tối ưu xử lý khung hình siêu tốc bằng `MSS` + `OpenCV` với độ trễ phản xạ chỉ 3–5ms.
- 🎯 **Căn thanh trượt tự động (Auto Perfect):** Tự động nhận diện ô vàng mục tiêu và vị trí phao, nhấp trúng đích 100% nhịp Hoàn Hảo kể cả khi ô vàng co lại rất nhỏ.
- 🧠 **Cơ chế Button State Machine 4 pha độc quyền:**
  1. **Xanh lá (`green_px > 400`):** Cần trên bờ -> Tự động quăng cần.
  2. **Xám (`grey_px > 600`):** Cần dưới nước -> Yên lặng chờ cá đớp, tuyệt đối không click bậy làm giật cần hỏng mồi.
  3. **Tím (`purple_px > 700`):** Cá cắn thật -> Giật cần tức thì & khóa chặt vòng lặp kéo cá, không bị ngắt quãng bởi chữ *'Hoàn hảo!'* hay *'Rất tuyệt!'*.
  4. **Tối / Modal:** Popup kết quả -> Chạm 2 nhịp vào vị trí an toàn (`Rel Y = 0.870`), **tuyệt đối không chạm vào nút X thoát game (`Rel Y = 0.950`)**.
- 🔍 **Công cụ kiểm tra trực quan (1-Click Preview):** Chạy `kiem_tra_vi_tri.bat` để xem trước toàn bộ các khung ngắm trực quan trong 5 giây.
- 🖥️ **Chuẩn hóa Per-Monitor DPI v2:** Tương thích hoàn toàn với mọi màn hình độ phân giải Full HD, 2K, 4K và tỉ lệ scale Windows (100%, 125%, 150%).
- 🛑 **Dừng khẩn cấp:** Giữ phím `q` bất cứ lúc nào để thoát an toàn.

---

## 🔄 Sơ Đồ Trạng Thái (State Machine Flow)

```text
[BẮT ĐẦU]
    │
    ▼
[Cần trên bờ] ──── (Nút Xanh > 400 px) ────► [Quăng Cần]
    ▲                                               │
    │ (Xong vòng / Popup đóng)                     ▼
[Đóng Popup / Nhận Quà]                     [Cần dưới nước] (Nút Xám > 600 px)
    ▲                                               │ (Chờ yên lặng, không click)
    │ (Hết tím > 0.8s)                             ▼
[Minigame Kéo Cá] ◄─── (Giật Cần Tức Thì) ─── [Cá Cắn Câu] (Nút Tím > 700 px)
 (100+ FPS, bám phao vào ô vàng)
```

---

## ⚙️ Cấu Hình Giả Lập Khuyến Nghị

Để đảm bảo toạ độ chính xác 100%:
1. Mở giả lập (**BlueStacks / LDPlayer / Nox**) -> Vào **Cài đặt (Settings)** ⚙️ -> **Hiển thị (Display)**:
   - **Chế độ hiển thị:** Chọn **Điện thoại (Mobile / Portrait / Dọc)** tỉ lệ 9:16.
   - **Độ phân giải khuyến nghị:** `720 x 1280` hoặc `1080 x 1920`.
   - **DPI:** `240` hoặc `320`.
2. Mở game và di chuyển nhân vật đến hồ câu cá.

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 👉 Dành cho người dùng (Khuyên dùng)
1. Cài đặt **Python 3.10+** từ [python.org](https://www.python.org/downloads/).
   > ⚠️ **LƯU Ý:** Khi cài đặt, bắt buộc phải tick vào ô: `[v] Add python.exe to PATH`.
2. Tải mã nguồn về máy: Bấm nút xanh **`Code`** -> **`Download ZIP`** -> Giải nén ra thư mục.
3. Nhấp đúp vào **`cai_dat.bat`** (chỉ cần chạy lần đầu để cài thư viện).
4. Nhấp đúp vào **`kiem_tra_vi_tri.bat`** để xem ảnh kiểm tra khung ngắm (5 giây).
5. Nhấp đúp vào **`run_auto.bat`** để bắt đầu câu cá tự động!

---

### 👉 Dành cho Developer
```bash
# 1. Clone repository
git clone https://github.com/<your-username>/AutoFishing-Android.git
cd AutoFishing-Android

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Kiểm tra khung nhận diện
python test_preview.py

# 4. Khởi động bot
python auto_cauca.py
```

---

## 📦 Đóng Gói File .EXE (Chạy không cần cài Python)

Nếu muốn chia sẻ cho bạn bè 1 file duy nhất để chạy ngay:
```bash
pip install pyinstaller
pyinstaller --onefile auto_cauca.py
```
File `auto_cauca.exe` sẽ được tạo trong thư mục `dist\`.

---

## 📁 Cấu Trúc Dự Án

```text
├── auto_cauca.py          # Logic chính của Bot (State Machine V12)
├── config.py              # Toạ độ tỉ lệ và ngưỡng màu HSV
├── test_preview.py        # Tool kiểm tra căn chỉnh khung hình trực quan
├── requirements.txt       # Danh sách thư viện Python phụ thuộc
├── cai_dat.bat            # Script 1-click kiểm tra môi trường & cài thư viện
├── run_auto.bat           # Script 1-click khởi động Bot
├── kiem_tra_vi_tri.bat    # Script 1-click chụp và mở ảnh xem trước khung ngắm
├── HUONG_DAN.md           # Hướng dẫn chi tiết bằng tiếng Việt
├── LICENSE                # Giấy phép MIT
└── README.md              # Giới thiệu & tài liệu tổng quan
```

---

## ⚖️ Giấy Phép (License)

Dự án được phân phối dưới giấy phép [MIT License](LICENSE).
