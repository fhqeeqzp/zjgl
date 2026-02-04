"""
项目数据库操作模块
负责项目数据的持久化存储
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from .project_model import Project, ProjectStatus, ProjectType


class ProjectDatabase:
    """项目数据库管理类"""
    
    def __init__(self, db_manager=None):
        """
        初始化项目数据库
        :param db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
    
    def create_tables(self) -> bool:
        """
        创建项目相关数据表
        :return: 是否创建成功
        """
        if not self.db_manager:
            return False
        
        try:
            # 先检查表是否存在
            result = self.db_manager.execute_query(
                "SHOW TABLES LIKE 'projects'"
            )
            
            if result and len(result) > 0:
                # 表已存在，检查是否需要更新字段
                self._update_table_columns()
            else:
                # 创建新表
                self._create_projects_table()
            
            # 创建日志表
            self._create_logs_table()
            
            return True
        except Exception as e:
            print(f"创建项目表失败: {e}")
            return False
    
    def _create_projects_table(self):
        """创建项目主表"""
        self.db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_code VARCHAR(50) NOT NULL UNIQUE COMMENT '项目编码',
                name VARCHAR(200) NOT NULL COMMENT '项目名称',
                project_type VARCHAR(50) DEFAULT '工业建筑' COMMENT '项目类型',
                status VARCHAR(20) DEFAULT '投标阶段' COMMENT '项目状态',
                bid_amount DECIMAL(15, 2) DEFAULT 0.00 COMMENT '投标金额',
                contract_amount DECIMAL(15, 2) DEFAULT 0.00 COMMENT '合同金额',
                received_amount DECIMAL(15, 2) DEFAULT 0.00 COMMENT '实收金额',
                paid_amount DECIMAL(15, 2) DEFAULT 0.00 COMMENT '实付金额',
                start_date DATE COMMENT '开始日期',
                completion_date DATE COMMENT '竣工日期',
                bid_attachment VARCHAR(500) COMMENT '投标附件路径',
                construction_attachment VARCHAR(500) COMMENT '施工附件路径',
                remark TEXT COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_project_code (project_code),
                INDEX idx_status (status),
                INDEX idx_project_type (project_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目主表'
        """)
    
    def _create_logs_table(self):
        """创建日志表"""
        self.db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS project_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL COMMENT '项目ID',
                action_type VARCHAR(50) NOT NULL COMMENT '操作类型',
                action_desc TEXT COMMENT '操作描述',
                old_value TEXT COMMENT '旧值',
                new_value TEXT COMMENT '新值',
                operator VARCHAR(100) COMMENT '操作人',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
                INDEX idx_project_id (project_id),
                INDEX idx_action_type (action_type),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目变更记录表'
        """)
    
    def _update_table_columns(self):
        """更新表字段（添加缺失的字段）"""
        try:
            # 获取现有字段
            result = self.db_manager.execute_query("SHOW COLUMNS FROM projects")
            existing_columns = {row['Field'] for row in result} if result else set()
            
            # 需要添加的字段
            columns_to_add = {
                'bid_amount': "DECIMAL(15, 2) DEFAULT 0.00 COMMENT '投标金额'",
                'contract_amount': "DECIMAL(15, 2) DEFAULT 0.00 COMMENT '合同金额'",
                'received_amount': "DECIMAL(15, 2) DEFAULT 0.00 COMMENT '实收金额'",
                'paid_amount': "DECIMAL(15, 2) DEFAULT 0.00 COMMENT '实付金额'",
                'bid_attachment': "VARCHAR(500) COMMENT '投标附件路径'",
                'construction_attachment': "VARCHAR(500) COMMENT '施工附件路径'",
                'completion_date': "DATE COMMENT '竣工日期'",
            }
            
            # 添加缺失的字段
            for column, definition in columns_to_add.items():
                if column not in existing_columns:
                    try:
                        self.db_manager.execute_update(
                            f"ALTER TABLE projects ADD COLUMN {column} {definition}"
                        )
                        print(f"添加字段 {column} 成功")
                    except Exception as e:
                        print(f"添加字段 {column} 失败: {e}")
            
            # 修改可能存在的旧字段
            if 'total_budget' in existing_columns:
                try:
                    self.db_manager.execute_update(
                        "ALTER TABLE projects DROP COLUMN total_budget"
                    )
                    print("删除旧字段 total_budget")
                except:
                    pass
            
            if 'actual_cost' in existing_columns:
                try:
                    self.db_manager.execute_update(
                        "ALTER TABLE projects DROP COLUMN actual_cost"
                    )
                    print("删除旧字段 actual_cost")
                except:
                    pass
                    
        except Exception as e:
            print(f"更新表字段失败: {e}")
    
    def add_project(self, project: Project) -> tuple:
        """
        添加新项目
        :param project: 项目对象
        :return: (是否成功, 项目ID或错误信息)
        """
        if not self.db_manager:
            return False, "数据库未配置"
        
        try:
            sql = """
                INSERT INTO projects (
                    project_code, name, project_type, status,
                    bid_amount, contract_amount, received_amount, paid_amount,
                    start_date, completion_date,
                    bid_attachment, construction_attachment, remark
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                project.project_code,
                project.name,
                project.project_type.value if isinstance(project.project_type, ProjectType) else project.project_type,
                project.status.value if isinstance(project.status, ProjectStatus) else project.status,
                project.bid_amount,
                project.contract_amount,
                project.received_amount,
                project.paid_amount,
                project.start_date,
                project.completion_date,
                project.bid_attachment,
                project.construction_attachment,
                project.remark,
            )
            
            project_id = self.db_manager.execute_update(sql, params)
            
            # 记录日志
            self._add_log(project_id, "CREATE", "创建项目", None, project.to_dict())
            
            return True, project_id
        except Exception as e:
            return False, str(e)
    
    def update_project(self, project: Project) -> tuple:
        """
        更新项目信息
        :param project: 项目对象
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未配置"
        
        if not project.id:
            return False, "项目ID不能为空"
        
        try:
            # 获取旧值用于记录日志
            old_project = self.get_project_by_id(project.id)
            
            sql = """
                UPDATE projects SET
                    project_code = %s,
                    name = %s,
                    project_type = %s,
                    status = %s,
                    bid_amount = %s,
                    contract_amount = %s,
                    received_amount = %s,
                    paid_amount = %s,
                    start_date = %s,
                    completion_date = %s,
                    bid_attachment = %s,
                    construction_attachment = %s,
                    remark = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            params = (
                project.project_code,
                project.name,
                project.project_type.value if isinstance(project.project_type, ProjectType) else project.project_type,
                project.status.value if isinstance(project.status, ProjectStatus) else project.status,
                project.bid_amount,
                project.contract_amount,
                project.received_amount,
                project.paid_amount,
                project.start_date,
                project.completion_date,
                project.bid_attachment,
                project.construction_attachment,
                project.remark,
                project.id,
            )
            
            self.db_manager.execute_update(sql, params)
            
            # 记录日志
            self._add_log(project.id, "UPDATE", "更新项目", 
                         old_project.to_dict() if old_project else None, 
                         project.to_dict())
            
            return True, "更新成功"
        except Exception as e:
            return False, str(e)
    
    def delete_project(self, project_id: int) -> tuple:
        """
        删除项目
        :param project_id: 项目ID
        :return: (是否成功, 错误信息)
        """
        if not self.db_manager:
            return False, "数据库未配置"
        
        try:
            self.db_manager.execute_update(
                "DELETE FROM projects WHERE id = %s",
                (project_id,)
            )
            self._add_log(project_id, "DELETE", "删除项目", None, None)
            
            return True, "删除成功"
        except Exception as e:
            return False, str(e)
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """
        根据ID获取项目
        :param project_id: 项目ID
        :return: 项目对象或None
        """
        if not self.db_manager:
            return None
        
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM projects WHERE id = %s",
                (project_id,)
            )
            
            if result and len(result) > 0:
                return Project.from_dict(result[0])
            return None
        except Exception as e:
            print(f"获取项目失败: {e}")
            return None
    
    def get_project_by_code(self, project_code: str) -> Optional[Project]:
        """
        根据编码获取项目
        :param project_code: 项目编码
        :return: 项目对象或None
        """
        if not self.db_manager:
            return None
        
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM projects WHERE project_code = %s",
                (project_code,)
            )
            
            if result and len(result) > 0:
                return Project.from_dict(result[0])
            return None
        except Exception as e:
            print(f"获取项目失败: {e}")
            return None
    
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
        if not self.db_manager:
            return []
        
        try:
            sql = "SELECT * FROM projects WHERE 1=1"
            params = []
            
            if status:
                sql += " AND status = %s"
                params.append(status)
            
            if project_type:
                sql += " AND project_type = %s"
                params.append(project_type)
            
            if keyword:
                sql += " AND (name LIKE %s OR project_code LIKE %s)"
                like_keyword = f"%{keyword}%"
                params.extend([like_keyword, like_keyword])
            
            sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            result = self.db_manager.execute_query(sql, params)
            
            return [Project.from_dict(row) for row in result] if result else []
        except Exception as e:
            print(f"获取项目列表失败: {e}")
            return []
    
    def get_project_count(self, status: str = None, project_type: str = None,
                          keyword: str = None) -> int:
        """
        获取项目数量
        :param status: 状态筛选
        :param project_type: 类型筛选
        :param keyword: 关键词搜索
        :return: 项目数量
        """
        if not self.db_manager:
            return 0
        
        try:
            sql = "SELECT COUNT(*) as count FROM projects WHERE 1=1"
            params = []
            
            if status:
                sql += " AND status = %s"
                params.append(status)
            
            if project_type:
                sql += " AND project_type = %s"
                params.append(project_type)
            
            if keyword:
                sql += " AND (name LIKE %s OR project_code LIKE %s)"
                like_keyword = f"%{keyword}%"
                params.extend([like_keyword, like_keyword])
            
            result = self.db_manager.execute_query(sql, params)
            
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取项目数量失败: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取项目统计数据
        :return: 统计数据字典
        """
        if not self.db_manager:
            return {}
        
        try:
            # 总项目数
            total = self.get_project_count()
            
            # 各状态数量
            status_counts = {}
            for status in ProjectStatus:
                count = self.get_project_count(status=status.value)
                status_counts[status.value] = count
            
            # 本月新增
            result = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM projects 
                WHERE YEAR(created_at) = YEAR(NOW()) AND MONTH(created_at) = MONTH(NOW())
            """)
            this_month = result[0]['count'] if result else 0
            
            # 金额统计
            result = self.db_manager.execute_query("""
                SELECT 
                    SUM(bid_amount) as total_bid,
                    SUM(contract_amount) as total_contract,
                    SUM(received_amount) as total_received,
                    SUM(paid_amount) as total_paid
                FROM projects
            """)
            amount_stats = result[0] if result else {}
            
            return {
                'total': total,
                'status_counts': status_counts,
                'this_month': this_month,
                'amount_stats': {
                    'total_bid': amount_stats.get('total_bid', 0) or 0,
                    'total_contract': amount_stats.get('total_contract', 0) or 0,
                    'total_received': amount_stats.get('total_received', 0) or 0,
                    'total_paid': amount_stats.get('total_paid', 0) or 0,
                }
            }
        except Exception as e:
            print(f"获取统计数据失败: {e}")
            return {}
    
    def _add_log(self, project_id: int, action_type: str, action_desc: str,
                 old_value: Any, new_value: Any):
        """
        添加操作日志
        :param project_id: 项目ID
        :param action_type: 操作类型
        :param action_desc: 操作描述
        :param old_value: 旧值
        :param new_value: 新值
        """
        if not self.db_manager:
            return
        
        try:
            import json
            from decimal import Decimal
            
            # 自定义JSON编码器，处理Decimal类型
            class DecimalEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, Decimal):
                        return float(obj)
                    return super().default(obj)
            
            sql = """
                INSERT INTO project_logs (project_id, action_type, action_desc, old_value, new_value)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                project_id,
                action_type,
                action_desc,
                json.dumps(old_value, ensure_ascii=False, cls=DecimalEncoder) if old_value else None,
                json.dumps(new_value, ensure_ascii=False, cls=DecimalEncoder) if new_value else None,
            )
            self.db_manager.execute_update(sql, params)
        except Exception as e:
            print(f"添加日志失败: {e}")
