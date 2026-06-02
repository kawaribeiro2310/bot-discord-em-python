import discord
import os
import sqlite3
from google import genai  # Novo SDK Oficial do Google
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --- CONFIGURAÇÃO DA IA ---
# Inicializa o cliente padrão do novo SDK
ai_client = genai.Client() 
# CORREÇÃO CRUCIAL: Atualizado para o modelo atual e suportado na API pública
MODELO_IA = 'gemini-2.5-flash'

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estudos.db')
    cursor = conn.cursor()
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

# --- CLIENTE ---
class Cliente(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.estudos = {}

    async def setup_hook(self):
        init_db()
        MEU_GUILD_ID = 1475163750003638376 
        guild = discord.Object(id=MEU_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"✅ Comandos sincronizados para o servidor {MEU_GUILD_ID}!")

    async def on_ready(self):
        print(f"✅ Bot online como {self.user}")

    # --- IA NO EVENTO ON_MESSAGE (RESPONDE AO MARCAR) ---
    async def on_message(self, message):
        # Ignora mensagens do próprio bot
        if message.author == self.user:
            return

        # Responde se for marcado (@Bot)
        if self.user.mentioned_in(message):
            async with message.channel.typing():
                try:
                    # Limpa as menções cruas (<@ID>) para que a IA receba apenas o texto limpo
                    pergunta = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
                    
                    if not pergunta:
                        await message.reply("Olá! Como posso ajudar nos seus estudos hoje? Marque-me e faça uma pergunta!")
                        return

                    # Envia a pergunta para o modelo estável
                    response = ai_client.models.generate_content(
                        model=MODELO_IA,
                        contents=pergunta,
                    )
                    
                    texto_resposta = response.text
                    if len(texto_resposta) > 2000:
                        texto_resposta = texto_resposta[:1990] + "... (cortado)"
                        
                    await message.reply(texto_resposta)
                except Exception as e:
                    await message.reply(f"❌ Erro na IA ao responder menção: {e}")

    async def on_voice_state_update(self, member, before, after):
        ID_CANAL_LOG = 1500944813334331526
        canal_log = self.get_channel(ID_CANAL_LOG)

        if before.channel is None and after.channel is not None:
            self.estudos[member.id] = datetime.now()
            if canal_log:
                await canal_log.send(f"📚 {member.mention} iniciou os estudos!")

        elif before.channel is not None and after.channel is None:
            if member.id in self.estudos:
                entrada = self.estudos.pop(member.id)
                segundos_sessao = int((datetime.now() - entrada).total_seconds())
                salvar_tempo(member.id, segundos_sessao)
                
                horas = segundos_sessao // 3600
                minutos = (segundos_sessao % 3600) // 60
                
                if canal_log:
                    await canal_log.send(f"📚 {member.mention} estudou {horas}h e {minutos}min!")

# --- INSTANCIA E COMANDOS ---
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True  # Obrigatório para capturar o texto das menções

client = Cliente(intents=intents)

@client.tree.command(name="perfil", description="Veja seu tempo total de estudo")
async def perfil(interaction: discord.Interaction):
    total_segundos = buscar_tempo_total(interaction.user.id)
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    
    embed = discord.Embed(title=f"📊 Perfil de {interaction.user.name}", color=0x2ecc71)
    embed.add_field(name="Tempo Total", value=f"⏱️ {horas}h {minutos}min", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="duvida", description="Tire uma dúvida com a IA")
async def duvida(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer() 
    try:
        response = ai_client.models.generate_content(
            model=MODELO_IA,
            contents=pergunta,
        )
        texto_resposta = response.text
        if len(texto_resposta) > 2000:
            texto_resposta = texto_resposta[:1990] + "... (cortado)"
            
        await interaction.followup.send(texto_resposta)
    except Exception as e:
        await interaction.followup.send(f"Erro: {e}")

client.run(os.getenv('TOKEN_BOT'))