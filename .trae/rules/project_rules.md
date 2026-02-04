# 工程造价管理系统 - 开发规范

## 1. 技术栈

- **UI框架**: PySide6
- **数据库**: MySQL
- **样式系统**: QSS (Qt Style Sheets)
- **主题支持**: 深色/浅色双主题

## 2. QSS样式管理规范（重要）

### 2.1 样式定义位置（强制）

**所有样式必须定义在以下位置，禁止在Python代码中硬编码样式：**

| 位置 | 用途 | 示例 |
|------|------|------|
| `themes/light.qss` | 浅色主题全局样式 | 所有控件基础样式 |
| `themes/dark.qss` | 深色主题全局样式 | 所有控件基础样式 |
| `ui/styles.py` | 动态样式生成（仅运行时颜色计算） | 需要程序计算的颜色 |

**禁止行为：**
```python
# ❌ 禁止在Python代码中硬编码样式
button.setStyleSheet("""
    QPushButton {
        background-color: #3c3c3c;
        color: #ffffff;
        border-radius: 4px;
    }
""")

label.setStyleSheet("color: #e74c3c; font-weight: bold;")
```

**正确做法：**
```python
# ✅ 使用objectName让QSS选择器匹配
button.setObjectName("primaryButton")
# 样式在 themes/dark.qss 或 light.qss 中定义

# ✅ 动态颜色使用StyleSheetManager生成
from ui.styles import StyleSheetManager
label.setStyleSheet(StyleSheetManager.get_status_label_style("error"))
```

### 2.2 QSS文件结构规范

`themes/dark.qss` 和 `themes/light.qss` 必须按以下结构组织：

```css
/* ============================================
   1. 基础控件样式
   ============================================ */
QWidget { ... }
QLabel { ... }
QPushButton { ... }
QLineEdit { ... }
QComboBox { ... }
QTableWidget { ... }
QTreeWidget { ... }
QScrollBar { ... }

/* ============================================
   2. 通用组件样式（按功能分类）
   ============================================ */
/* 按钮 */
#primaryButton { ... }
#secondaryButton { ... }
#dangerButton { ... }

/* 输入框 */
#searchInput { ... }
#formInput { ... }

/* 标签 */
#titleLabel { ... }
#subtitleLabel { ... }
#errorLabel { ... }
#successLabel { ... }
#warningLabel { ... }

/* 容器 */
#cardContainer { ... }
#dialogContainer { ... }

/* ============================================
   3. 特定对话框/窗口样式（按模块分类）
   ============================================ */
/* TBGL模块 */
#excelImportDialog { ... }
#detailImportDialog { ... }
#summaryTree { ... }
#detailTree { ... }

/* 登录模块 */
#loginWindow { ... }

/* ============================================
   4. 菜单和工具提示
   ============================================ */
QMenu { ... }
QToolTip { ... }
```

### 2.3 颜色变量规范

QSS文件顶部必须定义颜色变量（使用CSS变量或注释说明）：

```css
/* dark.qss 颜色定义 */
:root {
    --bg-primary: #1E1E1E;
    --bg-secondary: #252525;
    --bg-tertiary: #3c3c3c;
    --text-primary: #E6E6E6;
    --text-secondary: #AAAAAA;
    --accent-primary: #0078D4;
    --accent-secondary: #4EC9FF;
    --success: #4ade80;
    --warning: #fbbf24;
    --error: #f87171;
}
```

**颜色使用对照表：**

| 用途 | 深色主题 | 浅色主题 | CSS变量 |
|------|----------|----------|---------|
| 主背景 | `#1E1E1E` | `#FFFFFF` | `--bg-primary` |
| 次背景 | `#252525` | `#F5F5F5` | `--bg-secondary` |
| 控件背景 | `#3c3c3c` | `#FFFFFF` | `--bg-tertiary` |
| 主文字 | `#E6E6E6` | `#333333` | `--text-primary` |
| 次文字 | `#AAAAAA` | `#666666` | `--text-secondary` |
| 强调色 | `#0078D4` | `#0078D4` | `--accent-primary` |
| 高亮色 | `#4EC9FF` | `#0078D4` | `--accent-secondary` |
| 成功 | `#4ade80` | `#22c55e` | `--success` |
| 警告 | `#fbbf24` | `#f59e0b` | `--warning` |
| 错误 | `#f87171` | `#ef4444` | `--error` |

### 2.4 控件命名规范

为控件设置`objectName`以便QSS选择器匹配：

```python
# 对话框
self.setObjectName("excelImportDialog")

# 按钮
self.import_btn.setObjectName("primaryButton")
self.cancel_btn.setObjectName("secondaryButton")
self.delete_btn.setObjectName("dangerButton")

# 标签
self.title_label.setObjectName("titleLabel")
self.error_label.setObjectName("errorLabel")

# 树形控件
self.tree.setObjectName("summaryTree")  # 或 "detailTree"

# 容器
self.content_frame.setObjectName("dialogContainer")
```

### 2.5 动态样式处理

**仅以下情况允许在Python中设置样式：**

1. **运行时状态颜色变化**（成功/失败/警告）
```python
# ui/styles.py 中提供的方法
class StyleSheetManager:
    @staticmethod
    def get_status_color(status: str) -> str:
        """获取状态颜色值"""
        colors = {
            "success": "#4ade80" if is_dark_theme() else "#22c55e",
            "error": "#f87171" if is_dark_theme() else "#ef4444",
            "warning": "#fbbf24" if is_dark_theme() else "#f59e0b",
            "info": "#4EC9FF" if is_dark_theme() else "#0078D4",
        }
        return colors.get(status, colors["info"])

# 使用
self.status_label.setStyleSheet(f"color: {StyleSheetManager.get_status_color('success')};")
```

2. **需要计算的值**（如动态边框、渐变）
```python
# 允许：动态计算渐变
gradient = f"background: linear-gradient(135deg, {color1}, {color2});"
```

