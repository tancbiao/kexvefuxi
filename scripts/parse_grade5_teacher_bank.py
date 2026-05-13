#!/usr/bin/env python3
"""解析五年级教师版题库，生成 data/5-2.js 和 data/5-2-embedded.js"""

import re
import json

INPUT_FILE = r"C:\Users\tanc\Downloads\五年级下册知识点练习题（教师版）.txt"
OUTPUT_FILE = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\data\5-2.js"
EMBEDDED_OUTPUT = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\data\5-2-embedded.js"

UNIT_NAMES = {
    1: "身边的桥梁",
    2: "微观生命世界",
    3: "火山与地震",
    4: "地球运动与宇宙"
}

UNIT_CN = {
    1: '第一单元 身边的桥梁',
    2: '第二单元 微观生命世界',
    3: '第三单元 火山与地震',
    4: '第四单元 地球运动与宇宙'
}

UNIT_ICONS = {1: '🌉', 2: '🔬', 3: '🌋', 4: '🌍'}


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    lesson_blocks = re.split(r'(第(\d+)课\s+(.+?))\n', text)
    lessons_data = {}
    total_choices = 0
    total_tfs = 0

    for i in range(1, len(lesson_blocks), 4):
        lesson_num = int(lesson_blocks[i+1])
        lesson_name = lesson_blocks[i+2].strip()
        content = lesson_blocks[i+3] if i+3 < len(lesson_blocks) else ""

        choice_section = ""
        tf_section = ""
        choice_start = content.find("一、选择题")
        tf_start = content.find("二、判断题")

        if choice_start >= 0 and tf_start >= 0:
            choice_section = content[choice_start:tf_start]
            tf_section = content[tf_start:]
        elif choice_start >= 0:
            choice_section = content[choice_start:]

        choices = parse_choices(choice_section)
        tfs = parse_tf(tf_section)

        total_choices += len(choices)
        total_tfs += len(tfs)

        # 五年级教师版单元划分：1-6, 7-13, 14-16, 17-23
        if lesson_num <= 6:
            unit_num = 1
        elif lesson_num <= 13:
            unit_num = 2
        elif lesson_num <= 16:
            unit_num = 3
        else:
            unit_num = 4

        lessons_data[lesson_num] = {
            'name': lesson_name,
            'unit': unit_num,
            'choices': choices,
            'tfs': tfs
        }

    print(f"Parsed: {len(lessons_data)} lessons, {total_choices} choices, {total_tfs} TF = {total_choices+total_tfs} total")

    # Generate external JS (QUESTION_BANK_5_2 format)
    js = generate_external_js(lessons_data)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"External: {OUTPUT_FILE}")

    # Generate embedded JS (questionData format for HTML)
    embed = generate_embedded_js(lessons_data)
    with open(EMBEDDED_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(embed)
    print(f"Embedded: {EMBEDDED_OUTPUT}")


def parse_choices(text):
    questions = []
    if not text:
        return questions

    q_starts = list(re.finditer(r'^\d+\.\s+', text, re.MULTILINE))

    for idx, qm in enumerate(q_starts):
        start = qm.start()
        end = q_starts[idx+1].start() if idx+1 < len(q_starts) else len(text)
        block = text[start:end]

        ans_match = re.search(r'[（(]\s*([A-D])\s*[）)].*?★', block)
        if not ans_match:
            continue

        answer_idx = ord(ans_match.group(1)) - ord('A')

        first_line = block.split('\n')[0]
        q_clean = re.sub(r'\s*[（(]\s*[A-D]\s*[）)].*?★', '', first_line).strip()
        q_clean = re.sub(r'^\d+\.\s*', '', q_clean)

        all_opts = re.findall(r'[A-D]\.\s+(.+?)(?=\s+[A-D]\.|\s*【|$)', block)
        opts = [o.strip().rstrip('  ') for o in all_opts if o.strip()]

        hint = ''
        hint_match = re.search(r'【知识点】(.+?)(?:\n|$)', block)
        if hint_match:
            hint = hint_match.group(1).strip()

        questions.append({
            'type': 'choice',
            'q': q_clean,
            'opts': opts,
            'answer': answer_idx,
            'hint': hint
        })

    return questions


def parse_tf(text):
    questions = []
    if not text:
        return questions

    q_starts = list(re.finditer(r'^\d+\.\s+', text, re.MULTILINE))

    for idx, qm in enumerate(q_starts):
        start = qm.start()
        end = q_starts[idx+1].start() if idx+1 < len(q_starts) else len(text)
        block = text[start:end]

        ans_match = re.search(r'[（(]\s*([√×✓✗])\s*[）)].*?★', block)
        if not ans_match:
            continue

        answer = ans_match.group(1) in ('√', '✓')

        first_line = block.split('\n')[0]
        q_clean = re.sub(r'\s*[（(]\s*[√×✓✗]\s*[）)].*?★', '', first_line).strip()
        q_clean = re.sub(r'^\d+\.\s*', '', q_clean)

        hint = ''
        hint_match = re.search(r'【知识点】(.+?)(?:\n|$)', block)
        if hint_match:
            hint = hint_match.group(1).strip()

        questions.append({
            'type': 'tf',
            'q': q_clean,
            'answer': answer,
            'hint': hint
        })

    return questions


def generate_external_js(lessons_data):
    """Generate QUESTION_BANK_5_2 format for vs.html"""
    units = {}
    for lnum, ldata in lessons_data.items():
        u = ldata['unit']
        if u not in units:
            units[u] = {}
        units[u][lnum] = ldata

    lines = []
    lines.append("// 五年级下册科学题库（教师版）")
    lines.append("// 4个单元23课，每课10选择+5判断 = 345题")
    lines.append("// 更新：2026-04-23")
    lines.append("")
    lines.append("(function() {")
    lines.append("  window.QUESTION_BANK_5_2 = {")

    for unit_num in sorted(units.keys()):
        unit_lessons = units[unit_num]
        lines.append(f"    // =====================")
        lines.append(f"    // {UNIT_CN[unit_num]}")
        lines.append(f"    // =====================")
        lines.append(f"    {unit_num}: {{")
        lines.append(f"      name: '{UNIT_NAMES[unit_num]}',")
        lines.append(f"      icon: '{UNIT_ICONS[unit_num]}',")
        lines.append("      lessons: {")

        for lesson_num in sorted(unit_lessons.keys()):
            lesson = unit_lessons[lesson_num]
            choices = lesson['choices']
            tfs = lesson['tfs']

            basic = choices[:5] + tfs
            advance = choices[5:]

            def fmt_q(q):
                return json.dumps(q, ensure_ascii=False)

            lines.append(f"        {lesson_num}: {{")
            lines.append(f"          name: '{lesson['name']}',")

            basic_str = ',\n            '.join(fmt_q(q) for q in basic)
            lines.append(f"          basic: [")
            lines.append(f"            {basic_str}")
            lines.append(f"          ],")

            adv_str = ',\n            '.join(fmt_q(q) for q in advance)
            lines.append(f"          advance: [")
            lines.append(f"            {adv_str}")
            lines.append(f"          ]")
            lines.append(f"        }},")

        # vs精选
        vs_list = []
        for ln in sorted(unit_lessons.keys()):
            ch = unit_lessons[ln]['choices']
            if len(ch) >= 6:
                vs_list.append(ch[0])
                vs_list.append(ch[5])
            elif len(ch) >= 1:
                vs_list.append(ch[0])

        vs_str = ',\n        '.join(fmt_q(q) for q in vs_list)
        lines.append("      },")
        lines.append("      vs精选: [")
        lines.append("        " + vs_str)
        lines.append("      ]")
        lines.append("    },")

    lines.append("  };")
    lines.append("")
    lines.append("  window.VS_LIST_5_2 = function() {")
    lines.append("    const bank = window.QUESTION_BANK_5_2;")
    lines.append("    const q = [];")
    lines.append("    for (let unit = 1; unit <= 4; unit++) {")
    lines.append("      q.push(...bank[unit].vs精选);")
    lines.append("    }")
    lines.append("    return q.sort(() => Math.random() - 0.5);")
    lines.append("  };")
    lines.append("")
    lines.append("})();")

    return '\n'.join(lines)


def generate_embedded_js(lessons_data):
    """Generate questionData format for 5/2/index.html"""
    units = {}
    for lnum, ldata in lessons_data.items():
        u = ldata['unit']
        if u not in units:
            units[u] = {}
        units[u][lnum] = ldata

    UNIT_KEYS = ['unit1', 'unit2', 'unit3', 'unit4']

    lines = []
    lines.append("// ========== 五年级题库 - 按单元和课程（教师版 2026-04-23） ==========")
    lines.append("const questionData = {")

    for unit_num in sorted(units.keys()):
        ukey = UNIT_KEYS[unit_num - 1]
        unit_lessons = units[unit_num]

        lines.append(f"  {ukey}: {{")
        lines.append(f"    name: '{UNIT_CN[unit_num]}',")
        lines.append(f"    icon: '{UNIT_ICONS[unit_num]}',")
        lines.append("    lessons: [")

        for lesson_num in sorted(unit_lessons.keys()):
            lesson = unit_lessons[lesson_num]
            choices = lesson['choices']
            tfs = lesson['tfs']

            basic = []
            medium = []

            for i, c in enumerate(choices):
                q = {'q': c['q'], 'options': c['opts'], 'answer': c['answer'], 'hint': c['hint']}
                if i < 5:
                    basic.append(q)
                else:
                    medium.append(q)

            for i, t in enumerate(tfs):
                q = {'q': t['q'], 'options': ['√', '×'], 'answer': 0 if t['answer'] else 1, 'hint': t['hint']}
                if i < 3:
                    basic.append(q)
                else:
                    medium.append(q)

            def fmt(q):
                return json.dumps(q, ensure_ascii=False)

            lesson_id = f"u{unit_num}l{lesson_num}"
            lines.append(f"      {{ id: '{lesson_id}', name: '{lesson['name']}', icon: '📚',")

            basic_str = ',\n          '.join(fmt(q) for q in basic)
            lines.append(f"        basic: [")
            lines.append(f"          {basic_str}")
            lines.append(f"        ],")

            med_str = ',\n          '.join(fmt(q) for q in medium)
            lines.append(f"        medium: [")
            lines.append(f"          {med_str}")
            lines.append(f"        ],")

            lines.append(f"        hard: [],")
            lines.append(f"      }},")

        lines.append("    ],")
        lines.append("  },")

    lines.append("};")

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
