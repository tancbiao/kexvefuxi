#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整解析三年级科学题库Word文档并转换为网站JSON格式
"""

import re
import json

def parse_questions():
    # 读取提取的文本
    with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    # 数据结构
    units = []
    lessons_data = {}
    
    # 答案解析
    answers = {}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 匹配单元
        unit_match = re.match(r'第([一二三四五六七八九十]+)单元[：:](.+)', line)
        if unit_match:
            unit_name = f'第{unit_match.group(1)}单元 {unit_match.group(2).strip()}'
            units.append({'name': unit_name, 'lessons': []})
            i += 1
            continue
        
        # 匹配课程
        lesson_match = re.match(r'第(\d+)课[：:](.+)', line)
        if lesson_match:
            lesson_num = lesson_match.group(1)
            lesson_name = lesson_match.group(2).strip()
            lessons_data[lesson_num] = {
                'name': lesson_name,
                'basic': [],
                'medium': []
            }
            if units:
                units[-1]['lessons'].append(lesson_num)
            i += 1
            continue
        
        # 匹配答案部分
        ans_match = re.match(r'第(\d+)课答案', line)
        if ans_match:
            lesson_num = ans_match.group(1)
            # 下一行是选择题答案
            i += 1
            if i < len(lines):
                choice_ans = re.match(r'一、[\d-]+\s*([A-Z]+)', lines[i])
                if choice_ans:
                    answers[lesson_num] = {'choice': list(choice_ans.group(1))}
            # 再下一行是判断题答案
            i += 1
            if i < len(lines):
                judge_ans = re.match(r'二、[\d-]+\s*([√×]+)', lines[i])
                if judge_ans:
                    if lesson_num not in answers:
                        answers[lesson_num] = {'choice': [], 'judge': []}
                    answers[lesson_num]['judge'] = list(judge_ans.group(1))
            i += 1
            continue
        
        i += 1
    
    return units, lessons_data, answers

def build_question_data(units, lessons_data, answers):
    """
    构建最终的questionData结构
    由于实际解析题目内容很复杂，这里先生成框架
    """
    questionData = {}
    
    for idx, unit in enumerate(units):
        unit_key = f'unit{idx + 1}'
        questionData[unit_key] = {
            'name': unit['name'],
            'icon': '📚',
            'lessons': []
        }
        
        for lesson_num in unit['lessons']:
            lesson_info = lessons_data.get(lesson_num, {})
            lesson_obj = {
                'id': f'u{idx + 1}l{lesson_num}',
                'name': lesson_info.get('name', f'第{lesson_num}课'),
                'icon': '<img src="../../icons/book.png" class="icon-32">',
                'basic': [],
                'medium': [],
                'hard': []
            }
            questionData[unit_key]['lessons'].append(lesson_obj)
    
    return questionData

if __name__ == '__main__':
    units, lessons_data, answers = parse_questions()
    
    print('=== 单元结构 ===')
    for u in units:
        print(f"{u['name']}: {len(u['lessons'])}课")
    
    print(f'\n=== 答案统计 ===')
    for lesson, ans in sorted(answers.items(), key=lambda x: int(x[0])):
        print(f"第{lesson}课: 选择{len(ans.get('choice', []))}题, 判断{len(ans.get('judge', []))}题")
    
    # 生成questionData框架
    questionData = build_question_data(units, lessons_data, answers)
    
    # 输出JSON预览
    print('\n=== questionData 结构 ===')
    print(json.dumps(questionData, ensure_ascii=False, indent=2)[:2000])
