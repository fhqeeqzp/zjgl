"""
标题栏组件 - 使用 QSS 主题
"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from login.ui.dialogs import ChangePasswordDialog


class TitleBar(QFrame):
    """自定义标题栏 - 使用 QSS 主题"""

    def __init__(self, parent=None, theme_manager=None, db_config=None, db_manager=None, username=""):
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = theme_manager
        self.db_config = db_config
        self.db_manager = db_manager
        self.username = username
        self.drag_pos = None

        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        self.setFixedHeight(45)
        self.setObjectName("titleBarFrame")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题 - 从数据库读取或使用默认值
        app_name = self.get_app_name_from_db()
        self.title_label = QLabel(app_name)
        self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(self.title_label)

        layout.addStretch()

        # 用户信息区域（在最小化按钮前显示）
        self.user_widget = QFrame()
        user_layout = QHBoxLayout(self.user_widget)
        user_layout.setContentsMargins(0, 0, 10, 0)
        user_layout.setSpacing(5)

        # 用户图标
        self.user_icon = QLabel("👤")
        self.user_icon.setFont(QFont("Segoe UI Emoji", 12))
        user_layout.addWidget(self.user_icon)

        # 用户名（可点击）
        self.user_name_label = QLabel("未登录")
        self.user_name_label.setFont(QFont("Microsoft YaHei", 10))
        self.user_name_label.setCursor(Qt.PointingHandCursor)  # 鼠标手型
        self.user_name_label.mousePressEvent = self.on_user_click  # 点击事件
        user_layout.addWidget(self.user_name_label)

        layout.addWidget(self.user_widget)

        # 窗口控制按钮 - 使用QSS样式，45x45填满标题栏高度
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("minimizeButton")
        self.min_btn.setProperty("class", "titlebar-button")
        self.min_btn.setFixedSize(45, 45)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.clicked.connect(self.parent.showMinimized)

        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("maximizeButton")
        self.max_btn.setProperty("class", "titlebar-button")
        self.max_btn.setFixedSize(45, 45)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.clicked.connect(self.toggle_maximize)

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setProperty("class", "titlebar-button")
        self.close_btn.setFixedSize(45, 45)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def get_app_name_from_db(self):
        """从数据库获取应用名称"""
        if self.db_config:
            try:
                from login.data.db_manager import DatabaseManager
                db_manager = DatabaseManager(self.db_config.get_config())
                result = db_manager.execute_query(
                    "SELECT config_value FROM system_config WHERE config_key = 'app_name'"
                )
                if result and len(result) > 0:
                    return result[0]['config_value']
            except Exception:
                pass
        return "主题切换演示程序"

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        # 这里只需要处理特殊的动态样式
        pass

    def set_user_name(self, username):
        """设置显示的用户名"""
        self.username = username
        self.user_name_label.setText(username)

    def set_db_manager(self, db_manager):
        """设置数据库管理器"""
        self.db_manager = db_manager

    def on_user_click(self, event):
        """点击用户名 - 弹出修改密码对话框"""
        if self.username and self.username != "未登录":
            dialog = ChangePasswordDialog(
                parent=self.parent,
                username=self.username,
                db_manager=self.db_manager,
                theme_manager=self.theme_manager
            )
            dialog.exec_()

    def toggle_maximize(self):
        """切换最大化/还原"""
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            if self.parent.isMaximized():
                self.parent.showNormal()
                self.max_btn.setText("□")
            self.parent.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
