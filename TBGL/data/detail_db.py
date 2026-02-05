"""
投标明细数据库操作类
负责投标明细数据的持久化操作
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from .detail_model import BiddingDetail, DetailItem


class DetailDatabase:
    """投标明细数据库操作类"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
    
    def init_tables(self) -> bool:
        """初始化明细表结构"""
        if not self.db:
            return False
        
        try:
            # 创建投标明细主表
            sql_detail = """
            CREATE TABLE IF NOT EXISTS bidding_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bidding_id INT NOT NULL COMMENT '投标ID',
                summary_item_id INT COMMENT '关联的汇总项ID',
                version VARCHAR(20) DEFAULT 'V1.0' COMMENT '版本号',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_by VARCHAR(100) COMMENT '创建人',
                remark TEXT COMMENT '备注',
                FOREIGN KEY (bidding_id) REFERENCES biddings(id) ON DELETE CASCADE,
                FOREIGN KEY (summary_item_id) REFERENCES bidding_summary_items(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标明细表'
            """
            self.db.execute_update(sql_detail)
            
            # 创建投标明细项目表
            sql_items = """
            CREATE TABLE IF NOT EXISTS bidding_detail_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                detail_id INT NOT NULL COMMENT '明细表ID',
                parent_id INT DEFAULT NULL COMMENT '父节点ID',
                sequence VARCHAR(50) COMMENT '序号',
                name VARCHAR(500) COMMENT '分部分项工程名称',
                description VARCHAR(1000) COMMENT '项目特征描述',
                unit VARCHAR(50) COMMENT '单位',
                quantity DECIMAL(15, 4) DEFAULT 0 COMMENT '工程量',
                unit_price DECIMAL(15, 2) DEFAULT 0 COMMENT '综合单价',
                total_price DECIMAL(15, 2) DEFAULT 0 COMMENT '合价',
                labor_price DECIMAL(15, 2) DEFAULT 0 COMMENT '人工单价',
                main_material_price DECIMAL(15, 2) DEFAULT 0 COMMENT '主材单价',
                main_material_loss_rate DECIMAL(5, 2) DEFAULT 0 COMMENT '主材损耗率(%)',
                aux_material_price DECIMAL(15, 2) DEFAULT 0 COMMENT '辅材单价',
                machinery_price DECIMAL(15, 2) DEFAULT 0 COMMENT '机械单价',
                other_price DECIMAL(15, 2) DEFAULT 0 COMMENT '其他单价',
                labor_total DECIMAL(15, 2) DEFAULT 0 COMMENT '人工合价',
                material_total DECIMAL(15, 2) DEFAULT 0 COMMENT '主材合价',
                auxiliary_total DECIMAL(15, 2) DEFAULT 0 COMMENT '辅材合价',
                machine_total DECIMAL(15, 2) DEFAULT 0 COMMENT '机械合价',
                other_total DECIMAL(15, 2) DEFAULT 0 COMMENT '其他合价',
                management_total DECIMAL(15, 2) DEFAULT 0 COMMENT '管理费合计',
                tax_total DECIMAL(15, 2) DEFAULT 0 COMMENT '税金合价',
                comprehensive_total DECIMAL(15, 2) DEFAULT 0 COMMENT '综合合价',
                remark VARCHAR(500) COMMENT '备注',
                sort_order INT DEFAULT 0 COMMENT '排序顺序',
                FOREIGN KEY (detail_id) REFERENCES bidding_details(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES bidding_detail_items(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标明细项目表'
            """
            self.db.execute_update(sql_items)
            return True
        except Exception as e:
            print(f"创建明细表失败: {e}")
            return False
    
    def insert(self, detail: BiddingDetail) -> BiddingDetail:
        """插入明细主表记录"""
        sql = """
        INSERT INTO bidding_details 
        (bidding_id, summary_item_id, version, created_by, remark)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            detail.bidding_id,
            detail.summary_item_id if detail.summary_item_id else None,
            detail.version,
            detail.created_by,
            detail.remark
        )
        self.db.execute_update(sql, params)
        
        # 获取新插入的ID
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        if result:
            detail.id = result[0]['id']
        
        return detail
    
    def update(self, detail: BiddingDetail) -> BiddingDetail:
        """更新明细主表记录"""
        sql = """
        UPDATE bidding_details 
        SET version = %s, remark = %s, updated_at = NOW()
        WHERE id = %s
        """
        params = (detail.version, detail.remark, detail.id)
        self.db.execute_update(sql, params)
        return detail
    
    def delete(self, detail_id: int) -> bool:
        """删除明细记录（级联删除明细项目）"""
        try:
            self.db.execute_update(
                "DELETE FROM bidding_details WHERE id = %s",
                (detail_id,)
            )
            return True
        except Exception as e:
            print(f"删除明细失败: {e}")
            return False
    
    def get_by_id(self, detail_id: int) -> Optional[BiddingDetail]:
        """根据ID获取明细记录"""
        sql = "SELECT * FROM bidding_details WHERE id = %s"
        result = self.db.execute_query(sql, (detail_id,))
        
        if not result:
            return None
        
        row = result[0]
        detail = BiddingDetail(
            id=row['id'],
            bidding_id=row['bidding_id'],
            summary_item_id=row['summary_item_id'] or 0,
            version=row['version'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            created_by=row['created_by'] or '',
            remark=row['remark'] or ''
        )
        
        # 加载明细项目
        detail.items = self.get_items(detail_id)
        return detail
    
    def get_by_summary_item(self, bidding_id: int, summary_item_id: int, 
                           version: str = None) -> Optional[BiddingDetail]:
        """根据汇总项ID获取明细记录"""
        if version:
            sql = """
            SELECT * FROM bidding_details 
            WHERE bidding_id = %s AND summary_item_id = %s AND version = %s
            ORDER BY created_at DESC LIMIT 1
            """
            params = (bidding_id, summary_item_id, version)
        else:
            sql = """
            SELECT * FROM bidding_details 
            WHERE bidding_id = %s AND summary_item_id = %s
            ORDER BY created_at DESC LIMIT 1
            """
            params = (bidding_id, summary_item_id)
        
        result = self.db.execute_query(sql, params)
        
        if not result:
            return None
        
        row = result[0]
        detail = BiddingDetail(
            id=row['id'],
            bidding_id=row['bidding_id'],
            summary_item_id=row['summary_item_id'] or 0,
            version=row['version'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            created_by=row['created_by'] or '',
            remark=row['remark'] or ''
        )
        
        # 加载明细项目
        detail.items = self.get_items(detail.id)
        return detail
    
    def get_items(self, detail_id: int) -> List[DetailItem]:
        """获取明细项目列表"""
        sql = """
        SELECT * FROM bidding_detail_items 
        WHERE detail_id = %s 
        ORDER BY sort_order
        """
        result = self.db.execute_query(sql, (detail_id,))
        
        items = []
        for row in result:
            item = DetailItem(
                id=row['id'],
                detail_id=row['detail_id'],
                parent_id=row['parent_id'],
                sequence=row['sequence'] or '',
                name=row['name'] or '',
                description=row['description'] or '',
                unit=row['unit'] or '',
                quantity=float(row['quantity'] or 0),
                unit_price=float(row['unit_price'] or 0),
                total_price=float(row['total_price'] or 0),
                labor_price=float(row['labor_price'] or 0),
                main_material_price=float(row['main_material_price'] or 0),
                main_material_loss_rate=float(row['main_material_loss_rate'] or 0),
                aux_material_price=float(row['aux_material_price'] or 0),
                machinery_price=float(row['machinery_price'] or 0),
                other_price=float(row['other_price'] or 0),
                labor_total=float(row['labor_total'] or 0),
                material_total=float(row['material_total'] or 0),
                auxiliary_total=float(row['auxiliary_total'] or 0),
                machine_total=float(row['machine_total'] or 0),
                other_total=float(row['other_total'] or 0),
                management_total=float(row['management_total'] or 0),
                tax_total=float(row['tax_total'] or 0),
                comprehensive_total=float(row['comprehensive_total'] or 0),
                remark=row['remark'] or '',
                sort_order=row['sort_order'] or 0
            )
            items.append(item)
        
        # 构建树形结构
        detail = BiddingDetail()
        detail.build_tree(items)
        return detail.items
    
    def insert_item(self, item: DetailItem) -> DetailItem:
        """插入明细项目"""
        sql = """
        INSERT INTO bidding_detail_items
        (detail_id, parent_id, sequence, name, description, unit, quantity,
         unit_price, total_price, labor_price, main_material_price, main_material_loss_rate,
         aux_material_price, machinery_price, other_price, labor_total, material_total,
         auxiliary_total, machine_total, other_total, management_total, tax_total,
         comprehensive_total, remark, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            item.detail_id,
            item.parent_id,
            item.sequence,
            item.name,
            item.description,
            item.unit,
            item.quantity,
            item.unit_price,
            item.total_price,
            item.labor_price,
            item.main_material_price,
            item.main_material_loss_rate,
            item.aux_material_price,
            item.machinery_price,
            item.other_price,
            item.labor_total,
            item.material_total,
            item.auxiliary_total,
            item.machine_total,
            item.other_total,
            item.management_total,
            item.tax_total,
            item.comprehensive_total,
            item.remark,
            item.sort_order
        )
        self.db.execute_update(sql, params)
        
        # 获取新插入的ID
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        if result:
            item.id = result[0]['id']
        
        return item
    
    def update_item(self, item: DetailItem) -> DetailItem:
        """更新明细项目"""
        sql = """
        UPDATE bidding_detail_items
        SET sequence = %s, name = %s, description = %s, unit = %s, quantity = %s,
            unit_price = %s, total_price = %s, labor_price = %s, main_material_price = %s,
            main_material_loss_rate = %s, aux_material_price = %s, machinery_price = %s,
            other_price = %s, labor_total = %s, material_total = %s, auxiliary_total = %s,
            machine_total = %s, other_total = %s, management_total = %s, tax_total = %s,
            comprehensive_total = %s, remark = %s, sort_order = %s
        WHERE id = %s
        """
        params = (
            item.sequence, item.name, item.description, item.unit, item.quantity,
            item.unit_price, item.total_price, item.labor_price, item.main_material_price,
            item.main_material_loss_rate, item.aux_material_price, item.machinery_price,
            item.other_price, item.labor_total, item.material_total, item.auxiliary_total,
            item.machine_total, item.other_total, item.management_total, item.tax_total,
            item.comprehensive_total, item.remark, item.sort_order, item.id
        )
        self.db.execute_update(sql, params)
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """删除明细项目"""
        try:
            self.db.execute_update(
                "DELETE FROM bidding_detail_items WHERE id = %s",
                (item_id,)
            )
            return True
        except Exception as e:
            print(f"删除明细项目失败: {e}")
            return False
    
    def delete_items_by_detail(self, detail_id: int) -> bool:
        """删除指定明细表的所有项目"""
        try:
            self.db.execute_update(
                "DELETE FROM bidding_detail_items WHERE detail_id = %s",
                (detail_id,)
            )
            return True
        except Exception as e:
            print(f"删除明细项目失败: {e}")
            return False
    
    def get_versions(self, bidding_id: int, summary_item_id: int) -> List[str]:
        """获取指定汇总项的所有版本号"""
        sql = """
        SELECT DISTINCT version FROM bidding_details 
        WHERE bidding_id = %s AND summary_item_id = %s
        ORDER BY version
        """
        result = self.db.execute_query(sql, (bidding_id, summary_item_id))
        return [row['version'] for row in result]
