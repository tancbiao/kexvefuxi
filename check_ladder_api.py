import paramiko

host = "159.75.134.151"
port = 22
username = "root"
password = "sC,/{8v*!b9EQ2$"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, username, password)

# Check if ladder routes exist in api.py
stdin, stdout, stderr = client.exec_command("grep -n 'ladder\|/ladder' /data/api.py")
api_routes = stdout.read().decode()
print("=== Ladder routes in api.py ===")
print(api_routes if api_routes else "NONE FOUND - ladder API NOT deployed!")

# Check Nginx config for ladder routes
stdin, stdout, stderr = client.exec_command("grep -n 'ladder' /www/server/panel/vhost/nginx/api.conf")
nginx = stdout.read().decode()
print("\n=== Ladder in nginx config ===")
print(nginx if nginx else "NONE FOUND")

# Try local curl to bypass SSL
stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:5000/api/ladder/profile/01210221 2>&1")
local_resp = stdout.read().decode()
print(f"\n=== Local curl to ladder profile ===")
print(local_resp[:200] if local_resp else "No response")

client.close()
