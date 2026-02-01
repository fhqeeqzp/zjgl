# calendar_theme_manager.py
from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication
import sys


class CalendarThemeManager:
    """
    PySide6 日历控件 (QCalendarWidget) 主题管理器
    支持深色/浅色、中文、紧凑模式、大字体等
    """

    # ========== 内置 QSS ==========
    LIGHT_QSS = """
QCalendarWidget {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    color: #1A1A1A;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #F5F5F5;
    padding: 6px;
    min-height: 30px;
}
QCalendarWidget QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 2px 8px;
    color: #1A1A1A;
    min-width: 80px;
}
QCalendarWidget QComboBox:hover {
    border-color: #999999;
}
QCalendarWidget QComboBox::drop-down,
QCalendarWidget QComboBox::down-arrow {
    image: url(none);
}
QCalendarWidget QTableView {
    selection-background-color: #0078D4;
    selection-color: #FFFFFF;
    alternate-background-color: #FAFAFA;
    background-color: #FFFFFF;
    gridline-color: #E0E0E0;
    outline: 0;
    border: none;
}
QCalendarWidget QTableView::item {
    border: none;
    padding: VAR_PADDING;
    margin: 0;
    text-align: center;
}
QCalendarWidget QTableView::item:selected {
    background-color: #0078D4;
    color: white;
    border-radius: 4px;
}
QCalendarWidget QTableView::item[weekend="true"] {
    color: #D93025;
}
QCalendarWidget QHeaderView::section {
    background-color: #FAFAFA;
    color: #595959;
    font-size: VAR_HEADER_FONT_SIZE;
    font-weight: bold;
    padding: VAR_HEADER_PADDING;
    border: none;
    text-align: center;
}
QCalendarWidget QToolButton {
    background-color: transparent;
    border: none;
    color: #1A1A1A;
    font-weight: bold;
    padding: 2px 6px;
    margin: 0 2px;
}
QCalendarWidget QToolButton:hover {
    background-color: #E0E0E0;
    border-radius: 4px;
}
"""

    DARK_QSS = """
QCalendarWidget {
    background-color: #252525;
    border: 1px solid #444444;
    color: #E6E6E6;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #2D2D2D;
    padding: 6px;
    min-height: 30px;
}
QCalendarWidget QComboBox {
    background-color: #2D2D2D;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 2px 8px;
    color: #E6E6E6;
    min-width: 80px;
}
QCalendarWidget QComboBox:hover {
    border-color: #666666;
}
QCalendarWidget QComboBox::drop-down,
QCalendarWidget QComboBox::down-arrow {
    image: url(none);
}
QCalendarWidget QTableView {
    selection-background-color: #0078D4;
    selection-color: #FFFFFF;
    alternate-background-color: #2A2A2A;
    background-color: #252525;
    gridline-color: #3C3C3C;
    outline: 0;
    border: none;
}
QCalendarWidget QTableView::item {
    border: none;
    padding: VAR_PADDING;
    margin: 0;
    text-align: center;
}
QCalendarWidget QTableView::item:selected {
    background-color: #0078D4;
    color: white;
    border-radius: 4px;
}
QCalendarWidget QTableView::item[weekend="true"] {
    color: #F28B82;
}
QCalendarWidget QHeaderView::section {
    background-color: #2A2A2A;
    color: #B3B3B3;
    font-size: VAR_HEADER_FONT_SIZE;
    font-weight: bold;
    padding: VAR_HEADER_PADDING;
    border: none;
    text-align: center;
}
QCalendarWidget QToolButton {
    background-color: transparent;
    border: none;
    color: #E6E6E6;
    font-weight: bold;
    padding: 2px 6px;
    margin: 0 2px;
}
QCalendarWidget QToolButton:hover {
    background-color: #3C3C3C;
    border-radius: 4px;
}
"""

    def __init__(self, app: QApplication):
        self.app = app
        self._compact_mode = False
        self._large_text_mode = False
        self._chinese_locale = False

    def enable_chinese(self, enable: bool = True):
        """启用中文本地化（影响星期、月份显示）"""
        self._chinese_locale = enable
        if enable:
            QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))
        return self

    def set_compact_mode(self, enable: bool = True):
        """启用紧凑模式（减小内边距）"""
        self._compact_mode = enable
        self._apply_theme()
        return self

    def set_large_text_mode(self, enable: bool = True):
        """启用大字体模式（无障碍）"""
        self._large_text_mode = enable
        self._apply_theme()
        return self

    def detect_system_theme(self) -> str:
        """自动检测系统主题（仅 Windows/macOS 支持较好）"""
        palette = self.app.palette()
        bg = palette.color(QPalette.Window)
        # 简单判断：背景亮度 < 128 视为深色
        is_dark = bg.lightness() < 128
        return "dark" if is_dark else "light"

    def apply_theme(self, theme: str = "auto"):
        """
        应用主题
        :param theme: "light", "dark", or "auto"
        """
        if theme == "auto":
            theme = self.detect_system_theme()
        self._current_theme = theme
        self._apply_theme()

    def _apply_theme(self):
        # 选择基础 QSS
        base_qss = self.DARK_QSS if self._current_theme == "dark" else self.LIGHT_QSS

        # 动态替换变量
        if self._compact_mode:
            item_padding = "2px 0"
            header_padding = "2px 0"
        else:
            item_padding = "6px 0"
            header_padding = "4px 0"

        header_font_size = "14px" if self._large_text_mode else "11px"

        final_qss = (
            base_qss.replace("VAR_PADDING", item_padding)
                   .replace("VAR_HEADER_PADDING", header_padding)
                   .replace("VAR_HEADER_FONT_SIZE", header_font_size)
        )

        # 合并到全局样式（避免覆盖其他控件）
        current_style = self.app.styleSheet()
        # 移除已有的日历样式（简单方案：每次全量替换）
        self.app.setStyleSheet(final_qss + "\n" + self._filter_non_calendar_style(current_style))

    def _filter_non_calendar_style(self, style: str) -> str:
        """移除已存在的 QCalendarWidget 样式（简易实现）"""
        lines = style.splitlines()
        in_calendar_block = False
        filtered = []
        for line in lines:
            if "QCalendarWidget" in line and not line.strip().startswith("/*"):
                in_calendar_block = True
                continue
            if in_calendar_block and line.strip() == "}":
                in_calendar_block = False
                continue
            if not in_calendar_block:
                filtered.append(line)
        return "\n".join(filtered)


# ========== 快捷使用函数 ==========
def setup_calendar_theme(
    app: QApplication,
    theme: str = "auto",
    chinese: bool = True,
    compact: bool = False,
    large_text: bool = False
):
    """
    一行代码设置日历主题
    示例：
        setup_calendar_theme(app, theme="dark", chinese=True)
    """
    manager = CalendarThemeManager(app)
    if chinese:
        manager.enable_chinese()
    if compact:
        manager.set_compact_mode()
    if large_text:
        manager.set_large_text_mode()
    manager.apply_theme(theme)
    return manager