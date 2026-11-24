# QUY CHUẨN PHÁT TRIỂN & KIỂM THỬ TỰ ĐỘNG DÀNH CHO AI AGENT (AGENTS.MD)

Tài liệu này là **bản hợp đồng quy chuẩn bắt buộc** cho bất kỳ AI Agent nào (Antigravity, Cursor, Claude Code, Copilot, v.v.) làm việc trên dự án này.
Mục tiêu tối thượng: **Độ ổn định 100% trong môi trường chạy thật - Tuyệt đối không để xảy ra crash do lỗi logic hoặc ép kiểu lúc runtime.**

---

## 1. CÁC QUY TẮC AN TOÀN MÃ NGUỒN BẮT BUỘC (CRITICAL CODE SAFETY RULES)

### 1.1. An toàn mảng NumPy & OpenCV (NumPy / OpenCV Array Safety)
* **CẤM TUYỆT ĐỐI**: Không bao giờ được đánh giá mảng NumPy như một giá trị boolean:
  - ❌ `if arr:` hoặc `if not arr:`
  - ❌ `arr or fallback_arr`
  - ❌ `if arr1 and arr2:`
  *(Lý do: Trong Python, ép kiểu boolean trên mảng NumPy có $>1$ phần tử sẽ ném `ValueError: The truth value of an array with more than one element is ambiguous`).*
* **BẮT BUỘC SỬ DỤNG**:
  - Kiểm tra tồn tại: `if arr is not None:`
  - Kiểm tra rỗng: `if arr is not None and arr.size > 0:`
  - Gán giá trị mặc định: `arr = primary_arr if primary_arr is not None else fallback_arr`
  - So sánh điều kiện mảng: `if np.any(condition):` hoặc `if np.all(condition):`

### 1.2. An toàn Template Matching & Xử lý hình ảnh (Vision & Template Safety)
* Trước khi gọi `cv2.matchTemplate(image, template, ...)`:
  - Phải kiểm tra kích thước: `template.shape[0] <= image.shape[0]` và `template.shape[1] <= image.shape[1]`.
  - Phải kiểm tra chiều cao / chiều rộng tối thiểu sau khi resize (ví dụ: `max(5, int(w * scale))`).
* Không được để kích thước co giãn (scale) vượt quá kích thước vùng cắt bản đồ (crop).

### 1.3. An toàn Tọa độ & Đổi độ phân giải (Coordinate & DPI Scaling)
* Mọi tọa độ click hoặc crop khi tính toán qua tỉ lệ scale/offset phải được ép kiểu số nguyên: `int(coord)`.
* Giới hạn tọa độ luôn nằm trong phạm vi màn hình hoặc crop tương ứng: `max(0, min(max_val, val))`.

### 1.4. An toàn Luồng & Sự kiện dừng (Threading & Graceful Exit)
* Mọi vòng lặp vô tận của worker (`while True:`, `while _is_running:`) bắt buộc phải kiểm tra cờ dừng:
  ```python
  if _stop_event.is_set() or _is_paused:
      break # hoặc return
  ```
* Không chặn luồng giao diện chính. Mọi tác vụ xử lý ảnh, ADB, OCR phải chạy trên Worker Thread.

---

## 2. QUY TRÌNH KIỂM THỬ CHẤT LƯỢNG 4 BƯỚC BẮT BUỘC (4-STEP VERIFICATION GATE)

Trước khi xác nhận hoàn thành, commit hoặc build `.exe`, Agent **BẮT BUỘC** phải chạy đủ 4 bước sau:

### Bước 1: Kiểm tra Cú pháp Tĩnh (Static Syntax Compilation)
```powershell
python -m compileall -q .
```
*Điều kiện qua*: 0 lỗi cú pháp.

### Bước 2: Quét AST Chống Anti-Pattern (Anti-Pattern Static AST Scan)
```powershell
python tests/test_code_quality.py
```
*Điều kiện qua*: Không có bất kỳ biểu thức `or`, `and`, `not` nào chứa biến mảng hình ảnh (`template`, `crop`, `frame`, `arr`, `img`).

### Bước 3: Smoke Test Toàn Diện (Smoke Test Suite)
```powershell
python tests/test_code_quality.py
```
*Kiểm tra bao gồm*:
- Toàn bộ template trong `assets.py` decode thành công, shape hợp lệ, dtype `uint8`.
- Bộ tham số cấu hình trong `config.py` hợp lệ.
- Chạy qua pipeline ảnh mock không ném ngoại lệ.

### Bước 4: Kiểm tra Đóng gói Bản dựng (Build & Binary Verification)
Khi có thay đổi logic ảnh hưởng đến file chạy:
- Chạy lệnh build sang `.exe`
- Kiểm tra file thực thi được tạo thành công với mã thoát 0.

---

## 3. CHECKLIST DÀNH CHO AGENT TRƯỚC KHI TRẢ LỜI NGƯỜI DÙNG

1. [ ] Đã sửa code tuân thủ 100% mục 1 (không có `array or fallback`, không ép boolean mảng).
2. [ ] Đã chạy `python tests/test_code_quality.py` và toàn bộ test PASS.
3. [ ] Đã đồng bộ mã nguồn giữa cả 2 repo (`coc-auto-app` và `scripauto`).
4. [ ] Nếu thay đổi liên quan đến tính năng chính, đã build lại file thực thi `.exe` thành công.
5. [ ] Đã commit và push đồng bộ lên GitHub.
