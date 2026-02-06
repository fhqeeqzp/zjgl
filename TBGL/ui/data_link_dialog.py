"""
数据关联对话框 - 可视化关联汇总表和明细表数据
通过连线方式建立两级数据之间的关联关系
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget,
    QTreeWidgetItem, QPushButton, QSplitter, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from difflib import SequenceMatcher

from ui.message_dialog import MessageDialog


class DataLinkDialog(QDialog):
    """数据关联对话框 - 树形结构显示"""
    def __init__(self, summary_items, detail_items, existing_links=None, parent=None):
        super().__init__(parent)
        self.setObjectName("dataLinkDialog")
        self.summary_items = summary_items  # 汇总表数据
        self.detail_items = detail_items    # 明细表数据
        self.links = existing_links if existing_links else {}  # 关联关系 {summary_id: detail_id}

        self.setWindowTitle("数据关联 - 汇总表与明细表关联")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        self.load_data()
        self.update_linked_list()  # 显示已加载的关联

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # 标题
        title_label = QLabel("数据关联管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # 说明文字
        desc_label = QLabel("操作说明：\n1. 在左侧树中选择汇总表项目（任意级别）\n2. 在右侧树中选择对应的明细表项目（任意级别）\n3. 点击【建立关联】按钮\n4. 或使用【自动匹配】根据名称相似度自动关联")
        desc_label.setObjectName("descLabel")
        layout.addWidget(desc_label)

        # 主内容区 - 使用分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧 - 汇总表树
        left_frame = QFrame()
        left_frame.setObjectName("leftFrame")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_label = QLabel("汇总表项目（费用名称）")
        left_label.setObjectName("sectionLabel")
        left_layout.addWidget(left_label)

        self.summary_tree = QTreeWidget()
        self.summary_tree.setObjectName("summaryTree")
        self.summary_tree.setHeaderLabels(["序号", "费用名称", "级别"])
        self.summary_tree.setColumnWidth(0, 80)
        self.summary_tree.setColumnWidth(1, 250)
        self.summary_tree.setColumnWidth(2, 60)
        left_layout.addWidget(self.summary_tree)

        splitter.addWidget(left_frame)

        # 中间 - 关联操作区
        center_frame = QFrame()
        center_frame.setObjectName("centerFrame")
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_layout.setAlignment(Qt.AlignCenter)

        # 已关联列表
        linked_label = QLabel("已建立的关联")
        linked_label.setObjectName("sectionLabel")
        center_layout.addWidget(linked_label)

        self.linked_list = QListWidget()
        self.linked_list.setObjectName("linkedList")
        self.linked_list.setMaximumHeight(250)
        center_layout.addWidget(self.linked_list)

        # 操作按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.setAlignment(Qt.AlignCenter)

        link_btn = QPushButton("→ 建立关联 →")
        link_btn.setObjectName("primaryButton")
        link_btn.setToolTip("将左侧选中的汇总项与右侧选中的明细项关联")
        link_btn.clicked.connect(self.on_create_link)
        btn_layout.addWidget(link_btn)

        auto_btn = QPushButton("自动匹配")
        auto_btn.setObjectName("secondaryButton")
        auto_btn.setToolTip("根据名称相似度自动建立关联")
        auto_btn.clicked.connect(self.on_auto_match)
        btn_layout.addWidget(auto_btn)

        unlink_btn = QPushButton("解除关联")
        unlink_btn.setObjectName("secondaryButton")
        unlink_btn.setToolTip("解除选中的关联")
        unlink_btn.clicked.connect(self.on_remove_link)
        btn_layout.addWidget(unlink_btn)

        clear_btn = QPushButton("清除全部")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self.on_clear_links)
        btn_layout.addWidget(clear_btn)

        center_layout.addLayout(btn_layout)
        center_layout.addStretch()

        splitter.addWidget(center_frame)

        # 右侧 - 明细表树
        right_frame = QFrame()
        right_frame.setObjectName("rightFrame")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_label = QLabel("明细表项目（分部分项名称）")
        right_label.setObjectName("sectionLabel")
        right_layout.addWidget(right_label)

        self.detail_tree = QTreeWidget()
        self.detail_tree.setObjectName("detailTree")
        self.detail_tree.setHeaderLabels(["序号", "分部分项名称", "级别"])
        self.detail_tree.setColumnWidth(0, 80)
        self.detail_tree.setColumnWidth(1, 250)
        self.detail_tree.setColumnWidth(2, 60)
        right_layout.addWidget(self.detail_tree)

        splitter.addWidget(right_frame)

        # 设置分割器比例
        splitter.setSizes([400, 250, 400])
        layout.addWidget(splitter)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_data(self):
        """加载数据到树形控件"""
        # 加载汇总表数据
        self._load_tree_data(self.summary_items, self.summary_tree)

        # 加载明细表数据
        self._load_tree_data(self.detail_items, self.detail_tree)

        # 展开所有节点
        self.summary_tree.expandAll()
        self.detail_tree.expandAll()

    def _load_tree_data(self, items, tree_widget, parent_item=None):
        """递归加载树形数据"""
        for item in items:
            if parent_item:
                tree_item = QTreeWidgetItem(parent_item)
            else:
                tree_item = QTreeWidgetItem(tree_widget)

            tree_item.setText(0, item.get('sequence', ''))
            tree_item.setText(1, item.get('name', ''))
            tree_item.setText(2, str(item.get('level', 1)))
            tree_item.setData(0, Qt.UserRole, item.get('id'))

            # 递归加载子节点
            if item.get('children'):
                self._load_tree_data(item['children'], tree_widget, tree_item)

    def _get_selected_item(self, tree_widget):
        """获取选中的节点（任何级别都可以）"""
        selected_items = tree_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0]

    def on_create_link(self):
        """创建关联"""
        # 获取选中的节点（任何级别都可以）
        summary_item = self._get_selected_item(self.summary_tree)
        detail_item = self._get_selected_item(self.detail_tree)

        if not summary_item:
            MessageDialog.warning(self, "提示", "请先选择左侧汇总表的项目")
            return

        if not detail_item:
            MessageDialog.warning(self, "提示", "请先选择右侧明细表的项目")
            return

        summary_id = summary_item.data(0, Qt.UserRole)
        summary_name = summary_item.text(1)
        detail_id = detail_item.data(0, Qt.UserRole)
        detail_name = detail_item.text(1)

        # 检查是否已有关联
        if summary_id in self.links:
            old_detail_id = self.links[summary_id]
            # 找到旧的明细项名称
            old_detail_name = self._find_item_name_by_id(self.detail_tree, old_detail_id)

            result = MessageDialog.question(
                self,
                "确认替换",
                f"【{summary_name}】已关联到【{old_detail_name}】\n\n是否替换为【{detail_name}】？",
                buttons=MessageDialog.Yes | MessageDialog.No,
                default_button=MessageDialog.No
            )

            if result != MessageDialog.Yes:
                return

        # 建立关联
        self.links[summary_id] = detail_id
        self.update_linked_list()

        MessageDialog.information(
            self,
            "关联成功",
            f"【{summary_name}】→【{detail_name}】\n关联建立成功"
        )

    def _find_item_name_by_id(self, tree_widget, item_id):
        """根据ID在树中查找项目名称"""
        def search_tree(tree_item):
            if tree_item.data(0, Qt.UserRole) == item_id:
                return tree_item.text(1)

            for i in range(tree_item.childCount()):
                result = search_tree(tree_item.child(i))
                if result:
                    return result
            return None

        for i in range(tree_widget.topLevelItemCount()):
            result = search_tree(tree_widget.topLevelItem(i))
            if result:
                return result
        return "未知"

    def on_remove_link(self):
        """解除关联"""
        current_item = self.linked_list.currentItem()
        if not current_item:
            MessageDialog.warning(self, "提示", "请先选择要解除的关联")
            return

        summary_id = current_item.data(Qt.UserRole)
        summary_name = current_item.text().split("→")[0].strip()

        if summary_id in self.links:
            del self.links[summary_id]
            self.update_linked_list()
            MessageDialog.information(self, "成功", f"已解除【{summary_name}】的关联")

    def on_auto_match(self):
        """自动匹配"""
        # 收集所有叶子节点
        summary_leaves = self._collect_leaf_items(self.summary_items)
        detail_leaves = self._collect_leaf_items(self.detail_items)

        matches = []
        for summary_id, summary_name in summary_leaves:
            best_match = None
            best_ratio = 0
            for detail_id, detail_name in detail_leaves:
                ratio = SequenceMatcher(None, summary_name, detail_name).ratio()
                if ratio > best_ratio and ratio >= 0.6:  # 阈值60%
                    best_ratio = ratio
                    best_match = (detail_id, detail_name)

            if best_match:
                matches.append((summary_id, summary_name, best_match[0], best_match[1], best_ratio))
                self.links[summary_id] = best_match[0]

        self.update_linked_list()

        if matches:
            match_info = "\n".join([f"【{s_name}】→【{d_name}】({ratio:.0%})"
                                   for _, s_name, _, d_name, ratio in matches[:10]])
            if len(matches) > 10:
                match_info += f"\n... 等共 {len(matches)} 对关联"

            MessageDialog.information(
                self,
                "自动匹配完成",
                f"成功匹配 {len(matches)} 对数据：\n\n{match_info}"
            )
        else:
            MessageDialog.information(self, "自动匹配完成", "未找到匹配的关联")

    def _collect_all_items(self, items, result=None):
        """递归收集所有节点（包括非叶子节点）"""
        if result is None:
            result = {}

        for item in items:
            # 添加当前节点
            result[item.get('id')] = item.get('name', '')

            # 递归处理子节点
            if item.get('children'):
                self._collect_all_items(item['children'], result)

        return result

    def _collect_leaf_items(self, items, result=None):
        """递归收集所有叶子节点"""
        if result is None:
            result = []

        for item in items:
            if item.get('children'):
                # 有子节点，递归处理
                self._collect_leaf_items(item['children'], result)
            else:
                # 叶子节点
                result.append((item.get('id'), item.get('name', '')))

        return result

    def update_linked_list(self):
        """更新已关联列表显示"""
        self.linked_list.clear()

        # 创建ID到名称的映射（包含所有节点）
        summary_map = self._collect_all_items(self.summary_items)
        detail_map = self._collect_all_items(self.detail_items)

        # 显示关联
        for summary_id, detail_id in self.links.items():
            summary_name = summary_map.get(summary_id, "未知")
            detail_name = detail_map.get(detail_id, "未知")

            item = QListWidgetItem(f"{summary_name} → {detail_name}")
            item.setData(Qt.UserRole, summary_id)
            self.linked_list.addItem(item)

    def on_clear_links(self):
        """清除所有关联"""
        if not self.links:
            return

        result = MessageDialog.question(
            self,
            "确认清除",
            f"确定要清除所有 {len(self.links)} 个关联吗？",
            buttons=MessageDialog.Yes | MessageDialog.No,
            default_button=MessageDialog.No
        )

        if result == MessageDialog.Yes:
            self.links.clear()
            self.update_linked_list()
            MessageDialog.information(self, "成功", "已清除所有关联")

    def get_links(self):
        """获取所有关联关系"""
        return self.links
