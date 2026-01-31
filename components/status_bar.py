"""
状态栏组件
"""
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont

from ui import StyleSheetManager


class StatusBar(QFrame):
    """状态栏"""

    def __init__(self, theme_manager=None, db_config=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.db_config = db_config
        self.setup_ui()
        self.theme_manager.add_observer(self.apply_theme)

    def setup_ui(self):
        self.setFixedHeight(28)

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
        layout.addWidget(self.db_status_label)

        layout.addStretch()

        # 右侧信息
        self.info_label = QLabel("PyQt5 主题演示")
        self.info_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.info_label)

        self.apply_theme(self.theme_manager.get_theme())
        self.update_db_status()

    def apply_theme(self, theme):
        """应用主题"""
        self.setStyleSheet(StyleSheetManager.get_statusbar_style(theme))

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
                self.db_status_label.setStyleSheet("color: #4caf50;")
            else:
                self.db_status_label.setText("● 数据库: 未连接")
                self.db_status_label.setStyleSheet("color: #999999;")
        else:
            self.db_status_label.setText("● 数据库: 未配置")
            self.db_status_label.setStyleSheet("color: #999999;")
