"""
页面组件
"""
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui import StyleSheetManager


class HomePage(QFrame):
    """首页"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        self.theme_manager.add_observer(self.apply_theme)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("欢迎使用")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("这是一个支持深色/浅色主题切换的演示程序")
        subtitle.setFont(QFont("Microsoft YaHei", 12))
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

        self.apply_theme(self.theme_manager.get_theme())

    def create_card(self, title, value, icon):
        """创建信息卡片"""
        card = QFrame()
        card.setFixedSize(180, 120)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 11))
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        self.theme_manager.add_observer(lambda t, c=card: self.apply_card_theme(c, t))

        return card

    def apply_card_theme(self, card, theme):
        """应用卡片主题"""
        card.setStyleSheet(StyleSheetManager.get_card_style(theme))

    def apply_theme(self, theme):
        """应用主题"""
        self.setStyleSheet(StyleSheetManager.get_homepage_style(theme))


class SettingsPage(QFrame):
    """设置页面"""

    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        self.theme_manager.add_observer(self.apply_theme)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        layout.addWidget(title)

        layout.addSpacing(20)

        # 主题设置区域
        theme_frame = QFrame()
        theme_frame.setFixedHeight(150)
        self.theme_frame = theme_frame

        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(25, 25, 25, 25)

        theme_title = QLabel("🎨 外观设置")
        theme_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        theme_layout.addWidget(theme_title)

        theme_desc = QLabel("选择您喜欢的主题样式")
        theme_desc.setFont(QFont("Microsoft YaHei", 11))
        self.theme_desc = theme_desc
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
        self.current_theme_label = QLabel(f"当前主题: {self.theme_manager.get_theme()['name']}")
        self.current_theme_label.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(self.current_theme_label)

        layout.addStretch()

        self.apply_theme(self.theme_manager.get_theme())

    def switch_theme(self, theme_name):
        """切换主题"""
        self.theme_manager.switch_theme(theme_name)
        self.update_theme_buttons()

    def update_theme_buttons(self):
        """更新主题按钮状态"""
        current = self.theme_manager.get_current_theme_name()
        self.dark_btn.setChecked(current == 'dark')
        self.light_btn.setChecked(current == 'light')
        self.current_theme_label.setText(f"当前主题: {self.theme_manager.get_theme()['name']}")

    def apply_theme(self, theme):
        """应用主题"""
        self.setStyleSheet(StyleSheetManager.get_settings_page_style(theme))
        self.theme_frame.setStyleSheet(StyleSheetManager.get_settings_card_style(theme))
        self.theme_desc.setStyleSheet(f"color: {theme['text_secondary']}; border: none;")

        btn_style = StyleSheetManager.get_theme_btn_style(theme)
        self.dark_btn.setStyleSheet(btn_style)
        self.light_btn.setStyleSheet(btn_style)

        self.update_theme_buttons()


class PlaceholderPage(QFrame):
    """占位页面"""

    def __init__(self, title_text, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.title_text = title_text
        self.setup_ui()
        self.theme_manager.add_observer(self.apply_theme)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(f"{self.title_text}\n页面内容")
        label.setFont(QFont("Microsoft YaHei", 18))
        label.setAlignment(Qt.AlignCenter)
        self.label = label
        layout.addWidget(label)

        self.apply_theme(self.theme_manager.get_theme())

    def apply_theme(self, theme):
        """应用主题"""
        self.setStyleSheet(StyleSheetManager.get_placeholder_page_style(theme))
        self.label.setStyleSheet(f"color: {theme['text_secondary']}; border: none;")
