# main_system_page.py - 主功能页面文件（最终修复版本）
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QGridLayout, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from utils import BackgroundWidget

class LargeModuleCard(QFrame):
    """放大的功能模块卡片"""
    clicked = pyqtSignal(str)  # 发送模块名称
    
    def __init__(self, module_name, icon_path, features, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.icon_path = icon_path
        self.features = features
        self.title_label = None
        self.icon_label = None
        self.feature_labels = []
        self.init_ui()
        
    def init_ui(self):
        """初始化卡片UI"""
        # 设置响应式高度，让卡片能够根据内容自动调整
        self.setMinimumSize(350, 480)  # 减小最小高度
        self.setMaximumSize(600, 1200)  # 增大最大高度给更多空间
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 3px solid #e0e0e0;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: rgba(255, 255, 255, 1.0);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)  # 减小边距
        layout.setSpacing(15)  # 减小间距
        
        # 图标区域（不可点击）- 改为响应式大小
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setMinimumSize(150, 150)  # 最小尺寸
        self.icon_label.setMaximumSize(400, 400)  # 最大尺寸
        self.icon_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 尝试加载图标 - 初始大小
        if os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            # 如果图标不存在，显示默认图标
            default_icons = {
                "暴露分析": "📊",
                "风险表征": "⚠️", 
                "风险溯源": "🗺️"
            }
            icon_text = default_icons.get(self.module_name, "📋")
            self.icon_label.setText(icon_text)
            self.icon_label.setStyleSheet("""
                QLabel {
                    font-size: 80px;
                    color: #3498db;
                    background-color: #f8f9fa;
                    border-radius: 75px;
                    border: 3px solid #e9ecef;
                }
            """)
        
        layout.addWidget(self.icon_label, 0, Qt.AlignCenter)
        
        # 模块标题（可点击）- 使用最小高度而不是固定高度
        self.title_label = QLabel(self.module_name)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setMinimumHeight(60)  # 改为最小高度
        self.title_label.setMaximumHeight(120)  # 设置最大高度防止过大
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #2c3e50;
                margin: 15px 0;
                padding: 10px;
                background-color: transparent;
                border: none;
            }
        """)
        self.title_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.title_label)
        
        # 功能列表容器 - 使用响应式高度
        features_container = QFrame()
        features_container.setMinimumHeight(100)  # 改为最小高度
        features_container.setMaximumHeight(200)  # 设置最大高度
        features_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        features_container.setStyleSheet("background-color: transparent; border: none;")
        features_layout = QVBoxLayout(features_container)
        features_layout.setContentsMargins(0, 10, 0, 10)
        features_layout.setSpacing(12)
        
        # 功能列表（不可点击，无边框）- 增大字体
        for feature in self.features:
            feature_label = QLabel(f"• {feature}")
            feature_label.setAlignment(Qt.AlignCenter)
            feature_label.setWordWrap(True)  # 允许自动换行
            feature_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            feature_label.setStyleSheet("""
                QLabel {
                    font-size: 26px;
                    color: #34495e;
                    margin: 8px 0;
                    padding: 8px;
                    background-color: transparent;
                    border: none;
                }
            """)
            # 确保功能描述不可点击
            feature_label.setCursor(Qt.ArrowCursor)
            features_layout.addWidget(feature_label)
            self.feature_labels.append(feature_label)
        
        # 添加伸缩空间确保功能描述居中
        features_layout.addStretch()
        layout.addWidget(features_container)
        
        layout.addStretch()
        
    def resizeEvent(self, event):
        """重写大小改变事件，实现完全响应式"""
        super().resizeEvent(event)
        
        # 根据卡片大小动态调整内容
        width = self.width()
        height = self.height()
        
        # 计算图标大小：卡片宽度的25-45%
        icon_size = max(120, min(280, int(width * 0.35)))
        
        # 计算字体大小 - 显著增大字体
        title_font_size = max(28, min(60, int(width * 0.1)))  # 大幅增大标题字体
        feature_font_size = max(20, min(36, int(width * 0.065)))  # 大幅增大描述字体
        
        # 根据字体大小动态调整容器高度
        title_height = max(70, min(150, title_font_size * 2.2))
        features_height = max(120, min(250, feature_font_size * 5.5))
        
        # 更新图标大小
        if self.icon_label.pixmap():
            # 如果是图片图标
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(scaled_pixmap)
        else:
            # 如果是emoji图标
            emoji_font_size = max(60, min(160, int(icon_size * 0.6)))
            self.icon_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {emoji_font_size}px;
                    color: #3498db;
                    background-color: #f8f9fa;
                    border-radius: {icon_size//2}px;
                    border: 3px solid #e9ecef;
                }}
            """)
        
        # 更新图标容器尺寸
        self.icon_label.setFixedSize(icon_size, icon_size)
        
        # 更新容器高度
        if self.title_label:
            self.title_label.setMinimumHeight(int(title_height))
            self.title_label.setMaximumHeight(int(title_height * 1.8))
        
        # 更新标题字体
        if self.title_label:
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {title_font_size}px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 8px 0;
                    padding: 5px;
                    background-color: transparent;
                    border: none;
                }}
            """)
        
        # 更新功能描述字体
        for feature_label in self.feature_labels:
            feature_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {feature_font_size}px;
                    color: #34495e;
                    margin: 6px 0;
                    padding: 6px;
                    background-color: transparent;
                    border: none;
                    line-height: 1.4;
                }}
            """)
    
    def mousePressEvent(self, event):
        """点击事件 - 只响应标题区域的点击"""
        if event.button() == Qt.LeftButton:
            # 检查点击位置是否在标题区域
            title_rect = self.title_label.geometry()
            if title_rect.contains(event.pos()):
                self.clicked.emit(self.module_name)
        # 不调用super()，防止整个卡片响应点击

