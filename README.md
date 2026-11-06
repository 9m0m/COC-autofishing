# COC-autofishing (Auto Câu Cá Clash of Critters)

Công cụ tự động câu cá độ chính xác cao cho sự kiện Câu cá trong game **Clash of Critters** trên các trình giả lập Android phổ biến (BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu).

---

## ⚠️ LƯU Ý ĐẶC BIỆT QUAN TRỌNG (BẮT BUỘC ĐỌC TRƯỚC KHI DÙNG)

> [!CAUTION]
> **1. KIỂM TRA DÒNG LOG `[KET NOI]` KHI VỪA MỞ TOOL:**
> - Khi mở tool lên, bot sẽ quét các cửa sổ giả lập đang chạy và in ra dòng log:
>   `[KET NOI] 'Tên cửa sổ' (tên tiến trình) | Game: WxH tại (X, Y)`
> - **Bạn PHẢI nhìn kỹ dòng log này xem ĐÚNG cửa sổ giả lập mà bạn đang muốn câu chưa** (đặc biệt khi mở nhiều giả lập cùng lúc hoặc đang chạy đa nhiệm).
> - Nếu tool nhận nhầm cửa sổ giả lập khác: Hãy đóng tool lại, click chuột vào cửa sổ giả lập bạn muốn câu để kích hoạt nó, rồi mở lại tool.
>
> **2. TUYỆT ĐỐI KHÔNG DI CHUYỂN CỬA SỔ GIẢ LẬP KHI TOOL ĐANG CÂU:**
> - Khi bot đã kết nối, toạ độ các nút bấm và thanh trượt được định vị chuẩn xác theo vị trí cửa sổ lúc đó.
> - **Nếu bạn dùng chuột kéo/di chuyển cửa sổ giả lập sang vị trí khác trên màn hình trong lúc bot đang chạy**, con trỏ chuột của bot sẽ bị bấm lệch sang vị trí cũ $\rightarrow$ dẫn đến **click trượt, quăng cần hụt và câu thất bại!**
> - **Cách xử lý nếu lỡ di chuyển cửa sổ:** Nhấn phím **`ESC`** để tạm dừng tool $\rightarrow$ sắp xếp cửa sổ giả lập nằm cố định $\rightarrow$ nhấn **`Ctrl + Q`** để tool tự động đồng bộ lại toạ độ mới nhất rồi câu tiếp.
>
> **3. KHÔNG DÙNG CHUỘT KHI BOT ĐANG CÂU:**
> - Bot mô phỏng trực tiếp chuột máy tính để giật cần và bắt phao mini-game ở tốc độ mili-giây. Bạn không được dùng chuột làm việc khác khi bot đang hoạt động.
> - Muốn dùng chuột làm việc khác: Nhấn **`ESC`** để tạm dừng bất cứ lúc nào!

---

## 🎮 Bảng phím tắt điều khiển (Hotkeys)

Để an toàn tuyệt đối và tránh việc người dùng vô tình bấm nhầm khi đang chat/nhắn tin Zalo/Discord, tool sử dụng tổ hợp phím chuyên dụng:

| Phím tắt | Trạng thái | Chức năng chi tiết |
| :---: | :---: | :--- |
| **`Ctrl + Q`** | Chờ lệnh / Tạm dừng | **BẮT ĐẦU** lượt câu mới hoặc **TIẾP TỤC (Resume)** sau khi tạm dừng. |
| **`ESC`** | Đang chạy auto | **TẠM DÙNG KHẨN CẤP (Pause)** ngay lập tức và giải phóng chuột cho người dùng. |
| **`ESC` (lần 2)** | Đang tạm dừng | **THOÁT HẲN** chương trình auto. |

*(Người dùng có thể thoải mái tạm dừng tool rồi nhắn tin, gõ phím `Space` hoặc chữ cái tiếng Việt với Unikey mà bot không bao giờ bị kích hoạt nhầm).*

---

## 📖 Hướng dẫn sử dụng từng bước (Step-by-Step)

### Bước 1: Cài đặt màn hình giả lập (Chỉ cần làm 1 lần đầu)
1. Mở phần **Cài đặt (Settings)** của trình giả lập (BlueStacks, LDPlayer, MuMu, Nox, MEmu).
2. Vào mục **Hiển thị (Display)**:
   - Chọn chế độ hiển thị: **Điện thoại (Khổ dọc / Portrait / tỉ lệ 9:16)**.
   - Độ phân giải khuyến nghị: `720x1280` hoặc `1080x1920`.
   - Chỉ số DPI: `240` hoặc `320`.
3. Lưu cài đặt và khởi động lại giả lập nếu được nhắc.

