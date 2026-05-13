import re

html_path = r'c:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\4\2\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'const questionData = {'
start_idx = content.find(start_marker)
print(f'Start marker found at: {start_idx}')

end_marker = '// ========== 装备系统（兼容层）=========='
end_idx = content.find(end_marker)
print(f'End marker found at: {end_idx}')

if start_idx == -1:
    print('ERROR: Start marker not found')
elif end_idx == -1:
    print('ERROR: End marker not found')
else:
    before_end = content[:end_idx]
    last_brace = before_end.rfind('}')
    last_semicolon = before_end.rfind(';', 0, last_brace + 10)
    print(f'Last brace at: {last_brace}, semicolon at: {last_semicolon}')

    block_len = last_semicolon + 1 - start_idx
    print(f'Block to remove: {block_len} chars')

    new_block = '// questionData 由 data/4-2-lessons.js 动态加载，首次进入选课界面时填充\nvar questionData = {};'

    new_content = content[:start_idx] + new_block + '\n' + content[last_semicolon + 1:]

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'File size: before={len(content)}, after={len(new_content)}')
    print('SUCCESS: questionData replaced!')
