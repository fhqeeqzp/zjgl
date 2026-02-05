"""
可视化Excel导入对话框
支持手动标记行类型：清单行、合并行、父级行、无效行
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from enum import Enum

try:
    import openpyxl
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame, QSplitter, QWidget,
    QApplication, QScrollArea, QGridLayout, QFormLayout, QCheckBox,
    QAbstractItemView, QMenu, QToolButton, QButtonGroup, QRadioButton,
    QGroupBox, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread, QPoint
from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QCursor

from ui.message_dialog import MessageDialog
from ui.fluent_widgets import PushButton, PrimaryPushButton, ToolButton


class RowType(Enum):
    """行类型枚举"""
    UNKNOWN = "未知"
    INVALID = "无效行"
    DATA = "清单行"
    MERGE = "合并行"
    DIVISION = "父级行"


class RowTypeButton(QPushButton):
    """行类型选择按钮"""
    type_selected = Signal(str, RowType)  # 行索引, 行类型
    
    ROW_TYPE_STYLES = {
        RowType.UNKNOWN: ("#E0E0E0", "#666666"),  # 背景色, 文字色
        RowType.INVALID: ("#FFCDD2", "#C62828"),
        RowType.DATA: ("#C8E6C9", "#2E7D32"),
        RowType.MERGE: ("#FFF9C4", "#F57F17"),
        RowType.DIVISION: ("#BBDEFB", "#1565C0"),
    }
    
    def __init__(self, row_idx: int, parent=None):
        super().__init__(parent)
        self.row_idx = row_idx
        self.current_type = RowType.UNKNOWN
        self.setFixedSize(80, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.show_type_menu)
        self.update_style()
    
    def update_style(self):
        """更新按钮样式"""
        bg_color, text_color = self.ROW_TYPE_STYLES[self.current_type]
        self.setText(self.current_type.value)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {text_color};
                color: white;
            }}
        """)
    
    def show_type_menu(self):
        """显示类型选择菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        
        for row_type in RowType:
            action = menu.addAction(row_type.value)
            action.triggered.connect(lambda checked, t=row_type: self.set_type(t))
        
        menu.exec(self.mapToGlobal(QPoint(0, self.height())))
    
    def set_type(self, row_type: RowType):
        """设置行类型"""
        self.current_type = row_type
        self.update_style()
        self.type_selected.emit(str(self.row_idx), row_type)


class ExcelPreviewTable(QTableWidget):
    """Excel预览表格 - 支持行类型标记"""
    
    row_type_changed = Signal(int, RowType)  # 行号, 行类型
    selection_changed = Signal(list)  # 选中的行号列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.row_types: Dict[int, RowType] = {}  # 行号 -> 行类型
        self.checkboxes: Dict[int, QCheckBox] = {}  # 行号 -> 复选框
        self.type_buttons: Dict[int, RowTypeButton] = {}  # 行号 -> 类型按钮
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setColumnCount(3)  # 选择列, 行号列, 类型列, 数据列...
        self.setHorizontalHeaderLabels(["选择", "行号", "类型", "数据预览"])
        
        # 设置列宽
        self.setColumnWidth(0, 50)   # 选择列
        self.setColumnWidth(1, 60)   # 行号列
        self.setColumnWidth(2, 90)   # 类型列
        
        # 设置表头样式
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        # 设置选择模式
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # 设置样式
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 12px;
            }
        """)
    
    def set_excel_data(self, headers: List[str], data: List[List], start_row: int = 1):
        """设置Excel数据"""
        self.clear()
        self.row_types.clear()
        self.checkboxes.clear()
        self.type_buttons.clear()
        
        # 设置列数: 选择 + 行号 + 类型 + 数据列
        total_cols = 3 + len(headers)
        self.setColumnCount(total_cols)
        
        # 设置表头
        header_labels = ["选择", "行号", "类型"] + headers
        self.setHorizontalHeaderLabels(header_labels)
        
        # 设置行数
        self.setRowCount(len(data))
        
        # 填充数据
        for row_idx, row_data in enumerate(data):
            actual_row = start_row + row_idx
            
            # 选择列 - 复选框
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox { margin-left: 15px; }")
            self.setCellWidget(row_idx, 0, checkbox)
            self.checkboxes[actual_row] = checkbox
            
            # 行号列
            row_num_item = QTableWidgetItem(str(actual_row))
            row_num_item.setTextAlignment(Qt.AlignCenter)
            row_num_item.setFlags(row_num_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row_idx, 1, row_num_item)
            
            # 类型列 - 类型选择按钮
            type_btn = RowTypeButton(actual_row)
            type_btn.type_selected.connect(self.on_type_selected)
            self.setCellWidget(row_idx, 2, type_btn)
            self.type_buttons[actual_row] = type_btn
            
            # 数据列
            for col_idx, cell_value in enumerate(row_data):
                if col_idx < len(headers):
                    item = QTableWidgetItem(str(cell_value) if cell_value else "")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.setItem(row_idx, 3 + col_idx, item)
            
            # 初始化行类型
            self.row_types[actual_row] = RowType.UNKNOWN
        
        # 调整列宽
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 90)
    
    def on_type_selected(self, row_idx_str: str, row_type: RowType):
        """行类型选择回调"""
        row_idx = int(row_idx_str)
        self.row_types[row_idx] = row_type
        self.row_type_changed.emit(row_idx, row_type)
        
        # 更新行背景色
        self.update_row_style(row_idx)
    
    def update_row_style(self, row_idx: int):
        """更新行样式"""
        # 找到对应的表格行
        for visual_row in range(self.rowCount()):
            item = self.item(visual_row, 1)
            if item and int(item.text()) == row_idx:
                row_type = self.row_types.get(row_idx, RowType.UNKNOWN)
                bg_color = RowTypeButton.ROW_TYPE_STYLES[row_type][0]
                
                # 设置行背景色
                for col in range(self.columnCount()):
                    item = self.item(visual_row, col)
                    if item:
                        item.setBackground(QBrush(QColor(bg_color)))
                break
    
    def get_selected_rows(self) -> List[int]:
        """获取选中的行号列表"""
        selected = []
        for row_idx, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.append(row_idx)
        return selected
    
    def set_row_type(self, row_idx: int, row_type: RowType):
        """设置指定行的类型"""
        if row_idx in self.type_buttons:
            self.type_buttons[row_idx].set_type(row_type)
    
    def batch_set_type(self, row_indices: List[int], row_type: RowType):
        """批量设置行类型"""
        for row_idx in row_indices:
            self.set_row_type(row_idx, row_type)
    
    def get_row_types(self) -> Dict[int, RowType]:
        """获取所有行类型"""
        return self.row_types.copy()
    
    def auto_detect_types(self, mapping: Dict[str, int]):
        """自动检测行类型"""
        # 这里可以调用之前的自动识别逻辑
        pass


