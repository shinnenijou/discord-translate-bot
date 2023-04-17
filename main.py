import discord
from configparser import RawConfigParser


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
config = RawConfigParser()
config.read('config.ini')

token = config['account']['token']
client.run(token)
