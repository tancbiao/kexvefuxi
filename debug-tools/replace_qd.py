#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取新的questionData
with open(r'C:\Users\tanc\Desktop\questionData_32.json', 'r', encoding='utf-8') as f:
    newQD = f.read()

# 读取原HTML
with open(r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\3\2\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到questionData范围
startLine = None
endLine = None
braceCount = 0
inQD = False

for i, line in enumerate(lines):
    if 'const questionData' in line:
        startLine = i
        inQD = True
        braceCount = line.count('{') - line.count('}')
        continue
    if inQD:
        braceCount += line.count('{') - line.count('}')
        if braceCount <= 0:
            endLine = i
            break

print(f'替换范围: 第{startLine+1}行 到 第{endLine+1}行')

# 格式化新的questionData
newQD_js = 'const questionData = ' + newQD + ';\n'

# 替换内容
newLines = lines[:startLine] + [newQD_js] + lines[endLine+1:]

# 保存
with open(r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\3\2\index.html', 'w', encoding='utf-8') as f:
    f.writelines(newLines)

print(f'完成! 原文件{len(lines)}行, 新文件{len(newLines)}行')
