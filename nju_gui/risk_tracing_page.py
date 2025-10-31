# risk_tracing_page.py - 风险溯源页面

import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QGridLayout, QSizePolicy, QMessageBox,
                             QFileDialog, QTextEdit, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from utils import BackgroundWidget

# 导入溯源模型
from tracing_model import trace_risk_source


class RiskTracingPage(BackgroundWidget):
    """风险溯源页面"""
    
    # 信号定义
    back_to_main = pyqtSignal()  # 返回主页面
    back_to_risk_assessment = pyqtSignal()  # 返回风险表征
    
    def __init__(self):
        # 使用渐变背景
        super().__init__(use_gradient=True)
        
        # 状态变量
        self.risk_data_file_path = None  # 风险数据文件路径
        self.enterprise_list_file_path = None  # 企业清单文件路径
        self.result_excel_path = None  # 计算结果Excel文件路径
        self.is_calculating = False  # 是否正在计算
        
        # 文件路径配置
        self.media_path = "media"
        self.templates_path = os.path.join(self.media_path, "templates")
        self.results_path = os.path.join(self.media_path, "results", "tracing_results")
        
        # 确保目录存在
        os.makedirs(self.results_path, exist_ok=True)
        
        # 组件引用
        self.module3_1 = None
        self.module3_2 = None
        self.module3_3 = None
        self.result_display = None
        
        # 按钮引用
        self.import_risk_btn = None
        self.upload_risk_btn = None
        self.upload_enterprise_btn = None
        self.calculate_btn = None
        self.download_result_btn = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # 顶部标题栏
        self.create_header(main_layout)
        
        # 模块选项卡
        self.create_module_tabs(main_layout)
        
        # 主要内容区域
        self.create_main_content(main_layout)
        
        # 底部导航
        self.create_bottom_navigation(main_layout)
        
        self.setLayout(main_layout)
    
    def create_header(self, parent_layout):
        """创建顶部标题栏"""
        header_layout = QHBoxLayout()
        
        # 系统标题
        title_label = QLabel("园区高风险新污染物智慧识别系统 (v1.0)")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                font-family: "Microsoft YaHei", sans-serif;
                letter-spacing: 2px;
            }
        """)
        
        # 南京大学Logo
        nju_logo = QLabel()
        logo_path = "./logo.png"
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            nju_logo.setPixmap(scaled_logo)
        else:
            nju_logo.setText("南京大学")
            nju_logo.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(nju_logo)
        
        parent_layout.addLayout(header_layout)
    
    def create_module_tabs(self, parent_layout):
        """创建模块选项卡"""
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(0)
        
        # 模块1：暴露分析（非活跃）
        module1_tab = QLabel("模块1 暴露分析")
        module1_tab.setFixedHeight(50)
        module1_tab.setAlignment(Qt.AlignCenter)
        module1_tab.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.6);
                font-size: 18px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px 8px 0 0;
                padding: 10px 30px;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)

        # 模块2：风险表征（非活跃）
        module2_tab = QLabel("模块2 风险表征")
        module2_tab.setFixedHeight(50)
        module2_tab.setAlignment(Qt.AlignCenter)
        module2_tab.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.6);
                font-size: 18px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px 8px 0 0;
                padding: 10px 30px;
                font-family: "Microsoft YaHei", sans-serif;
                margin-left: 10px;
            }
        """)

        # 模块3：风险溯源（当前活跃 - 毛玻璃效果）
        module3_tab = QLabel("模块3 风险溯源")
        module3_tab.setFixedHeight(50)
        module3_tab.setAlignment(Qt.AlignCenter)
        module3_tab.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.25);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-bottom: 2px solid rgba(102, 126, 234, 0.8);
                border-radius: 8px 8px 0 0;
                padding: 10px 30px;
                font-family: "Microsoft YaHei", sans-serif;
                margin-left: 10px;
            }
        """)
        
        tabs_layout.addWidget(module1_tab)
        tabs_layout.addWidget(module2_tab)
        tabs_layout.addWidget(module3_tab)
        tabs_layout.addStretch()
        
        parent_layout.addLayout(tabs_layout)
    
    def create_main_content(self, parent_layout):
        """创建主要内容区域"""
        # 主容器 - 毛玻璃效果
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 0 0 16px 16px;
                padding: 20px;
            }
        """)
        
        main_content_layout = QVBoxLayout(main_container)
        main_content_layout.setSpacing(15)
        
        # 三个子模块
        modules_layout = QHBoxLayout()
        modules_layout.setSpacing(30)
        
        # 模块3-1：风险数据导入
        self.create_module_3_1(modules_layout)
        
        # 模块3-2：企业清单上传
        self.create_module_3_2(modules_layout)
        
        # 模块3-3：溯源计算
        self.create_module_3_3(modules_layout)
        
        main_content_layout.addLayout(modules_layout)
        
        # 结果显示区域
        self.create_result_area(main_content_layout)
        
        # 提示信息 - 紧凑样式
        tip_label = QLabel("💡 提示：模块3-1 ～ 3-3逐步解锁，绿色指示灯为当前可操作模块，红色为锁定状态")
        tip_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                font-weight: bold;
                padding: 8px 15px;
                background-color: rgba(255, 179, 71, 0.15);
                border: 1px solid rgba(255, 179, 71, 0.3);
                border-radius: 6px;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        tip_label.setWordWrap(True)
        tip_label.setMaximumHeight(40)
        main_content_layout.addWidget(tip_label)
        
        parent_layout.addWidget(main_container)
    
    def create_module_3_1(self, parent_layout):
        """创建模块3-1：风险数据导入"""
        module3_1_container = QFrame()
        module3_1_container.setFixedWidth(250)
        module3_1_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module3_1_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module3_1 = QLabel("●")
        self.module3_1.setStyleSheet("QLabel { color: #00f2a0; font-size: 18px; }")  # 绿色
        
        title_label = QLabel("模块3-1\n风险数据导入")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module3_1)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 导入风险数据按钮
        self.import_risk_btn = QPushButton("导入风险数据")
        self.import_risk_btn.setFixedHeight(40)
        self.import_risk_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(122, 146, 254, 1.0),
                    stop:1 rgba(138, 95, 182, 1.0));
            }
        """)
        self.import_risk_btn.clicked.connect(self.import_risk_data)
        layout.addWidget(self.import_risk_btn)
        
        # 上传风险数据按钮
        self.upload_risk_btn = QPushButton("上传风险数据")
        self.upload_risk_btn.setFixedHeight(40)
        self.upload_risk_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(122, 146, 254, 1.0),
                    stop:1 rgba(138, 95, 182, 1.0));
            }
        """)
        self.upload_risk_btn.clicked.connect(self.upload_risk_data)
        layout.addWidget(self.upload_risk_btn)
        
        # 下载模板按钮
        download_template_3_1 = QPushButton("下载数据模板")
        download_template_3_1.setFixedHeight(32)
        download_template_3_1.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                font-size: 12px;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        download_template_3_1.clicked.connect(self.download_template_3_1)
        layout.addWidget(download_template_3_1)
        
        parent_layout.addWidget(module3_1_container)
    
    def create_module_3_2(self, parent_layout):
        """创建模块3-2：企业清单上传"""
        module3_2_container = QFrame()
        module3_2_container.setFixedWidth(250)
        module3_2_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module3_2_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module3_2 = QLabel("●")
        self.module3_2.setStyleSheet("QLabel { color: #e74c3c; font-size: 18px; }")  # 红色
        
        title_label = QLabel("模块3-2\n企业清单上传")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module3_2)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 上传数据清单按钮
        self.upload_enterprise_btn = QPushButton("上传数据清单")
        self.upload_enterprise_btn.setFixedHeight(40)
        self.upload_enterprise_btn.setEnabled(False)  # 初始禁用
        self.upload_enterprise_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
                color: white;
                border: none;
            }
            QPushButton:enabled:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(122, 146, 254, 1.0),
                    stop:1 rgba(138, 95, 182, 1.0));
            }
        """)
        self.upload_enterprise_btn.clicked.connect(self.upload_enterprise_list)
        layout.addWidget(self.upload_enterprise_btn)
        
        # 下载模板按钮
        download_template_3_2 = QPushButton("下载数据模板")
        download_template_3_2.setFixedHeight(32)
        download_template_3_2.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                font-size: 12px;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        download_template_3_2.clicked.connect(self.download_template_3_2)
        layout.addWidget(download_template_3_2)
        
        parent_layout.addWidget(module3_2_container)
    
    def create_module_3_3(self, parent_layout):
        """创建模块3-3：溯源计算"""
        module3_3_container = QFrame()
        module3_3_container.setFixedWidth(250)
        module3_3_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module3_3_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module3_3 = QLabel("●")
        self.module3_3.setStyleSheet("QLabel { color: #e74c3c; font-size: 18px; }")  # 红色
        
        title_label = QLabel("模块3-3\n溯源计算")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module3_3)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 开始计算按钮
        self.calculate_btn = QPushButton("开始计算")
        self.calculate_btn.setFixedHeight(40)
        self.calculate_btn.setEnabled(False)  # 初始禁用
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 242, 160, 1.0),
                    stop:1 rgba(0, 210, 140, 1.0));
                color: white;
                border: none;
            }
            QPushButton:enabled:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(20, 255, 180, 1.0),
                    stop:1 rgba(20, 230, 160, 1.0));
            }
        """)
        self.calculate_btn.clicked.connect(self.start_calculation)
        layout.addWidget(self.calculate_btn)
        
        # 下载结果按钮
        self.download_result_btn = QPushButton("下载结果")
        self.download_result_btn.setFixedHeight(32)
        self.download_result_btn.setEnabled(False)  # 初始禁用
        self.download_result_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                font-size: 12px;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 179, 71, 1.0),
                    stop:1 rgba(255, 143, 29, 1.0));
                color: white;
                border: none;
            }
            QPushButton:enabled:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 199, 91, 1.0),
                    stop:1 rgba(255, 163, 49, 1.0));
            }
        """)
        self.download_result_btn.clicked.connect(self.download_result)
        layout.addWidget(self.download_result_btn)
        
        parent_layout.addWidget(module3_3_container)
    
    def create_result_area(self, parent_layout):
        """创建结果显示区域"""
        result_container = QFrame()
        result_container.setMinimumHeight(120)
        result_container.setMaximumHeight(180)
        result_container.setStyleSheet("""
            QFrame {
                border: none;
                background-color: transparent;
            }
        """)

        layout = QVBoxLayout(result_container)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(8)

        # 结果标题
        result_title = QLabel("计算状态")
        result_title.setFixedHeight(25)
        result_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: rgba(255, 255, 255, 0.95);
                font-family: "Microsoft YaHei", sans-serif;
                letter-spacing: 2px;
                border: none;
                background-color: transparent;
                padding: 0px;
            }
        """)
        layout.addWidget(result_title)

        # 结果显示文本框
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(70)
        self.result_display.setMaximumHeight(130)
        self.result_display.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 8px 10px;
                background-color: transparent;
                color: rgba(255, 255, 255, 0.85);
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
                line-height: 1.6;
            }
        """)
        self.result_display.setPlainText("等待导入或上传风险数据...")
        layout.addWidget(self.result_display)
        
        parent_layout.addWidget(result_container)
    
    def create_bottom_navigation(self, parent_layout):
        """创建底部导航"""
        nav_layout = QHBoxLayout()
        
        # 返回主页按钮
        back_btn = QPushButton("← 返回主页")
        back_btn.setFixedSize(120, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        back_btn.clicked.connect(self.back_to_main.emit)
        
        # 返回风险表征按钮
        prev_btn = QPushButton("← 上一模块 风险表征")
        prev_btn.setFixedSize(180, 40)
        prev_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 0.8),
                    stop:1 rgba(118, 75, 162, 0.8));
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(102, 126, 234, 1.0),
                    stop:1 rgba(118, 75, 162, 1.0));
            }
        """)
        prev_btn.clicked.connect(self.check_and_go_back)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(prev_btn)
        
        parent_layout.addLayout(nav_layout)
    
    # 功能方法
    def import_risk_data(self):
        """导入风险数据（从模块2-3结果）"""
        # 尝试查找最近的模块2-3结果文件
        risk_results_path = os.path.join(self.media_path, "results", "risk_results")
        
        if not os.path.exists(risk_results_path):
            QMessageBox.warning(self, "警告", "未找到模块2-3的结果目录！\n请先完成风险表征模块的计算。")
            return
        
        # 获取目录下的所有xlsx文件
        excel_files = [f for f in os.listdir(risk_results_path) if f.endswith('.xlsx')]
        
        if not excel_files:
            QMessageBox.warning(self, "警告", "未找到模块2-3的结果文件！\n请先完成风险表征模块的计算。")
            return
        
        # 使用最新的文件
        excel_files.sort(reverse=True)
        latest_file = os.path.join(risk_results_path, excel_files[0])
        
        self.risk_data_file_path = latest_file
        self.result_display.clear()
        self.result_display.append(f"✓ 已导入风险数据：{excel_files[0]}")
        
        # 激活模块3-2
        self.activate_module_3_2()
        
        QMessageBox.information(self, "导入成功", f"已导入风险数据：\n{excel_files[0]}")
    
    def upload_risk_data(self):
        """上传风险数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择风险数据文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.risk_data_file_path = file_path
            self.result_display.clear()
            self.result_display.append(f"✓ 已上传风险数据：{os.path.basename(file_path)}")
            
            # 激活模块3-2
            self.activate_module_3_2()
            
            QMessageBox.information(self, "上传成功", f"风险数据上传成功！\n文件：{os.path.basename(file_path)}")
    
    def activate_module_3_2(self):
        """激活模块3-2"""
        self.module3_2.setStyleSheet("QLabel { color: #00f2a0; font-size: 18px; }")
        self.upload_enterprise_btn.setEnabled(True)
        self.result_display.append("模块3-2已解锁，请上传企业清单")
    
    def download_template_3_1(self):
        """下载模块3-1数据模板"""
        template_source = os.path.join(self.templates_path, "风险数据模板.xlsx")
        
        if not os.path.exists(template_source):
            QMessageBox.warning(self, "提示", f"模板文件不存在，请检查目录：\n{template_source}")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存风险数据模板", "风险数据模板.xlsx", "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(template_source, save_path)
                QMessageBox.information(self, "模板下载", f"模板已保存至：\n{save_path}")
                self.result_display.append(f"✓ 模板3-1已下载：{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模板下载失败：{str(e)}")
    
    def upload_enterprise_list(self):
        """上传企业清单"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择企业清单文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.enterprise_list_file_path = file_path
            self.result_display.append(f"\n✓ 已上传企业清单：{os.path.basename(file_path)}")
            
            # 激活模块3-3
            self.module3_3.setStyleSheet("QLabel { color: #00f2a0; font-size: 18px; }")
            self.calculate_btn.setEnabled(True)
            self.result_display.append("模块3-3已解锁，可以开始计算")
            
            QMessageBox.information(self, "上传成功", f"企业清单上传成功！\n文件：{os.path.basename(file_path)}")
    
    def download_template_3_2(self):
        """下载模块3-2数据模板"""
        template_source = os.path.join(self.templates_path, "企业清单模板.xlsx")
        
        if not os.path.exists(template_source):
            QMessageBox.warning(self, "提示", f"模板文件不存在，请检查目录：\n{template_source}")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存企业清单模板", "企业清单模板.xlsx", "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(template_source, save_path)
                QMessageBox.information(self, "模板下载", f"模板已保存至：\n{save_path}")
                self.result_display.append(f"✓ 模板3-2已下载：{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模板下载失败：{str(e)}")
    
    def start_calculation(self):
        """开始溯源计算"""
        if not self.risk_data_file_path:
            QMessageBox.warning(self, "警告", "请先导入或上传风险数据！")
            return
        
        if not self.enterprise_list_file_path:
            QMessageBox.warning(self, "警告", "请先上传企业清单！")
            return
        
        self.is_calculating = True
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.setText("计算中...")
        
        self.result_display.clear()
        self.result_display.append("开始执行风险溯源计算...")
        self.result_display.append(f"使用风险数据：{os.path.basename(self.risk_data_file_path)}")
        self.result_display.append(f"使用企业清单：{os.path.basename(self.enterprise_list_file_path)}")
        self.result_display.append("正在处理...")
        
        # 强制刷新界面
        QApplication.processEvents()
        
        try:
            # 生成输出文件路径（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"溯源结果_{timestamp}.xlsx"
            output_file_path = os.path.join(self.results_path, result_filename)
            
            # 调用溯源模型函数
            trace_risk_source(
                risk_file=self.risk_data_file_path,
                enterprise_list_file=self.enterprise_list_file_path,
                output_file=output_file_path
            )
            
            # 检查结果文件是否生成
            if not os.path.exists(output_file_path):
                raise Exception("模型计算完成，但未找到结果文件")
            
            # 保存结果文件路径
            self.result_excel_path = output_file_path
            
            # 计算完成
            self.is_calculating = False
            self.calculate_btn.setText("重新计算")
            self.calculate_btn.setEnabled(True)
            
            # 显示完成信息
            self.result_display.append("\n计算完成！")
            self.result_display.append(f"结果文件：{result_filename}")
            self.result_display.append("点击'下载结果'保存Excel文件")
            
            # 启用下载按钮
            self.download_result_btn.setEnabled(True)
            
            QMessageBox.information(self, "计算完成", "风险溯源计算完成！\n点击'下载结果'保存Excel文件。")
            
        except NotImplementedError as e:
            # 捕获TODO占位符的错误
            self.is_calculating = False
            self.calculate_btn.setText("开始计算")
            self.calculate_btn.setEnabled(True)
            
            error_msg = str(e)
            self.result_display.append(f"\n⚠️ {error_msg}")
            QMessageBox.warning(self, "功能未实现", error_msg)
            
        except Exception as e:
            self.is_calculating = False
            self.calculate_btn.setText("开始计算")
            self.calculate_btn.setEnabled(True)
            
            error_msg = f"计算过程中发生错误：{str(e)}"
            self.result_display.append(f"\n❌ {error_msg}")
            QMessageBox.critical(self, "计算错误", error_msg)
    
    def download_result(self):
        """下载计算结果Excel文件"""
        if not self.result_excel_path or not os.path.exists(self.result_excel_path):
            QMessageBox.warning(self, "警告", "没有可下载的结果文件！")
            return
        
        # 默认文件名使用原始文件名
        default_filename = os.path.basename(self.result_excel_path)
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存计算结果", default_filename, "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                # 复制结果文件到用户指定位置
                shutil.copy2(self.result_excel_path, save_path)
                
                QMessageBox.information(self, "下载成功", f"Excel结果文件已保存至：\n{save_path}")
                self.result_display.append(f"✓ 结果已下载：{os.path.basename(save_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"文件复制失败：{str(e)}")
    
    def check_and_go_back(self):
        """检查并返回上一模块"""
        if self.is_calculating:
            # 显示确认对话框
            reply = QMessageBox.question(
                self, "确认跳转",
                "本模块任务尚未完成，是否确认跳转？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.back_to_risk_assessment.emit()
        else:
            self.back_to_risk_assessment.emit()


# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = RiskTracingPage()
    window.resize(1400, 900)
    window.show()
    
    sys.exit(app.exec_())

