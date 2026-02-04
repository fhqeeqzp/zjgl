"""
汇总表编辑对话框
支持树形结构的汇总表编辑
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTreeWidget, QTreeWidgetItem, QHeaderView,
    QAbstractItemView, QLineEdit, QComboBox,
    QMessageBox, QMenu, QPushButton, QDoubleSpinBox,
    QGroupBox, QFormLayout, QWidget, QSplitter
)
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtGui import QFont, QAction

from ..data.summary_model import SummaryItem, SummaryItemType, BiddingSummary, SummaryTemplate
from ui.fluent_widgets import PushButton, PrimaryPushButton


class SummaryEditDialog(QDialog):
    """汇总表编辑对话框"""

    def __init__(self, bidding_id: int, bidding_code: str, summary: BiddingSummary = None, parent=None):
        super().__init__(parent)
        self.bidding_id = bidding_id
        self.bidding_code = bidding_code
        self.summary = summary or BiddingSummary(bidding_id=bidding_id)
        self.current_item = None  # 当前选中的节点

        self.setWindowTitle(f"编辑汇总表 - {bidding_code}")
        self.setMinimumSize(1200, 800)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 顶部信息栏
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"投标编码: {self.bidding_code}"))
        info_layout.addSpacing(30)
        info_layout.addWidget(QLabel("版本:"))
        self.version_input = QLineEdit(self.summary.version)
        self.version_input.setFixedWidth(100)
        info_layout.addWidget(self.version_input)
        info_layout.addSpacing(10)
        info_layout.addWidget(QLabel("版本名称:"))
        self.version_name_input = QLineEdit(self.summary.version_name)
        self.version_name_input.setFixedWidth(200)
        info_layout.addWidget(self.version_name_input)
        info_layout.addStretch()

        # 总价显示
        info_layout.addWidget(QLabel("总价:"))
        self.total_label = QLabel("¥ 0.00")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        info_layout.addWidget(self.total_label)

        layout.addLayout(info_layout)

        # 分割器（左侧树形，右侧编辑）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：树形控件
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        # 树形工具栏
        tree_toolbar = QHBoxLayout()
        self.expand_btn = PushButton("📂 展开全部")
        self.expand_btn.clicked.connect(self.expand_all)
        tree_toolbar.addWidget(self.expand_btn)

        self.collapse_btn = PushButton("📁 折叠全部")
        self.collapse_btn.clicked.connect(self.collapse_all)
        tree_toolbar.addWidget(self.collapse_btn)

        tree_toolbar.addStretch()

        self.add_category_btn = PrimaryPushButton("➕ 添加章节")
        self.add_category_btn.clicked.connect(lambda: self.add_item(SummaryItemType.CATEGORY))
        tree_toolbar.addWidget(self.add_category_btn)

        self.add_item_btn = PrimaryPushButton("➕ 添加项目")
        self.add_item_btn.clicked.connect(lambda: self.add_item(SummaryItemType.ITEM))
        tree_toolbar.addWidget(self.add_item_btn)

        self.delete_btn = PushButton("🗑️ 删除")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self.delete_item)
        tree_toolbar.addWidget(self.delete_btn)

        tree_layout.addLayout(tree_toolbar)

        # 树形控件
        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(["序号", "项目名称", "单位", "数量", "单价", "金额"])
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)

        # 设置列宽
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.tree.setColumnWidth(0, 60)
        self.tree.setColumnWidth(2, 80)
        self.tree.setColumnWidth(3, 100)
        self.tree.setColumnWidth(4, 120)
        self.tree.setColumnWidth(5, 150)

        # 启用编辑
        self.tree.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        # 连接信号
        self.tree.itemSelectionChanged.connect(self.on_item_selected)
        self.tree.itemChanged.connect(self.on_item_changed)

        tree_layout.addWidget(self.tree)

        splitter.addWidget(tree_widget)

        # 右侧：编辑面板
        edit_panel = QWidget()
        edit_panel.setMaximumWidth(400)
        edit_layout = QVBoxLayout(edit_panel)
        edit_layout.setContentsMargins(10, 0, 0, 0)
        edit_layout.setSpacing(15)

        # 编辑表单
        edit_group = QGroupBox("项目编辑")
        form_layout = QFormLayout(edit_group)
        form_layout.setSpacing(10)

        # 序号
        self.seq_input = QLineEdit()
        self.seq_input.setPlaceholderText("如：一、1、1.1")
        form_layout.addRow("序号:", self.seq_input)

        # 项目名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入项目名称")
        form_layout.addRow("项目名称:", self.name_input)

        # 项目类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["章节", "项目"])
        form_layout.addRow("类型:", self.type_combo)

        # 单位
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("如：m²、工日、元")
        form_layout.addRow("单位:", self.unit_input)

        # 数量
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMaximum(999999999)
        self.quantity_input.setDecimals(2)
        form_layout.addRow("数量:", self.quantity_input)

        # 单价
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("¥ ")
        form_layout.addRow("单价:", self.price_input)

        # 金额（只读）
        self.amount_label = QLabel("¥ 0.00")
        self.amount_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        form_layout.addRow("金额:", self.amount_label)

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

        # 模板按钮
        template_group = QGroupBox("快速操作")
        template_layout = QVBoxLayout(template_group)

        self.load_template_btn = PushButton("📋 加载默认模板")
        self.load_template_btn.clicked.connect(self.load_default_template)
        template_layout.addWidget(self.load_template_btn)

        self.clear_btn = PushButton("🗑️ 清空全部")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.clicked.connect(self.clear_all)
        template_layout.addWidget(self.clear_btn)

        edit_layout.addWidget(template_group)

        splitter.addWidget(edit_panel)
        splitter.setSizes([800, 400])

        layout.addWidget(splitter)

        # 底部按钮
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

        layout.addLayout(btn_layout)

    def load_data(self):
        """加载汇总表数据到树形控件"""
        self.tree.clear()

        if not self.summary.items:
            # 如果没有数据，加载默认模板
            self.load_default_template()
            return

        # 递归添加节点
        def add_tree_item(parent_widget, item: SummaryItem):
            tree_item = QTreeWidgetItem(parent_widget)
            self.update_tree_item(tree_item, item)

            # 递归添加子节点
            for child in item.children:
                add_tree_item(tree_item, child)

            return tree_item

        for item in self.summary.items:
            add_tree_item(self.tree, item)

        self.tree.expandAll()
        self.calculate_total()

    def update_tree_item(self, tree_item: QTreeWidgetItem, item: SummaryItem):
        """更新树节点显示"""
        tree_item.setText(0, item.sequence)
        tree_item.setText(1, item.name)
        tree_item.setText(2, item.unit)
        tree_item.setText(3, str(item.quantity))
        tree_item.setText(4, f"{item.unit_price:,.2f}")
        tree_item.setText(5, f"{item.amount:,.2f}")

        # 存储数据
        tree_item.setData(0, Qt.UserRole, item)

        # 章节节点使用粗体
        if item.item_type == SummaryItemType.CATEGORY:
            font = QFont("Microsoft YaHei", 10, QFont.Bold)
            for col in range(6):
                tree_item.setFont(col, font)

        # 设置文本对齐
        tree_item.setTextAlignment(0, Qt.AlignCenter)
        tree_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
        tree_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
        tree_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)

    def load_default_template(self):
        """加载默认模板"""
        self.tree.clear()

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
                    unit=child_data.get('unit', ''),
                )
                category_item.children.append(child_item)

            # 添加到树
            tree_item = QTreeWidgetItem(self.tree)
            self.update_tree_item(tree_item, category_item)

            for child in category_item.children:
                child_tree_item = QTreeWidgetItem(tree_item)
                self.update_tree_item(child_tree_item, child)

        self.tree.expandAll()
        self.calculate_total()

    def add_item(self, item_type: SummaryItemType):
        """添加节点"""
        # 获取当前选中的节点
        current = self.tree.currentItem()

        if item_type == SummaryItemType.CATEGORY:
            # 添加章节（根节点）
            tree_item = QTreeWidgetItem(self.tree)
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
                parent_item = current.data(0, Qt.UserRole)
                item = SummaryItem(
                    item_type=SummaryItemType.ITEM,
                    sequence=self.get_next_child_sequence(current),
                    name="新项目",
                    unit="",
                )
                current.setExpanded(True)
            else:
                # 添加到根
                tree_item = QTreeWidgetItem(self.tree)
                item = SummaryItem(
                    item_type=SummaryItemType.ITEM,
                    sequence=self.get_next_sequence(),
                    name="新项目",
                    unit="",
                )

        self.update_tree_item(tree_item, item)
        self.tree.setCurrentItem(tree_item)
        self.calculate_total()

    def add_child_item(self):
        """添加子项目"""
        current = self.tree.currentItem()
        if not current:
            msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("提示")
        msg_box.setText("请先选择一个节点")
        msg_box.exec()
            return

        tree_item = QTreeWidgetItem(current)
        item = SummaryItem(
            item_type=SummaryItemType.ITEM,
            sequence=self.get_next_child_sequence(current),
            name="新项目",
            unit="",
        )
        self.update_tree_item(tree_item, item)
        current.setExpanded(True)
        self.tree.setCurrentItem(tree_item)
        self.calculate_total()

    def delete_item(self):
        """删除节点"""
        current = self.tree.currentItem()
        if not current:
            msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("提示")
        msg_box.setText("请先选择要删除的节点")
        msg_box.exec()
            return

        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除选中的项目吗？\n（如果是章节，将同时删除其下的所有子项目）",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            parent = current.parent()
            if parent:
                parent.removeChild(current)
            else:
                index = self.tree.indexOfTopLevelItem(current)
                self.tree.takeTopLevelItem(index)

            self.calculate_total()

    def clear_all(self):
        """清空全部"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有项目吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.tree.clear()
            self.calculate_total()

    def on_item_selected(self):
        """节点选中事件"""
        current = self.tree.currentItem()
        if not current:
            return

        item = current.data(0, Qt.UserRole)
        if not item:
            return

        self.current_item = item

        # 更新编辑面板
        self.seq_input.setText(item.sequence)
        self.name_input.setText(item.name)
        self.type_combo.setCurrentIndex(0 if item.item_type == SummaryItemType.CATEGORY else 1)
        self.unit_input.setText(item.unit)
        self.quantity_input.setValue(item.quantity)
        self.price_input.setValue(item.unit_price)
        self.amount_label.setText(f"¥ {item.amount:,.2f}")

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """节点编辑事件"""
        # 实时更新数据
        summary_item = item.data(0, Qt.UserRole)
        if not summary_item:
            return

        if column == 0:
            summary_item.sequence = item.text(0)
        elif column == 1:
            summary_item.name = item.text(1)
        elif column == 2:
            summary_item.unit = item.text(2)
        elif column == 3:
            try:
                summary_item.quantity = float(item.text(3) or 0)
            except:
                pass
        elif column == 4:
            try:
                summary_item.unit_price = float(item.text(4).replace(',', '') or 0)
            except:
                pass

        # 重新计算金额
        summary_item.calculate_amount()
        item.setText(5, f"{summary_item.amount:,.2f}")
        self.calculate_total()

    def apply_edit(self):
        """应用编辑"""
        current = self.tree.currentItem()
        if not current:
            msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("提示")
        msg_box.setText("请先选择一个节点")
        msg_box.exec()
            return

        item = current.data(0, Qt.UserRole)
        if not item:
            return

        # 更新数据
        item.sequence = self.seq_input.text()
        item.name = self.name_input.text()
        item.item_type = SummaryItemType.CATEGORY if self.type_combo.currentIndex() == 0 else SummaryItemType.ITEM
        item.unit = self.unit_input.text()
        item.quantity = self.quantity_input.value()
        item.unit_price = self.price_input.value()
        item.calculate_amount()

        # 更新显示
        self.update_tree_item(current, item)
        self.calculate_total()

        msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("成功")
        msg_box.setText("修改已应用")
        msg_box.exec()

    def calculate_total(self):
        """计算总价"""
        total = 0.0

        def sum_amount(item: QTreeWidgetItem):
            nonlocal total
            summary_item = item.data(0, Qt.UserRole)
            if summary_item and summary_item.item_type == SummaryItemType.ITEM:
                total += summary_item.amount

            for i in range(item.childCount()):
                sum_amount(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            sum_amount(self.tree.topLevelItem(i))

        self.total_label.setText(f"¥ {total:,.2f}")
        return total

    def get_next_sequence(self) -> str:
        """获取下一个根节点序号"""
        count = self.tree.topLevelItemCount()
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
        self.tree.expandAll()

    def collapse_all(self):
        """折叠全部"""
        self.tree.collapseAll()

    def build_summary_from_tree(self) -> BiddingSummary:
        """从树形控件构建汇总表数据"""
        summary = BiddingSummary(
            id=self.summary.id,
            bidding_id=self.bidding_id,
            version=self.version_input.text(),
            version_name=self.version_name_input.text(),
        )

        def build_item(tree_item: QTreeWidgetItem, parent_id: int = None) -> SummaryItem:
            item = tree_item.data(0, Qt.UserRole)
            if not item:
                return None

            item.parent_id = parent_id

            # 递归构建子节点
            for i in range(tree_item.childCount()):
                child = build_item(tree_item.child(i), item.id)
                if child:
                    item.children.append(child)

            # 计算金额
            item.calculate_amount()

            return item

        for i in range(self.tree.topLevelItemCount()):
            item = build_item(self.tree.topLevelItem(i))
            if item:
                summary.items.append(item)

        return summary

    def on_save(self):
        """保存"""
        # 构建数据
        summary = self.build_summary_from_tree()

        # TODO: 保存到数据库
        # 这里先打印数据
        # print(f"保存汇总表: {summary.to_dict()}")

        msg_box = QMessageBox(self)
        msg_box.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("成功")
        msg_box.setText("汇总表已保存")
        msg_box.exec()
            self.accept()
