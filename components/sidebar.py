"""
侧边栏组件 - 使用 QSS 主题
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SidebarButton(QPushButton):
    """侧边栏按钮 - 使用 QSS 主题"""

    def __init__(self, text, icon_text, theme_manager=None):
        super().__init__()
        self.text = text
        self.icon_text = icon_text
        self.theme_manager = theme_manager
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        self.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.setObjectName("sidebarButton")

        # 设置按钮文本为图标+文字（文字按4字宽度居中对齐）
        padded_text = self._pad_text_to_4_chars(text)
        self.setText(f"{icon_text}  {padded_text}")

    def _pad_text_to_4_chars(self, text):
        """将文字填充到4个字宽度（8个字符），不足的在中间加空格"""
        text_length = len(text)
        if text_length >= 4:
            return text
        elif text_length == 3:
            # 3个字：字 字 字（字与字之间各加1个空格，共8字符）
            return f"{text[0]} {text[1]} {text[2]}"
        elif text_length == 2:
            # 2个字：字    字（中间加4个空格，共8字符）
            return f"{text[0]}    {text[1]}"
        else:
            # 1个字：  字    （两边各加3个空格，共8字符）
            return f"   {text}   "


class Sidebar(QFrame):
    """侧边栏 - 使用 QSS 主题"""

    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.buttons = []
        self.setup_ui()
        # 监听主题变化
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        self.setFixedWidth(200)
        self.setObjectName("sidebarFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        # Logo/标题区域
        logo_label = QLabel("应用菜单")
        logo_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        layout.addSpacing(20)

        # 菜单按钮
        self.home_btn = SidebarButton("首页", "🏠", self.theme_manager)
        self.dashboard_btn = SidebarButton("仪表盘", "📊", self.theme_manager)
        self.projects_btn = SidebarButton("项目", "📁", self.theme_manager)
        self.bidding_btn = SidebarButton("投标", "📋", self.theme_manager)
        self.messages_btn = SidebarButton("消息", "💬", self.theme_manager)

        self.buttons.extend([self.home_btn, self.dashboard_btn, self.projects_btn, self.bidding_btn, self.messages_btn])

        for btn in self.buttons:
            layout.addWidget(btn)

        layout.addStretch()

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        self.separator = separator
        layout.addWidget(separator)

        layout.addSpacing(10)

        # 设置按钮（在底部）
        self.settings_btn = SidebarButton("设置", "⚙️", self.theme_manager)
        layout.addWidget(self.settings_btn)

    def on_theme_changed(self, theme):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        pass
