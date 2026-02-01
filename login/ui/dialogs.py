"""
统一风格的对话框组件
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFormLayout, QFrame, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .styles import LoginStyles


class BaseDialog(QDialog):
    """基础对话框 - 统一风格"""

    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """设置UI - 子类重写"""
        pass

    def apply_styles(self):
        """应用统一样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {LoginStyles.COLORS['card_bg']};
                border: none;
            }}
        """)

    def add_shadow(self):
        """添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def create_title_bar(self, title_text):
        """创建标题栏"""
        title_frame = QFrame()
        title_frame.setFixedHeight(45)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 0, 15, 0)

        title_label = QLabel(title_text)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {LoginStyles.COLORS['text_primary']}; background: transparent;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {LoginStyles.COLORS['text_secondary']};
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #f38ba8;
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)

        return title_frame

    def create_input(self, placeholder=""):
        """创建统一风格的输入框"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(40)
        input_field.setStyleSheet(LoginStyles.get_input_style())
        return input_field

    def create_primary_button(self, text):
        """创建主按钮"""
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(LoginStyles.get_primary_button_style())
        return btn

    def create_secondary_button(self, text):
        """创建次要按钮"""
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(LoginStyles.get_secondary_button_style())
        return btn


class RegisterDialog(BaseDialog):
    """注册对话框"""

    def __init__(self, parent=None, auth_manager=None):
        self.auth_manager = auth_manager
        super().__init__(parent, "用户注册")
        self.setFixedSize(380, 320)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar("用户注册")
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QFormLayout(content_frame)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(15)

        # 用户名
        self.username_input = self.create_input("请输入用户名")
        content_layout.addRow("用户名:", self.username_input)

        # 密码
        self.password_input = self.create_input("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        content_layout.addRow("密码:", self.password_input)

        # 确认密码
        self.confirm_input = self.create_input("请再次输入密码")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        content_layout.addRow("确认密码:", self.confirm_input)

        layout.addWidget(content_frame)

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)
        btn_layout.setSpacing(15)

        self.confirm_btn = self.create_primary_button("确认注册")
        self.confirm_btn.clicked.connect(self.do_register)

        self.cancel_btn = self.create_secondary_button("取消")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()


class ChangePasswordDialog(BaseDialog):
    """修改密码对话框"""

    def __init__(self, parent=None, username="", db_manager=None):
        self.username = username
        self.db_manager = db_manager
        self.success = False
        super().__init__(parent, "修改密码")
        self.setFixedSize(400, 350)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar("修改密码")
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 20, 30, 15)
        content_layout.setSpacing(15)

        # 用户名显示
        user_label = QLabel(f"当前用户: {self.username}")
        user_label.setFont(QFont("Microsoft YaHei", 11))
        user_label.setStyleSheet(f"color: {LoginStyles.COLORS['text_secondary']}; background: transparent;")
        content_layout.addWidget(user_label)

        # 原密码输入
        self.old_pwd_input = self.create_input("请输入原密码")
        self.old_pwd_input.setEchoMode(QLineEdit.Password)
        content_layout.addWidget(self.old_pwd_input)

        # 新密码输入
        self.new_pwd_input = self.create_input("请输入新密码")
        self.new_pwd_input.setEchoMode(QLineEdit.Password)
        content_layout.addWidget(self.new_pwd_input)

        # 确认新密码
        self.confirm_pwd_input = self.create_input("请确认新密码")
        self.confirm_pwd_input.setEchoMode(QLineEdit.Password)
        self.confirm_pwd_input.returnPressed.connect(self.on_confirm)
        content_layout.addWidget(self.confirm_pwd_input)

        layout.addWidget(content_frame)

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)
        btn_layout.setSpacing(15)

        self.cancel_btn = self.create_secondary_button("取消")
        self.cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = self.create_primary_button("确认修改")
        self.confirm_btn.clicked.connect(self.on_confirm)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.confirm_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()

    def on_confirm(self):
        """确认修改密码"""
        import hashlib

        old_pwd = self.old_pwd_input.text().strip()
        new_pwd = self.new_pwd_input.text().strip()
        confirm_pwd = self.confirm_pwd_input.text().strip()

        # 验证输入
        if not old_pwd:
            QMessageBox.warning(self, "提示", "请输入原密码")
            return

        if not new_pwd:
            QMessageBox.warning(self, "提示", "请输入新密码")
            return

        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            return

        if len(new_pwd) < 6:
            QMessageBox.warning(self, "提示", "新密码长度不能少于6位")
            return

        # 验证原密码并更新
        if self.db_manager:
            try:
                # 验证原密码
                old_hash = hashlib.sha256(old_pwd.encode()).hexdigest()
                result = self.db_manager.execute_query(
                    "SELECT * FROM users WHERE username = %s AND password_hash = %s AND status = 1",
                    (self.username, old_hash)
                )

                if not result or len(result) == 0:
                    QMessageBox.warning(self, "错误", "原密码错误")
                    return

                # 更新密码
                new_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
                self.db_manager.execute_update(
                    "UPDATE users SET password_hash = %s WHERE username = %s",
                    (new_hash, self.username)
                )

                self.success = True
                QMessageBox.information(self, "成功", "密码修改成功")
                self.accept()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改密码失败: {str(e)}")
        else:
            QMessageBox.warning(self, "错误", "数据库未连接")

    def do_register(self):
        """执行注册"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        success, message = self.auth_manager.register(username, password, confirm)
        if success:
            msg_dialog = MessageDialog(self, "注册成功", message, "success")
            msg_dialog.exec_()
            self.accept()
        else:
            msg_dialog = MessageDialog(self, "注册失败", message, "error")
            msg_dialog.exec_()


