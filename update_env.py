import paramiko

host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

commands = [
    'sed -i "s/GROUP_ID=.*/GROUP_ID=-1003971359893/" ~/mebel717-bot/.env',
    'cd ~/mebel717-bot && docker-compose restart bot'
]

for cmd in commands:
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"ERROR: {err}")

client.close()
