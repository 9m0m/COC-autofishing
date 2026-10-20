# Hướng dẫn cài đặt và sử dụng Auto Câu Cá (Bản V12.1 Đa Giả Lập)

Công cụ tự động câu cá cho sự kiện Câu cá trong game Clash of Critters trên các trình giả lập: BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.

---

## 1. Yêu cầu cấu hình giả lập (Bắt buộc)

Để bot nhận diện toạ độ chính xác:
1. Mở cài đặt giả lập (Settings) -> mục Hiển thị (Display):
   - Độ phân giải: Chọn chế độ Điện thoại (Portrait / 9:16), ví dụ 720x1280 hoặc 1080x1920.
   - DPI: 240 hoặc 320.
2. Mở game Clash of Critters và vào giao diện sự kiện Câu cá.
3. Không thu nhỏ (minimize) cửa sổ giả lập xuống thanh Taskbar khi đang auto.

---

## 2. Hướng dẫn sử dụng cho người dùng phổ thông

### Cách nhanh nhất (Dùng file .exe)
1. Tải file `auto_cauca.exe` từ mục Releases trên GitHub.
2. Mở game và vào sự kiện Câu cá trên giả lập.
3. Nhấp đúp vào `auto_cauca.exe`. Bot sẽ tự động kết nối và chờ lệnh.
4. Bấm phím **`Q`** (hoặc Space) để bắt đầu câu cá tự động.
5. Nhấn phím **`ESC`** bất kỳ lúc nào để dừng bot ngay lập tức.

---

## 3. Hướng dẫn cài đặt từ mã nguồn Python (Chỉ làm lần đầu)

### Bước 1: Cài đặt Python
- Tải Python từ trang chủ: https://www.python.org/downloads/ (chọn bản Python 3.10 trở lên).
- Lưu ý: Ở màn hình cài đặt đầu tiên, bắt buộc phải đánh dấu vào ô `Add python.exe to PATH` ở dưới cùng trước khi bấm Install.

### Bước 2: Cài đặt thư viện tự động
- Nhấp đúp vào file `cai_dat.bat` trong thư mục.
- Đợi khoảng 30 giây đến khi thông báo cài đặt hoàn tất.

### Bước 3: Kiểm tra vị trí (Tuỳ chọn)
- Mở game trên giả lập và vào giao diện sự kiện Câu cá.
- Nhấp đúp vào file `kiem_tra_vi_tri.bat`.
- Ảnh chụp màn hình sẽ tự động bật lên:
  - Khung tím: Vùng game thực tế sau khi trừ thanh viền giả lập.
  - Vòng tròn xanh lá: Vị trí tâm nút quăng cần câu.
  - Khung vàng: Vùng quét thanh trượt minigame.
  - Vòng tròn đỏ: Vị trí bấm nhận thưởng an toàn (cách xa nút thoát sự kiện).

### Bước 4: Chạy Auto Câu Cá
- Nhấp đúp chuột vào file `run_auto.bat`.
- Bot sẽ tự động kết nối và bắt đầu câu cá liên tục.
- Dừng bot: Nhấn phím **`ESC`** trên bàn phím bất kỳ lúc nào.

---

## 4. Cách đóng gói thành file .exe độc lập

Nếu muốn tự đóng gói lại file `.exe` từ mã nguồn:
1. Cài đặt công cụ PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
2. Đóng gói mã nguồn kèm file cấu hình:
   ```cmd
   pyinstaller --onefile --add-data "config.py;." auto_cauca.py
   ```
3. File `auto_cauca.exe` sẽ được tạo trong thư mục `dist\`.

---

## 5. Danh sách file trong dự án
- `auto_cauca.py`: Mã nguồn chính của bot (Bản V12.1).
- `config.py`: File cấu hình toạ độ tỉ lệ, dải màu HSV và thông số bù viền giả lập.
- `test_preview.py`: Công cụ chụp ảnh kiểm tra khung ngắm.
- `cai_dat.bat`: File cài đặt thư viện tự động chỉ bằng 1 click.
- `kiem_tra_vi_tri.bat`: File kiểm tra toạ độ trong 5 giây.
- `run_auto.bat`: File khởi động auto chỉ bằng 1 click.
- `requirements.txt`: Danh sách thư viện Python phụ thuộc.
- `HUONG_DAN.md`: File hướng dẫn chi tiết này.
- `README.md`: Tài liệu tổng quan dự án trên GitHub.
