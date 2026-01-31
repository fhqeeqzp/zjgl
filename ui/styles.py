"""
样式管理模块
集中管理所有UI组件的样式表
"""


class StyleSheetManager:
    """样式表管理器"""

    @staticmethod
    def get_titlebar_style(theme):
        """标题栏样式"""
        return f"""
            TitleBar {{
                background-color: {theme['sidebar_bg']};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border: none;
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
                color: {theme['text_primary']};
            }}
        """

    @staticmethod
    def get_close_btn_style(theme):
        """关闭按钮样式"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #f38ba8;
                color: #ffffff;
            }}
        """

    @staticmethod
    def get_sidebar_style(theme):
        """侧边栏样式"""
        return f"""
            Sidebar {{
                background-color: {theme['sidebar_bg']};
                border: none;
                border-radius: 0px;
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_sidebar_btn_style(theme):
        """侧边栏按钮样式"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                border-radius: 8px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['button_bg']};
                color: {theme['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {theme['accent']};
                color: #ffffff;
            }}
        """

    @staticmethod
    def get_main_window_style(theme):
        """主窗口样式"""
        return f"""
            QFrame {{
                background-color: {theme['window_bg']};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}
        """

    @staticmethod
    def get_homepage_style(theme):
        """首页样式"""
        return f"""
            HomePage {{
                background-color: {theme['content_bg']};
                border: none;
                border-radius: 0px;
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_card_style(theme):
        """卡片样式"""
        return f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border-radius: 0px;
                border: none;
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_settings_page_style(theme):
        """设置页面样式"""
        return f"""
            SettingsPage {{
                background-color: {theme['content_bg']};
                border: none;
                border-radius: 0px;
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_settings_card_style(theme):
        """设置页面卡片样式"""
        return f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border-radius: 0px;
                border: none;
            }}
        """

    @staticmethod
    def get_theme_btn_style(theme):
        """主题切换按钮样式"""
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text_primary']};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:checked {{
                background-color: {theme['accent']};
                color: #ffffff;
            }}
        """

    @staticmethod
    def get_placeholder_page_style(theme):
        """占位页面样式"""
        return f"""
            PlaceholderPage {{
                background-color: {theme['content_bg']};
                border: none;
                border-radius: 0px;
            }}
        """

    @staticmethod
    def get_statusbar_style(theme):
        """状态栏样式"""
        return f"""
            StatusBar {{
                background-color: {theme['sidebar_bg']};
                border: none;
                border-radius: 0px;
            }}
            QLabel {{
                color: {theme['text_secondary']};
                background: transparent;
                border: none;
            }}
        """
