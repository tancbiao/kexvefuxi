"""
生成瑞文推理测验题库数据 v2（轻量版，仅元数据+答案）
图片文件存储在 data/xuanba-images/ 目录
"""
import os
import json

output_dir = "D:/kexvefuxi/data/xuanba-images"
image_base = "data/xuanba-images"

groups = ["A", "B", "C", "D", "E"]
options_per_group = {"A": 6, "B": 6, "C": 8, "D": 8, "E": 8}

# Standard SPM answer key (1-indexed)
answer_key = {
    "A1": 4, "A2": 5, "A3": 1, "A4": 2, "A5": 6, "A6": 3,
    "A7": 6, "A8": 2, "A9": 1, "A10": 3, "A11": 4, "A12": 5,
    "B1": 2, "B2": 6, "B3": 1, "B4": 2, "B5": 1, "B6": 3,
    "B7": 5, "B8": 6, "B9": 4, "B10": 3, "B11": 4, "B12": 5,
    "C1": 8, "C2": 2, "C3": 3, "C4": 8, "C5": 7, "C6": 4,
    "C7": 5, "C8": 1, "C9": 7, "C10": 6, "C11": 1, "C12": 2,
    "D1": 3, "D2": 4, "D3": 3, "D4": 7, "D5": 8, "D6": 6,
    "D7": 5, "D8": 4, "D9": 1, "D10": 2, "D11": 5, "D12": 6,
    "E1": 7, "E2": 6, "E3": 8, "E4": 2, "E5": 1, "E6": 5,
    "E7": 4, "E8": 6, "E9": 3, "E10": 2, "E11": 4, "E12": 5,
}

questions = []
qid = 1
for group in groups:
    for qnum in range(1, 13):
        n_opts = options_per_group[group]
        key = f"{group}{qnum}"
        correct_idx = answer_key.get(key, 0) - 1

        # Verify images exist
        main_file = os.path.join(output_dir, f"{group}{qnum}.png")
        if not os.path.exists(main_file):
            print(f"WARNING: Missing {main_file}")
            continue

        options = []
        for opt in range(1, n_opts + 1):
            opt_file = os.path.join(output_dir, f"{group}{qnum}_{opt:02d}.png")
            if os.path.exists(opt_file):
                options.append(f"{image_base}/{group}{qnum}_{opt:02d}.png")
            else:
                print(f"WARNING: Missing option {opt_file}")
                options.append("")

        questions.append({
            "id": qid,
            "group": group,
            "num": qnum,
            "matrix": f"{image_base}/{group}{qnum}.png",
            "options": options,
            "correct": correct_idx,
            "optionCount": n_opts
        })
        qid += 1

# Write metadata JS
output_js = "// xuanba-questions-v2.js — 瑞文标准推理测验题库（60题）\n"
output_js += "// 图片: data/xuanba-images/ (492 PNG files)\n"
output_js += f"// 题量: {len(questions)}题，A-E各12题\n"
output_js += "var XUANBA_QUESTIONS = " + json.dumps(questions, ensure_ascii=False, indent=2) + ";\n"

js_path = "D:/kexvefuxi/data/xuanba-questions-v2.js"
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(output_js)

print(f"Generated {len(questions)} questions")
print(f"JS file size: {os.path.getsize(js_path) / 1024:.1f} KB")
print(f"Written to: {js_path}")
