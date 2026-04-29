import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("cd ~/mebel717-bot && docker-compose rm -fs bot && docker-compose up -d bot")
print(stdout.read().decode())
client.close()
