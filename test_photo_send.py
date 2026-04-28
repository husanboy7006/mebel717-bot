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

BOT_TOKEN = "8407740373:AAGWT2kQ1rIRg7D6qVTw8HQjgaZPZ0Vo8Ek"

async def test_send():
    bot = Bot(token=BOT_TOKEN)
    t = "-1003971359893"
    try:
        # Just send a dummy text message to make sure we can send
        await bot.send_message(chat_id=int(t), text="Testing photo send permission...")
        # Then send a photo by URL
        await bot.send_photo(chat_id=int(t), photo="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", caption="Test photo")
        print(f"SUCCESS to {t}")
    except Exception as e:
        print(f"FAILED {t}: {e}")
    await bot.session.close()

asyncio.run(test_send())
"""

stdin, stdout, stderr = client.exec_command('docker exec -i mebel_bot python -')
stdin.write(test_script)
stdin.channel.shutdown_write()

print(stdout.read().decode(errors='ignore'))
print(stderr.read().decode(errors='ignore'))
client.close()
