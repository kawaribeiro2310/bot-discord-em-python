import discord
import os
import sqlite3
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --- Funções do Banco de Dados ---
def init_db():
    conn = sqlite3.connect('estudos.db')
    cursor = conn.cursor()
    # Cria a tabela se não existir: ID do usuário e total de segundos estudados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            total_segundos INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def salvar_tempo(user_id, segundos):
    conn = sqlite3.connect('estudos.db')
    cursor = conn.cursor()
    # Insere ou atualiza o tempo acumulado
    cursor.execute('''
        INSERT INTO usuarios (user_id, total_segundos) 
        VALUES(?, ?) 
        ON CONFLICT(user_id) DO UPDATE SET total_segundos = total_segundos + ?
    ''', (user_id, segundos, segundos))
    conn.commit()
    conn.close()

def buscar_tempo_total(user_id):
    conn = sqlite3.connect('estudos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT total_segundos FROM usuarios WHERE user_id = ?', (user_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0

# --- Classe do Cliente ---
class Cliente(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.estudos = {} # {user_id: datetime_entrada}

    async def setup_hook(self):
        init_db() # Inicia o banco de dados
        await self.tree.sync()
        print("Comandos e Banco de Dados prontos!")

    async def on_ready(self):
        print(f"Estou Ligado papai {self.user}")

    async def on_voice_state_update(self, member, before, after):
        canal_log_id = 1500944813334331526 
        canal_log = self.get_channel(canal_log_id)

        # Entrada na call
        if before.channel is None and after.channel is not None:
            self.estudos[member.id] = datetime.now()
            if canal_log:
                await canal_log.send(f"📚 {member.mention} iniciou os estudos!")

        # Saída da call
        elif before.channel is not None and after.channel is None:
            if member.id in self.estudos:
                entrada = self.estudos.pop(member.id)
                duracao = datetime.now() - entrada
                segundos_sessao = int(duracao.total_seconds())
                
                # Salva no banco de dados
                salvar_tempo(member.id, segundos_sessao)
                
                horas = segundos_sessao // 3600
                minutos = (segundos_sessao % 3600) // 60
                
                if canal_log:
                    await canal_log.send(f"📚 {member.mention} finalizou! \n⏱️ **Sessão:** {horas}h {minutos}m")

# --- Configurações e Comandos ---
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = Cliente(intents=intents)

@client.tree.command(name="perfil", description="Veja seu tempo total de estudo acumulado")
async def perfil(interaction: discord.Interaction):
    total_segundos = buscar_tempo_total(interaction.user.id)
    
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    
    embed = discord.Embed(title=f"📊 Estatísticas de {interaction.user.display_name}", color=discord.Color.blue())
    embed.add_field(name="Tempo Total Dedicado", value=f"✅ {horas} horas e {minutos} minutos", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

client.run(os.getenv('TOKEN_BOT'))