import paramiko

host = '79.143.185.232'
user = 'root'
password = 'mebel717'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

test_script = """
import asyncio
from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def test_send():
    bot = Bot(token=BOT_TOKEN)
    targets = ["-1087968824", "-1001087968824", "1087968824"]
    for t in targets:
        try:
            await bot.send_message(chat_id=int(t), text=f"Test message to {t}")
            print(f"SUCCESS: {t}")
        except Exception as e:
            print(f"FAILED {t}: {e}")
    await bot.session.close()

asyncio.run(test_send())
"""

# write script to server
client.exec_command('cat << "EOF" > ~/mebel717-bot/test_group.py\n' + test_script + '\nEOF')

# execute inside the container
stdin, stdout, stderr = client.exec_command('docker exec mebel_bot python test_group.py')
print("STDOUT:")
print(stdout.read().decode())
print("STDERR:")
print(stderr.read().decode())

client.close()
