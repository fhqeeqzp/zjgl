"""
主题配置文件
包含所有主题的颜色定义和主题管理器
"""


class ThemeManager:
    """主题管理器 - 同时管理深色和浅色主题"""

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
            'border': '#313244',
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

    def __init__(self):
        self.current_theme = 'dark'
        self._observers = []

    def get_theme(self, theme_name=None):
        """获取主题配置"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES['dark'])

    def get_current_theme_name(self):
        """获取当前主题名称"""
        return self.current_theme

    def switch_theme(self, theme_name):
        """切换主题"""
        if theme_name in self.THEMES and theme_name != self.current_theme:
            self.current_theme = theme_name
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