## 3. UI布局规范

### 3.1 内边距与间距

- **组件内边距**: 统一为 `1px`
- **布局间距**: 使用 `QSpacerItem` 或 `layout.setSpacing(8)`
- **对话框边距**: `layout.setContentsMargins(16, 16, 16, 16)`

```python
# 正确示例
layout = QVBoxLayout()
layout.setSpacing(8)
layout.setContentsMargins(16, 16, 16, 16)

# 按钮布局
button_layout = QHBoxLayout()
button_layout.setSpacing(8)
button_layout.addStretch()
```

### 3.2 统一尺寸规范

| 组件类型 | 最小宽度 | 高度 | 字体大小 |
|----------|----------|------|----------|
| 主按钮 | 80px | 32px | 14px |
| 次按钮 | 80px | 32px | 14px |
| 输入框 | 200px | 32px | 13px |
| 下拉框 | 200px | 32px | 13px |
| 标签 | auto | auto | 13px |
| 标题标签 | auto | auto | 16px, bold |

### 3.3 字体规范

- **主字体**: `"Microsoft YaHei", "PingFang SC", sans-serif`
- **代码字体**: `"Consolas", "Monaco", monospace`
- **字体大小**: 统一使用像素值（px）而非点（pt）

```css
/* QSS中的字体定义 */
QLabel {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 13px;
}

#titleLabel {
    font-size: 16px;
    font-weight: bold;
}
```

## 4. 对话框规范

### 4.1 对话框结构

所有对话框必须遵循统一结构：

```python
class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("myDialog")  # 设置objectName用于QSS
        self.setWindowTitle("对话框标题")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 内容区域
        self.setup_content()
        
        # 按钮区域
        self.setup_buttons()
        
    def setup_content(self):
        """子类重写：设置对话框内容"""
        pass
        
    def setup_buttons(self):
        """底部按钮栏"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.setObjectName("primaryButton")
        self.confirm_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        
        self.layout().addLayout(button_layout)
```

### 4.2 对话框样式（QSS）

```css
/* 对话框基础样式 */
QDialog {
    background-color: var(--bg-primary);
    border-radius: 8px;
}

/* 标题栏 */
QDialog QLabel#titleLabel {
    font-size: 16px;
    font-weight: bold;
    color: var(--text-primary);
    padding-bottom: 8px;
}

/* 内容区域 */
QDialog QFrame#contentFrame {
    background-color: var(--bg-secondary);
    border-radius: 6px;
    padding: 12px;
}
```

## 5. 树形表格规范

### 5.1 层级缩进

树形表格必须使用缩进表示层级关系：

```python
# 设置缩进
self.tree.setIndentation(20)  # 每层缩进20像素

# 或自定义缩进
self.tree.setIndentation(24)
```

### 5.2 树形控件样式（QSS）

```css
QTreeWidget {
    background-color: var(--bg-secondary);
    border: 1px solid var(--bg-tertiary);
    border-radius: 6px;
    outline: none;
    padding: 4px;
}

QTreeWidget::item {
    height: 28px;
    padding: 4px 8px;
    border-radius: 4px;
    margin: 2px 0;
}

QTreeWidget::item:selected {
    background-color: var(--accent-primary);
    color: white;
}

QTreeWidget::item:hover {
    background-color: var(--bg-tertiary);
}

/* 展开/折叠指示器 */
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    image: url(:/icons/chevron-right.png);
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    image: url(:/icons/chevron-down.png);
}
```

## 6. 主题切换规范

### 6.1 主题管理

使用 `themes/theme_config.py` 中的 `ThemeConfig` 类管理主题：

```python
from themes.theme_config import ThemeConfig

# 应用主题
theme_config = ThemeConfig(self)
theme_config.apply_theme("dark")  # 或 "light"

# 获取当前主题
current_theme = theme_config.get_current_theme()
```

### 6.2 主题相关颜色获取

```python
from themes.theme_config import ThemeConfig

def get_theme_color(color_type: str) -> str:
    """
    获取当前主题的颜色值
    
    Args:
        color_type: 颜色类型 (primary, secondary, success, error, warning)
    
    Returns:
        颜色值 (hex格式)
    """
    theme_config = ThemeConfig()
    is_dark = theme_config.get_current_theme() == "dark"
    
    colors = {
        "primary": "#0078D4",
        "secondary": "#4EC9FF" if is_dark else "#0078D4",
        "success": "#4ade80" if is_dark else "#22c55e",
        "error": "#f87171" if is_dark else "#ef4444",
        "warning": "#fbbf24" if is_dark else "#f59e0b",
    }
    return colors.get(color_type, "#0078D4")
```

## 7. 代码审查清单

提交代码前，请确认以下事项：

- [ ] 没有在Python代码中硬编码QSS样式（除动态颜色外）
- [ ] 所有需要样式的控件都设置了`objectName`
- [ ] 新控件样式已添加到`themes/dark.qss`和`themes/light.qss`
- [ ] 颜色使用符合规范中的颜色对照表
- [ ] 组件内边距为1px
- [ ] 字体大小统一（13px常规，16px标题）
- [ ] 树形表格设置了适当的缩进
- [ ] 对话框遵循统一结构

## 8. 迁移指南

### 8.1 将Python中的样式迁移到QSS文件

**步骤1：识别需要迁移的样式**
```python
# 原代码
self.button.setStyleSheet("""
    QPushButton {
        background-color: #3c3c3c;
        color: #ffffff;
        border-radius: 4px;
        padding: 8px 16px;
    }
""")
```

**步骤2：为控件设置objectName**
```python
self.button.setObjectName("myCustomButton")
```

