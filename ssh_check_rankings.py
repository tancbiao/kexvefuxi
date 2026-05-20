import paramiko
import json

host = "159.75.134.151"
port = 22
username = "root"
password = "sC,/{8v*!b9EQ2$"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, username, password)

sftp = client.open_sftp()

# Read rankings data
with sftp.open("/data/kexvefuxi/rankings_grade_all.json", "rb") as f:
    rankings = json.loads(f.read().decode('utf-8'))

# Read students data
with sftp.open("/data/kexvefuxi/students.json", "rb") as f:
    students = json.loads(f.read().decode('utf-8'))

print(f"=== Rankings: {len(rankings)} entries ===")
# Show top 10 by totalPoints
sorted_r = sorted(rankings.items(), key=lambda x: x[1].get('totalPoints', 0) or 0, reverse=True)
print("Top 10 ranking entries:")
for sid, data in sorted_r[:10]:
    pts = data.get('totalPoints', 0) or 0
    floor = data.get('towerFloor', data.get('towerHighestFloor', 0)) or 0
    ladder = data.get('ladderScore', 0) or 0
    print(f"  {sid}: points={pts}, floor={floor}, ladder={ladder}")

print(f"\n=== Students: {len(students)} entries ===")
sorted_s = sorted(students.items(), key=lambda x: x[1].get('totalPoints', 0) or 0, reverse=True)
print("Top 10 student entries:")
for sid, data in sorted_s[:10]:
    pts = data.get('totalPoints', 0) or 0
    eq_count = len([e for e in data.get('equipment', []) if e])
    print(f"  {sid}: points={pts}, equipments={eq_count}")

# Also check total correct answers in students
print("\nTop 5 by accuracy/question count:")
for sid, data in sorted_s[:5]:
    qa = data.get('totalQuestionsAnswered', 0) or 0
    ca = data.get('totalCorrectAnswers', 0) or 0
    print(f"  {sid}: answered={qa}, correct={ca}")

sftp.close()
client.close()
