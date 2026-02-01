"""
QFluentWidgets 组件适配模块
提供与项目主题系统集成的Fluent风格组件
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    PushButton as FluentPushButton,
    PrimaryPushButton as FluentPrimaryPushButton,
    TransparentPushButton as FluentTransparentPushButton,
    LineEdit as FluentLineEdit,
    SearchLineEdit as FluentSearchLineEdit,
    PasswordLineEdit as FluentPasswordLineEdit,
    ComboBox as FluentComboBox,
    SpinBox as FluentSpinBox,
    DoubleSpinBox as FluentDoubleSpinBox,
    TextEdit as FluentTextEdit,
    DateEdit as FluentDateEdit,
    Theme,
    setTheme,
    setThemeColor
)


class FluentComponentAdapter:
    """Fluent组件适配器 - 将QFluentWidgets组件与项目主题系统集成"""

    @staticmethod
    def apply_theme_to_fluent(theme_dict: dict):
        """
        将项目主题应用到QFluentWidgets
        :param theme_dict: 项目主题字典
        """
        # 根据主题设置Fluent主题
        if theme_dict.get('name') == '浅色主题':
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)

        # 设置主题色
        accent_color = theme_dict.get('accent', '#6c5ce7')
        setThemeColor(accent_color)


class PushButton(FluentPushButton):
    """Fluent风格按钮 - 默认样式"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class PrimaryPushButton(FluentPrimaryPushButton):
    """Fluent风格主要按钮 - 主题色背景"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class TransparentPushButton(FluentTransparentPushButton):
    """Fluent风格透明按钮 - 用于图标按钮"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class LineEdit(FluentLineEdit):
    """Fluent风格输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class SearchLineEdit(FluentSearchLineEdit):
    """Fluent风格搜索输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setPlaceholderText("搜索...")


class PasswordLineEdit(FluentPasswordLineEdit):
    """Fluent风格密码输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setPlaceholderText("请输入密码")


class ComboBox(FluentComboBox):
    """Fluent风格下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class DoubleSpinBox(FluentDoubleSpinBox):
    """Fluent风格数值输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setDecimals(2)
        self.setRange(0, 9999999999.99)


class TextEdit(FluentTextEdit):
    """Fluent风格文本框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFont(QFont("Microsoft YaHei", 10))


class DateEdit(FluentDateEdit):
    """Fluent风格日期选择框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setCalendarPopup(True)


# 导出所有组件
__all__ = [
    'PushButton',
    'PrimaryPushButton',
    'TransparentPushButton',
    'LineEdit',
    'SearchLineEdit',
    'PasswordLineEdit',
    'ComboBox',
    'DoubleSpinBox',
    'TextEdit',
    'DateEdit',
    'FluentComponentAdapter'
]
