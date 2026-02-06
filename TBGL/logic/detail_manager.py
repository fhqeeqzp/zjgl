"""
投标明细管理器
负责投标明细的业务逻辑处理
"""
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from ..data.detail_model import BiddingDetail, DetailItem
from ..data.detail_db import DetailDatabase


class DetailManager:
    """投标明细管理器类"""
    
    def __init__(self, db_manager=None):
        """
        初始化明细管理器
        :param db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.db = DetailDatabase(db_manager)
        
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
        初始化明细数据库表
        :return: 是否成功
        """
        return self.db.init_tables()
    
    # ==================== 明细保存（核心方法）====================
    
    def save_detail(self, detail: BiddingDetail, update_summary: bool = True) -> tuple:
        """
        保存投标明细（核心方法）
        
        流程：
        1. 保存明细主表到 bidding_details
        2. 递归保存明细项目到 bidding_detail_items（树形结构）
        3. 计算各项费用汇总
        4. 更新对应汇总项的报价数据（如果 update_summary=True）
        5. 通知观察者刷新UI
        
        :param detail: 投标明细对象
        :param update_summary: 是否更新汇总表
        :return: (是否成功, 明细表ID或错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            # 1. 保存明细主表
            if detail.id:
                # 更新现有记录
                detail = self.db.update(detail)
                # 删除旧的明细项目（重新保存）
                self.db.delete_items_by_detail(detail.id)
            else:
                # 插入新记录
                detail = self.db.insert(detail)
            
            if not detail.id:
                return False, "保存明细主表失败"
            
            # 2. 递归保存明细项目（树形结构）
            self._save_items_recursive(detail.id, detail.items, None, 0)
            
            # 3. 计算汇总数据
            summary_data = detail.calculate_summary()
            
            # 4. 更新汇总表（如果需要）
            if update_summary and detail.summary_item_id:
                self._update_summary_item(detail.summary_item_id, summary_data)
            
            # 5. 通知观察者
            self._notify_observers('DETAIL_SAVED', {
                'bidding_id': detail.bidding_id,
                'detail_id': detail.id,
                'summary_item_id': detail.summary_item_id,
                'summary_data': summary_data
            })
            
            return True, detail.id
            
        except Exception as e:
            return False, f"保存明细失败: {e}"
    
    def _save_items_recursive(self, detail_id: int, items: List[DetailItem], 
                             parent_id: int = None, start_order: int = 0) -> int:
        """
        递归保存明细项目
        
        :param detail_id: 明细表ID
        :param items: 明细项目列表
        :param parent_id: 父节点ID
        :param start_order: 起始排序顺序
        :return: 保存的项目数量
        """
        count = 0
        for idx, item in enumerate(items):
            # 设置明细表ID和父节点ID
            item.detail_id = detail_id
            item.parent_id = parent_id
            item.sort_order = start_order + idx

            # 先递归保存子节点（确保子节点的ID已生成）
            if item.children:
                # 先保存当前项目（父节点），获取ID
                saved_item = self.db.insert_item(item)
                if saved_item.id:
                    count += 1
                    # 递归保存子节点
                    count += self._save_items_recursive(
                        detail_id, item.children, saved_item.id, 0
                    )
                    # 子节点保存完成后，重新计算父节点的汇总值
                    self._calculate_parent_totals(item)
                    # 更新父节点的合价值到数据库
                    self.db.update_item(item)
            else:
                # 叶子节点：计算合价并保存
                item.calculate_totals()
                saved_item = self.db.insert_item(item)
                if saved_item.id:
                    count += 1
        
        return count
    
    def _calculate_parent_totals(self, parent_item: DetailItem):
        """计算父级节点的汇总值（从子节点汇总）"""
        # 重置汇总值
        total_price = 0.0
        labor_total = 0.0
        material_total = 0.0
        auxiliary_total = 0.0
        machine_total = 0.0
        other_total = 0.0
        management_total = 0.0
        tax_total = 0.0
        comprehensive_total = 0.0
        
        # 累加所有子节点的值
        for child in parent_item.children:
            total_price += child.total_price
            labor_total += child.labor_total
            material_total += child.material_total
            auxiliary_total += child.auxiliary_total
            machine_total += child.machine_total
            other_total += child.other_total
            management_total += child.management_total
            tax_total += child.tax_total
            comprehensive_total += child.comprehensive_total
        
        # 更新父节点的值
        parent_item.total_price = total_price
        parent_item.labor_total = labor_total
        parent_item.material_total = material_total
        parent_item.auxiliary_total = auxiliary_total
        parent_item.machine_total = machine_total
        parent_item.other_total = other_total
        parent_item.management_total = management_total
        parent_item.tax_total = tax_total
        parent_item.comprehensive_total = comprehensive_total
    
    def _update_summary_item(self, summary_item_id: int, summary_data: dict):
        """
        更新汇总项的报价数据
        
        :param summary_item_id: 汇总项ID
        :param summary_data: 汇总数据字典
        """
        if not self.db_manager or not summary_item_id:
            return
        
        try:
            sql = """
            UPDATE bidding_summary_items
            SET quote_price = %s,
                labor_fee = %s,
                main_material_fee = %s,
                aux_material_fee = %s,
                machinery_fee = %s,
                other_fee = %s,
                management_fee = %s,
                tax_fee = %s
            WHERE id = %s
            """
            params = (
                summary_data.get('quote_price', 0),
                summary_data.get('labor_fee', 0),
                summary_data.get('main_material_fee', 0),
                summary_data.get('aux_material_fee', 0),
                summary_data.get('machinery_fee', 0),
                summary_data.get('other_fee', 0),
                summary_data.get('management_fee', 0),
                summary_data.get('tax_fee', 0),
                summary_item_id
            )
            self.db_manager.execute_update(sql, params)
            
            # 通知汇总表更新
            self._notify_observers('SUMMARY_UPDATED', {
                'summary_item_id': summary_item_id,
                'summary_data': summary_data
            })
            
        except Exception as e:
            print(f"更新汇总项失败: {e}")
    
    # ==================== 明细查询 ====================
    
    def get_detail(self, detail_id: int) -> Optional[BiddingDetail]:
        """
        根据ID获取明细
        :param detail_id: 明细表ID
        :return: 明细对象
        """
        return self.db.get_by_id(detail_id)
    
    def get_detail_by_summary_item(self, bidding_id: int, summary_item_id: int,
                                   version: str = None) -> Optional[BiddingDetail]:
        """
        根据汇总项ID获取明细
        :param bidding_id: 投标ID
        :param summary_item_id: 汇总项ID
        :param version: 版本号（None表示获取最新版本）
        :return: 明细对象
        """
        return self.db.get_by_summary_item(bidding_id, summary_item_id, version)
    
    def get_versions(self, bidding_id: int, summary_item_id: int) -> List[str]:
        """
        获取指定汇总项的所有版本号
        :param bidding_id: 投标ID
        :param summary_item_id: 汇总项ID
        :return: 版本号列表
        """
        return self.db.get_versions(bidding_id, summary_item_id)
    
    # ==================== 明细删除 ====================
    
    def delete_detail(self, detail_id: int) -> tuple:
        """
        删除明细
        :param detail_id: 明细表ID
        :return: (是否成功, 错误信息)
        """
        success = self.db.delete(detail_id)
        if success:
            self._notify_observers('DETAIL_DELETED', {'detail_id': detail_id})
            return True, "删除成功"
        else:
            return False, "删除失败"
    
    # ==================== 辅助方法 ====================
    
    def calculate_summary(self, items: List[DetailItem]) -> dict:
        """
        计算明细汇总数据
        
        :param items: 明细项目列表
        :return: 汇总数据字典
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
        
        for item in items:
            accumulate(item)
        
        return summary
    
    def create_new_version(self, bidding_id: int, summary_item_id: int,
                          base_version: str = None) -> str:
        """
        创建新版本号
        
        :param bidding_id: 投标ID
        :param summary_item_id: 汇总项ID
        :param base_version: 基础版本号（None表示自动生成）
        :return: 新版本号
        """
        if base_version:
            # 基于指定版本递增
            try:
                if base_version.startswith('V'):
                    version_num = float(base_version[1:])
                    new_version = f"V{version_num + 0.1:.1f}"
                else:
                    new_version = f"V{float(base_version) + 0.1:.1f}"
            except:
                new_version = "V1.0"
        else:
            # 获取现有版本列表
            versions = self.get_versions(bidding_id, summary_item_id)
            if not versions:
                new_version = "V1.0"
            else:
                # 找到最大版本号并递增
                max_version = 0.0
                for v in versions:
                    try:
                        if v.startswith('V'):
                            version_num = float(v[1:])
                        else:
                            version_num = float(v)
                        max_version = max(max_version, version_num)
                    except:
                        continue
                new_version = f"V{max_version + 0.1:.1f}"
        
        return new_version
