"""
投标编辑对话框
用于新建和编辑投标信息 - 使用 QSS 主题
"""
import os
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QGroupBox,
    QFileDialog,
    QWidget,
    QGridLayout,
    QFrame,
    QPushButton
)

from ui.message_dialog import MessageDialog
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from ..logic.bidding_manager import BiddingManager
from ui.fluent_widgets import (
    LineEdit, ComboBox, DateEdit, TextEdit,
    PushButton, PrimaryPushButton
)


class BiddingDialog(QDialog):
    """投标编辑对话框 - 无边框自定义标题栏，使用 QSS 主题"""

    def __init__(self, bidding_manager: BiddingManager, bidding_id: int = None,
                 theme_manager=None, parent=None):
        """
        初始化对话框
        :param bidding_manager: 投标管理器
        :param bidding_id: 投标ID（None表示新建）
        :param theme_manager: 主题管理器
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("biddingDialog")
        self.bidding_manager = bidding_manager
        self.bidding_id = bidding_id
        self.theme_manager = theme_manager
        self.bidding = None
        self.drag_pos = None
        self.parsed_data = {}  # 存储从Word解析的数据
        self.current_file_path = ""  # 当前选中的文件路径
        self.wd_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "WD")
        self._is_loading_data = False  # 标志：是否正在加载数据（防止编辑时自动触发解析）

        # 如果是编辑模式，加载投标数据
        if bidding_id:
            self.bidding = bidding_manager.get_bidding(bidding_id)

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

        # 应用主题
        if theme_manager:
            theme_manager.add_observer(self.on_theme_changed)

    def setup_ui(self):
        """设置UI - 自定义标题栏"""
        self.setMinimumWidth(700)
        self.setMinimumHeight(550)

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
        title_text = "新建投标" if not self.bidding_id else "编辑投标"
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

        # 选择项目（仅新建时）
        if not self.bidding_id:
            project_layout = QHBoxLayout()
            self.project_combo = ComboBox()
            self.project_combo.setMinimumWidth(400)
            self.project_combo.currentIndexChanged.connect(self.on_project_changed)
            project_layout.addWidget(self.project_combo)
            form_layout.addRow("* 选择项目:", project_layout)

            # 加载投标阶段的项目
            self.load_bidding_projects()

        # 投标编码（自动生成，只读）
        self.code_input = LineEdit()
        self.code_input.setReadOnly(True)
        self.code_input.setPlaceholderText("选择项目后自动生成")
        form_layout.addRow("投标编码:", self.code_input)

        # ========== 招标文件上传区域 ==========
        tender_group = QGroupBox("招标文件（Word文档）")
        tender_layout = QVBoxLayout(tender_group)
        tender_layout.setSpacing(10)

        upload_layout = QHBoxLayout()

        # 文件选择下拉框（显示已有文件列表）
        self.file_combo = ComboBox()
        self.file_combo.setMinimumWidth(300)
        self.file_combo.currentIndexChanged.connect(self.on_file_selected)
        upload_layout.addWidget(self.file_combo)

        self.upload_btn = PushButton("📁 选择文件")
        self.upload_btn.setObjectName("secondaryButton")
        self.upload_btn.clicked.connect(self.on_upload_tender_doc)
        upload_layout.addWidget(self.upload_btn)

        # 重新识别按钮
        self.reparse_btn = PushButton("🔄 重新识别")
        self.reparse_btn.setObjectName("secondaryButton")
        self.reparse_btn.clicked.connect(self.on_reparse_document)
        upload_layout.addWidget(self.reparse_btn)

        tender_layout.addLayout(upload_layout)

        # 提取信息显示区域
        extract_info_layout = QGridLayout()
        extract_info_layout.setSpacing(10)

        # 招标编码
        self.tender_code_input = LineEdit()
        self.tender_code_input.setPlaceholderText("自动提取或手动填写")
        extract_info_layout.addWidget(QLabel("招标编码:"), 0, 0)
        extract_info_layout.addWidget(self.tender_code_input, 0, 1)

        # 投标名称
        self.bidding_name_input = LineEdit()
        self.bidding_name_input.setPlaceholderText("自动提取或手动填写")
        extract_info_layout.addWidget(QLabel("投标名称:"), 0, 2)
        extract_info_layout.addWidget(self.bidding_name_input, 0, 3)

        # 招标人
        self.tenderer_input = LineEdit()
        self.tenderer_input.setPlaceholderText("自动提取或手动填写")
        extract_info_layout.addWidget(QLabel("招标人:"), 1, 0)
        extract_info_layout.addWidget(self.tenderer_input, 1, 1)

        # 计划工期
        self.planned_duration_input = LineEdit()
        self.planned_duration_input.setPlaceholderText("自动提取或手动填写")
        extract_info_layout.addWidget(QLabel("计划工期:"), 1, 2)
        extract_info_layout.addWidget(self.planned_duration_input, 1, 3)

        # 投标保证金
        self.bid_bond_input = LineEdit()
        self.bid_bond_input.setPlaceholderText("自动提取或手动填写金额")
        extract_info_layout.addWidget(QLabel("投标保证金:"), 2, 0)
        extract_info_layout.addWidget(self.bid_bond_input, 2, 1)

        # 开标日期
        self.bid_deadline_input = DateEdit()
        extract_info_layout.addWidget(QLabel("开标日期:"), 2, 2)
        extract_info_layout.addWidget(self.bid_deadline_input, 2, 3)

        # 招标控制价
        self.control_price_input = LineEdit()
        self.control_price_input.setPlaceholderText("自动提取或手动填写金额")
        extract_info_layout.addWidget(QLabel("招标控制价:"), 3, 0)
        extract_info_layout.addWidget(self.control_price_input, 3, 1)

        tender_layout.addLayout(extract_info_layout)
        form_layout.addRow(tender_group)

        # 投标状态
        self.status_combo = ComboBox()
        self.status_combo.addItems(self.bidding_manager.get_status_list())
        form_layout.addRow("投标状态:", self.status_combo)

        # 备注
        self.remark_input = TextEdit()
        self.remark_input.setPlaceholderText("请输入备注信息...")
        self.remark_input.setMaximumHeight(60)
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
        if self.bidding:
            self.load_bidding_data()

    def load_bidding_projects(self):
        """加载投标阶段的项目列表"""
        projects = self.bidding_manager.get_bidding_projects()
        self.project_combo.clear()
        self.project_combo.addItem("请选择项目...", None)
        for project in projects:
            self.project_combo.addItem(project['display'], project)

    def on_project_changed(self, index):
        """项目选择改变时更新投标编码和文件列表"""
        # 确保 code_input 存在（仅在新建模式下）
        if not hasattr(self, 'code_input') or not self.code_input:
            return

        if index > 0:
            project = self.project_combo.currentData()
            if project:
                project_code = project['project_code']
                # 生成投标编码
                bidding_code = self.bidding_manager.generate_bidding_code(project_code)
                self.code_input.setText(bidding_code)
                # 加载该项目的投标附件文件列表
                self.load_existing_files()
        else:
            self.code_input.clear()
            # 清空文件列表
            self.file_combo.clear()
            self.file_combo.addItem("请选择招标文件...", None)

    def get_project_name_for_file(self) -> str:
        """获取当前选择的项目名称（用于文件夹命名）"""
        if self.bidding_id and self.bidding:
            # 编辑模式，从投标数据获取项目名称
            project = self.bidding_manager.project_manager.get_project(self.bidding.project_id) if self.bidding_manager.project_manager else None
            return project.name if project else "未知项目"
        elif hasattr(self, 'project_combo'):
            # 新建模式，从下拉框获取
            project = self.project_combo.currentData()
            return project['name'] if project else "未知项目"
        return "未知项目"

    def get_bid_attachment_folder(self) -> str:
        """获取投标附件文件夹路径"""
        project_name = self.get_project_name_for_file()
        folder_path = os.path.join(self.wd_base_path, project_name, "投标附件")
        # 确保文件夹存在
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def load_existing_files(self):
        """加载已有的文件列表到下拉框"""
        self.file_combo.clear()
        self.file_combo.addItem("请选择招标文件...", None)

        try:
            folder_path = self.get_bid_attachment_folder()
            if os.path.exists(folder_path):
                # 获取所有Word文件
                word_files = []
                for ext in ['*.doc', '*.docx']:
                    word_files.extend(Path(folder_path).glob(ext))

                for file_path in sorted(word_files):
                    file_name = file_path.name
                    self.file_combo.addItem(file_name, str(file_path))
        except Exception as e:
            pass  # print(f"加载文件列表失败: {e}")

    def on_file_selected(self, index):
        """下拉框选择文件时"""
        # 如果正在加载数据，不触发解析
        if self._is_loading_data:
            return

        if index > 0:
            file_path = self.file_combo.currentData()
            if file_path and os.path.exists(file_path):
                self.current_file_path = file_path
                # 解析文档
                self._parse_and_fill(file_path)

    def on_upload_tender_doc(self):
        """上传招标文件并保存到WD文件夹"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择招标文件", "",
            "Word文档 (*.doc *.docx);;所有文件 (*.*)"
        )
        if not file_path:
            return

        try:
            # 获取目标文件夹
            target_folder = self.get_bid_attachment_folder()

            # 复制文件到WD文件夹
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

            # 更新当前文件路径
            self.current_file_path = target_path

            # 刷新下拉框列表
            self.load_existing_files()

            # 选中新上传的文件
            for i in range(self.file_combo.count()):
                if self.file_combo.itemData(i) == target_path:
                    self.file_combo.setCurrentIndex(i)
                    break

            # 解析文档
            self._parse_and_fill(target_path)

            MessageDialog.information(self, "上传成功", f"文件已保存到:\n{target_path}")

        except Exception as e:
            MessageDialog.critical(self, "上传失败", f"文件保存失败: {e}")

    def on_reparse_document(self):
        """重新识别文档"""
        file_path = self.current_file_path
        if not file_path:
            # 尝试从下拉框获取
            file_path = self.file_combo.currentData()

        if not file_path or not os.path.exists(file_path):
            MessageDialog.warning(self, "提示", "请先选择招标文件")
            return

        # 清空之前提取的数据
        self.parsed_data = {}

        # 重新解析
        self._parse_and_fill(file_path)

    def _parse_and_fill(self, file_path: str):
        """解析文档并填充数据"""
        try:
            # 解析文档
            self.parsed_data = self.bidding_manager.parse_tender_document(file_path)
            # 填充提取的数据
            self.fill_parsed_data()
        except Exception as e:
            MessageDialog.critical(self, "解析失败", f"文档解析出错: {e}")

    def fill_parsed_data(self):
        """填充从Word解析的数据"""
        if self.parsed_data.get('tender_code'):
            self.tender_code_input.setText(self.parsed_data['tender_code'])

        if self.parsed_data.get('bidding_name'):
            self.bidding_name_input.setText(self.parsed_data['bidding_name'])

        if self.parsed_data.get('tenderer'):
            self.tenderer_input.setText(self.parsed_data['tenderer'])

        if self.parsed_data.get('planned_duration'):
            self.planned_duration_input.setText(self.parsed_data['planned_duration'])

        if self.parsed_data.get('bid_bond'):
            bid_bond = self.parsed_data['bid_bond']
            if isinstance(bid_bond, (int, float)):
                self.bid_bond_input.setText(f"{bid_bond:,.2f}")
            else:
                self.bid_bond_input.setText(str(bid_bond))

        if self.parsed_data.get('bid_deadline'):
            deadline = self.parsed_data['bid_deadline']
            if isinstance(deadline, str):
                from datetime import datetime
                try:
                    deadline = datetime.strptime(deadline, '%Y-%m-%d')
                except:
                    pass
            if hasattr(deadline, 'year'):
                self.bid_deadline_input.setDate(QDate(deadline.year, deadline.month, deadline.day))

        if self.parsed_data.get('control_price'):
            control_price = self.parsed_data['control_price']
            if isinstance(control_price, (int, float)):
                self.control_price_input.setText(f"{control_price:,.2f}")
            else:
                self.control_price_input.setText(str(control_price))

        # 显示提取结果提示
        self._show_parse_result_dialog()

    def load_bidding_data(self):
        """加载投标数据（编辑模式）"""
        if not self.bidding:
            return

        # 设置标志，防止加载数据时触发自动解析
        self._is_loading_data = True

        try:
            self.code_input.setText(self.bidding.bidding_code)
            self.tender_code_input.setText(self.bidding.tender_code)
            self.bidding_name_input.setText(self.bidding.bidding_name)
            self.tenderer_input.setText(self.bidding.tenderer)
            self.planned_duration_input.setText(self.bidding.planned_duration)
            self.bid_bond_input.setText(f"{self.bidding.bid_bond:,.2f}" if self.bidding.bid_bond else "")
            self.control_price_input.setText(f"{self.bidding.control_price:,.2f}" if self.bidding.control_price else "")
            self.remark_input.setPlainText(self.bidding.remark)

            # 加载文件列表到下拉框
            self.load_existing_files()

            # 如果有已保存的文件路径，选中它
            if self.bidding.tender_doc_path and os.path.exists(self.bidding.tender_doc_path):
                self.current_file_path = self.bidding.tender_doc_path
                # 在下拉框中查找并选中
                for i in range(self.file_combo.count()):
                    if self.file_combo.itemData(i) == self.bidding.tender_doc_path:
                        self.file_combo.setCurrentIndex(i)
                        break
                else:
                    # 如果下拉框中没有，添加并选中
                    file_name = os.path.basename(self.bidding.tender_doc_path)
                    self.file_combo.addItem(file_name, self.bidding.tender_doc_path)
                    self.file_combo.setCurrentIndex(self.file_combo.count() - 1)

            if self.bidding.bid_deadline:
                self.bid_deadline_input.setDate(QDate(
                    self.bidding.bid_deadline.year,
                    self.bidding.bid_deadline.month,
                    self.bidding.bid_deadline.day
                ))

            status_value = self.bidding.status.value if hasattr(self.bidding.status, 'value') else str(self.bidding.status)
            index = self.status_combo.findText(status_value)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        finally:
            # 重置标志
            self._is_loading_data = False

    def _show_parse_result_dialog(self):
        """显示文档解析结果对话框（使用富文本格式）"""
        # 字段映射：内部字段名 -> 显示名称
        field_names = {
            'tender_code': '招标编码',
            'bidding_name': '投标名称',
            'tenderer': '招标人',
            'planned_duration': '计划工期',
            'bid_bond': '保证金',
            'bid_deadline': '开标日期',
            'control_price': '控制价',
        }

        # 分类成功和未成功提取的字段
        success_fields = []
        failed_fields = []

        for field, display_name in field_names.items():
            if self.parsed_data.get(field):
                success_fields.append(display_name)
            else:
                failed_fields.append(display_name)

        # 创建自定义无边框对话框
        self._show_custom_parse_dialog(success_fields, failed_fields)

    def _show_custom_parse_dialog(self, success_fields: list, failed_fields: list):
        """显示自定义无边框解析结果对话框"""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setFixedWidth(450)

        # 主布局
        main_layout = QVBoxLayout(dialog)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 内容框架
        content_frame = QFrame()
        content_frame.setObjectName("cardFrame")
        layout = QVBoxLayout(content_frame)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)

        # 标题栏（可拖动）
        title_label = QLabel("📄 文档解析完成")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # 成功提取信息
        if success_fields:
            success_title = QLabel("✅ 成功提取信息：")
            success_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
            success_title.setObjectName("successTitleLabel")
            layout.addWidget(success_title)

            success_content = QLabel("、".join(success_fields))
            success_content.setFont(QFont("Microsoft YaHei", 11))
            success_content.setObjectName("successContentLabel")
            success_content.setWordWrap(True)
            layout.addWidget(success_content)

        # 未成功提取信息
        if failed_fields:
            failed_title = QLabel("❌ 未成功提取信息：")
            failed_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
            failed_title.setObjectName("failedTitleLabel")
            layout.addWidget(failed_title)

            failed_content = QLabel("、".join(failed_fields))
            failed_content.setFont(QFont("Microsoft YaHei", 11))
            failed_content.setObjectName("failedContentLabel")
            failed_content.setWordWrap(True)
            layout.addWidget(failed_content)

        # 提示信息
        if failed_fields:
            tip_label = QLabel("⚠️ 未提取内容需要您手动填写！")
            tip_label.setFont(QFont("Microsoft YaHei", 10))
            tip_label.setObjectName("warningTipLabel")
            tip_label.setWordWrap(True)
            layout.addWidget(tip_label)

        layout.addSpacing(10)

        # 确定按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = PrimaryPushButton("确定")
        ok_btn.setFixedSize(100, 35)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        main_layout.addWidget(content_frame)

        # 启用拖动
        def mouse_press_event(event):
            if event.button() == Qt.LeftButton:
                dialog.drag_pos = event.globalPos() - dialog.frameGeometry().topLeft()
                event.accept()

        def mouse_move_event(event):
            if event.buttons() == Qt.LeftButton and hasattr(dialog, 'drag_pos'):
                dialog.move(event.globalPos() - dialog.drag_pos)
                event.accept()

        content_frame.mousePressEvent = mouse_press_event
        content_frame.mouseMoveEvent = mouse_move_event

        dialog.exec_()

    def on_save(self):
        """保存投标"""
        # 获取项目信息
        project_id = None
        project_code = ""
        if not self.bidding_id:
            project = self.project_combo.currentData()
            if not project:
                MessageDialog.warning(self, "验证失败", "请选择项目")
                self.project_combo.setFocus()
                return
            project_id = project['id']
            project_code = project['project_code']
        else:
            project_id = self.bidding.project_id
            project_code = self.bidding.project_code

        # 解析金额文本（移除逗号和货币符号）
        def parse_amount(text):
            if not text:
                return 0.0
            # 移除逗号、空格、货币符号
            cleaned = text.replace(',', '').replace(' ', '').replace('¥', '').replace('￥', '')
            try:
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                return 0.0

        bidding_data = {
            'project_id': project_id,
            'project_code': project_code,
            'bidding_code': self.code_input.text().strip(),
            'tender_code': self.tender_code_input.text().strip(),
            'bidding_name': self.bidding_name_input.text().strip(),
            'tenderer': self.tenderer_input.text().strip(),
            'planned_duration': self.planned_duration_input.text().strip(),
            'bid_bond': parse_amount(self.bid_bond_input.text()),
            'bid_deadline': self.bid_deadline_input.date().toString('yyyy-MM-dd'),
            'control_price': parse_amount(self.control_price_input.text()),
            'status': self.status_combo.currentText(),
            'tender_doc_path': self.current_file_path,
            'remark': self.remark_input.toPlainText().strip(),
        }

        if not bidding_data['bidding_code']:
            MessageDialog.warning(self, "验证失败", "投标编码不能为空")
            return

        if self.bidding_id:
            success, msg = self.bidding_manager.update_bidding(self.bidding_id, bidding_data)
        else:
            success, msg = self.bidding_manager.create_bidding(bidding_data)

        if success:
            MessageDialog.information(self, "成功", "保存成功")
            self.accept()
        else:
            MessageDialog.critical(self, "失败", f"保存失败: {msg}")

    def on_theme_changed(self, theme: dict):
        """主题变化回调 - QSS 已全局加载"""
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
