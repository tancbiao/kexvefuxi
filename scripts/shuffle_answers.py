# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
打乱题库选项顺序脚本
- 打乱 A/B/C/D 选项顺序
- 更新 answer 索引
- 跳过包含"以上都"的题目
- 跳过判断题(tf)
"""
import re
import random
import os

def fisher_yates_shuffle(arr):
    """原地洗牌"""
    a = list(arr)
    for i in range(len(a) - 1, 0, -1):
        j = random.randint(0, i)
        a[i], a[j] = a[j], a[i]
    return a

def process_file(filepath):
    print(f"\n处理文件: {os.path.basename(filepath)}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total = 0
    shuffled = 0
    skipped = 0
    result = content
    offset = 0  # 记录因替换导致的位置偏移

    # 遍历所有 choice 题
    # 匹配 {"type": "choice", ... } 对象
    pattern = re.compile(
        r'\{"type": "choice", "q": "([^"]*)", "opts": \[([^\]]+)\], "answer": (\d+), "hint": "([^"]*)"\}',
        re.DOTALL
    )

    matches = list(pattern.finditer(content))
    # 逆序处理（从后往前替换，避免索引偏移问题）
    for m in reversed(matches):
        q_text = m.group(1)
        opts_str = m.group(2)
        answer_idx = int(m.group(3))
        hint = m.group(4)

        # 解析选项数组
        opts = re.findall(r'"([^"]*)"', opts_str)

        total += 1

        # 判断是否跳过
        if answer_idx >= len(opts):
            continue
        correct_text = opts[answer_idx]
        if '以上都' in correct_text or '以上各' in correct_text:
            skipped += 1
            continue

        # 打乱
        indexed = [(t, i) for i, t in enumerate(opts)]
        shuffled_idx = fisher_yates_shuffle(indexed)
        new_opts = [t for t, _ in shuffled_idx]
        new_answer = next(i for t, i in shuffled_idx if t == correct_text)

        # 构建新对象字符串（保持原有格式风格）
        new_opts_str = ', '.join(f'"{o}"' for o in new_opts)
        new_obj = f'{{"type": "choice", "q": "{q_text}", "opts": [{new_opts_str}], "answer": {new_answer}, "hint": "{hint}"}}'

        # 替换原文
        start, end = m.start(), m.end()
        result = result[:start] + new_obj + result[end:]
        shuffled += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"  ✅ 完成！共{total}选择题，打乱{shuffled}题，跳过{skipped}题")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    files = ['4-2.js', '5-2.js', '6-2.js']

    for fname in files:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            process_file(fpath)
        else:
            print(f"文件不存在: {fpath}")

    print("\n🎉 全部处理完成！记得 git 提交推送。")

if __name__ == '__main__':
    main()
