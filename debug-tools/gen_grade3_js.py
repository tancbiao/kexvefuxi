# -*- coding: utf-8 -*-
import sys, re, json, shutil, os
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

BASE = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi'

doc = Document(r'C:\Users\tanc\Desktop\三年级下册题库.docx')
lines = []
for p in doc.paragraphs:
    text = p.text.strip()
    if text:
        for sub in text.split('\n'):
            s = sub.strip()
            if s:
                lines.append(s)

def split_inline_options(text):
    parts = re.split(r'\s+(?=[A-D][\.．、])', text)
    question, options = '', []
    for p in parts:
        if re.match(r'^[A-D][\.．、]', p):
            options.append(p)
        else:
            question += p
    return question.strip(), options

def parse_all(lines):
    lessons = []
    i = 0; n = len(lines)
    while i < n:
        m = re.match(r'^第(\d+)课[：:]\s*(.*)', lines[i])
        if not m: i += 1; continue
        lesson_num = int(m.group(1))
        lesson_name = m.group(2).strip().rstrip('。')
        i += 1
        while i < n and '选择题' not in lines[i]:
            if re.match(r'^[A-D][\.．、]', lines[i]): break
            i += 1
        if i < n and '选择题' in lines[i]: i += 1
        choices = []
        for _ in range(10):
            if i >= n: break
            if '二、判断题' in lines[i] or re.match(r'^第\d+课[：:]', lines[i]): break
            q_text, opts = '', []
            line = lines[i]; i += 1
            if re.search(r'[A-D][\.．、]', line):
                q_text, opts = split_inline_options(line)
            else:
                q_text = line
            while i < n and re.match(r'^[A-D][\.．、]', lines[i]):
                opt_line = lines[i]; i += 1
                if re.search(r'[A-D][\.．、].*[A-D][\.．、]', opt_line):
                    _, sub_opts = split_inline_options(opt_line)
                    opts.extend(sub_opts)
                else:
                    opts.append(opt_line)
                if len(opts) >= 6: break
            if not opts and i < n and '二、判断题' not in lines[i] and not re.match(r'^第\d+课', lines[i]):
                if re.match(r'^[①②③④]', lines[i]):
                    sub_items = lines[i]; i += 1
                    while i < n and re.match(r'^[A-D][\.．、]', lines[i]):
                        opts.append(lines[i]); i += 1
                        if len(opts) >= 6: break
                    if not opts: q_text = q_text + ' ' + sub_items
            choices.append({'question': q_text, 'options': opts})
        while i < n and '二、判断题' not in lines[i]:
            if re.match(r'^第\d+课答案', lines[i]): break
            i += 1
        if i < n and '二、判断题' in lines[i]: i += 1
        tfs = []
        for _ in range(5):
            if i >= n: break
            if re.match(r'^第\d+课答案', lines[i]): break
            tfs.append({'question': re.sub(r'（\s*）\s*$', '', lines[i]).strip()})
            i += 1
        ans_c, ans_t = '', ''
        if i < n and re.match(r'^第\d+课答案', lines[i]):
            i += 1
            if i < n and lines[i].startswith('一、'):
                ans_c = re.sub(r'^一、', '', lines[i]).strip(); i += 1
            if i < n and lines[i].startswith('二、'):
                ans_t = re.sub(r'^二、', '', lines[i]).strip(); i += 1
        # 提取答案中只有字母的部分（去掉 '1-5' '6-10' 等编号）
        cl = re.sub(r'[^A-D]', '', ans_c)
        for j, c in enumerate(choices):
            if j < len(cl): c['answer'] = {'A':0,'B':1,'C':2,'D':3}.get(cl[j], 0)
            else: c['answer'] = 0
        tc = ans_t.replace(' ', '')
        for j, t in enumerate(tfs):
            t['answer'] = (tc[j] == '√') if j < len(tc) else False
        lessons.append({'num': lesson_num, 'name': lesson_name, 'choices': choices, 'tfs': tfs})
    return lessons

lessons = parse_all(lines)

