# Hướng Dẫn Sử Dụng Auto Rally Sa Hải Mê Thành (Gold Rush)

> 🚀 **Phiên bản mới nhất:** Tự động quét toàn cảnh Mapview, hỗ trợ đa phe/đa mùa, click chuẩn tâm Avatar, tự phân biệt Rally nhiều cuộc và Rally lẻ, tự nhận thưởng 50 lon thể lực, chống click nhầm nút thoát map 100%.

---

## 1. Giới Thiệu Tính Năng

Khác với việc đọc tin nhắn trong khung Chat (dễ bị trôi tin nhắn khi có 5–6 cuộc Rally nổ liên tục và che khuất màn hình nhận quà), **Auto Rally** hoạt động tập trung 100% trên màn hình **Tổng Mapview** (màn hình bản đồ toàn cảnh 4 phe hoặc 8 phe):

1. **Quét Template Matching Đa Tỉ Lệ & Đa Mùa:**
   - Tự động nhận diện tiêu đề *"Tổng Tấn Công!"* trên khắp bản đồ của mọi phe phái (Vàng, Xanh Lam, Đỏ, Tím) bất kể màu nền hay mùa giải.
2. **Click Chuẩn Xác Tâm Avatar Người Mở Rally:**
   - Bot tính toán tọa độ click thẳng vào vòng tròn Avatar người mở Rally ở trung tâm ô đất, tuyệt đối không click vào mép trên banner làm mở nhầm bảng chi tiết ô đất phía trên.
3. **Tự Động Xử Lý Cả 2 Dạng Giao Diện Rally:**
   - **Dạng 1: Bảng danh sách "Tổng Tấn Công" (khi ô có nhiều cuộc Rally):** Quét tìm nút xanh **"Tham gia"** để click join; nếu tất cả đều là nút xám (*"Đang chờ"*, *"Đã tham gia"*, *"Đã đầy"*) thì bot tự đóng lại và đưa ô vào danh sách chờ.
   - **Dạng 2: Bảng chi tiết "Đơn Vị Tiêu Chuẩn" (khi là Rally lẻ 1 cuộc):** Nhận diện chính xác nút xanh **"Tham gia"** để click join rồi bấm Back `↩`. Nếu là nút xám (*"Chờ chấp thuận"*, *"Đã đầy"*), bot tự động khóa cooldown ô đó 60 giây để không mở lại liên tục, rồi bấm Back `↩` về Mapview.
4. **Cơ Chế Đóng Popup An Toàn Tuyệt Đối (Chống Thoát Map):**
   - Đóng popup danh sách bằng cách chạm vào khoảng trống mờ trên đỉnh màn hình (`y = 0.12`).
   - Tuyệt đối **không click vào nút X ở đáy màn hình**, tránh 100% nguy cơ click nhầm vào nút *"Thoát sự kiện Goldrush"* của game.
5. **Tự Động Nhận Thưởng Sau Trận:**
   - Phát hiện bảng kết toán chiến thắng và tự động click nút **"Xác Nhận"** màu xanh lá để nhận **50 lon thể lực**.

---

## 2. Chuẩn Bị Giả Lập & Màn Hình Game

- **Giả lập hỗ trợ:** BlueStacks 5, LDPlayer 9 / 5 / 4, MuMu Player, NoxPlayer, MEmu.
- **Thiết lập màn hình:**
  - Định dạng: Khổ dọc (**Portrait** 9:16).
  - Độ phân giải khuyến nghị: `720 x 1280` hoặc `1080 x 1920` (hoặc kéo giãn tự do, tool có thuật toán **Pillarbox** tự động căn lề vùng game thực).
- **Màn hình trong game:**
  - Mở sự kiện **Sa Hải Mê Thành** (Gold Rush).
  - Đưa game về màn hình **Tổng Mapview** (màn hình nhìn thấy toàn bộ bản đồ 4 phe căn cứ).
  - Giữ nguyên bản đồ ở mức zoom bao quát để bot quan sát được nhiều ô Rally nhất.

---

## 3. Cách Khởi Động Tool

Bạn có thể gửi file cho bạn bè chạy thử theo 1 trong 2 cách cực kỳ đơn giản:

### Cách 1: Chạy trực tiếp file đóng gói sẵn (Không cần cài Python)
1. Tải hoặc giải nén thư mục dự án.
2. Mở thư mục `dist`, click đúp chuột vào file **`auto_rally.exe`**.
3. (Hoặc click đúp vào file **`run_rally.bat`** ở thư mục gốc, file bat sẽ tự ưu tiên chạy `dist\auto_rally.exe`).

### Cách 2: Chạy bằng mã nguồn Python (Dành cho máy đã cài Python)
1. Mở Command Prompt / PowerShell tại thư mục dự án.
2. Chạy lệnh:
   ```cmd
   python auto_rally.py
   ```

---

## 4. Phím Tắt Điều Khiển