**步骤3：将样式添加到QSS文件**
```css
/* themes/dark.qss */
#myCustomButton {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
    border-radius: 4px;
    padding: 8px 16px;
}

/* themes/light.qss */
#myCustomButton {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
    border-radius: 4px;
    padding: 8px 16px;
}
```

**步骤4：移除Python中的setStyleSheet调用**
```python
# 删除 setStyleSheet 调用，只保留 objectName 设置
self.button.setObjectName("myCustomButton")
```

### 8.2 状态颜色迁移

对于需要动态变化的状态颜色：

```python
# 原代码
if success:
    label.setStyleSheet("color: #4ade80;")
else:
    label.setStyleSheet("color: #f87171;")

# 新代码
from ui.styles import StyleSheetManager
label.setStyleSheet(f"color: {StyleSheetManager.get_status_color('success' if success else 'error')};")
```

## 9. 示例代码

### 9.1 完整对话框示例

```python
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QFrame
)

class ProjectDialog(QDialog):
    """项目对话框示例"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectDialog")
        self.setWindowTitle("新建项目")
        self.setMinimumWidth(450)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 标题
        title = QLabel("新建项目")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # 内容区域
        content = QFrame()
        content.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)
        
        # 项目名称
        name_label = QLabel("项目名称:")
        name_label.setObjectName("formLabel")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("formInput")
        self.name_input.setPlaceholderText("请输入项目名称")
        
        content_layout.addWidget(name_label)
        content_layout.addWidget(self.name_input)
        layout.addWidget(content)
        
        # 按钮
        self.setup_buttons()
        
    def setup_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = QPushButton("确定")
        confirm_btn.setObjectName("primaryButton")
        confirm_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)
        
        self.layout().addLayout(button_layout)
```

### 9.2 对应QSS样式

```css
/* themes/dark.qss */
#projectDialog {
    background-color: var(--bg-primary);
}

#projectDialog #titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: var(--text-primary);
}

#projectDialog #contentFrame {
    background-color: var(--bg-secondary);
    border-radius: 8px;
    padding: 16px;
}

#projectDialog #formLabel {
    color: var(--text-secondary);
    font-size: 13px;
}

#projectDialog #formInput {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--bg-tertiary);
    border-radius: 4px;
    padding: 8px 12px;
    height: 32px;
}

#projectDialog #formInput:focus {
    border-color: var(--accent-primary);
}

#primaryButton {
    background-color: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 24px;
    min-width: 80px;
    height: 32px;
    font-weight: 500;
}

#primaryButton:hover {
    background-color: var(--accent-secondary);
}

#secondaryButton {
    background-color: transparent;
    color: var(--text-primary);
    border: 1px solid var(--bg-tertiary);
    border-radius: 4px;
    padding: 8px 24px;
    min-width: 80px;
    height: 32px;
}

#secondaryButton:hover {
    background-color: var(--bg-tertiary);
}
```

## 10. 架构分层规范（重要）

### 10.1 三层架构原则

项目采用严格的**三层架构**，各层职责分明，禁止跨层调用：

```
┌─────────────────────────────────────────────────────────────┐
│                        UI 层（表现层）                        │
│  - 负责界面展示和用户交互                                       │
│  - 调用 Logic 层处理业务                                       │
│  - 禁止直接访问数据库                                          │
├─────────────────────────────────────────────────────────────┤
│                      Logic 层（业务逻辑层）                     │
│  - 负责业务逻辑处理                                            │
│  - 调用 Data 层进行数据操作                                     │
│  - 禁止直接操作 UI 控件                                        │
├─────────────────────────────────────────────────────────────┤
│                       Data 层（数据层）                        │
│  - 负责数据持久化和读取                                        │
│  - 提供数据模型和数据库操作                                     │
│  - 禁止包含业务逻辑                                            │
└─────────────────────────────────────────────────────────────┘
```

**依赖方向：UI → Logic → Data（单向依赖，禁止反向）**

### 10.2 目录结构规范

每个业务模块必须按以下结构组织：

```
模块名/                          # 如 XMGL, TBGL, login
├── __init__.py
├── logic/                       # 业务逻辑层
│   ├── __init__.py
│   └── {功能}_manager.py        # 管理器类
├── data/                        # 数据层
│   ├── __init__.py
│   ├── {功能}_model.py          # 数据模型
│   ├── {功能}_db.py             # 数据库操作
│   └── {功能}_config.py         # 配置管理
└── ui/                          # UI层
    ├── __init__.py
    ├── {功能}_page.py           # 主页面
    ├── {功能}_dialog.py         # 对话框
    └── {功能}_tab.py            # 页签组件
```

### 10.3 各层文件命名规范

#### UI 层命名规范

| 类型 | 文件名模式 | 类名模式 | 示例 |
|------|-----------|---------|------|
| 主页面 | `{功能}_page.py` | `XxxPage` | `projects_page.py` → `ProjectsPage` |
| 对话框 | `{功能}_dialog.py` | `XxxDialog` | `bidding_dialog.py` → `BiddingDialog` |
| 页签 | `{功能}_tab.py` | `XxxTab` | `bidding_summary_tab.py` → `BiddingSummaryTab` |
| 导入对话框 | `{功能}_import_dialog.py` | `XxxImportDialog` | `excel_import_dialog.py` → `ExcelImportDialog` |

#### Logic 层命名规范

| 类型 | 文件名模式 | 类名模式 | 职责 |
|------|-----------|---------|------|
| 管理器 | `{功能}_manager.py` | `XxxManager` | 业务逻辑协调、状态管理 |
| 解析器 | `{功能}_parser.py` | `XxxParser` | 文件解析、数据转换 |
| 计算器 | `{功能}_calculator.py` | `XxxCalculator` | 数值计算、统计分析 |
| 验证器 | `{功能}_validator.py` | `XxxValidator` | 数据验证、规则检查 |

#### Data 层命名规范

