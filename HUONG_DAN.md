# HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG AUTO CÂU CÁ (ĐA GIẢ LẬP)

Tool tự động hoàn toàn: Hỗ trợ BlueStacks, LDPlayer, Nox, MuMu. Tự thả cần, tự giật khi cá cắn, tự căn thanh trượt siêu tốc (100+ FPS), tự nhận quà & tự vượt mọi loại popup.

---

## 1. YÊU CẦU CẤU HÌNH GIẢ LẬP (BLUESTACKS / LDPLAYER / NOX)

Để bot nhận diện đúng 100% toạ độ:
1. Mở giả lập của bạn (**BlueStacks**, **LDPlayer**, **Nox**, ...) -> Vào **Cài đặt (Settings)** -> **Hiển thị (Display)**:
   - **Độ phân giải:** Chọn chế độ **Điện thoại (Mobile / Portrait / Dọc)** tỉ lệ 9:16 (ví dụ: `720 x 1280` hoặc `1080 x 1920`).
2. Vào game, đứng tại khu vực câu cá.
3. Không thu nhỏ (minimize) cửa sổ giả lập xuống thanh Taskbar khi đang auto (có thể để hiển thị ở một góc màn hình).

---

## 2. HƯỚNG DẪN DÀNH CHO BẠN BÈ (CÀI ĐẶT LẦN ĐẦU)

### Bước 1: Cài đặt Python (Nếu máy chưa có)
- Tải Python từ trang chủ: https://www.python.org/downloads/ (bản 3.10 trở lên).
- **LƯU Ý QUAN TRỌNG:** Khi cài đặt, nhớ tick vào ô **"Add python.exe to PATH"** trước khi bấm Install.

### Bước 2: Cài đặt thư viện tự động
- Nháy đúp chuột vào file **`cai_dat.bat`** trong thư mục.
- Đợi 30 giây đến khi hiện chữ *"CAI DAT HOAN TAT!"*.

### Bước 3: Chạy Auto
- Nháy đúp chuột vào file **`run_auto.bat`** (hoặc chuột phải chọn *Run as administrator* nếu BlueStacks chạy quyền admin).
- Bot sẽ tự động kết nối với BlueStacks và bắt đầu câu cá!
- **DỪNG AUTO BẤT KỲ LÚC NÀO:** Nhấn giữ phím **`q`** trên bàn phím.

---

## 3. CÁCH ĐÓNG GÓI THÀNH FILE .EXE (Dành cho người không muốn cài Python)

Nếu bạn muốn gửi cho bạn bè chỉ duy nhất 1 file `.exe` để họ nhấp đúp là chơi luôn:
1. Mở CMD tại thư mục này, cài đặt PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
2. Đóng gói code thành file exe:
   ```cmd
   pyinstaller --onefile auto_cauca.py
   ```
3. Sau khi chạy xong, file `auto_cauca.exe` sẽ nằm trong thư mục `dist\`. Bạn chỉ cần nén file `auto_cauca.exe` đó lại và gửi cho bạn bè!

---

## 4. DANH SÁCH FILE CẦN GỬI CHO BẠN BÈ (Nếu gửi source code)
- `auto_cauca.py`: Mã nguồn chính của bot.
- `config.py`: File cấu hình toạ độ và dải màu.
- `cai_dat.bat`: File cài đặt thư viện tự động chỉ bằng 1 click.
- `run_auto.bat`: File khởi động auto chỉ bằng 1 click.
- `requirements.txt`: Danh sách thư viện Python.
- `HUONG_DAN.md`: File hướng dẫn này.
