"""
项目模块配置管理
存储项目编码规则等配置
"""
import json
import os
from typing import Dict, Any


class ProjectConfig:
    """项目配置管理类"""
    
    CONFIG_FILE = 'XMGL/data/project_config.json'
    
    # 默认配置
    DEFAULT_CONFIG = {
        'project_code_rule': {
            'prefix': 'ZHJG-XM-',  # 固定前缀
            'year_format': 'YYYY',  # 年份格式：YYYY或YY
            'sequence_digits': 3,   # 序号位数
        },
        'default_values': {
            'project_type': '工业建筑',
            'status': '投标阶段',
        }
    }
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置，确保所有字段都存在
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"加载项目配置失败: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """保存配置"""
        if config is not None:
            self.config = config
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存项目配置失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config
    
    def get_code_rule(self) -> Dict[str, Any]:
        """获取项目编码规则"""
        return self.config.get('project_code_rule', self.DEFAULT_CONFIG['project_code_rule'])
    
    def set_code_rule(self, prefix: str = None, year_format: str = None, sequence_digits: int = None) -> bool:
        """
        设置项目编码规则
        :param prefix: 固定前缀
        :param year_format: 年份格式（YYYY或YY）
        :param sequence_digits: 序号位数
        :return: 是否成功
        """
        code_rule = self.config.get('project_code_rule', {})
        
        if prefix is not None:
            code_rule['prefix'] = prefix
        if year_format is not None:
            code_rule['year_format'] = year_format
        if sequence_digits is not None:
            code_rule['sequence_digits'] = sequence_digits
        
        self.config['project_code_rule'] = code_rule
        return self.save_config()
    
    def update_config(self, **kwargs) -> bool:
        """更新配置"""
        self.config.update(kwargs)
        return self.save_config()


# 全局配置实例
_project_config = None


def get_project_config() -> ProjectConfig:
    """获取项目配置单例"""
    global _project_config
    if _project_config is None:
        _project_config = ProjectConfig()
    return _project_config
