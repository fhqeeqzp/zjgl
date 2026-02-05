#!/usr/bin/env python3
"""测试导入逻辑"""
import sys
sys.path.insert(0, '.')

import re
from typing import Dict

# 复制需要测试的方法
def _is_header_row(row: tuple, mapping: Dict[str, int]) -> bool:
    """智能检测是否为表头行或需要跳过的行"""
    header_title_patterns = [
        '分部分项工程和单价措施项目清单与计价表',
        '分部分项工程',
        '工程名称：',
        '标段：',
    ]
    
    header_column_keywords = ['序号', '项目编码', '项目名称', '项目特征', '计量单位', '工程量', '综合单价', '合价']
    summary_keywords = ['本页小计', '合计', '总计', '小计', '共', '页', '表—']
    
    name_col = mapping.get('name')
    desc_col = mapping.get('description')
    sequence_col = mapping.get('sequence')
    code_col = mapping.get('code')
    
    if name_col is not None and name_col < len(row):
        name_val = str(row[name_col]).strip() if row[name_col] else ""
        
        for keyword in summary_keywords:
            if keyword in name_val:
                return True
        
        for pattern in header_title_patterns:
            if pattern in name_val:
                return True
        
        if '项目名称' in name_val and len(name_val) < 15:
            return True
    
    if desc_col is not None and desc_col < len(row):
        desc_val = str(row[desc_col]).strip() if row[desc_col] else ""
        
        for keyword in summary_keywords:
            if keyword in desc_val:
                return True
        
        if '项目特征描述' in desc_val and len(desc_val) < 15:
            return True
    
    header_col_count = 0
    for col_idx in [sequence_col, code_col, name_col, desc_col]:
        if col_idx is not None and col_idx < len(row):
            cell_val = str(row[col_idx]).strip() if row[col_idx] else ""
            for keyword in header_column_keywords:
                if keyword in cell_val:
                    header_col_count += 1
                    break
    
    if header_col_count >= 2:
        return True
    
    if sequence_col is not None and sequence_col < len(row):
        seq_val = str(row[sequence_col]).strip() if row[sequence_col] else ""
        if seq_val == '序号' or '序号' in seq_val:
            return True
    
    return False

def _is_division_row(row: tuple, mapping: Dict[str, int]) -> bool:
    """检测是否为分部行"""
    name_col = mapping.get('name')
    sequence_col = mapping.get('sequence')
    code_col = mapping.get('code')
    
    if name_col is None or name_col >= len(row):
        return False
    
    name_val = str(row[name_col]).strip() if row[name_col] else ""
    if not name_val:
        return False
    
    division_keywords = ['工程', '分部', '分项', '措施项目']
    is_division = any(keyword in name_val for keyword in division_keywords)
    
    seq_val = str(row[sequence_col]).strip() if sequence_col is not None and sequence_col < len(row) and row[sequence_col] else ""
    code_val = str(row[code_col]).strip() if code_col is not None and code_col < len(row) and row[code_col] else ""
    
    if is_division and not seq_val and not code_val:
        return True
    
    return False

def _should_merge_with_previous(current_row: tuple, previous_item: Dict, mapping: Dict[str, int]) -> bool:
    """判断当前行是否应该与前一行合并"""
    if not previous_item:
        return False
    
    name_col = mapping.get('name')
    desc_col = mapping.get('description')
    sequence_col = mapping.get('sequence')
    code_col = mapping.get('code')
    
    current_name = str(current_row[name_col]).strip() if name_col is not None and name_col < len(current_row) and current_row[name_col] else ""
    current_desc = str(current_row[desc_col]).strip() if desc_col is not None and desc_col < len(current_row) and current_row[desc_col] else ""
    current_seq = str(current_row[sequence_col]).strip() if sequence_col is not None and sequence_col < len(current_row) and current_row[sequence_col] else ""
    current_code = str(current_row[code_col]).strip() if code_col is not None and code_col < len(current_row) and current_row[code_col] else ""
    
    prev_name = str(previous_item.get('name', '')).strip()
    prev_desc = str(previous_item.get('description', '')).strip()
    
    if current_code and re.match(r'^\d{9,}$', current_code.replace('-', '')):
        return False
    
    if current_seq and re.match(r'^\d+$', current_seq):
        return False
    
    if not current_seq and current_name and not current_code:
        return True
    
    if len(current_name) < 3 and len(prev_name) > 0:
        return True
    
    incomplete_endings_name = ['混凝', '预拌', '泵送', '强度', '等级', '基础', '独立', '类型', '种类', '形式']
    for ending in incomplete_endings_name:
        if prev_name.endswith(ending):
            return True
    
    incomplete_endings_desc = ['混凝', '预拌', '泵送', '强度等级:', '基础类型:', '混凝土种类:', '种类:', '等级:', '类型:']
    for ending in incomplete_endings_desc:
        if prev_desc.endswith(ending):
            return True
    
    continuation_starts = ['土', '送', '级', '凝', '础', '类', '型']
    if current_name and current_name[0] in continuation_starts:
        for ending in ['混凝', '预拌', '种类:', '类型:', '等级:']:
            if prev_name.endswith(ending) or prev_desc.endswith(ending):
                return True
    
    if current_desc and prev_desc:
        desc_continuations = [
            ('混凝', '土'),
            ('预拌', '混凝'),
            ('种类:', '预拌'),
            ('等级:', 'C'),
        ]
        for prev_ending, curr_start in desc_continuations:
            if prev_desc.endswith(prev_ending) and current_desc.startswith(curr_start):
                return True
    
    return False