| 类型 | 文件名模式 | 类名模式 | 职责 |
|------|-----------|---------|------|
| 数据模型 | `{功能}_model.py` | `Xxx`, `XxxModel` | 数据结构定义、枚举 |
| 数据库操作 | `{功能}_db.py` | `XxxDatabase` | SQL执行、CRUD操作 |
| 配置管理 | `{功能}_config.py` | `XxxConfig` | 配置读取、参数管理 |

### 10.4 层间调用规范

#### UI 层调用规范

```python
# ✅ 正确：UI层调用Logic层
from ..logic.project_manager import ProjectManager

class ProjectsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()  # 实例化Logic层
        
    def load_projects(self):
        # 调用Logic层方法
        projects = self.project_manager.get_all_projects()
        self.display_projects(projects)

# ❌ 错误：UI层直接访问数据库
from ..data.project_db import ProjectDatabase

class ProjectsPage(QWidget):
    def __init__(self):
        self.db = ProjectDatabase()  # 禁止！应该通过Logic层访问
```

#### Logic 层调用规范

```python
# ✅ 正确：Logic层调用Data层
from ..data.project_model import Project, ProjectStatus
from ..data.project_db import ProjectDatabase

class ProjectManager:
    def __init__(self):
        self.db = ProjectDatabase()  # 实例化Data层
        
    def create_project(self, name: str) -> Project:
        # 业务逻辑处理
        project_code = self.generate_code()
        
        # 调用Data层保存
        project = Project(code=project_code, name=name)
        return self.db.insert(project)

# ❌ 错误：Logic层操作UI
class ProjectManager:
    def create_project(self, name: str):
        # 禁止！Logic层不应该知道UI的存在
        self.status_label.setText("创建中...")
```

#### Data 层规范

```python
# ✅ 正确：Data层只负责数据操作
from .project_model import Project

class ProjectDatabase:
    def insert(self, project: Project) -> Project:
        """插入项目到数据库"""
        sql = "INSERT INTO projects (code, name) VALUES (%s, %s)"
        # 执行SQL...
        return project

# ❌ 错误：Data层包含业务逻辑
class ProjectDatabase:
    def create_project_with_validation(self, name: str):
        # 禁止！验证应该在Logic层
        if len(name) < 3:
            raise ValueError("名称太短")
        # ...
```

### 10.5 数据流向规范

#### 标准数据流

```
用户操作 → UI层 → Logic层 → Data层 → 数据库
                ↓
           业务逻辑处理
                ↓
UI更新 ← Logic层通知 ← Data层返回数据
```

#### 观察者模式（UI更新通知）

Logic层通过观察者模式通知UI更新，避免直接调用UI：

```python
# Logic层：project_manager.py
from typing import Callable, List

class ProjectManager:
    def __init__(self):
        self._observers: List[Callable] = []
        
    def add_observer(self, callback: Callable):
        """添加观察者"""
        self._observers.append(callback)
        
    def notify_observers(self, event: str, data: any):
        """通知所有观察者"""
        for observer in self._observers:
            observer(event, data)
            
    def create_project(self, name: str):
        # 业务逻辑...
        project = self.db.insert(...)
        # 通知UI更新
        self.notify_observers("project_created", project)

# UI层：projects_page.py
class ProjectsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        # 注册为观察者
        self.project_manager.add_observer(self.on_project_changed)
        
    def on_project_changed(self, event: str, data: any):
        """响应项目变更事件"""
        if event == "project_created":
            self.refresh_project_list()
```

### 10.6 跨模块调用规范

#### 禁止直接跨模块调用

```python
# ❌ 错误：TBGL模块直接调用XMGL模块的内部
from XMGL.logic.project_manager import ProjectManager

class BiddingManager:
    def __init__(self):
        self.project_manager = ProjectManager()  # 禁止！
```

#### 正确做法：通过主程序协调

```python
# ✅ 正确：通过构造函数注入依赖
class BiddingManager:
    def __init__(self, project_id: int = None):
        self.project_id = project_id
        
# 主程序协调
def open_bidding_page(project_id: int):
    bidding_page = BiddingPage(project_id)
    main_window.show_page(bidding_page)
```

### 10.7 全局共享组件

#### 允许的共享组件

```
main/
├── themes/                    # 主题管理（全局共享）
│   └── theme_config.py
├── ui/                        # 全局UI组件
│   ├── fluent_widgets.py      # 统一封装的控件
│   └── styles.py              # 动态样式（仅颜色计算）
└── components/                # 全局布局组件
    ├── title_bar.py
    ├── sidebar.py
    └── status_bar.py
```

#### 使用规范

```python
# ✅ 正确：使用全局共享组件
from ui.fluent_widgets import PushButton, LineEdit
from themes.theme_config import ThemeConfig

class MyPage(QWidget):
    def __init__(self):
        self.button = PushButton("点击")  # 使用封装组件
        self.theme_config = ThemeConfig()
```

### 10.8 数据模型规范

#### 模型定义

```python
# data/project_model.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class ProjectStatus(Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class Project:
    """项目数据模型"""
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """从字典创建实例"""
        return cls(
            id=data.get("id"),
            code=data.get("code", ""),
            name=data.get("name", ""),
            status=ProjectStatus(data.get("status", "draft")),
        )

class ProjectModel:
    """项目模型管理（可选，用于复杂业务逻辑）"""
    def __init__(self):
        self.projects: List[Project] = []
```

#### 数据库操作类

