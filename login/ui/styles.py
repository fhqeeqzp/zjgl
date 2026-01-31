"""
登录窗口样式管理
"""


class LoginStyles:
    """登录窗口样式表管理器"""

    # 登录窗口主题色
    COLORS = {
        'primary': '#2196F3',
        'primary_hover': '#1976D2',
        'secondary': '#757575',
        'background': '#f5f5f5',
        'card_bg': '#ffffff',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'border': '#e0e0e0',
        'input_bg': '#fafafa',
        'error': '#f44336',
        'success': '#4caf50'
    }

    @classmethod
    def get_main_window_style(cls):
        """主窗口样式"""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['background']};
            }}
        """

    @classmethod
    def get_left_panel_style(cls):
        """左侧图片区域样式"""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['primary']};
                border: none;
            }}
        """

    @classmethod
    def get_right_panel_style(cls):
        """右侧表单区域样式"""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['card_bg']};
                border: none;
            }}
        """

    @classmethod
    def get_title_label_style(cls):
        """标题样式"""
        return f"""
            QLabel {{
                color: {cls.COLORS['text_primary']};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                padding: 1px;
            }}
        """

    @classmethod
    def get_subtitle_label_style(cls):
        """副标题样式"""
        return f"""
            QLabel {{
                color: {cls.COLORS['text_secondary']};
                font-size: 14px;
                background: transparent;
                padding: 1px;
            }}
        """

    @classmethod
    def get_input_style(cls):
        """输入框样式"""
        return f"""
            QLineEdit {{
                background-color: {cls.COLORS['input_bg']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 8px;
                padding: 1px 5px;
                font-size: 14px;
                color: {cls.COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {cls.COLORS['primary']};
            }}
            QLineEdit::placeholder {{
                color: {cls.COLORS['text_secondary']};
            }}
        """

    @classmethod
    def get_primary_button_style(cls):
        """主按钮样式（登录）"""
        return f"""
            QPushButton {{
                background-color: {cls.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 1px 5px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS['primary']};
            }}
        """

    @classmethod
    def get_secondary_button_style(cls):
        """次要按钮样式（注册）"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {cls.COLORS['primary']};
                border: 1px solid {cls.COLORS['primary']};
                border-radius: 8px;
                padding: 1px 5px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['primary']};
                color: white;
            }}
        """

    @classmethod
    def get_link_button_style(cls):
        """链接按钮样式"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {cls.COLORS['secondary']};
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 1px;
            }}
            QPushButton:hover {{
                color: {cls.COLORS['primary']};
            }}
        """

    @classmethod
    def get_form_label_style(cls):
        """表单标签样式"""
        return f"""
            QLabel {{
                color: {cls.COLORS['text_primary']};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                padding: 1px;
            }}
        """

    @classmethod
    def get_error_label_style(cls):
        """错误提示样式"""
        return f"""
            QLabel {{
                color: {cls.COLORS['error']};
                font-size: 12px;
                background: transparent;
                padding: 1px;
            }}
        """

    @classmethod
    def get_checkbox_style(cls):
        """复选框样式"""
        return f"""
            QCheckBox {{
                color: {cls.COLORS['text_secondary']};
                font-size: 12px;
                background: transparent;
                padding: 1px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid {cls.COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {cls.COLORS['primary']};
                border-color: {cls.COLORS['primary']};
            }}
        """
