"""
项目管理页面
提供项目管理的用户界面 - 使用 QFluentWidgets 组件
"""
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QMenu,
    QAction, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..logic.project_manager import ProjectManager
from .project_dialog import ProjectDialog
from ui import StyleSheetManager
from ui.fluent_widgets import PushButton, PrimaryPushButton, SearchLineEdit


class ProjectsPage(QFrame):
    """项目管理页面"""
    
    def __init__(self, theme_manager=None, db_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.project_manager = ProjectManager(db_manager)
        
        # 存储项目ID列表，用于表格行到项目ID的映射
        self.project_ids = []
        
        # 初始化UI
        self.setup_ui()
        
        # 应用主题
        if self.theme_manager:
            self.theme_manager.add_observer(self.apply_theme)
            self.apply_theme(self.theme_manager.get_theme())
        
        # 注册为项目管理的观察者
        self.project_manager.add_observer(self.on_project_changed)
        
        # 初始化数据库表
        self.project_manager.init_database()
        
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
        self.separator = separator
        layout.addWidget(separator)
        
        # ========== 内容区域 ==========
        content_widget = self._create_content_area()
        layout.addWidget(content_widget)
    
    def _create_title_bar(self) -> QFrame:
        """创建顶部标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(60)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)
        
        # 标题
        self.title_label = QLabel("📁 项目管理")
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # 搜索框
        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("搜索项目编码或名称...")
        self.search_input.setFixedWidth(250)
        self.search_input.returnPressed.connect(self.on_search)
        layout.addWidget(self.search_input)

        # 搜索按钮
        self.search_btn = PushButton("🔍 搜索")
        self.search_btn.clicked.connect(self.on_search)
        layout.addWidget(self.search_btn)

        layout.addSpacing(15)

        # 新建项目按钮
        self.new_btn = PrimaryPushButton("➕ 新建项目")
        self.new_btn.clicked.connect(self.on_new_project)
        layout.addWidget(self.new_btn)
        
        return title_bar
    
    def _create_content_area(self) -> QFrame:
        """创建内容区域"""
        content = QFrame()
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 统计卡片区域
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # 创建统计卡片
        self.stat_cards = {}
        card_configs = [
            ("项目总数", "0", "📊"),
            ("投标阶段", "0", "📋"),
            ("施工阶段", "0", "🏗️"),
            ("结算阶段", "0", "📑"),
            ("完工阶段", "0", "✅"),
        ]
        
        for title, value, icon in card_configs:
            card = self._create_stat_card(title, value, icon)
            stats_layout.addWidget(card)
            self.stat_cards[title] = card
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # 去掉操作列，改为11列
        self.table.setHorizontalHeaderLabels([
            "项目编码", "项目名称", "项目类型", "项目状态",
            "投标金额", "合同金额", "实收金额", "实付金额",
            "开始日期", "竣工日期", "备注"
        ])
        
        # 表格样式设置
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 项目名称列自动拉满
        
        # 设置列宽
        self.table.setColumnWidth(0, 150)  # 项目编码
        # 第1列(项目名称)自动拉满，不设置固定宽度
        self.table.setColumnWidth(2, 100)  # 项目类型
        self.table.setColumnWidth(3, 100)  # 项目状态
        self.table.setColumnWidth(4, 100)  # 投标金额
        self.table.setColumnWidth(5, 100)  # 合同金额
        self.table.setColumnWidth(6, 100)  # 实收金额
        self.table.setColumnWidth(7, 100)  # 实付金额
        self.table.setColumnWidth(8, 100)  # 开始日期
        self.table.setColumnWidth(9, 100)  # 竣工日期
        self.table.setColumnWidth(10, 150)  # 备注
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)  # 设置默认行高为40像素
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)
        
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
        
        return content
    
    def _create_stat_card(self, title: str, value: str, icon: str) -> QFrame:
        """创建统计卡片"""
        card = QFrame()
        card.setFixedSize(140, 90)
        
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
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)
        
        return card
    
    # ==================== 事件处理 ====================
    
    def on_search(self):
        """搜索事件"""
        keyword = self.search_input.text().strip()
        self.refresh_table(keyword=keyword)
    
    def on_new_project(self):
        """新建项目事件"""
        dialog = ProjectDialog(
            self.project_manager,
            project_id=None,
            theme_manager=self.theme_manager,
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()
            self.update_statistics()
    
    def on_edit(self):
        """编辑项目事件"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要编辑的项目")
            return
        
        row = selected_rows[0].row()
        if row < len(self.project_ids):
            project_id = self.project_ids[row]
            self.open_edit_dialog(project_id)
    
    def open_edit_dialog(self, project_id: int):
        """打开编辑对话框"""
        dialog = ProjectDialog(
            self.project_manager,
            project_id=project_id,
            theme_manager=self.theme_manager,
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()
            self.update_statistics()
    
    def on_delete(self):
        """删除项目事件"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的项目")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.project_ids):
            return
        
        project_id = self.project_ids[row]
        project = self.project_manager.get_project(project_id)
        if not project:
            QMessageBox.warning(self, "提示", "项目不存在")
            return
        
        project_code = project.project_code
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除项目 [{project_code}] 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = self.project_manager.delete_project(project_id)
            if success:
                QMessageBox.information(self, "成功", "项目已删除")
                self.refresh_table()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "失败", f"删除失败: {msg}")
    
    def on_refresh(self):
        """刷新数据事件"""
        self.refresh_table()
        self.update_statistics()
    
    def on_table_context_menu(self, position):
        """表格右键菜单 - 自定义样式"""
        # 获取点击的行
        row = self.table.rowAt(position.y())
        if row < 0 or row >= len(self.project_ids):
            return

        # 选中该行
        self.table.selectRow(row)

        # 创建自定义菜单
        menu = QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)

        # 获取当前主题
        theme = self.theme_manager.get_theme() if self.theme_manager else {}

        # 设置菜单样式
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.get('card_bg', '#2d2d3d')};
                border: 1px solid {theme.get('border', '#3d3d4d')};
                border-radius: 8px;
                padding: 8px;
            }}
            QMenu::item {{
                color: {theme.get('text_primary', '#ffffff')};
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {theme.get('accent', '#6c5ce7')};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme.get('border', '#3d3d4d')};
                margin: 8px 12px;
            }}
        """)

        # 编辑操作
        edit_action = QAction("✏️  编辑项目", self)
        edit_action.triggered.connect(lambda: self.open_edit_dialog(self.project_ids[row]))
        menu.addAction(edit_action)

        menu.addSeparator()

        # 删除操作
        delete_action = QAction("🗑️  删除项目", self)
        delete_action.triggered.connect(self.on_delete)
        menu.addAction(delete_action)

        # 在鼠标位置显示菜单
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def on_project_changed(self, event_type: str, data: dict):
        """项目数据变更回调"""
        self.refresh_table()
        self.update_statistics()
    
    # ==================== 数据更新 ====================
    
    def update_statistics(self):
        """更新统计数据"""
        stats = self.project_manager.get_status_counts()
        
        # 更新统计卡片
        if "项目总数" in self.stat_cards:
            value_label = self.stat_cards["项目总数"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('all', 0)))
        
        if "投标阶段" in self.stat_cards:
            value_label = self.stat_cards["投标阶段"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('bidding', 0)))
        
        if "施工阶段" in self.stat_cards:
            value_label = self.stat_cards["施工阶段"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('construction', 0)))
        
        if "结算阶段" in self.stat_cards:
            value_label = self.stat_cards["结算阶段"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('settlement', 0)))
        
        if "完工阶段" in self.stat_cards:
            value_label = self.stat_cards["完工阶段"].findChild(QLabel, "stat_value")
            if value_label:
                value_label.setText(str(stats.get('completed', 0)))
    
    def refresh_table(self, keyword: str = None):
        """刷新表格数据"""
        # 获取项目列表
        projects = self.project_manager.get_projects(keyword=keyword)
        
        # 清空项目ID列表
        self.project_ids = []
        
        # 更新表格
        self.table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            # 保存项目ID
            self.project_ids.append(project.id)
            
            # 项目编码
            self.table.setItem(row, 0, QTableWidgetItem(project.project_code))
            # 项目名称
            self.table.setItem(row, 1, QTableWidgetItem(project.name))
            # 项目类型
            project_type = project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type)
            self.table.setItem(row, 2, QTableWidgetItem(project_type))
            # 项目状态
            status = project.status.value if hasattr(project.status, 'value') else str(project.status)
            self.table.setItem(row, 3, QTableWidgetItem(status))
            # 投标金额
            self.table.setItem(row, 4, QTableWidgetItem(f"{project.bid_amount:,.2f}"))
            # 合同金额
            self.table.setItem(row, 5, QTableWidgetItem(f"{project.contract_amount:,.2f}"))
            # 实收金额
            self.table.setItem(row, 6, QTableWidgetItem(f"{project.received_amount:,.2f}"))
            # 实付金额
            self.table.setItem(row, 7, QTableWidgetItem(f"{project.paid_amount:,.2f}"))
            # 开始日期
            start_date = project.start_date.strftime('%Y-%m-%d') if project.start_date else ""
            self.table.setItem(row, 8, QTableWidgetItem(start_date))
            # 竣工日期
            completion_date = project.completion_date.strftime('%Y-%m-%d') if project.completion_date else ""
            self.table.setItem(row, 9, QTableWidgetItem(completion_date))
            # 备注
            self.table.setItem(row, 10, QTableWidgetItem(project.remark))
            # 操作列已删除，使用右键菜单进行编辑和删除操作
    
    def delete_project_by_id(self, project_id: int):
        """根据ID删除项目"""
        project = self.project_manager.get_project(project_id)
        if not project:
            QMessageBox.warning(self, "提示", "项目不存在")
            return
        
        project_code = project.project_code
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除项目 [{project_code}] 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = self.project_manager.delete_project(project_id)
            if success:
                QMessageBox.information(self, "成功", "项目已删除")
                self.refresh_table()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "失败", f"删除失败: {msg}")
    
    # ==================== 主题应用 ====================
    
    def apply_theme(self, theme: dict):
        """应用主题"""
        # 页面背景和表格样式
        self.setStyleSheet(StyleSheetManager.get_projects_page_style(theme))
        
        # 分隔线
        self.separator.setStyleSheet(f"background-color: {theme['border']}; border: none;")
        
        # 搜索框样式
        self.search_input.setStyleSheet(StyleSheetManager.get_projects_input_style(theme))
        
        # 按钮样式
        btn_style = StyleSheetManager.get_projects_btn_style(theme)
        self.search_btn.setStyleSheet(btn_style)
        self.new_btn.setStyleSheet(btn_style)
        self.prev_btn.setStyleSheet(btn_style)
        self.next_btn.setStyleSheet(btn_style)
        
        # 统计卡片样式
        card_style = StyleSheetManager.get_projects_card_style(theme)
        for card in self.stat_cards.values():
            card.setStyleSheet(card_style)
