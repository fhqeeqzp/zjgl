"""
投标明细Excel导入对话框
用于从Excel文件导入明细数据，支持工作簿选择、列映射、数据预览
字段与汇总表类似，但针对明细数据优化
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

try:
    import openpyxl
    from openpyxl import load_workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QFrame,
    QSplitter,
    QWidget,
    QProgressBar,
    QTextEdit,
    QApplication,
    QScrollArea,
    QGridLayout,
    QFormLayout
)

from ui.message_dialog import MessageDialog
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

from ui.fluent_widgets import PushButton, PrimaryPushButton
from .excel_import_dialog import ColumnMappingWidget, ExcelLoadWorker


class ImportProgressDialog(QDialog):
    """导入进度对话框 - 显示导入进度和明细"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("正在导入数据...")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(800, 600)
        self.setModal(True)
        
        # 设置对象名以便QSS样式应用
        self.setObjectName("importProgressDialog")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 状态标签
        self.status_label = QLabel("正在准备导入...")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% (%v/%m)")
        layout.addWidget(self.progress_bar)
        
        # 当前行信息
        self.current_row_label = QLabel("")
        self.current_row_label.setObjectName("currentRowLabel")
        layout.addWidget(self.current_row_label)
        
        # 明细显示区域
        detail_label = QLabel("📋 导入明细（最近20行）：")
        detail_label.setObjectName("detailLabel")
        layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)
        
        # 统计信息
        self.stats_label = QLabel("已导入: 0 行")
        self.stats_label.setObjectName("statsLabel")
        layout.addWidget(self.stats_label)
        
        # 取消按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = PushButton("取消导入")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.clicked.connect(self.on_cancel)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.is_cancelled = False
        self.imported_count = 0
        self.error_count = 0
    
    def set_total_rows(self, total: int):
        """设置总行数"""
        self.progress_bar.setMaximum(total)
        self.total_rows = total
    
    def update_progress(self, current: int, row_data: dict = None):
        """更新进度"""
        self.progress_bar.setValue(current)
        
        percentage = (current / self.total_rows * 100) if self.total_rows > 0 else 0
        self.status_label.setText(f"正在导入... {percentage:.1f}%")
        
        if row_data:
            sequence = row_data.get('sequence', '')
            name = row_data.get('name', '')
            self.current_row_label.setText(f"当前行: {current}/{self.total_rows} - {sequence} {name[:30]}")
            self.add_detail_line(current, row_data)
        
        self.stats_label.setText(f"已导入: {self.imported_count} 行 | 错误: {self.error_count} 行")
        QApplication.processEvents()
    
    def add_detail_line(self, row_num: int, row_data: dict):
        """添加明细行"""
        sequence = row_data.get('sequence', '')
        name = row_data.get('name', '')
        level = row_data.get('level', 1)
        
        indent = "  " * (level - 1)
        line = f"[{row_num:4d}] {indent}{sequence:8s} {name[:40]}"
        
        self.detail_text.append(line)
        scrollbar = self.detail_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_cancel(self):
        """取消导入"""
        self.is_cancelled = True
        self.status_label.setText("正在取消...")
        self.status_label.setProperty("status", "error")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_completed(self, success_count: int, error_count: int):
        """设置完成状态"""
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText("✓ 导入完成")
        self.status_label.setProperty("status", "success")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.stats_label.setText(f"成功: {success_count} 行 | 错误: {error_count} 行")
        self.cancel_btn.setText("关闭")
        self.cancel_btn.setEnabled(True)

    def set_error(self, error_msg: str):
        """设置错误状态"""
        self.status_label.setText(f"✗ 导入失败")
        self.status_label.setProperty("status", "error")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.detail_text.append(f"\n错误: {error_msg}")
        self.cancel_btn.setText("关闭")


