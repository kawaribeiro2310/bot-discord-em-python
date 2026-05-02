import discord
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Cliente(discord.Client):
    async def on_ready(self):
        print(f"Estou Ligado papai {self.user}")

intents = discord.Intents.default()
intents.message_content = True

client = Cliente(intents=intents)

# token super secreto
client.run(os.getenv('TOKEN_BOT'))