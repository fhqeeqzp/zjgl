"""
项目编辑对话框
用于新建和编辑项目信息
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit,
    QPushButton, QFormLayout, QGroupBox, QMessageBox,
    QFileDialog, QWidget, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from ..logic.project_manager import ProjectManager
from ui import StyleSheetManager


class ProjectDialog(QDialog):
    """项目编辑对话框 - 无边框自定义标题栏"""

    def __init__(self, project_manager: ProjectManager, project_id: int = None,
                 theme_manager=None, parent=None):
        """
        初始化对话框
        :param project_manager: 项目管理器
        :param project_id: 项目ID（None表示新建）
        :param theme_manager: 主题管理器
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.project_manager = project_manager
        self.project_id = project_id
        self.theme_manager = theme_manager
        self.project = None
        self.drag_pos = None

        # 如果是编辑模式，加载项目数据
        if project_id:
            self.project = project_manager.get_project(project_id)

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

        # 应用主题
        if theme_manager:
            theme_manager.add_observer(self.apply_theme)
            self.apply_theme(theme_manager.get_theme())

    def setup_ui(self):
        """设置UI - 自定义标题栏"""
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建内容容器（带圆角和背景）
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 30)

        # ========== 自定义标题栏 ==========
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 0, 20, 0)
        title_bar_layout.setSpacing(10)

        # 标题
        title_text = "新建项目" if not self.project_id else "编辑项目"
        title = QLabel(title_text)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_bar_layout.addWidget(title)

        title_bar_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 32)
        close_btn.setFont(QFont("Microsoft YaHei", 14))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        title_bar_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # 分隔线
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)

        # ========== 表单内容区域 ==========
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setContentsMargins(30, 10, 30, 0)

        # 项目编码
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("留空自动生成")
        self.code_input.setReadOnly(True)

        code_layout = QHBoxLayout()
        code_layout.addWidget(self.code_input)
        self.manual_code_check = QPushButton("手动输入")
        self.manual_code_check.setCheckable(True)
        self.manual_code_check.setFixedWidth(80)
        self.manual_code_check.clicked.connect(self.on_manual_code_toggle)
        code_layout.addWidget(self.manual_code_check)

        form_layout.addRow("项目编码:", code_layout)

        # 项目名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入项目名称")
        form_layout.addRow("* 项目名称:", self.name_input)

        # 项目类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.project_manager.get_type_list())
        form_layout.addRow("项目类型:", self.type_combo)

        # 项目状态
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.project_manager.get_status_list())
        form_layout.addRow("项目状态:", self.status_combo)

        # 金额信息组
        amount_group = QGroupBox("金额信息")
        amount_layout = QGridLayout(amount_group)
        amount_layout.setSpacing(10)

        self.bid_spin = QDoubleSpinBox()
        self.bid_spin.setRange(0, 9999999999.99)
        self.bid_spin.setDecimals(2)
        self.bid_spin.setPrefix("¥ ")
        amount_layout.addWidget(QLabel("投标金额:"), 0, 0)
        amount_layout.addWidget(self.bid_spin, 0, 1)

        self.contract_spin = QDoubleSpinBox()
        self.contract_spin.setRange(0, 9999999999.99)
        self.contract_spin.setDecimals(2)
        self.contract_spin.setPrefix("¥ ")
        amount_layout.addWidget(QLabel("合同金额:"), 0, 2)
        amount_layout.addWidget(self.contract_spin, 0, 3)

        self.received_spin = QDoubleSpinBox()
        self.received_spin.setRange(0, 9999999999.99)
        self.received_spin.setDecimals(2)
        self.received_spin.setPrefix("¥ ")
        amount_layout.addWidget(QLabel("实收金额:"), 1, 0)
        amount_layout.addWidget(self.received_spin, 1, 1)

        self.paid_spin = QDoubleSpinBox()
        self.paid_spin.setRange(0, 9999999999.99)
        self.paid_spin.setDecimals(2)
        self.paid_spin.setPrefix("¥ ")
        amount_layout.addWidget(QLabel("实付金额:"), 1, 2)
        amount_layout.addWidget(self.paid_spin, 1, 3)

        form_layout.addRow(amount_group)

        # 日期信息组
        date_group = QGroupBox("日期信息")
        date_layout = QHBoxLayout(date_group)
        date_layout.setSpacing(20)

        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        start_layout.addWidget(self.start_date)
        date_layout.addLayout(start_layout)

        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("竣工日期:"))
        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.completion_date.setDate(QDate.currentDate())
        end_layout.addWidget(self.completion_date)
        date_layout.addLayout(end_layout)

        date_layout.addStretch()
        form_layout.addRow(date_group)

        # 附件信息组
        attachment_group = QGroupBox("附件信息")
        attachment_layout = QVBoxLayout(attachment_group)
        attachment_layout.setSpacing(10)

        bid_file_layout = QHBoxLayout()
        bid_file_layout.addWidget(QLabel("投标附件:"))
        self.bid_attachment = QLineEdit()
        self.bid_attachment.setReadOnly(True)
        bid_file_layout.addWidget(self.bid_attachment)
        self.bid_file_btn = QPushButton("选择文件")
        self.bid_file_btn.clicked.connect(lambda: self.select_file("bid"))
        bid_file_layout.addWidget(self.bid_file_btn)
        attachment_layout.addLayout(bid_file_layout)

        construction_file_layout = QHBoxLayout()
        construction_file_layout.addWidget(QLabel("施工附件:"))
        self.construction_attachment = QLineEdit()
        self.construction_attachment.setReadOnly(True)
        construction_file_layout.addWidget(self.construction_attachment)
        self.construction_file_btn = QPushButton("选择文件")
        self.construction_file_btn.clicked.connect(lambda: self.select_file("construction"))
        construction_file_layout.addWidget(self.construction_file_btn)
        attachment_layout.addLayout(construction_file_layout)

        form_layout.addRow(attachment_group)

        # 备注
        self.remark_input = QTextEdit()
        self.remark_input.setPlaceholderText("请输入备注信息...")
        self.remark_input.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remark_input)

        layout.addWidget(form_widget)

        layout.addStretch()

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(100, 40)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addSpacing(20)

        self.save_btn = QPushButton("保存")
        self.save_btn.setFixedSize(100, 40)
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        # 添加内容框架到主布局
        main_layout.addWidget(self.content_frame)

        # 如果是编辑模式，填充数据
        if self.project:
            self.load_project_data()
        else:
            self.code_input.setText(self.project_manager.generate_project_code())

    def load_project_data(self):
        """加载项目数据（编辑模式）"""
        if not self.project:
            return

        self.code_input.setText(self.project.project_code)
        self.name_input.setText(self.project.name)

        type_value = self.project.project_type.value if hasattr(self.project.project_type, 'value') else str(self.project.project_type)
        index = self.type_combo.findText(type_value)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        status_value = self.project.status.value if hasattr(self.project.status, 'value') else str(self.project.status)
        index = self.status_combo.findText(status_value)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        self.bid_spin.setValue(float(self.project.bid_amount))
        self.contract_spin.setValue(float(self.project.contract_amount))
        self.received_spin.setValue(float(self.project.received_amount))
        self.paid_spin.setValue(float(self.project.paid_amount))

        if self.project.start_date:
            self.start_date.setDate(QDate(self.project.start_date.year,
                                          self.project.start_date.month,
                                          self.project.start_date.day))
        if self.project.completion_date:
            self.completion_date.setDate(QDate(self.project.completion_date.year,
                                               self.project.completion_date.month,
                                               self.project.completion_date.day))

        self.bid_attachment.setText(self.project.bid_attachment)
        self.construction_attachment.setText(self.project.construction_attachment)
        self.remark_input.setPlainText(self.project.remark)

    def on_manual_code_toggle(self, checked):
        """切换手动输入编码模式"""
        self.code_input.setReadOnly(not checked)
        if not checked:
            self.code_input.setText(self.project_manager.generate_project_code())

    def select_file(self, file_type: str):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "",
            "所有文件 (*.*);;PDF文件 (*.pdf);;Word文档 (*.doc *.docx);;Excel表格 (*.xls *.xlsx)"
        )
        if file_path:
            if file_type == "bid":
                self.bid_attachment.setText(file_path)
            else:
                self.construction_attachment.setText(file_path)

    def on_save(self):
        """保存项目"""
        project_data = {
            'project_code': self.code_input.text().strip(),
            'name': self.name_input.text().strip(),
            'project_type': self.type_combo.currentText(),
            'status': self.status_combo.currentText(),
            'bid_amount': self.bid_spin.value(),
            'contract_amount': self.contract_spin.value(),
            'received_amount': self.received_spin.value(),
            'paid_amount': self.paid_spin.value(),
            'start_date': self.start_date.date().toString('yyyy-MM-dd'),
            'completion_date': self.completion_date.date().toString('yyyy-MM-dd'),
            'bid_attachment': self.bid_attachment.text(),
            'construction_attachment': self.construction_attachment.text(),
            'remark': self.remark_input.toPlainText().strip(),
        }

        if not project_data['name']:
            QMessageBox.warning(self, "验证失败", "项目名称不能为空")
            self.name_input.setFocus()
            return

        if self.project_id:
            success, msg = self.project_manager.update_project(self.project_id, project_data)
        else:
            success, msg = self.project_manager.create_project(project_data)

        if success:
            QMessageBox.information(self, "成功", "保存成功")
            self.accept()
        else:
            QMessageBox.critical(self, "失败", f"保存失败: {msg}")

    def apply_theme(self, theme: dict):
        """应用主题"""
        # 设置内容框架样式（圆角背景）
        self.content_frame.setStyleSheet(f"""
            QFrame#contentFrame {{
                background-color: {theme['content_bg']};
                border-radius: 10px;
                border: 1px solid {theme['border']};
            }}
        """)

        # 应用对话框内部样式
        self.content_frame.setStyleSheet(self.content_frame.styleSheet() + StyleSheetManager.get_project_dialog_style(theme))

    # ========== 鼠标拖动支持 ==========
    def mousePressEvent(self, event):
        """鼠标按下 - 开始拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
