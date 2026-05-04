import discord
import os
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Cliente(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        # Dicionário temporário para guardar as entradas: {user_id: hora_entrada}
        self.estudos = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos sincronizados com sucesso!")

    async def on_ready(self):
        print(f"Estou Ligado papai {self.user}")

    async def on_voice_state_update(self, member, before, after):
        # 1. Detecta entrada na call
        if before.channel is None and after.channel is not None:
            self.estudos[member.id] = datetime.now()
            print(f"[{datetime.now().strftime('%H:%M')}] {member.name} iniciou os estudos.")

        # 2. Detecta saída da call
        elif before.channel is not None and after.channel is None:
            if member.id in self.estudos:
                entrada = self.estudos.pop(member.id) # Pega o valor e remove do dicionário
                saida = datetime.now()
                duracao = saida - entrada
                
                # Extraindo horas e minutos da duração
                segundos_totais = int(duracao.total_seconds())
                horas = segundos_totais // 3600
                minutos = (segundos_totais % 3600) // 60
                
                mensagem = f"📚 {member.mention} finalizou a sessão de estudos!\n⏱️ **Duração:** {horas}h e {minutos}min"
                
                print(f"{member.name} estudou por {horas}h{minutos}min.")

                # Para enviar no canal onde ele estava ou um canal fixo:
                # Substitua pelo ID do seu canal de texto de logs
                canal_log = self.get_channel(123456789012345678) 
                if canal_log:
                    await canal_log.send(mensagem)

# Configuração de Intents
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          
intents.voice_states = True     

client = Cliente(intents=intents)

# --- Comandos ---

@client.tree.command(name="ping", description="Testa a latência do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(client.latency * 1000)}ms")

client.run(os.getenv('TOKEN_BOT'))