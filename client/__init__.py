import asyncio
import json

import discord

import utils
from translate import BaiduTranslator
from bilibili import DanmakuSender, BiliLiveAntiShield, words, rules


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translator = None
        self.__danmaku_senders = {}
        self.__anti_shield = None
        self.__channel_config = {}
        self.__command_handler = {}

    async def close(self) -> None:
        await super().close()
        if self.__translator is not None:
            await self.__translator.close()

        if not self.__danmaku_senders:
            for danmaku_sender in self.__danmaku_senders.values():
                await danmaku_sender.close()

    async def on_ready(self):
        pass

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content.strip()

        if content == '':
            return

        if content[0] == '!':
            await self.__handle_command(content, message)
            return

        channel = message.channel

        if channel.id not in self.__channel_config or channel.id not in self.__danmaku_senders:
            return

        channel_config = self.__channel_config[channel.id]

        if 'user' not in channel_config or message.author.name != channel_config.user:
            print(message.author.name)
            return

        send_lag = channel_config.get('send_lag', utils.SEND_LAG)
        await asyncio.sleep(send_lag)

        content = utils.text_processor.deal(message.content)
        dst_texts = await self.__translator.translate([content])
        for dst_text in dst_texts:
            dst_text = self.__anti_shield.deal(dst_text)
            texts = utils.slice_text(dst_text)

            first_flag = True
            for text in texts:
                result = await self.__danmaku_senders[channel.id].send(text)
                if result:
                    utils.log_info(f'[Successfully]Message {message.content} -> {text}')
                else:
                    utils.log_error(f'[Failed]Message {message.content} -> {text}')

                if first_flag:
                    first_flag = False
                else:
                    await asyncio.sleep(utils.SEND_INTERVAL)

    async def __handle_command(self, content, message):
        if len(content) < 2:
            return

        command = content[1:].split(' ')[0].upper()
        if command in self.__command_handler:
            await self.__command_handler[command](message)

    def init_channel_config(self):
        with open("channel_config.json", "a") as file:
            pass

        with open("channel_config.json", "r") as file:
            text = file.read()
            if text == '':
                self.__channel_config = {}
            else:
                self.__channel_config = json.loads(file.read())

        return True

    def init_translator(self, _appid: str, _key: str):
        self.__translator = BaiduTranslator(_appid, _key)
        return self.__translator.init()

    def init_danmaku_sender(self):
        for channel_id, channel_config in self.__channel_config.items():
            _room_id = channel_config.get('room_id', '')
            _sessdata = channel_config.get('sessdata', '')
            _bili_jct = channel_config.get('bili_jct', '')
            _buvid3 = channel_config.get('buvid3', '')

            self.__danmaku_senders[channel_id] = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
            if not self.__danmaku_senders[channel_id].init():
                del self.__danmaku_senders[channel_id]

        return True

    def init_anti_shield(self):
        self.__anti_shield = BiliLiveAntiShield(rules, words)
        return True

    def init_command_handler(self):
        self.__command_handler["SET"] = self.__set_config
        self.__command_handler["START"] = self.__start_channel
        self.__command_handler["STOP"] = self.__stop_channel

        return True

    async def __start_channel(self, message):
        if message.channel.id not in self.__channel_config:
            return

        if message.channel.id in self.__danmaku_senders:
            return

        channel_config = self.__channel_config[message.channel.id]
        _room_id = channel_config.get('room_id', '')
        _sessdata = channel_config.get('sessdata', '')
        _bili_jct = channel_config.get('bili_jct', '')
        _buvid3 = channel_config.get('buvid3', '')

        self.__danmaku_senders[message.channel.id] = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
        if not self.__danmaku_senders[message.channel.id].init():
            await message.channel.send('Failed to start.')
            del self.__danmaku_senders[message.channel.id]
        else:
            await message.channel.send('Successfully started.')

    async def __stop_channel(self, message):
        if message.channel.id not in self.__channel_config:
            return

        if message.channel.id not in self.__danmaku_senders:
            return

        await self.__danmaku_senders[message.channel.id].close()
        del self.__danmaku_senders[message.channel.id]
        await message.channel.send('Successfully stopped.')

    async def __set_config(self, message):
        params = message.content.strip().split()
        if len(params) < 2:
            return

        channel_id = message.channel.id
        if channel_id not in self.__channel_config:
            self.__channel_config[channel_id] = {}

        i = 2
        while i < len(params):
            key = params[i - 1].lower()
            self.__channel_config[channel_id][key] = params[i]
            i = i + 2

        with open("channel_config.json", "w") as file:
            file.write(json.dumps(self.__channel_config))
