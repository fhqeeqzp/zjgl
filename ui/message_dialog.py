"""
自定义消息对话框模块
替代 QMessageBox，支持主题切换、无标题栏、可拖动
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QPaintEvent, QPainter, QColor, QFont


class MessageDialog(QDialog):
    """
    自定义消息对话框
    - 无标题栏（自定义标题区域）
    - 可拖动
    - 扁平化设计
    - 支持主题切换（通过 QSS）
    """
    
    # 图标类型常量
    Information = 1
    Warning = 2
    Critical = 3
    Question = 4
    
    # 按钮类型常量
    Ok = 1
    Yes = 2
    No = 4
    Cancel = 8
    
    def __init__(self, parent=None, icon_type=Information, title="", text="", 
                 buttons=Ok, default_button=Ok, min_width=400, min_height=200):
        super().__init__(parent)
        
        self.icon_type = icon_type
        self.drag_pos = None
        self.min_width = min_width
        self.min_height = min_height
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置 objectName 用于 QSS 选择
        self.setObjectName("messageDialog")
        
        self.setup_ui(title, text, buttons, default_button)
        
        # 应用阴影效果
        self.apply_shadow()
    
    def setup_ui(self, title, text, buttons, default_button):
        """设置UI"""
        # 使用 setMinimumSize 设置最小尺寸
        self.setMinimumSize(self.min_width, self.min_height)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 内容容器（用于圆角和背景）
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏（可拖动区域）
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        title_layout.setSpacing(10)
        
        # 图标
        icon_label = QLabel()
        icon_label.setObjectName("iconLabel")
        icon_pixmap = self.get_icon_pixmap()
        if icon_pixmap:
            icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(20, 20)
        icon_label.setStyleSheet("background: transparent; border: none;")
        title_layout.addWidget(icon_label)
        
        # 标题文字
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("background: transparent; border: none;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        content_layout.addWidget(title_bar)
        
        # 内容区域
        body_widget = QWidget()
        body_widget.setObjectName("bodyWidget")
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)
        
        # 大图标
        big_icon = QLabel()
        big_icon.setObjectName("bigIconLabel")
        big_icon_pixmap = self.get_icon_pixmap(48)
        if big_icon_pixmap:
            big_icon.setPixmap(big_icon_pixmap)
        big_icon.setFixedSize(48, 48)
        big_icon.setStyleSheet("background: transparent; border: none;")
        body_layout.addWidget(big_icon)
        
        # 消息文本
        text_label = QLabel(text)
        text_label.setObjectName("textLabel")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_label.setStyleSheet("background: transparent; border: none;")
        body_layout.addWidget(text_label, 1)
        
        content_layout.addWidget(body_widget, 1)
        
        # 按钮区域
        btn_widget = QWidget()
        btn_widget.setObjectName("buttonWidget")
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(20, 10, 20, 20)
        btn_layout.addStretch()
        
        # 根据按钮类型添加按钮
        if buttons & self.Yes:
            yes_btn = QPushButton("是")
            yes_btn.setObjectName("yesButton")
            yes_btn.setDefault(default_button == self.Yes)
            yes_btn.clicked.connect(lambda: self.done(self.Yes))
            btn_layout.addWidget(yes_btn)
        
        if buttons & self.No:
            no_btn = QPushButton("否")
            no_btn.setObjectName("noButton")
            no_btn.setDefault(default_button == self.No)
            no_btn.clicked.connect(lambda: self.done(self.No))
            btn_layout.addWidget(no_btn)
        
        if buttons & self.Ok:
            ok_btn = QPushButton("确定")
            ok_btn.setObjectName("okButton")
            ok_btn.setDefault(default_button == self.Ok)
            ok_btn.clicked.connect(lambda: self.done(self.Ok))
            btn_layout.addWidget(ok_btn)
        
        if buttons & self.Cancel:
            cancel_btn = QPushButton("取消")
            cancel_btn.setObjectName("cancelButton")
            cancel_btn.setDefault(default_button == self.Cancel)
            cancel_btn.clicked.connect(lambda: self.done(self.Cancel))
            btn_layout.addWidget(cancel_btn)
        
        content_layout.addWidget(btn_widget)
        
        main_layout.addWidget(self.content_widget)
    
    def get_icon_pixmap(self, size=20):
        """获取图标"""
        from PySide6.QtWidgets import QStyle
        
        style = self.style()
        if self.icon_type == self.Information:
            return style.standardIcon(QStyle.SP_MessageBoxInformation).pixmap(size, size)
        elif self.icon_type == self.Warning:
            return style.standardIcon(QStyle.SP_MessageBoxWarning).pixmap(size, size)
        elif self.icon_type == self.Critical:
            return style.standardIcon(QStyle.SP_MessageBoxCritical).pixmap(size, size)
        elif self.icon_type == self.Question:
            return style.standardIcon(QStyle.SP_MessageBoxQuestion).pixmap(size, size)
        else:
            return style.standardIcon(QStyle.SP_MessageBoxInformation).pixmap(size, size)
    
    def apply_shadow(self):
        """应用阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.content_widget.setGraphicsEffect(shadow)
    
    # ========== 鼠标拖动支持 ==========
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            # 检查是否在标题栏区域
            if event.position().y() <= 40:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动"""
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放"""
        self.drag_pos = None
    
    # ========== 静态方法（类似 QMessageBox） ==========
    @staticmethod
    def information(parent, title, text, buttons=Ok, default_button=Ok, min_width=300, min_height=150):
        """信息对话框"""
        dialog = MessageDialog(parent, MessageDialog.Information, title, text,
                              buttons, default_button, min_width, min_height)
        return dialog.exec()

    @staticmethod
    def warning(parent, title, text, buttons=Ok, default_button=Ok, min_width=300, min_height=150):
        """警告对话框"""
        dialog = MessageDialog(parent, MessageDialog.Warning, title, text,
                              buttons, default_button, min_width, min_height)
        return dialog.exec()

    @staticmethod
    def critical(parent, title, text, buttons=Ok, default_button=Ok, min_width=300, min_height=150):
        """错误对话框"""
        dialog = MessageDialog(parent, MessageDialog.Critical, title, text,
                              buttons, default_button, min_width, min_height)
        return dialog.exec()

    @staticmethod
    def question(parent, title, text, buttons=Yes | No, default_button=No, min_width=300, min_height=150):
        """确认对话框"""
        dialog = MessageDialog(parent, MessageDialog.Question, title, text,
                              buttons, default_button, min_width, min_height)
        return dialog.exec()
