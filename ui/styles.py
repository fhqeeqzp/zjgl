"""
样式管理模块
集中管理所有UI组件的样式表

样式规范：
- 圆角统一：小圆角4px，中圆角6px，大圆角8px，窗口圆角10px
- 内边距统一：小内边距5px，中内边距8px，大内边距10px，按钮内边距8px 16px
- 字体大小统一：小字12px，正文13px，标题14px，大字16px
- 边框统一：细边框1px
"""


class StyleSheetManager:
    """样式表管理器 - 统一管理应用程序的所有样式"""

    # ==================== 基础组件样式常量 ====================
    # 圆角
    BORDER_RADIUS_SMALL = "4px"    # 小圆角：输入框
    BORDER_RADIUS_MEDIUM = "6px"   # 中圆角：按钮、卡片
    BORDER_RADIUS_LARGE = "8px"    # 大圆角：表格、分组框
    BORDER_RADIUS_WINDOW = "10px"  # 窗口圆角

    # 内边距
    PADDING_SMALL = "0px"          # 小内边距
    PADDING_MEDIUM = "0px"         # 中内边距
    PADDING_LARGE = "0px"         # 大内边距
    PADDING_BUTTON = "0px 0px"    # 按钮内边距
    PADDING_INPUT = "0px"          # 输入框内边距
    PADDING_TABLE_ITEM = "0px"     # 表格单元格内边距
    PADDING_HEADER = "0px"        # 表头内边距

    # 字体大小
    FONT_SIZE_SMALL = "12px"       # 小字
    FONT_SIZE_NORMAL = "13px"      # 正文
    FONT_SIZE_LARGE = "14px"       # 标题
    FONT_SIZE_ICON = "16px"        # 图标

    # 边框
    BORDER_WIDTH = "1px"           # 边框宽度
    BORDER_BOTTOM_WIDTH = "1px"    # 底部边框宽度

    # 尺寸
    BUTTON_HEIGHT_SMALL = "28px"   # 小按钮高度
    BUTTON_HEIGHT_NORMAL = "35px"  # 正常按钮高度
    BUTTON_HEIGHT_LARGE = "40px"   # 大按钮高度
    INPUT_HEIGHT = "35px"          # 输入框高度

    # ==================== 按钮类组件样式 ====================
    @staticmethod
    def _get_btn_base_style(theme, bg_color, text_color, hover_color, radius="6px", padding="8px 16px"):
        """按钮基础样式"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: {radius};
                padding: {padding};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    @staticmethod
    def get_primary_btn_style(theme):
        """主要按钮样式（主题色背景）"""
        return StyleSheetManager._get_btn_base_style(
            theme,
            theme['accent'],
            "#ffffff",
            theme['button_hover'],
            radius=StyleSheetManager.BORDER_RADIUS_MEDIUM
        )

    @staticmethod
    def get_secondary_btn_style(theme):
        """次要按钮样式（默认背景）"""
        return StyleSheetManager._get_btn_base_style(
            theme,
            theme['button_bg'],
            theme['text_primary'],
            theme['button_hover'],
            radius=StyleSheetManager.BORDER_RADIUS_MEDIUM
        )

    @staticmethod
    def get_sidebar_btn_style(theme):
        """侧边栏按钮样式"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                border-radius: {StyleSheetManager.BORDER_RADIUS_MEDIUM};
                text-align: center;
                font-size: {StyleSheetManager.FONT_SIZE_LARGE};
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
    def get_theme_btn_style(theme):
        """主题切换按钮样式"""
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text_primary']};
                border: none;
                border-radius: {StyleSheetManager.BORDER_RADIUS_LARGE};
                font-size: {StyleSheetManager.FONT_SIZE_NORMAL};
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
    def get_close_btn_style(theme):
        """关闭按钮样式"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                font-size: {StyleSheetManager.FONT_SIZE_ICON};
                font-weight: bold;
                border-radius: {StyleSheetManager.BORDER_RADIUS_SMALL};
            }}
            QPushButton:hover {{
                background-color: #f38ba8;
                color: #ffffff;
            }}
        """

    # ==================== 标签类组件样式 ====================
    @staticmethod
    def _get_label_style(color, font_size="13px", bg="transparent"):
        """标签基础样式"""
        return f"color: {color}; font-size: {font_size}; background: {bg};"

    @staticmethod
    def get_label_primary_style(theme):
        """主要文字标签"""
        return StyleSheetManager._get_label_style(theme['text_primary'])

    @staticmethod
    def get_label_secondary_style(theme):
        """次要文字标签"""
        return StyleSheetManager._get_label_style(theme['text_secondary'])

    @staticmethod
    def get_label_title_style(theme):
        """标题标签"""
        return f"color: {theme['text_primary']}; font-size: 18px; font-weight: bold; background: transparent;"

    # ==================== 输入框类组件样式 ====================
    @staticmethod
    def _get_input_base_style(theme, radius="1px", padding="0px"):
        """输入框基础样式"""
        return f"""
            background-color: {theme['card_bg']};
            border: 1px solid {theme['border']};
            border-radius: {radius};
            padding: {padding};
            color: {theme['text_primary']};
            font-size: 13px;
        """

    @staticmethod
    def get_input_style(theme):
        """标准输入框样式"""
        base = StyleSheetManager._get_input_base_style(theme)
        return f"""
            QLineEdit {{
                {base}
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
        """

    @staticmethod
    def get_projects_input_style(theme):
        """项目页面输入框样式"""
        return f"""
            QLineEdit {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['border']};
                border-radius: {StyleSheetManager.BORDER_RADIUS_MEDIUM};
                padding: 5px 10px;
                color: {theme['text_primary']};
                font-size: {StyleSheetManager.FONT_SIZE_NORMAL};
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
        """

    # ==================== 卡片/容器类组件样式 ====================
    @staticmethod
    def _get_card_base_style(theme, radius="8px"):
        """卡片基础样式"""
        return f"""
            background-color: {theme['card_bg']};
            border-radius: {radius};
            border: none;
        """

    @staticmethod
    def get_card_style(theme):
        """标准卡片样式"""
        return f"""
            QFrame {{
                {StyleSheetManager._get_card_base_style(theme)}
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_projects_card_style(theme):
        """项目页面统计卡片样式"""
        return f"""
            QFrame {{
                {StyleSheetManager._get_card_base_style(theme, StyleSheetManager.BORDER_RADIUS_MEDIUM)}
            }}
            QLabel {{
                color: {theme['text_primary']};
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

    # ==================== 表格类组件样式 ====================
    @staticmethod
    def get_table_style(theme):
        """仿 QFluentWidgets 风格的表格样式"""
        return f"""
            QTableWidget {{
                background-color: {theme['card_bg']};
                border: none;
                gridline-color: {theme['border']};
                color: {theme['text_primary']};
                outline: none;
                font-size: 14px;
                selection-background-color: {theme['accent']};
                alternate-background-color: {theme.get('table_alt_bg', theme['card_bg'])};
            }}

            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme['border']};
                border-right: 1px solid transparent;
                border-left: 1px solid transparent;
            }}

            QTableWidget::item:selected {{
                background-color: {theme['accent']}40; /* 半透明选中背景 */
                color: {theme['text_primary']};
                border: none;
            }}

            QTableWidget::item:focus {{
                outline: none;
            }}

            /* 表头样式 - 更现代 */
            QHeaderView::section {{
                background-color: {theme['card_bg']};
                color: {theme['text_secondary']};
                padding: 6px 12px;
                border: none;
                border-bottom: 1px solid {theme['border']};
                font-weight: 600;
                font-size: 13px;
            }}

            QHeaderView::section:first {{
                border-top-left-radius: {StyleSheetManager.BORDER_RADIUS_LARGE};
            }}

            QHeaderView::section:last {{
                border-top-right-radius: {StyleSheetManager.BORDER_RADIUS_LARGE};
            }}

            /* ------------------------------
                悬浮自动隐藏滚动条
             ------------------------------ */
            QTableWidget QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            QTableWidget QScrollBar::handle:vertical {{
                background: rgba(120, 120, 140, 0.25);
                border-radius: 3px;
                min-height: 30px;
                margin: 2px;
            }}
            QTableWidget QScrollBar::handle:vertical:hover {{
                background: rgba(160, 160, 180, 0.6);
                width: 10px;
                margin: 2px 0;
            }}
            QTableWidget QScrollBar::handle:vertical:pressed {{
                background: rgba(190, 190, 210, 0.8);
            }}

            QTableWidget QScrollBar:horizontal {{
                background: transparent;
                height: 6px;
                margin: 0;
            }}
            QTableWidget QScrollBar::handle:horizontal {{
                background: rgba(120, 120, 140, 0.25);
                border-radius: 3px;
                min-width: 30px;
                margin: 2px;
            }}
            QTableWidget QScrollBar::handle:horizontal:hover {{
                background: rgba(160, 160, 180, 0.6);
                height: 10px;
                margin: 0 2px;
            }}
            QTableWidget QScrollBar::handle:horizontal:pressed {{
                background: rgba(190, 190, 210, 0.8);
            }}

            QTableWidget QScrollBar::add-line,
            QTableWidget QScrollBar::sub-line,
            QTableWidget QScrollBar::add-page,
            QTableWidget QScrollBar::sub-page {{
                background: none;
            }}
        """

    # ==================== 页面容器类样式 ====================
    @staticmethod
    def _get_page_base_style(theme):
        """页面基础样式"""
        return f"""
            background-color: {theme['content_bg']};
            border: none;
            border-radius: 0px;
        """

    @staticmethod
    def get_homepage_style(theme):
        """首页样式"""
        return f"""
            HomePage {{
                {StyleSheetManager._get_page_base_style(theme)}
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
                {StyleSheetManager._get_page_base_style(theme)}
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
        """

    @staticmethod
    def get_placeholder_page_style(theme):
        """占位页面样式"""
        return f"""
            PlaceholderPage {{
                {StyleSheetManager._get_page_base_style(theme)}
            }}
        """

    # ==================== 特定组件样式 ====================
    @staticmethod
    def get_titlebar_style(theme):
        """标题栏样式"""
        return f"""
            TitleBar {{
                background-color: {theme['sidebar_bg']};
                border-top-left-radius: {StyleSheetManager.BORDER_RADIUS_WINDOW};
                border-top-right-radius: {StyleSheetManager.BORDER_RADIUS_WINDOW};
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
                font-size: {StyleSheetManager.FONT_SIZE_LARGE};
                font-weight: bold;
                border-radius: {StyleSheetManager.BORDER_RADIUS_SMALL};
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
                color: {theme['text_primary']};
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
    def get_main_window_style(theme):
        """主窗口样式"""
        return f"""
            QFrame {{
                background-color: {theme['window_bg']};
                border-top-left-radius: {StyleSheetManager.BORDER_RADIUS_WINDOW};
                border-top-right-radius: {StyleSheetManager.BORDER_RADIUS_WINDOW};
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
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

    # ==================== 项目管理页面样式 ====================
    @staticmethod
    def get_projects_page_style(theme):
        """项目管理页面样式"""
        return f"""
            ProjectsPage {{
                {StyleSheetManager._get_page_base_style(theme)}
            }}
            QLabel {{
                color: {theme['text_primary']};
                background: transparent;
                border: none;
            }}
            {StyleSheetManager.get_table_style(theme)}
            QSplitter::handle {{
                background-color: {theme['border']};
            }}
        """

    @staticmethod
    def get_projects_btn_style(theme):
        """项目页面按钮样式"""
        return StyleSheetManager._get_btn_base_style(
            theme,
            theme['button_bg'],
            theme['text_primary'],
            theme['button_hover'],
            radius=StyleSheetManager.BORDER_RADIUS_MEDIUM,
            padding="5px 15px"
        )

    # ==================== 项目对话框样式 ====================
    @staticmethod
    def get_project_dialog_style(theme):
        """项目对话框样式"""
        return f"""
            QDialog {{
                background-color: {theme['content_bg']};
            }}
            QLabel {{
                color: {theme['text_primary']};
                font-size: {StyleSheetManager.FONT_SIZE_NORMAL};
            }}
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['border']};
                border-radius: {StyleSheetManager.BORDER_RADIUS_SMALL};
                padding: {StyleSheetManager.PADDING_INPUT};
                color: {theme['text_primary']};
                font-size: {StyleSheetManager.FONT_SIZE_NORMAL};
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {theme['accent']};
            }}
            QGroupBox {{
                color: {theme['text_primary']};
                font-weight: bold;
                border: 1px solid {theme['border']};
                border-radius: {StyleSheetManager.BORDER_RADIUS_MEDIUM};
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            {StyleSheetManager._get_btn_base_style(theme, theme['button_bg'], theme['text_primary'], theme['button_hover'])}
            QPushButton:default {{
                background-color: {theme['accent']};
                color: white;
            }}
        """
