"""
数据关联数据库操作
"""
from typing import List, Optional, Dict
from .link_model import DataLink, DataLinkCollection


class DataLinkDatabase:
    """数据关联数据库操作类"""

    def __init__(self, db_manager=None):
        self.db = db_manager

    def init_tables(self) -> bool:
        """初始化数据关联表"""
        if not self.db:
            return False

        try:
            # 先删除旧表（如果存在）
            drop_sql = "DROP TABLE IF EXISTS data_links"
            self.db.execute_update(drop_sql)
            print("[数据关联] 已删除旧的数据关联表")

            # 创建新表
            sql = """
            CREATE TABLE data_links (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bidding_id INT NOT NULL COMMENT '投标ID',
                summary_version VARCHAR(20) DEFAULT 'V1.0' COMMENT '汇总表版本',
                detail_version VARCHAR(20) DEFAULT 'V1.0' COMMENT '明细表版本',
                summary_item_id INT NOT NULL COMMENT '汇总表项目ID',
                detail_item_id INT NOT NULL COMMENT '明细表项目ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_by VARCHAR(100) DEFAULT '',
                remark VARCHAR(500) DEFAULT '',
                UNIQUE KEY uk_bidding_summary (bidding_id, summary_version, summary_item_id),
                INDEX idx_bidding_id (bidding_id),
                INDEX idx_summary_item_id (summary_item_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据关联表'
            """
            self.db.execute_update(sql)
            print("[数据关联] 已创建新的数据关联表")
            return True
        except Exception as e:
            print(f"初始化数据关联表失败: {e}")
            return False

    def save_links(self, bidding_id: int, links: Dict[int, int],
                   summary_version: str = 'V1.0', detail_version: str = 'V1.0') -> bool:
        """
        保存关联关系
        :param bidding_id: 投标ID
        :param links: 关联字典 {summary_item_id: detail_item_id}
        :param summary_version: 汇总表版本
        :param detail_version: 明细表版本
        :return: 是否成功
        """
        if not self.db:
            return False

        try:
            # 先删除该投标该版本的所有关联
            self.delete_links_by_version(bidding_id, summary_version)

            # 插入新的关联
            for summary_item_id, detail_item_id in links.items():
                sql = """
                INSERT INTO data_links (bidding_id, summary_version, detail_version,
                                       summary_item_id, detail_item_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.db.execute_update(sql, (bidding_id, summary_version, detail_version,
                                            summary_item_id, detail_item_id))

            return True
        except Exception as e:
            print(f"保存关联关系失败: {e}")
            return False

    def get_links_by_bidding(self, bidding_id: int,
                              summary_version: str = 'V1.0') -> Dict[int, int]:
        """
        获取指定投标的所有关联
        :param bidding_id: 投标ID
        :param summary_version: 汇总表版本
        :return: 关联字典 {summary_item_id: detail_item_id}
        """
        if not self.db:
            return {}

        try:
            sql = """
            SELECT summary_item_id, detail_item_id
            FROM data_links
            WHERE bidding_id = %s AND summary_version = %s
            """
            result = self.db.execute_query(sql, (bidding_id, summary_version))

            links = {}
            for row in result:
                links[row['summary_item_id']] = row['detail_item_id']

            return links
        except Exception as e:
            print(f"获取关联关系失败: {e}")
            return {}

    def delete_links_by_bidding(self, bidding_id: int) -> bool:
        """
        删除指定投标的所有关联
        :param bidding_id: 投标ID
        :return: 是否成功
        """
        if not self.db:
            return False

        try:
            sql = "DELETE FROM data_links WHERE bidding_id = %s"
            self.db.execute_update(sql, (bidding_id,))
            return True
        except Exception as e:
            print(f"删除关联关系失败: {e}")
            return False

    def delete_links_by_version(self, bidding_id: int, summary_version: str) -> bool:
        """
        删除指定投标指定版本的所有关联
        :param bidding_id: 投标ID
        :param summary_version: 汇总表版本
        :return: 是否成功
        """
        if not self.db:
            return False

        try:
            sql = "DELETE FROM data_links WHERE bidding_id = %s AND summary_version = %s"
            self.db.execute_update(sql, (bidding_id, summary_version))
            return True
        except Exception as e:
            print(f"删除关联关系失败: {e}")
            return False

    def delete_link(self, bidding_id: int, summary_item_id: int) -> bool:
        """
        删除指定关联
        :param bidding_id: 投标ID
        :param summary_item_id: 汇总表项目ID
        :return: 是否成功
        """
        if not self.db:
            return False

        try:
            sql = "DELETE FROM data_links WHERE bidding_id = %s AND summary_item_id = %s"
            self.db.execute_update(sql, (bidding_id, summary_item_id))
            return True
        except Exception as e:
            print(f"删除关联失败: {e}")
            return False
