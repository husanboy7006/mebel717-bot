import paramiko
host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8000/api/products")
print("CURL STDOUT:")
print(stdout.read().decode()[:1000])

stdin, stdout, stderr = client.exec_command("curl -s https://mebel717.uz/api/products")
print("CURL STDOUT (HTTPS):")
print(stdout.read().decode()[:1000])

client.close()
