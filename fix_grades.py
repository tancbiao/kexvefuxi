#!/usr/bin/env python3
"""Fix grades 3/4/5: remove cloudKey, add wrapper null guard"""
import re, os

base = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi'

for grade in ['3', '4', '5']:
    path = os.path.join(base, grade, '2', 'index.html')
    print(f'Processing Grade {grade}...', end=' ')
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    
    # 1. Remove getCloudKey checks in saveToCloud/loadFromCloud
    content = re.sub(
        r"if \(typeof getCloudKey !== 'function' \|\| !getCloudKey\(\)\) return;?\n?",
        '', content
    )
    
    # 2. Remove JSONBin key check in loadAndRenderRanking
    content = re.sub(
        r"// 检查 JSONBin Key 是否配置\n.*?if \(typeof getCloudKey !== .function. \|\| !getCloudKey\(\)\) \{\n.*?listEl\.innerHTML = .*?;\n.*?return;\n.*?\}\n",
        '', content
    )
    
    # 3. Add wrapper null guard for mousedown
    content = re.sub(
        r"(const wrapper = document\.getElementById\('charWrapper'\);\s+let isDragging = false, offX, offY;)\s+wrapper\.addEventListener\('mousedown'",
        r"\1\n  if (wrapper) {\n  wrapper.addEventListener('mousedown'",
        content
    )
    
    # 4. Add wrapper null guard for touchstart
    content = re.sub(
        r"(document\.addEventListener\('mouseup', \(\) => \{ isDragging = false; \}\);)\s+wrapper\.addEventListener\('touchstart'",
        r"\1\n  }\n  if (wrapper) {\n  wrapper.addEventListener('touchstart'",
        content
    )
    
    # 5. Close mousedown if block
    content = re.sub(
        r"(e\.preventDefault\(\);\s+\}\);)\s+(document\.addEventListener\('mousemove')",
        r"\1\n  }\n  \2",
        content
    )
    
    # 6. Close touchstart if block
    content = re.sub(
        r"(\{ passive: true \}\);)\s+(document\.addEventListener\('touchmove')",
        r"\1\n  }\n  \2",
        content
    )
    
    # 7. Add null check in mousemove/touchmove handlers
    content = re.sub(
        r"if \(!isDragging\) return;\s+wrapper\.style\.left",
        r"if (!isDragging || !wrapper) return;\n  wrapper.style.left",
        content
    )
    
    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('FIXED')
    else:
        print('no changes')

print('ALL DONE')
