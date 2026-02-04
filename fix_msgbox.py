import re

# 读取文件
with open('TBGL/ui/bidding_summary_tab.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 QMessageBox.warning(self, ...)
content = re.sub(
    r'QMessageBox\.warning\(self,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'self.show_message_box(QMessageBox.Warning, "\1", "\2")',
    content
)

# 替换 QMessageBox.information(self, ...)
content = re.sub(
    r'QMessageBox\.information\(self,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'self.show_message_box(QMessageBox.Information, "\1", "\2")',
    content
)

# 替换 QMessageBox.critical(self, ...)
content = re.sub(
    r'QMessageBox\.critical\(self,\s*"([^"]+)",\s*"([^"]+)"\)',
    r'self.show_message_box(QMessageBox.Critical, "\1", "\2")',
    content
)

# 替换 QMessageBox.question(self, ...) - 处理多行情况
content = re.sub(
    r'QMessageBox\.question\(\s*self,\s*"([^"]+)",\s*"([^"]+)"',
    r'self.show_message_box(QMessageBox.Question, "\1", "\2"',
    content
)

# 写入文件
with open('TBGL/ui/bidding_summary_tab.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('替换完成！')
