import paramiko
import time

host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

# Git pull
print("Git pull boshlandi...")
stdin, stdout, stderr = client.exec_command("cd ~/mebel717-bot && git pull origin main 2>&1")
print("PULL:", stdout.read().decode())

# Docker build va restart
print("Docker build boshlandi...")
client.exec_command("cd ~/mebel717-bot && docker-compose up -d --build bot > ~/docker_build.log 2>&1")

time.sleep(15)

stdin, stdout, stderr = client.exec_command("cat ~/docker_build.log")
print("BUILD:", stdout.read().decode())

# Bot ishlayaptimi?
stdin, stdout, stderr = client.exec_command("docker ps --filter name=mebel_bot --format '{{.Status}}'")
print("BOT HOLATI:", stdout.read().decode())

client.close()
print("Yangilanish tugadi!")
