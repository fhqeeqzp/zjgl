"""
登录窗口入口
"""
import sys
import os

# 抑制Qt警告信息
os.environ['QT_LOGGING_RULES'] = '*.warning=false;qt.svg.warning=false;qt.png.warning=false'

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from login.ui import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
