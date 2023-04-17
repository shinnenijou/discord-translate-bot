import discord
from configparser import RawConfigParser

import utils
from translate import BaiduTranslator


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translator = None

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        dst_text = self.__translator.translate([message.content])
        print(f'Message from {message.author}: {message.content} -> {dst_text[0]}')

    def init_translator(self, _appid: str, _key: str):
        self.__translator = BaiduTranslator(_appid, _key)
        return self.__translator.init()


def main():
    config = RawConfigParser()
    config.read('config.ini')
    if not utils.check_config(config):
        print("[error]配置文件错误, 请检查配置文件")
        return

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    if not client.init_translator(config['baidu']['appid'], config['baidu']['key']):
        return

    token = config['discord']['token']
    client.run(token)


if __name__ == '__main__':
    main()
