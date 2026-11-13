# BÁO CÁO BÀN GIAO DỰ ÁN AUTO RALLY (SA HẢI MÊ THÀNH)

> **Mục đích**: Tài liệu bàn giao kỹ thuật đầy đủ để tiếp tục phát triển và xử lý dứt điểm trong Session chat mới.

---

## 1. Tổng quan Kiến trúc & Hiện trạng Mã nguồn

| Tệp tin | Vai trò & Hiện trạng |
| :--- | :--- |
| [auto_rally.py](file:///c:/ky_9_FPT/scripauto/auto_rally.py) | **Module điều khiển chính**: Vòng lặp quét Mapview, nhận diện Rally, xử lý popup tham gia, quản lý hotkey `Ctrl+Q` / `ESC`. |
| [assets.py](file:///c:/ky_9_FPT/scripauto/assets.py) | **Kho tài nguyên Base64**: Đã tích hợp hệ thống Multi-Faction Template cho cả 4 Phe (Vàng, Xanh, Đỏ, Tím). |
| [config.py](file:///c:/ky_9_FPT/scripauto/config.py) | **Cấu hình toạ độ & ngưỡng**: Chứa toạ độ tỉ lệ popup, dải màu HSV, thời gian delay. Giữ nguyên toàn bộ cấu hình câu cá từ dòng 1 đến 85. |
| [emulator.py](file:///c:/ky_9_FPT/scripauto/emulator.py) | **Giao tiếp Win32 API**: Chụp màn hình qua `mss`, hỗ trợ đa màn hình, click chuột không cướp tiêu điểm và tự khôi phục vị trí chuột cho người dùng. |
| [auto_cauca.py](file:///c:/ky_9_FPT/scripauto/auto_cauca.py) | **Tính năng câu cá gốc**: Hoạt động ổn định 100%, được cô lập hoàn toàn không bị ảnh hưởng. |
| [dist/auto_rally.exe](file:///c:/ky_9_FPT/scripauto/dist/auto_rally.exe) | File thực thi độc lập (75.3 MB), đã build sẵn bản mới nhất. |

*Toàn bộ mã nguồn đã được commit và đồng bộ trên Git remote: `https://github.com/9m0m/COC-autofishing.git` (nhánh `main`).*

---

## 2. Những tính năng cốt lõi đã chạy ổn định

1. **Khả năng chạy trên Màn hình phụ**:
   * Bot tự động phát hiện cửa sổ giả lập dù đặt ở màn hình chính hay màn hình phụ (`X > 1920`).
   * Win32 API `SetCursorPos` và `mouse_event` điều khiển toạ độ toàn cầu Virtual Desktop chuẩn xác.
2. **Khôi phục vị trí chuột tức thì (`touch_tap`)**:
   * Khi bot click vào giả lập trên màn hình 2, chuột lập tức được trả về vị trí cũ trên màn hình 1 trong vòng 80ms, không làm gián đoạn việc lướt web/xem video của người dùng.
3. **Bộ nhận diện Đa Phe (Multi-Faction Template)**:
   * Bản đồ game có 4 màu gạch (Vàng, Xanh, Đỏ, Tím). Đã tạo sẵn 4 mẫu template tương ứng với từng góc bản đồ, giải quyết việc chữ bị xuyên thấu màu nền.

---

## 3. Phát hiện bước ngoặt mới nhất: Lỗi Tỷ lệ Khung hình (Black Pillarbox Issue)

Từ bức ảnh mới nhất người dùng gửi (`media_1794543942203_b2c1a7f1.jpg`), nguyên nhân gốc rễ khiến bot đứng im không click đã được làm sáng tỏ:

```
+------------------ Cửa sổ BlueStacks (Rộng 587px) -------------------+
| [Dải đen 40px] |      Nội dung Game 9:16 (Rộng ~415px)     | [Dải đen 50px] |
|                 |  Chữ Rally "Tổng Tấn Công!" giữ nguyên cỡ |                |
+----------------------------------------------------------------------+
```

1. **Hiện tượng thực tế**:
   * Trò chơi *Clash of Critters* là game di động màn hình dọc cố định (tỷ lệ 9:16).
   * Khi người dùng kéo mép cửa sổ BlueStacks rộng ra (chiều rộng lên tới `587px`), game **không kéo giãn to ra** mà BlueStacks tự động chèn thêm **2 dải đen (pillarbox)** ở hai bên sườn.
   * Kích thước thực của giao diện game bên trong vẫn giữ nguyên kích thước chuẩn (~415px), tiêu đề Rally vẫn có kích thước gốc **$76 \times 36\text{ px}$**.

2. **Sai lệch trong mã nguồn hiện tại**:
   * Đoạn code hiện tại trong [auto_rally.py](file:///c:/ky_9_FPT/scripauto/auto_rally.py#L202):
     $$\text{scale} = \frac{\text{gw\_w}}{415.0} = \frac{537}{415.0} = 1.294$$
   * Code ngộ nhận rằng toàn bộ cửa sổ 537px là nội dung game, nên đã **phóng to template từ 76px lên tới 98px - 110px**.
   * Khi mang một template kích thước $98\text{ px}$ đi so khớp với chữ trong game kích thước thực tế chỉ có $76\text{ px}$, điểm tương quan bị rớt:
     * Quét theo tỷ lệ `scale = 1.29`: Điểm khớp chỉ đạt **0.59 - 0.65** ($< 0.66$ nên bot coi như không thấy Rally).
     * Quét theo tỷ lệ chuẩn `scale = 1.00`: Điểm khớp đạt tới **0.868 - 0.940** (Nhận diện thành công 100%).

---

## 4. Việc cần làm ngay cho Session Chat mới

Trong Session chat tiếp theo, AI tiếp nhận chỉ cần thực hiện 2 bước kỹ thuật ngắn gọn sau để xử lý dứt điểm:

### Nhiệm vụ 1: Sửa logic Scale trong [auto_rally.py](file:///c:/ky_9_FPT/scripauto/auto_rally.py)
Không tính `scale = gw_w / 415.0` dựa trên chiều rộng cửa sổ bị kéo dãn nữa. Luôn quét quanh tỷ lệ gốc:
```python
# Thay vì phụ thuộc vào gw_w:
# Quét dải tỷ lệ cố định của game mobile (quanh 1.0):
scale_factors = [0.92, 0.96, 1.00, 1.04, 1.08]
```
Thực nghiệm đã chứng minh dải này cho điểm khớp **0.868** ngay trên ảnh mới nhất của người dùng.

### Nhiệm vụ 2: Tự động loại trừ Dải đen hai bên (Pillarbox Detection)
Nếu cửa sổ BlueStacks bị kéo rộng hơn tỷ lệ 9:16:
* Tìm tọa độ viền đen hai bên mép (`pixel value < 10`) để xác định đúng vùng `game_left` và `game_w` thực tế.
* Điều này giúp các toạ độ click popup (như nút "Tham gia", nút Back) luôn rơi đúng tâm nút, không bị lệch do dải đen mép trái.

### Hướng dẫn người dùng (Tạm thời nếu chưa sửa code):
Chỉnh cửa sổ BlueStacks về đúng kích thước dọc chuẩn (không kéo giãn ngang quá rộng), hoặc vào Cài đặt BlueStacks -> Hiển thị -> Chọn độ phân giải chuẩn của điện thoại (ví dụ: `1080 x 1920` hoặc `720 x 1280`).
