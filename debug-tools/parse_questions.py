#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json

# 读取提取的文本
with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 答案映射 (字母->数字)
letter_to_num = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

# 结果数据结构
questionData = {}

# 当前状态
current_unit = None
current_unit_key = None
current_lesson = None
current_section = None  # 'choice' or 'judge'
question_idx = 0
judge_idx = 0

# 解析
for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
    
    # 匹配单元
    unit_match = re.match(r'第([一二三四五六七八九十]+)单元[：:](.+)', line)
    if unit_match:
        unit_num = unit_match.group(1)
        unit_name = unit_match.group(2).strip()
        current_unit = unit_name
        current_unit_key = f'unit{len(questionData) + 1}'
        questionData[current_unit_key] = {
            'name': f'第{unit_num}单元 {unit_name}',
            'icon': '📚',
            'lessons': []
        }
        continue
    
    # 匹配课程
    lesson_match = re.match(r'第(\d+)课[：:](.+)', line)
    if lesson_match:
        lesson_num = int(lesson_match.group(1))
        lesson_name = lesson_match.group(2).strip()
        current_lesson = {
            'id': f'u{len(questionData)}l{lesson_num}',
            'name': lesson_name,
            'icon': '<img src="../../icons/book.png" class="icon-32">',
            'basic': [],
            'medium': [],
            'hard': []
        }
        if current_unit_key and questionData.get(current_unit_key):
            questionData[current_unit_key]['lessons'].append(current_lesson)
        question_idx = 0
        judge_idx = 0
        continue
    
    # 匹配选择题部分
    if '一、选择题' in line:
        current_section = 'choice'
        continue
    
    # 匹配判断题部分
    if '二、判断题' in line:
        current_section = 'judge'
        continue
    
    # 匹配答案部分 - 跳过
    if re.match(r'第\d+课答案', line):
        current_section = None
        continue
    
    # 匹配选择题 (问题)
    if current_section == 'choice' and current_lesson:
        # 检查是否是选项行
        option_match = re.match(r'^([A-D])[\.、．]\s*(.+)', line)
        if option_match:
            # 这是一个选项
            continue
        
        # 检查是否是问题行
        q_match = re.match(r'^(\d+)[\.、．]\s*(.+?)\s*[（(]\s*[）)]', line)
        if q_match:
            question_idx += 1
            q_text = q_match.group(2).strip()
            # 简单存储，后续需要收集选项
            continue
    
    # 匹配判断题
    if current_section == 'judge' and current_lesson:
        j_match = re.match(r'^(\d+)[\.、．]\s*(.+?)\s*[（(]\s*[）)]', line)
        if j_match:
            judge_idx += 1
            j_text = j_match.group(2).strip()
            continue

# 输出结构预览
print(f'解析完成!')
print(f'单元数: {len(questionData)}')
for key, unit in questionData.items():
    print(f"  {key}: {unit['name']} - {len(unit['lessons'])}课")
