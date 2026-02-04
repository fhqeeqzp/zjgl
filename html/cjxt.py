import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem,
    QWidget, QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt  # 仅导入必要的 Qt，无多余依赖
from PySide6.QtGui import QFont

class HierarchyTreeWidget(QTreeWidget):
    """带层级连接线的树形控件，实现指定的层级标识样式（无报错版本）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # 启用树形连接线（核心配置）
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(True)
        self.setIndentation(24)
        # 等宽字体保证层级字符对齐
        self.setFont(QFont("Consolas", 9) if sys.platform == "win32" else QFont("Monaco", 9))
    
    def add_hierarchy_item(self, parent_item, text, level, is_top_level=False):
        """
        添加带层级前缀的节点（彻底避开 ItemIsExpandable）
        四级节点默认无下级，自然无法展开，无需额外设置标志
        """
        # 定义各层级的前缀标识（严格对应需求）
        level_prefixes = {
            0: "",  # 章节：实心方块
            1: "",  # 级别1：粗横线
            2: "",  # 级别2：T型连接
            3: "",  # 级别3：带竖线的T型
            4: ""  # 级别4：双竖线T型
        }
        
        # 拼接完整节点文本
        prefix = level_prefixes.get(level, "")
        full_text = f"{prefix}{text}"
        
        item = QTreeWidgetItem()
        item.setText(0, full_text)
        
        # 添加节点到树形控件
        if is_top_level:
            self.addTopLevelItem(item)
        else:
            if parent_item:
                parent_item.addChild(item)
        
        # 【关键修改】移除所有 ItemIsExpandable 相关代码
        # 四级节点无下级，自然无法展开，无需额外禁止，效果完全一致
        
        return item

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hierarchy QTreeWidget (Light/Dark Mode)")
        self.resize(700, 800)
        
        self.is_dark_mode = False
        
        # 布局初始化
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # 主题切换按钮
        self.switch_btn = QPushButton("切换到深色模式")
        self.switch_btn.clicked.connect(self.switch_theme)
        main_layout.addWidget(self.switch_btn)
        
        # 树形控件初始化
        self.tree_widget = HierarchyTreeWidget()
        self.init_hierarchy_data()
        main_layout.addWidget(self.tree_widget)
        
        # 初始浅色主题
        self.apply_light_theme()
    
    def init_hierarchy_data(self):
        """填充层级测试数据（四级节点无下级，自然无法展开）"""
        # 章节1
        chapter1 = self.tree_widget.add_hierarchy_item(
            None, "一、章节名称（项目概述）", level=0, is_top_level=True
        )
        level1_1 = self.tree_widget.add_hierarchy_item(
            chapter1, "1.1 一级项目（项目背景）", level=1
        )
        level2_1 = self.tree_widget.add_hierarchy_item(
            level1_1, "1.1.1 二级项目（行业现状）", level=2
        )
        level3_1 = self.tree_widget.add_hierarchy_item(
            level2_1, "1.1.1.1 三级项目（市场规模）", level=3
        )
        # 四级节点（无下级，自然无法展开，无任何报错）
        self.tree_widget.add_hierarchy_item(level3_1, "四级项目（细分领域占比）", level=4)
        self.tree_widget.add_hierarchy_item(level3_1, "四级项目（增长趋势分析）", level=4)
        
        # 同级节点补充
        level2_2 = self.tree_widget.add_hierarchy_item(level1_1, "1.1.2 二级项目（项目意义）", level=2)
        level3_2 = self.tree_widget.add_hierarchy_item(level2_2, "1.1.2.1 三级项目（社会价值）", level=3)
        self.tree_widget.add_hierarchy_item(level3_2, "四级项目（民生改善）", level=4)
        
        # 章节2
        chapter2 = self.tree_widget.add_hierarchy_item(None, "二、章节名称（技术方案）", level=0, is_top_level=True)
        self.tree_widget.add_hierarchy_item(chapter2, "2.1 一级项目（技术架构）", level=1)
        
        # 默认展开节点
        chapter1.setExpanded(True)
        level1_1.setExpanded(True)
        level2_1.setExpanded(True)
        level3_1.setExpanded(True)
    
    def apply_light_theme(self):
        """浅色主题（现代扁平，连接线清晰）"""
        light_qss = """
        QTreeWidget {
            background-color: #fafbfc;
            border: 1px solid #eef2f7;
            border-radius: 12px;
            padding: 12px;
            outline: none;
            color: #2d3748;
        }
        QTreeWidget::item {
            height: 36px;
            padding-left: 8px;
            border-radius: 6px;
            margin: 1px 4px;
        }
        QTreeWidget::item:hover {
            background-color: #eef7ff;
        }
        QTreeWidget::item:selected {
            background-color: #d1e7fe;
            color: #1a73e8;
        }
        QTreeWidget::item:selected:active {
            background-color: #c5e0fd;
        }
        /* 隐藏原生展开图标（仅保留自定义层级标识） */
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:has-children:has-siblings:closed,
        QTreeWidget::branch:has-children:!has-siblings:open,
        QTreeWidget::branch:has-children:has-siblings:open {
            image: none;
        }
        /* 连接线样式（清晰层级，扁平现代） */
        QTreeWidget::branch {
            border-image: none;
            background-color: transparent;
            color: #adb5bd;
        }
        QTreeWidget::branch:vertical {
            border-left: 1px solid #adb5bd;
        }
        QTreeWidget::branch:horizontal {
            border-top: 1px solid #adb5bd;
        }
        /* 按钮样式（配套现代风格） */
        QPushButton {
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            background-color: #1a73e8;
            color: white;
            font-size: 9pt;
            font-weight: 500;
            margin-bottom: 12px;
        }
        QPushButton:hover {
            background-color: #0d66d0;
            cursor: pointer;
        }
        """
        self.setStyleSheet(light_qss)
    
    def apply_dark_theme(self):
        """深色主题（护眼，层级清晰）"""
        dark_qss = """
        QTreeWidget {
            background-color: #1e1e2f;
            border: 1px solid #313244;
            border-radius: 12px;
            padding: 12px;
            outline: none;
            color: #cdd6f4;
        }
        QTreeWidget::item {
            height: 36px;
            padding-left: 8px;
            border-radius: 6px;
            margin: 1px 4px;
        }
        QTreeWidget::item:hover {
            background-color: #313244;
        }
        QTreeWidget::item:selected {
            background-color: #45475a;
            color: #89b4fa;
        }
        QTreeWidget::item:selected:active {
            background-color: #585b70;
        }
        /* 隐藏原生展开图标 */
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:has-children:has-siblings:closed,
        QTreeWidget::branch:has-children:!has-siblings:open,
        QTreeWidget::branch:has-children:has-siblings:open {
            image: none;
        }
        /* 连接线样式（适配深色主题） */
        QTreeWidget::branch {
            border-image: none;
            background-color: transparent;
            color: #45475a;
        }
        QTreeWidget::branch:vertical {
            border-left: 1px solid #45475a;
        }
        QTreeWidget::branch:horizontal {
            border-top: 1px solid #45475a;
        }
        /* 按钮样式（配套深色主题） */
        QPushButton {
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            background-color: #45475a;
            color: #cdd6f4;
            font-size: 9pt;
            font-weight: 500;
            margin-bottom: 12px;
        }
        QPushButton:hover {
            background-color: #585b70;
            cursor: pointer;
        }
        """
        self.setStyleSheet(dark_qss)
    
    def switch_theme(self):
        """切换浅色/深色主题（无缝衔接）"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_dark_theme()
            self.switch_btn.setText("切换到浅色模式")
        else:
            self.apply_light_theme()
            self.switch_btn.setText("切换到深色模式")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 9) if sys.platform == "win32" else QFont("Monaco", 9))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())