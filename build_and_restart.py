import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

# Run build and save to log
client.exec_command("cd ~/mebel717-bot && docker-compose up -d --build bot > ~/docker_build.log 2>&1")

import time
time.sleep(10)

stdin, stdout, stderr = client.exec_command("cat ~/docker_build.log")
print("BUILD:", stdout.read().decode())

client.close()
