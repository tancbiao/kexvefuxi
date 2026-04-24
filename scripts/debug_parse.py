import re
text = open(r'C:\Users\tanc\Downloads\四年级下册知识点练习题（教师版）.txt', 'r', encoding='utf-8').read()

# Check each lesson for missing choices
lesson_blocks = re.split(r'(第(\d+)课\s+(.+?))\n', text)

for i in range(1, len(lesson_blocks), 4):
    lesson_num = int(lesson_blocks[i+1])
    content = lesson_blocks[i+3] if i+3 < len(lesson_blocks) else ""
    
    choice_start = content.find("一、选择题")
    tf_start = content.find("二、判断题")
    
    if choice_start < 0:
        print(f"Lesson {lesson_num}: NO CHOICE SECTION")
        continue
    
    choice_section = content[choice_start:tf_start] if tf_start > 0 else content[choice_start:]
    
    q_starts = list(re.finditer(r'^\d+\.\s+', choice_section, re.MULTILINE))
    total = len(q_starts)
    
    matched = 0
    missed = 0
    for idx2, qm in enumerate(q_starts):
        start = qm.start()
        end = q_starts[idx2+1].start() if idx2+1 < len(q_starts) else len(choice_section)
        b = choice_section[start:end]
        ans = re.search(r'[（(]\s*([A-D])\s*[）)]\s*\.?\s*★', b)
        if ans:
            matched += 1
        else:
            missed += 1
            first_line = b.split('\n')[0][:80]
            print(f"  Lesson {lesson_num} MISSED q{idx2+1}: {first_line}")
    
    print(f"Lesson {lesson_num}: total={total}, matched={matched}, missed={missed}")