# ── 单元配置 ──
unit_map = {
    1: {'name': '认识动物', 'icon': '🦁', 'range': (1, 7)},
    2: {'name': '食物与健康', 'icon': '🍎', 'range': (8, 11)},
    3: {'name': '水与溶解', 'icon': '💧', 'range': (12, 16)},
    4: {'name': '天气与气候', 'icon': '🌤️', 'range': (17, 24)}
}

# ── 生成 JS（完全模仿 5-2.js 格式）──
def build_js(lessons, unit_map):
    out = []
    out.append('// 三年级下册科学题库（教师版）')
    out.append('// 粤教粤科版 4个单元24课，每课10选择+5判断 = 360题')
    out.append('// 生成时间：2026-05-05')
    out.append('')
    out.append('(function() {')
    out.append("  'use strict';")
    out.append('  window.QUESTION_BANK_3_2 = {')
    out.append('')

    for uid in sorted(unit_map.keys()):
        u = unit_map[uid]
        start, end = u['range']
        ul = [l for l in lessons if start <= l['num'] <= end]

        out.append(f"    // =====================")
        out.append(f"    // 单元{uid} {u['name']}")
        out.append(f"    // =====================")
        out.append(f"    {uid}: {{")
        out.append(f"      name: '{u['name']}',")
        out.append(f"      icon: '{u['icon']}',")
        out.append(f"      lessons: {{")

        for lesson in ul:
            ln = lesson['num']
            display_name = re.sub(r'^[（(]\d+[\.\d]+[）)]\s*', '', lesson['name'])

            basic = []
            advance = []
            for idx, q in enumerate(lesson['choices']):
                item = {
                    'type': 'choice',
                    'q': q['question'],
                    'opts': q['options'],
                    'answer': q['answer'],
                    'hint': '注意关键词，仔细分析'
                }
                if idx < 5: basic.append(item)
                else: advance.append(item)
            for idx, t in enumerate(lesson['tfs']):
                item = {
                    'type': 'tf',
                    'q': t['question'],
                    'answer': t['answer'],
                    'hint': '回忆课本相关内容'
                }
                if idx < 3: basic.append(item)
                else: advance.append(item)

            out.append(f"        {ln}: {{")
            out.append(f"          name: '{display_name}',")
            out.append(f"          basic: {json.dumps(basic, ensure_ascii=False, indent=10).strip()},")
            out.append(f"          advance: {json.dumps(advance, ensure_ascii=False, indent=10).strip()}")
            out.append(f"        }},")

        out.append("      }")
        out.append("    },")

    out.append("  };")
    out.append("})();")
    return '\n'.join(out)

js = build_js(lessons, unit_map)
out_path = os.path.join(BASE, 'data', '3-2.js')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(js)
print(f'[OK] Generated: {out_path}')

# ── 复制并修改网页 ──
src = os.path.join(BASE, '5', '2', 'index.html')
dst_dir = os.path.join(BASE, '3', '2')
dst = os.path.join(dst_dir, 'index.html')
os.makedirs(dst_dir, exist_ok=True)
shutil.copy2(src, dst)
with open(dst, 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('QUESTION_BANK_5_2', 'QUESTION_BANK_3_2')
html = html.replace('5-2.js', '3-2.js')
html = html.replace('五年级', '三年级')
with open(dst, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] Created: {dst}')

# ── 更新首页：解锁三年级 ──
idx_path = os.path.join(BASE, 'index.html')
with open(idx_path, 'r', encoding='utf-8') as f:
    idx_html = f.read()
# 替换三级的 locked 状态
import re
idx_html = re.sub(r'panel-3[^"]*"[^>]*locked[^"]*"[^>]*', 'panel-3" onclick="goGrade(3,2)"', idx_html)
idx_html = idx_html.replace('施工中', '✅ 已上线')
with open(idx_path, 'w', encoding='utf-8') as f:
    f.write(idx_html)
print(f'[OK] Updated: {idx_path}')

print(f'\n✅ 完成！共 {len(lessons)} 课，{sum(len(l["choices"]) for l in lessons)} 选择题，{sum(len(l["tfs"]) for l in lessons)} 判断题')
