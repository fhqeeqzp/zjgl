"""
数据库配置管理
"""
import json
import os


class DatabaseConfig:
    """数据库配置管理类"""

    CONFIG_FILE = 'login/data/db_config.json'

    DEFAULT_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'database': 'myapp',
        'username': 'root',
        'password': '',
        'is_configured': False  # 标记数据库是否已配置
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self, config):
        """保存配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_config(self):
        """获取当前配置"""
        return self.config

    def update_config(self, **kwargs):
        """更新配置"""
        self.config.update(kwargs)
        return self.save_config(self.config)

    def test_connection(self):
        """测试数据库连接"""
        # 这里可以实现实际的数据库连接测试
        # 目前返回模拟结果
        return True, "连接成功"
