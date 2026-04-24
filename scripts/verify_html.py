html_path = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\4\2\index.html'
html = open(html_path, 'r', encoding='utf-8').read()
print(f'Total lines: {html.count(chr(10))+1}')
print(f'Has html tag: {"<html" in html}')
print(f'Has questionData: {"const questionData" in html}')
print(f'Has selectOption: {"function selectOption" in html}')
print(f'Has finishQuiz: {"function finishQuiz" in html}')

# Count lessons in new questionData
import re
lessons = re.findall(r"id: 'u\d+l(\d+)'", html)
print(f'Lessons found: {len(lessons)}, IDs: {lessons}')

# Count total questions
basic_count = html.count('"q":')
print(f'Total questions: {basic_count}')