def _merge_rows(previous_item: Dict, current_row: tuple, mapping: Dict[str, int]) -> Dict:
    """合并两行数据"""
    merged = previous_item.copy()
    
    name_col = mapping.get('name')
    desc_col = mapping.get('description')
    
    if name_col is not None and name_col < len(current_row):
        current_name = str(current_row[name_col]).strip() if current_row[name_col] else ""
        if current_name:
            prev_name = str(previous_item.get('name', '')).strip()
            if prev_name and current_name:
                overlap = 0
                for i in range(1, min(len(prev_name), len(current_name)) + 1):
                    if prev_name[-i:] == current_name[:i]:
                        overlap = i
                if overlap > 0:
                    merged['name'] = prev_name + current_name[overlap:]
                else:
                    merged['name'] = prev_name + current_name
    
    if desc_col is not None and desc_col < len(current_row):
        current_desc = str(current_row[desc_col]).strip() if current_row[desc_col] else ""
        if current_desc:
            prev_desc = str(previous_item.get('description', '')).strip()
            if prev_desc and current_desc:
                overlap = 0
                for i in range(1, min(len(prev_desc), len(current_desc)) + 1):
                    if prev_desc[-i:] == current_desc[:i]:
                        overlap = i
                if overlap > 0:
                    merged['description'] = prev_desc + current_desc[overlap:]
                else:
                    merged['description'] = prev_desc + current_desc
    
    return merged

# 测试表头检测
def test_header_detection():
    print("=== 测试表头检测 ===")
    
    mapping = {
        'sequence': 0,
        'code': 1,
        'name': 3,
        'description': 5,
    }
    
    header_rows = [
        (None, None, None, '分部分项工程和单价措施项目清单与计价表', None, None),
        (None, None, None, '工程名称：辅助斜坡道空气预热间土建', None, None),
        ('序号', '项目编码', None, '项目名称', None, '项目特征描述'),
        (None, None, None, '本页小计', None, None),
    ]
    
    for i, row in enumerate(header_rows):
        is_header = _is_header_row(row, mapping)
        print(f"行{i+1}: {'是表头' if is_header else '不是表头'} - {row[3] if row[3] else ''}")

# 测试分部行检测
def test_division_detection():
    print("\n=== 测试分部行检测 ===")
    
    mapping = {
        'sequence': 0,
        'code': 1,
        'name': 3,
        'description': 5,
    }
    
    division_rows = [
        (None, None, None, '土石方工程', None, None),
        (None, None, None, '混凝土工程', None, None),
        ('1', '010104003004', None, '挖掘机挖装一般土方', None, '1.挖除现场工作面表层土'),
    ]
    
    for i, row in enumerate(division_rows):
        is_division = _is_division_row(row, mapping)
        print(f"行{i+1}: {'是分部' if is_division else '不是分部'} - {row[3]}")

# 测试合并逻辑
def test_merge_logic():
    print("\n=== 测试合并逻辑 ===")
    
    mapping = {
        'sequence': 0,
        'code': 1,
        'name': 3,
        'description': 5,
    }
    
    row2 = (None, None, None, '土', None, '土，泵送\n3.混凝土强度等级:C30')
    
    previous_item = {
        'sequence': '3',
        'code': '010501003002',
        'name': '现浇混凝土基础 独立基础 混凝',
        'description': '1.基础类型:独立基础\n2.混凝土种类:预拌混凝',
    }
    
    should_merge = _should_merge_with_previous(row2, previous_item, mapping)
    print(f"是否应该合并: {should_merge}")
    
    if should_merge:
        merged = _merge_rows(previous_item, row2, mapping)
        print(f"合并后的项目名称: {merged['name']}")
        print(f"合并后的项目特征: {merged['description']}")

if __name__ == '__main__':
    test_header_detection()
    test_division_detection()
    test_merge_logic()
