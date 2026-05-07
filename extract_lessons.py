#!/usr/bin/env python3
"""
Extract questionData from index.html files and create separate lesson JS files.
Uses recursive brace counting with proper handling.
"""

import re
import os
from datetime import datetime

# Base paths
BASE_DIR = 'c:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi'

# Grade configurations
GRADES = {
    '3': {
        'index_path': f'{BASE_DIR}/3/2/index.html',
        'data_path': f'{BASE_DIR}/data/3-2-lessons.js',
        'version': '20260507',
        'load_func': 'loadLessons32',
        'var_name': 'QUESTION_BANK_3_2_LESSONS'
    },
    '5': {
        'index_path': f'{BASE_DIR}/5/2/index.html',
        'data_path': f'{BASE_DIR}/data/5-2-lessons.js',
        'version': '20260507',
        'load_func': 'loadLessons52',
        'var_name': 'QUESTION_BANK_5_2_LESSONS'
    },
    '6': {
        'index_path': f'{BASE_DIR}/6/2/index.html',
        'data_path': f'{BASE_DIR}/data/6-2-lessons.js',
        'version': '20260507',
        'load_func': 'loadLessons62',
        'var_name': 'QUESTION_BANK_6_2_LESSONS'
    }
}

def find_matching_brace(content, start_pos):
    """Find the position of the matching closing brace using stack."""
    stack = 0
    i = start_pos
    while i < len(content):
        c = content[i]
        if c == '{':
            stack += 1
        elif c == '}':
            stack -= 1
            if stack == 0:
                return i + 1  # Return position after the closing brace
        elif c == '"':
            # Skip string literals to avoid counting braces inside strings
            i += 1
            while i < len(content):
                if content[i] == '\\':
                    i += 2
                    continue
                if content[i] == '"':
                    break
                i += 1
        i += 1
    return -1

def extract_question_data(filepath, grade):
    """Extract questionData from index.html"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find "const questionData = {"
    pattern = r'const questionData = \{'
    match = re.search(pattern, content)
    if not match:
        print(f"  [ERROR] 'const questionData = {{' not found in {filepath}")
        return None

    start_pos = match.end() - 1  # Position of the opening brace
    start_line = content[:start_pos].count('\n') + 1

    # Find the matching closing brace
    end_pos = find_matching_brace(content, start_pos)
    if end_pos == -1:
        print(f"  [ERROR] Could not find matching closing brace")
        return None

    end_line = content[:end_pos].count('\n')

    print(f"  [INFO] questionData: lines {start_line}-{end_line} ({end_line - start_line + 1} lines)")

    # Extract the content
    json_str = content[start_pos:end_pos]
    return json_str, start_pos, end_pos

def create_lessons_js(data_path, var_name, json_str, grade):
    """Create the lesson JS file from extracted data"""
    today = datetime.now().strftime('%Y-%m-%d')
    grade_name = {'3': '三', '5': '五', '6': '六'}.get(grade, grade)

    # The json_str starts with '{' and ends with '}'
    # We need to format it as JavaScript object literal

    # Create header
    header = f'''// {grade_name}年级下册科学题库（单人练习用）
// 由 index.html 提取，支持动态加载
// 最后更新：{today}

(function() {{
  // 加载内置题库数据
  var questionData = {json_str};

  // 注册到全局变量
  window.{var_name} = questionData;
}})();
'''

    # Write the file
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(header)

    # Check file size
    size = os.path.getsize(data_path)
    print(f"  [OK] Created {data_path} ({size} bytes)")

def modify_index_html(filepath, grade, load_func_name, var_name, data_filename, start_pos, end_pos):
    """Modify index.html to use dynamic loading"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create the replacement code
    load_code = f'''// questionData 由 data/{data_filename} 动态加载，首次进入选课界面时填充
var questionData = {{}};

var _lessonsLoaded = false;

function showLevelSelect() {{
  if (!_lessonsLoaded) {{
    var grid = document.getElementById('levelGrid');
    if (grid) grid.innerHTML = '<div style="text-align:center;padding:40px;">📚 正在加载题库...</div>';
    {load_func_name}(function() {{
      _lessonsLoaded = true;
      renderLevelGrid();
    }});
  }} else {{
    renderLevelGrid();
  }}
  showScreen('levelScreen');
}}

function {load_func_name}(callback) {{
  var script = document.createElement('script');
  script.src = '../../data/{data_filename}?v=20260507';
  script.onload = function() {{
    if (window.{var_name}) {{
      Object.assign(questionData, window.{var_name});
    }}
    callback && callback();
  }};
  script.onerror = function() {{
    var grid = document.getElementById('levelGrid');
    if (grid) grid.innerHTML = '<div style="text-align:center;padding:40px;color:#ff6b6b;">题库加载失败，请刷新重试</div>';
  }};
  document.head.appendChild(script);
}}

'''

    # Find "const questionData = {" and replace from there to the closing brace
    pattern = r'const questionData = \{'
    match = re.search(pattern, content)
    if not match:
        print(f"  [WARN] Could not find questionData to replace")
        return False

    # Insert the new code before questionData
    insert_pos = match.start()

    # Find the showLevelSelect function in the original code
    show_level_match = re.search(r'function showLevelSelect\(\)\s*\{[^}]*renderLevelGrid\(\);[^}]*\}', content)
    if show_level_match:
        # Replace the original showLevelSelect
        original_code = content[show_level_match.start():show_level_match.end()]
        # We'll handle this by just inserting our code before questionData

    # Replace the questionData section
    content = content[:insert_pos] + load_code + content[end_pos:]

    # Also add fallback loading in startLesson - find and add after existing checks
    # Look for patterns like: if (!questionData || Object.keys(questionData).length === 0)
    fallback_pattern = r"(if \(!questionData.*?\)\s*\{[^}]*Object\.assign\(questionData,.*?\);)"
    fallback_match = re.search(fallback_pattern, content, re.DOTALL)
    if fallback_match:
        print(f"  [INFO] Found existing fallback loading pattern")
    else:
        # Try to add fallback in startLesson function
        start_lesson_match = re.search(r'function startLesson\([^)]*\)\s*\{', content)
        if start_lesson_match:
            print(f"  [INFO] Adding fallback in startLesson")
            # Find a good insertion point (after the function declaration)
            insert_at = start_lesson_match.end()
            fallback = f'\n  // 确保题库已加载\n  if (!questionData || Object.keys(questionData).length === 0) {{\n    Object.assign(questionData, window.{var_name} || {{}});\n  }}\n'
            # Only add if not already present
            if 'Object.assign(questionData, window.' + var_name not in content:
                content = content[:insert_at] + fallback + content[insert_at:]

    # Save the modified file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Modified {filepath}")
    return True

def main():
    print("=" * 60)
    print("题库分离工具 - 提取内嵌题库到独立文件")
    print("=" * 60)

    for grade, config in GRADES.items():
        print(f"\n处理 {grade}年级...")

        # Step 1: Extract questionData
        result = extract_question_data(config['index_path'], grade)
        if not result:
            continue

        json_str, start_pos, end_pos = result

        # Step 2: Create lessons.js file
        data_filename = config['data_path'].split('/')[-1]
        create_lessons_js(
            config['data_path'],
            config['var_name'],
            json_str,
            grade
        )

        # Step 3: Modify index.html
        modify_index_html(
            config['index_path'],
            grade,
            config['load_func'],
            config['var_name'],
            data_filename,
            start_pos,
            end_pos
        )

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
