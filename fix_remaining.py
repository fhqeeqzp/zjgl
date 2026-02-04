"""
修复剩余的 QMessageBox 引用
"""
import re
import os

# 需要处理的文件列表
files_to_process = [
    'XMGL/ui/project_dialog.py',
    'login/ui/dialogs.py',
    'login/ui/login_window.py',
    'TBGL/ui/bidding_summary_tab.py',
    'TBGL/ui/excel_import_dialog.py',
    'TBGL/ui/bidding_dialog.py',
    'TBGL/ui/detail_import_dialog.py',
    'TBGL/ui/bidding_detail_tab.py',
]

def process_file(file_path):
    """处理单个文件"""
    full_path = os.path.join('e:\\编程目录\\工程造价管理\\main', file_path)

    if not os.path.exists(full_path):
        print(f"跳过: {file_path} (文件不存在)")
        return

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 替换 QMessageBox 静态方法调用
    content = re.sub(
        r'QMessageBox\.information\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.information(\1, "\2", "\3")',
        content
    )

    content = re.sub(
        r'QMessageBox\.warning\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.warning(\1, "\2", "\3")',
        content
    )

    content = re.sub(
        r'QMessageBox\.critical\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)',
        r'MessageDialog.critical(\1, "\2", "\3")',
        content
    )

    content = re.sub(
        r'QMessageBox\.question\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"',
        r'MessageDialog.question(\1, "\2", "\3"',
        content
    )

    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新: {file_path}")
    else:
        print(f"⚠️  无变化: {file_path}")


if __name__ == "__main__":
    print("开始修复剩余的 QMessageBox...\n")

    for file_path in files_to_process:
        process_file(file_path)

    print("\n✅ 修复完成！")
