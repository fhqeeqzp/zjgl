# TBGL - 工程造价管理系统

一个基于 PySide6 的现代化工程造价管理系统，采用 QSS 样式表管理主题，支持深色/浅色主题切换，提供项目管理和投标管理等核心功能。

## 功能特性

### 用户认证模块
- 安全的用户登录系统，支持 SHA256 密码加密存储
- 用户注册功能，支持用户名和密码验证
- 密码修改功能，需要验证原密码
- 数据库配置管理（主机、端口、数据库名、用户名、密码）
- 数据库连接状态实时显示
- 登录日志记录

### 项目管理模块 (XMGL)
- 项目信息的新增、编辑、删除
- 项目类型管理：投标项目、施工项目
- 项目状态管理：投标中、进行中、已完成、已暂停
- 金额管理：投标金额、合同金额、实收金额、实付金额
- 日期管理：开始日期、竣工日期（带日历弹窗，年份范围前后20年）
- 附件管理：支持上传投标附件和施工附件，文件存储在 WD/项目名/ 目录下
- 项目备注功能
- 项目统计信息展示（项目总数、投标阶段、施工阶段、结算阶段、完工阶段）
- 按项目编码或名称搜索

### 投标管理模块 (TBGL)
- 投标信息的新增、编辑、删除
- 招标文件（Word文档）上传和自动解析
- 自动提取招标信息：招标编码、投标名称、招标人、计划工期、投标保证金、开标日期、招标控制价
- 投标状态管理：进行中、已中标、未中标、已撤回
- 多页签设计：
  - **投标信息页签**：显示投标列表和统计信息
  - **投标汇总表页签**：树形表格展示工程项目及费用，支持Excel导入
  - **投标明细页签**：详细的分部分项工程明细，支持Excel导入
  - **报表管理页签**：投标报表展示
- 版本管理：支持创建多个投标版本（V1.0、V2.0等）

### 数据展示
- 统一行高40px的数据表格
- 交替行颜色显示
- 项目名称列自动拉伸填充
- 支持右键菜单操作（编辑、删除、提升/降低层级、添加子级）
- 支持双击编辑
- 表格列可自定义显示/隐藏
- 分页控制（上一页/下一页）

### 树形表格
- 使用 QTreeWidget 实现层级结构展示
- 层级缩进24像素，清晰展示父子关系
- 支持展开/折叠全部节点
- 支持多选批量操作
- 支持拖拽调整层级关系
- 缩进列宽度120px，可显示5-6级层级

### 主题系统
- 支持深色/浅色主题切换
- 使用 QSS 文件管理样式（themes/dark.qss、themes/light.qss）
- 全局样式统一应用
- 主题观察者模式，支持组件响应主题变化
- 日历控件独立主题管理

### 界面特性
- 无边框现代化窗口设计
- 自定义标题栏（最小化、最大化、关闭按钮）
- 可拖拽移动窗口
- 圆角边框设计
- 窗口阴影效果
- 响应式布局
- 多页面导航（首页、仪表盘、项目管理、投标管理、消息、设置）

### 对话框设计
- 统一无边框对话框样式
- 自定义标题栏带关闭按钮
- 支持鼠标拖动
- 表单布局统一内边距1像素
- 按钮统一高度35px
- 输入框统一高度35px

## 技术栈

- **Python 3.x**
- **PySide6 6.10.1+** - Qt GUI框架
- **PyMySQL 1.1.2+** - MySQL数据库连接
- **cryptography 3.4.8+** - 加密支持

## 项目结构

```
.
├── components/              # UI组件
│   ├── title_bar.py        # 自定义标题栏（带用户信息显示）
│   ├── sidebar.py          # 侧边栏导航（带图标按钮）
│   ├── status_bar.py       # 状态栏（显示数据库状态）
│   └── pages.py            # 页面组件（首页、设置页等）
│
├── login/                   # 登录模块
│   ├── ui/
│   │   ├── login_window.py # 登录窗口（左图右表单布局）
│   │   ├── dialogs.py      # 对话框（注册、改密、数据库配置、消息提示）
│   │   └── styles.py       # 登录模块样式
│   ├── logic/
│   │   └── auth_manager.py # 认证管理器（SHA256加密）
│   └── data/
│       ├── db_config.py    # 数据库配置管理
│       └── db_manager.py   # 数据库管理器
│
├── XMGL/                    # 项目管理模块
│   ├── ui/
│   │   ├── projects_page.py   # 项目管理页面（表格+统计卡片）
│   │   └── project_dialog.py  # 项目编辑对话框（无边框+附件管理）
│   ├── logic/
│   │   └── project_manager.py # 项目管理器
│   └── data/
│       ├── project_model.py   # 项目数据模型
│       ├── project_db.py      # 项目数据库操作
│       └── project_config.py  # 项目配置
│
├── TBGL/                    # 投标管理模块
│   ├── ui/
│   │   ├── bidding_page.py       # 投标管理页面（多页签）
│   │   ├── bidding_dialog.py     # 投标编辑对话框（Word解析）
│   │   ├── bidding_summary_tab.py # 投标汇总表页签（树形表格+Excel导入）
│   │   ├── bidding_detail_tab.py  # 投标明细页签（树形表格+列设置）
│   │   ├── bidding_report_tab.py  # 报表管理页签
│   │   ├── excel_import_dialog.py # Excel导入对话框
│   │   ├── detail_import_dialog.py # 明细导入对话框
│   │   └── summary_edit_dialog.py  # 汇总项编辑对话框
│   ├── logic/
│   │   ├── bidding_manager.py    # 投标管理器
│   │   └── tender_doc_parser.py  # 招标文件解析器
│   └── data/
│       ├── bidding_model.py      # 投标数据模型
│       └── summary_model.py      # 汇总表数据模型
│
├── themes/                  # 主题管理
│   ├── theme_config.py     # 主题配置管理器（QSS加载）
│   ├── calendar_theme_manager.py  # 日历主题管理
│   ├── dark.qss            # 深色主题QSS（Fluent Design风格）
│   └── light.qss           # 浅色主题QSS
│
├── ui/                      # 全局UI组件
│   ├── fluent_widgets.py   # Fluent风格组件封装（按钮、输入框、下拉框等）
│   └── styles.py           # 全局样式
│
├── WD/                      # 文件存储目录
│   └── {项目名}/           # 项目文件夹
│       ├── 投标附件/       # 投标相关文件
│       └── 施工附件/       # 施工相关文件
│
├── main.py                  # 程序主入口
├── login_main.py            # 登录测试入口
└── requirements.txt         # 依赖列表
```

