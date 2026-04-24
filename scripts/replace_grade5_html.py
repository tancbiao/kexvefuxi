"""Replace questionData in 5/2/index.html with teacher version"""
import re

html_path = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\5\2\index.html'
embedded_path = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\data\5-2-embedded.js'

html = open(html_path, 'r', encoding='utf-8').read()
new_qd = open(embedded_path, 'r', encoding='utf-8').read()

# Find old questionData block
start_marker = 'const questionData = {'
start_idx = html.find(start_marker)
if start_idx < 0:
    print('ERROR: Cannot find questionData in HTML')
    exit(1)

# Find matching closing };
brace_count = 0
for i in range(start_idx, len(html)):
    if html[i] == '{':
        brace_count += 1
    elif html[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            while end_idx < len(html) and html[end_idx] in ';\n ':
                end_idx += 1
            break

# Get surrounding context (include comment line before)
pre_start = html.rfind('\n', 0, start_idx)
if pre_start >= 0:
    pre_start = pre_start + 1

old_size = end_idx - pre_start
new_size = len(new_qd)
print(f'Replacing {old_size} chars with {new_size} chars')

html_new = html[:pre_start] + new_qd + '\n' + html[end_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_new)

# Verify
html2 = open(html_path, 'r', encoding='utf-8').read()
print(f'HTML size: {len(html2)} chars')
print(f'Has <html>: {"<html" in html2}')
print(f'Has </html>: {"</html>" in html2}')
print(f'Has questionData: {"const questionData" in html2}')
print(f'Has function selectOption: {"function selectOption" in html2}')

# Count lessons in new questionData
lesson_count = html2.count("id: 'u")
print(f'Lessons in questionData: {lesson_count}')
print('Done!')
