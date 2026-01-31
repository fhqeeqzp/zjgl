"""
登录窗口入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from login.ui import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
