import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

# Check status and start
commands = [
    'cd ~/mebel717-bot && docker-compose ps',
    'cd ~/mebel717-bot && docker-compose up -d bot',
    'cd ~/mebel717-bot && docker logs --tail 20 mebel_bot'
]

for cmd in commands:
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    print("STDOUT:", stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")

client.close()
