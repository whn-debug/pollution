# exposure_analysis_page.py - 风险暴露分析页面

import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QGridLayout, QSizePolicy, QMessageBox,
                             QFileDialog, QTextEdit, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from utils import BackgroundWidget

# 导入随机森林模型
from random_forest_model import process_data

class ExposureAnalysisPage(BackgroundWidget):
    """风险暴露分析页面"""
    
    # 信号定义
    switch_to_risk_assessment = pyqtSignal()  # 跳转到风险表征
    back_to_main = pyqtSignal()  # 返回主页面
    
    def __init__(self):
        # 使用背景图片
        background_path = "D:\\nju_gui\\VCG211410114301.jpg"
        if not os.path.exists(background_path):
            background_path = ""
        super().__init__(background_path)
        
        # 状态变量
        self.excel1_1_path = None  # 校正数据文件路径
        self.excel1_2_path = None  # 样品数据文件路径
        self.result_excel_path = None  # 计算结果Excel文件路径
        self.is_calculating = False  # 是否正在计算
        
        # 文件路径配置
        self.media_path = "media"
        self.templates_path = os.path.join(self.media_path, "templates")
        self.results_path = os.path.join(self.media_path, "results", "exposure_results")
        
        # 确保目录存在
        os.makedirs(self.results_path, exist_ok=True)
        
        # 组件引用
        self.module1_1 = None
        self.module1_2 = None
        self.module1_3 = None
        self.result_display = None
        
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
            }
        """)
        
        # 南京大学Logo
        nju_logo = QLabel()
        logo_path = "D:\\nju_gui\\logo.png"
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
        
        # 模块1：暴露分析（当前活跃）
        module1_tab = QLabel("模块1 暴露分析")
        module1_tab.setFixedHeight(50)
        module1_tab.setAlignment(Qt.AlignCenter)
        module1_tab.setStyleSheet("""
            QLabel {
                background-color: white;
                color: #333;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-bottom: none;
                padding: 10px 30px;
            }
        """)
        
        # 模块2：风险表征
        module2_tab = QLabel("模块2 风险表征")
        module2_tab.setFixedHeight(50)
        module2_tab.setAlignment(Qt.AlignCenter)
        module2_tab.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.7);
                color: #666;
                font-size: 18px;
                border: 2px solid #ddd;
                border-bottom: none;
                padding: 10px 30px;
                border-left: none;
            }
        """)
        
        # 模块3：风险溯源
        module3_tab = QLabel("模块3 风险溯源")
        module3_tab.setFixedHeight(50)
        module3_tab.setAlignment(Qt.AlignCenter)
        module3_tab.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.7);
                color: #666;
                font-size: 18px;
                border: 2px solid #ddd;
                border-bottom: none;
                padding: 10px 30px;
                border-left: none;
            }
        """)
        
        tabs_layout.addWidget(module1_tab)
        tabs_layout.addWidget(module2_tab)
        tabs_layout.addWidget(module3_tab)
        tabs_layout.addStretch()
        
        parent_layout.addLayout(tabs_layout)
    
    def create_main_content(self, parent_layout):
        """创建主要内容区域"""
        # 主容器
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid #ddd;
                border-top: none;
                padding: 20px;
            }
        """)
        
        main_content_layout = QVBoxLayout(main_container)
        main_content_layout.setSpacing(30)
        
        # 三个子模块
        modules_layout = QHBoxLayout()
        modules_layout.setSpacing(40)
        
        # 模块1-1：仪器校正
        self.create_module_1_1(modules_layout)
        
        # 模块1-2：实测物质筛查
        self.create_module_1_2(modules_layout)
        
        # 模块1-3：浓度预测
        self.create_module_1_3(modules_layout)
        
        main_content_layout.addLayout(modules_layout)
        
        # 结果显示区域
        self.create_result_area(main_content_layout)
        
        # 提示信息
        tip_label = QLabel("提示：模块1-1 ～ 1-3逐步解锁，指示灯显示绿色的模块为当前可操作模块；显示红色的模块当前不可操作模块。")
        tip_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(255, 235, 59, 0.3);
                border-radius: 5px;
            }
        """)
        tip_label.setWordWrap(True)
        main_content_layout.addWidget(tip_label)
        
        parent_layout.addWidget(main_container)
    
    def create_module_1_1(self, parent_layout):
        """创建模块1-1：仪器校正"""
        module1_1_container = QFrame()
        module1_1_container.setFixedWidth(280)
        module1_1_container.setStyleSheet("""
            QFrame {
                border: 2px dashed #bbb;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(module1_1_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module1_1 = QLabel("●")
        self.module1_1.setStyleSheet("QLabel { color: #27ae60; font-size: 20px; }")
        
        title_label = QLabel("模块1-1\n仪器校正")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        
        header_layout.addWidget(self.module1_1)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 上传按钮
        upload_btn_1_1 = QPushButton("上传校正实测数据")
        upload_btn_1_1.setFixedHeight(45)
        upload_btn_1_1.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        upload_btn_1_1.clicked.connect(self.upload_excel_1_1)
        layout.addWidget(upload_btn_1_1)
        
        # 下载模板按钮
        download_template_1_1 = QPushButton("下载数据模板")
        download_template_1_1.setFixedHeight(35)
        download_template_1_1.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        download_template_1_1.clicked.connect(self.download_template_1_1)
        layout.addWidget(download_template_1_1)
        
        parent_layout.addWidget(module1_1_container)
    
    def create_module_1_2(self, parent_layout):
        """创建模块1-2：实测物质筛查"""
        module1_2_container = QFrame()
        module1_2_container.setFixedWidth(280)
        module1_2_container.setStyleSheet("""
            QFrame {
                border: 2px dashed #bbb;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(module1_2_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module1_2 = QLabel("●")
        self.module1_2.setStyleSheet("QLabel { color: #e74c3c; font-size: 20px; }")
        
        title_label = QLabel("模块1-2\n实测物质筛查")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        
        header_layout.addWidget(self.module1_2)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 上传按钮
        self.upload_btn_1_2 = QPushButton("上传样品实测数据")
        self.upload_btn_1_2.setFixedHeight(45)
        self.upload_btn_1_2.setEnabled(False)  # 初始禁用
        self.upload_btn_1_2.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #7f8c8d;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:enabled {
                background-color: #3498db;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #2980b9;
            }
        """)
        self.upload_btn_1_2.clicked.connect(self.upload_excel_1_2)
        layout.addWidget(self.upload_btn_1_2)
        
        # 下载模板按钮
        download_template_1_2 = QPushButton("下载数据模板")
        download_template_1_2.setFixedHeight(35)
        download_template_1_2.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        download_template_1_2.clicked.connect(self.download_template_1_2)
        layout.addWidget(download_template_1_2)
        
        parent_layout.addWidget(module1_2_container)
    
    def create_module_1_3(self, parent_layout):
        """创建模块1-3：浓度预测"""
        module1_3_container = QFrame()
        module1_3_container.setFixedWidth(280)
        module1_3_container.setStyleSheet("""
            QFrame {
                border: 2px dashed #bbb;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(module1_3_container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # 标题和指示灯
        header_layout = QHBoxLayout()
        self.module1_3 = QLabel("●")
        self.module1_3.setStyleSheet("QLabel { color: #e74c3c; font-size: 20px; }")
        
        title_label = QLabel("模块1-3\n浓度预测")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
        """)
        
        header_layout.addWidget(self.module1_3)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 开始计算按钮
        self.calculate_btn = QPushButton("开始计算")
        self.calculate_btn.setFixedHeight(45)
        self.calculate_btn.setEnabled(False)  # 初始禁用
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #7f8c8d;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:enabled {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #229954;
            }
        """)
        self.calculate_btn.clicked.connect(self.start_calculation)
        layout.addWidget(self.calculate_btn)
        
        # 下载结果按钮
        self.download_result_btn = QPushButton("下载结果")
        self.download_result_btn.setFixedHeight(35)
        self.download_result_btn.setEnabled(False)  # 初始禁用
        self.download_result_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #7f8c8d;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:enabled {
                background-color: #f39c12;
                color: white;
            }
            QPushButton:enabled:hover {
                background-color: #e67e22;
            }
        """)
        self.download_result_btn.clicked.connect(self.download_result)
        layout.addWidget(self.download_result_btn)
        
        parent_layout.addWidget(module1_3_container)
    
    def create_result_area(self, parent_layout):
        """创建结果显示区域"""
        result_container = QFrame()
        result_container.setFixedHeight(150)
        result_container.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(result_container)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 结果标题
        result_title = QLabel("计算状态")
        result_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(result_title)
        
        # 结果显示文本框
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
                font-size: 12px;
            }
        """)
        self.result_display.setPlainText("等待上传数据并开始计算...")
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
                background-color: rgba(108, 117, 125, 0.8);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(108, 117, 125, 1.0);
            }
        """)
        back_btn.clicked.connect(self.back_to_main.emit)
        
        # 跳转到风险表征按钮
        next_btn = QPushButton("风险表征 >>>")
        next_btn.setFixedSize(150, 40)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 152, 219, 0.8);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 1.0);
            }
        """)
        next_btn.clicked.connect(self.check_and_switch_module)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        
        parent_layout.addLayout(nav_layout)
    
    # 功能方法
    def upload_excel_1_1(self):
        """上传校正实测数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择校正实测数据文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.excel1_1_path = file_path
            self.result_display.append(f"✓ 已上传校正数据：{os.path.basename(file_path)}")
            
            # 激活模块1-2
            self.module1_2.setStyleSheet("QLabel { color: #27ae60; font-size: 20px; }")
            self.upload_btn_1_2.setEnabled(True)
            
            QMessageBox.information(self, "上传成功", f"校正数据上传成功！\n文件：{os.path.basename(file_path)}")
    
    def upload_excel_1_2(self):
        """上传样品实测数据"""
        if not self.excel1_1_path:
            QMessageBox.warning(self, "警告", "请先上传校正实测数据！")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择样品实测数据文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            self.excel1_2_path = file_path
            self.result_display.append(f"✓ 已上传样品数据：{os.path.basename(file_path)}")
            
            # 激活模块1-3
            self.module1_3.setStyleSheet("QLabel { color: #27ae60; font-size: 20px; }")
            self.calculate_btn.setEnabled(True)
            
            QMessageBox.information(self, "上传成功", f"样品数据上传成功！\n文件：{os.path.basename(file_path)}")
    
    def download_template_1_1(self):
        """下载模块1-1数据模板"""
        template_source = os.path.join(self.templates_path, "校正重测数据模板.xlsx")
        
        if not os.path.exists(template_source):
            QMessageBox.warning(self, "提示", f"模板文件不存在，请检查目录：\n{template_source}")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存校正数据模板", "校正重测数据模板.xlsx", "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(template_source, save_path)
                QMessageBox.information(self, "模板下载", f"模板已保存至：\n{save_path}")
                self.result_display.append(f"✓ 模板1-1已下载：{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模板下载失败：{str(e)}")
    
    def download_template_1_2(self):
        """下载模块1-2数据模板"""
        template_source = os.path.join(self.templates_path, "样品实测模板.xlsx")
        
        if not os.path.exists(template_source):
            QMessageBox.warning(self, "提示", f"模板文件不存在，请检查目录：\n{template_source}")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存样品数据模板", "样品实测模板.xlsx", "Excel文件 (*.xlsx)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(template_source, save_path)
                QMessageBox.information(self, "模板下载", f"模板已保存至：\n{save_path}")
                self.result_display.append(f"✓ 模板1-2已下载：{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模板下载失败：{str(e)}")
    
    def start_calculation(self):
        """开始计算"""
        if not self.excel1_1_path or not self.excel1_2_path:
            QMessageBox.warning(self, "警告", "请先上传所需的数据文件！")
            return
        
        self.is_calculating = True
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.setText("计算中...")
        
        self.result_display.clear()
        self.result_display.append("开始执行随机森林模型计算...")
        self.result_display.append(f"使用校正数据：{os.path.basename(self.excel1_1_path)}")
        self.result_display.append(f"使用样品数据：{os.path.basename(self.excel1_2_path)}")
        self.result_display.append("正在处理...")
        
        # 强制刷新界面
        QApplication.processEvents()
        
        try:
            # 生成输出文件路径（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"浓度预测结果_{timestamp}.xlsx"
            output_file_path = os.path.join(self.results_path, result_filename)
            
            # 调用随机森林模型函数
            process_data(
                input_file1_path=self.excel1_1_path,
                input_file2_path=self.excel1_2_path,
                output_file_path=output_file_path
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
            self.result_display.append("计算完成！")
            self.result_display.append(f"结果文件：{result_filename}")
            self.result_display.append("点击'下载结果'保存Excel文件")
            
            # 启用下载按钮
            self.download_result_btn.setEnabled(True)
            
            QMessageBox.information(self, "计算完成", "随机森林模型计算完成！\n点击'下载结果'保存Excel文件。")
            
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
                self.switch_to_risk_assessment.emit()
        else:
            self.switch_to_risk_assessment.emit()

# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = ExposureAnalysisPage()
    window.resize(1400, 900)
    window.show()
    
    sys.exit(app.exec_())