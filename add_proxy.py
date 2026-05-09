import paramiko, time
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('159.75.134.151', username='root', password='sC,/{8v*!b9EQ2$', timeout=15, allow_agent=False, look_for_keys=False)

proxy_config = """
# API proxy
location /api/ {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
"""

chan = client.get_transport().open_session()
chan.setblocking(0)
cmd = f"cat >> /www/server/panel/vhost/nginx/159.75.134.151.conf << 'LOCEOF'\n{proxy_config}\nLOCEOF\n/www/server/nginx/sbin/nginx -s reload 2>&1\necho RELOADED"
chan.exec_command(cmd)
time.sleep(5)
out = b''
while chan.recv_ready():
    out += chan.recv(65536)
print(out.decode()[:1000])
chan.close()
client.close()