```python
# data/project_db.py
from typing import List, Optional
from .project_model import Project, ProjectStatus

class ProjectDatabase:
    """项目数据库操作类"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        
    def insert(self, project: Project) -> Project:
        """插入项目"""
        sql = """
            INSERT INTO projects (code, name, status, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        params = (project.code, project.name, project.status.value)
        project.id = self.db.execute_insert(sql, params)
        return project
        
    def update(self, project: Project) -> Project:
        """更新项目"""
        sql = """
            UPDATE projects 
            SET name = %s, status = %s, updated_at = NOW()
            WHERE id = %s
        """
        params = (project.name, project.status.value, project.id)
        self.db.execute_update(sql, params)
        return project
        
    def delete(self, project_id: int) -> bool:
        """删除项目"""
        sql = "DELETE FROM projects WHERE id = %s"
        return self.db.execute_delete(sql, (project_id,))
        
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """根据ID获取项目"""
        sql = "SELECT * FROM projects WHERE id = %s"
        row = self.db.execute_query_one(sql, (project_id,))
        return self._row_to_project(row) if row else None
        
    def get_all(self) -> List[Project]:
        """获取所有项目"""
        sql = "SELECT * FROM projects ORDER BY created_at DESC"
        rows = self.db.execute_query(sql)
        return [self._row_to_project(row) for row in rows]
        
    def _row_to_project(self, row: dict) -> Project:
        """将数据库行转换为Project对象"""
        return Project(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            status=ProjectStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
```

### 10.9 业务逻辑管理器规范

```python
# logic/project_manager.py
from typing import List, Optional, Callable
from ..data.project_model import Project, ProjectStatus
from ..data.project_db import ProjectDatabase
from ..data.project_config import ProjectConfig

class ProjectManager:
    """项目管理器 - 业务逻辑层"""
    
    def __init__(self):
        self.db = ProjectDatabase()
        self.config = ProjectConfig()
        self._observers: List[Callable] = []
        
    # ========== 观察者模式 ==========
    
    def add_observer(self, callback: Callable[[str, any], None]):
        """添加状态变更观察者"""
        self._observers.append(callback)
        
    def remove_observer(self, callback: Callable[[str, any], None]):
        """移除观察者"""
        if callback in self._observers:
            self._observers.remove(callback)
            
    def _notify(self, event: str, data: any = None):
        """通知观察者"""
        for observer in self._observers:
            observer(event, data)
            
    # ========== 业务方法 ==========
    
    def create_project(self, name: str, project_type: str = "normal") -> Project:
        """
        创建新项目
        
        Args:
            name: 项目名称
            project_type: 项目类型
            
        Returns:
            创建的项目对象
            
        Raises:
            ValueError: 项目名称无效
        """
        # 1. 验证输入
        if not name or len(name.strip()) < 2:
            raise ValueError("项目名称至少需要2个字符")
            
        # 2. 生成项目编码（业务逻辑）
        code = self._generate_project_code(project_type)
        
        # 3. 创建项目对象
        project = Project(
            code=code,
            name=name.strip(),
            status=ProjectStatus.DRAFT
        )
        
        # 4. 保存到数据库
        project = self.db.insert(project)
        
        # 5. 通知UI更新
        self._notify("project_created", project)
        
        return project
        
    def update_project(self, project_id: int, **kwargs) -> Project:
        """更新项目信息"""
        project = self.db.get_by_id(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
            
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
                
        project = self.db.update(project)
        self._notify("project_updated", project)
        return project
        
    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        # 业务逻辑检查
        project = self.db.get_by_id(project_id)
        if project and project.status == ProjectStatus.ACTIVE:
            raise ValueError("不能删除进行中的项目")
            
        result = self.db.delete(project_id)
        if result:
            self._notify("project_deleted", {"id": project_id})
        return result
        
    def get_all_projects(self) -> List[Project]:
        """获取所有项目"""
        return self.db.get_all()
        
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """根据ID获取项目"""
        return self.db.get_by_id(project_id)
        
    # ========== 私有方法 ==========
    
    def _generate_project_code(self, project_type: str) -> str:
        """生成项目编码"""
        prefix = self.config.get_code_prefix(project_type)
        sequence = self.config.get_next_sequence()
        return f"{prefix}-{datetime.now().year}-{sequence:04d}"
```

### 10.10 UI层规范

```python
# ui/projects_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget
from ..logic.project_manager import ProjectManager
from .project_dialog import ProjectDialog

class ProjectsPage(QWidget):
    """项目管理页面 - UI层"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectsPage")
        
        # 实例化Logic层
        self.project_manager = ProjectManager()
        self.project_manager.add_observer(self.on_project_changed)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 工具栏
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("新建项目")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.on_add_clicked)
        toolbar.addWidget(self.add_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 项目表格
        self.project_table = QTableWidget()
        self.project_table.setObjectName("projectTable")
        layout.addWidget(self.project_table)
        
    def load_data(self):
        """加载数据"""
        # 调用Logic层获取数据
        projects = self.project_manager.get_all_projects()
        self.display_projects(projects)
        
    def display_projects(self, projects: List[Project]):
        """显示项目列表"""
        self.project_table.setRowCount(len(projects))
        for i, project in enumerate(projects):
            self.project_table.setItem(i, 0, QTableWidgetItem(project.code))
            self.project_table.setItem(i, 1, QTableWidgetItem(project.name))
            
    def on_add_clicked(self):
        """点击添加按钮"""
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # 调用Logic层创建项目
            try:
                project = self.project_manager.create_project(dialog.get_name())
                # 成功后会通过观察者模式自动刷新
            except ValueError as e:
                QMessageBox.warning(self, "错误", str(e))
                
    def on_project_changed(self, event: str, data: any):
        """响应项目变更事件"""
        if event in ("project_created", "project_updated", "project_deleted"):
            self.load_data()  # 刷新数据
            
    def closeEvent(self, event):
        """页面关闭时清理"""
        # 移除观察者，避免内存泄漏
        self.project_manager.remove_observer(self.on_project_changed)
        super().closeEvent(event)
```

### 10.11 代码审查清单（架构分层）

提交代码前，请确认以下事项：

