"""
登录窗口
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QPixmap

from .styles import LoginStyles
from ..logic.auth_manager import AuthManager
from ..data.db_config import DatabaseConfig


class LoginWindow(QMainWindow):
    """登录窗口"""

    def __init__(self):
        super().__init__()

        # 初始化数据库配置
        self.db_config = DatabaseConfig()
        # 初始化认证管理器，传入数据库配置
        self.auth_manager = AuthManager(self.db_config.get_config())

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """设置UI"""
        # 窗口基本设置
        self.setWindowTitle("用户登录")
        self.setFixedSize(900, 550)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局（水平3:2比例）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧图片区域（占3份）
        left_panel = QFrame()
        left_panel.setFixedWidth(540)  # 900 * 3/5 = 540
        self.left_panel = left_panel

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.load_default_image()
        left_layout.addWidget(self.image_label)

        # 右侧表单区域（占2份）
        right_panel = QFrame()
        right_panel.setFixedWidth(360)  # 900 * 2/5 = 360
        self.right_panel = right_panel

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 50, 40, 50)
        right_layout.setSpacing(20)

        # 标题区域
        title_label = QLabel("欢迎回来")
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.title_label = title_label
        right_layout.addWidget(title_label)

        subtitle_label = QLabel("请登录您的账户")
        subtitle_label.setFont(QFont("Microsoft YaHei", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label = subtitle_label
        right_layout.addWidget(subtitle_label)

        right_layout.addSpacing(30)

        # 用户名输入（标签和输入框在一行）
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        username_label.setFixedWidth(70)
        self.username_label = username_label
        username_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(45)
        username_layout.addWidget(self.username_input)
        right_layout.addLayout(username_layout)

        right_layout.addSpacing(15)

        # 密码输入（标签和输入框在一行）
        password_layout = QHBoxLayout()
        password_label = QLabel("密  码:")
        password_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        password_label.setFixedWidth(70)
        self.password_label = password_label
        password_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.returnPressed.connect(self.on_login)  # 回车键登录
        password_layout.addWidget(self.password_input)
        right_layout.addLayout(password_layout)

        # 记住密码和忘记密码
        remember_layout = QHBoxLayout()

        self.remember_checkbox = QCheckBox("记住密码")
        remember_layout.addWidget(self.remember_checkbox)

        remember_layout.addStretch()

        forgot_btn = QPushButton("忘记密码?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.clicked.connect(self.on_forgot_password)
        self.forgot_btn = forgot_btn
        remember_layout.addWidget(forgot_btn)

        right_layout.addLayout(remember_layout)

        right_layout.addSpacing(20)

        # 错误提示标签
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        right_layout.addWidget(self.error_label)

        # 登录和注册按钮（在一行）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.login_btn = QPushButton("登 录")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.on_login)
        btn_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("注 册")
        self.register_btn.setFixedHeight(45)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.clicked.connect(self.on_register)
        btn_layout.addWidget(self.register_btn)

        right_layout.addLayout(btn_layout)

        right_layout.addStretch()

        # 数据库配置链接和状态
        db_config_layout = QHBoxLayout()
        db_config_layout.setSpacing(10)
        
        db_config_btn = QPushButton("数据库配置")
        db_config_btn.setCursor(Qt.PointingHandCursor)
        db_config_btn.clicked.connect(self.on_db_config)
        self.db_config_btn = db_config_btn
        db_config_layout.addWidget(db_config_btn)
        
        # 数据库连接状态
        self.db_status_label = QLabel("● 未连接")
        self.db_status_label.setFont(QFont("Microsoft YaHei", 10))
        self.update_db_status_label()
        db_config_layout.addWidget(self.db_status_label)
        
        # 创建一个容器来居中显示
        db_config_container = QWidget()
        db_config_container.setLayout(db_config_layout)
        right_layout.addWidget(db_config_container, alignment=Qt.AlignCenter)

        # 添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # 添加阴影效果
        self.add_shadow_effect()

    def load_default_image(self):
        """加载登录图片"""
        import os
        
        # 尝试加载 webp 图片
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '登录.webp')
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 设置图片并保持比例填充
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                ))
                self.image_label.setAlignment(Qt.AlignCenter)
                return
        
        # 如果图片加载失败，使用渐变色背景
        self.image_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2196F3,
                    stop: 1 #1976D2
                );
            }
        """)
        self.image_label.setText("🖼️\n登录图片")
        self.image_label.setFont(QFont("Segoe UI Emoji", 48))
        self.image_label.setAlignment(Qt.AlignCenter)

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(LoginStyles.get_main_window_style())
        self.left_panel.setStyleSheet(LoginStyles.get_left_panel_style())
        self.right_panel.setStyleSheet(LoginStyles.get_right_panel_style())

        self.title_label.setStyleSheet(LoginStyles.get_title_label_style())
        self.subtitle_label.setStyleSheet(LoginStyles.get_subtitle_label_style())
        self.username_label.setStyleSheet(LoginStyles.get_form_label_style())
        self.password_label.setStyleSheet(LoginStyles.get_form_label_style())

        self.username_input.setStyleSheet(LoginStyles.get_input_style())
        self.password_input.setStyleSheet(LoginStyles.get_input_style())

        self.login_btn.setStyleSheet(LoginStyles.get_primary_button_style())
        self.register_btn.setStyleSheet(LoginStyles.get_secondary_button_style())

        self.forgot_btn.setStyleSheet(LoginStyles.get_link_button_style())
        self.db_config_btn.setStyleSheet(LoginStyles.get_link_button_style())

        self.remember_checkbox.setStyleSheet(LoginStyles.get_checkbox_style())
        self.error_label.setStyleSheet(LoginStyles.get_error_label_style())

    def add_shadow_effect(self):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.centralWidget().setGraphicsEffect(shadow)

    def on_login(self):
        """登录按钮点击"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        remember = self.remember_checkbox.isChecked()

        # 调用认证管理器
        success, message = self.auth_manager.login(username, password, remember)

        if success:
            self.error_label.setVisible(False)
            # 调用登录成功回调（如果有）
            if hasattr(self, 'on_login_success') and callable(self.on_login_success):
                self.on_login_success()
            else:
                QMessageBox.information(self, "登录成功", message)
        else:
            self.error_label.setText(message)
            self.error_label.setVisible(True)

    def on_register(self):
        """注册按钮点击"""
        from .dialogs import RegisterDialog

        dialog = RegisterDialog(self, self.auth_manager)
        dialog.exec_()

    def on_forgot_password(self):
        """忘记密码"""
        from .dialogs import ForgotPasswordDialog

        dialog = ForgotPasswordDialog(self)
        dialog.exec_()

    def on_db_config(self):
        """数据库配置"""
        from .dialogs import DatabaseConfigDialog

        dialog = DatabaseConfigDialog(self, self.db_config)
        dialog.exec_()
        # 对话框关闭后更新状态显示
        self.update_db_status_label()

    def update_db_status_label(self):
        """更新数据库连接状态显示"""
        config = self.db_config.get_config()
        is_configured = config.get('is_configured', False)
        
        if is_configured:
            self.db_status_label.setText("● 已连接")
            self.db_status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['success']};
                background: transparent;
            """)
        else:
            self.db_status_label.setText("● 未连接")
            self.db_status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['text_secondary']};
                background: transparent;
            """)

    def mousePressEvent(self, event):
        """鼠标按下事件（用于拖动窗口）"""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件（用于拖动窗口）"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
