"""
样式管理模块
提供运行时动态颜色计算，用于状态标签等需要动态变化颜色的场景

注意：所有静态样式已迁移到 themes/dark.qss 和 themes/light.qss 文件中
"""


class StyleSheetManager:
    """样式表管理器 - 仅提供运行时动态颜色计算"""

    @staticmethod
    def get_status_color(status: str) -> str:
        """
        获取状态颜色值（用于动态样式）

        Args:
            status: 状态类型 - "success", "error", "warning", "info"

        Returns:
            颜色值 (hex格式)
        """
        try:
            from themes.theme_config import ThemeConfig
            theme_config = ThemeConfig()
            is_dark = theme_config.get_current_theme() == "dark"
        except Exception:
            # 如果无法获取主题配置，默认使用深色主题颜色
            is_dark = True

        colors = {
            "success": "#4ade80" if is_dark else "#22c55e",
            "error": "#f87171" if is_dark else "#ef4444",
            "warning": "#fbbf24" if is_dark else "#f59e0b",
            "info": "#4EC9FF" if is_dark else "#0078D4",
        }
        return colors.get(status, colors["info"])

    @staticmethod
    def get_status_style(status: str) -> str:
        """
        获取状态标签的完整样式字符串

        Args:
            status: 状态类型 - "success", "error", "warning", "info"

        Returns:
            完整的样式字符串
        """
        color = StyleSheetManager.get_status_color(status)
        return f"color: {color}; font-weight: bold;"
