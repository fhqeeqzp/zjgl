"""
投标数据模型
定义投标的数据结构和状态
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class BiddingStatus(Enum):
    """投标状态枚举"""
    IN_PROGRESS = "进行中"
    WON = "已中标"
    LOST = "未中标"
    WITHDRAWN = "已撤回"


@dataclass
class Bidding:
    """投标数据类"""
    # 基本信息
    id: Optional[int] = None
    bidding_code: str = ""  # 投标编码 (项目编码+TB-001)
    project_id: Optional[int] = None  # 关联的项目ID
    project_code: str = ""  # 项目编码（冗余存储）
    
    # 招标信息（从Word文档提取）
    tender_code: str = ""  # 招标编码
    bidding_name: str = ""  # 投标名称/招标项目名称
    tenderer: str = ""  # 招标人
    planned_duration: str = ""  # 计划工期
    bid_bond: float = 0.0  # 投标保证金
    bid_deadline: Optional[datetime] = None  # 开标日期/投标截止日期
    control_price: float = 0.0  # 招标控制价
    
    # 投标状态
    status: BiddingStatus = BiddingStatus.IN_PROGRESS
    
    # 附件路径
    tender_doc_path: str = ""  # 招标文件Word路径
    
    # 备注
    remark: str = ""
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
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
            'bidding_code': self.bidding_code,
            'project_id': self.project_id,
            'project_code': self.project_code,
            'tender_code': self.tender_code,
            'bidding_name': self.bidding_name,
            'tenderer': self.tenderer,
            'planned_duration': self.planned_duration,
            'bid_bond': self.bid_bond,
            'bid_deadline': self.bid_deadline.strftime('%Y-%m-%d') if self.bid_deadline else None,
            'control_price': self.control_price,
            'status': self.status.value if isinstance(self.status, BiddingStatus) else self.status,
            'tender_doc_path': self.tender_doc_path,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Bidding':
        """从字典创建对象"""
        # 处理枚举类型
        status = data.get('status', '进行中')
        if isinstance(status, str):
            status = BiddingStatus(status)
        
        # 处理日期时间
        bid_deadline = data.get('bid_deadline')
        if isinstance(bid_deadline, str):
            bid_deadline = datetime.strptime(bid_deadline, '%Y-%m-%d')
        
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
        
        return cls(
            id=data.get('id'),
            bidding_code=data.get('bidding_code', ''),
            project_id=data.get('project_id'),
            project_code=data.get('project_code', ''),
            tender_code=data.get('tender_code', ''),
            bidding_name=data.get('bidding_name', ''),
            tenderer=data.get('tenderer', ''),
            planned_duration=data.get('planned_duration', ''),
            bid_bond=float(data.get('bid_bond', 0.0)),
            bid_deadline=bid_deadline,
            control_price=float(data.get('control_price', 0.0)),
            status=status,
            tender_doc_path=data.get('tender_doc_path', ''),
            remark=data.get('remark', ''),
            created_at=created_at,
            updated_at=updated_at,
        )


class BiddingModel:
    """投标数据模型管理类"""
    
    @staticmethod
    def get_status_list() -> list:
        """获取所有状态列表"""
        return [status.value for status in BiddingStatus]
    
    @staticmethod
    def get_status_from_value(value: str) -> BiddingStatus:
        """从字符串值获取状态枚举"""
        for status in BiddingStatus:
            if status.value == value:
                return status
        return BiddingStatus.IN_PROGRESS
