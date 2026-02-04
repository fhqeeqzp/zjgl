"""
主题切换演示程序 - 主入口
使用 QSS 文件管理主题
"""
import sys
import os

# 抑制Qt警告信息
os.environ['QT_LOGGING_RULES'] = '*.warning=false;qt.svg.warning=false;qt.png.warning=false'

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QFrame,
    QGraphicsDropShadowEffect,
    QDialog
)

from ui.message_dialog import MessageDialog
from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QColor, QFont

from themes import ThemeManager
from components import TitleBar, Sidebar, StatusBar, HomePage, SettingsPage, PlaceholderPage
from login.ui import LoginWindow
from login.data.db_config import DatabaseConfig
from XMGL.ui import ProjectsPage
from TBGL.ui import BiddingPage


class MainWindow(QMainWindow):
    """主窗口 - 使用 QSS 主题"""

    def __init__(self, theme_manager=None):
        super().__init__()

        # 使用传入的主题管理器或创建新的
        self.theme_manager = theme_manager if theme_manager else ThemeManager()
        
        # 加载数据库配置
        self.db_config = DatabaseConfig()

        self.setup_ui()
        # 不再调用 apply_window_theme，使用全局 QSS

        # 监听主题变化
        self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        # 无边框窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口大小
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        # 中央部件
        self.central_widget = QFrame()
        self.central_widget.setObjectName("centralWidget")
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
        # 从login.data.db_manager导入DatabaseManager获取数据库连接
        from login.data.db_manager import DatabaseManager
        from XMGL.logic.project_manager import ProjectManager
        db_manager = DatabaseManager(self.db_config.get_config()) if self.db_config.get_config().get('is_configured') else None
        self.project_manager = ProjectManager(db_manager)
        self.projects_page = ProjectsPage(self.theme_manager, db_manager)
        self.bidding_page = BiddingPage(self.theme_manager, db_manager, self.project_manager)
        self.messages_page = PlaceholderPage("消息", self.theme_manager)
        self.settings_page = SettingsPage(self.theme_manager)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.projects_page)
        self.stack.addWidget(self.bidding_page)
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
        self.sidebar.bidding_btn.clicked.connect(lambda: self.switch_page(3))
        self.sidebar.messages_btn.clicked.connect(lambda: self.switch_page(4))
        self.sidebar.settings_btn.clicked.connect(lambda: self.switch_page(5))

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
        self.sidebar.settings_btn.setChecked(index == 5)

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载，这里处理特殊逻辑"""
        # 如果需要处理特殊的主题变化逻辑，可以在这里添加
        pass

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

    def set_user_name(self, username):
        """设置显示的用户名"""
        self.title_bar.set_user_name(username)

    def set_db_manager(self, db_manager):
        """设置数据库管理器"""
        self.title_bar.set_db_manager(db_manager)


def patch_dialogs():
    """补丁：让所有对话框默认无边框"""
    from PySide6.QtWidgets import QDialog

    # 保存原始的QDialog构造函数
    QDialog._original_init = QDialog.__init__

    def _patched_dialog_init(self, parent=None, flags=Qt.WindowFlags()):
        # 调用原始构造函数，添加无边框标志
        QDialog._original_init(self, parent, flags | Qt.FramelessWindowHint)

    # 替换构造函数
    QDialog.__init__ = _patched_dialog_init

    # 处理QProgressDialog
    from PySide6.QtWidgets import QProgressDialog
    QProgressDialog._original_init = QProgressDialog.__init__

    def _patched_progress_init(self, labelText="", cancelButtonText="", minimum=0, maximum=100, parent=None, flags=Qt.WindowFlags()):
        QProgressDialog._original_init(self, labelText, cancelButtonText, minimum, maximum, parent, flags | Qt.FramelessWindowHint)
        # 设置固定大小
        self.setFixedSize(400, 120)
        # 禁用调整大小
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint, True)

    QProgressDialog.__init__ = _patched_progress_init


def main():
    # 应用对话框无边框补丁（在创建任何对话框之前）
    patch_dialogs()

    # 创建应用程序
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    # 创建主题管理器并设置应用程序（自动加载 QSS）
    theme_manager = ThemeManager()
    theme_manager.set_application(app)

    # 创建登录窗口，传入主题管理器
    login_window = LoginWindow(theme_manager)
    login_window.show()

    # 等待登录结果
    def on_login_success():
        """登录成功回调"""
        # 获取登录用户名和数据库管理器
        username = login_window.auth_manager.get_current_user() or "用户"
        db_manager = login_window.auth_manager.db_manager
        login_window.close()
        
        # 创建主窗口，传入相同的主题管理器
        main_window = MainWindow(theme_manager)
        # 设置标题栏显示用户名和数据库管理器
        main_window.set_user_name(username)
        main_window.set_db_manager(db_manager)
        # 满屏显示
        main_window.showMaximized()

    # 修改登录窗口的登录成功处理
    login_window.on_login_success = on_login_success

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
