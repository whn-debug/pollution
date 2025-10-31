# login_page.py - 登录页面文件（CSV验证 + 字体响应式版本）
import csv
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFrame, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from utils import BackgroundWidget

class LoginPage(BackgroundWidget):
    """登录页面"""
    switch_to_main = pyqtSignal()
    login_success = pyqtSignal()
    
    def __init__(self):
        # 使用渐变背景替代图片
        super().__init__(use_gradient=True)
        # 保存元素引用以便在resizeEvent中使用
        self.form_frame = None
        self.login_title = None
        self.back_btn = None
        self.login_btn = None
        self.init_ui()
        
    def resizeEvent(self, event):
        """重写窗口大小改变事件，让所有元素和字体响应式缩放"""
        super().resizeEvent(event)
        if self.form_frame and self.login_title and self.back_btn and self.login_btn:
            # 根据表单当前大小计算字体大小
            form_width = self.form_frame.width()
            
            # 标题字体：表单宽度的6-8%，范围24px-48px
            title_font_size = max(24, min(48, int(form_width * 0.07)))
            # 返回按钮字体：表单宽度的3-4%，范围15px-28px
            back_font_size = max(15, min(28, int(form_width * 0.04)))
            
            # 登录按钮字体：表单宽度的4-5%，范围16px-32px
            login_font_size = max(16, min(32, int(form_width * 0.045)))
            
            # 输入框字体：表单宽度的3.5-4.5%，范围14px-28px
            input_font_size = max(14, min(28, int(form_width * 0.04)))
            
            # 返回按钮大小和字体
            back_width = max(100, min(200, int(form_width * 0.3)))
            back_height = max(40, min(80, int(back_width * 0.4)))
            self.back_btn.setFixedSize(back_width, back_height)
            self.back_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(102, 126, 234, 0.8),
                        stop:1 rgba(118, 75, 162, 0.8));
                    color: white;
                    border: none;
                    border-radius: {back_height // 2}px;
                    font-size: {back_font_size}px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei", sans-serif;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(102, 126, 234, 1.0),
                        stop:1 rgba(118, 75, 162, 1.0));
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(82, 106, 214, 1.0),
                        stop:1 rgba(98, 55, 142, 1.0));
                }}
            """)
            
            # 更新标题字体（增强视觉效果）
            self.login_title.setStyleSheet(f"""
                QLabel {{
                    color: #ffffff;
                    font-size: {title_font_size}px;
                    font-weight: bold;
                    margin-top: 15px;
                    margin-bottom: 35px;
                    font-family: "Microsoft YaHei", sans-serif;
                    letter-spacing: 6px;
                }}
            """)
            
            # 更新输入框字体（优化样式）
            input_style = f"""
                QLineEdit {{
                    background-color: rgba(255, 255, 255, 0.95);
                    border: 2px solid rgba(255, 255, 255, 0.25);
                    border-radius: 12px;
                    padding: 16px 20px;
                    font-size: {input_font_size}px;
                    margin-bottom: 18px;
                    color: #1a1a2e;
                    font-family: "Microsoft YaHei", sans-serif;
                }}
                QLineEdit:focus {{
                    border: 2px solid rgba(102, 126, 234, 1.0);
                    background-color: rgba(255, 255, 255, 1.0);
                }}
                QLineEdit::placeholder {{
                    color: rgba(44, 62, 80, 0.5);
                }}
            """
            
            self.username_input.setStyleSheet(input_style)
            self.password_input.setStyleSheet(input_style.replace("margin-bottom: 18px", "margin-bottom: 30px"))
            
            # 更新登录按钮字体（优化渐变按钮）
            self.login_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 1.0),
                        stop:1 rgba(118, 75, 162, 1.0));
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: {login_font_size}px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei", sans-serif;
                    letter-spacing: 3px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(122, 146, 254, 1.0),
                        stop:1 rgba(138, 95, 182, 1.0));
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(82, 106, 214, 1.0),
                        stop:1 rgba(98, 55, 142, 1.0));
                }}
            """)

    def load_users_from_csv(self, csv_file_path="users.csv"):
        """从CSV文件加载用户数据"""
        users = {}
        try:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        username = row.get('username', '').strip()
                        password = row.get('password', '').strip()
                        if username and password:  # 确保用户名和密码都不为空
                            users[username] = password
                return users
            else:
                return {}
        except Exception as e:
            return {}
    
    def validate_user(self, username, password):
        """验证用户名和密码"""
        users = self.load_users_from_csv()
        
        if not users:
            return False, "无法加载用户数据，请检查CSV文件是否存在"
        
        if username not in users:
            return False, f"用户名 '{username}' 不存在"
        
        if users[username] != password:
            return False, "密码错误，请检查后重试"
        
        return True, "登录成功"
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # 返回按钮 - 保存引用
        self.back_btn = QPushButton("← 返回")
        # 设置最小和最大尺寸，允许缩放
        self.back_btn.setMinimumSize(100, 40)
        self.back_btn.setMaximumSize(200, 80)
        # 设置尺寸策略
        self.back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(102, 126, 234, 0.8),
                    stop:1 rgba(118, 75, 162, 0.8));
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
            }
        """)
        self.back_btn.clicked.connect(self.switch_to_main.emit)
        
        top_layout = QHBoxLayout()
        # 给返回按钮一些空间进行缩放
        top_layout.addWidget(self.back_btn, 1)  # 占1份空间
        top_layout.addStretch(4)  # 剩余空间
        main_layout.addLayout(top_layout)
        
        main_layout.addStretch()
        
        # 登录表单 - 保存引用
        self.form_frame = QFrame()
        # 移除固定尺寸，改为最小和最大尺寸限制
        self.form_frame.setMinimumSize(400, 320)
        self.form_frame.setMaximumSize(800, 640)
        # 设置尺寸策略，让表单能够扩展
        self.form_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 增强的毛玻璃效果卡片 + 阴影
        self.form_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.18);
                border-radius: 32px;
            }
        """)
        
        form_layout = QVBoxLayout(self.form_frame)
        form_layout.setContentsMargins(50, 50, 50, 50)
        
        # 添加装饰性顶部渐变条
        top_decoration = QLabel()
        top_decoration.setFixedHeight(6)
        top_decoration.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.8),
                    stop:0.5 rgba(118, 75, 162, 0.8),
                    stop:1 rgba(102, 126, 234, 0.8));
                border-radius: 3px;
                margin-bottom: 10px;
            }
        """)
        form_layout.addWidget(top_decoration)

        # 登录标题 - 保存引用（增强的视觉效果）
        self.login_title = QLabel("用户登录")
        self.login_title.setAlignment(Qt.AlignCenter)
        self.login_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 38px;
                font-weight: bold;
                margin-top: 15px;
                margin-bottom: 35px;
                font-family: "Microsoft YaHei", sans-serif;
                letter-spacing: 6px;
            }
        """)
        form_layout.addWidget(self.login_title)
        
        # 用户名输入 - 改为响应式
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        # 设置最小和最大高度范围
        self.username_input.setMinimumHeight(50)
        self.username_input.setMaximumHeight(100)
        # 设置尺寸策略
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                margin-bottom: 18px;
                color: #1a1a2e;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 1.0);
                background-color: rgba(255, 255, 255, 1.0);
            }
            QLineEdit::placeholder {
                color: rgba(44, 62, 80, 0.5);
            }
        """)
        form_layout.addWidget(self.username_input)
        
        # 密码输入 - 改为响应式
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        # 设置最小和最大高度范围
        self.password_input.setMinimumHeight(50)
        self.password_input.setMaximumHeight(100)
        # 设置尺寸策略
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 18px;
                margin-bottom: 30px;
                color: #1a1a2e;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid rgba(102, 126, 234, 1.0);
                background-color: rgba(255, 255, 255, 1.0);
            }
            QLineEdit::placeholder {
                color: rgba(44, 62, 80, 0.5);
            }
        """)
        form_layout.addWidget(self.password_input)
        
        # 登录按钮 - 保存引用
        self.login_btn = QPushButton("登录")
        # 改为最小和最大高度，允许扩展
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setMaximumHeight(90)
        # 设置尺寸策略
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 22px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                letter-spacing: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(122, 146, 254, 1.0),
                    stop:1 rgba(138, 95, 182, 1.0));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(82, 106, 214, 1.0),
                    stop:1 rgba(98, 55, 142, 1.0));
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)
        
        # 按回车键也可以登录
        self.password_input.returnPressed.connect(self.handle_login)
        
        # 居中显示登录表单 - 添加边距让表单能够缩放
        center_layout = QHBoxLayout()
        center_layout.addStretch(1)  # 左边距
        center_layout.addWidget(self.form_frame, 2)  # 表单占2份空间
        center_layout.addStretch(1)  # 右边距
        
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def handle_login(self):
        """处理登录逻辑 - 使用CSV文件验证"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # 基本输入验证
        if not username:
            self.show_message("输入错误", "请输入用户名")
            return
        
        if not password:
            self.show_message("输入错误", "请输入密码")
            return
        
        # 使用CSV文件验证用户
        is_valid, message = self.validate_user(username, password)
        
        if is_valid:
            self.show_message("登录成功", f"欢迎您，{username}！")
            self.login_success.emit()
        else:
            self.show_message("登录失败", message)
    
    def show_message(self, title, message):
        """显示消息框"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # 根据标题设置不同的图标
        if "成功" in title:
            msg_box.setIcon(QMessageBox.Information)
        elif "失败" in title or "错误" in title:
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Warning)
        
        msg_box.exec_()