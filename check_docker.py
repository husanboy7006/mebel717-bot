import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("docker logs --tail 100 mebel_bot")
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
with open('docker_logs.txt', 'w', encoding='utf-8') as f:
    f.write(out)
    if err: f.write("\nERRORS:\n" + err)

client.close()
