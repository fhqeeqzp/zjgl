import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem
)

class PrettyScrollBarDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_light_theme = True
        self.apply_light_theme()

    def init_ui(self):
        # 窗口设置
        self.setWindowTitle("PySide6 精致滚动条 QSS 样式演示")
        self.resize(600, 500)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 切换主题按钮
        self.theme_btn = QPushButton("切换为深色主题")
        self.theme_btn.clicked.connect(self.switch_theme)
        layout.addWidget(self.theme_btn)

        # 1. 带滚动条的文本框
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("输入大量文本查看滚动条效果...")
        test_text = "精致滚动条样式测试 " * 1000
        self.text_edit.setText(test_text)
        layout.addWidget(self.text_edit)

        # 2. 带滚动条的表格
        self.table = QTableWidget(20, 4)
        self.table.setHorizontalHeaderLabels(["列1", "列2", "列3", "列4"])
        for row in range(20):
            for col in range(4):
                self.table.setItem(row, col, QTableWidgetItem(f"数据-{row+1}-{col+1}"))
        layout.addWidget(self.table)

    def apply_light_theme(self):
        """应用精致浅色主题"""
        light_qss = """
        /* 全局控件基础样式（配合滚动条，保持清新） */
        QWidget {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            font-size: 13px;
        }

        QTextEdit, QTableWidget {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #e9e9e9;
            border-radius: 8px;
            padding: 8px;
        }

        QTableWidget::horizontalHeader::section {
            background-color: #fafafa;
            border: none;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #f8f9fa;
            color: #333333;
            border: 1px solid #e9e9e9;
            border-radius: 8px;
            padding: 6px 16px;
            transition: background-color 0.2s ease;
        }

        QPushButton:hover {
            background-color: #eef5ff;
            border-color: #c8d8e8;
        }

        /* ========== 精致浅色主题 - 滚动条 ========== */
        QScrollBar:vertical {
            width: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
            margin: 4px 2px 4px 2px;
        }

        QScrollBar::handle:vertical {
            background-color: #c8d8e8;
            border-radius: 5px;
            min-height: 40px;
            margin: 2px 0px;
            transition: background-color 0.2s ease;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #a0b9d0;
        }

        QScrollBar::handle:vertical:pressed {
            background-color: #7d9fc7;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            display: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background-color: transparent;
        }

        QScrollBar:horizontal {
            height: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
            margin: 2px 4px 2px 4px;
        }

        QScrollBar::handle:horizontal {
            background-color: #c8d8e8;
            border-radius: 5px;
            min-width: 40px;
            margin: 0px 2px;
            transition: background-color 0.2s ease;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #a0b9d0;
        }

        QScrollBar::handle:horizontal:pressed {
            background-color: #7d9fc7;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            display: none;
        }

        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background-color: transparent;
        }
        """
        self.setStyleSheet(light_qss)

    def apply_dark_theme(self):
        """应用精致深色主题"""
        dark_qss = """
        /* 全局控件基础样式（配合滚动条，保持高级感） */
        QWidget {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            font-size: 13px;
        }

        QTextEdit, QTableWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 8px;
        }

        QTableWidget::horizontalHeader::section {
            background-color: #252525;
            border: none;
            padding: 8px;
            font-weight: bold;
        }

        QPushButton {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 6px 16px;
            transition: background-color 0.2s ease;
        }

        QPushButton:hover {
            background-color: #3a4f6b;
            border-color: #405468;
        }

        /* ========== 精致深色主题 - 滚动条 ========== */
        QScrollBar:vertical {
            width: 10px;
            background-color: #292929;
            border-radius: 5px;
            margin: 4px 2px 4px 2px;
        }

        QScrollBar::handle:vertical {
            background-color: #405468;
            border-radius: 5px;
            min-height: 40px;
            margin: 2px 0px;
            transition: background-color 0.2s ease;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #526a82;
        }

        QScrollBar::handle:vertical:pressed {
            background-color: #647f9c;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            display: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background-color: transparent;
        }

        QScrollBar:horizontal {
            height: 10px;
            background-color: #292929;
            border-radius: 5px;
            margin: 2px 4px 2px 4px;
        }

        QScrollBar::handle:horizontal {
            background-color: #405468;
            border-radius: 5px;
            min-width: 40px;
            margin: 0px 2px;
            transition: background-color 0.2s ease;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #526a82;
        }

        QScrollBar::handle:horizontal:pressed {
            background-color: #647f9c;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            display: none;
        }

        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background-color: transparent;
        }
        """
        self.setStyleSheet(dark_qss)

    def switch_theme(self):
        """切换浅色/深色主题"""
        if self.is_light_theme:
            self.apply_dark_theme()
            self.theme_btn.setText("切换为浅色主题")
            self.is_light_theme = False
        else:
            self.apply_light_theme()
            self.theme_btn.setText("切换为深色主题")
            self.is_light_theme = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PrettyScrollBarDemo()
    window.show()
    sys.exit(app.exec())