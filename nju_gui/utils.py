# utils.py - 工具类文件
import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor

class BackgroundWidget(QWidget):
    """带背景图片的自定义Widget"""
    def __init__(self, background_path):
        super().__init__()
        self.background_path = background_path
        
    def paintEvent(self, event):
        painter = QPainter(self)
        if os.path.exists(self.background_path):
            pixmap = QPixmap(self.background_path)
            # 缩放背景图片以适应窗口
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # 如果背景图片不存在，使用渐变背景
            gradient = QColor(45, 45, 85)
            painter.fillRect(self.rect(), gradient)