class VisualImportDialog(QDialog):
    """可视化导入对话框"""
    
    import_confirmed = Signal(list)  # 发送导入的数据列表
    
    def __init__(self, excel_path: str, parent=None):
        super().__init__(parent)
        self.excel_path = excel_path
        self.workbook = None
        self.current_sheet = None
        self.sheet_names = []
        self.headers = []
        self.preview_data = []
        
        self.setWindowTitle("导入Excel招标文件")
        self.setMinimumSize(1400, 900)
        
        self.setup_ui()
        self.load_excel()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ========== 顶部工具栏 ==========
        toolbar = QHBoxLayout()
        
        # 文件信息
        file_label = QLabel(f"📄 导入Excel表: {self.excel_path}")
        file_label.setStyleSheet("font-size: 13px; color: #666;")
        toolbar.addWidget(file_label)
        
        toolbar.addStretch()
        
        # 工作表选择
        toolbar.addWidget(QLabel("选择数据表:"))
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(200)
        self.sheet_combo.currentIndexChanged.connect(self.on_sheet_changed)
        toolbar.addWidget(self.sheet_combo)
        
        # 导入目标选择
        toolbar.addWidget(QLabel("导入至:"))
        self.target_combo = QComboBox()
        self.target_combo.addItem("分部分项工程量清单")
        self.target_combo.setMinimumWidth(150)
        toolbar.addWidget(self.target_combo)
        
        # 识别行按钮
        self.detect_btn = PrimaryPushButton("识别行")
        self.detect_btn.setFixedSize(80, 32)
        self.detect_btn.clicked.connect(self.auto_detect_rows)
        toolbar.addWidget(self.detect_btn)
        
        main_layout.addLayout(toolbar)
        
        # ========== 中间主体区域 ==========
        splitter = QSplitter(Qt.Horizontal)
        
        # ---- 左侧：树形结构（当前节点）----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_title = QLabel("📁 当前节点")
        left_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        left_layout.addWidget(left_title)
        
        # 这里可以添加树形控件显示当前汇总表的节点结构
        self.tree_placeholder = QLabel("汇总表节点结构\n（待实现）")
        self.tree_placeholder.setAlignment(Qt.AlignCenter)
        self.tree_placeholder.setStyleSheet("""
            background-color: #f5f5f5;
            border: 1px dashed #ccc;
            padding: 20px;
            color: #999;
        """)
        left_layout.addWidget(self.tree_placeholder)
        
        splitter.addWidget(left_panel)
        
        # ---- 右侧：Excel预览表格 ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格工具栏
        table_toolbar = QHBoxLayout()
        
        # 过滤条件
        table_toolbar.addWidget(QLabel("过滤条件:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["显示全部", "仅显示清单行", "仅显示父级行", "仅显示无效行"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        table_toolbar.addWidget(self.filter_combo)
        
        table_toolbar.addStretch()
        
        # 批量操作按钮
        batch_label = QLabel("批量标记为:")
        batch_label.setStyleSheet("color: #666;")
        table_toolbar.addWidget(batch_label)
        
        self.batch_invalid_btn = PushButton("无效行")
        self.batch_invalid_btn.setFixedSize(60, 28)
        self.batch_invalid_btn.clicked.connect(lambda: self.batch_set_type(RowType.INVALID))
        table_toolbar.addWidget(self.batch_invalid_btn)
        
        self.batch_data_btn = PushButton("清单行")
        self.batch_data_btn.setFixedSize(60, 28)
        self.batch_data_btn.clicked.connect(lambda: self.batch_set_type(RowType.DATA))
        table_toolbar.addWidget(self.batch_data_btn)
        
        self.batch_merge_btn = PushButton("合并行")
        self.batch_merge_btn.setFixedSize(60, 28)
        self.batch_merge_btn.clicked.connect(lambda: self.batch_set_type(RowType.MERGE))
        table_toolbar.addWidget(self.batch_merge_btn)
        
        self.batch_division_btn = PushButton("父级行")
        self.batch_division_btn.setFixedSize(60, 28)
        self.batch_division_btn.clicked.connect(lambda: self.batch_set_type(RowType.DIVISION))
        table_toolbar.addWidget(self.batch_division_btn)
        
        right_layout.addLayout(table_toolbar)
        
        # 图例说明
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("图例:"))
        
        for row_type in [RowType.INVALID, RowType.DATA, RowType.MERGE, RowType.DIVISION]:
            bg_color, text_color = RowTypeButton.ROW_TYPE_STYLES[row_type]
            label = QLabel(f"  {row_type.value}  ")
            label.setStyleSheet(f"""
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            """)
            legend_layout.addWidget(label)
        
        legend_layout.addStretch()
        right_layout.addLayout(legend_layout)
        
        # Excel预览表格
        self.preview_table = ExcelPreviewTable()
        self.preview_table.row_type_changed.connect(self.on_row_type_changed)
        right_layout.addWidget(self.preview_table)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 1150])
        
        main_layout.addWidget(splitter)
        
        # ========== 底部按钮区域 ==========
        bottom_layout = QHBoxLayout()
        
        # 左侧提示
        hint_label = QLabel("💡 提示: 通过鼠标左键拖动可批量选中行，点击类型列可修改行类型")
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        bottom_layout.addWidget(hint_label)
        
        bottom_layout.addStretch()
        
        # 常见问题按钮
        help_btn = PushButton("常见问题")
        help_btn.setFixedSize(80, 32)
        bottom_layout.addWidget(help_btn)
        
        # 清空导入复选框
        self.clear_import_check = QCheckBox("清空导入")
        bottom_layout.addWidget(self.clear_import_check)
        
        # 导入按钮
        self.import_btn = PrimaryPushButton("导入")
        self.import_btn.setFixedSize(80, 32)
        self.import_btn.clicked.connect(self.on_import)
        bottom_layout.addWidget(self.import_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def load_excel(self):
        """加载Excel文件"""
        try:
            self.workbook = load_workbook(self.excel_path, data_only=True)
            self.sheet_names = self.workbook.sheetnames
            
            # 填充工作表选择框
            self.sheet_combo.clear()
            self.sheet_combo.addItems(self.sheet_names)
            
        except Exception as e:
            MessageDialog.error(self, "错误", f"加载Excel文件失败:\n{str(e)}")
    
    def on_sheet_changed(self, index):
        """工作表切换"""
        if index < 0 or not self.workbook:
            return
        
        sheet_name = self.sheet_combo.currentText()
        self.current_sheet = self.workbook[sheet_name]
        
        # 加载预览数据
        self.load_sheet_preview()
    
    def load_sheet_preview(self):
        """加载工作表预览"""
        if not self.current_sheet:
            return
        
        # 读取前100行作为预览
        max_rows = 100
        data = []
        headers = []
        
        for row_idx, row in enumerate(self.current_sheet.iter_rows(values_only=True), 1):
            if row_idx == 1:
                # 假设第一行是表头
                headers = [str(cell) if cell else f"列{chr(65+i)}" for i, cell in enumerate(row)]
            else:
                data.append([str(cell) if cell else "" for cell in row])
            
            if row_idx > max_rows:
                break
        
        self.headers = headers
        self.preview_data = data
        
        # 更新表格
        self.preview_table.set_excel_data(headers, data, start_row=2)
    
    def on_row_type_changed(self, row_idx: int, row_type: RowType):
        """行类型改变回调"""
        # 可以在这里添加额外的处理逻辑
        pass
    
    def on_filter_changed(self, filter_text: str):
        """过滤条件改变"""
        # 实现行过滤逻辑
        pass
    
    def batch_set_type(self, row_type: RowType):
        """批量设置行类型"""
        selected_rows = self.preview_table.get_selected_rows()
        if not selected_rows:
            MessageDialog.warning(self, "提示", "请先选择要标记的行（勾选左侧复选框）")
            return
        
        self.preview_table.batch_set_type(selected_rows, row_type)
        MessageDialog.information(self, "完成", f"已将 {len(selected_rows)} 行标记为【{row_type.value}】")
    
    def auto_detect_rows(self):
        """自动识别行类型"""
        # 这里可以调用之前的自动识别逻辑
        MessageDialog.information(self, "提示", "自动识别功能开发中...")
    
    def on_import(self):
        """执行导入"""
        row_types = self.preview_table.get_row_types()
        
        # 统计各类型的行数
        type_counts = {}
        for row_type in row_types.values():
            type_counts[row_type.value] = type_counts.get(row_type.value, 0) + 1
        
        # 显示确认对话框
        type_info = "\n".join([f"  {k}: {v} 行" for k, v in type_counts.items()])
        reply = QMessageBox.question(
            self,
            "确认导入",
            f"即将导入以下数据:\n{type_info}\n\n是否继续?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 执行导入逻辑
            self.import_confirmed.emit([])
            self.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # 测试对话框
    dialog = VisualImportDialog("test.xlsx")
    dialog.show()
    
    sys.exit(app.exec())
