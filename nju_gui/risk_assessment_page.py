# risk_assessment_page.py - 风险表征页面

import os
import sys
from datetime import datetime
from typing import List
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QGridLayout, QSizePolicy, QMessageBox,
                             QFileDialog, QTextEdit, QApplication, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from utils import BackgroundWidget

# 导入风险模型
from risk_model import calculate_risk


class RiskAssessmentPage(BackgroundWidget):
    """风险表征页面"""
    
    # 信号定义
    switch_to_risk_tracing = pyqtSignal()  # 跳转到风险溯源
    back_to_main = pyqtSignal()  # 返回主页面
    
    def __init__(self):
        # 使用渐变背景
        super().__init__(use_gradient=True)
        
        # 状态变量
        self.selected_endpoints = []  # 选中的毒性终点
        self.concentration_file_path = None  # 浓度数据文件路径
        self.result_excel_path = None  # 计算结果Excel文件路径
        self.is_calculating = False  # 是否正在计算
        
        # 文件路径配置
        self.media_path = "media"
        self.templates_path = os.path.join(self.media_path, "templates")
        self.results_path = os.path.join(self.media_path, "results", "risk_results")
        
        # 确保目录存在
        os.makedirs(self.results_path, exist_ok=True)
        
        # 组件引用
        self.module2_1 = None
        self.module2_2 = None
        self.module2_3 = None
        self.result_display = None
        self.endpoint_buttons = {}  # 存储终点按钮引用
        
        # 按钮引用
        self.submit_btn = None
        self.import_data_btn = None
        self.upload_data_btn = None
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

        # 模块2：风险表征（当前活跃 - 毛玻璃效果）
        module2_tab = QLabel("模块2 风险表征")
        module2_tab.setFixedHeight(50)
        module2_tab.setAlignment(Qt.AlignCenter)
        module2_tab.setStyleSheet("""
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

        # 模块3：风险溯源（非活跃）
        module3_tab = QLabel("模块3 风险溯源")
        module3_tab.setFixedHeight(50)
        module3_tab.setAlignment(Qt.AlignCenter)
        module3_tab.setStyleSheet("""
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
        main_content_layout.setSpacing(15)  # 从30缩小到15，减少模块和结果区域之间的间距
        
        # 三个子模块
        modules_layout = QHBoxLayout()
        modules_layout.setSpacing(30)  # 从40缩小到30，减少模块之间的横向间距
        
        # 模块2-1：毒性终点选择
        self.create_module_2_1(modules_layout)
        
        # 模块2-2：浓度数据导入
        self.create_module_2_2(modules_layout)
        
        # 模块2-3：风险计算
        self.create_module_2_3(modules_layout)
        
        main_content_layout.addLayout(modules_layout)
        
        # 结果显示区域
        self.create_result_area(main_content_layout)
        
        # 提示信息 - 紧凑样式
        tip_label = QLabel("💡 提示：模块2-1 ～ 2-3逐步解锁，绿色指示灯为当前可操作模块，红色为锁定状态")
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
    
    def create_module_2_1(self, parent_layout):
        """创建模块2-1：毒性终点选择"""
        module2_1_container = QFrame()
        module2_1_container.setFixedWidth(250)  # 从280缩小到250
        module2_1_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module2_1_container)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)  # 从12缩小到10
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module2_1 = QLabel("●")
        self.module2_1.setStyleSheet("QLabel { color: #00f2a0; font-size: 18px; }")  # 从20px缩小到18px
        
        title_label = QLabel("模块2-1\n毒性终点选择")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module2_1)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 13个终点按钮 - 网格布局（3列）
        endpoints_container = QFrame()
        endpoints_container.setStyleSheet("background-color: transparent; border: none;")
        endpoints_layout = QGridLayout(endpoints_container)
        endpoints_layout.setSpacing(6)  # 从8缩小到6
        endpoints_layout.setContentsMargins(0, 3, 0, 3)  # 从5缩小到3
        
        for i in range(13):
            endpoint_name = f"终点{i+1}"
            btn = QPushButton(endpoint_name)
            btn.setFixedHeight(26)  # 从28缩小到26
            btn.setCheckable(True)  # 使按钮可切换
            btn.setStyleSheet(self.get_endpoint_button_style(False))
            btn.clicked.connect(lambda checked, name=endpoint_name, button=btn: self.toggle_endpoint(name, button))
            
            row = i // 3
            col = i % 3
            endpoints_layout.addWidget(btn, row, col)
            
            self.endpoint_buttons[endpoint_name] = btn
        
        layout.addWidget(endpoints_container)
        
        # 提交按钮
        self.submit_btn = QPushButton("提交")
        self.submit_btn.setFixedHeight(36)  # 从40缩小到36
        self.submit_btn.setStyleSheet("""
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
        self.submit_btn.clicked.connect(self.submit_endpoints)
        layout.addWidget(self.submit_btn)
        
        parent_layout.addWidget(module2_1_container)
    
    def get_endpoint_button_style(self, is_selected):
        """获取终点按钮样式"""
        if is_selected:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(102, 126, 234, 1.0),
                        stop:1 rgba(118, 75, 162, 1.0));
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei", sans-serif;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(122, 146, 254, 1.0),
                        stop:1 rgba(138, 95, 182, 1.0));
                }
            """
        else:
            return """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    color: rgba(255, 255, 255, 0.8);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 6px;
                    font-size: 11px;
                    font-family: "Microsoft YaHei", sans-serif;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """
    
    def toggle_endpoint(self, endpoint_name, button):
        """切换终点选中状态"""
        if button.isChecked():
            # 选中
            if endpoint_name not in self.selected_endpoints:
                self.selected_endpoints.append(endpoint_name)
            button.setStyleSheet(self.get_endpoint_button_style(True))
        else:
            # 取消选中
            if endpoint_name in self.selected_endpoints:
                self.selected_endpoints.remove(endpoint_name)
            button.setStyleSheet(self.get_endpoint_button_style(False))
        
        # 移除了每次选中时的提示，只在提交时统一显示
    
    def submit_endpoints(self):
        """提交毒性终点选择"""
        if not self.selected_endpoints:
            QMessageBox.warning(self, "警告", "请至少选择一个毒性终点！")
            return
        
        # 激活模块2-2
        self.module2_2.setStyleSheet("QLabel { color: #00f2a0; font-size: 18px; }")  # 修正字体大小
        self.import_data_btn.setEnabled(True)
        self.upload_data_btn.setEnabled(True)
        
        # 统一在提交时显示所有选中的终点
        self.result_display.clear()
        self.result_display.append(f"✓ 已选择 {len(self.selected_endpoints)} 个毒性终点：")
        self.result_display.append(f"  {', '.join(self.selected_endpoints)}")
        self.result_display.append("\n模块2-2已解锁，请导入或上传浓度数据")
        
        QMessageBox.information(self, "提交成功", 
                               f"已选择 {len(self.selected_endpoints)} 个毒性终点：\n{', '.join(self.selected_endpoints)}\n\n模块2-2已解锁！")
    
    def create_module_2_2(self, parent_layout):
        """创建模块2-2：浓度数据导入"""
        module2_2_container = QFrame()
        module2_2_container.setFixedWidth(250)  # 从280缩小到250
        module2_2_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module2_2_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)  # 从15缩小到12
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module2_2 = QLabel("●")
        self.module2_2.setStyleSheet("QLabel { color: #e74c3c; font-size: 18px; }")  # 从20px缩小到18px
        
        title_label = QLabel("模块2-2\n浓度数据导入")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module2_2)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 导入浓度数据按钮
        self.import_data_btn = QPushButton("导入浓度数据")
        self.import_data_btn.setFixedHeight(40)  # 从45缩小到40
        self.import_data_btn.setEnabled(False)  # 初始禁用
        self.import_data_btn.setStyleSheet("""
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
        self.import_data_btn.clicked.connect(self.import_concentration_data)
        layout.addWidget(self.import_data_btn)
        
        # 上传数据按钮
        self.upload_data_btn = QPushButton("上传数据")
        self.upload_data_btn.setFixedHeight(40)  # 从45缩小到40
        self.upload_data_btn.setEnabled(False)  # 初始禁用
        self.upload_data_btn.setStyleSheet("""
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
        self.upload_data_btn.clicked.connect(self.upload_concentration_data)
        layout.addWidget(self.upload_data_btn)
        
        # 下载模板按钮
        download_template_2_2 = QPushButton("下载数据模板")
        download_template_2_2.setFixedHeight(32)  # 从35缩小到32
        download_template_2_2.setStyleSheet("""
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
        download_template_2_2.clicked.connect(self.download_template_2_2)
        layout.addWidget(download_template_2_2)
        
        parent_layout.addWidget(module2_2_container)
    
    def create_module_2_3(self, parent_layout):
        """创建模块2-3：风险计算"""
        module2_3_container = QFrame()
        module2_3_container.setFixedWidth(250)  # 从280缩小到250
        module2_3_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(module2_3_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)  # 从15缩小到12
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module2_3 = QLabel("●")
        self.module2_3.setStyleSheet("QLabel { color: #e74c3c; font-size: 18px; }")  # 从20px缩小到18px
        
        title_label = QLabel("模块2-3\n风险计算")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)
        
        header_layout.addWidget(self.module2_3)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 开始计算按钮
        self.calculate_btn = QPushButton("开始计算")
        self.calculate_btn.setFixedHeight(40)  # 从45缩小到40
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
        self.download_result_btn.setFixedHeight(32)  # 从35缩小到32
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
        
        parent_layout.addWidget(module2_3_container)
    
    def create_result_area(self, parent_layout):
        """创建结果显示区域"""
        result_container = QFrame()
        result_container.setMinimumHeight(120)  # 调整为120，不要太高
        result_container.setMaximumHeight(180)  # 添加最大高度限制
        result_container.setStyleSheet("""
            QFrame {
                border: none;
                background-color: transparent;
            }
        """)

        layout = QVBoxLayout(result_container)
        layout.setContentsMargins(0, 10, 0, 10)  # 从15减小到10
        layout.setSpacing(8)  # 从10减小到8

        # 结果标题
        result_title = QLabel("计算状态")
        result_title.setFixedHeight(25)  # 从30减小到25
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
        self.result_display.setMinimumHeight(70)  # 调整为70
        self.result_display.setMaximumHeight(130)  # 添加最大高度限制
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
        self.result_display.setPlainText("等待选择毒性终点并提交...")
        layout.addWidget(self.result_display)
        
        parent_layout.addWidget(result_container)
    
    def create_bottom_navigation(self, parent_layout):
        """创建底部导航"""
        nav_layout = QHBoxLayout()
        
        # 返回按钮
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
        
        # 跳转到风险溯源按钮
        next_btn = QPushButton("下一模块 风险溯源 >>>")
        next_btn.setFixedSize(200, 40)
        next_btn.setStyleSheet("""
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
        next_btn.clicked.connect(self.check_and_switch_module)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        
        parent_layout.addLayout(nav_layout)
    
    # 功能方法
    def import_concentration_data(self):
        """导入浓度数据（从模块1-3结果）"""
        # 尝试查找最近的模块1-3结果文件
        exposure_results_path = os.path.join(self.media_path, "results", "exposure_results")
        
        if not os.path.exists(exposure_results_path):
            QMessageBox.warning(self, "警告", "未找到模块1-3的结果目录！\n请先完成暴露分析模块的计算。")
            return
        
        # 获取目录下的所有xlsx文件
        excel_files = [f for f in os.listdir(exposure_results_path) if f.endswith('.xlsx')]
        
        if not excel_files:
            QMessageBox.warning(self, "警告", "未找到模块1-3的结果文件！\n请先完成暴露分析模块的计算。")
            return
        
        # 使用最新的文件
        excel_files.sort(reverse=True)
        latest_file = os.path.join(exposure_results_path, excel_files[0])
        
        self.concentration_file_path = latest_file
        self.result_display.append(f"\n✓ 已导入浓度数据：{excel_files[0]}")
        
        # 激活模块2-3
        self.activate_module_2_3()
        
        QMessageBox.information(self, "导入成功", f"已导入浓度数据：\n{excel_files[0]}")
    
    def upload_concentration_data(self):
        """上传浓度数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择浓度数据文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.concentration_file_path = file_path
            self.result_display.append(f"\n✓ 已上传浓度数据：{os.path.basename(file_path)}")
            
            # 激活模块2-3
            self.activate_module_2_3()
            
            QMessageBox.information(self, "上传成功", f"浓度数据上传成功！\n文件：{os.path.basename(file_path)}")
    
    def activate_module_2_3(self):
        """激活模块2-3"""
        self.module2_3.setStyleSheet("QLabel { color: #00f2a0; font-size: 20px; }")
        self.calculate_btn.setEnabled(True)
        self.result_display.append("模块2-3已解锁，可以开始计算")
    
    def download_template_2_2(self):
        """下载模块2-2数据模板"""
        template_source = os.path.join(self.templates_path, "浓度数据模板.xlsx")
        
        if not os.path.exists(template_source):
            QMessageBox.warning(self, "提示", f"模板文件不存在，请检查目录：\n{template_source}")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存浓度数据模板", "浓度数据模板.xlsx", "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(template_source, save_path)
                QMessageBox.information(self, "模板下载", f"模板已保存至：\n{save_path}")
                self.result_display.append(f"✓ 模板2-2已下载：{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模板下载失败：{str(e)}")
    
    def start_calculation(self):
        """开始风险计算"""
        if not self.concentration_file_path:
            QMessageBox.warning(self, "警告", "请先导入或上传浓度数据！")
            return
        
        if not self.selected_endpoints:
            QMessageBox.warning(self, "警告", "请先选择毒性终点！")
            return
        
        self.is_calculating = True
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.setText("计算中...")
        
        self.result_display.clear()
        self.result_display.append("开始执行风险表征计算...")
        self.result_display.append(f"使用浓度数据：{os.path.basename(self.concentration_file_path)}")
        self.result_display.append(f"选择的毒性终点：{', '.join(self.selected_endpoints)}")
        self.result_display.append("正在处理...")
        
        # 强制刷新界面
        QApplication.processEvents()
        
        try:
            # 生成输出文件路径（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"风险表征结果_{timestamp}.xlsx"
            output_file_path = os.path.join(self.results_path, result_filename)
            
            # 调用风险模型函数
            calculate_risk(
                concentration_file=self.concentration_file_path,
                toxicity_endpoints=self.selected_endpoints,
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
            
            QMessageBox.information(self, "计算完成", "风险表征计算完成！\n点击'下载结果'保存Excel文件。")
            
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
    
    def check_and_switch_module(self):
        """检查并切换模块"""
        if self.is_calculating:
            # 显示确认对话框
            reply = QMessageBox.question(
                self, "确认跳转",
                "本模块任务尚未完成，是否确认跳转？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.switch_to_risk_tracing.emit()
        else:
            self.switch_to_risk_tracing.emit()


# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = RiskAssessmentPage()
    window.resize(1400, 900)
    window.show()
    
    sys.exit(app.exec_())

