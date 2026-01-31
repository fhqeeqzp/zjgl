"""
数据库管理模块
负责数据库连接、创建、表结构管理等
"""
import pymysql
from pymysql.cursors import DictCursor


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, config):
        self.config = config
        self.connection = None

    def test_connection(self):
        """测试数据库连接"""
        try:
            conn = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                charset='utf8mb4',
                cursorclass=DictCursor,
                connect_timeout=5
            )
            conn.close()
            return True, "连接成功"
        except pymysql.Error as e:
            return False, f"连接失败: {str(e)}"

    def create_or_update_database(self):
        """
        创建或更新数据库
        - 如果数据库不存在，创建新数据库
        - 如果数据库存在，保留数据，只更新表结构
        """
        try:
            # 连接到MySQL服务器（不指定数据库）
            conn = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            cursor = conn.cursor()
            
            db_name = self.config.get('database', 'myapp')
            
            # 检查数据库是否存在
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            exists = cursor.fetchone()
            
            if exists:
                # 数据库已存在，使用现有数据库
                cursor.execute(f"USE {db_name}")
                print(f"数据库 '{db_name}' 已存在，使用现有数据库")
            else:
                # 创建新数据库
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.execute(f"USE {db_name}")
                print(f"数据库 '{db_name}' 创建成功")
            
            # 创建/更新数据表
            self._create_tables(cursor)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"数据库 '{db_name}' 初始化完成"
            
        except pymysql.Error as e:
            return False, f"数据库操作失败: {str(e)}"

    def _create_tables(self, cursor):
        """
        创建所有数据表
        如果表已存在，会跳过创建（保留现有数据）
        """
        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                status TINYINT DEFAULT 1 COMMENT '1:启用 0:禁用',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login_at TIMESTAMP NULL,
                INDEX idx_username (username),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表'
        """)
        
        # 用户配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                setting_key VARCHAR(50) NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_setting (user_id, setting_key),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户配置表'
        """)
        
        # 登录日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(50),
                ip_address VARCHAR(45),
                login_status TINYINT COMMENT '1:成功 0:失败',
                fail_reason VARCHAR(255),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表'
        """)
        
        # 系统配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                config_key VARCHAR(50) NOT NULL UNIQUE,
                config_value TEXT,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_config_key (config_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表'
        """)
        
        # 初始化默认管理员账号
        self._init_default_data(cursor)
        
        print("所有数据表初始化完成")

    def _init_default_data(self, cursor):
        """初始化默认数据"""
        import hashlib
        
        # 检查是否已有管理员账号
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result['count'] == 0:
            # 创建默认管理员账号
            password_hash = hashlib.sha256('123456'.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, status)
                VALUES ('admin', %s, 'admin@example.com', 1)
            """, (password_hash,))
            print("默认管理员账号创建成功 (admin/123456)")
        
        # 初始化系统配置
        default_configs = [
            ('app_name', '工程造价管理系统', '应用名称'),
            ('app_version', '1.0.0', '应用版本'),
            ('theme_default', 'dark', '默认主题'),
        ]
        
        for key, value, desc in default_configs:
            cursor.execute("""
                INSERT IGNORE INTO system_config (config_key, config_value, description)
                VALUES (%s, %s, %s)
            """, (key, value, desc))

    def get_connection(self):
        """获取数据库连接"""
        if not self.connection or not self.connection.open:
            self.connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                database=self.config.get('database', 'myapp'),
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
        return self.connection

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()

    def execute_query(self, sql, params=None):
        """执行查询语句"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()

    def execute_update(self, sql, params=None):
        """执行更新语句"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
