# Bộ Công Cụ Tự Động Clash of Critters (COC-AutoTools)

Kho công cụ tự động hóa độ chính xác cao cho game **Clash of Critters** trên các trình giả lập Android phổ biến (BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu):

1. **Auto Câu Cá (Fishing Minigame)**: Tự động giật cần, khóa cứng ô vàng siêu nhỏ 2-pha, tự giải phóng thẻ bài và nhận quà (chi tiết xem bên dưới).
2. **Auto Rally Sa Hải Mê Thành (Gold Rush)**: Tự động quét và tham gia các cuộc Tổng Tấn Công trên Tổng Mapview, tự đóng popup và nhận thưởng (chi tiết xem riêng tại: **[HUONG_DAN_RALLY.md](HUONG_DAN_RALLY.md)**).
3. **Auto Phiêu Lưu Cổ Vật (Relic Adventure)**: Tự động đi mê cung, thu thập bảo vật/cổ vật mọi tier, luôn chọn chiến đấu quái vật, tự kết toán và reset vòng lặp với cơ chế chống treo đa tầng (chi tiết xem riêng tại: **[HUONG_DAN_PHIEULUU.md](HUONG_DAN_PHIEULUU.md)**).

---

## PHẦN 1: AUTO CÂU CÁ (COC-autofishing)

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
   - **Auto Câu Cá**: Chạy file `dist/auto_cauca.exe` hoặc click `run_auto.bat`.
   - **Auto Rally Sa Hải Mê Thành**: Chạy file `dist/auto_rally.exe` hoặc click `run_rally.bat`.
2. Đặt file chạy ở vị trí thuận tiện trên máy tính (ví dụ: Desktop).

---

## ⚡ Hướng dẫn sử dụng Auto Rally (Sa Hải Mê Thành - Gold Rush)

1. **Khởi động game & giả lập**:
   - Mở game *Clash of Critters* trên BlueStacks 5, LDPlayer, MuMu, Nox hoặc MEmu.
   - Bạn có thể để màn hình ở:
     - **Kênh Chat Phe Vàng** (Khuyên dùng: gom 100% rally toàn map).
     - Hoặc **Mapview Sa Hải Mê Thành** (Quét trực tiếp các ô Tổng Tấn Công chưa tham gia).
2. **Khởi chạy Auto**:
   - Chạy file `dist\auto_rally.exe` hoặc click đúp vào `run_rally.bat`.
   - Tool tự động nhận diện cửa sổ giả lập và tính toán viewport chuẩn xác.
3. **Cơ chế hoạt động**:
   - Khi có người mở Rally $\rightarrow$ Tool bấm "Tham gia".
   - Popup "Đơn Vị Tiêu Chuẩn / Xung Kích" hiện lên $\rightarrow$ Tool bấm nút xanh "Tham gia" ở đáy $\rightarrow$ Chờ chuyển sang "Chờ chấp thuận / Đã tham gia" $\rightarrow$ **Tự động click nút Back nhỏ $\hookleftarrow$** ở góc dưới bên trái để hạ popup về lại Mapview.
   - Khi kết thúc 5 phút đếm ngược $\rightarrow$ Tool tự động click nút "Xác Nhận" màu xanh để nhận quà (50 lon nước thể lực) và đóng bảng.
4. **Phím tắt điều khiển**:
   - **`Ctrl + Q`**: BẬT / TẠM DỪNG bot.
   - **`ESC`**: DỪNG và THOÁT hoàn toàn.

---

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

## PHẦN 2: AUTO RALLY SA HẢI MÊ THÀNH (COC-autorally)
- **Sự kiện:** Sa Hải Mê Thành (Gold Rush).
- **Tính năng:** Tự động quét và tham gia các cuộc Tổng Tấn Công trên Tổng Mapview, tự đóng popup và nhận thưởng 50 lon thể lực.
- **Hướng dẫn chi tiết:** Xem tại **[HUONG_DAN_RALLY.md](HUONG_DAN_RALLY.md)**.
- **Khởi chạy:** Nhấp đúp file `run_rally.bat` hoặc chạy `dist/auto_rally.exe`.

---

## PHẦN 3: AUTO PHIÊU LƯU CỔ VẬT (COC-autophieuluu)

> **Dành cho Sự Kiện: Phiêu Lưu Cổ Vật (Relic Adventure) - Game Clash of Critters**  
> Tự động hoá 100% vòng lặp khám phá mê cung, nhặt bảo vật, đánh quái và kết toán reset sảnh.

---

