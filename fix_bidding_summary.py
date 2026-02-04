import re

# 读取文件
with open('TBGL/ui/bidding_summary_tab.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 self.show_message_box(QMessageBox.Warning, ...) 为 MessageDialog.warning(self, ...)
content = re.sub(
    r'self\.show_message_box\(QMessageBox\.Warning,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'MessageDialog.warning(self, "\1", "\2")',
    content
)

# 替换 self.show_message_box(QMessageBox.Information, ...) 为 MessageDialog.information(self, ...)
content = re.sub(
    r'self\.show_message_box\(QMessageBox\.Information,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'MessageDialog.information(self, "\1", "\2")',
    content
)

# 替换 self.show_message_box(QMessageBox.Critical, ...) 为 MessageDialog.critical(self, ...)
content = re.sub(
    r'self\.show_message_box\(QMessageBox\.Critical,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'MessageDialog.critical(self, "\1", "\2")',
    content
)

# 替换 question 对话框
content = re.sub(
    r'reply\s*=\s*self\.show_message_box\(QMessageBox\.Question,\s*"([^"]+)",\s*"([^"]+)",\s*([^)]+)\)',
    r'reply = MessageDialog.question(self, "\1", "\2", \3)',
    content
)

# 写入文件
with open('TBGL/ui/bidding_summary_tab.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('替换完成！')