- [ ] UI层只调用Logic层，不直接访问数据库
- [ ] Logic层只调用Data层，不直接操作UI控件
- [ ] Data层不包含业务逻辑，只负责数据操作
- [ ] 各层之间单向依赖（UI → Logic → Data）
- [ ] 使用观察者模式进行UI更新通知，不直接调用UI
- [ ] 数据模型使用 `@dataclass` 定义，包含 `to_dict` 和 `from_dict` 方法
- [ ] 数据库操作类方法命名规范（insert/update/delete/get_by_id/get_all）
- [ ] 业务逻辑管理器包含完整的类型注解和文档字符串
- [ ] 跨模块调用通过主程序协调，不直接导入其他模块的内部类
- [ ] 页面关闭时移除Logic层的观察者，避免内存泄漏

### 10.12 常见问题与解决方案

#### 问题1：需要在UI层显示数据库查询结果

**错误做法：**
```python
# UI层直接查询数据库
from ..data.project_db import ProjectDatabase

class ProjectsPage:
    def load(self):
        db = ProjectDatabase()
        projects = db.get_all()  # 禁止！
```

**正确做法：**
```python
# UI层通过Logic层获取数据
from ..logic.project_manager import ProjectManager

class ProjectsPage:
    def __init__(self):
        self.manager = ProjectManager()
        
    def load(self):
        projects = self.manager.get_all_projects()  # 正确
```

#### 问题2：Logic层需要更新UI进度

**错误做法：**
```python
class ImportManager:
    def import_data(self, file_path: str):
        self.progress_bar.setValue(50)  # 禁止！Logic层不应该知道UI控件
```

**正确做法：**
```python
class ImportManager:
    def import_data(self, file_path: str, progress_callback=None):
        for i, row in enumerate(data):
            # 处理数据...
            if progress_callback:
                progress_callback(int(i / total * 100))  # 通过回调通知进度
                
# UI层
class ImportDialog:
    def start_import(self):
        self.manager.import_data(file_path, self.update_progress)
        
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)  # UI层更新控件
```

#### 问题3：多个UI页面需要共享数据

**错误做法：**
```python
# 全局变量共享
project_data = None

class Page1:
    def save(self):
        global project_data
        project_data = self.get_data()

class Page2:
    def load(self):
        global project_data
        self.set_data(project_data)
```

**正确做法：**
```python
# 通过Logic层共享
class ProjectManager:
    def __init__(self):
        self._current_project: Optional[Project] = None
        
    def set_current_project(self, project: Project):
        self._current_project = project
        self._notify("current_project_changed", project)
        
    def get_current_project(self) -> Optional[Project]:
        return self._current_project

# 各页面通过同一个Manager实例访问
class Page1:
    def __init__(self, manager: ProjectManager):
        self.manager = manager
        
class Page2:
    def __init__(self, manager: ProjectManager):
        self.manager = manager
```

## 11. 对话框规范

### 11.1 统一使用 MessageDialog

项目中所有消息对话框必须使用 `ui.message_dialog.MessageDialog`，禁止使用 `QMessageBox`。

#### 禁止使用的对话框

```python
# ❌ 禁止使用 QMessageBox
from PySide6.QtWidgets import QMessageBox

QMessageBox.information(self, "标题", "消息内容")
QMessageBox.warning(self, "标题", "警告内容")
QMessageBox.critical(self, "标题", "错误内容")
QMessageBox.question(self, "标题", "确认吗？")
```

#### 正确做法

```python
# ✅ 使用 MessageDialog
from ui.message_dialog import MessageDialog

# 信息提示
MessageDialog.information(self, "提示", "操作成功完成")

# 警告提示
MessageDialog.warning(self, "警告", "数据未保存，确定要退出吗？")

# 错误提示
MessageDialog.critical(self, "错误", "数据库连接失败")

# 确认对话框
result = MessageDialog.question(
    self, 
    "确认删除", 
    "确定要删除该项目吗？此操作不可恢复。",
    buttons=MessageDialog.Yes | MessageDialog.No,
    default_button=MessageDialog.No
)
if result == MessageDialog.Yes:
    # 执行删除
    pass
```

### 11.2 MessageDialog 特性

`MessageDialog` 相比 `QMessageBox` 的优势：

1. **无标题栏**：自定义标题区域，更美观
2. **可拖动**：支持拖动对话框位置
3. **主题适配**：通过 QSS 自动适配深色/浅色主题
4. **阴影效果**：自带阴影，视觉层次更清晰
5. **统一风格**：与项目整体 UI 风格一致

### 11.3 MessageDialog 使用方法

#### 静态方法（推荐）

```python
from ui.message_dialog import MessageDialog

# 信息对话框
MessageDialog.information(
    parent=self,           # 父窗口
    title="提示",          # 标题
    text="操作成功",       # 内容
    buttons=MessageDialog.Ok,  # 按钮类型
    default_button=MessageDialog.Ok,  # 默认按钮
    min_width=300,         # 最小宽度
    min_height=150         # 最小高度
)

# 警告对话框
MessageDialog.warning(parent, title, text, ...)

# 错误对话框
MessageDialog.critical(parent, title, text, ...)

# 确认对话框
result = MessageDialog.question(
    parent,
    title,
    text,
    buttons=MessageDialog.Yes | MessageDialog.No | MessageDialog.Cancel,
    default_button=MessageDialog.No
)
# result 返回值：MessageDialog.Yes / MessageDialog.No / MessageDialog.Cancel
```

#### 实例化使用（自定义）

```python
from ui.message_dialog import MessageDialog

dialog = MessageDialog(
    parent=self,
    icon_type=MessageDialog.Information,  # 图标类型
    title="自定义标题",
    text="自定义消息内容",
    buttons=MessageDialog.Ok | MessageDialog.Cancel,
    default_button=MessageDialog.Ok,
    min_width=400,
    min_height=200
)

result = dialog.exec()
if result == MessageDialog.Ok:
    pass
```

#### 图标类型常量

