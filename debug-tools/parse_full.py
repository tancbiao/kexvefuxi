#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整解析三年级科学题库并生成JSON
格式：问题行 + 选项行（选择题）/ 单行（判断题）
"""

import re
import json

def parse_all():
    with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    # 结果
    questionData = {}
    current_unit_key = None
    current_lesson = None
    current_section = None  # 'choice' or 'judge'
    question_count = 0
    judge_count = 0
    
    # 答案映射
    answer_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    # 当前课程的答案
    lesson_answers = {'choice': [], 'judge': []}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # === 单元标题 ===
        unit_match = re.match(r'第([一二三四五六七八九十]+)单元[：:](.+)', line)
        if unit_match:
            unit_num = len(questionData) + 1
            current_unit_key = f'unit{unit_num}'
            unit_name = f'第{unit_match.group(1)}单元 {unit_match.group(2).strip()}'
            questionData[current_unit_key] = {
                'name': unit_name,
                'icon': '📚',
                'lessons': []
            }
            i += 1
            continue
        
        # === 课程标题 ===
        lesson_match = re.match(r'第(\d+)课[：:](.+)', line)
        if lesson_match:
            lesson_num = lesson_match.group(1)
            lesson_name = lesson_match.group(2).strip()
            current_lesson = {
                'id': f'u{len(questionData)}l{lesson_num}',
                'name': lesson_name,
                'icon': '<img src="../../icons/book.png" class="icon-32">',
                'basic': [],
                'medium': [],
                'hard': []
            }
            if current_unit_key:
                questionData[current_unit_key]['lessons'].append(current_lesson)
            question_count = 0
            judge_count = 0
            lesson_answers = {'choice': [], 'judge': []}
            i += 1
            continue
        
        # === 选择题部分 ===
        if '一、选择题' in line:
            current_section = 'choice'
            i += 1
            continue
        
        # === 判断题部分 ===
        if '二、判断题' in line:
            current_section = 'judge'
            i += 1
            continue
        
        # === 答案部分 ===
        ans_match = re.match(r'第(\d+)课答案', line)
        if ans_match:
            current_section = None
            # 下一行是选择题答案
            i += 1
            if i < len(lines):
                choice_ans = re.search(r'[A-D]{5,10}', lines[i])
                if choice_ans:
                    lesson_answers['choice'] = [answer_map[c] for c in choice_ans.group()]
            # 再下一行是判断题答案
            i += 1
            if i < len(lines):
                judge_ans = re.search(r'[√×]{5}', lines[i])
                if judge_ans:
                    lesson_answers['judge'] = [0 if c == '√' else 1 for c in judge_ans.group()]
            i += 1
            continue
        
        # === 跳过答案行格式 ===
        if re.match(r'一、\d+-\d+\s*[A-Z]+', line):
            continue
        if re.match(r'二、\d+-\d+\s*[√×]+', line):
            continue
        
        # === 解析选择题 ===
        if current_section == 'choice' and current_lesson:
            # 检查是否是问题行（以数字开头，以括号结尾）
            q_match = re.match(r'^\d+[\.、．]\s*(.+?)\s*[（(]\s*[）)]', line)
            if q_match:
                question_text = q_match.group(1).strip()
                
                # 下一行是选项
                i += 1
                if i < len(lines):
                    options_line = lines[i]
                    # 解析选项 A. xxx B. xxx C. xxx
                    options = re.findall(r'[A-D][\.、．]\s*([^A-D]+?)(?=\s*[A-D][\.、．]|$)', options_line)
                    options = [opt.strip() for opt in options if opt.strip()]
                    
                    # 获取答案
                    if question_count < len(lesson_answers['choice']):
                        answer = lesson_answers['choice'][question_count]
                    else:
                        answer = 0  # 默认
                    
                    question_obj = {
                        'q': question_text,
                        'options': options,
                        'answer': answer,
                        'hint': ''
                    }
                    
                    # 前7题放basic，后3题放medium
                    if question_count < 7:
                        current_lesson['basic'].append(question_obj)
                    else:
                        current_lesson['medium'].append(question_obj)
                    
                    question_count += 1
        
        # === 解析判断题 ===
        if current_section == 'judge' and current_lesson:
            j_match = re.match(r'^\d+[\.、．]\s*(.+?)\s*[（(]\s*[）)]', line)
            if j_match:
                question_text = j_match.group(1).strip()
                
                # 判断题选项固定
                options = ['√', '×']
                
                # 获取答案
                if judge_count < len(lesson_answers['judge']):
                    answer = lesson_answers['judge'][judge_count]
                else:
                    answer = 0  # 默认
                
                question_obj = {
                    'q': question_text,
                    'options': options,
                    'answer': answer,
                    'hint': ''
                }
                
                # 判断题都放basic
                current_lesson['basic'].append(question_obj)
                judge_count += 1
        
        i += 1
    
    return questionData

if __name__ == '__main__':
    print('开始解析...')
    questionData = parse_all()
    
    # 统计
    total_lessons = 0
    total_basic = 0
    total_medium = 0
    
    for unit_key, unit in questionData.items():
        print(f"\n{unit['name']}")
        for lesson in unit['lessons']:
            total_lessons += 1
            basic_count = len(lesson['basic'])
            medium_count = len(lesson['medium'])
            total_basic += basic_count
            total_medium += medium_count
            print(f"  {lesson['name']}: basic {basic_count}题, medium {medium_count}题")
    
    print(f"\n总计: {total_lessons}课, basic {total_basic}题, medium {total_medium}题")
    
    # 保存JSON
    output_path = r'C:\Users\tanc\Desktop\questionData_32.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questionData, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {output_path}")
