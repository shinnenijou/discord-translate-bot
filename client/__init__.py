import asyncio

import discord

import utils
from translate import BaiduTranslator
from bilibili import DanmakuSender, BiliLiveAntiShield, words, rules


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translator = None
        self.__danmaku_sender = None
        self.__anti_shield = None

    async def close(self) -> None:
        await super().close()
        if self.__translator is not None:
            await self.__translator.close()

        if self.__danmaku_sender is not None:
            await self.__danmaku_sender.close()

    async def on_ready(self):
        print(f'Logged on as {self.user}!, send danmaku as {self.__danmaku_sender.get_name()}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == '':
            return

        await asyncio.sleep(utils.SEND_LAG)

        dst_texts = await self.__translator.translate([message.content])
        for dst_text in dst_texts:
            dst_text = self.__anti_shield.deal(dst_text)
            texts = utils.slice_text(dst_text)

            first_flag = True
            for text in texts:
                result = await self.__danmaku_sender.send(text)
                if result:
                    utils.log_info(f'[Successfully]Message {message.content} -> {text}')
                else:
                    utils.log_error(f'[Failed]Message {message.content} -> {text}')

                if first_flag:
                    first_flag = False
                else:
                    await asyncio.sleep(utils.SEND_INTERVAL)

    def init_translator(self, _appid: str, _key: str):
        self.__translator = BaiduTranslator(_appid, _key)
        return self.__translator.init()

    def init_danmaku_sender(self, _room_id, _sessdata, _bili_jct, _buvid3):
        self.__danmaku_sender = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
        return self.__danmaku_sender.init()

    def init_anti_shield(self):
        self.__anti_shield = BiliLiveAntiShield(rules, words)
        return True