```python
MessageDialog.Information  # 信息图标（蓝色 i）
MessageDialog.Warning      # 警告图标（黄色 !）
MessageDialog.Critical     # 错误图标（红色 X）
MessageDialog.Question     # 问号图标（蓝色 ?）
```

#### 按钮类型常量

```python
MessageDialog.Ok       # 确定按钮
MessageDialog.Yes      # 是按钮
MessageDialog.No       # 否按钮
MessageDialog.Cancel   # 取消按钮

# 组合使用
MessageDialog.Yes | MessageDialog.No           # 是和否
MessageDialog.Ok | MessageDialog.Cancel        # 确定和取消
MessageDialog.Yes | MessageDialog.No | MessageDialog.Cancel  # 是、否、取消
```

### 11.4 常见使用场景

#### 操作成功提示

```python
# 添加成功后提示
self.project_manager.create_project(name)
MessageDialog.information(self, "成功", f"项目 '{name}' 创建成功")
```

#### 操作确认

```python
# 删除前确认
result = MessageDialog.question(
    self,
    "确认删除",
    f"确定要删除项目 '{project.name}' 吗？\n此操作不可恢复。",
    buttons=MessageDialog.Yes | MessageDialog.No,
    default_button=MessageDialog.No
)
if result == MessageDialog.Yes:
    self.project_manager.delete_project(project.id)
    MessageDialog.information(self, "成功", "项目已删除")
```

#### 错误处理

```python
try:
    self.project_manager.import_data(file_path)
except ValueError as e:
    MessageDialog.warning(self, "导入失败", str(e))
except Exception as e:
    MessageDialog.critical(self, "系统错误", f"发生未知错误：{str(e)}")
```

#### 保存确认

```python
def closeEvent(self, event):
    """关闭前检查是否有未保存的更改"""
    if self.has_unsaved_changes():
        result = MessageDialog.question(
            self,
            "未保存的更改",
            "有未保存的更改，是否保存？",
            buttons=MessageDialog.Yes | MessageDialog.No | MessageDialog.Cancel,
            default_button=MessageDialog.Yes
        )
        if result == MessageDialog.Yes:
            self.save_changes()
            event.accept()
        elif result == MessageDialog.No:
            event.accept()
        else:  # Cancel
            event.ignore()
    else:
        event.accept()
```

### 11.5 对话框样式（QSS）

`MessageDialog` 的样式通过 QSS 文件统一管理：

```css
/* themes/dark.qss */
#messageDialog {
    background: transparent;
}

#messageDialog #contentWidget {
    background-color: #2b2b2b;
    border-radius: 8px;
    border: 1px solid #3c3c3c;
}

#messageDialog #titleBar {
    background-color: #333333;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom: 1px solid #3c3c3c;
}

#messageDialog #titleLabel {
    color: #E6E6E6;
    font-size: 14px;
    font-weight: 500;
}

#messageDialog #closeButton {
    background: transparent;
    color: #AAAAAA;
    border: none;
    font-size: 18px;
    border-radius: 4px;
}

#messageDialog #closeButton:hover {
    background-color: #e81123;
    color: white;
}

#messageDialog #bodyWidget {
    background: transparent;
}

#messageDialog #textLabel {
    color: #E6E6E6;
    font-size: 13px;
    line-height: 1.5;
}

#messageDialog #buttonWidget {
    background: transparent;
}

#messageDialog #okButton,
#messageDialog #yesButton {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    min-width: 80px;
    height: 32px;
    font-size: 13px;
}

#messageDialog #okButton:hover,
#messageDialog #yesButton:hover {
    background-color: #4EC9FF;
}

#messageDialog #noButton,
#messageDialog #cancelButton {
    background-color: transparent;
    color: #E6E6E6;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 20px;
    min-width: 80px;
    height: 32px;
    font-size: 13px;
}

#messageDialog #noButton:hover,
#messageDialog #cancelButton:hover {
    background-color: #3c3c3c;
}
```

### 11.6 自定义对话框继承 MessageDialog

如果需要创建自定义对话框，可以继承 `MessageDialog`：

```python
from ui.message_dialog import MessageDialog
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QLabel

class InputDialog(MessageDialog):
    """带输入框的对话框"""
    
    def __init__(self, parent=None, title="输入", label="请输入：", default_text=""):
        # 先调用父类初始化，但不设置内容
        self.input_label_text = label
        self.default_text = default_text
        
        super().__init__(
            parent=parent,
            icon_type=MessageDialog.Question,
            title=title,
            text="",  # 空文本，自定义内容
            buttons=MessageDialog.Ok | MessageDialog.Cancel,
            default_button=MessageDialog.Ok
        )
        
    def setup_ui(self, title, text, buttons, default_button):
        """重写 setup_ui 添加输入框"""
        super().setup_ui(title, text, buttons, default_button)
        
        # 在 body 中添加输入框
        from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QLabel
        
        input_layout = QVBoxLayout()
        
        label = QLabel(self.input_label_text)
        label.setObjectName("inputLabel")
        input_layout.addWidget(label)
        
        self.input_field = QLineEdit(self.default_text)
        self.input_field.setObjectName("inputField")
        input_layout.addWidget(self.input_field)
        
        # 添加到 body
        body_widget = self.findChild(QWidget, "bodyWidget")
        if body_widget:
            body_layout = body_widget.layout()
            body_layout.addLayout(input_layout)
    
    def get_text(self):
        """获取输入的文本"""
        return self.input_field.text()

# 使用
 dialog = InputDialog(self, title="新建文件夹", label="文件夹名称：")
if dialog.exec() == MessageDialog.Ok:
    folder_name = dialog.get_text()
```

### 11.7 代码审查清单（对话框）

提交代码前，请确认以下事项：

