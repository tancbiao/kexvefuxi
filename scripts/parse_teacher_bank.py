#!/usr/bin/env python3
"""
解析教师版题库文本，生成 4-2.js 数据文件
"""

import re
import json

INPUT_FILE = r"C:\Users\tanc\Downloads\四年级下册知识点练习题（教师版）.txt"
OUTPUT_FILE = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\data\4-2.js"

UNIT_NAMES = {
    1: "植物大观园",
    2: "动物的需求",
    3: "运动与力",
    4: "地球上看到的光和影"
}

LESSON_NAMES = {
    1: "白兰和银杏", 2: "月季和茉莉", 3: "凤仙花和狗尾草", 4: "葡萄和爬墙虎",
    5: "睡莲和荷花", 6: "校园里的植物", 7: "网上学习：有趣的植物",
    8: "动物需要空气", 9: "动物需要水分", 10: "动物需要食物",
    11: "动物行为", 12: "动物的巢穴", 13: "帮鸟儿建个家",
    14: "车动了吗", 15: "物体的运动方式", 16: "运动的快与慢",
    17: "风帆小车", 18: "运动与摩擦力", 19: "运动的物体有能量",
    20: "哪里有影子", 21: "阳光下的影子", 22: "明亮的月光", 23: "变化的月相"
}


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    # 按 "第X课" 分割整个文本
    lesson_blocks = re.split(r'(第(\d+)课\s+(.+?))\n', text)
    # lesson_blocks: [preamble, header, num, name, content, header, num, name, content, ...]
    
    lessons_data = {}
    total_choices = 0
    total_tfs = 0
    
    for i in range(1, len(lesson_blocks), 4):
        lesson_num = int(lesson_blocks[i+1])
        lesson_name = lesson_blocks[i+2].strip()
        content = lesson_blocks[i+3] if i+3 < len(lesson_blocks) else ""
        
        # 提取选择题区域
        choice_section = ""
        tf_section = ""
        
        choice_start = content.find("一、选择题")
        tf_start = content.find("二、判断题")
        
        if choice_start >= 0 and tf_start >= 0:
            choice_section = content[choice_start:tf_start]
            tf_section = content[tf_start:]
        elif choice_start >= 0:
            choice_section = content[choice_start:]
        
        # 解析选择题
        choices = parse_choices(choice_section)
        tfs = parse_tf(tf_section)
        
        total_choices += len(choices)
        total_tfs += len(tfs)
        
        # 确定单元号
        if lesson_num <= 7:
            unit_num = 1
        elif lesson_num <= 13:
            unit_num = 2
        elif lesson_num <= 19:
            unit_num = 3
        else:
            unit_num = 4
        
        lessons_data[lesson_num] = {
            'name': LESSON_NAMES.get(lesson_num, lesson_name),
            'unit': unit_num,
            'choices': choices,
            'tfs': tfs
        }
    
    print(f"解析完成：")
    print(f"  课程数: {len(lessons_data)}")
    print(f"  选择题: {total_choices}")
    print(f"  判断题: {total_tfs}")
    print(f"  总题数: {total_choices + total_tfs}")
    
    # 生成 JS
    js = generate_js(lessons_data)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"\n已生成: {OUTPUT_FILE}")


def parse_choices(text):
    """解析选择题"""
    questions = []
    if not text:
        return questions
    
    # 按题号分割：匹配 "数字. 题干（ 答案 ）★"
    # 先找到所有题目的起始位置
    q_starts = list(re.finditer(r'^\d+\.\s+', text, re.MULTILINE))
    
    for idx, qm in enumerate(q_starts):
        start = qm.start()
        end = q_starts[idx+1].start() if idx+1 < len(q_starts) else len(text)
        block = text[start:end]
        
        # 提取答案（支持多种格式：★（ B ）, （ B ）★, （ B ）。★, （ B ）。★ 等）
        ans_match = re.search(r'[（(]\s*([A-D])\s*[）)].*?★', block)
        if not ans_match:
            continue
        
        answer_idx = ord(ans_match.group(1)) - ord('A')
        
        # 提取题干（第一行）
        first_line = block.split('\n')[0]
        q_clean = re.sub(r'\s*[（(]\s*[A-D]\s*[）)].*?★', '', first_line).strip()
        # 去掉开头的题号
        q_clean = re.sub(r'^\d+\.\s*', '', q_clean)
        
        # 提取选项（可能在同一行用空格分隔，或不同行）
        opts = []
        # 在整个 block 中寻找选项（排除题干行的答案标记）
        opt_block = '\n'.join(block.split('\n')[1:])  # 去掉题干行
        # 选项格式: A. xxx  B. xxx  C. xxx  D. xxx (同一行或多行)
        opt_matches = re.findall(r'([A-D])\.\s+(\S+(?:\s+(?![A-D]\.)\S+)*)', opt_block)
        # 但这可能匹配过多，换一种方法：按 A. B. C. D. 切分
        # 更简单：直接在整个block找所有选项
        all_opts = re.findall(r'[A-D]\.\s+(.+?)(?=\s+[A-D]\.|\s*【|$)', block)
        opts = [o.strip().rstrip('  ') for o in all_opts if o.strip()]
        
        # 提取知识点
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
    """解析判断题"""
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