class MainSystemPage(BackgroundWidget):
    """主功能系统页面"""
    logout_signal = pyqtSignal()
    module_selected = pyqtSignal(str)
    
    def __init__(self):
        # 使用背景图片，如果不存在则使用空字符串
        background_path = "D:\\nju_gui\\VCG211410114301.jpg"
        if not os.path.exists(background_path):
            background_path = ""
        super().__init__(background_path)
        
        # 保存组件引用用于响应式
        self.title_label = None
        self.cards = []
        self.init_ui()
        
    def resizeEvent(self, event):
        """重写窗口大小改变事件，让标题字体响应式缩放"""
        super().resizeEvent(event)
        
        if self.title_label:
            window_width = self.width()
            # 标题字体：窗口宽度的3-5%，范围40px-100px
            title_font_size = max(40, min(100, int(window_width * 0.045)))
            
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    font-size: {title_font_size}px;
                    font-weight: bold;
                    margin: 30px 0;
                }}
            """)
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 40)
        
        # 顶部区域：标题和用户信息
        top_layout = QHBoxLayout()
        
        # 系统标题
        self.title_label = QLabel("核心模块")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 60px;
                font-weight: bold;
                margin: 30px 0;
            }
        """)
        
        # 退出登录按钮
        logout_btn = QPushButton("退出登录")
        logout_btn.setFixedSize(140, 50)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.8);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(231, 76, 60, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(192, 57, 43, 1.0);
            }
        """)
        logout_btn.clicked.connect(self.logout_signal.emit)
        
        top_layout.addStretch()
        top_layout.addWidget(logout_btn)
        main_layout.addLayout(top_layout)
        
        # 标题居中
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        main_layout.addLayout(title_layout)
        
        main_layout.addStretch(1)
        
        # 功能模块卡片区域 - 响应式布局
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(50)  # 增大卡片间距
        cards_layout.setContentsMargins(20, 0, 20, 0)
        
        # 模块数据 - 重新添加功能描述
        modules_data = [
            {
                "name": "暴露分析",
                "icon": "exposure_analysis.png",
                "features": ["质谱数据处理", "环境浓度预测"]
            },
            {
                "name": "风险表征",
                "icon": "risk_assessment.png",
                "features": ["毒性数据获取", "风险物质排序"]
            },
            {
                "name": "风险溯源",
                "icon": "risk_tracing.png",
                "features": ["使用清单匹配", "企业源头追溯"]
            }
        ]
        
        # 创建模块卡片
        for module_data in modules_data:
            card = LargeModuleCard(
                module_data["name"],
                module_data["icon"],
                module_data["features"]  # 重新添加功能描述参数
            )
            card.clicked.connect(self.on_module_clicked)
            self.cards.append(card)
            cards_layout.addWidget(card, 1)  # 每个卡片占相等空间
        
        main_layout.addLayout(cards_layout)
        main_layout.addStretch(2)
        
        # 底部信息
        info_layout = QHBoxLayout()
        version_label = QLabel("园区高风险新污染物智慧识别系统 (v1.0)")
        version_label.setAlignment(Qt.AlignLeft)
        version_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 18px;
                margin: 10px;
            }
        """)
        
        # 只保留南京大学logo，去掉文字
        nju_logo = QLabel()
        logo_path = "./logo.png"
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            # 大幅放大logo - 从80×60增加到120×90
            scaled_logo = logo_pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            nju_logo.setPixmap(scaled_logo)
            nju_logo.setAlignment(Qt.AlignRight)
        
        info_layout.addWidget(version_label)
        info_layout.addStretch()
        if nju_logo.pixmap():
            info_layout.addWidget(nju_logo)
        
        main_layout.addLayout(info_layout)
        
        self.setLayout(main_layout)
    
    def on_module_clicked(self, module_name):
        """模块点击事件处理"""
        print(f"点击了模块标题: {module_name}")
        self.module_selected.emit(module_name)
        
        # 显示模块选择提示
        msg = QMessageBox()
        msg.setWindowTitle("模块选择")
        msg.setText(f"您点击了 '{module_name}' 模块标题\n\n该功能正在开发中...")
        msg.setIcon(QMessageBox.Information)
        
        # 设置按钮
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()