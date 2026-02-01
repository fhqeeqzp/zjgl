"""
项目管理器
负责项目模块的业务逻辑处理
"""
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from ..data.project_model import Project, ProjectStatus, ProjectType, ProjectModel
from ..data.project_db import ProjectDatabase
from ..data.project_config import get_project_config


class ProjectManager:
    """项目管理器类"""
    
    def __init__(self, db_manager=None):
        """
        初始化项目管理器
        :param db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.project_db = ProjectDatabase(db_manager)
        self.model = ProjectModel()
        self.config = get_project_config()
        
        # 观察者列表（用于UI更新通知）
        self._observers: List[Callable] = []
    
    # ==================== 观察者模式 ====================
    
    def add_observer(self, callback: Callable):
        """添加观察者"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """移除观察者"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self, event_type: str, data: Any = None):
        """通知所有观察者"""
        for callback in self._observers:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"通知观察者失败: {e}")
    
    # ==================== 数据库初始化 ====================
    
    def init_database(self) -> bool:
        """
        初始化项目数据库表
        :return: 是否成功
        """
        return self.project_db.create_tables()
    
    # ==================== 项目编码生成 ====================
    
    def generate_project_code(self) -> str:
        """
        根据配置规则生成项目编码
        格式: 前缀 + 年份 + 序号
        例如: ZHJG-XM-2026001
        :return: 项目编码
        """
        code_rule = self.config.get_code_rule()
        prefix = code_rule.get('prefix', 'ZHJG-XM-')
        year_format = code_rule.get('year_format', 'YYYY')
        sequence_digits = code_rule.get('sequence_digits', 3)
        
        # 获取年份
        now = datetime.now()
        if year_format == 'YY':
            year_str = now.strftime('%y')
        else:  # 默认YYYY
            year_str = now.strftime('%Y')
        
        # 查询当年已有项目数量，用于生成序号
        current_year = now.year
        count = self._get_project_count_by_year(current_year)
        
        # 生成序号（从001开始）
        sequence = str(count + 1).zfill(sequence_digits)
        
        return f"{prefix}{year_str}{sequence}"
    
    def _get_project_count_by_year(self, year: int) -> int:
        """获取指定年份的项目数量"""
        if not self.db_manager:
            return 0
        
        try:
            result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM projects WHERE YEAR(created_at) = %s",
                (year,)
            )
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取项目数量失败: {e}")
            return 0
    
    # ==================== 项目CRUD操作 ====================
    
    def create_project(self, project_data: Dict[str, Any]) -> tuple:
        """
        创建新项目
        :param project_data: 项目数据字典
        :return: (是否成功, 项目ID或错误信息)
        """
        # 如果没有提供项目编码，自动生成
        if not project_data.get('project_code'):
            project_data['project_code'] = self.generate_project_code()
        
        # 数据验证
        valid, msg = self._validate_project_data(project_data)
        if not valid:
            return False, msg
        
        # 检查项目编码是否已存在
        existing = self.project_db.get_project_by_code(project_data.get('project_code', ''))
        if existing:
            return False, "项目编码已存在"
        
        # 创建项目对象
        project = Project.from_dict(project_data)
        if not project.status:
            project.status = ProjectStatus.BIDDING
        project.created_at = datetime.now()
        project.updated_at = datetime.now()
        
        # 保存到数据库
        success, result = self.project_db.add_project(project)
        
        if success:
            self._notify_observers('PROJECT_CREATED', {'project_id': result})
        
        return success, result
    
    def update_project(self, project_id: int, project_data: Dict[str, Any]) -> tuple:
        """
        更新项目信息
        :param project_id: 项目ID
        :param project_data: 项目数据字典
        :return: (是否成功, 错误信息)
        """
        # 获取原项目
        project = self.project_db.get_project_by_id(project_id)
        if not project:
            return False, "项目不存在"
        
        # 数据验证
        valid, msg = self._validate_project_data(project_data, is_update=True)
        if not valid:
            return False, msg
        
        # 检查项目编码是否与其他项目冲突
        new_code = project_data.get('project_code', '')
        if new_code and new_code != project.project_code:
            existing = self.project_db.get_project_by_code(new_code)
            if existing and existing.id != project_id:
                return False, "项目编码已存在"
        
        # 更新项目对象
        project.name = project_data.get('name', project.name)
        project.project_code = project_data.get('project_code', project.project_code)
        project.project_type = self.model.get_type_from_value(
            project_data.get('project_type', project.project_type.value)
        )
        project.status = self.model.get_status_from_value(
            project_data.get('status', project.status.value)
        )
        
        # 金额信息
        project.bid_amount = float(project_data.get('bid_amount', project.bid_amount))
        project.contract_amount = float(project_data.get('contract_amount', project.contract_amount))
        project.received_amount = float(project_data.get('received_amount', project.received_amount))
        project.paid_amount = float(project_data.get('paid_amount', project.paid_amount))
        
        # 附件信息
        project.bid_attachment = project_data.get('bid_attachment', project.bid_attachment)
        project.construction_attachment = project_data.get('construction_attachment', project.construction_attachment)
        
        # 备注
        project.remark = project_data.get('remark', project.remark)
        
        project.updated_at = datetime.now()
        
        # 处理日期
        if 'start_date' in project_data:
            start_date = project_data['start_date']
            if isinstance(start_date, str) and start_date:
                project.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        if 'completion_date' in project_data:
            completion_date = project_data['completion_date']
            if isinstance(completion_date, str) and completion_date:
                project.completion_date = datetime.strptime(completion_date, '%Y-%m-%d')
        
        # 保存到数据库
        success, msg = self.project_db.update_project(project)
        
        if success:
            self._notify_observers('PROJECT_UPDATED', {'project_id': project_id})
        
        return success, msg
    
    def delete_project(self, project_id: int) -> tuple:
        """
        删除项目
        :param project_id: 项目ID
        :return: (是否成功, 错误信息)
        """
        # 先检查项目是否存在
        project = self.project_db.get_project_by_id(project_id)
        if not project:
            return False, "项目不存在"
        
        success, msg = self.project_db.delete_project(project_id)
        
        if success:
            self._notify_observers('PROJECT_DELETED', {'project_id': project_id})
        
        return success, msg
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """
        获取单个项目
        :param project_id: 项目ID
        :return: 项目对象或None
        """
        return self.project_db.get_project_by_id(project_id)
    
    def get_project_by_code(self, project_code: str) -> Optional[Project]:
        """
        根据编码获取项目
        :param project_code: 项目编码
        :return: 项目对象或None
        """
        return self.project_db.get_project_by_code(project_code)
    
    def get_projects(self, status: str = None, project_type: str = None,
                     keyword: str = None, limit: int = 100, offset: int = 0) -> List[Project]:
        """
        获取项目列表
        :param status: 状态筛选
        :param project_type: 类型筛选
        :param keyword: 关键词搜索
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 项目列表
        """
        return self.project_db.get_projects(status, project_type, keyword, limit, offset)
    
    def get_project_count(self, status: str = None, project_type: str = None,
                          keyword: str = None) -> int:
        """
        获取项目数量
        :param status: 状态筛选
        :param project_type: 类型筛选
        :param keyword: 关键词搜索
        :return: 项目数量
        """
        return self.project_db.get_project_count(status, project_type, keyword)
    
    # ==================== 项目状态管理 ====================
    
    def change_project_status(self, project_id: int, new_status: str) -> tuple:
        """
        修改项目状态
        :param project_id: 项目ID
        :param new_status: 新状态
        :return: (是否成功, 错误信息)
        """
        project = self.project_db.get_project_by_id(project_id)
        if not project:
            return False, "项目不存在"
        
        try:
            status_enum = self.model.get_status_from_value(new_status)
            project.status = status_enum
            project.updated_at = datetime.now()
            
            success, msg = self.project_db.update_project(project)
            
            if success:
                self._notify_observers('PROJECT_STATUS_CHANGED', {
                    'project_id': project_id,
                    'new_status': new_status
                })
            
            return success, msg
        except Exception as e:
            return False, str(e)
    
    # ==================== 统计查询 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取项目统计数据
        :return: 统计数据字典
        """
        return self.project_db.get_statistics()
    
    def get_status_counts(self) -> Dict[str, int]:
        """
        获取各状态的项目数量
        :return: 数量字典
        """
        return {
            'all': self.get_project_count(),
            'bidding': self.get_project_count(status='投标阶段'),
            'construction': self.get_project_count(status='施工阶段'),
            'settlement': self.get_project_count(status='结算阶段'),
            'completed': self.get_project_count(status='完工阶段'),
        }
    
    # ==================== 数据验证 ====================
    
    def _validate_project_data(self, data: Dict[str, Any], is_update: bool = False) -> tuple:
        """
        验证项目数据
        :param data: 项目数据字典
        :param is_update: 是否为更新操作
        :return: (是否有效, 错误信息)
        """
        # 项目编码验证
        project_code = data.get('project_code', '').strip()
        if not is_update or project_code:  # 新增时必须，更新时如果提供则验证
            if not project_code:
                return False, "项目编码不能为空"
            if len(project_code) > 50:
                return False, "项目编码不能超过50个字符"
        
        # 项目名称验证
        name = data.get('name', '').strip()
        if not is_update or name:  # 新增时必须，更新时如果提供则验证
            if not name:
                return False, "项目名称不能为空"
            if len(name) > 200:
                return False, "项目名称不能超过200个字符"
        
        # 项目类型验证
        project_type = data.get('project_type', '')
        if project_type and project_type not in self.model.get_type_list():
            return False, f"无效的项目类型: {project_type}"
        
        # 项目状态验证
        status = data.get('status', '')
        if status and status not in self.model.get_status_list():
            return False, f"无效的项目状态: {status}"
        
        # 金额验证
        for field_name in ['bid_amount', 'contract_amount', 'received_amount', 'paid_amount']:
            amount = data.get(field_name, 0)
            if amount:
                try:
                    amount_val = float(amount)
                    if amount_val < 0:
                        return False, f"{field_name}必须是非负数"
                except (ValueError, TypeError):
                    return False, f"{field_name}必须是有效数字"
        
        return True, "验证通过"
    
    # ==================== 配置管理 ====================
    
    def get_code_config(self) -> Dict[str, Any]:
        """获取编码配置"""
        return self.config.get_code_rule()
    
    def update_code_config(self, prefix: str = None, year_format: str = None, sequence_digits: int = None) -> bool:
        """更新编码配置"""
        return self.config.set_code_rule(prefix, year_format, sequence_digits)
    
    # ==================== 辅助方法 ====================
    
    def get_status_list(self) -> List[str]:
        """获取状态列表"""
        return self.model.get_status_list()
    
    def get_type_list(self) -> List[str]:
        """获取类型列表"""
        return self.model.get_type_list()
