"""
投标汇总表数据模型
支持层级结构的汇总表数据管理
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SummaryItemType(Enum):
    """汇总表项目类型"""
    CATEGORY = "category"      # 分类/章节（一级）
    SUBCATEGORY = "subcategory"  # 子分类（二级）
    ITEM = "item"              # 具体项目（三级）


@dataclass
class SummaryItem:
    """汇总表项目（树形节点）
    
    字段说明：
    - sequence: 序号
    - name: 工程项目及费用名称
    - quote_price: 报价
    - main_material_fee: 其中：主材费
    - aux_material_fee: 其中：辅材费
    - labor_fee: 其中：人工费
    - machinery_fee: 其中：机械费
    - other_fee: 其中：其他费
    - management_fee: 其中：管理费
    - tax_fee: 其中：税金
    """
    id: int = 0
    summary_id: int = 0
    parent_id: Optional[int] = None  # 父节点ID，None表示根节点
    item_type: SummaryItemType = SummaryItemType.ITEM
    
    # 显示信息
    sequence: str = ""           # 序号
    name: str = ""               # 工程项目及费用名称
    
    # 费用字段
    quote_price: float = 0.0     # 报价
    main_material_fee: float = 0.0   # 其中：主材费
    aux_material_fee: float = 0.0    # 其中：辅材费
    labor_fee: float = 0.0       # 其中：人工费
    machinery_fee: float = 0.0   # 其中：机械费
    other_fee: float = 0.0       # 其中：其他费
    management_fee: float = 0.0  # 其中：管理费
    tax_fee: float = 0.0         # 其中：税金
    
    # 子节点
    children: List['SummaryItem'] = field(default_factory=list)
    
    def calculate_quote_price(self):
        """计算报价（各项费用之和）"""
        if self.item_type == SummaryItemType.ITEM:
            self.quote_price = (
                self.main_material_fee +
                self.aux_material_fee +
                self.labor_fee +
                self.machinery_fee +
                self.other_fee +
                self.management_fee +
                self.tax_fee
            )
        else:
            # 分类节点金额为子节点金额之和
            self.quote_price = sum(child.quote_price for child in self.children)
        return self.quote_price
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'summary_id': self.summary_id,
            'parent_id': self.parent_id,
            'item_type': self.item_type.value,
            'sequence': self.sequence,
            'name': self.name,
            'quote_price': self.quote_price,
            'main_material_fee': self.main_material_fee,
            'aux_material_fee': self.aux_material_fee,
            'labor_fee': self.labor_fee,
            'machinery_fee': self.machinery_fee,
            'other_fee': self.other_fee,
            'management_fee': self.management_fee,
            'tax_fee': self.tax_fee,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SummaryItem':
        """从字典创建"""
        return cls(
            id=data.get('id', 0),
            summary_id=data.get('summary_id', 0),
            parent_id=data.get('parent_id'),
            item_type=SummaryItemType(data.get('item_type', 'item')),
            sequence=data.get('sequence', ''),
            name=data.get('name', ''),
            quote_price=float(data.get('quote_price', 0)),
            main_material_fee=float(data.get('main_material_fee', 0)),
            aux_material_fee=float(data.get('aux_material_fee', 0)),
            labor_fee=float(data.get('labor_fee', 0)),
            machinery_fee=float(data.get('machinery_fee', 0)),
            other_fee=float(data.get('other_fee', 0)),
            management_fee=float(data.get('management_fee', 0)),
            tax_fee=float(data.get('tax_fee', 0)),
        )


@dataclass
class BiddingSummary:
    """投标汇总表"""
    id: int = 0
    bidding_id: int = 0
    version: str = "V1.0"           # 版本号
    version_name: str = "初始版本"   # 版本名称
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""             # 创建人
    remark: str = ""                 # 备注
    is_active: bool = True           # 是否为当前生效版本
    
    # 根节点列表（树形结构）
    items: List[SummaryItem] = field(default_factory=list)
    
    def calculate_total(self) -> float:
        """计算汇总表总价"""
        return sum(item.quote_price for item in self.items)
    
    def build_tree(self, flat_items: List[SummaryItem]):
        """从扁平列表构建树形结构"""
        # 清空现有数据
        self.items = []
        
        # 按parent_id分组
        item_map = {item.id: item for item in flat_items}
        
        for item in flat_items:
            if item.parent_id is None:
                # 根节点
                self.items.append(item)
            else:
                # 子节点
                parent = item_map.get(item.parent_id)
                if parent:
                    parent.children.append(item)
        
        # 按sequence排序
        self.items.sort(key=lambda x: x.sequence)
        for item in self.items:
            item.children.sort(key=lambda x: x.sequence)
    
    def flatten_items(self) -> List[SummaryItem]:
        """将树形结构展开为扁平列表"""
        result = []
        
        def traverse(item: SummaryItem):
            result.append(item)
            for child in item.children:
                traverse(child)
        
        for item in self.items:
            traverse(item)
        
        return result
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'bidding_id': self.bidding_id,
            'version': self.version,
            'version_name': self.version_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'remark': self.remark,
            'is_active': self.is_active,
            'total_amount': self.calculate_total(),
        }


class SummaryTemplate:
    """汇总表模板（用于快速创建）"""
    
    @staticmethod
    def get_default_template() -> List[dict]:
        """获取默认模板"""
        return [
            {
                'sequence': '一',
                'name': '分部分项工程',
                'item_type': 'category',
                'children': [
                    {'sequence': '1', 'name': '人工费', 'item_type': 'item'},
                    {'sequence': '2', 'name': '材料费', 'item_type': 'item'},
                    {'sequence': '3', 'name': '机械费', 'item_type': 'item'},
                ]
            },
            {
                'sequence': '二',
                'name': '措施项目',
                'item_type': 'category',
                'children': [
                    {'sequence': '1', 'name': '安全文明施工费', 'item_type': 'item'},
                    {'sequence': '2', 'name': '夜间施工增加费', 'item_type': 'item'},
                    {'sequence': '3', 'name': '脚手架', 'item_type': 'item'},
                ]
            },
            {
                'sequence': '三',
                'name': '其他项目',
                'item_type': 'category',
                'children': [
                    {'sequence': '1', 'name': '暂列金额', 'item_type': 'item'},
                    {'sequence': '2', 'name': '暂估价', 'item_type': 'item'},
                ]
            },
            {
                'sequence': '四',
                'name': '规费',
                'item_type': 'category',
                'children': [
                    {'sequence': '1', 'name': '社会保险费', 'item_type': 'item'},
                    {'sequence': '2', 'name': '住房公积金', 'item_type': 'item'},
                ]
            },
            {
                'sequence': '五',
                'name': '税金',
                'item_type': 'category',
                'children': [
                    {'sequence': '1', 'name': '增值税', 'item_type': 'item'},
                ]
            },
        ]
