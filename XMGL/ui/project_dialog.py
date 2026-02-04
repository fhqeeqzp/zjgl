"""
项目编辑对话框
用于新建和编辑项目信息 - 使用 QSS 主题
"""
import os
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFormLayout, QGroupBox, QMessageBox,
    QFileDialog, QWidget, QGridLayout, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from ..logic.project_manager import ProjectManager
from ui.fluent_widgets import (
    LineEdit, ComboBox, DateEdit, TextEdit,
    PushButton, PrimaryPushButton
)


class ProjectDialog(QDialog):
    """项目编辑对话框 - 无边框自定义标题栏，使用 QSS 主题"""

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

        # WD文件夹基础路径
        self.wd_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "WD")

        # 存储附件文件列表
        self.bid_files = []  # 投标附件文件列表
        self.construction_files = []  # 施工附件文件列表

        # 如果是编辑模式，加载项目数据
        if project_id:
            self.project = project_manager.get_project(project_id)

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

        # 应用主题
        if theme_manager:
            theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        """设置UI - 自定义标题栏"""
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建内容容器
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        layout = QVBoxLayout(self.content_frame)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 20)

        # ========== 自定义标题栏 ==========
        title_bar = QFrame()
        title_bar.setObjectName("titleBarFrame")
        title_bar.setFixedHeight(50)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 0, 20, 0)
        title_bar_layout.setSpacing(10)

        # 标题
        title_text = "新建项目" if not self.project_id else "编辑项目"
        title = QLabel(title_text)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setObjectName("titleLabel")
        title_bar_layout.addWidget(title)

        title_bar_layout.addStretch()

        # 关闭按钮 - 使用QSS样式
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.setProperty("class", "titlebar-button")
        close_btn.setFixedSize(46, 32)
        close_btn.setFont(QFont("Microsoft YaHei", 14))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        title_bar_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # ========== 表单内容区域 ==========
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setContentsMargins(30, 10, 30, 0)

        # 项目编码
        self.code_input = LineEdit()
        self.code_input.setPlaceholderText("留空自动生成")
        self.code_input.setReadOnly(True)

        code_layout = QHBoxLayout()
        code_layout.addWidget(self.code_input)
        self.manual_code_check = PushButton("手动输入")
        self.manual_code_check.setObjectName("secondaryButton")
        self.manual_code_check.setCheckable(True)
        self.manual_code_check.setFixedWidth(80)
        self.manual_code_check.clicked.connect(self.on_manual_code_toggle)
        code_layout.addWidget(self.manual_code_check)

        form_layout.addRow("项目编码:", code_layout)

        # 项目名称
        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("请输入项目名称")
        form_layout.addRow("* 项目名称:", self.name_input)

        # 项目类型和状态水平布局
        type_status_layout = QHBoxLayout()
        
        # 项目类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("项目类型:"))
        self.type_combo = ComboBox()
        self.type_combo.addItems(self.project_manager.get_type_list())
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        
        # 项目状态
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("项目状态:"))
        self.status_combo = ComboBox()
        self.status_combo.addItems(self.project_manager.get_status_list())
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        
        type_status_layout.addLayout(type_layout)
        type_status_layout.addLayout(status_layout)
        form_layout.addRow(type_status_layout)

        # 日期信息组
        date_group = QGroupBox("日期信息")
        date_layout = QHBoxLayout(date_group)
        date_layout.setSpacing(20)

        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("开始日期:"))
        self.start_date = DateEdit()
        start_layout.addWidget(self.start_date)
        date_layout.addLayout(start_layout)

        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("竣工日期:"))
        self.completion_date = DateEdit()
        end_layout.addWidget(self.completion_date)
        date_layout.addLayout(end_layout)

        date_layout.addStretch()
        form_layout.addRow(date_group)

        # ========== 附件区域（投标附件和施工附件并排） ==========
        attachment_layout = QHBoxLayout()
        attachment_layout.setSpacing(20)

        # 投标附件区域
        bid_group = QGroupBox("投标附件")
        bid_layout = QVBoxLayout(bid_group)
        bid_layout.setSpacing(10)

        # 投标附件表格
        self.bid_table = QTableWidget()
        self.bid_table.setColumnCount(3)
        self.bid_table.setHorizontalHeaderLabels(["序号", "文件名", "操作"])
        self.bid_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bid_table.verticalHeader().setVisible(False)
        self.bid_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bid_table.setMaximumHeight(150)

        # 设置列宽
        header = self.bid_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.bid_table.setColumnWidth(0, 50)
        self.bid_table.setColumnWidth(2, 60)

        bid_layout.addWidget(self.bid_table)

        # 投标附件上传按钮
        self.bid_upload_btn = PushButton("➕ 上传文件")
        self.bid_upload_btn.setObjectName("secondaryButton")
        self.bid_upload_btn.clicked.connect(lambda: self.upload_file("bid"))
        bid_layout.addWidget(self.bid_upload_btn)

        attachment_layout.addWidget(bid_group, 1)

        # 施工附件区域
        construction_group = QGroupBox("施工附件")
        construction_layout = QVBoxLayout(construction_group)
        construction_layout.setSpacing(10)

        # 施工附件表格
        self.construction_table = QTableWidget()
        self.construction_table.setColumnCount(3)
        self.construction_table.setHorizontalHeaderLabels(["序号", "文件名", "操作"])
        self.construction_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.construction_table.verticalHeader().setVisible(False)
        self.construction_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.construction_table.setMaximumHeight(150)

        # 设置列宽
        header2 = self.construction_table.horizontalHeader()
        header2.setSectionResizeMode(0, QHeaderView.Fixed)
        header2.setSectionResizeMode(1, QHeaderView.Stretch)
        header2.setSectionResizeMode(2, QHeaderView.Fixed)
        self.construction_table.setColumnWidth(0, 50)
        self.construction_table.setColumnWidth(2, 60)

        construction_layout.addWidget(self.construction_table)

        # 施工附件上传按钮
        self.construction_upload_btn = PushButton("➕ 上传文件")
        self.construction_upload_btn.setObjectName("secondaryButton")
        self.construction_upload_btn.clicked.connect(lambda: self.upload_file("construction"))
        construction_layout.addWidget(self.construction_upload_btn)

        attachment_layout.addWidget(construction_group, 1)

        form_layout.addRow(attachment_layout)

        # 备注
        self.remark_input = TextEdit()
        self.remark_input.setPlaceholderText("请输入备注信息...")
        self.remark_input.setMaximumHeight(80)
        form_layout.addRow("备注:", self.remark_input)

        layout.addWidget(form_widget)

        layout.addStretch()

        # 按钮区域（居中）
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addSpacing(20)

        self.save_btn = PrimaryPushButton("保存")
        self.save_btn.setFixedSize(100, 35)
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)

        btn_layout.addStretch()

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

        if self.project.start_date:
            self.start_date.setDate(QDate(self.project.start_date.year,
                                          self.project.start_date.month,
                                          self.project.start_date.day))
        if self.project.completion_date:
            self.completion_date.setDate(QDate(self.project.completion_date.year,
                                               self.project.completion_date.month,
                                               self.project.completion_date.day))

        # 加载附件文件列表
        self.load_attachment_files()

        self.remark_input.setPlainText(self.project.remark)

    def on_manual_code_toggle(self, checked):
        """切换手动输入编码模式"""
        self.code_input.setReadOnly(not checked)
        if not checked:
            self.code_input.setText(self.project_manager.generate_project_code())

    def get_project_name(self) -> str:
        """获取项目名称"""
        if self.project_id and self.project:
            return self.project.name
        return self.name_input.text().strip() or "新建项目"

    def get_attachment_folder(self, file_type: str) -> str:
        """获取附件文件夹路径"""
        project_name = self.get_project_name()
        folder_name = "投标附件" if file_type == "bid" else "施工附件"
        folder_path = os.path.join(self.wd_base_path, project_name, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def load_attachment_files(self):
        """加载附件文件列表到表格"""
        # 加载投标附件
        self.bid_files = self._get_files_from_folder("bid")
        self._refresh_table(self.bid_table, self.bid_files, "bid")

        # 加载施工附件
        self.construction_files = self._get_files_from_folder("construction")
        self._refresh_table(self.construction_table, self.construction_files, "construction")

    def _get_files_from_folder(self, file_type: str) -> list:
        """从文件夹获取文件列表"""
        folder_path = self.get_attachment_folder(file_type)
        if not os.path.exists(folder_path):
            return []

        files = []
        for item in sorted(os.listdir(folder_path)):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                files.append({
                    'name': item,
                    'path': item_path
                })
        return files

    def _refresh_table(self, table: QTableWidget, files: list, file_type: str):
        """刷新表格显示"""
        table.setRowCount(len(files))
        for row, file_info in enumerate(files):
            # 序号
            item_no = QTableWidgetItem(str(row + 1))
            item_no.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_no)

            # 文件名
            item_name = QTableWidgetItem(file_info['name'])
            item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 1, item_name)

            # 删除按钮
            delete_btn = PushButton("🗑️")
            delete_btn.setFixedSize(40, 28)
            delete_btn.setObjectName("dangerButton")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, r=row, t=file_type: self.delete_file(r, t))
            table.setCellWidget(row, 2, delete_btn)

    def upload_file(self, file_type: str):
        """上传文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择文件", "",
            "所有文件 (*.*);;PDF文件 (*.pdf);;Word文档 (*.doc *.docx);;Excel表格 (*.xls *.xlsx)"
        )

        if not file_paths:
            return

        try:
            target_folder = self.get_attachment_folder(file_type)
            uploaded_count = 0

            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(target_folder, file_name)

                # 如果文件已存在，添加序号
                counter = 1
                original_name, ext = os.path.splitext(file_name)
                while os.path.exists(target_path):
                    target_path = os.path.join(target_folder, f"{original_name}_{counter}{ext}")
                    counter += 1

                # 复制文件
                shutil.copy2(file_path, target_path)
                uploaded_count += 1

            # 刷新表格
            self.load_attachment_files()

            QMessageBox.information(self, "上传成功", f"成功上传 {uploaded_count} 个文件")

        except Exception as e:
            QMessageBox.critical(self, "上传失败", f"文件上传失败: {e}")

    def delete_file(self, row: int, file_type: str):
        """删除文件"""
        files = self.bid_files if file_type == "bid" else self.construction_files
        if row < 0 or row >= len(files):
            return

        file_info = files[row]
        file_name = file_info['name']

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除文件 [{file_name}] 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                file_path = file_info['path']
                if os.path.exists(file_path):
                    os.remove(file_path)

                # 刷新表格
                self.load_attachment_files()

                QMessageBox.information(self, "成功", "文件已删除")
            except Exception as e:
                QMessageBox.critical(self, "失败", f"删除失败: {e}")

    def on_save(self):
        """保存项目"""
        # 确保文件夹与项目名同步（如果项目名改变）
        self._sync_attachment_folders()

        project_data = {
            'project_code': self.code_input.text().strip(),
            'name': self.name_input.text().strip(),
            'project_type': self.type_combo.currentText(),
            'status': self.status_combo.currentText(),
            'start_date': self.start_date.date().toString('yyyy-MM-dd'),
            'completion_date': self.completion_date.date().toString('yyyy-MM-dd'),
            'bid_attachment': self.get_attachment_folder("bid"),
            'construction_attachment': self.get_attachment_folder("construction"),
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

    def _sync_attachment_folders(self):
        """同步附件文件夹（当项目名称改变时）"""
        if not self.project_id or not self.project:
            return

        old_name = self.project.name
        new_name = self.name_input.text().strip()

        if old_name == new_name or not new_name:
            return

        try:
            old_base_path = os.path.join(self.wd_base_path, old_name)
            new_base_path = os.path.join(self.wd_base_path, new_name)

            if os.path.exists(old_base_path) and not os.path.exists(new_base_path):
                # 重命名文件夹
                os.rename(old_base_path, new_base_path)
                print(f"附件文件夹已同步: {old_name} -> {new_name}")
        except Exception as e:
            print(f"同步附件文件夹失败: {e}")

    def on_theme_changed(self, theme: dict):
        """主题变化回调 - QSS 已全局加载"""
        # QSS 样式已通过 ThemeManager.apply_qss() 全局加载
        pass

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
