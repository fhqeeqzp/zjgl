"""
PySide6 原生组件封装模块
提供统一风格的组件封装，替代 QFluentWidgets
"""
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QDoubleSpinBox,
    QTextEdit, QDateEdit
)


class PushButton(QPushButton):
    """标准按钮 - 统一风格"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setCursor(Qt.PointingHandCursor)


class PrimaryPushButton(QPushButton):
    """主要按钮 - 主题色背景"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()
        self.setDefault(True)

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setCursor(Qt.PointingHandCursor)


class TransparentPushButton(QPushButton):
    """透明按钮 - 用于图标按钮"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)


class LineEdit(QLineEdit):
    """标准输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class SearchLineEdit(QLineEdit):
    """搜索输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setPlaceholderText("搜索...")


class PasswordLineEdit(QLineEdit):
    """密码输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setPlaceholderText("请输入密码")
        self.setEchoMode(QLineEdit.Password)


class ComboBox(QComboBox):
    """下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))


class DoubleSpinBox(QDoubleSpinBox):
    """数值输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setDecimals(2)
        self.setRange(0, 9999999999.99)


class TextEdit(QTextEdit):
    """文本框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()

    def _setup_style(self):
        """设置基础样式"""
        self.setFont(QFont("Microsoft YaHei", 10))


class DateEdit(QDateEdit):
    """日期选择框 - 带日历弹窗，年份范围当前年份前后20年"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_calendar()

    def _setup_style(self):
        """设置基础样式"""
        self.setFixedHeight(35)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())

    def _setup_calendar(self):
        """设置日历弹窗年份范围"""
        from PySide6.QtCore import QDate
        from PySide6.QtWidgets import QCalendarWidget
        
        # 创建自定义日历控件
        calendar = QCalendarWidget(self)
        
        # 设置年份范围：当前年份前后20年
        current_year = QDate.currentDate().year()
        calendar.setMinimumDate(QDate(current_year - 20, 1, 1))
        calendar.setMaximumDate(QDate(current_year + 20, 12, 31))
        
        # 设置日历弹窗
        self.setCalendarWidget(calendar)


class FluentComponentAdapter:
    """兼容适配器 - 保留类名用于兼容"""

    @staticmethod
    def apply_theme_to_fluent(theme_dict: dict):
        """
        主题适配方法 - 现在通过样式表应用主题
        :param theme_dict: 项目主题字典
        """
        # PySide6 原生组件通过样式表应用主题
        pass


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
