"""
下载瑞文推理测验题目图片 (从 iq.szzxsw.cn)
60题: A, B, C, D, E 各12题
"""
import urllib.request
import os
import time

base_url = "http://iq.szzxsw.cn/images/png/"
output_dir = "D:/kexvefuxi/data/xuanba-images"
os.makedirs(output_dir, exist_ok=True)

# Groups: A, B, C, D, E (skip AB for now)
groups = ["A", "B", "C", "D", "E"]
# Options per group: A & B have 6, C/D/E have 8
options_per_group = {"A": 6, "B": 6, "C": 8, "D": 8, "E": 8}

# Standard SPM answer key
answer_key = {
    # Set A (6 options)
    "A1": 4, "A2": 5, "A3": 1, "A4": 2, "A5": 6, "A6": 3,
    "A7": 6, "A8": 2, "A9": 1, "A10": 3, "A11": 4, "A12": 5,
    # Set B (6 options)
    "B1": 2, "B2": 6, "B3": 1, "B4": 2, "B5": 1, "B6": 3,
    "B7": 5, "B8": 6, "B9": 4, "B10": 3, "B11": 4, "B12": 5,
    # Set C (8 options)
    "C1": 8, "C2": 2, "C3": 3, "C4": 8, "C5": 7, "C6": 4,
    "C7": 5, "C8": 1, "C9": 7, "C10": 6, "C11": 1, "C12": 2,
    # Set D (8 options)
    "D1": 3, "D2": 4, "D3": 3, "D4": 7, "D5": 8, "D6": 6,
    "D7": 5, "D8": 4, "D9": 1, "D10": 2, "D11": 5, "D12": 6,
    # Set E (8 options)
    "E1": 7, "E2": 6, "E3": 8, "E4": 2, "E5": 1, "E6": 5,
    "E7": 4, "E8": 6, "E9": 3, "E10": 2, "E11": 4, "E12": 5,
}

total = 0
success = 0
failed = []

for group in groups:
    n_opts = options_per_group[group]
    for qnum in range(1, 13):
        # Download main image
        main_name = f"{group}{qnum}.png"
        main_url = base_url + main_name
        main_path = os.path.join(output_dir, main_name)
        
        try:
            urllib.request.urlretrieve(main_url, main_path)
            total += 1
            success += 1
            print(f"OK  {main_name}")
        except Exception as e:
            print(f"FAIL {main_name}: {e}")
            failed.append(main_name)
        
        # Download option images
        for opt in range(1, n_opts + 1):
            opt_name = f"{group}{qnum}_{opt:02d}.png"
            opt_url = base_url + opt_name
            opt_path = os.path.join(output_dir, opt_name)
            
            try:
                urllib.request.urlretrieve(opt_url, opt_path)
                total += 1
                success += 1
            except Exception as e:
                print(f"FAIL {opt_name}: {e}")
                failed.append(opt_name)
        
        time.sleep(0.05)  # Be polite to the server

print(f"\n=== Download Complete ===")
print(f"Total: {total}, Success: {success}, Failed: {len(failed)}")
if failed:
    print(f"Failed files: {failed}")

# Generate question data JS
import base64
import json

questions = []
qid = 1
for group in groups:
    for qnum in range(1, 13):
        n_opts = options_per_group[group]
        key = f"{group}{qnum}"
        correct_idx = answer_key.get(key, 0) - 1  # 0-indexed
        
        # Read main image and encode as base64
        main_file = os.path.join(output_dir, f"{group}{qnum}.png")
        main_b64 = ""
        if os.path.exists(main_file):
            with open(main_file, 'rb') as f:
                main_b64 = base64.b64encode(f.read()).decode()
        
        # Read option images
        options = []
        for opt in range(1, n_opts + 1):
            opt_file = os.path.join(output_dir, f"{group}{qnum}_{opt:02d}.png")
            if os.path.exists(opt_file):
                with open(opt_file, 'rb') as f:
                    options.append(base64.b64encode(f.read()).decode())
            else:
                options.append("")
        
        questions.append({
            "id": qid,
            "group": group,
            "num": qnum,
            "matrix_b64": main_b64,
            "options_b64": options,
            "correct": correct_idx,
            "optionCount": n_opts
        })
        qid += 1

# Write question data as JS
output_js = "// xuanba-questions-v2.js — 瑞文标准推理测验题库（60题，图片取自公开资源）\n"
output_js += "// 仅供学校课堂教学使用\n"
output_js += f"// 题量: {len(questions)}题，5组各12题\n"
output_js += "// 格式: base64 编码的 PNG 图片\n"
output_js += "var XUANBA_QUESTIONS = " + json.dumps(questions, ensure_ascii=False) + ";\n"

js_path = "D:/kexvefuxi/data/xuanba-questions-v2.js"
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(output_js)
print(f"\nQuestion data written to: {js_path}")
print(f"Questions: {len(questions)}")

# Report file sizes
total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir) if f.endswith('.png'))
print(f"Total image size: {total_size / 1024 / 1024:.1f} MB")
js_size = os.path.getsize(js_path)
print(f"Base64 JS size: {js_size / 1024 / 1024:.1f} MB")