### 🔄 1. Quy trình hoạt động khép kín (State Machine)
Bot vận hành theo máy trạng thái nhận diện thị giác máy tính OpenCV (Template Matching đa tỉ lệ kết hợp dải màu HSV chuẩn xác 100%):

1. **Sảnh khởi đầu (Hình 6):**  
   - Tự động phát hiện nút màu cam **"Bắt Đầu Phiêu Lưu!"**.
   - Bấm nút và chờ 2.0 giây để tải vào màn mê cung.
2. **Di chuyển trong mê cung (Hình 3 & Hình 4):**  
   - Nhận diện nút tròn xanh ngọc **"Tiến Lên"** (kèm icon đuốc).
   - Bấm nút và **chờ đúng 2.0 giây** nhịp bước đi của nhân vật (tránh hoàn toàn việc spam click vô ích gây lag).
3. **Thu thập bảo vật / cổ vật (Hình 1, 5, 8, 9):**  
   - Dù là đồ tier thấp (D, C) hay tier cao (B, A, Siêu hiếm, Huyền thoại), popup đều hiển thị dòng chữ *"Chạm điểm bất kì để tiếp tục"*.
   - Bot **chờ đúng 1.0 giây theo nhịp timing của game** (game khoá cảm ứng trong 1s đầu) rồi mới chạm nhẹ điểm an toàn để đóng popup mượt mà.
4. **Gặp quái vật chắn đường (Hình 2):**  
   - Xuất hiện bảng *"Zobo Thủy Thủ chắn đường!"* với 2 thẻ lựa chọn: **Rút Lui** và **Chiến Đấu**.
   - Bot **luôn luôn chọn Chiến Đấu** (bấm thẻ bên phải có biểu tượng 2 thanh kiếm bắt chéo) bất kể tỉ lệ thắng là bao nhiêu, đúng theo yêu cầu.
   - Chờ 1.8 giây cho trận đánh diễn ra.
5. **Kết toán & Reset vòng lặp (Hình 7):**  
   - Khi chiến đấu thất bại, màn hình kết quả *"Phiêu Lưu Kết Thúc"* xuất hiện.
   - Bot tự động bấm nút màu xanh lá **"Chấp Nhận"**.
   - **Chờ đúng 2.0 giây** để game thoát ra sảnh chính, sau đó tự động bắt đầu lại vòng đi mới từ đầu đến vô tận.

---

### 🖱️ 2. Cơ chế KHÔNG CHIẾM CHUỘT 100% (Đa nhiệm lướt web / xem phim)
Khác với các phần mềm auto click thông thường chiếm giữ chuột liên tục khiến bạn không thể sử dụng máy tính, bot được tích hợp công nghệ **"Chạm tức thì & Trả chuột tự động" (`restore_cursor=True`)**:
- **Thời gian chạm cực ngắn:** Bot chỉ điều khiển chuột sang cửa sổ game trong khoảng **~0.08 giây** để gửi tín hiệu chạm cảm ứng Android qua Win32 API.
- **Tự động nhớ và trả chuột về vị trí cũ:** Ngay sau khi nhấc chuột lên, bot **ngay lập tức hoàn trả con trỏ chuột về đúng toạ độ ban đầu** mà bạn đang trỏ trên Windows.
- **Thoải mái làm việc đa nhiệm:** Bạn hoàn toàn có thể bật auto chạy ngầm, vừa lướt web, làm việc, xem YouTube, gõ văn bản trên màn hình chính (hoặc trên dàn 2 màn hình) mà con trỏ chuột không bao giờ bị giật hay bị kẹt vào game!

---

### 🎯 3. Cơ chế tự động định vị & quét màn hình chuẩn xác 100%
Bạn không cần phải căn chỉnh toạ độ thủ công, bot tự động tính toán toạ độ chuẩn xác trên mọi thiết lập:
- **Tự động nhận diện cửa sổ giả lập:** Quét và kết nối đúng cửa sổ BlueStacks 5, LDPlayer 9/5/4, MuMu Player, NoxPlayer, MEmu theo tiêu đề và tên tiến trình (`get_process_name_by_hwnd`).
- **Tự bù trừ viền tiêu đề & thanh công cụ:** Tự động trừ thanh tiêu đề trên cùng (title bar ~32px) và thanh công cụ sidebar bên phải (~44-50px) theo từng dòng giả lập để xác định đúng vùng hiển thị game (`Game Viewport`).
- **Loại trừ dải đen hai bên sườn (Pillarbox Detection):** Nếu bạn vô tình kéo dãn cửa sổ giả lập theo chiều ngang, bot tự động quét và cắt bỏ dải đen hai bên, giữ nguyên tỉ lệ khung hình chuẩn 9:16.
- **Co dãn Template thích ứng (Multi-scale Adaptive):** Tất cả các mẫu template nhận diện (Bắt đầu, Tiến lên, Chiến đấu, Chấp nhận, Popup) tự động co dãn theo tỉ lệ chiều rộng thực tế (`scale = width / 405.0`), giúp bot bấm trúng đích 100% dù bạn phóng to, thu nhỏ hay đặt giả lập ở bất kỳ góc nào trên màn hình.

