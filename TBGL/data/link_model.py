"""
数据关联模型
定义汇总表和明细表之间的关联关系
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class DataLink:
    """数据关联模型"""
    id: Optional[int] = None
    bidding_id: int = 0  # 投标ID
    summary_item_id: int = 0  # 汇总表项目ID
    detail_item_id: int = 0  # 明细表项目ID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = ""
    remark: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'bidding_id': self.bidding_id,
            'summary_item_id': self.summary_item_id,
            'detail_item_id': self.detail_item_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'remark': self.remark
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataLink":
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            bidding_id=data.get('bidding_id', 0),
            summary_item_id=data.get('summary_item_id', 0),
            detail_item_id=data.get('detail_item_id', 0),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            created_by=data.get('created_by', ''),
            remark=data.get('remark', '')
        )


@dataclass
class DataLinkCollection:
    """数据关联集合"""
    bidding_id: int = 0
    links: List[DataLink] = field(default_factory=list)

    def add_link(self, summary_item_id: int, detail_item_id: int) -> DataLink:
        """添加关联"""
        # 检查是否已存在
        for link in self.links:
            if link.summary_item_id == summary_item_id:
                # 更新现有关联
                link.detail_item_id = detail_item_id
                link.updated_at = datetime.now()
                return link

        # 创建新关联
        new_link = DataLink(
            bidding_id=self.bidding_id,
            summary_item_id=summary_item_id,
            detail_item_id=detail_item_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.links.append(new_link)
        return new_link

    def remove_link(self, summary_item_id: int) -> bool:
        """移除关联"""
        for i, link in enumerate(self.links):
            if link.summary_item_id == summary_item_id:
                self.links.pop(i)
                return True
        return False

    def get_link(self, summary_item_id: int) -> Optional[DataLink]:
        """获取关联"""
        for link in self.links:
            if link.summary_item_id == summary_item_id:
                return link
        return None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'bidding_id': self.bidding_id,
            'links': [link.to_dict() for link in self.links]
        }
