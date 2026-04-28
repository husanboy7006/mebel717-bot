import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

# Run git pull and restart and save to log
client.exec_command("cd ~/mebel717-bot && git pull > ~/git_pull.log 2>&1")
import time
time.sleep(3)
client.exec_command("cd ~/mebel717-bot && docker-compose restart bot > ~/docker_res.log 2>&1")
time.sleep(3)

stdin, stdout, stderr = client.exec_command("cat ~/git_pull.log")
print("GIT:", stdout.read().decode())

client.close()