---

### 🛡️ 4. Hệ thống Chống Treo đa tầng (Watchdog Protection)
- **Chống kẹt màn hình lạ (> 3.5s):** Nếu mạng lag, có thông báo đột xuất hoặc bảng quà tặng che khuất quá 3.5 giây, bot tự động chạm nhẹ vào điểm an toàn giữa màn hình để giải phóng giao diện.
- **Chống mất tiêu điểm (> 8.0s):** Tự động kích hoạt đưa cửa sổ giả lập lên phía trước (`activate_window`) và đồng bộ lại Game Viewport.
- **Phát hiện kẹt trạng thái / Hết Đuốc:** Nếu bấm nút "Tiến Lên" quá 4 lần liên tiếp mà cảnh không dịch chuyển, bot sẽ cảnh báo lên màn hình console và thử giải phóng trung tâm.

---

### 🚀 5. Hướng dẫn sử dụng & Phím tắt điều khiển

#### Cách khởi chạy:
- **Cách 1 (Khuyên dùng):** Chạy trực tiếp file `dist/auto_phieuluu.exe` (bản đóng gói sẵn, không cần cài Python).
- **Cách 2:** Nhấp đúp chuột vào file `run_phieuluu.bat`.
- **Cách 3:** Chạy lệnh: `python auto_phieuluu.py`.

#### Bảng phím tắt toàn cục (Chuẩn 100% giống Auto Câu Cá):
| Phím tắt | Trạng thái | Chức năng & Chi tiết |
| :---: | :---: | :--- |
| **`Ctrl + Q`** | **[CHỜ LỆNH]** / **[TẠM DÙNG]** | **BẮT ĐẦU / TIẾP TỤC (Resume)**: Khi mở tool hoặc sau khi tạm dừng, nhấn `Ctrl + Q` để bắt đầu/tiếp tục chạy bot. |
| **`ESC`** | **[ĐANG CHẠY]** | **TẠM DỪNG (Pause)**: Lập tức dừng quét và giải phóng chuột hoàn toàn để bạn chat/lướt web. |
| **`ESC`** | **[TẠM DỪNG]** | **THOÁT HẲN**: Nhấn ESC lần thứ 2 khi bot đang tạm dừng để tắt tool an toàn và xuất bảng tổng kết. |

#### ⚠️ Những điều cần lưu ý quan trọng:
1. **Chạy nhiều giả lập cùng lúc (`coc1`, `coc2`, `coc3`)**: Trước khi nhấn `Ctrl + Q`, bạn chỉ cần click chuột vào cửa sổ giả lập muốn chạy để Active/Focus. Bot sẽ tự động ưu tiên cửa sổ đang được chọn!
2. **Không thu nhỏ (Minimize) cửa sổ giả lập xuống Taskbar:** Bạn có thể để cửa sổ ở góc màn hình, để ở màn hình phụ hoặc để cửa sổ khác đè lên một phần, nhưng không được Minimize xuống thanh taskbar vì Windows sẽ ngưng render hình ảnh vào VRAM.
3. **Tắt chế độ Tiết kiệm tài nguyên (Eco Mode trên BlueStacks):** Nhấn `Ctrl + Shift + F` trên BlueStacks để tắt Eco Mode, đảm bảo game chạy ổn định 60 FPS khi ở chế độ nền.
4. **Di chuyển hoặc thu phóng cửa sổ:** Nhờ thuật toán Quét FLEX đa tỉ lệ, nếu bạn kéo cửa sổ giả lập sang vị trí khác hoặc phóng to/thu nhỏ, bot sẽ tự động tính toán lại tâm nút thực tế mà không bị lệch chuột.

---

## 📬 Liên hệ hỗ trợ
Nếu bạn gặp bất kỳ vấn đề gì trong quá trình sử dụng, vui lòng liên hệ qua Discord: **`@9m0m`**.
