"""
主题切换演示程序 - 主入口
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from themes import ThemeManager
from ui import StyleSheetManager
from components import TitleBar, Sidebar, StatusBar, HomePage, SettingsPage, PlaceholderPage
from login.ui import LoginWindow
from login.data.db_config import DatabaseConfig


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()

        # 创建主题管理器（默认深色主题）
        self.theme_manager = ThemeManager()
        
        # 加载数据库配置
        self.db_config = DatabaseConfig()

        self.setup_ui()
        self.apply_window_theme(self.theme_manager.get_theme())

        # 监听主题变化
        self.theme_manager.add_observer(self.apply_window_theme)

    def setup_ui(self):
        # 无边框窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口大小
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        # 中央部件
        self.central_widget = QFrame()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        self.title_bar = TitleBar(self, self.theme_manager, self.db_config)
        main_layout.addWidget(self.title_bar)

        # 内容区域（标题栏和状态栏之间）
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar(self, self.theme_manager)
        content_layout.addWidget(self.sidebar)

        # 页面堆叠
        self.stack = QStackedWidget()

        # 创建各个页面
        self.home_page = HomePage(self.theme_manager)
        self.dashboard_page = PlaceholderPage("仪表盘", self.theme_manager)
        self.projects_page = PlaceholderPage("项目", self.theme_manager)
        self.messages_page = PlaceholderPage("消息", self.theme_manager)
        self.settings_page = SettingsPage(self.theme_manager)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.projects_page)
        self.stack.addWidget(self.messages_page)
        self.stack.addWidget(self.settings_page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

        # 状态栏
        self.status_bar = StatusBar(self.theme_manager, self.db_config)
        main_layout.addWidget(self.status_bar)

        # 连接按钮信号
        self.sidebar.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.sidebar.dashboard_btn.clicked.connect(lambda: self.switch_page(1))
        self.sidebar.projects_btn.clicked.connect(lambda: self.switch_page(2))
        self.sidebar.messages_btn.clicked.connect(lambda: self.switch_page(3))
        self.sidebar.settings_btn.clicked.connect(lambda: self.switch_page(4))

        # 默认选中首页
        self.sidebar.home_btn.setChecked(True)

        # 添加阴影效果
        self.add_shadow_effect()

    def switch_page(self, index):
        """切换页面"""
        self.stack.setCurrentIndex(index)

        # 更新按钮选中状态
        for i, btn in enumerate(self.sidebar.buttons):
            btn.setChecked(i == index)
        self.sidebar.settings_btn.setChecked(index == 4)

    def apply_window_theme(self, theme):
        """应用窗口主题"""
        self.central_widget.setStyleSheet(StyleSheetManager.get_main_window_style(theme))

    def add_shadow_effect(self):
        """添加窗口阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(shadow)

    def showEvent(self, event):
        """窗口显示时居中"""
        super().showEvent(event)
        self.center_window()

    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    # 先显示登录窗口
    login_window = LoginWindow()
    login_window.show()

    # 等待登录结果
    def on_login_success():
        """登录成功回调"""
        # 获取登录用户名
        username = login_window.auth_manager.get_current_user() or "用户"
        login_window.close()
        main_window = MainWindow()
        # 设置标题栏显示用户名
        main_window.title_bar.set_user_name(username)
        main_window.show()

    # 修改登录窗口的登录成功处理
    login_window.on_login_success = on_login_success

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
