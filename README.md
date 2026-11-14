# Bộ Công Cụ Tự Động Clash of Critters (COC-AutoTools)

Tập hợp công cụ tự động hóa cho game Clash of Critters trên các trình giả lập Android (BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu).

Các công cụ:
1. **Auto Câu Cá (auto_cauca.exe)**: Tự động giật cần, khóa ô vàng 2 pha, tự nhận quà và đóng thẻ bài.
2. **Auto Phiêu Lưu Cổ Vật (auto_phieuluu.exe)**: Tự động đi mê cung, nhặt cổ vật mọi tier, luôn chọn chiến đấu, tự kết toán và reset vòng lặp. Chi tiết: [HUONG_DAN_PHIEULUU.md](HUONG_DAN_PHIEULUU.md).
3. **Auto Rally Sa Hải Mê Thành [Coming Soon]**: Đang phát triển, xem [HUONG_DAN_RALLY.md](HUONG_DAN_RALLY.md).

---

### Tải bản build chạy ngay (.exe)

Tải bản phát hành mới nhất tại: **[GitHub Releases](https://github.com/9m0m/COC-autofishing/releases/latest)**

- `auto_cauca.exe`: File chạy Auto Câu Cá
- `auto_phieuluu.exe`: File chạy Auto Phiêu Lưu Cổ Vật
- Chạy trực tiếp trên Windows, không cần cài đặt Python.

---

## 1. Lưu ý quan trọng về chuột (Chiếm quyền điều khiển chuột)

Cả hai công cụ đều dùng API hệ thống Windows (`SetCursorPos` và `mouse_event`) để đưa trỏ chuột đến toạ độ trên màn hình và click. Vì vậy, **cả hai tool đều chiếm quyền chuột khi hoạt động**:

- **Auto Câu Cá (auto_cauca.exe) - Chiếm chuột 100% liên tục:**  
  Minigame câu cá yêu cầu bám thanh trượt liên tục ở tốc độ mili-giây. Tool sẽ giữ con trỏ chuột trong suốt chu trình câu. Tuyệt đối không đụng vào chuột hoặc làm việc khác khi tool đang câu vì sẽ làm lệch toạ độ và đứt cước. Khi cần dùng máy tính, nhấn `ESC` để tạm dừng.

- **Auto Phiêu Lưu (auto_phieuluu.exe) - Chiếm chuột ngắt quãng (Không thể vừa làm việc vừa chạy):**  
  Tool có lưu toạ độ cũ và trả lại con trỏ chuột sau mỗi lần bấm (~0.08 giây). Tuy nhiên, cứ mỗi 1-2 giây tool lại giật con trỏ chuột về giả lập để click một lần. Do đó, bạn **không thể vừa làm việc (soạn thảo, lướt web, kéo thả file) vừa bật auto**. Việc di chuột làm việc khác trong lúc tool đang chạy sẽ khiến chuột bị giật sang giả lập, dẫn đến click nhầm vào phần mềm đang làm việc hoặc làm bot click trượt toạ độ trong game.

**Kết luận:** Khi đã bật auto chạy, hãy để máy tính tự động thao tác. Nếu cần dùng máy tính làm việc khác, hãy nhấn `ESC` để tạm dừng bot trước.

---

## 2. Cách để tool quét và bắt đúng cửa sổ giả lập

Khi trên màn hình mở nhiều phần mềm hoặc nhiều tab giả lập, tool có thể quét nhầm cửa sổ. Để tool nhận diện chính xác 100%:

1. **Thu nhỏ các cửa sổ khác:** Thu nhỏ (Minimize) toàn bộ trình duyệt, Discord, thư mục... Chỉ để duy nhất cửa sổ trình giả lập hiển thị trên màn hình trước khi mở tool.
2. **Kích hoạt cửa sổ game:** Dùng chuột click vào bên trong cửa sổ giả lập để đưa nó lên trạng thái active/focus (đang được chọn).
3. **Mở tool và kiểm tra log [KET NOI]:**  
   Mở file `.exe`, quan sát ngay dòng log đầu tiên:
   ```text
   [KET NOI] 'BlueStacks App Player' (hd-player) | Game: 540x960 tai (1920, 32)
   ```
   - Nếu tên cửa sổ hoặc toạ độ chưa đúng giả lập cần chạy: Đóng tool, click chọn lại cửa sổ giả lập mong muốn, rồi mở lại tool.
   - Khi đã thấy đúng cửa sổ: Nhấn `Ctrl + Q` để bắt đầu.
4. **Không che khuất hoặc thu nhỏ giả lập xuống Taskbar:** Tool sử dụng cơ chế chụp và nhận diện hình ảnh trực tiếp trên màn hình. Cửa sổ game phải luôn hiển thị trọn vẹn. Nếu cửa sổ bị che khuất một phần hoặc thu nhỏ xuống Taskbar, Windows sẽ ngừng render hình ảnh và bot không thể thao tác được.
5. **Khi chạy nhiều giả lập (coc1, coc2...):** Xếp các cửa sổ giả lập riêng biệt trên màn hình (không để cửa sổ này đè lên cửa sổ kia). Muốn chạy cửa sổ nào thì click vào cửa sổ đó trước, rồi nhấn `Ctrl + Q`.

---

## 3. Phím tắt điều khiển chung

| Phím tắt | Trạng thái | Chức năng |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | Chờ lệnh / Tạm dừng | Bắt đầu hoặc Tiếp tục (Resume) chạy auto. |
| **`ESC`** | Đang chạy | Tạm dừng khẩn cấp (Pause) ngay lập tức và giải phóng con trỏ chuột. |
| **`ESC` (lần 2)** | Đang tạm dừng | Thoát hẳn chương trình. |

---

## 4. Hướng dẫn nhanh Auto Câu Cá (auto_cauca.exe)

1. Cài đặt giả lập: Khổ dọc (Portrait 9:16), độ phân giải khuyến nghị `720x1280` hoặc `1080x1920`.
2. Mở minigame Câu cá trong game (thấy mặt nước và nút quăng cần).
3. Thu nhỏ các ứng dụng khác, click vào giả lập, mở file `auto_cauca.exe`.
4. Xem log `[KET NOI]`, nhấn `Ctrl + Q` để bắt đầu.
5. Bot tự động quăng mồi, giật cá, căn ô vàng và đóng thẻ bài kỷ lục.

---

## 5. Hướng dẫn nhanh Auto Phiêu Lưu Cổ Vật (auto_phieuluu.exe)

1. Mở sự kiện Phiêu Lưu Cổ Vật trong game (ở sảnh hoặc trong mê cung).
2. Thu nhỏ các ứng dụng khác, click vào giả lập, mở file `auto_phieuluu.exe`.
3. Xem log `[KET NOI]`, nhấn `Ctrl + Q` để bắt đầu.
4. Bot tự động:
   - Sảnh chính: Bấm nút cam bắt đầu (hỗ trợ cả tiếng Việt, tiếng Trung và dải màu).
   - Trong mê cung: Bấm "Tiến Lên" (hỗ trợ mọi chặng, kể cả chặng 11+ có Ba Lô, Lv.1, đuốc 40-50). Chờ 2.0s hoạt ảnh bước đi.
   - Nhặt bảo vật: Chờ 1.0s timing khóa cảm ứng của game rồi mới click đóng popup.
   - Gặp quái: Luôn chọn thẻ "Chiến Đấu".
   - Kết toán: Bấm "Chấp Nhận", chờ reset ra sảnh lặp lại từ đầu.
   - Chống kẹt: Tự giải phóng khi kẹt màn hình lạ, tự bấm "Tiếp Tục" nếu menu thoát vô tình mở ra.

Chi tiết toạ độ và cấu hình xem tại: [HUONG_DAN_PHIEULUU.md](HUONG_DAN_PHIEULUU.md).

---

## 6. Auto Rally Sa Hải Mê Thành [Coming Soon]

Tính năng tự động quét bản đồ Mapview và tham gia Rally hiện đang phát triển. Chi tiết xem tại: [HUONG_DAN_RALLY.md](HUONG_DAN_RALLY.md).

---

## Hỗ trợ
Discord: `@9m0m`
