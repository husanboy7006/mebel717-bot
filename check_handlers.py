import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("docker exec mebel_bot cat /app/handlers/user_handlers.py | grep -A 10 GROUP_ID")
print("USER_HANDLERS:")
print(stdout.read().decode())
client.close()
