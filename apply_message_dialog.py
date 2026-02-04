"""
批量替换所有 QMessageBox 为 MessageDialog
"""
import re
import os

# 需要处理的文件列表
files_to_process = [
    'TBGL/ui/bidding_detail_tab.py',
    'TBGL/ui/detail_import_dialog.py',
    'TBGL/ui/summary_edit_dialog.py',
    'TBGL/ui/bidding_dialog.py',
    'TBGL/ui/excel_import_dialog.py',
    'TBGL/ui/bidding_summary_tab.py',
    'TBGL/ui/bidding_report_tab.py',
    'login/ui/login_window.py',
    'XMGL/ui/projects_page.py',
    'main.py',
    'login/ui/dialogs.py',
    'XMGL/ui/project_dialog.py',
    'TBGL/ui/bidding_page.py',
]

def process_file(file_path):
    """处理单个文件"""
    full_path = os.path.join('e:\\编程目录\\工程造价管理\\main', file_path)

    if not os.path.exists(full_path):
        print(f"跳过: {file_path} (文件不存在)")
        return

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否包含 QMessageBox
    if 'QMessageBox' not in content:
        print(f"跳过: {file_path} (无 QMessageBox)")
        return

    original_content = content

    # 1. 替换导入语句
    # 从: from PySide6.QtWidgets import ..., QMessageBox, ...
    # 改为: from PySide6.QtWidgets import ...
    #       from ui.message_dialog import MessageDialog
    content = re.sub(
        r'from PySide6\.QtWidgets import \(([^)]+)\)',
        lambda m: process_import(m.group(1)),
        content
    )

    # 单行导入
    content = re.sub(
        r'from PySide6\.QtWidgets import ([^,]+, )*QMessageBox(,[ \w]+)?',
        lambda m: process_single_import(m.group(0)),
        content
    )

    # 2. 替换 QMessageBox 静态方法调用
    # QMessageBox.information(parent, title, text) -> MessageDialog.information(parent, title, text)
    content = re.sub(
        r'QMessageBox\.information\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.information(\1, "\2", "\3")',
        content
    )

    # QMessageBox.warning(parent, title, text) -> MessageDialog.warning(parent, title, text)
    content = re.sub(
        r'QMessageBox\.warning\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.warning(\1, "\2", "\3")',
        content
    )

    # QMessageBox.critical(parent, title, text) -> MessageDialog.critical(parent, title, text)
    content = re.sub(
        r'QMessageBox\.critical\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.critical(\1, "\2", "\3")',
        content
    )

    # QMessageBox.question(parent, title, text, ...) -> MessageDialog.question(parent, title, text, ...)
    content = re.sub(
        r'QMessageBox\.question\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"',
        r'MessageDialog.question(\1, "\2", "\3"',
        content
    )

    # 3. 替换 QMessageBox.Yes/No/Ok/Cancel 为 MessageDialog.Yes/No/Ok/Cancel
    content = content.replace('QMessageBox.Yes', 'MessageDialog.Yes')
    content = content.replace('QMessageBox.No', 'MessageDialog.No')
    content = content.replace('QMessageBox.Ok', 'MessageDialog.Ok')
    content = content.replace('QMessageBox.Cancel', 'MessageDialog.Cancel')

    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新: {file_path}")
    else:
        print(f"⚠️  无变化: {file_path}")


def process_import(import_list):
    """处理多行导入"""
    # 移除 QMessageBox
    items = [item.strip() for item in import_list.split(',')]
    items = [item for item in items if item and item != 'QMessageBox']

    result = 'from PySide6.QtWidgets import (\n    ' + ',\n    '.join(items) + '\n)'

    # 添加 MessageDialog 导入
    result += '\n\nfrom ui.message_dialog import MessageDialog'

    return result


def process_single_import(import_line):
    """处理单行导入"""
    # 移除 QMessageBox
    import_line = re.sub(r',?\s*QMessageBox\s*,?', ',', import_line)
    import_line = import_line.replace(',,', ',')
    import_line = import_line.rstrip(',').rstrip()

    # 添加 MessageDialog 导入
    result = import_line + '\nfrom ui.message_dialog import MessageDialog'

    return result


if __name__ == "__main__":
    print("开始批量替换 QMessageBox 为 MessageDialog...\n")

    for file_path in files_to_process:
        process_file(file_path)

    print("\n✅ 批量替换完成！")
