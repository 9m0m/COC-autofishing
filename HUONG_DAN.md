# HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG AUTO CÂU CÁ (BẢN V12 ĐA GIẢ LẬP)

Tool tự động hoàn toàn: Hỗ trợ BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu.
Tự quăng cần, tự chờ cá cắn, tự căn thanh trượt siêu tốc (100+ FPS), tự nhận quà & tự vượt mọi loại popup.

---

## 1. YÊU CẦU CẤU HÌNH GIẢ LẬP (BẮT BUỘC)

Để tool nhận diện chính xác 100% toạ độ:
1. Mở giả lập của bạn (**BlueStacks**, **LDPlayer**, **Nox**, ...) -> Vào **Cài đặt (Settings)** ⚙️ -> **Hiển thị (Display)**:
   - **Độ phân giải:** Chọn chế độ **Điện thoại (Mobile / Portrait / Dọc)** tỉ lệ 9:16 (ví dụ: `720 x 1280` hoặc `1080 x 1920`).
   - **DPI:** `240` hoặc `320`.
2. Mở game, cho nhân vật đứng tại vị trí bờ hồ câu cá.
3. Không thu nhỏ (minimize) cửa sổ giả lập xuống thanh Taskbar khi đang auto.

---

## 2. HƯỚNG DẪN CÀI ĐẶT DÀNH CHO BẠN BÈ (CHỈ LÀM LẦN ĐẦU)

### Bước 1: Cài đặt Python (Nếu máy chưa có)
- Tải Python từ trang chủ: https://www.python.org/downloads/ (chọn bản Python 3.10 trở lên).
- ⚠️ **LƯU Ý CỰC KỲ QUAN TRỌNG:** Ở màn hình cài đặt đầu tiên, **bắt buộc phải tick vào ô `[v] Add python.exe to PATH`** ở dưới cùng trước khi bấm Install Now!

### Bước 2: Cài đặt thư viện tự động
- Nhấp đúp vào file **`cai_dat.bat`** trong thư mục.
- Đợi khoảng 30 giây đến khi hiện chữ *"CAI DAT HOAN TAT 100%!"*.

### Bước 3: Kiểm tra vị trí (Khuyên dùng trước khi câu thật)
- Mở game trên giả lập và đứng ở hồ câu.
- Nhấp đúp vào file **`kiem_tra_vi_tri.bat`**.
- Ảnh chụp màn hình sẽ tự động bật lên:
  + Vòng tròn xanh lá bao trúng nút quăng cần câu.
  + Khung vàng bao trọn thanh trượt minigame.
  + Vòng tròn đỏ nằm ở vị trí nút Nhận Ngay an toàn (cách xa vạch cảnh báo nút X ở đáy).
- Nếu các khung bao trúng vị trí, bạn có thể hoàn toàn yên tâm 100%!

### Bước 4: Chạy Auto Câu Cá
- Nhấp đúp chuột vào file **`run_auto.bat`**.
- Tool sẽ tự động kết nối với cửa sổ game và bắt đầu câu cá liên tục.
- **DỪNG AUTO BẤT KỲ LÚC NÀO:** Nhấn giữ phím **`q`** trên bàn phím.

---

## 3. CÁCH ĐÓNG GÓI THÀNH FILE .EXE (Dành cho người không muốn cài Python)

Nếu bạn muốn gửi cho bạn bè chỉ duy nhất 1 file `.exe`:
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

## 4. DANH SÁCH FILE KHI GỬI CHO BẠN BÈ
- `auto_cauca.py`: Mã nguồn chính của bot (Bản V12).
- `config.py`: File cấu hình toạ độ và dải màu.
- `test_preview.py`: Tool chụp ảnh kiểm tra khung ngắm.
- `cai_dat.bat`: File cài đặt thư viện tự động chỉ bằng 1 click.
- `kiem_tra_vi_tri.bat`: File kiểm tra toạ độ trong 5 giây.
- `run_auto.bat`: File khởi động auto chỉ bằng 1 click.
- `requirements.txt`: Danh sách thư viện Python.
- `HUONG_DAN.md`: File hướng dẫn này.