class DetailImportDialog(QDialog):
    """投标明细导入对话框"""
    
    # 字段定义: (字段标识, 字段显示名称, 是否必填, 匹配关键词列表)
    FIELD_DEFINITIONS = [
        ('sequence', '序号', False, [
            '序号', '编号', 'no', 'no.', 'number', 'id'
        ]),
        ('name', '分部分项工程名称', True, [
            '分部分项工程名称', '工程名称', '项目名称', '名称', '项目', '工程', 'name', 'item'
        ]),
        ('specification', '规格型号', False, [
            '规格型号', '规格', '型号', 'spec', 'specification', 'type', 'model'
        ]),
        ('description', '项目特征描述', False, [
            '项目特征描述', '特征描述', '项目特征', '描述', '特征', 'description',
            '工作内容', '内容', '工作', 'work content', 'content'
        ]),
        ('unit', '单位', False, [
            '单位', '计量单位', 'unit', '计量'
        ]),
        ('quantity', '工程量', False, [
            '工程量', '数量', 'quantity', 'amount', '工程数量'
        ]),
        ('unit_price', '综合单价', False, [
            '综合单价', '单价', 'unit price', 'price', '单价(元)'
        ]),
        ('labor_unit_price', '人工单价', False, [
            '人工单价', '人工费单价', '人工', 'labor price', 'labor unit price'
        ]),
        ('material_unit_price', '主材单价', False, [
            '主材单价', '材料单价', '材料费单价'
        ]),
        ('material_loss_rate', '主材损耗%', False, [
            '主材损耗', '材料损耗', '损耗率', '损耗%', '损耗'
        ]),
        ('auxiliary_unit_price', '辅材单价', False, [
            '辅材单价', '辅助材料单价', '辅材', 'auxiliary price'
        ]),
        ('machine_unit_price', '机械单价', False, [
            '机械单价', '机械费单价', '机械台班单价', '机械', 'machine price'
        ]),
        ('other_unit_price', '其他单价', False, [
            '其他单价', '其他费单价', '其他', 'other price'
        ]),
        # 合价由计算得出，不进行导入识别
        # ('total_price', '合价', False, [
        #     '合价', '总价', '金额', 'total', '合价(元)', '金额(元)'
        # ]),
        ('remark', '备注', False, [
            '备注', '说明', 'note', 'remark', '注释'
        ]),
    ]
    
    def __init__(self, excel_path: str, bidding_name: str = "", summary_name: str = "", parent=None):
        super().__init__(parent)
        self.excel_path = excel_path
        self.bidding_name = bidding_name
        self.summary_name = summary_name  # 汇总项名称（工程项目及费用名称）
        self.sheet_names = []
        self.headers = []
        self.sample_data = []
        self.preview_rows = []
        self.header_row_index = 0
        self.header_row_count = 1  # 表头行数（支持多行表头）
        self.load_worker = None
        self.current_sheet_name = None
        self.drag_pos = None

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(1000, 800)

        self.setup_ui()
        self.load_excel_async()

    def setup_ui(self):
        """设置UI - 自定义标题栏"""
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
        title = QLabel("投标明细导入 - 列映射配置")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setObjectName("titleLabel")
        title_bar_layout.addWidget(title)

        title_bar_layout.addStretch()

        # 关闭按钮
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

        # 文件信息
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_label = QLabel(f"📄 文件: {os.path.basename(self.excel_path)}")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        form_layout.addRow("文件:", info_frame)

        # 工作簿选择
        sheet_layout = QHBoxLayout()
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(180)
        self.sheet_combo.currentIndexChanged.connect(self.on_sheet_changed)
        sheet_layout.addWidget(self.sheet_combo)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        sheet_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        sheet_layout.addWidget(self.status_label)

        sheet_layout.addStretch()
        form_layout.addRow("工作簿:", sheet_layout)

        # 表头行选择
        header_row_layout = QHBoxLayout()
        self.header_row_combo = QComboBox()
        self.header_row_combo.setMinimumWidth(250)
        self.header_row_combo.setToolTip("选择哪一行作为表头")
        self.header_row_combo.currentIndexChanged.connect(self.on_header_row_changed)
        header_row_layout.addWidget(self.header_row_combo)

        header_row_hint = QLabel("💡 提示: 请选择包含列标题的行")
        header_row_hint.setObjectName("hintLabel")
        header_row_layout.addWidget(header_row_hint)

        header_row_layout.addStretch()
        form_layout.addRow("表头行:", header_row_layout)

        layout.addWidget(form_widget)

        # 分割器
        splitter = QSplitter(Qt.Vertical)

        # 上半部分：列映射（带滚动条）
        mapping_widget = QWidget()
        mapping_layout = QVBoxLayout(mapping_widget)
        mapping_layout.setContentsMargins(0, 0, 0, 0)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setObjectName("mappingScrollArea")

        # 列映射容器（两列布局）
        mapping_container = QWidget()
        mapping_container.setObjectName("mappingContainer")
        mapping_inner_layout = QGridLayout(mapping_container)
        mapping_inner_layout.setContentsMargins(15, 15, 15, 15)
        mapping_inner_layout.setSpacing(10)
        mapping_inner_layout.setColumnStretch(0, 1)
        mapping_inner_layout.setColumnStretch(1, 1)

        # 创建列映射组件（两列布局）
        self.mapping_widgets = {}
        row = 0
        col = 0
        for field_key, field_name, is_required, _ in self.FIELD_DEFINITIONS:
            display_name = f"* {field_name}" if is_required else field_name
            widget = ColumnMappingWidget(field_key, display_name)
            widget.mapping_changed.connect(self.on_mapping_changed)
            self.mapping_widgets[field_key] = widget
            mapping_inner_layout.addWidget(widget, row, col)

            col += 1
            if col >= 2:  # 每行2个
                col = 0
                row += 1

        scroll_area.setWidget(mapping_container)
        mapping_layout.addWidget(scroll_area)

        # 按钮区域（固定居中）
        btn_frame = QFrame()
        btn_frame.setObjectName("buttonFrame")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(20)

        auto_btn = PushButton("🔍 智能识别列")
        auto_btn.setToolTip("根据表头名称自动匹配列")
        auto_btn.setFixedSize(120, 35)
        auto_btn.clicked.connect(self.auto_detect_columns)
        btn_layout.addWidget(auto_btn)

        clear_btn = PushButton("🗑️ 清除选择")
        clear_btn.setFixedSize(120, 35)
        clear_btn.clicked.connect(self.clear_mappings)
        btn_layout.addWidget(clear_btn)

        mapping_layout.addWidget(btn_frame)
        splitter.addWidget(mapping_widget)

        # 下半部分：原始数据预览（增加高度）
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(250)

        preview_layout.addWidget(self.preview_table)
        splitter.addWidget(preview_widget)
        
        splitter.setSizes([350, 400])
        layout.addWidget(splitter)

        layout.addStretch()

        # 按钮区域（居中）
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = PushButton("取消")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addSpacing(20)

        self.import_btn = PrimaryPushButton("确认导入")
        self.import_btn.setFixedSize(100, 35)
        self.import_btn.clicked.connect(self.on_import)
        btn_layout.addWidget(self.import_btn)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # 添加内容框架到主布局
        main_layout.addWidget(self.content_frame)
    
    def load_excel_async(self):
        """异步加载Excel文件"""
        if not OPENPYXL_AVAILABLE:
            MessageDialog.warning(self, "提示", "请先安装openpyxl: pip install openpyxl")
            self.reject()
            return
        
        self.progress_bar.show()
        self.status_label.setText("正在加载Excel文件...")
        self.import_btn.setEnabled(False)
        
        self.load_worker = ExcelLoadWorker(self.excel_path)
        self.load_worker.loaded.connect(self.on_excel_loaded)
        self.load_worker.sheet_data_loaded.connect(self.on_sheet_data_loaded)
        self.load_worker.error.connect(self.on_load_error)
        self.load_worker.start()
    
    def on_excel_loaded(self, sheet_names: list):
        """Excel文件加载完成回调 - 智能选择工作簿"""
        self.sheet_names = sheet_names
        
        self.sheet_combo.clear()
        for name in sheet_names:
            self.sheet_combo.addItem(name)
        
        if sheet_names:
            # 智能选择工作簿：优先选择包含"清单"、"明细"、"分部分项"等关键词的工作簿
            preferred_keywords = ['清单', '明细', '分部分项', '工程', '项目', 'data', 'sheet']
            selected_idx = 0
            best_score = 0
            
            for idx, name in enumerate(sheet_names):
                name_lower = name.lower()
                score = 0
                for keyword in preferred_keywords:
                    if keyword in name_lower:
                        score += 1
                # 默认工作簿名称（如Sheet1）得分较低
                if 'sheet' in name_lower and any(c.isdigit() for c in name):
                    score -= 0.5
                    
                if score > best_score:
                    best_score = score
                    selected_idx = idx
            
            self.current_sheet_name = sheet_names[selected_idx]
            self.sheet_combo.setCurrentIndex(selected_idx)
            # print(f"[工作簿选择] 自动选择: {self.current_sheet_name} (得分: {best_score})")
            self.load_worker.set_sheet(self.current_sheet_name)

    def on_sheet_data_loaded(self, preview_rows: list, _, row_count: int):
        """工作表数据加载完成回调"""
        # print(f"[明细导入] 加载完成，共 {row_count} 行预览数据")

        self.preview_rows = preview_rows

        # 填充表头行选择下拉框
        self.header_row_combo.clear()
        for i, row in enumerate(preview_rows):
            preview_text = " | ".join(str(cell)[:10] for cell in row[:3] if cell)
            if len(preview_text) > 30:
                preview_text = preview_text[:30] + "..."
            self.header_row_combo.addItem(f"第 {i+1} 行: {preview_text}", i)

        # 自动识别表头行
        detected_row = self._detect_header_row(preview_rows)
        self.header_row_index = detected_row
        self.header_row_combo.setCurrentIndex(detected_row)

        self.progress_bar.hide()
        self.import_btn.setEnabled(True)

        self._update_header_and_data()
        
        # 更新状态标签，显示表头行数
        self.status_label.setText(f"✓ 已加载 {row_count} 行预览数据 | 表头: {self.header_row_count} 行")

        if self.load_worker:
            self.load_worker.stop()
            self.load_worker = None

    def on_header_row_changed(self, index):
        """表头行选择改变"""
        if index >= 0 and self.preview_rows:
            self.header_row_index = index
            self._update_header_and_data()

    def _update_header_and_data(self):
        """根据选择的表头行更新数据 - 支持多行表头合并"""
        if not self.preview_rows or self.header_row_index >= len(self.preview_rows):
            return

        # 检查是否需要合并多行表头
        # 如果当前行和下一行都有内容，可能是多行表头
        merged_headers = []
        current_row = self.preview_rows[self.header_row_index]
        
        # 尝试合并后续2-3行作为完整表头
        rows_to_merge = [current_row]
        for i in range(1, 3):  # 最多合并后续2行
            if self.header_row_index + i < len(self.preview_rows):
                next_row = self.preview_rows[self.header_row_index + i]
                # 如果下一行有非空单元格，可能是多行表头的一部分
                if any(cell and str(cell).strip() for cell in next_row):
                    rows_to_merge.append(next_row)
                else:
                    break
        
        # 合并多行表头
        max_cols = max(len(row) for row in rows_to_merge)
        for col_idx in range(max_cols):
            header_parts = []
            for row in rows_to_merge:
                if col_idx < len(row) and row[col_idx]:
                    cell_val = str(row[col_idx]).strip()
                    if cell_val and cell_val not in header_parts:
                        header_parts.append(cell_val)
            
            # 合并表头部分（如"人工费" + "单价" = "人工费单价"）
            if header_parts:
                merged_headers.append(''.join(header_parts))
            else:
                merged_headers.append('')
        
        self.headers = merged_headers
        self.header_row_count = len(rows_to_merge)  # 记录表头行数
        self.sample_data = self.preview_rows[self.header_row_index + len(rows_to_merge):]
        
        # print(f"[表头识别] 合并了 {len(rows_to_merge)} 行表头: {self.headers[:5]}...")

        self.update_mapping_widgets()
        self.update_raw_preview()
        self.auto_detect_columns()
    
    def on_load_error(self, error_msg: str):
        """加载错误回调"""
        self.progress_bar.hide()
        self.status_label.setText("加载失败")
        self.import_btn.setEnabled(True)
        MessageDialog.critical(self, "错误", f"无法加载Excel文件:\n{error_msg}")
        
        if self.load_worker:
            self.load_worker.stop()
            self.load_worker = None
    
    def load_sheet_async(self, sheet_name: str):
        """异步加载指定工作表"""
        if not sheet_name:
            return
        
        self.current_sheet_name = sheet_name
        
        self.progress_bar.show()
        self.status_label.setText(f"正在加载工作表: {sheet_name}...")
        self.import_btn.setEnabled(False)
        
        self.load_worker = ExcelLoadWorker(self.excel_path)
        self.load_worker.sheet_data_loaded.connect(self.on_sheet_data_loaded)
        self.load_worker.error.connect(self.on_load_error)
        self.load_worker.set_sheet(sheet_name)
        self.load_worker.start()
    
    def update_mapping_widgets(self):
        """更新列映射组件"""
        for widget in self.mapping_widgets.values():
            widget.set_headers(self.headers, self.sample_data)
    
    def update_raw_preview(self):
        """更新原始数据预览"""
        if not self.headers:
            return
        
        self.preview_table.clear()
        self.preview_table.setColumnCount(len(self.headers))
        self.preview_table.setHorizontalHeaderLabels(self.headers)
        
        row_count = min(5, len(self.sample_data))
        self.preview_table.setRowCount(row_count)
        
        for row_idx, row_data in enumerate(self.sample_data[:5]):
            for col_idx, value in enumerate(row_data):
                if value is None:
                    value = ""
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.preview_table.setItem(row_idx, col_idx, item)
        
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
    
    def _normalize_text(self, text: str) -> str:
        """标准化文本"""
        if not text:
            return ""
        text = str(text).strip()
        text = re.sub(r'[：:\(\)（）\[\]【】\s\.\-_]', '', text)
        return text.lower()

    def _detect_header_row(self, preview_rows: List[List[str]]) -> int:
        """自动识别表头行 - 增强版"""
        if not preview_rows:
            return 0

        # 收集所有字段的匹配关键词
        all_keywords = []
        for _, _, _, keywords in self.FIELD_DEFINITIONS:
            all_keywords.extend(keywords)
        
        # 添加额外的表头识别关键词
        header_indicators = ['序号', '编号', '名称', '项目', '单位', '数量', '单价', '合价', '金额', '备注']
        all_keywords.extend(header_indicators)

        best_row_idx = 0
        best_score = 0.0
        
        # print(f"[自动识别表头] 开始识别，共 {len(preview_rows)} 行预览数据")

        for row_idx, row in enumerate(preview_rows):
            score = 0.0
            matched_keywords = []

            for cell in row:
                cell_norm = self._normalize_text(cell)
                if not cell_norm:
                    continue

                for keyword in all_keywords:
                    keyword_norm = self._normalize_text(keyword)
                    if not keyword_norm:
                        continue

                    if cell_norm == keyword_norm:
                        score += 1.0
                        matched_keywords.append(f"{cell}={keyword}")
                    elif keyword_norm in cell_norm:
                        score += 0.8
                        matched_keywords.append(f"{cell}~{keyword}")
                    # 部分匹配（至少2个字符）
                    elif len(keyword_norm) >= 2:
                        for i in range(len(keyword_norm)):
                            for j in range(i + 2, min(i + 5, len(keyword_norm) + 1)):
                                substr = keyword_norm[i:j]
                                if substr in cell_norm:
                                    score += 0.3 * (len(substr) / len(keyword_norm))

            # 归一化分数
            normalized_score = score / max(len(row), 1)

            # print(f"[自动识别表头] 第 {row_idx + 1} 行: 得分={normalized_score:.2f}, 匹配={matched_keywords[:5]}")

            if normalized_score > best_score:
                best_score = normalized_score
                best_row_idx = row_idx

        # print(f"[自动识别表头] 结果: 第 {best_row_idx + 1} 行是表头 (得分: {best_score:.2f})")
        return best_row_idx

    def _calculate_similarity(self, header: str, keyword: str) -> float:
        """计算表头与关键词的相似度 - 增强版，支持多行表头"""
        header_norm = self._normalize_text(header)
        keyword_norm = self._normalize_text(keyword)
        
        if not header_norm or not keyword_norm:
            return 0.0
        
        # 完全匹配
        if header_norm == keyword_norm:
            return 1.0
        
        # 包含匹配
        if keyword_norm in header_norm:
            if header_norm.startswith(keyword_norm):
                return 0.9
            elif header_norm.endswith(keyword_norm):
                return 0.8
            else:
                return 0.7
        
        # 处理多行表头情况（如"人工费单价"可以匹配"人工费"+"单价"）
        # 将关键词拆分为部分
        keyword_parts = keyword_norm.split('费') if '费' in keyword_norm else [keyword_norm]
        if len(keyword_parts) > 1:
            # 检查是否包含关键词的各个部分
            matched_parts = 0
            for part in keyword_parts:
                if part and part in header_norm:
                    matched_parts += 1
            if matched_parts > 0:
                return 0.6 * (matched_parts / len(keyword_parts))
        
        # 部分匹配（共同子串）
        max_common = 0
        for i in range(len(keyword_norm)):
            for j in range(i + 1, len(keyword_norm) + 1):
                substr = keyword_norm[i:j]
                if substr in header_norm and len(substr) > max_common:
                    max_common = len(substr)
        
        if max_common > 0:
            return 0.5 * (max_common / max(len(header_norm), len(keyword_norm)))
        
        return 0.0
    
    def auto_detect_columns(self):
        """智能识别列 - 带排除词检查"""
        if not self.headers:
            return

        assigned_columns = set()

        # 定义字段的排除词（如果表头包含这些词，则不应匹配）
        exclusion_keywords = {
            'material_unit_price': ['损耗', '损', 'loss', '损耗率'],
            'material_loss_rate': [],  # 损耗列没有排除词
        }

        for field_key, field_name, is_required, keywords in self.FIELD_DEFINITIONS:
            best_match_idx = None
            best_score = 0.0

            for idx, header in enumerate(self.headers):
                if idx in assigned_columns:
                    continue

                # 检查排除词
                header_lower = header.lower()
                excluded = False
                if field_key in exclusion_keywords:
                    for exclude_word in exclusion_keywords[field_key]:
                        if exclude_word in header_lower:
                            excluded = True
                            # print(f"[排除匹配] {field_key}: '{header}' 包含排除词 '{exclude_word}'")
                            break

                if excluded:
                    continue

                for keyword in keywords:
                    score = self._calculate_similarity(header, keyword)

                    if score > best_score:
                        best_score = score
                        best_match_idx = idx

            threshold = 0.6 if is_required else 0.5

            if best_match_idx is not None and best_score >= threshold:
                self.mapping_widgets[field_key].set_selected_column(best_match_idx)
                assigned_columns.add(best_match_idx)
                # print(f"[匹配成功] {field_key} -> 列{best_match_idx} '{self.headers[best_match_idx]}' (得分: {best_score:.2f})")

        self.on_mapping_changed()
    
    def clear_mappings(self):
        """清除所有列映射"""
        for widget in self.mapping_widgets.values():
            widget.combo.setCurrentIndex(0)
    
    def on_sheet_changed(self, index):
        """工作簿改变"""
        if index >= 0 and self.sheet_names:
            sheet_name = self.sheet_names[index]
            if sheet_name != self.current_sheet_name:
                self.load_sheet_async(sheet_name)
    
    def on_mapping_changed(self):
        """列映射改变"""
        pass
    
    def get_column_mapping(self) -> Dict[str, int]:
        """获取列映射配置"""
        mapping = {}
        for field_key, widget in self.mapping_widgets.items():
            col_idx = widget.get_selected_column()
            if col_idx is not None:
                mapping[field_key] = col_idx
        return mapping
    
    def parse_sequence_level(self, sequence: str) -> int:
        """解析序号层级"""
        if not sequence:
            return 1
        
        sequence = str(sequence).strip()
        
        # 中文数字 -> 层级1
        chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if any(c in sequence for c in chinese_nums):
            return 1
        
        # 计算小数点数量
        dots = sequence.count('.')
        return dots + 2
    
    def import_data_with_progress(self, progress_dialog: ImportProgressDialog) -> List[Dict]:
        """导入数据（带进度显示）- 支持跨行数据合并"""
        if not self.current_sheet_name or not self.excel_path:
            return []

        mapping = self.get_column_mapping()

        # 检查必填字段
        for field_key, field_name, is_required, _ in self.FIELD_DEFINITIONS:
            if is_required and field_key not in mapping:
                MessageDialog.warning(self, "提示", f"必须配置 {field_name} 列")
                return []

        try:
            workbook = load_workbook(self.excel_path, data_only=True)
            sheet = workbook[self.current_sheet_name]

            # 数据起始行 = 表头起始行 + 表头行数 + 1
            start_row = self.header_row_index + self.header_row_count + 1
            
            # 计算总行数
            total_rows = sheet.max_row - start_row + 1
            progress_dialog.set_total_rows(total_rows)

            imported_items = []
            error_count = 0
            first_row_name = None  # 存储第一行（顶级）的名称
            
            # 用于存储跨行合并的数据
            pending_item = None  # 待处理的行数据（可能还有后续行需要合并）
            
            for row_idx, row in enumerate(sheet.iter_rows(min_row=start_row, values_only=True), start=1):
                # 检查是否取消
                if progress_dialog.is_cancelled:
                    break
                
                try:
                    # 提取当前行的数据
                    row_data = {}
                    for field_key, col_idx in mapping.items():
                        if col_idx < len(row):
                            value = row[col_idx]

                            # 数值字段处理（合价由计算得出，不导入）
                            numeric_fields = ['quantity', 'unit_price', 'labor_unit_price',
                                            'material_unit_price', 'material_loss_rate',
                                            'auxiliary_unit_price',
                                            'machine_unit_price', 'other_unit_price']
                            if field_key in numeric_fields:
                                try:
                                    value = float(value) if value is not None else 0.0
                                except (ValueError, TypeError):
                                    value = 0.0
                            else:
                                value = str(value).strip() if value is not None else ""

                            row_data[field_key] = value
                        else:
                            # 数值字段默认值
                            numeric_fields = ['quantity', 'unit_price', 'labor_unit_price',
                                            'material_unit_price', 'material_loss_rate',
                                            'auxiliary_unit_price',
                                            'machine_unit_price', 'other_unit_price']
                            if field_key in numeric_fields:
                                row_data[field_key] = 0.0
                            else:
                                row_data[field_key] = ""

                    # 获取序号和名称
                    sequence = str(row_data.get('sequence', '')).strip()
                    name = str(row_data.get('name', '')).strip()
                    description = str(row_data.get('description', '')).strip()
                    
                    # 判断这是否是一个新记录还是上一行的延续
                    # 如果序号为空，且名称不为空，说明是上一行的延续（项目名称或描述被分行了）
                    is_continuation = not sequence and name and pending_item is not None
                    
                    if is_continuation:
                        # 合并数据到上一行
                        # 合并项目名称
                        if name:
                            pending_name = str(pending_item.get('name', '')).strip()
                            if pending_name:
                                pending_item['name'] = pending_name + name
                            else:
                                pending_item['name'] = name
                        
                        # 合并项目特征描述
                        if description:
                            pending_desc = str(pending_item.get('description', '')).strip()
                            if pending_desc:
                                pending_item['description'] = pending_desc + description
                            else:
                                pending_item['description'] = description
                        
                        # 其他文本字段也进行合并
                        for field_key in ['specification', 'unit', 'remark']:
                            if field_key in row_data and row_data[field_key]:
                                pending_value = str(pending_item.get(field_key, '')).strip()
                                if pending_value:
                                    pending_item[field_key] = pending_value + str(row_data[field_key])
                                else:
                                    pending_item[field_key] = row_data[field_key]
                        
                        # 数值字段：如果当前行有值且不为0，则使用当前行的值
                        for field_key in ['quantity', 'unit_price', 'labor_unit_price',
                                        'material_unit_price', 'material_loss_rate',
                                        'auxiliary_unit_price', 'machine_unit_price', 'other_unit_price']:
                            if field_key in row_data and row_data[field_key]:
                                try:
                                    val = float(row_data[field_key])
                                    if val != 0:
                                        pending_item[field_key] = val
                                except:
                                    pass
                        
                    else:
                        # 这是一个新记录
                        # 先保存之前的待处理项
                        if pending_item is not None:
                            # 清理数据
                            pending_item['name'] = str(pending_item.get('name', '')).strip()
                            pending_item['description'] = str(pending_item.get('description', '')).strip()
                            
                            # 过滤空行
                            if pending_item['name']:
                                imported_items.append(pending_item)
                                progress_dialog.imported_count += 1
                        
                        # 检查当前行是否为空行
                        if not name:
                            pending_item = None
                            continue
                        
                        # 计算层级
                        if sequence:
                            row_data['level'] = self.parse_sequence_level(sequence)
                        else:
                            row_data['level'] = 1
                        
                        # 存储第一行（顶级）的名称
                        if first_row_name is None:
                            first_row_name = name
                        
                        # 设置当前行为待处理项
                        pending_item = row_data
                    
                except Exception as e:
                    error_count += 1
                    progress_dialog.error_count += 1
                
                # 更新进度（每5行更新一次）
                if row_idx % 5 == 0 or row_idx == total_rows:
                    current_item = pending_item if pending_item else (imported_items[-1] if imported_items else None)
                    progress_dialog.update_progress(row_idx, current_item)
            
            # 处理最后一个待处理项
            if pending_item is not None:
                pending_item['name'] = str(pending_item.get('name', '')).strip()
                pending_item['description'] = str(pending_item.get('description', '')).strip()
                if pending_item['name']:
                    imported_items.append(pending_item)
                    progress_dialog.imported_count += 1

            workbook.close()
            
            # 使用汇总项名称作为顶级行名称
            if self.summary_name and imported_items:
                # 检查第一行是否已经是顶级（level=1）
                if imported_items[0].get('level', 1) == 1:
                    # 第一行已经是顶级，替换其名称
                    imported_items[0]['name'] = self.summary_name
                else:
                    # 需要创建一个顶级行
                    top_level_item = {
                        'sequence': '1',
                        'name': self.summary_name,
                        'specification': '',
                        'description': '',
                        'unit': '',
                        'quantity': 0.0,
                        'unit_price': 0.0,
                        'labor_unit_price': 0.0,
                        'material_unit_price': 0.0,
                        'material_loss_rate': 0.0,
                        'auxiliary_unit_price': 0.0,
                        'machine_unit_price': 0.0,
                        'other_unit_price': 0.0,
                        'total_price': 0.0,
                        'level': 1,
                        'remark': ''
                    }
                    # 将其他所有行的层级加1
                    for item in imported_items:
                        item['level'] = item.get('level', 1) + 1
                    # 在开头插入顶级行
                    imported_items.insert(0, top_level_item)
            
            progress_dialog.set_completed(len(imported_items), error_count)
            return imported_items

        except Exception as e:
            progress_dialog.set_error(str(e))
            MessageDialog.critical(self, "错误", f"导入数据失败:\n{e}")
            return []
    
    def on_import(self):
        """确认导入"""
        # 创建进度对话框
        progress_dialog = ImportProgressDialog(self)
        
        # 显示进度对话框
        progress_dialog.show()
        QApplication.processEvents()
        
        # 执行导入
        data = self.import_data_with_progress(progress_dialog)
        
        # 存储导入的数据
        if data and len(data) > 0:
            self._imported_data = data
            # 导入完成，显示成功信息
            MessageDialog.information(self, "导入成功", f"成功导入 {len(data)} 条数据")
            progress_dialog.close()
            self.accept()
        elif data is not None and len(data) == 0:
            # 没有数据导入
            MessageDialog.warning(self, "提示", "没有导入任何数据，请检查Excel文件")
            progress_dialog.close()
        else:
            # 导入失败
            progress_dialog.close()
    
    def get_imported_data(self) -> List[Dict]:
        """获取导入的数据"""
        return getattr(self, '_imported_data', [])
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.load_worker:
            self.load_worker.stop()
            self.load_worker = None
        event.accept()

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
