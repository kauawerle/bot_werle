import os
import aiohttp
import discord
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 1. O load_dotenv() DEVE vir antes de ler as variáveis
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')

# Configura as permissões (intents) do bot
intents = discord.Intents.default()
intents.message_content = True

app = Flask('')
client = discord.Client(intents=intents)

url_base = 'https://horas.zibikoski.com.br/api/v1/'

@app.route('/')
def home():
    return 'O bot está online!'

def run_web_server():
    # O Render usa a porta 10000 por padrão se não achar a variável PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == '!consultar':
        url_completa = f'{url_base}hours?ra=505692'

        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url_completa, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    hours = data.get('horas_formatadas', 'Não foi possível obter as horas.')
                    acesso = data.get('ultimo_acesso', 'Não foi possível obter essa informação.')
                    await message.channel.send(f'As horas são: {hours}. Último acesso: {acesso}')
                else:
                    try:
                        texto_erro = await response.text()
                    except Exception as e:
                        texto_erro = str(e)
                    await message.channel.send(f'Erro ao consultar a API externa: {texto_erro}')

    if message.content.lower() == '!ping':
        await message.channel.send('Pong!')

# 2. Iniciamos a Thread FORA do bloco __main__ para garantir que o Render execute o Flask
server_thread = Thread(target=run_web_server)
# Define como Daemon para que a thread feche junto com o programa principal se houver erro
server_thread.daemon = True 
server_thread.start()

# 3. Executa o bot do Discord
if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
else:
    print("ERRO: DISCORD_TOKEN não foi encontrado! Verifique as Environment Variables no Render.")
