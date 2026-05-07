#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析三年级科学题库 - 格式：问题行(无编号) + 选项行
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

questionData = {}
currentUnitKey = None
currentLesson = None
currentSection = None
qCount = 0
jCount = 0
lessonAns = {'c': [], 'j': []}
ansMap = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

i = 0
while i < len(lines):
    L = lines[i]

    # 单元
    m = re.match(r'第([一二三四五六七八九十]+)单元[：:](.+)', L)
    if m:
        currentUnitKey = f'unit{len(questionData)+1}'
        questionData[currentUnitKey] = {
            'name': f'第{m.group(1)}单元 {m.group(2).strip()}',
            'icon': '📚',
            'lessons': []
        }
        i += 1
        continue

    # 课程
    m = re.match(r'第(\d+)课[：:](.+)', L)
    if m:
        currentLesson = {
            'id': f'u{len(questionData)}l{m.group(1)}',
            'name': m.group(2).strip(),
            'icon': '<img src="../../icons/book.png" class="icon-32">',
            'basic': [],
            'medium': [],
            'hard': []
        }
        if currentUnitKey:
            questionData[currentUnitKey]['lessons'].append(currentLesson)
        qCount = 0
        jCount = 0
        lessonAns = {'c': [], 'j': []}
        i += 1
        continue

    # 选择题部分
    if '一、选择题' in L:
        currentSection = 'c'
        i += 1
        continue

    # 判断题部分
    if '二、判断题' in L:
        currentSection = 'j'
        i += 1
        continue

    # 答案
    m = re.match(r'第(\d+)课答案', L)
    if m:
        currentSection = None
        i += 1
        if i < len(lines):
            m2 = re.search(r'[ABCD]{5,10}', lines[i])
            if m2:
                lessonAns['c'] = [ansMap[c] for c in m2.group()]
        i += 1
        if i < len(lines):
            m2 = re.search(r'[√×]{5}', lines[i])
            if m2:
                lessonAns['j'] = [0 if c=='√' else 1 for c in m2.group()]
        i += 1
        continue

    # 跳过答案格式行
    if re.match(r'一、\d+-\d+', L) or re.match(r'二、\d+-\d+', L):
        i += 1
        continue

    # 选择题 - 无编号问题行，以（ ）结尾
    if currentSection == 'c' and currentLesson:
        # 问题行：以（ ）结尾
        if re.search(r'[（(]\s*[）)]', L):
            qText = re.sub(r'\s*[（(]\s*[）)].*$', '', L).strip()
            if qText:
                i += 1
                if i < len(lines):
                    # 选项行
                    opts = re.findall(r'[ABCD][\.、．]\s*([^ABCD]+?)(?=\s*[ABCD][\.、．]|$)', lines[i])
                    opts = [o.strip() for o in opts if o.strip()]
                    if len(opts) >= 2:
                        ans = lessonAns['c'][qCount] if qCount < len(lessonAns['c']) else 0
                        qObj = {'q': qText, 'options': opts, 'answer': ans, 'hint': ''}
                        if qCount < 7:
                            currentLesson['basic'].append(qObj)
                        else:
                            currentLesson['medium'].append(qObj)
                        qCount += 1

    # 判断题 - 以（ ）结尾
    if currentSection == 'j' and currentLesson:
        if re.search(r'[（(]\s*[）)]', L):
            qText = re.sub(r'\s*[（(]\s*[）)].*$', '', L).strip()
            if qText:
                opts = ['√', '×']
                ans = lessonAns['j'][jCount] if jCount < len(lessonAns['j']) else 0
                qObj = {'q': qText, 'options': opts, 'answer': ans, 'hint': ''}
                currentLesson['basic'].append(qObj)
                jCount += 1

    i += 1

# 统计
totalL = 0
totalB = 0
totalM = 0
for uk, u in questionData.items():
    for l in u['lessons']:
        totalL += 1
        totalB += len(l['basic'])
        totalM += len(l['medium'])

print(f'完成! {len(questionData)}单元, {totalL}课, {totalB}basic, {totalM}medium')

# 保存
with open(r'C:\Users\tanc\Desktop\questionData_32.json', 'w', encoding='utf-8') as f:
    json.dump(questionData, f, ensure_ascii=False, indent=2)
print('已保存')