class PasswordVerifyDialog(BaseDialog):
    """密码验证对话框"""

    def __init__(self, parent=None):
        super().__init__(parent, "验证身份")
        self.setFixedSize(350, 200)
        self.verified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar("验证身份")
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(15)

        # 提示信息
        info_label = QLabel("请输入管理员密码以重新配置")
        info_label.setFont(QFont("Microsoft YaHei", 11))
        info_label.setStyleSheet(f"color: {LoginStyles.COLORS['text_secondary']}; background: transparent;")
        content_layout.addWidget(info_label)

        # 密码输入
        self.pwd_input = self.create_input("请输入密码")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        content_layout.addWidget(self.pwd_input)

        layout.addWidget(content_frame)

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)
        btn_layout.setSpacing(15)

        self.confirm_btn = self.create_primary_button("确认")
        self.confirm_btn.clicked.connect(self.verify_password)

        self.cancel_btn = self.create_secondary_button("取消")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()

    def verify_password(self):
        """验证密码 - 从数据库验证admin用户密码"""
        import hashlib
        from login.data.db_manager import DatabaseManager
        from login.data.db_config import DatabaseConfig
        
        password = self.pwd_input.text().strip()
        
        # 获取数据库配置
        db_config = DatabaseConfig()
        config = db_config.get_config()
        
        # 如果数据库已配置，从数据库验证
        if config.get('is_configured'):
            try:
                db_manager = DatabaseManager(config)
                # 计算密码哈希
                hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                # 查询数据库验证
                result = db_manager.execute_query(
                    "SELECT * FROM users WHERE username = 'admin' AND password_hash = %s AND status = 1",
                    (hashed_pwd,)
                )
                
                if result and len(result) > 0:
                    self.verified = True
                    self.accept()
                else:
                    QMessageBox.warning(self, "验证失败", "密码错误，请重试")
                    self.pwd_input.clear()
                    self.pwd_input.setFocus()
            except Exception as e:
                QMessageBox.warning(self, "验证失败", f"数据库错误: {str(e)}")
                self.pwd_input.clear()
                self.pwd_input.setFocus()
        else:
            # 数据库未配置时，使用默认密码验证
            if password == "123456":
                self.verified = True
                self.accept()
            else:
                QMessageBox.warning(self, "验证失败", "密码错误，请重试")
                self.pwd_input.clear()
                self.pwd_input.setFocus()


