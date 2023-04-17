import discord

import utils
from translate import BaiduTranslator
from bilibili import DanmakuSender


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translator = None
        self.__danmaku_sender = None

    async def on_ready(self):
        print(f'Logged on as {self.user}!, send danmaku as {self.__danmaku_sender.get_name()}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        dst_texts = self.__translator.translate([message.content])
        for text in dst_texts:
            if self.__danmaku_sender.send(text):
                utils.log_info(f'[Successfully]Message {message.content} -> {text}')
            else:
                utils.log_error(f'[Failed]Message {message.content} -> {text}')

    def init_translator(self, _appid: str, _key: str):
        self.__translator = BaiduTranslator(_appid, _key)
        return self.__translator.init()

    def init_danmaku_sender(self, _room_id, _sessdata, _bili_jct, _buvid3):
        self.__danmaku_sender = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
        return self.__danmaku_sender.init()
