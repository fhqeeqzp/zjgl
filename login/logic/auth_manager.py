"""
认证管理器
处理登录、注册等认证逻辑
"""
import hashlib
import re


class AuthManager:
    """认证管理类"""

    def __init__(self, db_config=None):
        self.db_config = db_config
        self.current_user = None
        self.db_manager = None
        
        # 如果提供了配置，初始化数据库管理器
        if db_config:
            from ..data.db_manager import DatabaseManager
            self.db_manager = DatabaseManager(db_config)

    def validate_username(self, username):
        """验证用户名"""
        if not username:
            return False, "用户名不能为空"
        if len(username) < 3:
            return False, "用户名至少需要3个字符"
        if len(username) > 20:
            return False, "用户名不能超过20个字符"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "用户名只能包含字母、数字和下划线"
        return True, "验证通过"

    def validate_password(self, password):
        """验证密码"""
        if not password:
            return False, "密码不能为空"
        if len(password) < 6:
            return False, "密码至少需要6个字符"
        if len(password) > 32:
            return False, "密码不能超过32个字符"
        return True, "验证通过"

    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password, remember=False):
        """
        用户登录
        返回: (success: bool, message: str)
        """
        # 验证用户名
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg

        # 验证密码
        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg

        # 使用数据库验证
        if self.db_manager:
            try:
                hashed_pwd = self.hash_password(password)
                result = self.db_manager.execute_query(
                    "SELECT * FROM users WHERE username = %s AND password_hash = %s AND status = 1",
                    (username, hashed_pwd)
                )
                
                if result and len(result) > 0:
                    self.current_user = username
                    # 更新最后登录时间
                    self.db_manager.execute_update(
                        "UPDATE users SET last_login_at = NOW() WHERE username = %s",
                        (username,)
                    )
                    # 记录登录日志
                    self.db_manager.execute_update(
                        "INSERT INTO login_logs (user_id, username, login_status) VALUES (%s, %s, 1)",
                        (result[0]['id'], username)
                    )
                    return True, "登录成功"
                else:
                    # 记录失败日志
                    self.db_manager.execute_update(
                        "INSERT INTO login_logs (username, login_status, fail_reason) VALUES (%s, 0, %s)",
                        (username, "用户名或密码错误")
                    )
                    return False, "用户名或密码错误"
            except Exception as e:
                return False, f"数据库错误: {str(e)}"
        else:
            # 没有数据库配置时使用模拟数据
            if username == "admin" and password == "123456":
                self.current_user = username
                return True, "登录成功"
            return False, "用户名或密码错误"

    def register(self, username, password, confirm_password):
        """
        用户注册
        返回: (success: bool, message: str)
        """
        # 验证用户名
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg

        # 验证密码
        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg

        # 确认密码
        if password != confirm_password:
            return False, "两次输入的密码不一致"

        # 使用数据库保存用户
        if self.db_manager:
            try:
                # 检查用户名是否已存在
                result = self.db_manager.execute_query(
                    "SELECT COUNT(*) as count FROM users WHERE username = %s",
                    (username,)
                )
                if result[0]['count'] > 0:
                    return False, "用户名已存在"
                
                # 插入新用户
                hashed_pwd = self.hash_password(password)
                self.db_manager.execute_update(
                    "INSERT INTO users (username, password_hash, status) VALUES (%s, %s, 1)",
                    (username, hashed_pwd)
                )
                return True, "注册成功"
            except Exception as e:
                return False, f"数据库错误: {str(e)}"
        else:
            # 没有数据库配置时使用模拟验证
            if username == "admin":
                return False, "用户名已存在"
            return True, "注册成功"

    def logout(self):
        """退出登录"""
        self.current_user = None
        return True

    def is_logged_in(self):
        """检查是否已登录"""
        return self.current_user is not None

    def get_current_user(self):
        """获取当前用户"""
        return self.current_user
