⚡ My Discord Lab
"A melhor maneira de prever o futuro é inventá-lo." > Este repositório é o meu "laboratório" pessoal onde estou desbravando a biblioteca discord.py e transformando café em código. ☕️🚀

🎯 Objetivo do Projeto
Não é apenas "mais um bot". O foco aqui é o aprendizado. Estou explorando a documentação oficial para entender a lógica por trás de:

Interações assíncronas (async/await).

Gerenciamento de estados e cache do Discord.

Tratamento de erros e permissões de usuário.

🛠️ Evolução do Conhecimento
Abaixo, os tópicos que já dominei e os que ainda estão na mira:

[x] Criar e conectar o bot ao gateway.

[x] Comandos básicos e respostas simples.

[x] Uso de Embeds (mensagens elegantes).

[ ] Implementação de Cogs (modularização).

[ ] Integração com Banco de Dados (SQLite).

[ ] Slash Commands (comandos de barra).

📂 Como testar (Modo Dev)
Se você caiu aqui de paraquedas e quer ver o progresso:

Clone este cantinho:

Bash
git clone https://github.com/seu-usuario/bot-discord-em-python.git
Prepare o ambiente:

Bash
pip install -r requirements.txt
Segurança em primeiro lugar:

⚠️ Nunca suba seu token para o GitHub! Crie um arquivo .env para guardá-lo.

🧩 Snippet Favorito
Um pedacinho de código que achei interessante durante o estudo:

Python
@bot.event
async def on_ready():
    print(f'✅ Logado com sucesso como {bot.user}!')
    print('------')
