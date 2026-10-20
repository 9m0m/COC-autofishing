# 🎣 AutoFishing-Android (Auto Câu Cá Siêu Tốc Đa Giả Lập)

> **Công cụ tự động câu cá thông minh dựa trên thị giác máy tính (Computer Vision) thời gian thực dành cho BlueStacks 5, LDPlayer, NoxPlayer, MuMu Player, MEmu.**

---

## 🌟 Tính Năng Nổi Bật

- 📱 **Hỗ trợ đa giả lập Android:** Tự động kết nối BlueStacks, LDPlayer (LDPlayer 9), NoxPlayer, MuMu Player, MEmu.
- ⚡ **Thị giác máy tính tốc độ cao (100+ FPS):** Sử dụng `MSS` + `OpenCV` tối ưu xử lý từng khung hình chỉ 3–5ms, phản xạ nhanh gấp 50 lần người thật.
- 🎯 **Căn thanh trượt tự động (Auto Perfect):** Tự động nhận diện ô vàng và vị trí phao câu, nhấp trúng đích 100% kể cả khi ô vàng thu nhỏ.
- 🐟 **Xử lý trọn vẹn mọi loại cá:** Từ cá thường 1–2 nhịp cho đến cá boss/kỷ lục giằng co 10–15 nhịp (Cá Mập Búa, Cá Đuối Đỏ, Cá Ngừ...).
- 🛡️ **Tự động nhận thưởng & đóng popup:** Tự đóng mọi loại modal (Cá thường, Kỷ lục cá nhân, Kỷ lục team, Xếp hạng server) an toàn, tuyệt đối không chạm vào nút 'X' thoát game.
- 🖥️ **Hỗ trợ Per-Monitor DPI v2:** Tự động thích ứng với mọi độ phân giải màn hình và tỉ lệ DPI scaling (100%, 125%, 150%, 2K, 4K).
- 🛑 **Dừng khẩn cấp:** Giữ phím `q` bất cứ lúc nào để dừng bot ngay lập tức.

---

## ⚙️ Cấu Hình Giả Lập Khuyến Nghị (Bắt buộc cho cả BlueStacks & LDPlayer)

Trước khi chạy bot, hãy đảm bảo cấu hình giả lập của bạn như sau:
1. Mở giả lập (**BlueStacks**, **LDPlayer**, **Nox**, ...) -> Vào **Cài đặt (Settings)** ⚙️ -> **Nâng cao / Hiển thị (Display)**.
2. Tại mục **Độ phân giải hiển thị (Resolution)**: Chọn chế độ **Điện thoại (Mobile / Portrait / Dọc)** tỉ lệ 9:16 (ví dụ: `720 x 1280` hoặc `1080 x 1920`).
3. Mở game, đứng sẵn tại vị trí câu cá.

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 👉 Cách 1: Dành cho người dùng thông thường (Khuyên dùng)
1. Cài đặt **Python** (bản 3.10 trở lên) từ [python.org](https://www.python.org/downloads/).
   > ⚠️ **LƯU Ý QUAN TRỌNG:** Khi cài đặt Python, **bắt buộc phải tick vào ô `Add python.exe to PATH`** ở dưới cùng trước khi bấm Install!
2. Tải mã nguồn về máy: Bấm nút xanh **`Code`** ở trên -> Chọn **`Download ZIP`** -> Giải nén ra thư mục.
3. Nhấp đúp chuột vào file **`cai_dat.bat`** (chỉ cần làm lần đầu tiên, đợi đến khi hiện thông báo thành công).
4. Mở BlueStacks vào game, sau đó nhấp đúp vào **`run_auto.bat`** để chạy bot!

---

### 👉 Cách 2: Chạy trực tiếp từ dòng lệnh (Dành cho Developer)
```bash
# 1. Clone repository
git clone https://github.com/<your-username>/AutoFishing-BlueStacks.git
cd AutoFishing-BlueStacks

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Chạy tool
python auto_cauca.py
```

---

## 📦 Đóng Gói Thành File .EXE (Chạy không cần cài Python)

Nếu bạn muốn tạo file thực thi duy nhất để gửi cho bạn bè không rành công nghệ:
```bash
pip install pyinstaller
pyinstaller --onefile auto_cauca.py
```
Sau khi hoàn tất, file `auto_cauca.exe` sẽ nằm trong thư mục `dist\`. Người nhận chỉ cần nhấp đúp là chạy luôn!

---

## 📁 Cấu Trúc Dự Án

```text
├── auto_cauca.py      # Mã nguồn logic chính của Bot
├── config.py          # Toạ độ tỉ lệ và ngưỡng màu HSV
├── test_preview.py    # Tool kiểm tra căn chỉnh khung hình BlueStacks
├── requirements.txt   # Danh sách thư viện Python
├── cai_dat.bat        # Script 1-click tự động cài thư viện
├── run_auto.bat       # Script 1-click khởi động Bot
├── .gitignore         # Danh sách file loại trừ
└── README.md          # Tài liệu hướng dẫn
```

---

## ⚖️ Giấy Phép (License)

Dự án được phân phối dưới giấy phép [MIT License](LICENSE). Được tự do sử dụng và tùy biến cho mục đích cá nhân.
