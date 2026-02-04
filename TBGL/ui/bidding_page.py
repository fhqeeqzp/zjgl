"""
投标管理页面
提供投标管理的用户界面 - 使用 QSS 主题
包含四个页签：投标信息、投标汇总表、投标明细、报表管理
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QMenu,
    QDialog, QPushButton, QTabWidget, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction

from ..logic.bidding_manager import BiddingManager
from .bidding_dialog import BiddingDialog
from .bidding_summary_tab import BiddingSummaryTab
from .bidding_detail_tab import BiddingDetailTab
from .bidding_report_tab import BiddingReportTab
from ui.fluent_widgets import PushButton, PrimaryPushButton, SearchLineEdit


class BiddingPage(QFrame):
    """投标管理页面 - 使用 QSS 主题，包含多页签"""

    def __init__(self, theme_manager=None, db_manager=None, project_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.bidding_manager = BiddingManager(db_manager, project_manager)

        # 当前选中的投标ID（用于页签间数据传递）
        self.current_bidding_id = None
        self.current_bidding_code = None

        # 初始化UI
        self.setup_ui()

        # 应用主题
        if self.theme_manager:
            self.theme_manager.add_observer(self.on_theme_changed)

        # 注册为投标管理的观察者
        self.bidding_manager.add_observer(self.on_bidding_changed)

        # 初始化数据库表
        self.bidding_manager.init_database()

        # 加载数据
        self.refresh_table()
        self.update_statistics()

    def setup_ui(self):
        """设置UI布局"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== 顶部标题栏 ==========
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)

        # ========== 分隔线 ==========
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        layout.addWidget(separator)

        # ========== 页签区域 ==========
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("biddingTabWidget")

        # 创建四个页签
        self.info_tab = self._create_info_tab()
        self.summary_tab = BiddingSummaryTab(self)
        self.detail_tab = BiddingDetailTab(self)
        self.report_tab = BiddingReportTab(self)

        # 添加页签
        self.tab_widget.addTab(self.info_tab, "📋 投标信息")
        self.tab_widget.addTab(self.summary_tab, "📊 投标汇总表")
        self.tab_widget.addTab(self.detail_tab, "📝 投标明细")
        self.tab_widget.addTab(self.report_tab, "📈 报表管理")

        # 连接页签切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tab_widget)

        # 初始化页签状态（锁定汇总表、明细、报表页签）
        self._update_tab_status()

    def _create_title_bar(self) -> QFrame:
        """创建顶部标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(60)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)

        # 标题
        self.title_label = QLabel("📋 投标管理")
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # 搜索框
        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("搜索投标编码或名称...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.on_search)
        layout.addWidget(self.search_input)

        # 搜索按钮
        self.search_btn = PushButton("🔍 搜索")
        self.search_btn.clicked.connect(self.on_search)
        layout.addWidget(self.search_btn)

        layout.addSpacing(15)

        # 新建投标按钮
        self.new_btn = PrimaryPushButton("➕ 新建投标")
        self.new_btn.clicked.connect(self.on_new_bidding)
        layout.addWidget(self.new_btn)

        return title_bar

    def _create_info_tab(self) -> QWidget:
        """创建投标信息页签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 统计卡片区域
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # 创建统计卡片
        self.stat_cards = {}
        card_configs = [
            ("投标总数", "0", "📊"),
            ("进行中", "0", "📝"),
            ("已中标", "0", "✅"),
            ("未中标", "0", "❌"),
            ("已撤回", "0", "🚫"),
        ]

        for title, value, icon in card_configs:
            card = self._create_stat_card(title, value, icon)
            stats_layout.addWidget(card)
            self.stat_cards[title] = card

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "投标编码", "项目名称", "招标编码", "投标名称",
            "招标人", "开标日期", "投标保证金", "招标控制价",
            "投标状态", "备注"
        ])

        # 表格样式设置
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        # 项目名称、投标名称、招标人列自动拉伸
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        # 设置列宽
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 100)
        self.table.setColumnWidth(8, 80)
        self.table.setColumnWidth(9, 150)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)

        # 双击事件 - 选中投标并切换到汇总表
        self.table.doubleClicked.connect(self.on_table_double_clicked)

        # 初始空数据
        self.table.setRowCount(0)

        layout.addWidget(self.table)

        # 分页控制区域
        page_layout = QHBoxLayout()
        page_layout.addStretch()

        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.setFixedHeight(35)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        page_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("第 1 页")
        self.page_label.setFont(QFont("Microsoft YaHei", 11))
        page_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.setFixedHeight(35)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        page_layout.addWidget(self.next_btn)

        layout.addLayout(page_layout)

        return tab

    def _create_stat_card(self, title: str, value: str, icon: str) -> QFrame:
        """创建统计卡片"""
        card = QFrame()
        card.setFixedSize(140, 90)
        card.setObjectName("cardFrame")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        # 图标和标题
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 10))
        title_label.setObjectName("subtitleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)

        return card

    def _update_tab_status(self):
        """更新页签状态（根据是否有选中的投标）"""
        has_selection = self.current_bidding_id is not None

        # 汇总表页签：需要选中投标才能访问
        self.tab_widget.setTabEnabled(1, has_selection)

        # 明细页签：需要选中投标才能访问
        self.tab_widget.setTabEnabled(2, has_selection)

        # 报表页签：需要选中投标才能访问
        self.tab_widget.setTabEnabled(3, has_selection)

    def on_tab_changed(self, index: int):
        """页签切换事件"""
        if index == 1 and self.current_bidding_id:  # 汇总表页签
            self.summary_tab.load_bidding_data(self.current_bidding_id)
        elif index == 2 and self.current_bidding_id:  # 明细页签
            self.detail_tab.load_bidding_data(self.current_bidding_id)
        elif index == 3 and self.current_bidding_id:  # 报表页签
            self.report_tab.load_bidding_data(self.current_bidding_id)

    def select_bidding(self, bidding_id: int, bidding_code: str = None):
        """选中投标（供其他页签调用）"""
        self.current_bidding_id = bidding_id
        self.current_bidding_code = bidding_code or ""

        # 更新页签状态
        self._update_tab_status()

        # 通知各页签
        self.summary_tab.on_bidding_selected(bidding_id, bidding_code)
        self.detail_tab.on_bidding_selected(bidding_id, bidding_code)
        self.report_tab.on_bidding_selected(bidding_id, bidding_code)

    def switch_to_detail_tab(self, bidding_id: int, bidding_code: str, bidding_name: str,
                              project_item_name: str, summary_item=None):
        """切换到明细页签并加载数据（供汇总表页签双击调用）"""
        # 更新当前选中的投标
        self.current_bidding_id = bidding_id
        self.current_bidding_code = bidding_code

        # 更新页签状态
        self._update_tab_status()

        # 切换到明细页签（索引为2）
        self.tab_widget.setCurrentIndex(2)

        # 加载明细数据
        self.detail_tab.load_detail_data(
            bidding_id,
            bidding_code,
            bidding_name,
            project_item_name,
            summary_item
        )

    # ==================== 事件处理 ====================

    def on_search(self):
        """搜索事件"""
        keyword = self.search_input.text().strip()
        self.refresh_table(keyword=keyword)

    def on_new_bidding(self):
        """新建投标事件"""
        dialog = BiddingDialog(
            self.bidding_manager,
            bidding_id=None,
            theme_manager=self.theme_manager,
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()
            self.update_statistics()

    def on_edit(self):
        """编辑投标事件"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要编辑的投标")
            return

        row = selected_rows[0].row()
        if row < len(self.bidding_ids):
            bidding_id = self.bidding_ids[row]
            self.open_edit_dialog(bidding_id)

    def open_edit_dialog(self, bidding_id: int):
        """打开编辑对话框"""
        dialog = BiddingDialog(
            self.bidding_manager,
            bidding_id=bidding_id,
            theme_manager=self.theme_manager,
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()
            self.update_statistics()

    def on_delete(self):
        """删除投标事件"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的投标")
            return

        row = selected_rows[0].row()
        if row >= len(self.bidding_ids):
            return

        bidding_id = self.bidding_ids[row]
        bidding = self.bidding_manager.get_bidding(bidding_id)
        if not bidding:
            QMessageBox.warning(self, "提示", "投标不存在")
            return

        bidding_code = bidding.bidding_code

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除投标 [{bidding_code}] 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, msg = self.bidding_manager.delete_bidding(bidding_id)
            if success:
                # 如果删除的是当前选中的投标，清空选择
                if self.current_bidding_id == bidding_id:
                    self.current_bidding_id = None
                    self.current_bidding_code = None
                    self._update_tab_status()
                QMessageBox.information(self, "成功", "投标已删除")
                self.refresh_table()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "失败", f"删除失败: {msg}")

    def on_refresh(self):
        """刷新数据事件"""
        self.refresh_table()
        self.update_statistics()

    def on_table_context_menu(self, position):
        """表格右键菜单"""
        row = self.table.rowAt(position.y())
        if row < 0 or row >= len(self.bidding_ids):
            return

        self.table.selectRow(row)

        menu = QMenu(self)

        edit_action = QAction("✏️  编辑信息", self)
        edit_action.triggered.connect(lambda: self.open_edit_dialog(self.bidding_ids[row]))
        menu.addAction(edit_action)

        # 添加"报价详情"选项
        menu.addSeparator()
        summary_action = QAction("📊 报价详情", self)
        summary_action.triggered.connect(lambda: self.select_bidding_and_switch(self.bidding_ids[row], 1))
        menu.addAction(summary_action)

        menu.addSeparator()

        delete_action = QAction("🗑️  删除投标", self)
        delete_action.triggered.connect(self.on_delete)
        menu.addAction(delete_action)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def on_table_double_clicked(self, index):
        """表格双击事件 - 选中投标并切换到汇总表"""
        row = index.row()
        if row < 0 or row >= len(self.bidding_ids):
            return

        bidding_id = self.bidding_ids[row]
        bidding = self.bidding_manager.get_bidding(bidding_id)
        if bidding:
            self.select_bidding_and_switch(bidding_id, 1, bidding.bidding_code)

    def select_bidding_and_switch(self, bidding_id: int, tab_index: int, bidding_code: str = None):
        """选中投标并切换到指定页签"""
        if not bidding_code:
            bidding = self.bidding_manager.get_bidding(bidding_id)
            if bidding:
                bidding_code = bidding.bidding_code

        self.select_bidding(bidding_id, bidding_code)
        self.tab_widget.setCurrentIndex(tab_index)

    def on_bidding_changed(self, event_type: str, data: dict):
        """投标数据变更回调"""
        self.refresh_table()
        self.update_statistics()

    # ==================== 数据更新 ====================

    def update_statistics(self):
        """更新统计数据"""
        stats = self.bidding_manager.get_status_counts()

        # 更新统计卡片
        if "投标总数" in self.stat_cards:
            value_label = self.stat_cards["投标总数"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('all', 0)))

        if "进行中" in self.stat_cards:
            value_label = self.stat_cards["进行中"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('in_progress', 0)))

        if "已中标" in self.stat_cards:
            value_label = self.stat_cards["已中标"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('won', 0)))

        if "未中标" in self.stat_cards:
            value_label = self.stat_cards["未中标"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('lost', 0)))

        if "已撤回" in self.stat_cards:
            value_label = self.stat_cards["已撤回"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('withdrawn', 0)))

    def refresh_table(self, keyword: str = None):
        """刷新表格数据"""
        # 获取投标列表
        biddings = self.bidding_manager.get_biddings(keyword=keyword)

        # 清空投标ID列表
        self.bidding_ids = []

        # 更新表格
        self.table.setRowCount(len(biddings))
        for row, bidding in enumerate(biddings):
            # 保存投标ID
            self.bidding_ids.append(bidding.id)

            # 投标编码（居中对齐）
            item_code = QTableWidgetItem(bidding.bidding_code)
            item_code.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_code)

            # 项目名称（通过project_id从project_manager获取，左对齐）
            project_name = self._get_project_name(bidding.project_id)
            item_project = QTableWidgetItem(project_name)
            item_project.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 1, item_project)

            # 招标编码（居中对齐）
            item_tender_code = QTableWidgetItem(bidding.tender_code)
            item_tender_code.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_tender_code)

            # 投标名称（左对齐）
            item_name = QTableWidgetItem(bidding.bidding_name)
            item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 3, item_name)

            # 招标人（左对齐）
            item_tenderer = QTableWidgetItem(bidding.tenderer)
            item_tenderer.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 4, item_tenderer)

            # 开标日期（居中对齐）
            bid_deadline = bidding.bid_deadline.strftime('%Y-%m-%d') if bidding.bid_deadline else ""
            item_deadline = QTableWidgetItem(bid_deadline)
            item_deadline.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, item_deadline)

            # 投标保证金（右对齐，金额格式）
            item_bond = QTableWidgetItem(f"{bidding.bid_bond:,.2f}")
            item_bond.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 6, item_bond)

            # 招标控制价（右对齐，金额格式）
            item_price = QTableWidgetItem(f"{bidding.control_price:,.2f}")
            item_price.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 7, item_price)

            # 投标状态（居中对齐）
            status = bidding.status.value if hasattr(bidding.status, 'value') else str(bidding.status)
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 8, item_status)

            # 备注（左对齐）
            item_remark = QTableWidgetItem(bidding.remark)
            item_remark.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 9, item_remark)

    def _get_project_name(self, project_id: int) -> str:
        """根据项目ID获取项目名称"""
        if not project_id or not self.bidding_manager.project_manager:
            return ""
        try:
            project = self.bidding_manager.project_manager.get_project(project_id)
            return project.name if project else ""
        except Exception:
            return ""

    # ==================== 主题应用 ====================

    def on_theme_changed(self, theme: dict):
        """主题变化回调 - QSS 已全局加载"""
        pass
