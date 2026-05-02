import discord
import os
from discord import app_commands  # Importante para os Slash Commands
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class Cliente(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # Criamos a árvore de comandos vinculada a este cliente
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Esta função roda UMA VEZ antes do bot ligar de vez
        # Ela é ideal para sincronizar os comandos com o Discord
        await self.tree.sync()
        print("Comandos sincronizados com sucesso!")

    async def on_ready(self):
        print(f"Estou Ligado papai {self.user}")

# Configuração de Intents
intents = discord.Intents.default()
intents.message_content = True # Necessário se ainda quiser ler mensagens comuns

client = Cliente(intents=intents)

# --- Seção de Comandos Slash ---

@client.tree.command(name="ping", description="Testa a latência do bot")
async def ping(interaction: discord.Interaction):
    # Em Slash Commands, usamos interaction.response.send_message
    await interaction.response.send_message(f"Pong! 🏓 {round(client.latency * 1000)}ms")

@client.tree.command(name="eco", description="O bot repete o que você disser")
@app_commands.describe(mensagem="A frase que o bot deve repetir")
async def eco(interaction: discord.Interaction, mensagem: str):
    await interaction.response.send_message(f"Você disse: {mensagem}")

# Execução
client.run(os.getenv('TOKEN_BOT'))