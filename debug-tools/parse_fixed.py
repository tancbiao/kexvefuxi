#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tanc\Desktop\_temp_questions.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

# 第一步：收集所有答案
allAnswers = {}
ansMap = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

for i, L in enumerate(lines):
    m = re.match(r'第(\d+)课答案', L)
    if m:
        lessonNum = m.group(1)
        choiceAns = []
        judgeAns = []

        # 选择题答案（下一行）
        if i+1 < len(lines):
            for c in re.findall(r'[ABCD]', lines[i+1]):
                choiceAns.append(ansMap[c])

        # 判断题答案（下下行）
        if i+2 < len(lines):
            for c in re.findall(r'[√×]', lines[i+2]):
                judgeAns.append(0 if c == '√' else 1)

        allAnswers[lessonNum] = {'c': choiceAns, 'j': judgeAns}

print(f'收集到 {len(allAnswers)} 课答案')

# 第二步：解析题目
questionData = {}
currentUnitKey = None
currentLesson = None
currentLessonNum = None
currentSection = None
qCount = 0
jCount = 0

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
        currentLessonNum = m.group(1)
        lessonName = m.group(2).strip()
        currentLesson = {
            'id': f'u{len(questionData)}l{currentLessonNum}',
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

    # 选择题部分开始
    if '一、选择题' in L:
        currentSection = 'c'
        i += 1
        continue

    # 判断题部分开始
    if '二、判断题' in L:
        currentSection = 'j'
        i += 1
        continue

    # 跳过答案部分
    if re.match(r'第\d+课答案', L):
        i += 3  # 跳过答案块
        continue

    # 跳过答案格式行
    if re.match(r'[一二]、\d+-\d+', L):
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
                        # 获取答案
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
