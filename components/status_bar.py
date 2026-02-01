"""
状态栏组件 - 使用 QSS 主题
"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtGui import QFont


class StatusBar(QFrame):
    """状态栏 - 使用 QSS 主题"""

    def __init__(self, theme_manager=None, db_config=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.db_config = db_config
        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        self.setFixedHeight(28)
        self.setObjectName("statusBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(20)

        # 左侧状态信息
        self.status_label = QLabel("就绪")
        self.status_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.status_label)

        # 数据库连接状态
        self.db_status_label = QLabel("● 数据库: 未连接")
        self.db_status_label.setFont(QFont("Microsoft YaHei", 9))
        self.db_status_label.setObjectName("subtitleLabel")
        layout.addWidget(self.db_status_label)

        layout.addStretch()

        # 右侧信息
        self.info_label = QLabel("PyQt5 主题演示")
        self.info_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.info_label)

        self.update_db_status()

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        pass

    def set_status(self, text):
        """设置状态文本"""
        self.status_label.setText(text)

    def update_db_status(self):
        """更新数据库连接状态"""
        if self.db_config:
            config = self.db_config.get_config()
            is_configured = config.get('is_configured', False)
            
            if is_configured:
                self.db_status_label.setText("● 数据库: 已连接")
                self.db_status_label.setObjectName("successLabel")
            else:
                self.db_status_label.setText("● 数据库: 未连接")
                self.db_status_label.setObjectName("subtitleLabel")
        else:
            self.db_status_label.setText("● 数据库: 未配置")
            self.db_status_label.setObjectName("subtitleLabel")
