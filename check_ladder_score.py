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

# 1. Check rankings_grade_all.json for 01210221
with sftp.open("/data/kexvefuxi/rankings_grade_all.json", "rb") as f:
    rankings = json.loads(f.read().decode('utf-8'))
r_data = rankings.get('01210221', {})
print(f"=== rankings_grade_all.json ===")
print(f"  totalPoints: {r_data.get('totalPoints', 0)}")
print(f"  towerFloor: {r_data.get('towerFloor', 0)}")
print(f"  towerHighestFloor: {r_data.get('towerHighestFloor', 0)}")
print(f"  ladderScore: {r_data.get('ladderScore', 0)}")

# 2. Check students.json for 01210221
with sftp.open("/data/kexvefuxi/students.json", "rb") as f:
    students = json.loads(f.read().decode('utf-8'))
# Try both key formats
for key in students:
    if '01210221' in key:
        s_data = students[key]
        print(f"\n=== students.json (key={key}) ===")
        print(f"  totalPoints: {s_data.get('totalPoints', 0)}")
        print(f"  towerCoins: {s_data.get('towerCoins', 0)}")
        print(f"  towerHighestFloor: {s_data.get('towerHighestFloor', 0)}")

# 3. Check ladder profile via API
import requests
try:
    resp = requests.get('https://api.xixitime.cn/api/ladder/profile/01210221', timeout=5)
    if resp.status_code == 200:
        lp = resp.json()
        print(f"\n=== API /ladder/profile/01210221 ===")
        print(f"  score: {lp.get('score', 'N/A')}")
        print(f"  bestScore: {lp.get('bestScore', 'N/A')}")
        print(f"  tier: {lp.get('tier', 'N/A')}")
    else:
        print(f"\n=== API /ladder/profile/01210221: HTTP {resp.status_code} ===")
except Exception as e:
    print(f"\n=== API /ladder/profile: Error - {e} ===")

# 4. Check the ladder profile on server file if it exists
try:
    with sftp.open("/data/kexvefuxi/ladder_profiles.json", "rb") as f:
        lps = json.loads(f.read().decode('utf-8'))
    ld = lps.get('01210221', {})
    print(f"\n=== ladder_profiles.json ===")
    print(f"  score: {ld.get('score', 'N/A')}")
    print(f"  bestScore: {ld.get('bestScore', 'N/A')}")
except:
    print(f"\n=== ladder_profiles.json: NOT FOUND ===")

# Check all ladder-related files
stdin, stdout, stderr = client.exec_command("ls -la /data/kexvefuxi/ladder* 2>/dev/null && ls -la /data/kexvefuxi/*ladder* 2>/dev/null")
print(f"\nLadder files:\n{stdout.read().decode()}")

sftp.close()
client.close()
