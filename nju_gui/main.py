# main.py - 主程序入口文件（简化开发版本）
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget,QDesktopWidget
from main_page import MainPage
from login_page import LoginPage
from main_system_page import MainSystemPage
from exposure_analysis_page import ExposureAnalysisPage
from risk_assessment_page import RiskAssessmentPage
from risk_tracing_page import RiskTracingPage

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("园区高风险新污染物智慧识别系统")
        # 增大窗口尺寸以适应更大的内容
        self.resize( 1400, 900)
        
        # 创建页面堆栈
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建各个页面
        self.main_page = MainPage()
        self.login_page = LoginPage()
        self.system_page = MainSystemPage()  # 新增主功能页面
        self.exposure_page = ExposureAnalysisPage()  # 新增暴露分析页面
        self.risk_assessment_page = RiskAssessmentPage()  # 新增风险表征页面
        self.risk_tracing_page = RiskTracingPage()  # 新增风险溯源页面
        
        # 添加页面到堆栈
        self.stacked_widget.addWidget(self.main_page)    # 索引 0：启动页面
        self.stacked_widget.addWidget(self.login_page)   # 索引 1：登录页面
        self.stacked_widget.addWidget(self.system_page)  # 索引 2：主功能页面
        self.stacked_widget.addWidget(self.exposure_page)  # 索引 3：暴露分析页面
        self.stacked_widget.addWidget(self.risk_assessment_page)  # 索引 4：风险表征页面
        self.stacked_widget.addWidget(self.risk_tracing_page)  # 索引 5：风险溯源页面

        # 连接暴露分析页面信号
        self.exposure_page.back_to_main.connect(self.show_system_page)
        self.exposure_page.switch_to_risk_assessment.connect(self.show_risk_assessment_page)
        
        # 连接风险表征页面信号
        self.risk_assessment_page.back_to_main.connect(self.show_system_page)
        self.risk_assessment_page.switch_to_risk_tracing.connect(self.show_risk_tracing_page)
        
        # 连接风险溯源页面信号
        self.risk_tracing_page.back_to_main.connect(self.show_system_page)
        self.risk_tracing_page.back_to_risk_assessment.connect(self.show_risk_assessment_page)

        
        # 连接信号
        # 主页面信号：点击"开始使用"
        self.main_page.switch_to_login.connect(self.show_login_page)
        
        # 登录页面信号
        self.login_page.switch_to_main.connect(self.show_main_page)     # 点击"返回"
        self.login_page.login_success.connect(self.show_system_page)    # 登录成功
        
        # 主功能页面信号
        self.system_page.logout_signal.connect(self.show_main_page)     # 点击"退出登录"
        self.system_page.module_selected.connect(self.handle_module_selection)  # 点击模块卡片
        
        # 显示主页面
        self.stacked_widget.setCurrentWidget(self.main_page)

        # 窗口居中显示 - 添加这行
        self.center_window()

    def center_window(self):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        
        # 获取窗口尺寸
        window = self.geometry()
        
        # 计算居中位置
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        
        # 设置窗口位置
        self.move(x, y)
    
    def show_main_page(self):
        """显示主页面"""
        self.stacked_widget.setCurrentWidget(self.main_page)
    
    def show_login_page(self):
        """显示登录页面"""
        # 清空登录页面的输入框
        self.login_page.username_input.clear()
        self.login_page.password_input.clear()
        self.stacked_widget.setCurrentWidget(self.login_page)

    def show_system_page(self):
        """显示主功能页面"""
        self.stacked_widget.setCurrentWidget(self.system_page)
    
    def handle_module_selection(self, module_name):
        """处理模块选择"""
        print(f"用户选择了模块: {module_name}")
        
        # 根据不同的模块跳转到不同的子页面
        if module_name == "暴露分析":
            self.show_exposure_page()
        elif module_name == "风险表征":
            self.show_risk_assessment_page()
        elif module_name == "风险溯源":
            self.show_risk_tracing_page()
    
    def show_exposure_page(self):
        """显示暴露分析页面"""
        self.stacked_widget.setCurrentWidget(self.exposure_page)
    
    def show_risk_assessment_page(self):
        """显示风险表征页面"""
        self.stacked_widget.setCurrentWidget(self.risk_assessment_page)
    
    def show_risk_tracing_page(self):
        """显示风险溯源页面"""
        self.stacked_widget.setCurrentWidget(self.risk_tracing_page)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()