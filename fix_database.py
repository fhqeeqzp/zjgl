"""
数据库修复脚本 - 添加缺失的 specification 字段
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from login.data.db_config import DatabaseConfig
from login.data.db_manager import DatabaseManager

def fix_database():
    """修复数据库 - 添加缺失的字段"""
    try:
        # 加载数据库配置
        db_config = DatabaseConfig()
        config = db_config.get_config()
        db = DatabaseManager(config)
        
        # 检查 bidding_detail_items 表是否有 specification 字段
        check_sql = """
        SELECT COUNT(*) as count 
        FROM information_schema.columns 
        WHERE table_name = 'bidding_detail_items' 
        AND column_name = 'specification'
        AND table_schema = DATABASE()
        """
        result = db.execute_query(check_sql)
        
        if result and result[0]['count'] == 0:
            # 添加 specification 字段
            alter_sql = """
            ALTER TABLE bidding_detail_items 
            ADD COLUMN specification VARCHAR(500) COMMENT '规格型号' AFTER name
            """
            db.execute_update(alter_sql)
            print("✓ 成功添加字段: bidding_detail_items.specification")
        else:
            print("✓ 字段已存在: bidding_detail_items.specification")
            
        print("\n数据库修复完成！")
        
    except Exception as e:
        print(f"✗ 数据库修复失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_database()
