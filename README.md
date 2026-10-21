# COC-autofishing (Auto Câu Cá Clash of Critters)

Công cụ tự động câu cá chính xác cao cho sự kiện Câu cá trong game Clash of Critters trên các trình giả lập Android phổ biến (BlueStacks 5, LDPlayer 9, NoxPlayer, MuMu Player, MEmu).

---

## Lưu ý quan trọng trước khi sử dụng

- **Phương thức hoạt động**: Bot mô phỏng và điều khiển trực tiếp con trỏ chuột của máy tính để thao tác vào màn hình giả lập theo thời gian thực.
- **Không sử dụng chuột làm việc khác khi bot đang chạy**: Trong suốt quá trình bot đang câu cá, bạn **không được sử dụng chuột** của máy tính đó (không lướt web, không làm việc hay chơi game khác trên cùng máy). Nếu bạn di chuyển chuột thủ công, thao tác bấm của bot sẽ bị lệch tâm và dẫn đến câu trượt.
- **Dừng khẩn cấp**: Bất kỳ lúc nào bạn cần lấy lại chuột để làm việc, chỉ cần nhấn phím **ESC** trên bàn phím để dừng bot ngay lập tức.

---

## Hướng dẫn sử dụng từng bước (Step-by-Step)

Bạn chỉ cần thực hiện đúng theo các bước đơn giản sau:

### Bước 1: Cài đặt màn hình giả lập (Chỉ cần làm 1 lần đầu)

Để bot nhận diện hình ảnh và toạ độ chuẩn xác:
1. Mở phần **Cài đặt (Settings)** của trình giả lập bạn đang dùng (LDPlayer, BlueStacks, NoxPlayer, MuMu Player, MEmu).
2. Vào mục **Hiển thị (Display)**:
   - Chọn chế độ hiển thị: **Điện thoại (Khổ dọc / Portrait / tỉ lệ 9:16)**.
   - Độ phân giải khuyến nghị: `720x1280` hoặc `1080x1920`.
   - Chỉ số DPI: `240` hoặc `320`.
3. Lưu cài đặt và khởi động lại giả lập nếu được nhắc.

### Bước 2: Tải file chạy Auto về máy

1. Tải bản chạy sẵn mới nhất (chỉ duy nhất 1 file `.exe`, không cần cài thêm bất kỳ công cụ nào):
   > **[Nhấn vào đây để tải file auto_cauca.exe tại GitHub Releases](https://github.com/9m0m/COC-autofishing/releases/latest)**
2. Đặt file `auto_cauca.exe` ở bất kỳ thư mục nào tiện cho bạn (ví dụ: màn hình Desktop hoặc thư mục Downloads).

### Bước 3: Mở game và vào màn hình câu cá

1. Khởi động game Clash of Critters trên giả lập.
2. Vào khu vực sự kiện **Câu cá** sao cho màn hình hiển thị đầy đủ mặt nước và nút câu cá ở góc dưới.
3. **Lưu ý**: Giữ cửa sổ giả lập luôn mở trên màn hình máy tính (không thu nhỏ / minimize cửa sổ xuống thanh Taskbar và không bị ứng dụng khác che khuất hoàn toàn).

### Bước 4: Mở file auto_cauca.exe

1. Nhấp đúp chuột vào file `auto_cauca.exe` đã tải về ở Bước 2.
2. Một cửa sổ dòng lệnh màu đen sẽ hiện lên. Bot sẽ tự động dò tìm và kết nối với cửa sổ giả lập đang mở.
3. Khi kết nối thành công, màn hình sẽ thông báo trạng thái sẵn sàng nhận lệnh.

### Bước 5: Điều khiển Auto bằng bàn phím

- **Bắt đầu câu:** Nhấn phím **`Q`** (hoặc phím **Space**) trên bàn phím. Bot sẽ bắt đầu chiếm quyền điều khiển chuột để quăng cần, canh giật nút tím, bắt minigame thanh trượt và nhận cá tự động.
- **Tạm dừng / Dừng hẳn:** Nhấn phím **`ESC`** trên bàn phím bất kỳ lúc nào. Bot sẽ lập tức dừng lại và nhả quyền điều khiển chuột để bạn sử dụng máy tính bình thường.

---

## Các cơ chế đã tích hợp

- **Quăng cần tự động:** Quét nút màu xanh lá cây để thả cần xuống nước.
- **Canh cá cắn:** Giật cần ngay khi nút chuyển sang màu tím, hạn chế giật non làm mất mồi.
- **Xử lý thanh trượt minigame:** Quét thanh trượt liên tục, tự động ghi nhớ vị trí ô vàng và tính toán va chạm theo vệt di chuyển của phao để hạn chế tối đa việc lướt qua ô vàng nhỏ.
- **Tự động nhận thưởng:** Tự bấm đóng thẻ bài kỷ lục cá và bấm nút "Nhận Ngay" để chuyển sang lượt câu tiếp theo.
- **Tự giải phóng khi kẹt:** Nếu gặp tình trạng giật lag hoặc kẹt bảng thông báo quá 2.5 giây, bot sẽ tự bấm giải phóng để tiếp tục chu trình.

---

## Lưu ý về độ chính xác và liên hệ hỗ trợ

- **Tỉ lệ chính xác:** Mặc dù đã được tối ưu kỹ, trong quá trình chạy thực tế (như khi máy bị tụt khung hình hoặc game giật lag đột ngột), tool vẫn có thể xảy ra trường hợp câu sai hoặc click hụt. Tuy nhiên tỉ lệ hụt là rất ít.
- **Liên hệ hỗ trợ:** Nếu bạn gặp lỗi hoặc có vấn đề gì trong quá trình sử dụng, vui lòng liên hệ qua Discord: **`@9m0m`**.

---

## Câu hỏi thường gặp (FAQ)

1. **Bấm phím Q nhưng bot không quăng cần?**
   - Kiểm tra xem cửa sổ giả lập đã vào đúng màn hình câu cá chưa.
   - Đảm bảo cửa sổ giả lập không bị thu nhỏ (minimize) xuống thanh tác vụ.

2. **Bot bấm lệch vị trí các nút?**
   - Kiểm tra lại cài đặt độ phân giải giả lập ở Bước 1. Phải chắc chắn giả lập đang ở chế độ Điện thoại (khổ dọc 9:16 như `720x1280` hoặc `1080x1920`).

3. **Tôi muốn làm việc khác trên máy tính trong lúc auto câu thì sao?**
   - Do bot sử dụng trực tiếp chuột của máy tính để bấm, bạn không thể dùng chuột làm việc khác trên cùng máy tính đó trong lúc bot đang chạy. Hãy nhấn phím `ESC` để dừng bot khi bạn cần dùng chuột.
