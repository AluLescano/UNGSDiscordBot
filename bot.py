#bot.py
import os
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.client()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'{client.user} se ha conectado a Discord!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)