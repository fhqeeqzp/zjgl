"""
报表管理页签
显示投标相关报表
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QGroupBox,
    QComboBox
)

from ui.message_dialog import MessageDialog
from PySide6.QtCore import Qt

from ui.fluent_widgets import PushButton, PrimaryPushButton


class BiddingReportTab(QWidget):
    """报表管理页签"""

    def __init__(self, parent_page):
        super().__init__()
        self.parent_page = parent_page
        self.bidding_manager = parent_page.bidding_manager
        self.current_bidding_id = None

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 提示信息
        self.tip_label = QLabel("请先选择投标项目")
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setObjectName("tipLabel")
        layout.addWidget(self.tip_label)

        # 报表内容区域（初始隐藏）
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()

        toolbar_layout.addWidget(QLabel("当前投标:"))
        self.current_bidding_label = QLabel("")
        self.current_bidding_label.setObjectName("biddingInfoLabel")
        toolbar_layout.addWidget(self.current_bidding_label)

        toolbar_layout.addSpacing(20)

        # 报表类型选择
        toolbar_layout.addWidget(QLabel("报表类型:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "投标报价汇总表",
            "分部分项工程量清单",
            "措施项目清单",
            "其他项目清单",
            "规费税金清单"
        ])
        toolbar_layout.addWidget(self.report_type_combo)

        toolbar_layout.addStretch()

        # 导出按钮
        self.export_btn = PushButton("📥 导出Excel")
        self.export_btn.setObjectName("secondaryButton")
        self.export_btn.clicked.connect(self.on_export)
        toolbar_layout.addWidget(self.export_btn)

        # 打印按钮
        self.print_btn = PrimaryPushButton("🖨️ 打印")
        self.print_btn.clicked.connect(self.on_print)
        toolbar_layout.addWidget(self.print_btn)

        content_layout.addLayout(toolbar_layout)

        # 报表表格
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "序号", "项目名称", "金额（元）", "占比", "备注"
        ])
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.report_table.verticalHeader().setVisible(False)
        self.report_table.setAlternatingRowColors(True)

        header = self.report_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        content_layout.addWidget(self.report_table)

        # 汇总信息
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        summary_layout.addWidget(QLabel("投标总价:"))
        self.total_label = QLabel("¥ 0.00")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setProperty("large", "true")
        summary_layout.addWidget(self.total_label)
        content_layout.addLayout(summary_layout)

        layout.addWidget(self.content_widget)
        self.content_widget.hide()

    def on_bidding_selected(self, bidding_id: int, bidding_code: str = None):
        """从父页面接收选中的投标"""
        if bidding_id:
            self.load_bidding_data(bidding_id)
        else:
            self.show_tip()

    def show_tip(self):
        """显示提示信息"""
        self.tip_label.show()
        self.content_widget.hide()
        self.current_bidding_id = None

    def show_content(self):
        """显示内容区域"""
        self.tip_label.hide()
        self.content_widget.show()

    def load_bidding_data(self, bidding_id: int):
        """加载投标报表数据"""
        self.current_bidding_id = bidding_id
        bidding = self.bidding_manager.get_bidding(bidding_id)
        if not bidding:
            self.show_tip()
            return

        self.show_content()
        self.current_bidding_label.setText(f"{bidding.bidding_code} - {bidding.bidding_name}")

        # TODO: 从数据库加载报表数据
        # 这里先显示示例数据
        self.report_table.setRowCount(5)
        sample_data = [
            ["1", "分部分项工程费", "642,500.00", "85.67%", ""],
            ["2", "措施项目费", "80,000.00", "10.67%", ""],
            ["3", "其他项目费", "20,000.00", "2.67%", ""],
            ["4", "规费", "5,000.00", "0.67%", ""],
            ["5", "税金", "2,500.00", "0.33%", ""],
        ]
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                elif col == 2 or col == 3:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.report_table.setItem(row, col, item)

        # 更新总价
        self.total_label.setText("¥ 750,000.00")

    def on_export(self):
        """导出报表"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return
        # TODO: 实现导出功能
        pass

    def on_print(self):
        """打印报表"""
        if not self.current_bidding_id:
            MessageDialog.warning(self, "提示", "请先选择投标")
            return
        # TODO: 实现打印功能
        pass
