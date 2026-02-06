"""
投标汇总表页签
显示投标汇总信息，支持选择投标和版本，使用QTreeWidget树形结构
支持直接在页签内编辑，支持从Excel导入数据
"""
import os
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QDoubleSpinBox,
    QFormLayout,
    QSplitter,
    QDialog,
    QScrollArea,
    QMenu,
    QMessageBox
)

from ui.message_dialog import MessageDialog

from ui.message_dialog import MessageDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QAction

from ui.fluent_widgets import PushButton, PrimaryPushButton
from ..data.summary_model import SummaryItem, SummaryItemType, SummaryTemplate
from ..data.link_db import DataLinkDatabase
from ..logic.detail_manager import DetailManager
from .excel_import_dialog import ExcelImportDialog, ExcelFileSelector


class BiddingSummaryTab(QWidget):
    """投标汇总表页签 - 集成编辑功能和Excel导入"""

    def __init__(self, parent_page):
        super().__init__()
        self.parent_page = parent_page
        self.bidding_manager = parent_page.bidding_manager
        self.current_bidding_id = None
        self.current_bidding_code = None
        self.current_bidding_name = None
        self.wd_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "WD")

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 分割器（左侧树形，右侧编辑）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：树形控件区域
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(10)

        # 树形工具栏（集成投标选择、版本、总价）
        tree_toolbar = QHBoxLayout()
        tree_toolbar.setSpacing(10)

        # 投标选择下拉框
        tree_toolbar.addWidget(QLabel("投标:"))
        self.bidding_combo = QComboBox()
        self.bidding_combo.setMinimumWidth(200)
        self.bidding_combo.currentIndexChanged.connect(self.on_bidding_changed)
        tree_toolbar.addWidget(self.bidding_combo)

        # 版本选择下拉框
        tree_toolbar.addWidget(QLabel("版本:"))
        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(150)
        self.version_combo.currentIndexChanged.connect(self.on_version_changed)
        tree_toolbar.addWidget(self.version_combo)
        
        # 版本管理按钮
        self.new_version_btn = PushButton("➕ 新版本")
        self.new_version_btn.setToolTip("基于当前数据创建新版本")
        self.new_version_btn.clicked.connect(self.on_new_version)
        tree_toolbar.addWidget(self.new_version_btn)
        
        self.delete_version_btn = PushButton("🗑️ 删除版本")
        self.delete_version_btn.setToolTip("删除当前选中的版本")
        self.delete_version_btn.clicked.connect(self.on_delete_version)
        tree_toolbar.addWidget(self.delete_version_btn)

        tree_toolbar.addSpacing(20)

        # 展开/折叠按钮
        self.expand_btn = PushButton("📂 展开")
        self.expand_btn.clicked.connect(self.expand_all)
        tree_toolbar.addWidget(self.expand_btn)

        self.collapse_btn = PushButton("📁 折叠")
        self.collapse_btn.clicked.connect(self.collapse_all)
        tree_toolbar.addWidget(self.collapse_btn)

        tree_toolbar.addSpacing(20)

        # 数据关联按钮
        self.data_link_btn = PushButton("🔗 数据关联")
        self.data_link_btn.setToolTip("可视化关联汇总表和明细表数据")
        self.data_link_btn.clicked.connect(self.on_data_link)
        tree_toolbar.addWidget(self.data_link_btn)

        tree_toolbar.addStretch()

        # 总价显示
        tree_toolbar.addWidget(QLabel("总价:"))
        self.total_label = QLabel("¥ 0.00")
        self.total_label.setObjectName("totalLabel")
        tree_toolbar.addWidget(self.total_label)

        tree_layout.addLayout(tree_toolbar)

        # Excel导入工具栏
        excel_toolbar = QHBoxLayout()
        excel_toolbar.setSpacing(10)

        # Excel文件选择器
        self.excel_selector = ExcelFileSelector()
        excel_toolbar.addWidget(self.excel_selector)

        # 导入按钮
        self.import_excel_btn = PrimaryPushButton("📥 导入Excel")
        self.import_excel_btn.clicked.connect(self.on_import_excel)
        excel_toolbar.addWidget(self.import_excel_btn)

        # 重置级别按钮
        self.reset_level_btn = PushButton("🔄 重置为级别1")
        self.reset_level_btn.setToolTip("将所有导入的数据重置为级别1，保持原有顺序")
        self.reset_level_btn.clicked.connect(self.reset_all_to_level_one)
        excel_toolbar.addWidget(self.reset_level_btn)

        excel_toolbar.addStretch()

        # 保存汇总表按钮
        self.save_btn = PrimaryPushButton("💾 保存汇总表")
        self.save_btn.clicked.connect(self.on_save)
        excel_toolbar.addWidget(self.save_btn)

        tree_layout.addLayout(excel_toolbar)

        # 树形控件
        self.summary_tree = QTreeWidget()
        self.summary_tree.setColumnCount(10)

        # 启用原生树形连接线（必须在setHeaderLabels之前）
        self.summary_tree.setRootIsDecorated(True)
        self.summary_tree.setItemsExpandable(True)
        self.summary_tree.setExpandsOnDoubleClick(True)
        self.summary_tree.setIndentation(24)  # 缩进24像素
        self.summary_tree.setUniformRowHeights(True)
        # print(f"[树形控件配置] RootIsDecorated: {self.summary_tree.rootIsDecorated()}, Indentation: {self.summary_tree.indentation()}")
        
        # 强制设置树形控件样式，确保连接线显示
        self.summary_tree.setObjectName("summaryTree")

        self.summary_tree.setHeaderLabels([
            "工程项目及费用名称", "序号", "报价", "其中：主材费", "其中：辅材费",
            "其中：人工费", "其中：机械费", "其中：其他费", "其中：管理费", "其中：税金"
        ])
        self.summary_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.summary_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 启用多选
        self.summary_tree.setAlternatingRowColors(True)
        self.summary_tree.setUniformRowHeights(True)

        # 设置列宽 - 第一列（工程项目及费用名称）需要足够宽以显示展开图标和层级缩进
        header = self.summary_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 第一列自适应
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # 序号列固定宽度
        for col in range(2, 10):
            header.setSectionResizeMode(col, QHeaderView.Fixed)

        # 设置列宽
        self.summary_tree.setColumnWidth(1, 80)  # 序号列
        self.summary_tree.setColumnWidth(2, 100)
        self.summary_tree.setColumnWidth(3, 100)
        self.summary_tree.setColumnWidth(4, 100)
        self.summary_tree.setColumnWidth(5, 100)
        self.summary_tree.setColumnWidth(6, 100)
        self.summary_tree.setColumnWidth(7, 100)
        self.summary_tree.setColumnWidth(8, 100)
        self.summary_tree.setColumnWidth(9, 100)

        # 启用编辑
        self.summary_tree.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        # 连接信号
        self.summary_tree.itemSelectionChanged.connect(self.on_item_selected)
        self.summary_tree.itemChanged.connect(self.on_item_changed)
        self.summary_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        # 启用右键菜单
        self.summary_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.summary_tree.customContextMenuRequested.connect(self.show_context_menu)

        tree_layout.addWidget(self.summary_tree)

        splitter.addWidget(tree_widget)

        # 右侧：编辑面板（使用滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(350)
        scroll_area.setMinimumWidth(300)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        edit_panel = QWidget()
        edit_layout = QVBoxLayout(edit_panel)
        edit_layout.setContentsMargins(10, 0, 10, 0)
        edit_layout.setSpacing(15)

        # 编辑表单
        edit_group = QGroupBox("项目编辑")
        form_layout = QFormLayout(edit_group)
        form_layout.setSpacing(10)

        # 序号
        self.seq_input = QLineEdit()
        self.seq_input.setPlaceholderText("如：一、1、1.1")
        form_layout.addRow("序号:", self.seq_input)

        # 工程项目及费用名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入工程项目及费用名称")
        form_layout.addRow("工程项目及费用名称:", self.name_input)

        # 各项费用输入
        self.main_material_input = QDoubleSpinBox()
        self.main_material_input.setMaximum(999999999)
        self.main_material_input.setDecimals(2)
        self.main_material_input.setPrefix("¥ ")
        self.main_material_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：主材费:", self.main_material_input)

        self.aux_material_input = QDoubleSpinBox()
        self.aux_material_input.setMaximum(999999999)
        self.aux_material_input.setDecimals(2)
        self.aux_material_input.setPrefix("¥ ")
        self.aux_material_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：辅材费:", self.aux_material_input)

        self.labor_input = QDoubleSpinBox()
        self.labor_input.setMaximum(999999999)
        self.labor_input.setDecimals(2)
        self.labor_input.setPrefix("¥ ")
        self.labor_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：人工费:", self.labor_input)

        self.machinery_input = QDoubleSpinBox()
        self.machinery_input.setMaximum(999999999)
        self.machinery_input.setDecimals(2)
        self.machinery_input.setPrefix("¥ ")
        self.machinery_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：机械费:", self.machinery_input)

        self.other_input = QDoubleSpinBox()
        self.other_input.setMaximum(999999999)
        self.other_input.setDecimals(2)
        self.other_input.setPrefix("¥ ")
        self.other_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：其他费:", self.other_input)

        self.management_input = QDoubleSpinBox()
        self.management_input.setMaximum(999999999)
        self.management_input.setDecimals(2)
        self.management_input.setPrefix("¥ ")
        self.management_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：管理费:", self.management_input)

        self.tax_input = QDoubleSpinBox()
        self.tax_input.setMaximum(999999999)
        self.tax_input.setDecimals(2)
        self.tax_input.setPrefix("¥ ")
        self.tax_input.valueChanged.connect(self.calculate_quote_price)
        form_layout.addRow("其中：税金:", self.tax_input)

        # 报价（只读，自动计算）
        self.quote_label = QLabel("¥ 0.00")
        self.quote_label.setObjectName("quoteLabel")
        form_layout.addRow("报价:", self.quote_label)

        edit_layout.addWidget(edit_group)

        # 应用按钮
        self.apply_btn = PrimaryPushButton("✓ 应用修改")
        self.apply_btn.clicked.connect(self.apply_edit)
        edit_layout.addWidget(self.apply_btn)

        # 添加子项目按钮
        self.add_child_btn = PushButton("➕ 添加子项目")
        self.add_child_btn.setObjectName("secondaryButton")
        self.add_child_btn.clicked.connect(self.add_child_item)
        edit_layout.addWidget(self.add_child_btn)

        edit_layout.addStretch()

        scroll_area.setWidget(edit_panel)

        splitter.addWidget(scroll_area)
        splitter.setSizes([700, 350])

        layout.addWidget(splitter)

        # 加载投标列表
        self.load_bidding_combo()

    def get_excel_directory(self) -> str:
        """获取Excel文件目录"""
        if not self.current_bidding_id:
            return ""

        # 获取项目名称
        bidding = self.bidding_manager.get_bidding(self.current_bidding_id)
        if not bidding:
            return ""

        project = self.bidding_manager.project_manager.get_project(bidding.project_id) if self.bidding_manager.project_manager else None
        project_name = project.name if project else "未知项目"

        # 构建路径: WD/项目名/投标附件/
        folder_path = os.path.join(self.wd_base_path, project_name, "投标附件")
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def on_bidding_changed(self, index):
        """投标选择改变"""
        if index > 0:
            bidding_id = self.bidding_combo.currentData()
            bidding = self.bidding_manager.get_bidding(bidding_id)
            if bidding:
                self.current_bidding_id = bidding_id
                self.current_bidding_code = bidding.bidding_code
                self.current_bidding_name = bidding.bidding_name
                
                # 加载版本列表
                self.load_version_combo()
                
                # 加载数据
                self.load_bidding_data(bidding_id)

                # 更新Excel文件选择器目录
                excel_dir = self.get_excel_directory()
                self.excel_selector.set_directory(excel_dir)

                # 通知父页面更新当前选中的投标
                self.parent_page.select_bidding(bidding_id, bidding.bidding_code)
        else:
            self.current_bidding_id = None
            self.current_bidding_code = None
            self.current_bidding_name = None
            self.version_combo.clear()
            self.summary_tree.clear()
            self.excel_selector.set_directory("")
            self.calculate_total()
    
    def load_version_combo(self):
        """加载版本列表到下拉框"""
        self.version_combo.clear()
        
        if not self.current_bidding_id:
            return
        
        versions = self.bidding_manager.get_summary_versions(self.current_bidding_id)
        
        if not versions:
            self.version_combo.addItem("无版本", None)
            return
        
        for version in versions:
            version_id = version.get('id')
            version_code = version.get('version', 'V1.0')
            version_name = version.get('version_name', '')
            is_active = version.get('is_active', False)
            created_at = version.get('created_at', '')
            
            # 格式化日期
            if created_at:
                if hasattr(created_at, 'strftime'):
                    # datetime 对象
                    date_str = created_at.strftime('%Y-%m-%d')
                else:
                    # 字符串
                    date_str = str(created_at)[:10]
            else:
                date_str = ''
            
            # 格式化显示文本
            display_text = f"{version_code}"
            if version_name:
                display_text += f" - {version_name}"
            if is_active:
                display_text += " (当前)"
            if date_str:
                display_text += f" [{date_str}]"
            
            self.version_combo.addItem(display_text, version_id)
    
    def on_version_changed(self, index):
        """版本选择改变"""
        if index < 0 or not self.current_bidding_id:
            return
        
        version_id = self.version_combo.currentData()
        # print(f"[版本切换] index: {index}, version_id: {version_id}")
        
        if not version_id:
            # print("[版本切换] version_id 为空，跳过加载")
            return
        
        # 加载指定版本的数据
        items = self.bidding_manager.get_bidding_summary_by_id(version_id)
        # print(f"[版本切换] 获取到 {len(items)} 条数据")
        
        if items:
            self.build_tree_from_db_data(items)
            # print(f"[版本切换] 已加载版本 ID: {version_id}")
        else:
            pass  # print(f"[版本切换] 版本 {version_id} 没有数据")

    def on_new_version(self):
        """创建新版本"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 获取当前所有版本
        versions = self.bidding_manager.get_summary_versions(self.current_bidding_id)

        # 生成新版本号
        if versions:
            latest_version = versions[0].get('version', 'V1.0')
            try:
                # 解析版本号，如 V1.0 -> V2.0
                version_num = float(latest_version.replace('V', '').replace('v', ''))
                new_version = f"V{version_num + 1:.1f}"
            except:
                new_version = f"V{len(versions) + 1}.0"
        else:
            new_version = "V1.0"

        # 弹出对话框输入版本信息
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        version_name, ok = QInputDialog.getText(
            self, "新建版本", "版本名称:",
            QLineEdit.Normal, f"版本 {new_version}"
        )

        if not ok:
            return

        # 收集当前数据
        items_data = []

        def collect_items(item: QTreeWidgetItem, parent_temp_id: int = None):
            summary_item = item.data(0, Qt.UserRole)
            if summary_item:
                temp_id = len(items_data)
                item_data = {
                    'temp_id': temp_id,
                    'parent_temp_id': parent_temp_id,
                    'item_type': summary_item.item_type.value,
                    'sequence': summary_item.sequence,
                    'name': summary_item.name,
                    'quote_price': summary_item.quote_price,
                    'main_material_fee': summary_item.main_material_fee,
                    'aux_material_fee': summary_item.aux_material_fee,
                    'labor_fee': summary_item.labor_fee,
                    'machinery_fee': summary_item.machinery_fee,
                    'other_fee': summary_item.other_fee,
                    'management_fee': summary_item.management_fee,
                    'tax_fee': summary_item.tax_fee,
                }
                items_data.append(item_data)

                for i in range(item.childCount()):
                    collect_items(item.child(i), temp_id)

        for i in range(self.summary_tree.topLevelItemCount()):
            collect_items(self.summary_tree.topLevelItem(i))

        if not items_data:
            MessageDialog.warning(self, "提示", "当前没有数据")
            return

        # 保存新版本
        success, result = self.bidding_manager.save_bidding_summary(
            self.current_bidding_id,
            items_data,
            version=new_version,
            version_name=version_name,
            created_by="",
            remark=""
        )

        if success:
            self.show_message_box(QMessageBox.Information, "成功", f"新版本 {new_version} 已创建")
            self.load_version_combo()
            # 选中新创建的版本
            for i in range(self.version_combo.count()):
                if self.version_combo.itemData(i) == result:
                    self.version_combo.setCurrentIndex(i)
                    break
        else:
            self.show_message_box(QMessageBox.Critical, "错误", f"创建版本失败:\n{result}")
    
    def on_delete_version(self):
        """删除当前版本"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return
        
        version_id = self.version_combo.currentData()
        if not version_id:
            MessageDialog.warning(self, "提示", "请先选择要删除的版本")
            return
        
        # 确认删除
        reply = MessageDialog.question(self, "确认删除", "确定要删除当前版本吗？\n此操作不可恢复！", MessageDialog.Yes | MessageDialog.No,
            MessageDialog.No
        )
        
        if reply != MessageDialog.Yes:
            return
        
        success, msg = self.bidding_manager.delete_summary_version(version_id)
        
        if success:
            MessageDialog.information(self, "成功", "版本已删除")
            self.load_version_combo()
            # 重新加载数据
            self.load_bidding_data(self.current_bidding_id)
        else:
            QMessageBox.critical(self, "错误", msg)

    def load_bidding_combo(self):
        """加载投标列表到下拉框"""
        self.bidding_combo.clear()
        self.bidding_combo.addItem("请选择投标...", None)

        biddings = self.bidding_manager.get_biddings()
        for bidding in biddings:
            display_text = f"{bidding.bidding_code} - {bidding.bidding_name}"
            self.bidding_combo.addItem(display_text, bidding.id)

    def on_bidding_selected(self, bidding_id: int, bidding_code: str = None):
        """从父页面接收选中的投标 - 自动加载最后版本汇总表数据"""
        if bidding_id:
            self.current_bidding_id = bidding_id
            self.current_bidding_code = bidding_code

            bidding = self.bidding_manager.get_bidding(bidding_id)
            if bidding:
                self.current_bidding_name = bidding.bidding_name

            # 在下拉框中选中对应的投标
            for i in range(self.bidding_combo.count()):
                if self.bidding_combo.itemData(i) == bidding_id:
                    self.bidding_combo.setCurrentIndex(i)
                    break

            # 更新Excel文件选择器目录
            excel_dir = self.get_excel_directory()
            self.excel_selector.set_directory(excel_dir)
            
            # 自动加载最后版本的汇总表数据
            self.load_last_version_summary(bidding_id)

    def load_last_version_summary(self, bidding_id: int):
        """加载最后版本的汇总表数据 - 如果没有版本则清空显示"""
        # 获取所有版本
        versions = self.bidding_manager.get_summary_versions(bidding_id)
        
        if versions:
            # 有版本，加载最后一个版本（最新的）
            last_version = versions[0]  # 假设按时间倒序排列
            version_id = last_version.get('id')
            version_code = last_version.get('version', 'V1.0')
            
            # 加载该版本的数据
            items = self.bidding_manager.get_bidding_summary_by_id(version_id)
            if items:
                self.build_tree_from_db_data(items)
                # 更新版本下拉框
                self.load_version_combo()
                # 选中最后一个版本
                for i in range(self.version_combo.count()):
                    if self.version_combo.itemData(i) == version_id:
                        self.version_combo.setCurrentIndex(i)
                        break
            else:
                # 版本存在但没有数据，清空显示
                self.summary_tree.clear()
                self.load_default_template()
        else:
            # 没有版本，清空显示并加载默认模板（空表状态）
            self.summary_tree.clear()
            self.load_default_template()
            # 清空版本下拉框
            self.version_combo.clear()
            self.version_combo.addItem("无版本", None)

    def load_bidding_data(self, bidding_id: int):
        """加载投标汇总数据 - 优先从数据库加载，如果没有则加载默认模板"""
        # 先尝试从数据库加载
        items = self.bidding_manager.get_bidding_summary(bidding_id)

        if items:
            # 从数据库加载成功
            self.build_tree_from_db_data(items)
            # 标记有明细的汇总行
            self._mark_items_with_detail(bidding_id)
            # print(f"从数据库加载了 {len(items)} 条汇总数据")
        else:
            # 数据库中没有数据，加载默认模板
            # print("数据库中没有数据，加载默认模板")
            self.load_default_template()

    def _mark_items_with_detail(self, bidding_id: int):
        """标记有明细的汇总行（红色字体）"""
        # 获取有明细的汇总项ID列表
        summary_item_ids = self.bidding_manager.get_summary_item_ids_with_detail(bidding_id)
        if not summary_item_ids:
            return

        # 遍历树形控件，标记有明细的行
        def traverse_and_mark(parent_item=None):
            if parent_item is None:
                # 从顶层节点开始
                for i in range(self.summary_tree.topLevelItemCount()):
                    item = self.summary_tree.topLevelItem(i)
                    self._check_and_mark_item(item, summary_item_ids)
                    traverse_and_mark(item)
            else:
                # 遍历子节点
                for i in range(parent_item.childCount()):
                    item = parent_item.child(i)
                    self._check_and_mark_item(item, summary_item_ids)
                    traverse_and_mark(item)

        traverse_and_mark()

    def _check_and_mark_item(self, tree_item, summary_item_ids: list):
        """检查并标记单个树项"""
        item_data = tree_item.data(0, Qt.UserRole)
        if not item_data:
            return

        item_id = getattr(item_data, 'id', None)
        if item_id and item_id in summary_item_ids:
            self._set_item_red_font(tree_item)

    def on_import_excel(self):
        """导入Excel"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        excel_path = self.excel_selector.get_selected_file()
        if not excel_path:
            MessageDialog.warning(self, "提示", "请先选择Excel文件")
            return

        # 打开导入对话框
        dialog = ExcelImportDialog(excel_path, self.current_bidding_name, self)
        if dialog.exec() == QDialog.Accepted:
            imported_data = dialog.get_imported_data()
            if imported_data:
                self.build_tree_from_imported_data(imported_data)
                MessageDialog.information(self, "成功", f"成功导入 {len(imported_data)} 条数据")

    def build_tree_from_imported_data(self, data: List[Dict]):
        """从导入的数据构建树形结构"""
        self.summary_tree.clear()

        if not data:
            return

        # 创建根节点（投标名称）
        root_item = SummaryItem(
            item_type=SummaryItemType.CATEGORY,
            sequence="",
            name=self.current_bidding_name or "投标汇总",
        )
        root_tree_item = QTreeWidgetItem(self.summary_tree)
        self.update_tree_item(root_tree_item, root_item)

        # 使用栈来构建层级结构
        # 栈中存储 (层级, 树节点)
        stack = [(0, root_tree_item)]

        for item_data in data:
            level = item_data.get('level', 2)
            sequence = str(item_data.get('sequence', ''))
            name = str(item_data.get('name', ''))

            # 创建SummaryItem
            summary_item = SummaryItem(
                item_type=SummaryItemType.ITEM if level > 1 else SummaryItemType.CATEGORY,
                sequence=sequence,
                name=name,
                quote_price=float(item_data.get('quote_price', 0)),
                main_material_fee=float(item_data.get('main_material_fee', 0)),
                aux_material_fee=float(item_data.get('aux_material_fee', 0)),
                labor_fee=float(item_data.get('labor_fee', 0)),
                machinery_fee=float(item_data.get('machinery_fee', 0)),
                other_fee=float(item_data.get('other_fee', 0)),
                management_fee=float(item_data.get('management_fee', 0)),
                tax_fee=float(item_data.get('tax_fee', 0)),
            )
            summary_item.calculate_quote_price()

            # 找到正确的父节点
            while stack and stack[-1][0] >= level:
                stack.pop()

            if stack:
                parent_tree_item = stack[-1][1]
            else:
                parent_tree_item = root_tree_item

            # 创建树节点
            tree_item = QTreeWidgetItem(parent_tree_item)
            self.update_tree_item(tree_item, summary_item)

            # 展开父节点
            parent_tree_item.setExpanded(True)

            # 将当前节点加入栈
            stack.append((level, tree_item))

        # 展开根节点
        root_tree_item.setExpanded(True)
        self.summary_tree.expandAll()
        self.calculate_total()

    def build_tree_from_db_data(self, items: List[Dict]):
        """从数据库数据构建树形结构"""
        self.summary_tree.clear()

        if not items:
            # print("[构建树] 没有数据")
            return

        # print(f"[构建树] 开始构建，共 {len(items)} 条数据")
        # print(f"[构建树] 原始数据: {items}")

        # 创建ID到树节点的映射
        id_to_tree_item = {}

        for item_data in items:
            db_id = item_data.get('id')
            parent_id = item_data.get('parent_id')
            item_type = item_data.get('item_type', 'item')
            sequence = str(item_data.get('sequence', ''))
            name = str(item_data.get('name', ''))

            # print(f"[构建树] 处理: id={db_id}, parent_id={parent_id}, parent_id in mapping={parent_id in id_to_tree_item if parent_id else False}, name={name[:20] if name else ''}")

            # 创建SummaryItem
            summary_item = SummaryItem(
                id=db_id or 0,  # 设置数据库ID
                summary_id=item_data.get('summary_id', 0),
                parent_id=parent_id,
                item_type=SummaryItemType.CATEGORY if item_type == 'category' else SummaryItemType.ITEM,
                sequence=sequence,
                name=name,
                quote_price=float(item_data.get('quote_price', 0)),
                main_material_fee=float(item_data.get('main_material_fee', 0)),
                aux_material_fee=float(item_data.get('aux_material_fee', 0)),
                labor_fee=float(item_data.get('labor_fee', 0)),
                machinery_fee=float(item_data.get('machinery_fee', 0)),
                other_fee=float(item_data.get('other_fee', 0)),
                management_fee=float(item_data.get('management_fee', 0)),
                tax_fee=float(item_data.get('tax_fee', 0)),
            )

            # 创建树节点
            if parent_id is not None and parent_id in id_to_tree_item:
                # 有父节点，作为子节点添加
                parent_tree_item = id_to_tree_item[parent_id]
                tree_item = QTreeWidgetItem(parent_tree_item)
                parent_tree_item.setExpanded(True)
                # print(f"[构建树]   -> 作为子节点添加到 parent_id={parent_id}")
            else:
                # 没有父节点或父节点不存在，作为顶级节点添加
                tree_item = QTreeWidgetItem(self.summary_tree)
                # print(f"[构建树]   -> 作为顶级节点 (parent_id={parent_id}, 是否在映射中: {parent_id in id_to_tree_item if parent_id else 'N/A'})")

            self.update_tree_item(tree_item, summary_item)

            # 保存ID映射
            if db_id:
                id_to_tree_item[db_id] = tree_item
                # print(f"[构建树]   -> 保存映射: db_id={db_id}")

        # 展开所有节点
        self.summary_tree.expandAll()
        self.calculate_total()
        # print(f"[构建树] 构建完成，树节点数: {self.summary_tree.topLevelItemCount()}")

    def move_item_level_up(self):
        """提升节点层级（变为父节点的兄弟）- 支持多选批量操作"""
        selected_items = self.summary_tree.selectedItems()
        if not selected_items:
            MessageDialog.warning(self, "提示", "请先选择要提升层级的节点")
            return

        # 过滤掉无法提升的节点（根节点）
        movable_items = []
        for item in selected_items:
            if item.parent() is not None:
                movable_items.append(item)

        if not movable_items:
            MessageDialog.warning(self, "提示", "选中的节点都是根节点，无法提升层级")
            return

        if len(movable_items) < len(selected_items):
            MessageDialog.information(self, "提示", f"已跳过 {len(selected_items) - len(movable_items)} 个根节点")

        # 按在树中的位置排序（从上到下），确保处理顺序正确
        movable_items.sort(key=lambda item: self._get_item_sort_key(item))

        # 批量提升
        new_items = []
        for item in movable_items:
            new_item = self._move_single_item_level_up(item)
            if new_item:
                new_items.append(new_item)

        # 重新选中所有新节点
        if new_items:
            self.summary_tree.clearSelection()
            for new_item in new_items:
                new_item.setSelected(True)
            self.summary_tree.setCurrentItem(new_items[-1])

        self.calculate_total()

    def _move_single_item_level_up(self, item: QTreeWidgetItem) -> QTreeWidgetItem:
        """提升单个节点的层级"""
        parent = item.parent()
        if not parent:
            return None

        grandparent = parent.parent()
        new_item = QTreeWidgetItem()
        self.copy_tree_item(item, new_item)

        if not grandparent:
            # 变为根节点
            index = self.summary_tree.indexOfTopLevelItem(parent)
            self.summary_tree.insertTopLevelItem(index + 1, new_item)
        else:
            # 插入到父节点的后面
            parent_index = grandparent.indexOfChild(parent)
            grandparent.insertChild(parent_index + 1, new_item)

        # 删除原节点
        parent.removeChild(item)

        return new_item

    def move_item_level_down(self):
        """降低节点层级（变为前一个兄弟的子节点）- 支持多选批量操作"""
        selected_items = self.summary_tree.selectedItems()
        if not selected_items:
            MessageDialog.warning(self, "提示", "请先选择要降低层级的节点")
            return

        # 过滤掉无法降低的节点（每个父节点下的第一个子节点）
        movable_items = []
        for item in selected_items:
            parent = item.parent()
            if parent:
                # 有父节点，检查是否是第一个子节点
                index = parent.indexOfChild(item)
                if index > 0:
                    movable_items.append(item)
            else:
                # 根节点，检查是否是第一个根节点
                index = self.summary_tree.indexOfTopLevelItem(item)
                if index > 0:
                    movable_items.append(item)

        if not movable_items:
            MessageDialog.warning(self, "提示", "选中的节点都是第一个子节点，无法降低层级")
            return

        if len(movable_items) < len(selected_items):
            MessageDialog.information(self, "提示", f"已跳过 {len(selected_items) - len(movable_items)} 个第一个子节点")

        # 按在树中的位置排序（从上到下），确保处理顺序正确
        movable_items.sort(key=lambda item: self._get_item_sort_key(item))

        # 批量降低
        new_items = []
        for item in movable_items:
            new_item = self._move_single_item_level_down(item)
            if new_item:
                new_items.append(new_item)

        # 重新选中所有新节点
        if new_items:
            self.summary_tree.clearSelection()
            for new_item in new_items:
                new_item.setSelected(True)
            self.summary_tree.setCurrentItem(new_items[-1])

        self.calculate_total()

    def _move_single_item_level_down(self, item: QTreeWidgetItem) -> QTreeWidgetItem:
        """降低单个节点的层级"""
        parent = item.parent()
        new_item = QTreeWidgetItem()
        self.copy_tree_item(item, new_item)

        if not parent:
            # 根节点，找前一个根节点
            index = self.summary_tree.indexOfTopLevelItem(item)
            prev_sibling = self.summary_tree.topLevelItem(index - 1)
            prev_sibling.addChild(new_item)
            prev_sibling.setExpanded(True)
            self.summary_tree.takeTopLevelItem(index)
        else:
            # 找前一个兄弟
            index = parent.indexOfChild(item)
            prev_sibling = parent.child(index - 1)
            prev_sibling.addChild(new_item)
            prev_sibling.setExpanded(True)
            parent.removeChild(item)

        return new_item

    def _get_item_sort_key(self, item: QTreeWidgetItem) -> tuple:
        """获取节点的排序键，用于确定节点在树中的位置顺序"""
        key = []

        # 获取从根到该节点的路径
        current = item
        path = []
        while current:
            parent = current.parent()
            if parent:
                path.append(parent.indexOfChild(current))
            else:
                path.append(self.summary_tree.indexOfTopLevelItem(current))
            current = parent

        # 反转路径，从根开始
        path.reverse()

        # 填充路径，确保可以比较
        # 根节点层级为0，子节点层级递增
        max_depth = 10  # 假设最大深度为10
        result = []
        for i in range(max_depth):
            if i < len(path):
                result.append(path[i])
            else:
                result.append(-1)  # -1 表示该层级不存在

        return tuple(result)

    def copy_tree_item(self, source: QTreeWidgetItem, target: QTreeWidgetItem):
        """复制树节点数据 - 并重新应用样式"""
        # 复制数据
        item_data = source.data(0, Qt.UserRole)
        if item_data:
            # 使用 update_tree_item 重新应用样式（包括图标和颜色）
            self.update_tree_item(target, item_data)
        else:
            # 如果没有数据，简单复制文本
            for col in range(self.summary_tree.columnCount()):
                target.setText(col, source.text(col))

        # 递归复制子节点
        for i in range(source.childCount()):
            child = QTreeWidgetItem(target)
            self.copy_tree_item(source.child(i), child)

    def load_default_template(self):
        """加载默认模板"""
        self.summary_tree.clear()

        template = SummaryTemplate.get_default_template()

        for cat_data in template:
            # 创建章节节点
            category_item = SummaryItem(
                item_type=SummaryItemType.CATEGORY,
                sequence=cat_data['sequence'],
                name=cat_data['name'],
            )

            # 添加子项目
            for child_data in cat_data.get('children', []):
                child_item = SummaryItem(
                    item_type=SummaryItemType.ITEM,
                    sequence=child_data['sequence'],
                    name=child_data['name'],
                )
                category_item.children.append(child_item)

            # 添加到树
            tree_item = QTreeWidgetItem(self.summary_tree)
            self.update_tree_item(tree_item, category_item)

            for child in category_item.children:
                child_tree_item = QTreeWidgetItem(tree_item)
                self.update_tree_item(child_tree_item, child)

        self.summary_tree.expandAll()
        self.calculate_total()

    def update_tree_item(self, tree_item: QTreeWidgetItem, item: SummaryItem):
        """更新树节点显示 - 使用QSS样式"""
        # 列顺序：0-工程项目及费用名称, 1-序号, 2-报价, 3-主材费, 4-辅材费, 5-人工费, 6-机械费, 7-其他费, 8-管理费, 9-税金
        tree_item.setText(0, item.name)  # 第一列：工程项目及费用名称（显示树形缩进）
        tree_item.setText(1, item.sequence)  # 第二列：序号
        tree_item.setText(2, f"{item.quote_price:,.2f}")
        tree_item.setText(3, f"{item.main_material_fee:,.2f}")
        tree_item.setText(4, f"{item.aux_material_fee:,.2f}")
        tree_item.setText(5, f"{item.labor_fee:,.2f}")
        tree_item.setText(6, f"{item.machinery_fee:,.2f}")
        tree_item.setText(7, f"{item.other_fee:,.2f}")
        tree_item.setText(8, f"{item.management_fee:,.2f}")
        tree_item.setText(9, f"{item.tax_fee:,.2f}")

        # 存储数据
        tree_item.setData(0, Qt.UserRole, item)

        # 章节节点使用粗体（其他样式由QSS控制）
        if item.item_type == SummaryItemType.CATEGORY:
            font = QFont("Microsoft YaHei", 10, QFont.Bold)
            for col in range(10):
                tree_item.setFont(col, font)

        # 设置文本对齐
        tree_item.setTextAlignment(1, Qt.AlignCenter)  # 序号居中
        for col in range(2, 10):
            tree_item.setTextAlignment(col, Qt.AlignRight | Qt.AlignVCenter)

    def _get_item_level(self, tree_item: QTreeWidgetItem) -> int:
        """获取节点的层级（1开始）"""
        level = 1
        parent = tree_item.parent()
        while parent:
            level += 1
            parent = parent.parent()
        return level

    def add_item(self, item_type: SummaryItemType):
        """添加节点"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 获取当前选中的节点
        current = self.summary_tree.currentItem()

        if item_type == SummaryItemType.CATEGORY:
            # 添加章节（根节点）
            tree_item = QTreeWidgetItem(self.summary_tree)
            item = SummaryItem(
                item_type=SummaryItemType.CATEGORY,
                sequence=self.get_next_sequence(),
                name="新章节",
            )
        else:
            # 添加项目
            if current:
                # 作为子节点添加
                tree_item = QTreeWidgetItem(current)
                item = SummaryItem(
                    item_type=SummaryItemType.ITEM,
                    sequence=self.get_next_child_sequence(current),
                    name="新项目",
                )
                current.setExpanded(True)
            else:
                # 添加到根
                tree_item = QTreeWidgetItem(self.summary_tree)
                item = SummaryItem(
                    item_type=SummaryItemType.ITEM,
                    sequence=self.get_next_sequence(),
                    name="新项目",
                )

        self.update_tree_item(tree_item, item)
        self.summary_tree.setCurrentItem(tree_item)
        self.calculate_total()

    def add_child_item(self):
        """添加子项目"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        current = self.summary_tree.currentItem()
        if not current:
            MessageDialog.warning(self, "提示", "请先选择一个节点")
            return

        tree_item = QTreeWidgetItem(current)
        item = SummaryItem(
            item_type=SummaryItemType.ITEM,
            sequence=self.get_next_child_sequence(current),
            name="新项目",
        )
        self.update_tree_item(tree_item, item)
        current.setExpanded(True)
        self.summary_tree.setCurrentItem(tree_item)
        self.calculate_total()

    def delete_item(self):
        """删除节点 - 支持多选批量删除"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        selected_items = self.summary_tree.selectedItems()
        if not selected_items:
            MessageDialog.warning(self, "提示", "请先选择要删除的节点")
            return

        # 统计信息
        category_count = 0
        item_count = 0
        for item in selected_items:
            summary_item = item.data(0, Qt.UserRole)
            if summary_item:
                if summary_item.item_type == SummaryItemType.CATEGORY:
                    category_count += 1
                    # 统计子项目数量
                    item_count += self._count_child_items(item)
                else:
                    item_count += 1

        # 构建提示信息
        msg_parts = []
        if category_count > 0:
            msg_parts.append(f"{category_count} 个章节")
        if item_count > 0:
            msg_parts.append(f"{item_count} 个项目")

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected_items)} 个节点吗？\n"
            f"包含: {', '.join(msg_parts)}\n\n"
            f"注意：删除章节将同时删除其下的所有子项目！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 按在树中的位置排序（从下到上），确保删除不影响其他节点的位置
            items_to_delete = sorted(selected_items, key=lambda item: self._get_item_sort_key(item), reverse=True)

            for item in items_to_delete:
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    index = self.summary_tree.indexOfTopLevelItem(item)
                    self.summary_tree.takeTopLevelItem(index)

            self.calculate_total()

    def _count_child_items(self, item: QTreeWidgetItem) -> int:
        """统计节点的所有子项目数量（递归）"""
        count = 0
        for i in range(item.childCount()):
            child = item.child(i)
            summary_child = child.data(0, Qt.UserRole)
            if summary_child:
                if summary_child.item_type == SummaryItemType.CATEGORY:
                    count += self._count_child_items(child)
                else:
                    count += 1
        return count

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        menu.setObjectName("contextMenu")

        # 层级操作
        level_up_action = QAction("⬆️ 提升层级", self)
        level_up_action.triggered.connect(self.move_item_level_up)
        menu.addAction(level_up_action)

        level_down_action = QAction("⬇️ 降低层级", self)
        level_down_action.triggered.connect(self.move_item_level_down)
        menu.addAction(level_down_action)

        menu.addSeparator()

        # 添加操作
        add_category_action = QAction("➕ 添加父级", self)
        add_category_action.triggered.connect(lambda: self.add_item(SummaryItemType.CATEGORY))
        menu.addAction(add_category_action)

        add_child_action = QAction("➕ 添加子级", self)
        add_child_action.triggered.connect(self.add_child_item)
        menu.addAction(add_child_action)

        menu.addSeparator()

        # 删除操作
        delete_action = QAction("🗑️ 删除", self)
        delete_action.triggered.connect(self.delete_item)
        menu.addAction(delete_action)

        # 清空操作
        clear_action = QAction("🗑️ 清空全部", self)
        clear_action.triggered.connect(self.clear_all)
        menu.addAction(clear_action)

        menu.exec(self.summary_tree.viewport().mapToGlobal(position))

    def reset_all_to_level_one(self):
        """将所有节点重置为级别1，保持原有顺序"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 收集所有节点数据（按当前顺序）
        all_items_data = []

        def collect_items(item: QTreeWidgetItem):
            """递归收集所有节点数据"""
            summary_item = item.data(0, Qt.UserRole)  # 第0列存储数据
            
            if summary_item:
                # 创建数据副本
                item_data = {
                    'sequence': summary_item.sequence,
                    'name': summary_item.name,
                    'quote_price': summary_item.quote_price,
                    'main_material_fee': summary_item.main_material_fee,
                    'aux_material_fee': summary_item.aux_material_fee,
                    'labor_fee': summary_item.labor_fee,
                    'machinery_fee': summary_item.machinery_fee,
                    'other_fee': summary_item.other_fee,
                    'management_fee': summary_item.management_fee,
                    'tax_fee': summary_item.tax_fee,
                }
                all_items_data.append(item_data)
            else:
                # 如果没有数据，尝试从文本读取
                name = item.text(0)  # 第0列是名称
                sequence = item.text(1)  # 第1列是序号
                if name and name.strip():
                    item_data = {
                        'sequence': sequence,
                        'name': name,
                        'quote_price': 0.0,
                        'main_material_fee': 0.0,
                        'aux_material_fee': 0.0,
                        'labor_fee': 0.0,
                        'machinery_fee': 0.0,
                        'other_fee': 0.0,
                        'management_fee': 0.0,
                        'tax_fee': 0.0,
                    }
                    all_items_data.append(item_data)

            # 递归收集子节点
            for i in range(item.childCount()):
                collect_items(item.child(i))

        # 从根节点开始收集
        for i in range(self.summary_tree.topLevelItemCount()):
            collect_items(self.summary_tree.topLevelItem(i))

        if not all_items_data:
            MessageDialog.information(self, "提示", "没有数据需要重置")
            return

        # 确认对话框
        reply = QMessageBox.question(
            self, "确认重置",
            f"确定要将所有 {len(all_items_data)} 个节点重置为级别1吗？\n"
            f"这将保持原有顺序，但所有节点都变为平级。",
            MessageDialog.Yes | MessageDialog.No,
            MessageDialog.No
        )

        if reply != MessageDialog.Yes:
            return

        # 清空树
        self.summary_tree.clear()

        # 重新创建所有节点作为级别1（根节点）
        for i, data in enumerate(all_items_data):
            # 创建新的SummaryItem，类型改为ITEM
            new_item = SummaryItem(
                item_type=SummaryItemType.ITEM,
                sequence=str(i + 1),  # 重新编号
                name=data['name'],
                quote_price=data['quote_price'],
                main_material_fee=data['main_material_fee'],
                aux_material_fee=data['aux_material_fee'],
                labor_fee=data['labor_fee'],
                machinery_fee=data['machinery_fee'],
                other_fee=data['other_fee'],
                management_fee=data['management_fee'],
                tax_fee=data['tax_fee'],
            )

            # 创建树节点
            tree_item = QTreeWidgetItem(self.summary_tree)
            self.update_tree_item(tree_item, new_item)

        self.calculate_total()
        MessageDialog.information(self, "成功", f"已重置 {len(all_items_data)} 个节点为级别1")

    def clear_all(self):
        """清空全部"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        reply = MessageDialog.question(self, "确认清空", "确定要清空所有项目吗？\n此操作不可恢复！", MessageDialog.Yes | MessageDialog.No,
            MessageDialog.No
        )

        if reply == MessageDialog.Yes:
            self.summary_tree.clear()
            self.calculate_total()

    def on_item_selected(self):
        """节点选中事件"""
        current = self.summary_tree.currentItem()
        if not current:
            return

        item = current.data(0, Qt.UserRole)
        if not item:
            return

        # 更新编辑面板
        self.seq_input.setText(item.sequence)
        self.name_input.setText(item.name)
        self.main_material_input.setValue(item.main_material_fee)
        self.aux_material_input.setValue(item.aux_material_fee)
        self.labor_input.setValue(item.labor_fee)
        self.machinery_input.setValue(item.machinery_fee)
        self.other_input.setValue(item.other_fee)
        self.management_input.setValue(item.management_fee)
        self.tax_input.setValue(item.tax_fee)
        self.quote_label.setText(f"¥ {item.quote_price:,.2f}")

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """节点编辑事件"""
        summary_item = item.data(0, Qt.UserRole)
        if not summary_item:
            return

        # 列顺序：0-工程项目及费用名称, 1-序号, 2-报价, ...
        if column == 0:
            summary_item.name = item.text(0)  # 第0列是名称
        elif column == 1:
            summary_item.sequence = item.text(1)  # 第1列是序号
        elif column == 2:
            try:
                summary_item.quote_price = float(item.text(2).replace(',', '') or 0)
            except:
                pass
        elif column == 3:
            try:
                summary_item.main_material_fee = float(item.text(3).replace(',', '') or 0)
            except:
                pass
        elif column == 4:
            try:
                summary_item.aux_material_fee = float(item.text(4).replace(',', '') or 0)
            except:
                pass
        elif column == 5:
            try:
                summary_item.labor_fee = float(item.text(5).replace(',', '') or 0)
            except:
                pass
        elif column == 6:
            try:
                summary_item.machinery_fee = float(item.text(6).replace(',', '') or 0)
            except:
                pass
        elif column == 7:
            try:
                summary_item.other_fee = float(item.text(7).replace(',', '') or 0)
            except:
                pass
        elif column == 8:
            try:
                summary_item.management_fee = float(item.text(8).replace(',', '') or 0)
            except:
                pass
        elif column == 9:
            try:
                summary_item.tax_fee = float(item.text(9).replace(',', '') or 0)
            except:
                pass

        # 重新计算报价
        summary_item.calculate_quote_price()
        item.setText(2, f"{summary_item.quote_price:,.2f}")
        self.calculate_total()

    def on_data_link(self):
        """打开数据关联对话框"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 收集汇总表数据
        summary_items = self._collect_tree_data(self.summary_tree)

        if not summary_items:
            MessageDialog.warning(self, "提示", "汇总表数据为空，无法建立关联")
            return

        # 收集明细表数据（从数据库加载所有有明细数据的汇总项）
        detail_items = self._load_all_detail_items()

        if not detail_items:
            MessageDialog.warning(self, "提示", "明细表数据为空，请先导入明细数据")
            return

        # 加载已保存的关联关系
        existing_links = self._load_data_links()

        # 打开数据关联对话框
        from .data_link_dialog import DataLinkDialog
        dialog = DataLinkDialog(summary_items, detail_items, existing_links, self)

        if dialog.exec() == QDialog.Accepted:
            # 获取关联关系
            links = dialog.get_links()
            print(f"[数据关联] 建立了 {len(links)} 对关联")

            # 保存关联关系到数据库
            self._save_data_links(links)

            MessageDialog.information(
                self,
                "关联完成",
                f"成功建立 {len(links)} 对数据关联"
            )

    def _get_current_summary_version(self) -> str:
        """获取当前汇总表版本号"""
        current_version_text = self.version_combo.currentText()
        if not current_version_text or current_version_text == "无版本":
            return "V1.0"
        # 从文本中提取版本号，格式如 "V1.0 - 初始版本"
        version = current_version_text.split(' - ')[0] if ' - ' in current_version_text else current_version_text
        return version

    def _save_data_links(self, links: dict):
        """保存关联关系到数据库"""
        if not self.current_bidding_id:
            return

        # 从 parent_page 获取 db_manager
        db_manager = None
        if self.parent_page and hasattr(self.parent_page, 'bidding_manager'):
            db_manager = self.parent_page.bidding_manager.db_manager

        if not db_manager:
            print("[数据关联] 错误：无法获取数据库连接")
            return

        # 获取当前版本号
        summary_version = self._get_current_summary_version()
        print(f"[数据关联] 当前汇总表版本: {summary_version}")

        # 创建 DataLinkDatabase 实例
        link_db = DataLinkDatabase(db_manager)

        # 初始化表（如果不存在）
        link_db.init_tables()

        # 保存关联关系（带版本信息）
        success = link_db.save_links(self.current_bidding_id, links, summary_version)
        if success:
            print(f"[数据关联] 成功保存 {len(links)} 对关联到数据库（版本: {summary_version}）")
            # 根据关联关系更新汇总表数据
            self._update_summary_from_links(links)
        else:
            print("[数据关联] 保存关联关系失败")

    def _update_summary_from_links(self, links: dict):
        """根据关联关系更新汇总表数据"""
        if not links:
            return

        print(f"[数据关联] 开始更新汇总表数据，关联数: {len(links)}")

        # 从 parent_page 获取 db_manager
        db_manager = None
        if self.parent_page and hasattr(self.parent_page, 'bidding_manager'):
            db_manager = self.parent_page.bidding_manager.db_manager

        if not db_manager:
            print("[数据关联] 错误：无法获取数据库连接")
            return

        # 创建 DetailManager 实例
        detail_manager = DetailManager(db_manager)

        # 遍历所有关联，计算明细合价并更新汇总表
        for summary_item_id, detail_item_id in links.items():
            try:
                print(f"[数据关联] 处理关联: 汇总项 {summary_item_id} -> 明细项 {detail_item_id}")

                # 获取汇总项对应的明细数据
                detail = detail_manager.get_detail_by_summary_item(
                    self.current_bidding_id, summary_item_id
                )

                if not detail:
                    print(f"[数据关联] 警告: 汇总项 {summary_item_id} 没有对应的明细数据")
                    continue

                if not detail.items:
                    print(f"[数据关联] 警告: 汇总项 {summary_item_id} 的明细数据为空")
                    continue

                print(f"[数据关联] 汇总项 {summary_item_id} 有 {len(detail.items)} 个明细根项")

                # 在明细项中查找关联的明细项及其子项
                total_price = self._calculate_linked_detail_total(
                    detail.items, detail_item_id
                )

                print(f"[数据关联] 计算得到的合价: {total_price}")

                if total_price > 0:
                    # 更新汇总表的报价
                    self._update_summary_item_price(summary_item_id, total_price)
                    print(f"[数据关联] 更新汇总项 {summary_item_id} 的报价为 {total_price}")
                else:
                    print(f"[数据关联] 警告: 汇总项 {summary_item_id} 的计算合价为0，不更新")

            except Exception as e:
                print(f"[数据关联] 更新汇总项 {summary_item_id} 失败: {e}")
                import traceback
                traceback.print_exc()

        # 刷新汇总表显示
        self.refresh_summary_display()

    def _calculate_linked_detail_total(self, detail_items, linked_detail_id) -> float:
        """计算关联明细项及其子项的合价总和"""
        total = 0.0
        found = False

        def find_and_sum(items, target_id):
            nonlocal total, found
            for item in items:
                if item.id == target_id:
                    # 找到目标项，累加其合价
                    total += item.total_price
                    print(f"[数据关联] 找到明细项 {target_id}, 合价: {item.total_price}")
                    # 累加所有子项的合价
                    if item.children:
                        for child in item.children:
                            total += child.total_price
                            print(f"[数据关联] 累加子项 {child.id}, 合价: {child.total_price}")
                            # 递归累加孙项
                            if child.children:
                                sum_children_recursive(child.children)
                    found = True
                    return True
                # 递归查找子项
                if item.children:
                    if find_and_sum(item.children, target_id):
                        return True
            return False

        def sum_children_recursive(children):
            """递归累加所有子项的合价"""
            nonlocal total
            for child in children:
                total += child.total_price
                print(f"[数据关联] 累加孙项 {child.id}, 合价: {child.total_price}")
                if child.children:
                    sum_children_recursive(child.children)

        find_and_sum(detail_items, linked_detail_id)

        if not found:
            print(f"[数据关联] 警告: 未找到明细项 {linked_detail_id}")

        return total

    def _update_summary_item_price(self, summary_item_id: int, total_price: float):
        """更新汇总表项目的报价"""
        def update_tree_item(tree_item):
            data_obj = tree_item.data(0, Qt.UserRole)
            if data_obj and hasattr(data_obj, 'id') and data_obj.id == summary_item_id:
                # 更新报价
                data_obj.quote_price = total_price
                # 更新显示
                tree_item.setText(2, f"{total_price:,.2f}")
                return True

            # 递归处理子节点
            for i in range(tree_item.childCount()):
                if update_tree_item(tree_item.child(i)):
                    return True
            return False

        # 遍历顶层节点
        for i in range(self.summary_tree.topLevelItemCount()):
            if update_tree_item(self.summary_tree.topLevelItem(i)):
                break

    def refresh_summary_display(self):
        """刷新汇总表显示"""
        # 重新计算总价
        self.calculate_total()

    def _load_data_links(self) -> dict:
        """从数据库加载关联关系"""
        if not self.current_bidding_id:
            return {}

        # 从 parent_page 获取 db_manager
        db_manager = None
        if self.parent_page and hasattr(self.parent_page, 'bidding_manager'):
            db_manager = self.parent_page.bidding_manager.db_manager

        if not db_manager:
            return {}

        # 获取当前版本号
        summary_version = self._get_current_summary_version()

        # 创建 DataLinkDatabase 实例
        link_db = DataLinkDatabase(db_manager)

        # 加载关联关系（带版本信息）
        links = link_db.get_links_by_bidding(self.current_bidding_id, summary_version)
        print(f"[数据关联] 从数据库加载了 {len(links)} 对关联（版本: {summary_version}）")
        return links

    def _load_all_detail_items(self):
        """从数据库加载所有明细数据"""
        detail_items = []

        # 获取所有汇总项ID
        summary_ids = self._get_all_summary_item_ids()
        print(f"[数据关联] 找到 {len(summary_ids)} 个汇总项")

        if not summary_ids:
            return detail_items

        # 从 parent_page 获取 db_manager
        db_manager = None
        if self.parent_page and hasattr(self.parent_page, 'bidding_manager'):
            db_manager = self.parent_page.bidding_manager.db_manager

        if not db_manager:
            print("[数据关联] 错误：无法获取数据库连接")
            return detail_items

        # 创建 DetailManager 实例，传入 db_manager
        detail_manager = DetailManager(db_manager)

        # 遍历所有汇总项，获取对应的明细数据
        for summary_id in summary_ids:
            try:
                detail = detail_manager.get_detail_by_summary_item(
                    self.current_bidding_id, summary_id
                )
                if detail and detail.items:
                    print(f"[数据关联] 汇总项 {summary_id} 有 {len(detail.items)} 个明细项")
                    # 将明细数据转换为字典格式
                    for item in detail.items:
                        detail_dict = self._detail_item_to_dict(item)
                        if detail_dict:
                            detail_items.append(detail_dict)
                else:
                    print(f"[数据关联] 汇总项 {summary_id} 没有明细数据")
            except Exception as e:
                print(f"[数据关联] 加载汇总项 {summary_id} 的明细数据失败: {e}")

        print(f"[数据关联] 总共加载 {len(detail_items)} 个明细项")
        return detail_items

    def _get_all_summary_item_ids(self):
        """获取所有汇总项的ID"""
        ids = []

        def collect_ids(tree_item):
            data_obj = tree_item.data(0, Qt.UserRole)
            if data_obj and hasattr(data_obj, 'id'):
                ids.append(data_obj.id)

            # 递归处理子节点
            for i in range(tree_item.childCount()):
                collect_ids(tree_item.child(i))

        # 遍历顶层节点
        for i in range(self.summary_tree.topLevelItemCount()):
            collect_ids(self.summary_tree.topLevelItem(i))

        return ids

    def _detail_item_to_dict(self, item):
        """将 DetailItem 转换为字典"""
        if not item:
            return None

        result = {
            'id': item.id,
            'name': item.name,
            'sequence': item.sequence,
            'level': item.level,
            'children': []
        }

        # 递归处理子节点
        if item.children:
            for child in item.children:
                child_dict = self._detail_item_to_dict(child)
                if child_dict:
                    result['children'].append(child_dict)

        return result

    def _collect_tree_data(self, tree_widget):
        """将树形控件数据转换为字典列表"""
        items = []

        def convert_item(tree_item):
            # 从 SummaryItem/DetailItem 对象获取数据
            data_obj = tree_item.data(0, Qt.UserRole)

            # 获取级别
            level = 1
            if hasattr(data_obj, 'level'):
                level = data_obj.level
            elif hasattr(data_obj, 'item_type'):
                # SummaryItem 使用 item_type 判断级别
                if data_obj.item_type.value == 'category':
                    level = 1
                elif data_obj.item_type.value == 'subcategory':
                    level = 2
                else:
                    level = 3

            # 判断是汇总表还是明细表
            header_text = tree_item.treeWidget().headerItem().text(0)
            is_summary = header_text == '工程项目及费用名称'
            is_detail = header_text == ''

            if is_summary:
                # 汇总表：列0是名称，列1是序号
                item_data = {
                    'id': getattr(data_obj, 'id', None),
                    'name': tree_item.text(0),
                    'sequence': tree_item.text(1),
                    'level': level,
                    'children': []
                }
            elif is_detail:
                # 明细表：列0是空，列1是序号，列2是名称
                item_data = {
                    'id': getattr(data_obj, 'id', None),
                    'sequence': tree_item.text(1),
                    'name': tree_item.text(2),
                    'level': level,
                    'children': []
                }
            else:
                # 默认
                item_data = {
                    'id': getattr(data_obj, 'id', None),
                    'name': tree_item.text(0),
                    'sequence': tree_item.text(1) if tree_item.treeWidget().columnCount() > 1 else '',
                    'level': level,
                    'children': []
                }

            # 递归处理子节点
            for i in range(tree_item.childCount()):
                child_data = convert_item(tree_item.child(i))
                item_data['children'].append(child_data)

            return item_data

        # 遍历顶层节点
        for i in range(tree_widget.topLevelItemCount()):
            items.append(convert_item(tree_widget.topLevelItem(i)))

        return items

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """节点双击事件 - 跳转到投标明细页签"""
        summary_item = item.data(0, Qt.UserRole)
        if not summary_item:
            return

        # 获取当前选中的投标信息
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 获取工程项目及费用名称
        project_item_name = summary_item.name

        # 通知父页面切换到明细页签，并传递选中的汇总项信息
        self.parent_page.switch_to_detail_tab(
            self.current_bidding_id,
            self.current_bidding_code,
            self.current_bidding_name,
            project_item_name,
            summary_item
        )

    def calculate_quote_price(self):
        """计算当前编辑项的报价"""
        main_material = self.main_material_input.value()
        aux_material = self.aux_material_input.value()
        labor = self.labor_input.value()
        machinery = self.machinery_input.value()
        other = self.other_input.value()
        management = self.management_input.value()
        tax = self.tax_input.value()

        quote = main_material + aux_material + labor + machinery + other + management + tax
        self.quote_label.setText(f"¥ {quote:,.2f}")

    def apply_edit(self):
        """应用编辑"""
        current = self.summary_tree.currentItem()
        if not current:
            MessageDialog.warning(self, "提示", "请先选择一个节点")
            return

        item = current.data(0, Qt.UserRole)
        if not item:
            return

        # 更新数据
        item.sequence = self.seq_input.text()
        item.name = self.name_input.text()
        item.main_material_fee = self.main_material_input.value()
        item.aux_material_fee = self.aux_material_input.value()
        item.labor_fee = self.labor_input.value()
        item.machinery_fee = self.machinery_input.value()
        item.other_fee = self.other_input.value()
        item.management_fee = self.management_input.value()
        item.tax_fee = self.tax_input.value()
        item.calculate_quote_price()

        # 更新显示
        self.update_tree_item(current, item)
        self.calculate_total()

        MessageDialog.information(self, "成功", "修改已应用")

    def calculate_total(self):
        """计算总价"""
        total = 0.0

        def sum_quote(item: QTreeWidgetItem):
            nonlocal total
            summary_item = item.data(0, Qt.UserRole)
            if summary_item and summary_item.item_type == SummaryItemType.ITEM:
                total += summary_item.quote_price

            for i in range(item.childCount()):
                sum_quote(item.child(i))

        for i in range(self.summary_tree.topLevelItemCount()):
            sum_quote(self.summary_tree.topLevelItem(i))

        self.total_label.setText(f"¥ {total:,.2f}")
        return total

    def get_next_sequence(self) -> str:
        """获取下一个根节点序号"""
        count = self.summary_tree.topLevelItemCount()
        sequences = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        if count < len(sequences):
            return sequences[count]
        return f"{count + 1}"

    def get_next_child_sequence(self, parent: QTreeWidgetItem) -> str:
        """获取下一个子节点序号"""
        parent_seq = parent.text(0)
        child_count = parent.childCount()
        return f"{parent_seq}.{child_count + 1}"

    def expand_all(self):
        """展开全部"""
        self.summary_tree.expandAll()

    def collapse_all(self):
        """折叠全部"""
        self.summary_tree.collapseAll()

    def on_save(self):
        """保存汇总表到数据库"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return

        # 收集所有节点数据
        items_data = []

        def collect_items(item: QTreeWidgetItem, parent_temp_id: int = None):
            """递归收集所有节点数据"""
            summary_item = item.data(0, Qt.UserRole)
            if summary_item:
                # 生成临时ID用于父子关系映射
                temp_id = len(items_data)
                
                item_data = {
                    'temp_id': temp_id,
                    'parent_temp_id': parent_temp_id,
                    'item_type': summary_item.item_type.value,
                    'sequence': summary_item.sequence,
                    'name': summary_item.name,
                    'quote_price': summary_item.quote_price,
                    'main_material_fee': summary_item.main_material_fee,
                    'aux_material_fee': summary_item.aux_material_fee,
                    'labor_fee': summary_item.labor_fee,
                    'machinery_fee': summary_item.machinery_fee,
                    'other_fee': summary_item.other_fee,
                    'management_fee': summary_item.management_fee,
                    'tax_fee': summary_item.tax_fee,
                }
                items_data.append(item_data)

                # 递归收集子节点
                for i in range(item.childCount()):
                    collect_items(item.child(i), temp_id)

        # 从根节点开始收集
        for i in range(self.summary_tree.topLevelItemCount()):
            collect_items(self.summary_tree.topLevelItem(i))

        if not items_data:
            MessageDialog.warning(self, "提示", "没有数据需要保存")
            return

        # 获取当前版本ID
        current_version_id = self.version_combo.currentData()
        
        # 获取当前版本信息
        current_version_id = self.version_combo.currentData()
        current_version_text = self.version_combo.currentText()
        
        if current_version_id:
            # 更新当前版本
            success, result = self.bidding_manager.update_bidding_summary(
                current_version_id,
                items_data
            )
            if success:
                version_code = current_version_text.split(' - ')[0] if ' - ' in current_version_text else current_version_text
                MessageDialog.information(self, "保存成功", 
                    f"汇总表数据已保存\n"
                    f"版本: {version_code}\n"
                    f"共 {len(items_data)} 条记录")
                # 刷新版本列表显示
                self.load_version_combo()
            else:
                MessageDialog.critical(self, "错误", f"更新失败:\n{result}")
        else:
            # 没有当前版本，自动创建V1.0版本
            version = "V1.0"
            version_name = "初始版本"
            
            success, result = self.bidding_manager.save_bidding_summary(
                self.current_bidding_id,
                items_data,
                version=version,
                version_name=version_name,
                created_by="",
                remark=""
            )
            
            if success:
                MessageDialog.information(self, "保存成功", 
                    f"汇总表数据已保存\n"
                    f"版本: {version}（自动创建）\n"
                    f"共 {len(items_data)} 条记录")
                # 刷新版本列表并选中新版本
                self.load_version_combo()
                for i in range(self.version_combo.count()):
                    if self.version_combo.itemData(i) == result:
                        self.version_combo.setCurrentIndex(i)
                        break
            else:
                MessageDialog.critical(self, "错误", f"保存失败:\n{result}")

    def mark_item_with_detail(self, summary_item):
        """标记包含明细的汇总行为红色字体"""
        if not summary_item:
            print("[标记红色] summary_item 为空")
            return
        
        # 获取汇总项的ID或名称用于匹配
        target_id = getattr(summary_item, 'id', None)
        target_name = getattr(summary_item, 'name', '')
        target_sequence = getattr(summary_item, 'sequence', '')
        print(f"[标记红色] 目标: id={target_id}, name={target_name}, sequence={target_sequence}")
        
        # 遍历树形控件查找匹配的项
        print(f"[标记红色] 开始遍历树，顶层节点数: {self.summary_tree.topLevelItemCount()}")
        found = False
        
        def find_and_mark_item(parent_item=None):
            nonlocal found
            if parent_item is None:
                # 从顶层节点开始
                for i in range(self.summary_tree.topLevelItemCount()):
                    item = self.summary_tree.topLevelItem(i)
                    item_data = item.data(0, Qt.UserRole)
                    if item_data:
                        print(f"[标记红色] 检查顶层节点: {getattr(item_data, 'name', 'unknown')}")
                    if self._is_matching_item(item, target_id, target_name, target_sequence):
                        print(f"[标记红色] 找到匹配项，设置红色字体")
                        self._set_item_red_font(item)
                        found = True
                        return True
                    # 递归查找子节点
                    if find_and_mark_item(item):
                        return True
            else:
                # 查找子节点
                for i in range(parent_item.childCount()):
                    item = parent_item.child(i)
                    if self._is_matching_item(item, target_id, target_name, target_sequence):
                        print(f"[标记红色] 找到匹配项（子节点），设置红色字体")
                        self._set_item_red_font(item)
                        found = True
                        return True
                    # 递归查找子节点
                    if find_and_mark_item(item):
                        return True
            return False
        
        find_and_mark_item()
        if not found:
            print(f"[标记红色] 未找到匹配项")
    
    def _is_matching_item(self, tree_item, target_id, target_name, target_sequence):
        """检查树项是否匹配目标汇总项"""
        item_data = tree_item.data(0, Qt.UserRole)
        if not item_data:
            return False
        
        # 优先使用ID匹配
        if target_id and hasattr(item_data, 'id') and item_data.id == target_id:
            print(f"[匹配成功] ID匹配: {target_id}")
            return True
        
        # 使用名称和序号匹配
        item_name = getattr(item_data, 'name', '')
        item_sequence = getattr(item_data, 'sequence', '')
        
        matched = item_name == target_name and item_sequence == target_sequence
        if matched:
            print(f"[匹配成功] 名称序号匹配: {target_sequence} {target_name}")
        return matched
    
    def _set_item_red_font(self, tree_item):
        """设置树项为红色字体"""
        from PySide6.QtGui import QColor
        red_font = QFont("Microsoft YaHei", 10)
        red_font.setBold(True)
        
        # 设置所有列为红色字体
        for col in range(self.summary_tree.columnCount()):
            tree_item.setForeground(col, QColor("#FF0000"))
            tree_item.setFont(col, red_font)