- [ ] 使用 `MessageDialog` 替代 `QMessageBox`
- [ ] 信息提示使用 `MessageDialog.information()`
- [ ] 警告提示使用 `MessageDialog.warning()`
- [ ] 错误提示使用 `MessageDialog.critical()`
- [ ] 确认操作使用 `MessageDialog.question()`
- [ ] 确认对话框设置了合适的默认按钮（通常是"取消"或"否"）
- [ ] 对话框标题简洁明了（2-6个字符）
- [ ] 对话框内容清晰说明操作后果
- [ ] 处理用户点击"取消"的情况

## 12. 组件使用规范

### 12.1 禁止使用分组框（QGroupBox）

项目中**禁止使用** `QGroupBox` 分组框组件，使用 `QFrame` 替代。

#### 禁止使用的组件

```python
# ❌ 禁止使用 QGroupBox
from PySide6.QtWidgets import QGroupBox

group = QGroupBox("分组标题")  # 禁止！
group_layout = QVBoxLayout(group)
group_layout.addWidget(widget1)
group_layout.addWidget(widget2)
```

#### 正确做法

```python
# ✅ 使用 QFrame + QLabel 替代
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

# 创建带标题的分组区域
group_frame = QFrame()
group_frame.setObjectName("groupFrame")
group_layout = QVBoxLayout(group_frame)

# 添加标题标签（可选）
title_label = QLabel("分组标题")
title_label.setObjectName("groupTitleLabel")
group_layout.addWidget(title_label)

# 添加内容
group_layout.addWidget(widget1)
group_layout.addWidget(widget2)
```

### 12.2 分组区域样式（QSS）

```css
/* themes/dark.qss */
#groupFrame {
    background-color: #252525;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 12px;
}

#groupTitleLabel {
    color: #E6E6E6;
    font-size: 14px;
    font-weight: bold;
    padding-bottom: 8px;
    border-bottom: 1px solid #3c3c3c;
    margin-bottom: 8px;
}

/* themes/light.qss */
#groupFrame {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 12px;
}

#groupTitleLabel {
    color: #333333;
    font-size: 14px;
    font-weight: bold;
    padding-bottom: 8px;
    border-bottom: 1px solid #E0E0E0;
    margin-bottom: 8px;
}
```

### 12.3 常见分组场景示例

#### 表单分组

```python
from PySide6.QtWidgets import (
    QFrame, QLabel, QLineEdit, QVBoxLayout, 
    QFormLayout, QHBoxLayout
)

def create_form_group(title: str, fields: list) -> QFrame:
    """创建表单分组区域"""
    frame = QFrame()
    frame.setObjectName("groupFrame")
    
    layout = QVBoxLayout(frame)
    layout.setSpacing(8)
    layout.setContentsMargins(12, 12, 12, 12)
    
    # 标题
    if title:
        title_label = QLabel(title)
        title_label.setObjectName("groupTitleLabel")
        layout.addWidget(title_label)
    
    # 表单内容
    form_layout = QFormLayout()
    form_layout.setSpacing(8)
    
    for label_text, widget in fields:
        label = QLabel(label_text)
        label.setObjectName("formLabel")
        form_layout.addRow(label, widget)
    
    layout.addLayout(form_layout)
    return frame

# 使用
name_input = QLineEdit()
name_input.setObjectName("formInput")
code_input = QLineEdit()
code_input.setObjectName("formInput")

basic_info_group = create_form_group(
    "基本信息",
    [("项目名称:", name_input), ("项目编码:", code_input)]
)
```

#### 按钮分组

```python
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout

def create_button_group(buttons: list) -> QFrame:
    """创建按钮分组区域"""
    frame = QFrame()
    frame.setObjectName("groupFrame")
    
    layout = QHBoxLayout(frame)
    layout.setSpacing(8)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.addStretch()
    
    for btn in buttons:
        layout.addWidget(btn)
    
    return frame

# 使用
save_btn = QPushButton("保存")
save_btn.setObjectName("primaryButton")
cancel_btn = QPushButton("取消")
cancel_btn.setObjectName("secondaryButton")

button_group = create_button_group([cancel_btn, save_btn])
```

#### 信息展示分组

```python
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGridLayout

def create_info_group(title: str, info_dict: dict) -> QFrame:
    """创建信息展示分组区域"""
    frame = QFrame()
    frame.setObjectName("groupFrame")
    
    layout = QVBoxLayout(frame)
    layout.setSpacing(8)
    layout.setContentsMargins(12, 12, 12, 12)
    
    # 标题
    if title:
        title_label = QLabel(title)
        title_label.setObjectName("groupTitleLabel")
        layout.addWidget(title_label)
    
    # 信息内容
    info_layout = QGridLayout()
    info_layout.setSpacing(8)
    
    row = 0
    for key, value in info_dict.items():
        key_label = QLabel(f"{key}:")
        key_label.setObjectName("infoKeyLabel")
        
        value_label = QLabel(str(value))
        value_label.setObjectName("infoValueLabel")
        
        info_layout.addWidget(key_label, row, 0)
        info_layout.addWidget(value_label, row, 1)
        row += 1
    
    layout.addLayout(info_layout)
    layout.addStretch()
    
    return frame

# 使用
project_info = create_info_group(
    "项目信息",
    {
        "项目名称": "某某工程",
        "项目编码": "XM-2024-001",
        "创建时间": "2024-01-15",
        "项目状态": "进行中"
    }
)
```

### 12.4 代码审查清单（组件使用）

提交代码前，请确认以下事项：

- [ ] 未使用 `QGroupBox` 组件
- [ ] 使用 `QFrame` 替代分组框功能
- [ ] 分组区域设置了 `objectName="groupFrame"`
- [ ] 分组标题使用 `QLabel` 并设置 `objectName="groupTitleLabel"`
- [ ] 样式已添加到 `themes/dark.qss` 和 `themes/light.qss`

---

**最后更新**: 2026-02-04
**版本**: v1.3
