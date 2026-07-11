# src/crop_widget.py
# -*- coding: utf-8 -*-
"""
自定义裁剪框控件

在图片上叠加一个可拖拽移动、缩放的可视化裁剪框。
支持：
  - 鼠标拖拽移动裁剪框
  - 四角/边缘拖拽缩放
  - 比例锁定（按证件照规格）
  - 实时信号通知
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush


# ── 鼠标在裁剪框上的命中区域 ──────────────────────────
_OUTSIDE     = 0  # 外部
_MOVE        = 1  # 内部 → 拖拽移动
_RESIZE_TL   = 2  # 左上角
_RESIZE_TR   = 3  # 右上角
_RESIZE_BL   = 4  # 左下角
_RESIZE_BR   = 5  # 右下角
_RESIZE_TOP  = 6  # 上边缘
_RESIZE_BOT  = 7  # 下边缘
_RESIZE_LEFT = 8  # 左边缘
_RESIZE_RIGHT= 9  # 右边缘


class CropWidget(QWidget):
    """可拖拽缩放的矩形裁剪框控件"""

    # 当裁剪框发生变化时发射，传递当前 QRect
    crop_rect_changed = Signal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 透明背景，露出下方图片
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # 默认裁剪框（宽高比约 3:4）
        self.crop_rect = QRect(50, 50, 240, 320)
        self._min_size = 30          # 最小宽高

        # 拖拽状态
        self._mode = _OUTSIDE
        self._drag_start_pos = QPoint()
        self._drag_start_rect = QRect()

        # 是否锁定宽高比（0 表示不锁定）
        self._aspect_ratio = 0.0

        # 手柄大小（像素）
        self._handle_size = 8
        self._handle_half = self._handle_size // 2

    # ── 公共接口 ────────────────────────────────────────

    def set_crop_rect(self, rect: QRect):
        """外部设置裁剪框（如根据图片尺寸初始化）"""
        self.crop_rect = rect.normalized()
        self.update()
        self.crop_rect_changed.emit(self.crop_rect)

    def set_aspect_ratio(self, ratio: float):
        """锁定宽高比（w/h），传入 0 解除锁定"""
        self._aspect_ratio = ratio

    # ── 绘制 ────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 半透明遮罩（裁剪区域外部变暗）
        brush = QBrush(QColor(0, 0, 0, 100))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        # 用 4 个矩形覆盖遮罩区
        r = self.crop_rect
        painter.drawRect(0, 0, self.width(), r.top())                     # 上
        painter.drawRect(0, r.top(), r.left(), r.height())               # 左
        painter.drawRect(r.right(), r.top(), self.width()-r.right(), r.height())  # 右
        painter.drawRect(0, r.bottom(), self.width(), self.height()-r.bottom())   # 下

        # 2. 裁剪框边框（绿色虚线）
        pen = QPen(QColor(0, 255, 0), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(r)

        # 3. 四角手柄（绿色实心方块）
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        corners = [r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()]
        for pt in corners:
            painter.drawRect(pt.x() - self._handle_half,
                             pt.y() - self._handle_half,
                             self._handle_size, self._handle_size)

    # ── 鼠标事件 ────────────────────────────────────────

    def _hit_test(self, pos: QPoint) -> int:
        """判断点击位置在裁剪框的哪个区域"""
        r = self.crop_rect
        # 四角（优先级最高）
        if (pos - r.topLeft()).manhattanLength() <= 15:
            return _RESIZE_TL
        if (pos - r.topRight()).manhattanLength() <= 15:
            return _RESIZE_TR
        if (pos - r.bottomLeft()).manhattanLength() <= 15:
            return _RESIZE_BL
        if (pos - r.bottomRight()).manhattanLength() <= 15:
            return _RESIZE_BR

        # 边缘（5px 容差）
        on_left   = abs(pos.x() - r.left())   <= 5 and r.top()  <= pos.y() <= r.bottom()
        on_right  = abs(pos.x() - r.right())  <= 5 and r.top()  <= pos.y() <= r.bottom()
        on_top    = abs(pos.y() - r.top())    <= 5 and r.left() <= pos.x() <= r.right()
        on_bottom = abs(pos.y() - r.bottom()) <= 5 and r.left() <= pos.x() <= r.right()

        if on_left and on_top:
            return _RESIZE_TL
        if on_right and on_top:
            return _RESIZE_TR
        if on_left and on_bottom:
            return _RESIZE_BL
        if on_right and on_bottom:
            return _RESIZE_BR
        if on_left:
            return _RESIZE_LEFT
        if on_right:
            return _RESIZE_RIGHT
        if on_top:
            return _RESIZE_TOP
        if on_bottom:
            return _RESIZE_BOT

        # 内部 → 移动
        if r.contains(pos):
            return _MOVE

        return _OUTSIDE

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mode = self._hit_test(event.pos())
            self._drag_start_pos = event.pos()
            self._drag_start_rect = QRect(self.crop_rect)
            self.setCursor(self._cursor_for_mode(self._mode))

    def mouseMoveEvent(self, event):
        if self._mode == _OUTSIDE:
            # 悬停时改变光标
            mode = self._hit_test(event.pos())
            self.setCursor(self._cursor_for_mode(mode))
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # 计算偏移
        delta = event.pos() - self._drag_start_pos
        new_rect = QRect(self._drag_start_rect)

        if self._mode == _MOVE:
            new_rect.translate(delta)
        elif self._mode == _RESIZE_TL:
            new_rect.setTopLeft(self._drag_start_rect.topLeft() + delta)
        elif self._mode == _RESIZE_TR:
            new_rect.setTopRight(self._drag_start_rect.topRight() + delta)
        elif self._mode == _RESIZE_BL:
            new_rect.setBottomLeft(self._drag_start_rect.bottomLeft() + delta)
        elif self._mode == _RESIZE_BR:
            new_rect.setBottomRight(self._drag_start_rect.bottomRight() + delta)
        elif self._mode == _RESIZE_TOP:
            new_rect.setTop(self._drag_start_rect.top() + delta.y())
        elif self._mode == _RESIZE_BOT:
            new_rect.setBottom(self._drag_start_rect.bottom() + delta.y())
        elif self._mode == _RESIZE_LEFT:
            new_rect.setLeft(self._drag_start_rect.left() + delta.x())
        elif self._mode == _RESIZE_RIGHT:
            new_rect.setRight(self._drag_start_rect.right() + delta.x())

        new_rect = new_rect.normalized()

        # 限制最小尺寸
        if new_rect.width() < self._min_size or new_rect.height() < self._min_size:
            return

        # 边界限制
        new_rect = new_rect.intersected(QRect(0, 0, self.width(), self.height()))

        # 宽高比锁定
        if self._aspect_ratio > 0 and new_rect.isValid():
            # 以宽度为基准锁定高度
            locked_h = int(new_rect.width() / self._aspect_ratio)
            new_rect.setHeight(locked_h)
            # 如果超出边界，以高度为基准重新计算
            if new_rect.bottom() > self.height():
                new_rect.setHeight(self.height() - new_rect.top())
                locked_w = int(new_rect.height() * self._aspect_ratio)
                new_rect.setWidth(locked_w)

        self.crop_rect = new_rect
        self.update()
        self.crop_rect_changed.emit(self.crop_rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mode = _OUTSIDE
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # ── 辅助 ────────────────────────────────────────────

    @staticmethod
    def _cursor_for_mode(mode: int):
        mapping = {
            _RESIZE_TL: Qt.CursorShape.SizeFDiagCursor,
            _RESIZE_BR: Qt.CursorShape.SizeFDiagCursor,
            _RESIZE_TR: Qt.CursorShape.SizeBDiagCursor,
            _RESIZE_BL: Qt.CursorShape.SizeBDiagCursor,
            _RESIZE_TOP:   Qt.CursorShape.SizeVerCursor,
            _RESIZE_BOT:   Qt.CursorShape.SizeVerCursor,
            _RESIZE_LEFT:  Qt.CursorShape.SizeHorCursor,
            _RESIZE_RIGHT: Qt.CursorShape.SizeHorCursor,
            _MOVE: Qt.CursorShape.SizeAllCursor,
        }
        return mapping.get(mode, Qt.CursorShape.ArrowCursor)
