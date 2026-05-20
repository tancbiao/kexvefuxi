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

# List all JSON files in data directory
stdin, stdout, stderr = client.exec_command("ls -la /data/kexvefuxi/*.json 2>/dev/null")
print("=== All JSON files ===")
print(stdout.read().decode())

# Check each rankings file
for grade in ['grade_3', 'grade_4', 'grade_5', 'grade_6', 'grade_all']:
    path = f'/data/kexvefuxi/rankings_{grade}.json'
    try:
        with sftp.open(path, "rb") as f:
            data = json.loads(f.read().decode('utf-8'))
            if isinstance(data, dict):
                entries = len(data)
                sorted_items = sorted(data.items(), key=lambda x: x[1].get('totalPoints', 0) or 0, reverse=True)[:5]
                print(f"\n=== rankings_{grade}.json: {entries} entries ===")
                for sid, d in sorted_items[:5]:
                    print(f"  {sid}: pts={d.get('totalPoints',0)}, floor={d.get('towerFloor',0)}, ladder={d.get('ladderScore',0)}")
            else:
                print(f"\n=== rankings_{grade}.json: not a dict (type={type(data).__name__}, len={len(data) if hasattr(data,'__len__') else 'N/A'}) ===")
    except FileNotFoundError:
        print(f"\n=== rankings_{grade}.json: NOT FOUND ===")

# Check students per grade
for grade in ['grade_3', 'grade_4', 'grade_5', 'grade_6', 'grade_all']:
    path = f'/data/kexvefuxi/students_{grade}.json'
    try:
        with sftp.open(path, "rb") as f:
            data = json.loads(f.read().decode('utf-8'))
            if isinstance(data, dict):
                print(f"\n=== students_{grade}.json: {len(data)} entries ===")
    except FileNotFoundError:
        print(f"\n=== students_{grade}.json: NOT FOUND ===")

# Check main students.json key format
print("\n=== students.json keys ===")
with sftp.open("/data/kexvefuxi/students.json", "rb") as f:
    students = json.loads(f.read().decode('utf-8'))
for key in list(students.keys())[:10]:
    print(f"  '{key}'")

# Check if there are backup/recovery files
stdin, stdout, stderr = client.exec_command("ls -la /data/kexvefuxi/recovery_backups/ 2>/dev/null | head -20")
backups = stdout.read().decode()
if backups.strip():
    print(f"\n=== Backups ===\n{backups}")

# Check if any old ranking data in student_info.json
try:
    with sftp.open("/data/kexvefuxi/student_info.json", "rb") as f:
        info = json.loads(f.read().decode('utf-8'))
    if isinstance(info, dict):
        print(f"\n=== student_info.json: {len(info)} entries ===")
except:
    print("\n=== student_info.json: NOT FOUND ===")

sftp.close()
client.close()