def generate_js(lessons_data):
    """生成 JS"""
    # 按单元分组
    units = {}
    for lnum, ldata in lessons_data.items():
        u = ldata['unit']
        if u not in units:
            units[u] = {}
        units[u][lnum] = ldata
    
    lines = []
    lines.append("// 四年级下册科学题库（教师版）")
    lines.append("// 来源：教师版题库 - 4个单元23课，每课10选择+5判断")
    lines.append("// 更新：2026-04-23")
    lines.append("")
    lines.append("(function() {")
    lines.append("  window.QUESTION_BANK_4_2 = {")
    
    for unit_num in sorted(units.keys()):
        unit_lessons = units[unit_num]
        lines.append(f"    // =====================")
        lines.append(f"    // 单元{unit_num}：{UNIT_NAMES[unit_num]}")
        lines.append(f"    // =====================")
        lines.append(f"    {unit_num}: {{")
        lines.append(f"      name: '{UNIT_NAMES[unit_num]}',")
        lines.append("      lessons: {")
        
        for lesson_num in sorted(unit_lessons.keys()):
            lesson = unit_lessons[lesson_num]
            choices = lesson['choices']
            tfs = lesson['tfs']
            
            basic = choices[:5] + tfs  # 前5选择 + 全部判断
            advance = choices[5:]       # 后5选择
            
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
        
        # vs精选：每课2题
        vs_list = []
        for lesson_num in sorted(unit_lessons.keys()):
            ch = unit_lessons[lesson_num]['choices']
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
    lines.append("  // 竞赛精选题")
    lines.append("  window.VS_LIST_4_2 = function() {")
    lines.append("    const bank = window.QUESTION_BANK_4_2;")
    lines.append("    const q = [];")
    lines.append("    for (let unit = 1; unit <= 4; unit++) {")
    lines.append("      q.push(...bank[unit].vs精选);")
    lines.append("    }")
    lines.append("    return q.sort(() => Math.random() - 0.5);")
    lines.append("  };")
    lines.append("")
    lines.append("})();")
    
    return '\n'.join(lines)


def generate_embedded_js(lessons_data, output_path):
    """生成内嵌在 HTML 中的 questionData 格式"""
    # 按单元分组
    units = {}
    for lnum, ldata in lessons_data.items():
        u = ldata['unit']
        if u not in units:
            units[u] = {}
        units[u][lnum] = ldata
    
    UNIT_KEYS = ['unit1', 'unit2', 'unit3', 'unit4']
    UNIT_CN = {
        1: '第一单元 植物大观园',
        2: '第二单元 动物的需求',
        3: '第三单元 运动与力',
        4: '第四单元 地球上看到的光和影'
    }
    UNIT_ICONS = {1: '🌿', 2: '🐾', 3: '🚀', 4: '🌙'}
    
    lines = []
    lines.append("// ========== 题库 - 按单元和课程（教师版 2026-04-23） ==========")
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
            
            # 分配难度：
            # basic: 前5选择题 + 前3判断题
            # medium: 后5选择题 + 后2判断题
            # hard: (当前没有，全放空或者加一些判断)
            basic = []
            medium = []
            
            for i, c in enumerate(choices):
                q = {
                    'q': c['q'],
                    'options': c['opts'],
                    'answer': c['answer'],
                    'hint': c['hint']
                }
                if i < 5:
                    basic.append(q)
                else:
                    medium.append(q)
            
            for i, t in enumerate(tfs):
                q = {
                    'q': t['q'],
                    'options': ['√', '×'],
                    'answer': 0 if t['answer'] else 1,
                    'hint': t['hint']
                }
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
    
    js = '\n'.join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"内嵌题库已生成: {output_path}")


if __name__ == '__main__':
    main()
    # Also generate embedded format
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lesson_blocks = re.split(r'(第(\d+)课\s+(.+?))\n', text)
    lessons_data = {}
    
    for i in range(1, len(lesson_blocks), 4):
        lesson_num = int(lesson_blocks[i+1])
        lesson_name = lesson_blocks[i+2].strip()
        content = lesson_blocks[i+3] if i+3 < len(lesson_blocks) else ""
        
        choice_start = content.find("一、选择题")
        tf_start = content.find("二、判断题")
        
        choice_section = content[choice_start:tf_start] if choice_start >= 0 and tf_start >= 0 else (content[choice_start:] if choice_start >= 0 else "")
        tf_section = content[tf_start:] if tf_start >= 0 else ""
        
        choices = parse_choices(choice_section)
        tfs = parse_tf(tf_section)
        
        if lesson_num <= 7: unit_num = 1
        elif lesson_num <= 13: unit_num = 2
        elif lesson_num <= 19: unit_num = 3
        else: unit_num = 4
        
        lessons_data[lesson_num] = {
            'name': LESSON_NAMES.get(lesson_num, lesson_name),
            'unit': unit_num,
            'choices': choices,
            'tfs': tfs
        }
    
    EMBEDDED_OUTPUT = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\data\4-2-embedded.js"
    generate_embedded_js(lessons_data, EMBEDDED_OUTPUT)
