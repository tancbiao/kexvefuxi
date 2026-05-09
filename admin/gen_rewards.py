import json
import random
import time
import datetime

# 神话宠物列表（最高稀有度）
pets = [
    {'id': 'pet_dragon', 'name': '神龙宝宝', 'rarity': 'mythical'},
    {'id': 'pet_phoenix', 'name': '凤凰雏鸟', 'rarity': 'mythical'},
    {'id': 'pet_qilin', 'name': '麒麟幼崽', 'rarity': 'mythical'},
    {'id': 'pet_white_tiger', 'name': '白虎幼崽', 'rarity': 'mythical'},
    {'id': 'pet_black_tortoise', 'name': '玄武幼崽', 'rarity': 'mythical'}
]

students = []
for i in range(1, 51):
    student_id = f"012102{str(i).zfill(2)}"
    pt = random.choice(pets)
    students.append({
        'studentId': student_id,
        'rewards': [{'type': 'pet', 'id': pt['id']}]
    })
    print(f"{student_id} -> {pt['name']}")

data = {
    'batchId': 'BATCH_MYTH_PETS_' + str(int(time.time())),
    'batchName': '神话宠物发放',
    'createdAt': datetime.datetime.now().isoformat(),
    'students': students
}

output_path = 'c:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/admin/rewards.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n已生成 {len(students)} 个学生的奖励数据 -> {output_path}')
