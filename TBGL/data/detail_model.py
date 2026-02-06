"""
投标明细表数据模型
支持层级结构的明细表数据管理
与汇总表通过 summary_item_id 关联
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class DetailItem:
    """投标明细项目（树形节点）
    
    字段说明：
    - sequence: 序号
    - name: 分部分项工程名称
    - description: 项目特征描述
    - unit: 单位
    - quantity: 工程量
    - unit_price: 综合单价
    - total_price: 合价
    - labor_price: 人工单价
    - main_material_price: 主材单价
    - main_material_loss_rate: 主材损耗率(%)
    - aux_material_price: 辅材单价
    - machinery_price: 机械单价
    - other_price: 其他单价
    """
    id: Optional[int] = None
    detail_id: int = 0
    parent_id: Optional[int] = None  # 父节点ID，None表示根节点
    
    # 显示信息
    sequence: str = ""           # 序号
    name: str = ""               # 分部分项工程名称
    specification: str = ""      # 规格型号
    description: str = ""        # 项目特征描述
    unit: str = ""               # 单位
    
    # 数量和价格
    quantity: float = 0.0        # 工程量
    unit_price: float = 0.0      # 综合单价
    total_price: float = 0.0     # 合价
    
    # 各项单价
    labor_price: float = 0.0             # 人工单价
    main_material_price: float = 0.0     # 主材单价
    main_material_loss_rate: float = 0.0 # 主材损耗率(%)
    aux_material_price: float = 0.0      # 辅材单价
    machinery_price: float = 0.0         # 机械单价
    other_price: float = 0.0             # 其他单价
    
    # 各项合价（由计算得出）
    labor_total: float = 0.0         # 人工合价
    material_total: float = 0.0      # 主材合价
    auxiliary_total: float = 0.0     # 辅材合价
    machine_total: float = 0.0       # 机械合价
    other_total: float = 0.0         # 其他合价
    management_total: float = 0.0    # 管理费合计
    tax_total: float = 0.0           # 税金合价
    comprehensive_total: float = 0.0 # 综合合价
    
    # 其他
    remark: str = ""             # 备注
    sort_order: int = 0          # 排序顺序
    level: int = 1               # 层级（用于UI显示）
    
    # 子节点
    children: List['DetailItem'] = field(default_factory=list)
    
    def calculate_totals(self):
        """计算各项合价"""
        # 基本合价
        self.total_price = self.quantity * self.unit_price
        
        # 各项费用合价
        self.labor_total = self.quantity * self.labor_price
        # 主材合价 = 工程量 × 主材单价 × (1 + 损耗率/100)
        self.material_total = self.quantity * self.main_material_price * (1 + self.main_material_loss_rate / 100)
        self.auxiliary_total = self.quantity * self.aux_material_price
        self.machine_total = self.quantity * self.machinery_price
        self.other_total = self.quantity * self.other_price
        
        # 综合合价 = 基本合价 + 管理费 + 税金
        self.comprehensive_total = self.total_price + self.management_total + self.tax_total
        
        return self.total_price
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'detail_id': self.detail_id,
            'parent_id': self.parent_id,
            'sequence': self.sequence,
            'name': self.name,
            'description': self.description,
            'unit': self.unit,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'labor_price': self.labor_price,
            'main_material_price': self.main_material_price,
            'main_material_loss_rate': self.main_material_loss_rate,
            'aux_material_price': self.aux_material_price,
            'machinery_price': self.machinery_price,
            'other_price': self.other_price,
            'labor_total': self.labor_total,
            'material_total': self.material_total,
            'auxiliary_total': self.auxiliary_total,
            'machine_total': self.machine_total,
            'other_total': self.other_total,
            'management_total': self.management_total,
            'tax_total': self.tax_total,
            'comprehensive_total': self.comprehensive_total,
            'remark': self.remark,
            'sort_order': self.sort_order,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DetailItem':
        """从字典创建"""
        return cls(
            id=data.get('id'),
            detail_id=data.get('detail_id', 0),
            parent_id=data.get('parent_id'),
            sequence=data.get('sequence', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            unit=data.get('unit', ''),
            quantity=float(data.get('quantity', 0)),
            unit_price=float(data.get('unit_price', 0)),
            total_price=float(data.get('total_price', 0)),
            labor_price=float(data.get('labor_price', 0)),
            main_material_price=float(data.get('main_material_price', 0)),
            main_material_loss_rate=float(data.get('main_material_loss_rate', 0)),
            aux_material_price=float(data.get('aux_material_price', 0)),
            machinery_price=float(data.get('machinery_price', 0)),
            other_price=float(data.get('other_price', 0)),
            labor_total=float(data.get('labor_total', 0)),
            material_total=float(data.get('material_total', 0)),
            auxiliary_total=float(data.get('auxiliary_total', 0)),
            machine_total=float(data.get('machine_total', 0)),
            other_total=float(data.get('other_total', 0)),
            management_total=float(data.get('management_total', 0)),
            tax_total=float(data.get('tax_total', 0)),
            comprehensive_total=float(data.get('comprehensive_total', 0)),
            remark=data.get('remark', ''),
            sort_order=data.get('sort_order', 0),
        )


@dataclass
class BiddingDetail:
    """投标明细表"""
    id: Optional[int] = None
    bidding_id: int = 0
    summary_item_id: int = 0      # 关联的汇总项ID（关键关联字段）
    version: str = "V1.0"         # 版本号
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = ""          # 创建人
    remark: str = ""              # 备注
    
    # 根节点列表（树形结构）
    items: List[DetailItem] = field(default_factory=list)
    
    def calculate_summary(self) -> dict:
        """计算汇总数据（用于回写到汇总表）
        
        Returns:
            dict: 包含各项费用汇总的字典
        """
        summary = {
            'quote_price': 0.0,
            'labor_fee': 0.0,
            'main_material_fee': 0.0,
            'aux_material_fee': 0.0,
            'machinery_fee': 0.0,
            'other_fee': 0.0,
            'management_fee': 0.0,
            'tax_fee': 0.0,
        }
        
        def accumulate(item: DetailItem):
            """递归累加"""
            # 累加当前节点的值
            summary['quote_price'] += item.total_price
            summary['labor_fee'] += item.labor_total
            summary['main_material_fee'] += item.material_total
            summary['aux_material_fee'] += item.auxiliary_total
            summary['machinery_fee'] += item.machine_total
            summary['other_fee'] += item.other_total
            summary['management_fee'] += item.management_total
            summary['tax_fee'] += item.tax_total
            
            # 递归处理子节点
            for child in item.children:
                accumulate(child)
        
        for item in self.items:
            accumulate(item)
        
        return summary
    
    def build_tree(self, flat_items: List[DetailItem]):
        """从扁平列表构建树形结构"""
        # 清空现有数据
        self.items = []
        
        # 按parent_id分组
        item_map = {item.id: item for item in flat_items if item.id}
        
        for item in flat_items:
            if item.parent_id is None:
                # 根节点
                item.level = 1
                self.items.append(item)
            else:
                # 子节点
                parent = item_map.get(item.parent_id)
                if parent:
                    parent.children.append(item)
                    item.level = parent.level + 1
        
        # 按sort_order排序
        self.items.sort(key=lambda x: x.sort_order)
        for item in self.items:
            item.children.sort(key=lambda x: x.sort_order)
    
    def flatten_items(self) -> List[DetailItem]:
        """将树形结构展开为扁平列表"""
        result = []
        
        def traverse(item: DetailItem):
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
            'summary_item_id': self.summary_item_id,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'remark': self.remark,
        }


class DetailSummary:
    """明细汇总数据（用于回写到汇总表）"""
    
    def __init__(self):
        self.quote_price: float = 0.0
        self.labor_fee: float = 0.0
        self.main_material_fee: float = 0.0
        self.aux_material_fee: float = 0.0
        self.machinery_fee: float = 0.0
        self.other_fee: float = 0.0
        self.management_fee: float = 0.0
        self.tax_fee: float = 0.0
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'quote_price': self.quote_price,
            'labor_fee': self.labor_fee,
            'main_material_fee': self.main_material_fee,
            'aux_material_fee': self.aux_material_fee,
            'machinery_fee': self.machinery_fee,
            'other_fee': self.other_fee,
            'management_fee': self.management_fee,
            'tax_fee': self.tax_fee,
        }
