"""
项目数据模型
定义项目的数据结构和状态
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ProjectStatus(Enum):
    """项目状态枚举"""
    BIDDING = "投标阶段"
    CONSTRUCTION = "施工阶段"
    SETTLEMENT = "结算阶段"
    COMPLETED = "完工阶段"


class ProjectType(Enum):
    """项目类型枚举"""
    INDUSTRIAL = "工业建筑"
    CIVIL = "民用建筑"
    LANDSCAPE = "园林绿化"
    MAINTENANCE = "厂区维修"
    OTHER = "其他"


@dataclass
class Project:
    """项目数据类"""
    # 基本信息
    id: Optional[int] = None
    project_code: str = ""  # 项目编码
    name: str = ""  # 项目名称
    project_type: ProjectType = ProjectType.INDUSTRIAL  # 项目类型
    
    # 项目状态
    status: ProjectStatus = ProjectStatus.BIDDING  # 项目状态
    
    # 金额信息
    bid_amount: float = 0.0  # 投标金额
    contract_amount: float = 0.0  # 合同金额
    received_amount: float = 0.0  # 实收金额
    paid_amount: float = 0.0  # 实付金额
    
    # 日期信息
    start_date: Optional[datetime] = None  # 开始日期
    completion_date: Optional[datetime] = None  # 竣工日期
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间
    
    # 附件信息（存储文件路径）
    bid_attachment: str = ""  # 投标附件路径
    construction_attachment: str = ""  # 施工附件路径
    
    # 备注
    remark: str = ""  # 备注
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'project_code': self.project_code,
            'name': self.name,
            'project_type': self.project_type.value if isinstance(self.project_type, ProjectType) else self.project_type,
            'status': self.status.value if isinstance(self.status, ProjectStatus) else self.status,
            'bid_amount': self.bid_amount,
            'contract_amount': self.contract_amount,
            'received_amount': self.received_amount,
            'paid_amount': self.paid_amount,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'completion_date': self.completion_date.strftime('%Y-%m-%d') if self.completion_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'bid_attachment': self.bid_attachment,
            'construction_attachment': self.construction_attachment,
            'remark': self.remark,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """从字典创建对象"""
        # 处理枚举类型
        project_type = data.get('project_type', '工业建筑')
        if isinstance(project_type, str):
            project_type = ProjectType(project_type)
        
        status = data.get('status', '投标阶段')
        if isinstance(status, str):
            status = ProjectStatus(status)
        
        # 处理日期时间
        start_date = data.get('start_date')
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        completion_date = data.get('completion_date')
        if isinstance(completion_date, str):
            completion_date = datetime.strptime(completion_date, '%Y-%m-%d')
        
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
        
        return cls(
            id=data.get('id'),
            project_code=data.get('project_code', ''),
            name=data.get('name', ''),
            project_type=project_type,
            status=status,
            bid_amount=data.get('bid_amount', 0.0),
            contract_amount=data.get('contract_amount', 0.0),
            received_amount=data.get('received_amount', 0.0),
            paid_amount=data.get('paid_amount', 0.0),
            start_date=start_date,
            completion_date=completion_date,
            created_at=created_at,
            updated_at=updated_at,
            bid_attachment=data.get('bid_attachment', ''),
            construction_attachment=data.get('construction_attachment', ''),
            remark=data.get('remark', ''),
        )


class ProjectModel:
    """项目数据模型管理类"""
    
    @staticmethod
    def get_status_list() -> list:
        """获取所有状态列表"""
        return [status.value for status in ProjectStatus]
    
    @staticmethod
    def get_type_list() -> list:
        """获取所有类型列表"""
        return [project_type.value for project_type in ProjectType]
    
    @staticmethod
    def get_status_from_value(value: str) -> ProjectStatus:
        """从字符串值获取状态枚举"""
        for status in ProjectStatus:
            if status.value == value:
                return status
        return ProjectStatus.BIDDING
    
    @staticmethod
    def get_type_from_value(value: str) -> ProjectType:
        """从字符串值获取类型枚举"""
        for project_type in ProjectType:
            if project_type.value == value:
                return project_type
        return ProjectType.INDUSTRIAL
