# main_page.py - 主页面文件
import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from utils import BackgroundWidget

class MainPage(BackgroundWidget):
    """主页面"""
    switch_to_login = pyqtSignal()
    
    def __init__(self):
        super().__init__("./VCG211410114301.jpg")
        self.start_btn = None  # 保存按钮引用
        self.init_ui()
        
    def resizeEvent(self, event):
        """重写窗口大小改变事件，让按钮和字体响应式缩放"""
        super().resizeEvent(event)
        if self.start_btn:
            # 根据窗口宽度计算按钮大小
            window_width = self.width()
            # 按钮宽度为窗口宽度的20-30%，最小180px，最大500px
            button_width = max(180, min(500, int(window_width * 0.25)))
            button_height = max(50, min(120, int(button_width * 0.3)))
            
            # 根据按钮大小计算字体大小
            # 字体大小根据按钮宽度调整，范围在16px到40px之间
            font_size = max(16, min(40, int(button_width * 0.08)))
            
            # 设置按钮大小
            self.start_btn.setFixedSize(button_width, button_height)
            
            # 动态更新按钮样式，包括字体大小
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(52, 152, 219, 0.8);
                    color: white;
                    border: none;
                    border-radius: 30px;
                    font-size: {font_size}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(52, 152, 219, 1.0);
                }}
                QPushButton:pressed {{
                    background-color: rgba(41, 128, 185, 1.0);
                }}
            """)
        
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # 顶部logo区域
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        # 南京大学logo
        logo_label = QLabel()
        if os.path.exists("./logo.png"):
            logo_pixmap = QPixmap("./logo.png")
            # 调整logo大小 - 增大logo
            scaled_logo = logo_pixmap.scaled(160, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            # 如果logo不存在，显示文字
            logo_label.setText("南京大学")
            logo_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        top_layout.addWidget(logo_label)
        main_layout.addLayout(top_layout)
        
        # 中间标题区域
        main_layout.addStretch(2)
        
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # 主标题
        main_title = QLabel("园区高风险新污染物")
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 72px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        
        # 副标题
        sub_title = QLabel("智慧识别系统 (v1.0)")
        sub_title.setAlignment(Qt.AlignCenter)
        sub_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 54px;
                font-weight: bold;
                margin-bottom: 80px;
            }
        """)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        main_layout.addLayout(title_layout)
        
        # 按钮区域 - 真正的响应式
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        # 开始使用按钮 - 保存引用以便在resizeEvent中使用
        self.start_btn = QPushButton("开始使用")
        self.start_btn.setMinimumSize(180, 50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 152, 219, 0.8);
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(41, 128, 185, 1.0);
            }
        """)
        self.start_btn.clicked.connect(self.switch_to_login.emit)
        
        button_layout.addWidget(self.start_btn)
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch(2)
        self.setLayout(main_layout)