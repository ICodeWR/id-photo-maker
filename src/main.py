# src/main.py
# -*- coding: utf-8 -*-
"""
智能证件照制作工具 — 主程序入口

UI 由 Qt Designer 设计 (src/ui/main_window.ui)，
经 pyside6-uic 编译为 src/ui/ui_main_window.py，
本模块通过多继承方式加载并绑定业务逻辑。

依赖：PySide6 + OpenCV（见 ../pyproject.toml）
"""

import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QImage

# 确保项目根目录在 sys.path 中
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.ui.ui_main_window import Ui_MainWindow
from src.crop_widget import CropWidget
from src.image_processor import ImageProcessor


class MainWindow(QMainWindow, Ui_MainWindow):
    """主窗口 — 多继承：QMainWindow（窗口基类）+ Ui_MainWindow（Designer UI）"""

    def __init__(self):
        super().__init__()
        # ── 1. 加载 Qt Designer 设计的 UI ─────────────────
        self.setupUi(self)

        # ── 2. 内部状态 ────────────────────────────────────
        self.current_image = None       # 原始图像 (numpy.ndarray, BGR)
        self.processed_image = None     # 最终处理后的图像
        self.camera = None              # cv2.VideoCapture
        self.camera_timer = None        # QTimer 刷新摄像头
        self._img_dims = (0, 0)         # 原始图像尺寸 (w, h)
        self._display_scale = 1.0       # 显示缩放比例
        self._display_offset = (0, 0)   # 显示偏移 (offset_x, offset_y)
        self._camera_raw_preview = True  # 摄像头预览时，是否在预览区显示原始帧（True=实时显示，False=冻结显示处理后结果）

        # ── 3. 裁剪控件（叠加在 label_original 上） ──────
        self.crop_widget = CropWidget(self.label_original)
        self.crop_widget.setGeometry(self.label_original.rect())
        self.crop_widget.hide()
        # 让裁剪框尺寸始终跟随 label_original（图片缩放时自动适配）
        self.label_original.installEventFilter(self)
        self.label_preview.installEventFilter(self)

        # ── 4. 防抖定时器 —— 拖拽裁剪框时不立刻重处理 ────
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._process_and_preview)

        # ── 5. 信号/槽绑定 ────────────────────────────────
        self._connect_signals()

        # ── 6. 初始状态 ────────────────────────────────────
        self.statusbar.showMessage("就绪")

    # ═════════════════════════════════════════════════════
    #  信号/槽绑定
    # ═════════════════════════════════════════════════════

    def _connect_signals(self):
        """连接 UI 控件信号到对应的槽函数"""
        # 工具栏按钮
        self.btn_upload.clicked.connect(self.on_upload)
        self.btn_camera.clicked.connect(self.on_camera_toggle)
        self.btn_capture.clicked.connect(self.on_capture)
        self.btn_save.clicked.connect(self.on_save)
        # 下拉框
        self.combo_bg.currentTextChanged.connect(self._on_bg_or_size_changed)
        self.combo_size.currentTextChanged.connect(self._on_bg_or_size_changed)
        # 裁剪框
        self.crop_widget.crop_rect_changed.connect(self._on_crop_changed)

    # ═════════════════════════════════════════════════════
    #  上传 / 打开图片
    # ═════════════════════════════════════════════════════

    def on_upload(self):
        """打开文件选择对话框，加载图片"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if not path:
            return
        self._load_image_from_path(path)

    def _load_image_from_path(self, path: str):
        """从文件路径加载图片并显示"""
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            QMessageBox.warning(self, "错误", f"无法加载图片：{path}")
            return
        self.current_image = img
        self._display_image(img, self.label_original)
        self._init_crop_on_image(img)
        self.statusbar.showMessage(f"已加载：{os.path.basename(path)}")
        # 触发一次处理
        self._on_bg_or_size_changed()

    def _display_image(self, img: np.ndarray, label) -> QPixmap:
        """将 OpenCV 图像显示到指定的 QLabel 上"""
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        # 缩放以适应 label
        pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(pixmap)
        if label is self.label_original and self.current_image is not None:
            # 原图标签发生变化时，更新裁剪框尺寸并转换坐标
            self.crop_widget.setGeometry(self.label_original.rect())
        return pixmap

    def _init_crop_on_image(self, img: np.ndarray):
        """根据图片尺寸初始化裁剪框（坐标已换算到显示空间）
        注意：此方法会重置裁剪框位置和大小，适合首次显示图片时调用。
        摄像头实时预览期间不应调用此方法，否则会覆盖用户对裁剪框的调整。
        """
        self._update_display_params(img)
        img_h, img_w = img.shape[:2]

        # 在显示坐标空间中取居中裁剪框（比例约 3:4）
        disp_w = int(img_w * self._display_scale)
        disp_h = int(img_h * self._display_scale)
        ox, oy = self._display_offset
        crop_w = min(disp_w, int(disp_h * 3 / 4))
        crop_h = int(crop_w * 4 / 3)
        if crop_h > disp_h:
            crop_h = disp_h
            crop_w = int(crop_h * 3 / 4)
        x = ox + (disp_w - crop_w) // 2
        y = oy + (disp_h - crop_h) // 2

        self.crop_widget.set_crop_rect(QRect(x, y, crop_w, crop_h))
        self.crop_widget.show()
        self._update_crop_aspect_ratio()

    def _update_display_params(self, img: np.ndarray):
        """更新显示缩放参数（供坐标转换使用），不改变裁剪框几何"""
        img_h, img_w = img.shape[:2]
        self._img_dims = (img_w, img_h)

        label_w = self.label_original.width()
        label_h = self.label_original.height()
        scale = min(label_w / img_w, label_h / img_h)
        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)
        offset_x = (label_w - disp_w) // 2
        offset_y = (label_h - disp_h) // 2
        self._display_scale = scale
        self._display_offset = (offset_x, offset_y)

    def _crop_rect_to_image(self, display_rect: QRect) -> QRect:
        """将显示坐标空间中的裁剪框转换回原始图像坐标"""
        r = display_rect.normalized()
        scale = self._display_scale
        ox, oy = self._display_offset
        # 转换：去除偏移，按比例缩放
        x = int((r.x() - ox) / scale)
        y = int((r.y() - oy) / scale)
        w = int(r.width() / scale)
        h = int(r.height() / scale)
        return QRect(x, y, w, h)

    def _image_rect_to_display(self, image_rect: QRect) -> QRect:
        """将原始图像坐标转换回显示坐标空间"""
        r = image_rect.normalized()
        scale = self._display_scale
        ox, oy = self._display_offset
        x = int(r.x() * scale + ox)
        y = int(r.y() * scale + oy)
        w = int(r.width() * scale)
        h = int(r.height() * scale)
        return QRect(x, y, w, h)

    def _update_crop_aspect_ratio(self):
        """根据 combo_size 当前值设置裁剪框宽高比"""
        size_name = self.combo_size.currentText()
        size = ImageProcessor.SIZE_MAP.get(size_name)
        if size:
            w, h = size
            self.crop_widget.set_aspect_ratio(w / h)
        else:
            self.crop_widget.set_aspect_ratio(0.0)

    # ═════════════════════════════════════════════════════
    #  摄像头
    # ═════════════════════════════════════════════════════

    def on_camera_toggle(self):
        """打开/关闭摄像头"""
        if self.camera is not None:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        """启动摄像头预览"""
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            QMessageBox.warning(self, "错误", "无法打开摄像头")
            self.camera = None
            return
        self.btn_camera.setText("📷 关闭摄像头")
        self._camera_raw_preview = True  # 进入实时预览模式，两侧均显示原始帧

        # 读取第一帧，一次性初始化裁剪框位置和显示参数
        ret, frame = self.camera.read()
        if ret:
            self.current_image = frame
            self._display_image(frame, self.label_original)
            self._init_crop_on_image(frame)    # 首次初始化裁剪框（居中位置）
            if self._camera_raw_preview:
                self._display_image(frame, self.label_preview)

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self._update_camera_frame)
        self.camera_timer.start(30)

    def _stop_camera(self):
        """停止摄像头预览"""
        if self.camera_timer:
            self.camera_timer.stop()
            self.camera_timer = None
        if self.camera:
            self.camera.release()
            self.camera = None
        self.btn_camera.setText("📷 打开摄像头")
        self.statusbar.showMessage("摄像头已关闭")

    def _update_camera_frame(self):
        """定时器回调：读取摄像头帧并显示"""
        ret, frame = self.camera.read()
        if ret:
            self.current_image = frame
            self._display_image(frame, self.label_original)
            # 只更新显示参数（用于坐标转换），不重置裁剪框位置/大小
            self._update_display_params(frame)
            # 如果处于原始帧预览模式，同时更新预览区显示实时画面
            # 当用户点击"拍照"后，此标志设为 False，预览区保持显示处理结果
            if self._camera_raw_preview:
                self._display_image(frame, self.label_preview)

    def on_capture(self):
        """拍照：从摄像头捕获当前帧作为最终图片"""
        if self.current_image is None:
            QMessageBox.information(self, "提示", "请先打开摄像头或上传图片")
            return
        self._camera_raw_preview = False  # 冻结预览区，保持显示处理后的结果
        self._on_bg_or_size_changed()
        self.statusbar.showMessage("已拍照")

    # ═════════════════════════════════════════════════════
    #  背景 / 尺寸变更
    # ═════════════════════════════════════════════════════

    def _on_bg_or_size_changed(self):
        """背景色或尺寸改变时重新处理图片（立即执行）"""
        if self.current_image is None:
            return
        self._update_crop_aspect_ratio()
        # 下拉框变更不需要防抖，立即处理
        self._debounce_timer.stop()
        self._process_and_preview()

    def _on_crop_changed(self, rect: QRect):
        """裁剪框变化时——启动防抖，不立刻重处理"""
        if self.current_image is None:
            return
        # 拖拽过程中延迟 350ms 再处理，避免频繁调用 rembg
        self.statusbar.showMessage("处理中…")
        self._debounce_timer.stop()
        self._debounce_timer.start(350)

    def _process_and_preview(self):
        """执行裁剪 + 背景替换 + 尺寸调整，并显示预览"""
        img = self.current_image
        if img is None:
            return

        self.statusbar.showMessage("处理中…")
        # 强制界面刷新，让用户看到"处理中…"
        QApplication.processEvents()

        # 1. 裁剪（将显示坐标转回图像坐标）
        display_rect = self.crop_widget.crop_rect
        image_rect = self._crop_rect_to_image(display_rect)
        cropped = ImageProcessor.crop_image(img, image_rect)

        # 2. 替换背景
        bg_color_name = self.combo_bg.currentText()
        target_bgr = ImageProcessor.COLOR_MAP.get(bg_color_name, (255, 255, 255))
        processed = ImageProcessor.replace_background(cropped, target_bgr)

        # 3. 缩放到目标尺寸
        size_name = self.combo_size.currentText()
        target_size = ImageProcessor.SIZE_MAP.get(size_name)
        if target_size:
            processed = ImageProcessor.resize_for_standard(processed, target_size)

        self.processed_image = processed
        self._display_image(processed, self.label_preview)
        self.statusbar.showMessage(
            f"背景：{bg_color_name} | 尺寸：{size_name} | "
            f"输出：{processed.shape[1]}×{processed.shape[0]} px"
        )

    # ═════════════════════════════════════════════════════
    #  保存
    # ═════════════════════════════════════════════════════

    def on_save(self):
        """保存处理后的图片（支持中文路径）"""
        if self.processed_image is None:
            QMessageBox.information(self, "提示", "请先加载并处理图片")
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self, "保存图片", "证件照.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if not path:
            return

        # ── 处理中文路径问题 ────────────────────────────
        # OpenCV 的 cv2.imwrite 在 Windows 上依赖系统 locale，
        # 有时无法正确处理 UTF-8 中文路径。
        # 策略：先用 cv2.imwrite，失败则用 PIL 兜底。
        success = cv2.imwrite(path, self.processed_image)

        if not success:
            # 尝试用 PIL 兜底（支持 Unicode 路径）
            try:
                from PIL import Image as PILImage
                # OpenCV BGR → RGB
                rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                pil_img = PILImage.fromarray(rgb)
                pil_img.save(path)
                success = True
            except Exception as exc:
                self.statusbar.showMessage(f"保存失败：{exc}")

        if success:
            self.statusbar.showMessage(f"已保存：{os.path.basename(path)}")
            QMessageBox.information(self, "成功", f"图片已保存到：\n{path}")
        else:
            QMessageBox.warning(
                self, "错误",
                "保存失败，可能原因：\n"
                "1. 目标目录没有写入权限\n"
                "2. 文件已被其他程序打开\n"
                "3. 路径包含特殊字符\n\n"
                "请尝试换一个目录（如桌面）保存。"
            )

    # ═════════════════════════════════════════════════════
    #  事件过滤器 — 让裁剪框/预览区跟随窗口缩放
    # ═════════════════════════════════════════════════════

    def eventFilter(self, watched, event):
        """监听 label 的 Resize 事件，同步显示内容与裁剪框"""
        if event.type() != event.Type.Resize:
            return super().eventFilter(watched, event)

        # ── 原图区尺寸变化 ──────────────────────────────
        if watched is self.label_original:
            # 1. 保存当前裁剪框在图像坐标中的位置（不变区域）
            old_image_rect = None
            if self.current_image is not None and self.crop_widget.isVisible():
                old_image_rect = self._crop_rect_to_image(
                    self.crop_widget.crop_rect
                )

            # 2. 更新裁剪框覆盖层尺寸
            self.crop_widget.setGeometry(self.label_original.rect())

            # 3. 重算显示参数
            if self.current_image is not None:
                img_h, img_w = self.current_image.shape[:2]
                label_w = self.label_original.width()
                label_h = self.label_original.height()
                scale = min(label_w / img_w, label_h / img_h)
                self._display_scale = scale
                self._display_offset = (
                    (label_w - int(img_w * scale)) // 2,
                    (label_h - int(img_h * scale)) // 2,
                )

                # 4. 将裁剪框从图像坐标恢复到新的显示坐标
                if old_image_rect is not None and old_image_rect.isValid():
                    new_display_rect = self._image_rect_to_display(old_image_rect)
                    self.crop_widget.set_crop_rect(new_display_rect)

                # 5. 重新显示原图（按新 label 尺寸缩放）
                self._display_image(self.current_image, self.label_original)

        # ── 预览区尺寸变化 ──────────────────────────────
        elif watched is self.label_preview:
            if self.processed_image is not None:
                self._display_image(self.processed_image, self.label_preview)
            elif self.current_image is not None:
                self._display_image(self.current_image, self.label_preview)

        return super().eventFilter(watched, event)

    # ═════════════════════════════════════════════════════
    #  窗口关闭事件
    # ═════════════════════════════════════════════════════

    def closeEvent(self, event):
        """关闭窗口时释放摄像头等资源"""
        self._stop_camera()
        super().closeEvent(event)

    # ═════════════════════════════════════════════════════
    #  窗口尺寸变化
    # ═════════════════════════════════════════════════════

    def resizeEvent(self, event):
        """窗口缩放时裁剪框自适应"""
        super().resizeEvent(event)
        if self.current_image is not None and self.crop_widget.isVisible():
            self._on_crop_changed(self.crop_widget.crop_rect)


# ═════════════════════════════════════════════════════════
#  入口
# ═════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("智能证件照制作工具")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