## 安装运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

首次运行时，点击登录界面的"数据库配置"按钮，设置 MySQL 连接信息：
- 主机地址（默认：localhost）
- 端口（默认：3306）
- 数据库名（默认：myapp）
- 用户名（默认：root）
- 密码

系统会自动创建所需的数据库表结构。

### 3. 运行程序

```bash
python main.py
```

## 主要依赖

| 包名 | 版本 | 说明 |
|------|------|------|
| PySide6 | >=6.10.1 | Qt GUI框架 |
| pymysql | >=1.1.2 | MySQL数据库连接 |
| cryptography | >=3.4.8 | 加密支持 |

## 界面组件说明

### 按钮组件 (ui/fluent_widgets.py)
- **PushButton**: 标准按钮，高度35px
- **PrimaryPushButton**: 主要按钮（主题色）
- **TransparentPushButton**: 透明按钮

### 输入组件
- **LineEdit**: 标准输入框，高度35px
- **SearchLineEdit**: 搜索输入框，带占位符
- **PasswordLineEdit**: 密码输入框，带掩码
- **ComboBox**: 下拉框，高度35px
- **DateEdit**: 日期选择框，带日历弹窗
- **TextEdit**: 多行文本框
- **DoubleSpinBox**: 数值输入框，2位小数

### 表格组件
- **QTableWidget**: 数据表格，行高40px，交替行颜色
- **QTreeWidget**: 树形表格，缩进24px，支持层级展示

### 对话框组件
- **BaseDialog**: 基础对话框（无边框+自定义标题栏）
- **RegisterDialog**: 用户注册对话框
- **ChangePasswordDialog**: 修改密码对话框
- **DatabaseConfigDialog**: 数据库配置对话框
- **MessageDialog**: 消息提示对话框
- **PasswordVerifyDialog**: 密码验证对话框
- **ProjectDialog**: 项目编辑对话框
- **BiddingDialog**: 投标编辑对话框

## 数据库表结构

### 用户表 (users)
- id, username, password_hash, status, created_at, updated_at, last_login_at

### 登录日志表 (login_logs)
- id, user_id, username, login_status, fail_reason, login_time

### 项目表 (projects)
- id, project_code, name, project_type, status, start_date, completion_date, bid_amount, contract_amount, received_amount, paid_amount, bid_attachment, construction_attachment, remark, created_at, updated_at

### 投标表 (biddings)
- id, project_id, project_code, bidding_code, tender_code, bidding_name, tenderer, planned_duration, bid_bond, bid_deadline, control_price, status, tender_doc_path, remark, created_at, updated_at

### 投标汇总表 (bidding_summaries)
- id, bidding_id, version_id, item_type, sequence, name, quote_price, main_material_fee, aux_material_fee, labor_fee, machinery_fee, other_fee, management_fee, tax_fee, parent_id, created_at

### 汇总版本表 (bidding_summary_versions)
- id, bidding_id, version, version_name, is_active, created_by, remark, created_at

## QSS 样式规范

### 颜色变量（深色主题）
- 窗口背景：#1E1E1E
- 内容背景：#252525
- 边框颜色：#444444
- 主色调：#0078D4
- 文字主色：#E6E6E6
- 文字次色：#B3B3B3

### 组件规范
- 所有组件内边距：1px
- 按钮高度：35px
- 输入框高度：35px
- 表格行高：40px
- 树形缩进：24px
- 边框圆角：4px（卡片8px）

## 文件存储规范

所有附件文件存储在项目根目录的 `WD` 文件夹下：
```
WD/
├── {项目名}/
│   ├── 投标附件/       # 存放招标文件、Excel等
│   └── 施工附件/       # 存放施工相关文件
```

## 开发团队

- 开发维护：网络刀客

## 许可证

MIT License
