import paramiko
import time

host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

# Start gracefully
client.exec_command("nohup sh -c 'cd ~/mebel717-bot && docker-compose up -d' > /dev/null 2>&1 &")
time.sleep(2) # Give it time to start
client.close()
