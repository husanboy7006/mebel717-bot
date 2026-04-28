import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("cat ~/mebel717-bot/.env")
print("ENV:")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command("docker logs --tail 20 mebel_bot")
print("LOGS:")
print(stdout.read().decode())
client.close()
