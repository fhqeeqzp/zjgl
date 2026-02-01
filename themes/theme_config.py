"""
主题配置文件
使用 QSS 文件管理主题样式
"""
import os


class ThemeManager:
    """主题管理器 - 使用 QSS 文件管理主题"""

    # 主题配置（保留颜色配置供程序逻辑使用）
    THEMES = {
        'dark': {
            'name': '深色主题',
            'window_bg': '#1e1e2e',
            'sidebar_bg': '#252535',
            'content_bg': '#2d2d3d',
            'text_primary': '#cdd6f4',
            'text_secondary': '#a6adc8',
            'accent': '#89b4fa',
            'accent_hover': '#b4befe',
            'border': '#45475a',
            'button_bg': '#45475a',
            'button_hover': '#585b70',
            'card_bg': '#313244',
            'shadow': '#000000'
        },
        'light': {
            'name': '浅色主题',
            'window_bg': '#eff1f5',
            'sidebar_bg': '#e6e9ef',
            'content_bg': '#ffffff',
            'text_primary': '#4c4f69',
            'text_secondary': '#6c6f85',
            'accent': '#1e66f5',
            'accent_hover': '#7287fd',
            'border': '#ccd0da',
            'button_bg': '#dce0e8',
            'button_hover': '#bcc0cc',
            'card_bg': '#e6e9ef',
            'shadow': '#9ca0b0'
        }
    }

    def __init__(self, qss_path=None):
        """
        初始化主题管理器
        :param qss_path: QSS 文件目录路径，默认为 themes 目录
        """
        self.current_theme = 'dark'
        self._observers = []
        self._app = None  # QApplication 实例

        # 设置 QSS 文件路径
        if qss_path is None:
            self.qss_path = os.path.dirname(os.path.abspath(__file__))
        else:
            self.qss_path = qss_path

    def set_application(self, app):
        """
        设置 QApplication 实例，用于应用 QSS
        :param app: QApplication 实例
        """
        self._app = app
        # 初始化时应用当前主题
        self.apply_qss()

    def get_qss_file_path(self, theme_name=None):
        """
        获取 QSS 文件路径
        :param theme_name: 主题名称，默认为当前主题
        :return: QSS 文件完整路径
        """
        if theme_name is None:
            theme_name = self.current_theme
        return os.path.join(self.qss_path, f"{theme_name}.qss")

    def load_qss(self, theme_name=None):
        """
        加载 QSS 文件内容
        :param theme_name: 主题名称，默认为当前主题
        :return: QSS 样式字符串
        """
        qss_file = self.get_qss_file_path(theme_name)
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"QSS 文件未找到: {qss_file}")
            return ""
        except Exception as e:
            print(f"加载 QSS 文件失败: {e}")
            return ""

    def apply_qss(self, theme_name=None):
        """
        应用 QSS 样式到应用程序
        :param theme_name: 主题名称，默认为当前主题
        """
        if theme_name is None:
            theme_name = self.current_theme

        qss_content = self.load_qss(theme_name)

        if self._app and qss_content:
            self._app.setStyleSheet(qss_content)
            return True
        return False

    def get_theme(self, theme_name=None):
        """获取主题配置（颜色字典）"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES['dark'])

    def get_current_theme_name(self):
        """获取当前主题名称"""
        return self.current_theme

    def switch_theme(self, theme_name):
        """
        切换主题
        :param theme_name: 主题名称 ('dark' 或 'light')
        :return: 是否切换成功
        """
        if theme_name in self.THEMES and theme_name != self.current_theme:
            self.current_theme = theme_name
            # 应用新的 QSS
            self.apply_qss()
            # 通知观察者
            self._notify_observers()
            return True
        return False

    def toggle_theme(self):
        """切换主题（深色/浅色之间切换）"""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        return self.switch_theme(new_theme)

    def add_observer(self, callback):
        """添加主题变化观察者"""
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback):
        """移除主题变化观察者"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """通知所有观察者主题已变化"""
        theme = self.get_theme()
        for callback in self._observers:
            callback(theme)
