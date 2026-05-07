#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两步解析：
1. 先收集所有答案
2. 再解析题目并应用答案
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

# 第一步：收集所有答案
allAnswers = {}
ansMap = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

i = 0
while i < len(lines):
    m = re.match(r'第(\d+)课答案', lines[i])
    if m:
        lessonNum = m.group(1)
        choiceAns = []
        judgeAns = []

        i += 1
        # 选择题答案行
        if i < len(lines):
            # 提取所有答案字母
            ansMatches = re.findall(r'[ABCD]+', lines[i])
            for am in ansMatches:
                choiceAns.extend([ansMap[c] for c in am])

        i += 1
        # 判断题答案行
        if i < len(lines):
            judgeMatches = re.findall(r'[√×]+', lines[i])
            for jm in judgeMatches:
                judgeAns.extend([0 if c == '√' else 1 for c in jm])

        allAnswers[lessonNum] = {'c': choiceAns, 'j': judgeAns}
        i += 1
    else:
        i += 1

print(f'收集到 {len(allAnswers)} 课答案')

# 第二步：解析题目结构
questionData = {}
currentUnitKey = None
currentLesson = None
currentSection = None
qCount = 0
jCount = 0

i = 0
while i < len(lines):
    L = lines[i]

    # 跳过答案部分
    if re.match(r'第\d+课答案', L):
        while i < len(lines) and not re.match(r'第[一二三四五六七八九十]+单元', lines[i]):
            i += 1
        continue

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
        lessonNum = m.group(1)
        lessonName = m.group(2).strip()
        currentLesson = {
            'id': f'u{len(questionData)}l{lessonNum}',
            'name': lessonName,
            'icon': '<img src="../../icons/book.png" class="icon-32">',
            'basic': [],
            'medium': [],
            'hard': []
        }
        if currentUnitKey:
            questionData[currentUnitKey]['lessons'].append(currentLesson)
        qCount = 0
        jCount = 0
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

    # 选择题
    if currentSection == 'c' and currentLesson:
        if re.search(r'[（(]\s*[）)]', L):
            qText = re.sub(r'\s*[（(]\s*[）)].*$', '', L).strip()
            if qText and len(qText) > 2:
                i += 1
                if i < len(lines):
                    opts = re.findall(r'[ABCD][\.、．]\s*([^ABCD]+?)(?=\s*[ABCD][\.、．]|$)', lines[i])
                    opts = [o.strip() for o in opts if o.strip()]
                    if len(opts) >= 2:
                        # 应用答案
                        lessonNum = None
                        for k, v in allAnswers.items():
                            if len(v['c']) >= qCount:
                                lessonNum = k
                                break

                        if lessonNum and qCount < len(allAnswers[lessonNum]['c']):
                            ans = allAnswers[lessonNum]['c'][qCount]
                        else:
                            # 尝试从当前课程的答案中获取
                            currentLessonNum = currentLesson['id'].split('l')[1]
                            if currentLessonNum in allAnswers and qCount < len(allAnswers[currentLessonNum]['c']):
                                ans = allAnswers[currentLessonNum]['c'][qCount]
                            else:
                                ans = 0

                        qObj = {'q': qText, 'options': opts, 'answer': ans, 'hint': ''}
                        if qCount < 7:
                            currentLesson['basic'].append(qObj)
                        else:
                            currentLesson['medium'].append(qObj)
                        qCount += 1

    # 判断题
    if currentSection == 'j' and currentLesson:
        if re.search(r'[（(]\s*[）)]', L):
            qText = re.sub(r'\s*[（(]\s*[）)].*$', '', L).strip()
            if qText and len(qText) > 2:
                opts = ['√', '×']

                # 应用答案
                currentLessonNum = currentLesson['id'].split('l')[1]
                if currentLessonNum in allAnswers and jCount < len(allAnswers[currentLessonNum]['j']):
                    ans = allAnswers[currentLessonNum]['j'][jCount]
                else:
                    ans = 0

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
