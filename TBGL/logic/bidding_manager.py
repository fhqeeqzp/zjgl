"""
投标管理器
负责投标模块的业务逻辑处理
"""
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from ..data.bidding_model import Bidding, BiddingStatus, BiddingModel
from .tender_doc_parser import TenderDocParser


class BiddingManager:
    """投标管理器类"""
    
    def __init__(self, db_manager=None, project_manager=None):
        """
        初始化投标管理器
        :param db_manager: 数据库管理器实例
        :param project_manager: 项目管理器实例（用于获取投标阶段项目）
        """
        self.db_manager = db_manager
        self.project_manager = project_manager
        self.model = BiddingModel()
        
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
        初始化投标数据库表
        :return: 是否成功
        """
        if not self.db_manager:
            return False
        
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS biddings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bidding_code VARCHAR(50) NOT NULL UNIQUE COMMENT '投标编码',
                project_id INT COMMENT '关联项目ID',
                project_code VARCHAR(50) COMMENT '项目编码',
                tender_code VARCHAR(100) COMMENT '招标编码',
                bidding_name VARCHAR(200) COMMENT '投标名称',
                tenderer VARCHAR(200) COMMENT '招标人',
                planned_duration VARCHAR(50) COMMENT '计划工期',
                bid_bond DECIMAL(15, 2) DEFAULT 0 COMMENT '投标保证金',
                bid_deadline DATE COMMENT '开标日期',
                control_price DECIMAL(15, 2) DEFAULT 0 COMMENT '招标控制价',
                status VARCHAR(20) DEFAULT '进行中' COMMENT '投标状态',
                tender_doc_path VARCHAR(500) COMMENT '招标文件路径',
                remark TEXT COMMENT '备注',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标信息表'
            """
            self.db_manager.execute_update(sql)
            
            # 初始化汇总表
            self.init_summary_tables()
            
            return True
        except Exception as e:
            print(f"创建投标表失败: {e}")
            return False
    
    # ==================== 投标编码生成 ====================
    
    def generate_bidding_code(self, project_code: str) -> str:
        """
        生成投标编码
        格式: 项目编码 + TB-001
        例如: ZHJG-XM-2026001-TB-001
        :param project_code: 项目编码
        :return: 投标编码
        """
        if not self.db_manager:
            return f"{project_code}-TB-001"
        
        try:
            # 查询该项目下已有投标数量
            result = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM biddings WHERE project_code = %s",
                (project_code,)
            )
            count = result[0]['count'] if result else 0
            
            # 生成序号（从001开始）
            sequence = str(count + 1).zfill(3)
            
            return f"{project_code}-TB-{sequence}"
        except Exception as e:
            print(f"生成投标编码失败: {e}")
            return f"{project_code}-TB-001"
    
    # ==================== 获取投标阶段项目 ====================
    
    def get_bidding_projects(self) -> List[Dict[str, Any]]:
        """
        获取所有投标阶段的项目
        :return: 项目列表
        """
        if self.project_manager:
            projects = self.project_manager.get_projects(status='投标阶段')
            return [
                {
                    'id': p.id,
                    'project_code': p.project_code,
                    'name': p.name,
                    'display': f"{p.project_code} - {p.name}"
                }
                for p in projects
            ]
        return []
    
    # ==================== Word文档解析 ====================
    
    def parse_tender_document(self, file_path: str) -> Dict[str, Any]:
        """
        解析招标文件
        :param file_path: Word文档路径
        :return: 提取的数据字典
        """
        parser = TenderDocParser()
        return parser.parse(file_path)
    
    # ==================== 投标CRUD操作 ====================
    
    def create_bidding(self, bidding_data: Dict[str, Any]) -> tuple:
        """
        创建新投标
        :param bidding_data: 投标数据字典
        :return: (是否成功, 投标ID或错误信息)
        """
        # 数据验证
        valid, msg = self._validate_bidding_data(bidding_data)
        if not valid:
            return False, msg
        
        # 获取项目编码
        project_code = bidding_data.get('project_code', '')
        project_id = bidding_data.get('project_id')
        
        # 如果没有提供投标编码，自动生成
        if not bidding_data.get('bidding_code'):
            bidding_data['bidding_code'] = self.generate_bidding_code(project_code)
        
        # 检查投标编码是否已存在
        existing = self.get_bidding_by_code(bidding_data.get('bidding_code', ''))
        if existing:
            return False, "投标编码已存在"
        
        # 创建投标对象
        bidding = Bidding.from_dict(bidding_data)
        bidding.project_id = project_id
        bidding.project_code = project_code
        bidding.created_at = datetime.now()
        bidding.updated_at = datetime.now()
        
        # 保存到数据库
        success, result = self._save_bidding(bidding)
        
        if success:
            self._notify_observers('BIDDING_CREATED', {'bidding_id': result})
        
        return success, result
    
    def update_bidding(self, bidding_id: int, bidding_data: Dict[str, Any]) -> tuple:
        """
        更新投标信息
        :param bidding_id: 投标ID
        :param bidding_data: 投标数据字典
        :return: (是否成功, 错误信息)
        """
        # 获取原投标
        bidding = self.get_bidding(bidding_id)
        if not bidding:
            return False, "投标不存在"
        
        # 数据验证
        valid, msg = self._validate_bidding_data(bidding_data, is_update=True)
        if not valid:
            return False, msg
        
        # 更新投标对象
        if 'tender_code' in bidding_data:
            bidding.tender_code = bidding_data['tender_code']
        if 'bidding_name' in bidding_data:
            bidding.bidding_name = bidding_data['bidding_name']
        if 'tenderer' in bidding_data:
            bidding.tenderer = bidding_data['tenderer']
        if 'planned_duration' in bidding_data:
            bidding.planned_duration = bidding_data['planned_duration']
        if 'bid_bond' in bidding_data:
            bidding.bid_bond = float(bidding_data['bid_bond'])
        if 'control_price' in bidding_data:
            bidding.control_price = float(bidding_data['control_price'])
        if 'status' in bidding_data:
            bidding.status = self.model.get_status_from_value(bidding_data['status'])
        if 'tender_doc_path' in bidding_data:
            bidding.tender_doc_path = bidding_data['tender_doc_path']
        if 'remark' in bidding_data:
            bidding.remark = bidding_data['remark']
        
        # 处理日期
        if 'bid_deadline' in bidding_data:
            bid_deadline = bidding_data['bid_deadline']
            if isinstance(bid_deadline, str) and bid_deadline:
                bidding.bid_deadline = datetime.strptime(bid_deadline, '%Y-%m-%d')
        
        bidding.updated_at = datetime.now()
        
        # 保存到数据库
        success, msg = self._update_bidding(bidding)
        
        if success:
            self._notify_observers('BIDDING_UPDATED', {'bidding_id': bidding_id})
        
        return success, msg
    
    def delete_bidding(self, bidding_id: int) -> tuple:
        """
        删除投标
        :param bidding_id: 投标ID
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            self.db_manager.execute_update(
                "DELETE FROM biddings WHERE id = %s",
                (bidding_id,)
            )
            self._notify_observers('BIDDING_DELETED', {'bidding_id': bidding_id})
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"

    def get_bidding(self, bidding_id: int) -> Optional[Bidding]:
        """
        获取单个投标
        :param bidding_id: 投标ID
        :return: 投标对象或None
        """
        if not self.db_manager:
            return None
        
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM biddings WHERE id = %s",
                (bidding_id,)
            )
            if result:
                return Bidding.from_dict(result[0])
            return None
        except Exception as e:
            print(f"获取投标失败: {e}")
            return None
    
    def get_bidding_by_code(self, bidding_code: str) -> Optional[Bidding]:
        """
        根据编码获取投标
        :param bidding_code: 投标编码
        :return: 投标对象或None
        """
        if not self.db_manager:
            return None
        
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM biddings WHERE bidding_code = %s",
                (bidding_code,)
            )
            if result:
                return Bidding.from_dict(result[0])
            return None
        except Exception as e:
            print(f"获取投标失败: {e}")
            return None
    
    def get_biddings(self, status: str = None, keyword: str = None,
                     limit: int = 100, offset: int = 0) -> List[Bidding]:
        """
        获取投标列表
        :param status: 状态筛选
        :param keyword: 关键词搜索
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 投标列表
        """
        if not self.db_manager:
            return []
        
        try:
            sql = "SELECT * FROM biddings WHERE 1=1"
            params = []
            
            if status:
                sql += " AND status = %s"
                params.append(status)
            
            if keyword:
                sql += " AND (bidding_code LIKE %s OR bidding_name LIKE %s OR tenderer LIKE %s)"
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            
            sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            result = self.db_manager.execute_query(sql, tuple(params))
            return [Bidding.from_dict(row) for row in result]
        except Exception as e:
            print(f"获取投标列表失败: {e}")
            return []
    
    def get_bidding_count(self, status: str = None, keyword: str = None) -> int:
        """
        获取投标数量
        :param status: 状态筛选
        :param keyword: 关键词搜索
        :return: 投标数量
        """
        if not self.db_manager:
            return 0
        
        try:
            sql = "SELECT COUNT(*) as count FROM biddings WHERE 1=1"
            params = []
            
            if status:
                sql += " AND status = %s"
                params.append(status)
            
            if keyword:
                sql += " AND (bidding_code LIKE %s OR bidding_name LIKE %s OR tenderer LIKE %s)"
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            
            result = self.db_manager.execute_query(sql, tuple(params))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取投标数量失败: {e}")
            return 0
    
    # ==================== 统计查询 ====================
    
    def get_status_counts(self) -> Dict[str, int]:
        """
        获取各状态的投标数量
        :return: 数量字典
        """
        return {
            'all': self.get_bidding_count(),
            'in_progress': self.get_bidding_count(status='进行中'),
            'won': self.get_bidding_count(status='已中标'),
            'lost': self.get_bidding_count(status='未中标'),
            'withdrawn': self.get_bidding_count(status='已撤回'),
        }
    
    # ==================== 数据验证 ====================
    
    def _validate_bidding_data(self, data: Dict[str, Any], is_update: bool = False) -> tuple:
        """
        验证投标数据
        :param data: 投标数据字典
        :param is_update: 是否为更新操作
        :return: (是否有效, 错误信息)
        """
        # 项目编码验证
        project_code = data.get('project_code', '').strip()
        if not is_update or project_code:
            if not project_code:
                return False, "项目编码不能为空"
        
        # 投标编码验证
        bidding_code = data.get('bidding_code', '').strip()
        if bidding_code and len(bidding_code) > 100:
            return False, "投标编码不能超过100个字符"
        
        # 金额验证
        for field_name in ['bid_bond', 'control_price']:
            amount = data.get(field_name, 0)
            if amount:
                try:
                    amount_val = float(amount)
                    if amount_val < 0:
                        return False, f"{field_name}必须是非负数"
                except (ValueError, TypeError):
                    return False, f"{field_name}必须是有效数字"
        
        return True, "验证通过"
    
    # ==================== 数据库操作辅助方法 ====================
    
    def _save_bidding(self, bidding: Bidding) -> tuple:
        """保存投标到数据库"""
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            sql = """
            INSERT INTO biddings (
                bidding_code, project_id, project_code, tender_code, bidding_name,
                tenderer, planned_duration, bid_bond, bid_deadline, control_price,
                status, tender_doc_path, remark, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                bidding.bidding_code,
                bidding.project_id,
                bidding.project_code,
                bidding.tender_code,
                bidding.bidding_name,
                bidding.tenderer,
                bidding.planned_duration,
                bidding.bid_bond,
                bidding.bid_deadline,
                bidding.control_price,
                bidding.status.value if isinstance(bidding.status, BiddingStatus) else bidding.status,
                bidding.tender_doc_path,
                bidding.remark,
                bidding.created_at,
                bidding.updated_at,
            )
            
            result = self.db_manager.execute_update(sql, params)
            # 获取最后插入的ID
            query_result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
            bidding_id = query_result[0]['id'] if query_result else None
            return True, bidding_id
        except Exception as e:
            return False, f"保存投标失败: {e}"
    
    def _update_bidding(self, bidding: Bidding) -> tuple:
        """更新投标到数据库"""
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            sql = """
            UPDATE biddings SET
                tender_code = %s,
                bidding_name = %s,
                tenderer = %s,
                planned_duration = %s,
                bid_bond = %s,
                bid_deadline = %s,
                control_price = %s,
                status = %s,
                tender_doc_path = %s,
                remark = %s,
                updated_at = %s
            WHERE id = %s
            """
            params = (
                bidding.tender_code,
                bidding.bidding_name,
                bidding.tenderer,
                bidding.planned_duration,
                bidding.bid_bond,
                bidding.bid_deadline,
                bidding.control_price,
                bidding.status.value if isinstance(bidding.status, BiddingStatus) else bidding.status,
                bidding.tender_doc_path,
                bidding.remark,
                bidding.updated_at,
                bidding.id,
            )
            
            self.db_manager.execute_update(sql, params)
            return True, "更新成功"
        except Exception as e:
            return False, f"更新投标失败: {e}"
    
    # ==================== 辅助方法 ====================
    
    def get_status_list(self) -> List[str]:
        """获取状态列表"""
        return self.model.get_status_list()
    
    # ==================== 投标汇总表管理 ====================
    
    def init_summary_tables(self) -> bool:
        """
        初始化投标汇总表数据库表
        :return: 是否成功
        """
        if not self.db_manager:
            return False
        
        try:
            # 创建汇总表主表
            sql_summary = """
            CREATE TABLE IF NOT EXISTS bidding_summaries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bidding_id INT NOT NULL COMMENT '投标ID',
                version VARCHAR(20) DEFAULT 'V1.0' COMMENT '版本号',
                version_name VARCHAR(100) DEFAULT '初始版本' COMMENT '版本名称',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_by VARCHAR(100) COMMENT '创建人',
                remark TEXT COMMENT '备注',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否为当前生效版本',
                total_amount DECIMAL(15, 2) DEFAULT 0 COMMENT '汇总金额',
                FOREIGN KEY (bidding_id) REFERENCES biddings(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标汇总表'
            """
            self.db_manager.execute_update(sql_summary)
            
            # 创建汇总表明细表
            sql_items = """
            CREATE TABLE IF NOT EXISTS bidding_summary_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                summary_id INT NOT NULL COMMENT '汇总表ID',
                parent_id INT DEFAULT NULL COMMENT '父节点ID',
                item_type VARCHAR(20) DEFAULT 'item' COMMENT '项目类型: category/subcategory/item',
                sequence VARCHAR(50) COMMENT '序号',
                name VARCHAR(500) COMMENT '工程项目及费用名称',
                quote_price DECIMAL(15, 2) DEFAULT 0 COMMENT '报价',
                main_material_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：主材费',
                aux_material_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：辅材费',
                labor_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：人工费',
                machinery_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：机械费',
                other_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：其他费',
                management_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：管理费',
                tax_fee DECIMAL(15, 2) DEFAULT 0 COMMENT '其中：税金',
                sort_order INT DEFAULT 0 COMMENT '排序顺序',
                FOREIGN KEY (summary_id) REFERENCES bidding_summaries(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES bidding_summary_items(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标汇总表明细'
            """
            self.db_manager.execute_update(sql_items)
            return True
        except Exception as e:
            print(f"创建汇总表失败: {e}")
            return False
    
    def save_bidding_summary(self, bidding_id: int, items: List[Dict], 
                            version: str = "V1.0", version_name: str = "初始版本",
                            created_by: str = "", remark: str = "") -> tuple:
        """
        保存投标汇总表
        :param bidding_id: 投标ID
        :param items: 汇总表项目列表（树形结构扁平化后的数据）
        :param version: 版本号
        :param version_name: 版本名称
        :param created_by: 创建人
        :param remark: 备注
        :return: (是否成功, 汇总表ID或错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            # 计算总价
            total_amount = sum(item.get('quote_price', 0) for item in items)
            
            # 插入汇总表主记录
            sql_summary = """
            INSERT INTO bidding_summaries 
            (bidding_id, version, version_name, created_by, remark, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db_manager.execute_update(sql_summary, 
                (bidding_id, version, version_name, created_by, remark, total_amount))
            
            # 获取新插入的汇总表ID
            result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
            summary_id = result[0]['id'] if result else None
            
            if not summary_id:
                return False, "获取汇总表ID失败"
            
            # 保存明细项目（需要先保存父节点，再保存子节点）
            id_mapping = {}  # 用于映射临时ID到数据库ID
            
            print(f"[保存汇总表] 开始保存 {len(items)} 条数据")
            
            # 第一遍：保存所有项目，建立ID映射
            for idx, item in enumerate(items):
                parent_temp_id = item.get('parent_temp_id')
                parent_db_id = id_mapping.get(parent_temp_id) if parent_temp_id is not None else None
                
                print(f"[保存汇总表] 第{idx+1}条: temp_id={item.get('temp_id')}, parent_temp_id={parent_temp_id}, parent_db_id={parent_db_id}, name={item.get('name', '')[:20]}")
                
                sql_item = """
                INSERT INTO bidding_summary_items
                (summary_id, parent_id, item_type, sequence, name, quote_price,
                 main_material_fee, aux_material_fee, labor_fee, machinery_fee,
                 other_fee, management_fee, tax_fee, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    summary_id,
                    parent_db_id,
                    item.get('item_type', 'item'),
                    item.get('sequence', ''),
                    item.get('name', ''),
                    item.get('quote_price', 0),
                    item.get('main_material_fee', 0),
                    item.get('aux_material_fee', 0),
                    item.get('labor_fee', 0),
                    item.get('machinery_fee', 0),
                    item.get('other_fee', 0),
                    item.get('management_fee', 0),
                    item.get('tax_fee', 0),
                    idx
                )
                self.db_manager.execute_update(sql_item, params)
                
                # 获取新插入的项目ID
                result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                db_id = result[0]['id'] if result else None
                
                # 保存临时ID到数据库ID的映射
                temp_id = item.get('temp_id')
                if temp_id is not None:
                    id_mapping[temp_id] = db_id
                    print(f"[保存汇总表]   -> 建立映射: temp_id={temp_id} -> db_id={db_id}")
            
            print(f"[保存汇总表] 保存完成，summary_id={summary_id}")
            self._notify_observers('SUMMARY_SAVED', {'bidding_id': bidding_id, 'summary_id': summary_id})
            return True, summary_id
            
        except Exception as e:
            print(f"[保存汇总表] 错误: {e}")
            return False, f"保存汇总表失败: {e}"
    
    def update_bidding_summary(self, summary_id: int, items: List[Dict]) -> tuple:
        """
        更新现有版本的投标汇总表
        :param summary_id: 汇总表ID
        :param items: 汇总表项目列表
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            # 计算总价
            total_amount = sum(item.get('quote_price', 0) for item in items)
            
            # 更新汇总表主记录
            sql_summary = """
            UPDATE bidding_summaries 
            SET total_amount = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            self.db_manager.execute_update(sql_summary, (total_amount, summary_id))
            
            # 删除旧的明细项目
            self.db_manager.execute_update(
                "DELETE FROM bidding_summary_items WHERE summary_id = %s",
                (summary_id,)
            )
            
            # 保存新的明细项目
            id_mapping = {}
            
            print(f"[更新汇总表] 开始保存 {len(items)} 条数据")
            
            for idx, item in enumerate(items):
                parent_temp_id = item.get('parent_temp_id')
                parent_db_id = id_mapping.get(parent_temp_id) if parent_temp_id is not None else None
                
                print(f"[更新汇总表] 第{idx+1}条: temp_id={item.get('temp_id')}, parent_temp_id={parent_temp_id}, parent_db_id={parent_db_id}, name={item.get('name', '')[:20]}")
                
                sql_item = """
                INSERT INTO bidding_summary_items
                (summary_id, parent_id, item_type, sequence, name, quote_price,
                 main_material_fee, aux_material_fee, labor_fee, machinery_fee,
                 other_fee, management_fee, tax_fee, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    summary_id,
                    parent_db_id,
                    item.get('item_type', 'item'),
                    item.get('sequence', ''),
                    item.get('name', ''),
                    item.get('quote_price', 0),
                    item.get('main_material_fee', 0),
                    item.get('aux_material_fee', 0),
                    item.get('labor_fee', 0),
                    item.get('machinery_fee', 0),
                    item.get('other_fee', 0),
                    item.get('management_fee', 0),
                    item.get('tax_fee', 0),
                    idx
                )
                self.db_manager.execute_update(sql_item, params)
                
                # 获取新插入的项目ID
                result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                db_id = result[0]['id'] if result else None
                
                # 保存临时ID到数据库ID的映射
                temp_id = item.get('temp_id')
                if temp_id is not None:
                    id_mapping[temp_id] = db_id
                    print(f"[更新汇总表]   -> 建立映射: temp_id={temp_id} -> db_id={db_id}")
            
            print(f"[更新汇总表] 保存完成")
            self._notify_observers('SUMMARY_UPDATED', {'summary_id': summary_id})
            return True, "更新成功"
            
        except Exception as e:
            print(f"[更新汇总表] 错误: {e}")
            return False, f"更新汇总表失败: {e}"
    
    def get_bidding_summary(self, bidding_id: int, version: str = None) -> List[Dict]:
        """
        获取投标汇总表
        :param bidding_id: 投标ID
        :param version: 版本号，None表示获取最新版本
        :return: 汇总表项目列表
        """
        if not self.db_manager:
            return []
        
        try:
            # 获取汇总表ID
            if version:
                sql = "SELECT id FROM bidding_summaries WHERE bidding_id = %s AND version = %s AND is_active = TRUE"
                result = self.db_manager.execute_query(sql, (bidding_id, version))
            else:
                sql = "SELECT id FROM bidding_summaries WHERE bidding_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1"
                result = self.db_manager.execute_query(sql, (bidding_id,))
            
            if not result:
                return []
            
            summary_id = result[0]['id']
            return self.get_bidding_summary_by_id(summary_id)
            
        except Exception as e:
            print(f"获取汇总表失败: {e}")
            return []
    
    def get_bidding_summary_by_id(self, summary_id: int) -> List[Dict]:
        """
        根据汇总表ID获取明细数据
        :param summary_id: 汇总表ID
        :return: 汇总表项目列表
        """
        if not self.db_manager:
            return []
        
        try:
            # 获取明细项目
            sql_items = """
            SELECT * FROM bidding_summary_items 
            WHERE summary_id = %s 
            ORDER BY sort_order
            """
            items = self.db_manager.execute_query(sql_items, (summary_id,))
            
            return items if items else []
            
        except Exception as e:
            print(f"获取汇总表明细失败: {e}")
            return []
    
    def get_summary_versions(self, bidding_id: int) -> List[Dict]:
        """
        获取投标汇总表的所有版本
        :param bidding_id: 投标ID
        :return: 版本列表
        """
        if not self.db_manager:
            return []
        
        try:
            sql = """
            SELECT id, version, version_name, created_at, updated_at, 
                   created_by, remark, is_active, total_amount
            FROM bidding_summaries 
            WHERE bidding_id = %s 
            ORDER BY created_at DESC
            """
            return self.db_manager.execute_query(sql, (bidding_id,))
        except Exception as e:
            print(f"获取汇总表版本失败: {e}")
            return []
    
    def delete_summary_version(self, summary_id: int) -> tuple:
        """
        删除汇总表版本
        :param summary_id: 汇总表ID
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            self.db_manager.execute_update(
                "DELETE FROM bidding_summaries WHERE id = %s",
                (summary_id,)
            )
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"
    
    # ==================== 投标明细管理 ====================
    
    def init_detail_tables(self) -> bool:
        """
        初始化投标明细数据库表
        :return: 是否成功
        """
        if not self.db_manager:
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
            self.db_manager.execute_update(sql_detail)
            
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
                remark VARCHAR(500) COMMENT '备注',
                sort_order INT DEFAULT 0 COMMENT '排序顺序',
                FOREIGN KEY (detail_id) REFERENCES bidding_details(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES bidding_detail_items(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标明细项目表'
            """
            self.db_manager.execute_update(sql_items)
            return True
        except Exception as e:
            print(f"创建明细表失败: {e}")
            return False
    
    def save_bidding_detail(self, bidding_id: int, summary_item_id: int, items: List[Dict],
                           version: str = "V1.0", created_by: str = "", remark: str = "") -> tuple:
        """
        保存投标明细
        :param bidding_id: 投标ID
        :param summary_item_id: 关联的汇总项ID
        :param items: 明细项目列表
        :param version: 版本号
        :param created_by: 创建人
        :param remark: 备注
        :return: (是否成功, 明细表ID或错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            # 插入明细表主记录
            sql_detail = """
            INSERT INTO bidding_details 
            (bidding_id, summary_item_id, version, created_by, remark)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.db_manager.execute_update(sql_detail, 
                (bidding_id, summary_item_id, version, created_by, remark))
            
            # 获取新插入的明细表ID
            result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
            detail_id = result[0]['id'] if result else None
            
            if not detail_id:
                return False, "获取明细表ID失败"
            
            # 保存明细项目
            id_mapping = {}
            
            for idx, item in enumerate(items):
                parent_temp_id = item.get('parent_temp_id')
                parent_db_id = id_mapping.get(parent_temp_id) if parent_temp_id else None
                
                sql_item = """
                INSERT INTO bidding_detail_items
                (detail_id, parent_id, sequence, name, description, unit, quantity,
                 unit_price, total_price, remark, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    detail_id,
                    parent_db_id,
                    item.get('sequence', ''),
                    item.get('name', ''),
                    item.get('description', ''),
                    item.get('unit', ''),
                    item.get('quantity', 0),
                    item.get('unit_price', 0),
                    item.get('total_price', 0),
                    item.get('remark', ''),
                    idx
                )
                self.db_manager.execute_update(sql_item, params)
                
                # 获取新插入的项目ID
                result = self.db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                db_id = result[0]['id'] if result else None
                
                temp_id = item.get('temp_id')
                if temp_id:
                    id_mapping[temp_id] = db_id
            
            self._notify_observers('DETAIL_SAVED', {'bidding_id': bidding_id, 'detail_id': detail_id})
            return True, detail_id
            
        except Exception as e:
            return False, f"保存明细失败: {e}"
    
    def get_bidding_detail(self, bidding_id: int, summary_item_id: int = None) -> List[Dict]:
        """
        获取投标明细
        :param bidding_id: 投标ID
        :param summary_item_id: 汇总项ID，None表示获取所有明细
        :return: 明细项目列表
        """
        if not self.db_manager:
            return []
        
        try:
            # 获取明细表ID
            if summary_item_id:
                sql = """
                SELECT id FROM bidding_details 
                WHERE bidding_id = %s AND summary_item_id = %s 
                ORDER BY created_at DESC LIMIT 1
                """
                result = self.db_manager.execute_query(sql, (bidding_id, summary_item_id))
            else:
                sql = """
                SELECT id FROM bidding_details 
                WHERE bidding_id = %s 
                ORDER BY created_at DESC LIMIT 1
                """
                result = self.db_manager.execute_query(sql, (bidding_id,))
            
            if not result:
                return []
            
            detail_id = result[0]['id']
            
            # 获取明细项目
            sql_items = """
            SELECT * FROM bidding_detail_items 
            WHERE detail_id = %s 
            ORDER BY sort_order
            """
            return self.db_manager.execute_query(sql_items, (detail_id,))
            
        except Exception as e:
            print(f"获取明细失败: {e}")
            return []
    
    def delete_bidding_detail(self, detail_id: int) -> tuple:
        """
        删除投标明细
        :param detail_id: 明细表ID
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未连接"
        
        try:
            self.db_manager.execute_update(
                "DELETE FROM bidding_details WHERE id = %s",
                (detail_id,)
            )
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"