class DatabaseConfigDialog(BaseDialog):
    """数据库配置对话框"""

    def __init__(self, parent=None, db_config=None):
        self.db_config = db_config
        super().__init__(parent, "数据库配置")
        self.setFixedSize(420, 400)

    def setup_ui(self):
        config = self.db_config.get_config()
        # 从配置中读取是否已配置状态
        is_configured = config.get('is_configured', False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar("数据库配置")
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QFormLayout(content_frame)
        content_layout.setContentsMargins(30, 20, 30, 15)
        content_layout.setSpacing(12)

        # 主机
        self.host_input = self.create_input("localhost")
        self.host_input.setText(config.get('host', 'localhost'))
        content_layout.addRow("主机:", self.host_input)

        # 端口
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(config.get('port', 3306))
        self.port_input.setFixedHeight(40)
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {LoginStyles.COLORS['input_bg']};
                border: 2px solid {LoginStyles.COLORS['border']};
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border-color: {LoginStyles.COLORS['primary']};
            }}
        """)
        content_layout.addRow("端口:", self.port_input)

        # 数据库
        self.db_input = self.create_input("myapp")
        self.db_input.setText(config.get('database', 'myapp'))
        content_layout.addRow("数据库:", self.db_input)

        # 用户名
        self.user_input = self.create_input("root")
        self.user_input.setText(config.get('username', 'root'))
        content_layout.addRow("用户名:", self.user_input)

        # 密码
        self.pwd_input = self.create_input("")
        self.pwd_input.setText(config.get('password', ''))
        self.pwd_input.setEchoMode(QLineEdit.Password)
        content_layout.addRow("密码:", self.pwd_input)

        # 连接状态显示
        self.status_label = QLabel("● 未连接")
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet(f"""
            color: {LoginStyles.COLORS['text_secondary']};
            background: transparent;
            padding: 5px 0;
        """)
        content_layout.addRow("状态:", self.status_label)

        layout.addWidget(content_frame)

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)
        btn_layout.setSpacing(10)

        self.test_btn = self.create_secondary_button("测试连接")
        self.test_btn.clicked.connect(self.test_connection)

        self.save_btn = self.create_primary_button("保存配置")
        self.save_btn.clicked.connect(self.save_config)

        # 重新配置按钮（初始隐藏）
        self.reconfig_btn = self.create_secondary_button("重新配置")
        self.reconfig_btn.clicked.connect(self.reconfigure)
        self.reconfig_btn.setVisible(False)

        self.cancel_btn = self.create_secondary_button("取消")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reconfig_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()

        # 如果已配置，则禁用输入并显示重新配置按钮
        if is_configured:
            self.set_inputs_enabled(False)
            self.test_btn.setEnabled(False)
            self.save_btn.setVisible(False)
            self.reconfig_btn.setVisible(True)
            # 更新状态为已连接
            self.status_label.setText("● 已连接")
            self.status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['success']};
                background: transparent;
                padding: 5px 0;
            """)

    def test_connection(self):
        """测试连接并初始化数据库"""
        from ..data.db_manager import DatabaseManager
        
        # 更新配置
        self.db_config.update_config(
            host=self.host_input.text(),
            port=self.port_input.value(),
            database=self.db_input.text(),
            username=self.user_input.text(),
            password=self.pwd_input.text()
        )

        # 先测试连接
        success, message = self.db_config.test_connection()
        if not success:
            # 更新状态为连接失败
            self.status_label.setText("● 连接失败")
            self.status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['error']};
                background: transparent;
                padding: 5px 0;
            """)
            msg_dialog = MessageDialog(self, "连接失败", message, "error")
            msg_dialog.exec_()
            return
        
        # 连接成功，初始化数据库
        db_manager = DatabaseManager(self.db_config.get_config())
        success, message = db_manager.create_or_update_database()
        
        if success:
            # 更新状态为已连接
            self.status_label.setText("● 已连接")
            self.status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['success']};
                background: transparent;
                padding: 5px 0;
            """)
            msg_dialog = MessageDialog(self, "初始化完成", message, "success")
            msg_dialog.exec_()
            # 禁用所有输入控件
            self.set_inputs_enabled(False)
            # 禁用测试连接按钮
            self.test_btn.setEnabled(False)
            # 隐藏保存配置按钮，显示重新配置按钮
            self.save_btn.setVisible(False)
            self.reconfig_btn.setVisible(True)
            # 保存已配置状态
            self.db_config.update_config(is_configured=True)
        else:
            # 更新状态为初始化失败
            self.status_label.setText("● 初始化失败")
            self.status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['error']};
                background: transparent;
                padding: 5px 0;
            """)
            msg_dialog = MessageDialog(self, "初始化失败", message, "error")
            msg_dialog.exec_()

    def save_config(self):
        """保存配置"""
        success = self.db_config.update_config(
            host=self.host_input.text(),
            port=self.port_input.value(),
            database=self.db_input.text(),
            username=self.user_input.text(),
            password=self.pwd_input.text(),
            is_configured=True
        )

        if success:
            msg_dialog = MessageDialog(self, "保存成功", "数据库配置已保存", "success")
            msg_dialog.exec_()
            self.accept()
        else:
            msg_dialog = MessageDialog(self, "保存失败", "配置保存失败，请检查权限", "error")
            msg_dialog.exec_()

    def reconfigure(self):
        """重新配置 - 需要验证密码"""
        verify_dialog = PasswordVerifyDialog(self)
        if verify_dialog.exec_() == QDialog.Accepted and verify_dialog.verified:
            # 验证成功，解除禁用
            self.set_inputs_enabled(True)
            self.test_btn.setEnabled(True)
            # 显示保存配置按钮，隐藏重新配置按钮
            self.save_btn.setVisible(True)
            self.reconfig_btn.setVisible(False)
            # 更新配置状态为未配置
            self.db_config.update_config(is_configured=False)
            # 重置状态显示
            self.status_label.setText("● 未连接")
            self.status_label.setStyleSheet(f"""
                color: {LoginStyles.COLORS['text_secondary']};
                background: transparent;
                padding: 5px 0;
            """)
            msg_dialog = MessageDialog(self, "验证成功", "现在可以重新配置数据库", "success")
            msg_dialog.exec_()

    def set_inputs_enabled(self, enabled):
        """设置所有输入控件的启用状态"""
        self.host_input.setEnabled(enabled)
        self.port_input.setEnabled(enabled)
        self.db_input.setEnabled(enabled)
        self.user_input.setEnabled(enabled)
        self.pwd_input.setEnabled(enabled)


class MessageDialog(BaseDialog):
    """消息提示对话框"""

    def __init__(self, parent=None, title="提示", message="", msg_type="info"):
        self.message = message
        self.msg_type = msg_type  # info, warning, error, success
        super().__init__(parent, title)
        self.setFixedSize(350, 200)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar(self.windowTitle())
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 25, 30, 20)
        content_layout.setSpacing(15)

        # 根据类型设置图标颜色
        icon_colors = {
            'info': LoginStyles.COLORS['primary'],
            'success': LoginStyles.COLORS['success'],
            'warning': '#ff9800',
            'error': LoginStyles.COLORS['error']
        }
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        # 图标和消息
        msg_layout = QHBoxLayout()
        msg_layout.setSpacing(15)

        icon_label = QLabel(icons.get(self.msg_type, 'ℹ️'))
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setStyleSheet("background: transparent;")
        msg_layout.addWidget(icon_label)

        message_label = QLabel(self.message)
        message_label.setFont(QFont("Microsoft YaHei", 12))
        message_label.setStyleSheet(f"color: {LoginStyles.COLORS['text_primary']}; background: transparent;")
        message_label.setWordWrap(True)
        msg_layout.addWidget(message_label, 1)

        content_layout.addLayout(msg_layout)
        layout.addWidget(content_frame)
        layout.addStretch()

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)

        self.ok_btn = self.create_primary_button("确定")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()


class ForgotPasswordDialog(BaseDialog):
    """忘记密码对话框"""

    def __init__(self, parent=None):
        super().__init__(parent, "忘记密码")
        self.setFixedSize(380, 250)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar("忘记密码")
        layout.addWidget(title_bar)

        # 内容区域
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 20)
        content_layout.setSpacing(20)

        # 提示信息
        info_label = QLabel("请联系管理员重置密码")
        info_label.setFont(QFont("Microsoft YaHei", 12))
        info_label.setStyleSheet(f"color: {LoginStyles.COLORS['text_primary']}; background: transparent;")
        info_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(info_label)

        # 邮箱信息
        email_label = QLabel("📧  admin@example.com")
        email_label.setFont(QFont("Microsoft YaHei", 11))
        email_label.setStyleSheet(f"color: {LoginStyles.COLORS['primary']}; background: transparent;")
        email_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(email_label)

        # 电话信息
        phone_label = QLabel("📞  400-123-4567")
        phone_label.setFont(QFont("Microsoft YaHei", 11))
        phone_label.setStyleSheet(f"color: {LoginStyles.COLORS['primary']}; background: transparent;")
        phone_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(phone_label)

        layout.addWidget(content_frame)
        layout.addStretch()

        # 按钮区域
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30, 10, 30, 20)

        self.ok_btn = self.create_primary_button("知道了")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(btn_frame)

        self.add_shadow()