| Phím tắt | Trạng thái hiện tại | Chức năng chi tiết |
| :--- | :--- | :--- |
| **`Ctrl + Q`** | [Chờ lệnh] / [Tạm dừng] | **Bắt đầu** hoặc **Tiếp tục** (Resume) quét Mapview. |
| **`ESC`** | [Đang chạy] | **Tạm dừng an toàn tức thì** (`[TAM DUNG]`), ngắt mọi click trong 20ms và nhả chuột cho người dùng thao tác máy tính. |
| **`ESC` (lần 2)** | [Đang tạm dừng] | **Thoát hoàn toàn chương trình** (`[THOAT]`). |

> 💡 **Lưu ý:** Phím `ESC` được tích hợp cơ chế chống bấm đúp nhanh (debounce 0.8s) nên khi bạn bấm `ESC` để dừng chuột, bot sẽ tạm dừng an toàn chứ không bị văng thoát đột ngột.

---

## 5. Quy Trình Hoạt Động Của Tool

```text
[Mở Tool] ──> Kết nối giả lập & Căn chỉnh màn hình
                  │
                  ▼
          Nhấn [Ctrl + Q]
                  │
                  ▼
┌─────────────────┴──────────────────────────────────────┐
│  VÒNG LẶP QUÉT TỔNG MAPVIEW                            │
│                                                        │
│  1. Kiểm tra nhận quà 50 lon thể lực ──> Tự nhận       │
│  2. Quét Template tiêu đề 'Tổng Tấn Công!' đa phe     │
│  3. Phát hiện Rally ──> Click thẳng tâm Avatar        │
│     │                                                  │
│     ├── Nếu là Bảng danh sách nhiều Rally (Dạng 1):    │
│     │     - Có nút XANH 'Tham gia' ──> Click Join      │
│     │     - Toàn nút XÁM ──> Cooldown ô đất            │
│     │     - Chạm khoảng trống đỉnh (y=0.12) để đóng   │
│     │                                                  │
│     ├── Nếu là Bảng Rally lẻ 'Đơn Vị Tiêu Chuẩn' (Dạng 2):
│     │     - Nút XANH 'Tham gia' ──> Click Join & Back ↩│
│     │     - Nút XÁM ('Chờ chấp thuận') ──> Cooldown 60s│
│     │       và bấm nút Back ↩                          │
│     │                                                  │
│     └── Nếu mở nhầm bảng Đất (nút VÀNG 'Tấn Công'):    │
│           - Tự động bấm nút Back ↩ đóng ngay lập tức   │
└────────────────────────────────────────────────────────┘
```

---

## 6. Những Lưu Ý Quan Trọng Khi Sử Dụng

1. **Vấn đề chiếm chuột:**
   - Khi phát hiện có cuộc Rally mở ra, bot sẽ di chuyển con trỏ chuột sang giả lập để click tham gia (~0.3 - 0.5 giây), sau đó thả chuột về trạng thái nghỉ.
   - Trong lúc bot đang quét và xử lý click, bạn không nên di chuột làm việc khác vì có thể làm chệch tọa độ bấm. Nếu cần dùng máy tính, hãy nhấn **`ESC`** để tạm dừng trước.
2. **Không che khuất cửa sổ giả lập:**
   - Bot nhận diện bằng mắt thần chụp màn hình tốc độ cao, do đó cửa sổ giả lập phải hiển thị rõ trên màn hình (không thu nhỏ xuống thanh Taskbar).
3. **Khi mở nhiều giả lập:**
   - Hãy sắp xếp cửa sổ giả lập cần auto hiển thị rõ. Click chuột vào bên trong cửa sổ giả lập đó rồi nhấn `Ctrl + Q` để bot khóa đúng mục tiêu.
4. **Log trên màn hình Console:**
   - `[KET NOI]`: Thông tin cửa sổ và tọa độ game.
   - `[MAPVIEW] Phat hien Rally...`: Đã tìm thấy cuộc tổng tấn công trên bản đồ.
   - `[RALLY] Tham gia thanh cong #...`: Đã tham gia thành công vào đội rally.
   - `[REWARD] Nhan thuong Rally #...`: Đã nhận xong phần thưởng 50 lon thể lực.
   - `[HOTKEY] [TAM DUNG]`: Bot đã dừng an toàn, bạn có toàn quyền dùng chuột.

---

## 7. Khắc Phục Sự Cố Thường Gặp

| Hiện tượng | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| Bot báo `Khong tim thay cua so gia lap` | Cửa sổ game chưa mở hoặc bị đổi tên | Mở BlueStacks / LDPlayer lên, click vào màn hình game rồi bật lại tool. |
| Bot không click vào Rally | Bản đồ bị kéo lệch khỏi khu vực có Rally | Đưa góc nhìn bản đồ về trung tâm bao quát cả 4 phe căn cứ. |
| Bị văng ra ngoài sự kiện | Do phiên bản cũ bấm nhầm nút X dưới đáy | Hãy dùng bản cập nhật mới nhất (đã loại bỏ hoàn toàn click đáy màn hình). |
| Muốn tắt hẳn bot | Đang ở chế độ chạy | Nhấn `ESC` lần 1 để Tạm dừng $\rightarrow$ Nhấn `ESC` lần 2 để Thoát hẳn. |

---
*Chúc bạn và liên minh càn quét mọi mỏ vàng và đạt top cao trong sự kiện Sa Hải Mê Thành!*
