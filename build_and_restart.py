import paramiko
import time

HOST = '79.143.185.232'
USER = 'root'
PASSWORD = 'mebel717'
APP_DIR = '/root/mebel717-bot'
IMAGE = 'mebel717-bot'
CONTAINER = 'mebel_bot'

def run(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out + ('\n' + err if err else '')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASSWORD)

print("1. Git pull...")
print(run(client, f"cd {APP_DIR} && git pull origin main 2>&1"))

print("\n2. Docker image build...")
out = run(client, f"cd {APP_DIR} && docker build -t {IMAGE} . 2>&1 | tail -5")
print(out)

print("\n3. Eski konteyner to'xtatilmoqda...")
run(client, f"docker stop {CONTAINER} 2>/dev/null; docker rm {CONTAINER} 2>/dev/null")

print("4. Yangi konteyner ishga tushirilmoqda...")
cmd = (
    f"docker run -d "
    f"--name {CONTAINER} "
    f"--restart unless-stopped "
    f"--network mebel717-bot_default "
    f"--network-alias bot "
    f"-p 8000:8000 "
    f"-v {APP_DIR}/mebel.db:/app/mebel.db "
    f"-v {APP_DIR}/downloads:/app/downloads "
    f"--env-file {APP_DIR}/.env "
    f"{IMAGE}"
)
print(run(client, cmd))

time.sleep(8)

print("\n5. Holat:")
print(run(client, "docker ps --format '{{.Names}} | {{.Status}}'"))

print("\n6. Bot loglari:")
print(run(client, f"docker logs {CONTAINER} --tail 10 2>&1"))

client.close()
print("\n✅ Deploy tugadi!")
