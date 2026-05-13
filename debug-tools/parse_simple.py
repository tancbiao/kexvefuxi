#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json

with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

questionData = {}
current_unit_key = None
current_lesson = None
current_section = None
q_count = 0
j_count = 0
lesson_ans = {'c': [], 'j': []}
ans_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

i = 0
while i < len(lines):
    L = lines[i]
    
    # 单元
    m = re.match(r'第([一二三四五六七八九十]+)单元[：:](.+)', L)
    if m:
        current_unit_key = f'unit{len(questionData)+1}'
        questionData[current_unit_key] = {'name': f'第{m.group(1)}单元 {m.group(2).strip()}', 'icon': '📚', 'lessons': []}
        i += 1
        continue
    
    # 课程
    m = re.match(r'第(\d+)课[：:](.+)', L)
    if m:
        current_lesson = {'id': f'u{len(questionData)}l{m.group(1)}', 'name': m.group(2).strip(),
                          'icon': '<img src="../../icons/book.png" class="icon-32">',
                          'basic': [], 'medium': [], 'hard': []}
        if current_unit_key:
            questionData[current_unit_key]['lessons'].append(current_lesson)
        q_count = 0
        j_count = 0
        lesson_ans = {'c': [], 'j': []}
        i += 1
        continue
    
    # 选择题部分
    if '一、选择题' in L:
        current_section = 'c'
        i += 1
        continue
    
    # 判断题部分
    if '二、判断题' in L:
        current_section = 'j'
        i += 1
        continue
    
    # 答案
    m = re.match(r'第(\d+)课答案', L)
    if m:
        current_section = None
        i += 1
        if i < len(lines):
            m2 = re.search(r'[A-D]{5,10}', lines[i])
            if m2:
                lesson_ans['c'] = [ans_map[c] for c in m2.group()]
        i += 1
        if i < len(lines):
            m2 = re.search(r'[√×]{5}', lines[i])
            if m2:
                lesson_ans['j'] = [0 if c=='√' else 1 for c in m2.group()]
        i += 1
        continue
    
    # 跳过答案格式行
    if re.match(r'一、\d+-\d+', L) or re.match(r'二、\d+-\d+', L):
        i += 1
        continue
    
    # 选择题
    if current_section == 'c' and current_lesson:
        m = re.match(r'^\d+[\.、．]\s*(.+?)\s*[（(]\s*[）)]', L)
        if m:
            q_text = m.group(1).strip()
            i += 1
            if i < len(lines):
                opts = re.findall(r'[A-D][\.、．]\s*([^A-D]+?)(?=\s*[A-D][\.、．]|$)', lines[i])
                opts = [o.strip() for o in opts if o.strip()]
                if opts and len(opts) >= 2:
                    ans = lesson_ans['c'][q_count] if q_count < len(lesson_ans['c']) else 0
                    q_obj = {'q': q_text, 'options': opts, 'answer': ans, 'hint': ''}
                    if q_count < 7:
                        current_lesson['basic'].append(q_obj)
                    else:
                        current_lesson['medium'].append(q_obj)
                    q_count += 1
    
    # 判断题
    if current_section == 'j' and current_lesson:
        m = re.match(r'^\d+[\.、．]\s*(.+?)\s*[（(]\s*[）)]', L)
        if m:
            q_text = m.group(1).strip()
            opts = ['√', '×']
            ans = lesson_ans['j'][j_count] if j_count < len(lesson_ans['j']) else 0
            q_obj = {'q': q_text, 'options': opts, 'answer': ans, 'hint': ''}
            current_lesson['basic'].append(q_obj)
            j_count += 1
    
    i += 1

# 保存
with open(r'C:\Users\tanc\Desktop\questionData_32.json', 'w', encoding='utf-8') as f:
    json.dump(questionData, f, ensure_ascii=False, indent=2)

print('Done')
