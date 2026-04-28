import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("cd ~/mebel717-bot && docker-compose down && docker-compose up -d")
print("STDOUT:")
print(stdout.read().decode())
print("STDERR:")
print(stderr.read().decode())

stdin, stdout, stderr = client.exec_command("docker ps")
print("PS:")
print(stdout.read().decode())

client.close()
