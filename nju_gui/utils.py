# utils.py - 工具类文件
import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QRadialGradient

class BackgroundWidget(QWidget):
    """现代化背景Widget - 支持渐变和图片"""
    def __init__(self, background_path=None, use_gradient=True):
        super().__init__()
        self.background_path = background_path
        self.use_gradient = use_gradient

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.use_gradient and self.background_path and os.path.exists(self.background_path):
            # 使用背景图片
            pixmap = QPixmap(self.background_path)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # 使用现代渐变背景（深蓝到深紫）
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor(26, 26, 46))      # #1a1a2e 深蓝
            gradient.setColorAt(0.5, QColor(22, 33, 62))      # #16213e 中间色
            gradient.setColorAt(1.0, QColor(15, 52, 96))      # #0f3460 深紫蓝
            painter.fillRect(self.rect(), gradient)

            # 添加径向渐变光晕效果（可选）
            radial = QRadialGradient(QPointF(self.width() * 0.3, self.height() * 0.2),
                                    min(self.width(), self.height()) * 0.6)
            radial.setColorAt(0.0, QColor(100, 126, 234, 30))  # 中心淡紫光晕
            radial.setColorAt(1.0, QColor(0, 0, 0, 0))         # 透明边缘
            painter.fillRect(self.rect(), radial)