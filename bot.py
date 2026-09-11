import os
import aiohttp
import discord
from dotenv import load_dotenv

load_dotenv()
# Configura as permissões (intents) do bot
intents = discord.Intents.default()
intents.message_content = True

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')

# Inicializa o cliente do bot
client = discord.Client(intents=intents)

url_base = 'https://horas.zibikoski.com.br/api/v1/'


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
        'Authorization': 'Bearer ' + API_KEY,
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
          await message.channel.send(
              f'Erro ao consultar a API externa: {texto_erro}'
          )

  if message.content.lower() == '!ping':
    await message.channel.send('Pong!')


client.run(DISCORD_TOKEN)
