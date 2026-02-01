"""
页面组件 - 使用 QSS 主题
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HomePage(QFrame):
    """首页 - 使用 QSS 主题"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("欢迎使用")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("这是一个支持深色/浅色主题切换的演示程序")
        subtitle.setFont(QFont("Microsoft YaHei", 12))
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # 卡片容器
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # 创建卡片
        self.card1 = self.create_card("用户统计", "1,234", "👥")
        self.card2 = self.create_card("项目数量", "56", "📂")
        self.card3 = self.create_card("消息通知", "12", "🔔")

        cards_layout.addWidget(self.card1)
        cards_layout.addWidget(self.card2)
        cards_layout.addWidget(self.card3)

        layout.addLayout(cards_layout)
        layout.addStretch()

    def create_card(self, title, value, icon):
        """创建信息卡片"""
        card = QFrame()
        card.setFixedSize(180, 120)
        card.setObjectName("cardFrame")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 11))
        title_label.setObjectName("subtitleLabel")
        layout.addWidget(title_label)

        return card

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        pass


class SettingsPage(QFrame):
    """设置页面 - 使用 QSS 主题"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        layout.addSpacing(20)

        # 主题设置区域
        theme_frame = QFrame()
        theme_frame.setFixedHeight(150)
        theme_frame.setObjectName("cardFrame")
        self.theme_frame = theme_frame

        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(25, 25, 25, 25)

        theme_title = QLabel("🎨 外观设置")
        theme_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        theme_layout.addWidget(theme_title)

        theme_desc = QLabel("选择您喜欢的主题样式")
        theme_desc.setFont(QFont("Microsoft YaHei", 11))
        theme_desc.setObjectName("subtitleLabel")
        theme_layout.addWidget(theme_desc)

        theme_layout.addSpacing(15)

        # 主题切换按钮
        btn_layout = QHBoxLayout()

        self.dark_btn = QPushButton("🌙 深色主题")
        self.dark_btn.setCheckable(True)
        self.dark_btn.setCursor(Qt.PointingHandCursor)
        self.dark_btn.setFixedSize(120, 40)
        self.dark_btn.clicked.connect(lambda: self.switch_theme('dark'))

        self.light_btn = QPushButton("☀️ 浅色主题")
        self.light_btn.setCheckable(True)
        self.light_btn.setCursor(Qt.PointingHandCursor)
        self.light_btn.setFixedSize(120, 40)
        self.light_btn.clicked.connect(lambda: self.switch_theme('light'))

        btn_layout.addWidget(self.dark_btn)
        btn_layout.addWidget(self.light_btn)
        btn_layout.addStretch()

        theme_layout.addLayout(btn_layout)
        layout.addWidget(theme_frame)

        # 当前主题显示
        self.current_theme_label = QLabel(f"当前主题: {self.theme_manager.get_theme()['name'] if self.theme_manager else '深色主题'}")
        self.current_theme_label.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(self.current_theme_label)

        layout.addStretch()

        # 初始化按钮状态
        self.update_theme_buttons()

    def switch_theme(self, theme_name):
        """切换主题"""
        if self.theme_manager:
            self.theme_manager.switch_theme(theme_name)
            self.update_theme_buttons()

    def update_theme_buttons(self):
        """更新主题按钮状态"""
        if self.theme_manager:
            current = self.theme_manager.get_current_theme_name()
            self.dark_btn.setChecked(current == 'dark')
            self.light_btn.setChecked(current == 'light')
            self.current_theme_label.setText(f"当前主题: {self.theme_manager.get_theme()['name']}")

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        self.update_theme_buttons()


class PlaceholderPage(QFrame):
    """占位页面 - 使用 QSS 主题"""

    def __init__(self, title_text, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.title_text = title_text
        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(f"{self.title_text}\n页面内容")
        label.setFont(QFont("Microsoft YaHei", 18))
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("subtitleLabel")
        self.label = label
        layout.addWidget(label)

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        pass
