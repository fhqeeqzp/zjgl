"""
修复 f-string 中的 QMessageBox 引用
"""
import re
import os

# 需要处理的文件列表
files_to_process = [
    'XMGL/ui/project_dialog.py',
    'login/ui/dialogs.py',
    'TBGL/ui/bidding_summary_tab.py',
    'TBGL/ui/excel_import_dialog.py',
    'TBGL/ui/bidding_dialog.py',
    'TBGL/ui/detail_import_dialog.py',
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

    # 替换 f-string 中的 QMessageBox 调用
    # QMessageBox.information(self, "...", f"...") -> MessageDialog.information(self, "...", f"...")
    content = re.sub(
        r'QMessageBox\.information\(([^,]+),\s*"([^"]+)",\s*f"([^"]+)"\)',
        r'MessageDialog.information(\1, "\2", f"\3")',
        content
    )

    content = re.sub(
        r'QMessageBox\.warning\(([^,]+),\s*"([^"]+)",\s*f"([^"]+)"\)',
        r'MessageDialog.warning(\1, "\2", f"\3")',
        content
    )

    content = re.sub(
        r'QMessageBox\.critical\(([^,]+),\s*"([^"]+)",\s*f"([^"]+)"\)',
        r'MessageDialog.critical(\1, "\2", f"\3")',
        content
    )

    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新: {file_path}")
    else:
        print(f"⚠️  无变化: {file_path}")


if __name__ == "__main__":
    print("开始修复 f-string QMessageBox...\n")

    for file_path in files_to_process:
        process_file(file_path)

    print("\n✅ 修复完成！")
