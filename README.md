# TBGL - 工程造价管理系统

一个基于 PySide6 的现代化工程造价管理系统，采用 QFluentWidgets 风格设计，支持深色/浅色主题切换。

## 功能特性

### 用户认证模块
- 安全的用户登录系统
- 密码使用 SHA256 加密存储
- 支持回车键快速登录
- 用户名点击修改密码功能
- 数据库配置管理（主机、端口、用户名、密码）

### 项目管理模块
- 项目信息的新增、编辑、删除
- 项目类型：投标项目、施工项目
- 项目状态：投标中、进行中、已完成、已暂停
- 金额管理：投标金额、合同金额、实收金额、实付金额
- 日期管理：开始日期、竣工日期
- 附件管理：支持上传投标附件和施工附件
- 项目备注功能
- 项目统计信息展示

### 数据展示
- 美观的数据表格（仿 QFluentWidgets 风格）
- 表格行高统一设置为 40px
- 项目名称列自动拉伸填充
- 支持右键菜单操作（编辑、删除）
- 现代化的表格样式设计
- 支持按项目名称搜索

### 主题系统
- 支持深色/浅色主题切换
- 使用 QSS 文件管理样式
- 实时主题切换
- 主题观察者模式

### 界面特性
- 无边框现代化窗口设计
- 自定义标题栏（最小化、最大化、关闭按钮）
- 可拖拽移动窗口
- 圆角边框设计
- 窗口阴影效果
- 响应式布局
- 多页面导航（首页、仪表盘、项目管理、消息、设置）

## 技术栈

- **Python 3.14**
- **PySide6** - GUI 框架
- **PyQt-Fluent-Widgets / PyQt6-Fluent-Widgets** - 现代化 UI 组件
- **PyMySQL** - MySQL 数据库连接
- **SQLAlchemy** - ORM 框架
- **bcrypt** - 密码加密

## 项目结构

```
.
├── components/              # UI 组件
│   ├── title_bar.py        # 自定义标题栏
│   ├── sidebar.py          # 侧边栏导航
│   ├── status_bar.py       # 状态栏
│   └── pages.py            # 页面组件（首页、设置页等）
├── login/                   # 登录模块
│   ├── ui/
│   │   ├── login_window.py # 登录窗口
│   │   ├── dialogs.py      # 对话框（数据库配置、修改密码）
│   │   └── styles.py       # 登录模块样式
│   ├── logic/
│   │   └── auth_manager.py # 认证管理器
│   └── data/
│       ├── db_config.py    # 数据库配置
│       └── db_manager.py   # 数据库管理器
├── XMGL/                    # 项目管理模块
│   ├── ui/
│   │   ├── projects_page.py   # 项目管理页面
│   │   └── project_dialog.py  # 项目编辑对话框
│   ├── logic/
│   │   └── project_manager.py # 项目管理器
│   └── data/
│       ├── project_model.py   # 项目数据模型
│       ├── project_db.py      # 项目数据库操作
│       └── project_config.py  # 项目配置
├── themes/                  # 主题管理
│   ├── theme_config.py     # 主题配置管理器
│   ├── calendar_theme_manager.py  # 日历主题管理
│   ├── dark.qss            # 深色主题 QSS
│   └── light.qss           # 浅色主题 QSS
├── ui/                      # 全局 UI 组件
│   ├── fluent_widgets.py   # Fluent 风格组件封装
│   └── styles.py           # 全局样式
├── main.py                  # 程序主入口
├── login_main.py            # 登录测试入口
└── requirements_backup.txt  # 依赖列表
```

## 安装运行

### 1. 安装依赖

```bash
pip install -r requirements_backup.txt
```

### 2. 配置数据库

首次运行时，点击登录界面的"数据库配置"按钮，设置 MySQL 连接信息：
- 主机地址
- 端口
- 用户名
- 密码

### 3. 运行程序

```bash
python main.py
```

## 主要依赖

| 包名 | 版本 | 说明 |
|------|------|------|
| PySide6 | 6.10.2 | Qt 绑定 |
| PyQt6-Fluent-Widgets | 1.11.0 | Fluent 风格组件 |
| PyQt6-Frameless-Window | 0.7.7 | 无边框窗口 |
| PyMySQL | 1.1.2 | MySQL 连接 |
| bcrypt | 5.0.0 | 密码加密 |
| darkdetect | 0.8.0 | 系统主题检测 |

## 界面预览

- **登录界面**：现代化登录窗口，支持数据库配置
- **主界面**：侧边栏导航 + 内容区域，支持多页面切换
- **项目管理**：表格展示、搜索、新增/编辑/删除操作
- **主题切换**：支持深色/浅色模式实时切换

## 开发团队

- 开发维护：TBGL Team

## 许可证

MIT License