### Bước 2: Tải file chạy Auto về máy
1. Tải bản chạy sẵn mới nhất (chỉ duy nhất 1 file `.exe`, không cần cài thêm Python hay bất kỳ thư viện nào):
   > **[Nhấn vào đây để tải file auto_cauca.exe tại GitHub Releases](https://github.com/9m0m/COC-autofishing/releases/latest)**
2. Đặt file `auto_cauca.exe` ở vị trí thuận tiện trên máy tính (ví dụ: Desktop).

### Bước 3: Mở game và vào màn hình câu cá
1. Khởi động game Clash of Critters trên giả lập.
2. Vào khu vực sự kiện **Cuộc Thi Câu Cá** sao cho nhìn thấy mặt nước và nút câu cá ở góc dưới.
3. Để cửa sổ giả lập ở vị trí cố định trên màn hình (không thu nhỏ / minimize cửa sổ xuống taskbar).

### Bước 4: Mở file `auto_cauca.exe` và kiểm tra Log
1. Nhấp đúp chuột vào file `auto_cauca.exe`.
2. Quan sát dòng thông báo màu trắng trên terminal:
   ```text
   [KET NOI] 'BlueStacks App Player' (hd-player) | Game: 540x960 tai (2400, 32)
   ```
   **Kiểm tra xem tên giả lập và toạ độ đã đúng với cửa sổ bạn muốn câu chưa.**
3. Sau khi xác nhận đúng, nhấn tổ hợp phím **`Ctrl + Q`** để bắt đầu.

### Bước 5: Thư giãn và nhận thành quả
- Bot sẽ tự động hoàn toàn:
  1. Thả mồi câu (`[1/4]`).
  2. Chờ cá cắn và giật cần chuẩn xác theo màu tím (`[2/4]`).
  3. Kéo cá qua mini-game thanh trượt với cơ chế 2-Pha tốc độ cao (`[3/4]`).
  4. Đóng các loại thẻ bài kỷ lục, cá mới, cá mập và bấm nhận thưởng (`[4/4]`).

---

## ⚡ Các công nghệ & cơ chế tối ưu tích hợp sẵn

- **Cơ chế 2-Pha (2-Phase Slider Lock):** Tự động phát hiện và **khóa cứng toạ độ ô vàng** ngay khi xuất hiện, cho phép bắt trúng 100% kể cả ô vàng siêu nhỏ (20px) ở các lượt click cuối mà không sợ phao che khuất.
- **Cô lập rãnh trượt (Spatial Rail Isolation):** Loại bỏ hoàn toàn nhiễu từ chữ *"Hoàn Hảo!"* và các tia sáng lấp lánh bay phía trên thanh trượt, triệt tiêu lỗi click hụt bị trừ 2 giây (`-2s`).
- **Khử nhiễu pháo hoa giấy (Confetti Filter):** Phân biệt chính xác giữa phao đỏ thật và pháo hoa giấy rơi trên các màn hình thẻ bài kỷ lục (như Cá Mập Giày), giúp bot tự động thoát ván kéo cá sau 0.35s mà không bị treo.
- **Tự giải phóng đa tầng (Popup Recovery):** Tự động đóng popup phần thưởng (con sò, rương, thẻ kỷ lục) và tự cứu kẹt nếu mất cần dưới nước quá 3 giây.
- **Tự động đồng bộ toạ độ (Dynamic Viewport Sync):** Tự động quét lại toạ độ cửa sổ mới nhất mỗi khi Resume hoặc bắt đầu vòng câu mới nếu bạn lỡ di chuyển cửa sổ.

---

## ❓ Câu hỏi thường gặp (FAQ)

1. **Bấm `Ctrl + Q` nhưng bot không quăng cần?**
   - Nhìn dòng `[KET NOI]` xem bot có kết nối nhầm sang cửa sổ giả lập khác đang chạy ngầm không.
   - Đảm bảo cửa sổ giả lập không bị thu nhỏ (minimize) xuống thanh Taskbar.
   - Đảm bảo màn hình game đang ở giao diện câu cá có nút tròn màu xanh.

2. **Lỡ kéo di chuyển cửa sổ giả lập sang góc khác thì làm sao?**
   - Nhấn **`ESC`** để tạm dừng bot.
   - Thả chuột ra và nhấn **`Ctrl + Q`** $\rightarrow$ bot sẽ tự động đo lại toạ độ mới nhất của cửa sổ và câu tiếp bình thường!

3. **Tôi muốn dừng lại để chat Zalo/Discord thì làm thế nào?**
   - Chỉ cần nhấn **`ESC`**. Bot sẽ nhả chuột ngay lập tức. Bạn có thể chat, gõ phím Space thoải mái. Khi nào muốn câu tiếp thì bấm **`Ctrl + Q`**.

---

## 📬 Liên hệ hỗ trợ
Nếu bạn gặp bất kỳ vấn đề gì trong quá trình sử dụng, vui lòng liên hệ qua Discord: **`@9m0m`**.
