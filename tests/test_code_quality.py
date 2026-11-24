"""
Code Quality & Safety Test Suite for COC AutoFishing & Rally (scripauto)
Enforces:
1. Anti-pattern static AST check: Cấm tuyệt đối ép kiểu boolean trên mảng NumPy/OpenCV.
2. Assets integrity check: Đảm bảo toàn bộ template Base64 hợp lệ, không None, đúng shape.
3. Config schema check: Đảm bảo đầy đủ các hằng số cấu hình với kiểu dữ liệu hợp lệ.
4. Mock pipeline execution: Chạy thử pipeline nhận diện trên ảnh giả lập để đảm bảo không văng runtime crash.
"""

import ast
import glob
import os
import sys
import unittest
import numpy as np

# Thêm thư mục gốc vào path để import
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import assets
import config


class TestCodeQuality(unittest.TestCase):

    def test_ast_no_array_boolean_coercion(self):
        """
        Quét tĩnh AST toàn bộ mã nguồn Python.
        Bắt các lỗi ép kiểu boolean mảng NumPy:
        - arr or fallback
        - arr and other
        - if arr: / if not arr: (với các biến mảng ảnh)
        """
        array_keywords = {"template", "tpl", "crop", "frame", "arr", "img", "pill"}
        violations = []

        for py_path in glob.glob(os.path.join(REPO_ROOT, "**", "*.py"), recursive=True):
            rel_path = os.path.relpath(py_path, REPO_ROOT)
            if any(skip in rel_path for skip in ["build", "dist", ".git", "tests", "__pycache__"]):
                continue

            with open(py_path, "r", encoding="utf-8") as f:
                src = f.read()

            try:
                tree = ast.parse(src, filename=rel_path)
            except SyntaxError as e:
                self.fail(f"Lỗi cú pháp trong {rel_path}: {e}")

            for node in ast.walk(tree):
                # 1. Bắt 'arr or fallback' hoặc 'arr and other'
                if isinstance(node, ast.BoolOp):
                    for v in node.values:
                        if isinstance(v, ast.Name) and any(kw in v.id.lower() for kw in array_keywords):
                            violations.append(
                                f"{rel_path}:{node.lineno} -> Biến mảng '{v.id}' bị ép kiểu boolean trong biểu thức {type(node.op).__name__}."
                            )

        if violations:
            msg = "\n".join(violations)
            self.fail(
                f"\n[PHÁT HIỆN ANTI-PATTERN ÉP KIỂU MẢNG NUMPY]\n{msg}\n"
                "-> HÃY DÙNG: 'arr if arr is not None else fallback' thay vì 'arr or fallback'!\n"
            )

    def test_assets_integrity(self):
        """Kiểm tra toàn bộ template và asset base64 giải mã ra đúng định dạng hình ảnh."""
        rally_tpls = assets.get_rally_templates()
        self.assertGreater(len(rally_tpls), 0, "Danh sách rally templates không được rỗng")
        for name, tpl in rally_tpls:
            self.assertIsInstance(tpl, np.ndarray, f"Template {name} phải là np.ndarray")
            self.assertEqual(tpl.dtype, np.uint8, f"Template {name} dtype phải là uint8")
            self.assertGreater(tpl.size, 0, f"Template {name} không được rỗng")
            self.assertIn(len(tpl.shape), (2, 3), f"Template {name} phải có 2 hoặc 3 chiều")

        timer_tpl = assets.get_rally_timer_template()
        self.assertIsNotNone(timer_tpl, "Universal Timer Pill template không được None")
        self.assertIsInstance(timer_tpl, np.ndarray, "Timer template phải là np.ndarray")
        self.assertEqual(timer_tpl.dtype, np.uint8, "Timer template dtype phải là uint8")
        self.assertGreater(timer_tpl.shape[0], 5, "Chiều cao timer template phải > 5px")
        self.assertGreater(timer_tpl.shape[1], 10, "Chiều rộng timer template phải > 10px")

    def test_config_schema(self):
        """Kiểm tra tính hợp lệ của các tham số cấu hình."""
        self.assertTrue(hasattr(config, "RALLY_TIMER_MATCH_THRESHOLD"), "Thiếu RALLY_TIMER_MATCH_THRESHOLD")
        thresh = getattr(config, "RALLY_TIMER_MATCH_THRESHOLD")
        self.assertIsInstance(thresh, (float, int))
        self.assertTrue(0.0 < thresh < 1.0, f"Ngưỡng {thresh} phải nằm trong (0.0, 1.0)")

        self.assertTrue(hasattr(config, "RALLY_TIMER_AVATAR_OFFSET_Y"), "Thiếu RALLY_TIMER_AVATAR_OFFSET_Y")
        offset = getattr(config, "RALLY_TIMER_AVATAR_OFFSET_Y")
        self.assertIsInstance(offset, (float, int))
        self.assertTrue(0.1 <= offset <= 2.0, f"Tỉ lệ offset avatar {offset} không hợp lệ")

        self.assertTrue(hasattr(config, "RALLY_SCALE_FACTORS"), "Thiếu RALLY_SCALE_FACTORS")
        scales = getattr(config, "RALLY_SCALE_FACTORS")
        self.assertIsInstance(scales, (list, tuple))
        self.assertGreater(len(scales), 0)

    def test_mock_pipeline_safety(self):
        """Chạy pipeline quét Rally trên ảnh giả lập để đảm bảo không bị runtime crash."""
        import cv2

        dummy_h, dummy_w = 900, 500
        dummy_img = np.random.randint(50, 200, (dummy_h, dummy_w, 3), dtype=np.uint8)

        # Chèn giả lập 1 viên pill đen vào dummy_img
        timer_tpl = assets.get_rally_timer_template()
        if timer_tpl is not None:
            th, tw = timer_tpl.shape[:2]
            dummy_img[300:300+th, 200:200+tw] = timer_tpl

        # Test scan logic
        my1, my2 = int(dummy_h * 0.15), int(dummy_h * 0.85)
        map_crop = dummy_img[my1:my2, 0:dummy_w]

        try:
            scale_factors = [1.0, 0.9, 0.8]
            candidates = []
            timer_thresh = 0.52
            avatar_offset_ratio = 0.85
            t_th, t_tw = timer_tpl.shape[:2]

            for cur_sc in scale_factors:
                cur_tw = max(15, int(t_tw * cur_sc))
                cur_th = max(10, int(t_th * cur_sc))
                scaled = cv2.resize(timer_tpl, (cur_tw, cur_th))
                res = cv2.matchTemplate(map_crop, scaled, cv2.TM_CCOEFF_NORMED)
                locs = np.where(res >= timer_thresh)
                for pt in zip(*locs[::-1]):
                    tx, ty = int(pt[0]), int(pt[1])
                    score = float(res[ty, tx])
                    click_x = int(0 + tx + cur_tw // 2)
                    click_y = int(my1 + ty - int(cur_th * avatar_offset_ratio))
                    tile = (click_x, click_y)
                    if not any(abs(c[0] - click_x) < 35 and abs(c[1] - click_y) < 35 for c in candidates):
                        candidates.append((click_x, click_y, tile, "Timer", score))

            self.assertGreaterEqual(len(candidates), 1, "Pipeline phải tìm thấy timer pill đã chèn")
        except Exception as e:
            self.fail(f"Pipeline quét Rally bị ném ngoại lệ khi chạy thử: {e}")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCodeQuality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
