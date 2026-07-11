# src/image_processor.py
# -*- coding: utf-8 -*-
"""
图像处理核心逻辑

提供：裁剪、背景替换、尺寸调整、颜色/尺寸映射等静态方法。

背景替换支持两种模式（自动降级）：
  1. AI 抠图 — 使用 rembg 深度学习模型，效果最佳（处理任意背景）
  2. HSV 颜色键控 — 针对绿幕/蓝幕纯色背景的基础方案
"""

import logging
import cv2
import numpy as np
from PySide6.QtCore import QRect

logger = logging.getLogger(__name__)

# 尝试导入 AI 抠图库
try:
    import rembg
    import PIL.Image as PILImage

    _REMBG_AVAILABLE = True
except ImportError:  # pragma: no cover
    _REMBG_AVAILABLE = False


class ImageProcessor:
    """图像处理工具类（所有方法均为静态）"""

    # ── 颜色映射表（OpenCV BGR 格式） ─────────────────
    COLOR_MAP = {
        '红色':   (0, 0, 255),
        '蓝色':   (255, 0, 0),
        '白色':   (255, 255, 255),
        '灰色':   (128, 128, 128),
        '绿色':   (0, 255, 0),
    }

    # ── 标准证件照尺寸（宽, 高）像素（300 DPI） ─────
    SIZE_MAP = {
        '一寸':     (295, 413),
        '二寸':     (413, 579),
        '小一寸':   (260, 370),
        '大一寸':   (389, 566),
        '小二寸':   (357, 480),
        '大二寸':   (413, 626),
        '三寸':     (550, 787),
        '五寸':     (480, 640),
        '护照':     (390, 510),
        '签证':     (450, 540),
        '驾驶证':   (220, 320),
    }

    @classmethod
    def crop_image(cls, image: np.ndarray, rect: QRect) -> np.ndarray:
        """
        根据 QRect 裁剪图像

        Args:
            image: OpenCV 图像 (H, W, C)
            rect:  裁剪矩形

        Returns:
            裁剪后的图像
        """
        # 标准化矩形（处理负宽/高）
        rect = rect.normalized()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        h_img, w_img = image.shape[:2]

        # 边界安全
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        if w <= 0 or h <= 0:
            return image

        return image[y:y + h, x:x + w].copy()

    @classmethod
    def replace_background(
        cls,
        image: np.ndarray,
        target_color_bgr: tuple,
    ) -> np.ndarray:
        """
        替换背景色

        优先使用 rembg AI 抠图（效果最佳，支持任意背景）；
        降级时使用 HSV 颜色键控（仅适用于绿幕/蓝幕等纯色背景）。

        Args:
            image:           输入图像 (BGR)
            target_color_bgr: 目标背景色 (B, G, R)

        Returns:
            替换背景后的图像
        """
        # ── 策略 1：AI 抠图（rembg）────────────────────
        if _REMBG_AVAILABLE:
            try:
                return cls._replace_bg_rembg(image, target_color_bgr)
            except Exception as exc:
                logger.warning("rembg 处理失败，降级到 HSV 方案: %s", exc)

        # ── 策略 2：HSV 颜色键控（绿幕/蓝幕） ─────────
        return cls._replace_bg_hsv(image, target_color_bgr)

    # ── 私有实现 ────────────────────────────────────────

    @classmethod
    def _replace_bg_rembg(
        cls,
        image: np.ndarray,
        target_color_bgr: tuple,
    ) -> np.ndarray:
        """
        使用 rembg 深度学习模型生成前景蒙版并替换背景。

        流程：
          1. BGR → RGB（rembg 要求 RGB 输入）
          2. rembg.remove → 获取 RGBA 结果（alpha 为前景透明度）
          3. 用 alpha 蒙版合成目标背景色
          4. BGR 转回供 OpenCV 使用
        """
        # BGR → RGB（rembg 期望 RGB）
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # rembg 处理：输入 numpy array → 输出 PIL Image（RGBA）
        result_pil: PILImage.Image = rembg.remove(rgb)  # type: ignore[arg-type]
        result_np = np.array(result_pil)  # (H, W, 4) RGBA

        # 提取 alpha 通道并归一化到 [0, 1]
        alpha = result_np[:, :, 3].astype(np.float32) / 255.0

        # RGB → BGR（前景）
        fg = cv2.cvtColor(result_np[:, :, :3], cv2.COLOR_RGB2BGR)

        # 创建纯色背景
        bg = np.full_like(fg, target_color_bgr, dtype=np.uint8)

        # 合成：前景 * alpha + 背景 * (1 - alpha)
        # alpha=1 → 前景保留；alpha=0 → 显示背景
        for c in range(3):
            fg[:, :, c] = (fg[:, :, c] * alpha
                           + bg[:, :, c] * (1.0 - alpha))

        return fg

    @classmethod
    def _replace_bg_hsv(
        cls,
        image: np.ndarray,
        target_color_bgr: tuple,
    ) -> np.ndarray:
        """
        使用 HSV 颜色键控替换背景（针对绿幕/蓝幕纯色背景）。

        通过检测绿色范围生成二值蒙版，经形态学去噪 + 边缘羽化后合成。
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 绿色幕布检测范围
        lower_green = np.array([35, 80, 80])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 形态学操作去除噪点
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 边缘羽化
        mask = cv2.GaussianBlur(mask, (5, 5), 2)
        mask_float = mask.astype(np.float32) / 255.0

        # 合成：前景 * (1 - mask) + 背景 * mask
        # mask=1 → 原为绿幕区域 → 替换为目标背景色
        # mask=0 → 原为前景区域 → 保留
        bg = np.full_like(image, target_color_bgr, dtype=np.uint8)
        for c in range(3):
            image[:, :, c] = (image[:, :, c] * (1.0 - mask_float)
                              + bg[:, :, c] * mask_float)

        return image

    @classmethod
    def resize_for_standard(
        cls,
        image: np.ndarray,
        target_size: tuple | str,
    ) -> np.ndarray:
        """
        调整为标准证件照尺寸

        Args:
            image:       输入图像
            target_size: (宽, 高) 像素元组，或尺寸名称字符串（如 '一寸'）

        Returns:
            调整后的图像
        """
        if isinstance(target_size, str):
            target_size = cls.map_size_name_to_px(target_size)
        # OpenCV resize 要求 (宽, 高)
        return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    @classmethod
    def map_color_name_to_bgr(cls, color_name: str) -> tuple:
        """将颜色名称转为 OpenCV BGR 元组"""
        return cls.COLOR_MAP[color_name]

    @classmethod
    def map_size_name_to_px(cls, size_name: str) -> tuple:
        """将尺寸名称转为 (宽, 高) 像素"""
        return cls.SIZE_MAP[size_name]
