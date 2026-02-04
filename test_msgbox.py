"""
测试自定义消息对话框
"""
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

# 导入自定义对话框
from ui.message_dialog import MessageDialog


class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义消息对话框测试")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 测试按钮
        btn_info = QPushButton("测试 Information 对话框 (600x400)")
        btn_info.clicked.connect(self.test_info)
        layout.addWidget(btn_info)
        
        btn_warning = QPushButton("测试 Warning 对话框 (600x400)")
        btn_warning.clicked.connect(self.test_warning)
        layout.addWidget(btn_warning)
        
        btn_critical = QPushButton("测试 Critical 对话框 (600x400)")
        btn_critical.clicked.connect(self.test_critical)
        layout.addWidget(btn_critical)
        
        btn_question = QPushButton("测试 Question 对话框 (600x400)")
        btn_question.clicked.connect(self.test_question)
        layout.addWidget(btn_question)
        
        btn_long_text = QPushButton("测试长文本对话框 (600x400)")
        btn_long_text.clicked.connect(self.test_long_text)
        layout.addWidget(btn_long_text)
    
    def test_info(self):
        result = MessageDialog.information(
            self, 
            "成功", 
            "操作成功完成！",
            min_width=600,
            min_height=400
        )
        print(f"Information 返回: {result}")
    
    def test_warning(self):
        result = MessageDialog.warning(
            self, 
            "提示", 
            "请先选择投标",
            min_width=600,
            min_height=400
        )
        print(f"Warning 返回: {result}")
    
    def test_critical(self):
        result = MessageDialog.critical(
            self, 
            "错误", 
            "创建版本失败:\n详细错误信息...",
            min_width=600,
            min_height=400
        )
        print(f"Critical 返回: {result}")
    
    def test_question(self):
        result = MessageDialog.question(
            self, 
            "确认", 
            "确定要删除这个版本吗？\n删除后将无法恢复！",
            buttons=MessageDialog.Yes | MessageDialog.No,
            default_button=MessageDialog.No,
            min_width=600,
            min_height=400
        )
        print(f"Question 返回: {'是' if result == MessageDialog.Yes else '否'}")
    
    def test_long_text(self):
        long_text = "这是一段很长的文本内容，用于测试对话框的尺寸设置是否正确。" * 10
        result = MessageDialog.information(
            self, 
            "长文本测试", 
            long_text,
            min_width=600,
            min_height=400
        )
        print(f"Long text 返回: {result}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 加载深色主题样式
    try:
        with open('themes/message_dialog_dark.qss', 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"加载样式失败: {e}")
    
    window = TestWidget()
    window.show()
    sys.exit(app.exec())
