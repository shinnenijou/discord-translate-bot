import asyncio
import json

import discord

import utils
from translate import TRANSLATORS_MAP
from bilibili import DanmakuSender, BiliLiveAntiShield, words, rules


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translators = {}
        self.__danmaku_senders = {}
        self.__anti_shield = None
        self.__channel_config = {}
        self.__command_handler = {}
        self.__config = None

    async def close(self) -> None:
        await super().close()
        if not self.__translators:
            for translator in self.__translators.values():
                await translator.close()

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
        channel_id = str(channel.id)

        if channel_id not in self.__channel_config or channel_id not in self.__danmaku_senders:
            return

        channel_config = self.__channel_config[channel_id]

        if 'user' not in channel_config or message.author.name != channel_config['user']:
            return

        send_lag = int(channel_config.get('send_lag', utils.SEND_LAG))
        await asyncio.sleep(send_lag)

        content = utils.text_processor.deal(message.content)
        dst_texts = await self.__translators[channel_id].translate([content])
        for dst_text in dst_texts:
            dst_text = self.__anti_shield.deal(dst_text)
            texts = utils.slice_text(dst_text)

            first_flag = True
            for text in texts:
                result = await self.__danmaku_senders[channel_id].send(text)
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

    def init_channel_config(self, config):
        self.__config = config

        with open("channel_config.json", "a") as file:
            pass

        with open("channel_config.json", "r") as file:
            text = file.read()
            if text == '':
                self.__channel_config = {}
            else:
                self.__channel_config = json.loads(text)

        return True

    def init_translator(self):
        for channel_id, channel_config in self.__channel_config.items():
            if channel_config.get('status', 0) == 0:
                continue

            user = channel_config.get('user', '')
            room_id = channel_config.get('room_id', '')
            api = channel_config.get('api', 'baidu')

            if api not in TRANSLATORS_MAP:
                continue

            self.__translators[channel_id] = TRANSLATORS_MAP[api](self.__config[api]['id'], self.__config[api]['key'])
            if not self.__translators[channel_id].init():
                del self.__translators[channel_id]
            else:
                utils.log_info(f'[Successfully]Translator for {user}({room_id}) is ready.')

        return True

    def init_danmaku_sender(self):
        for channel_id, channel_config in self.__channel_config.items():
            if channel_config.get('status', 0) == 0:
                continue

            if channel_id not in self.__translators:
                channel_config['status'] = 0
                continue

            _user = channel_config.get('user', '')
            _room_id = channel_config.get('room_id', '')
            _sessdata = channel_config.get('sessdata', '')
            _bili_jct = channel_config.get('bili_jct', '')
            _buvid3 = channel_config.get('buvid3', '')

            self.__danmaku_senders[channel_id] = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
            if not self.__danmaku_senders[channel_id].init():
                del self.__danmaku_senders[channel_id]
                channel_config['status'] = 0
            else:
                utils.log_info(f'[Successfully]Danmaku sender for {_user}({_room_id}) started.')

        with open("channel_config.json", "w") as file:
            file.write(json.dumps(self.__channel_config))

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
        channel_id = str(message.channel.id)
        if channel_id not in self.__channel_config:
            return

        if channel_id in self.__translators:
            return

        if channel_id in self.__danmaku_senders:
            return

        channel_config = self.__channel_config[channel_id]
        _room_id = channel_config.get('room_id', '')
        _sessdata = channel_config.get('sessdata', '')
        _bili_jct = channel_config.get('bili_jct', '')
        _buvid3 = channel_config.get('buvid3', '')
        _api = channel_config.get('api', 'baidu')

        if _api not in TRANSLATORS_MAP:
            await message.channel.send('Invalid API.')
            return

        self.__translators[channel_id] = TRANSLATORS_MAP[_api](self.__config[_api]['id'], self.__config[_api]['key'])
        if not self.__translators[channel_id].init():
            await message.channel.send('Failed to start translator.')
            del self.__translators[channel_id]
            return

        self.__danmaku_senders[channel_id] = DanmakuSender(_room_id, _sessdata, _bili_jct, _buvid3)
        if not self.__danmaku_senders[channel_id].init():
            await message.channel.send('Failed to start Danmaku Sender.')
            del self.__danmaku_senders[channel_id]
            return

        await message.channel.send('Successfully started.')

        self.__channel_config[channel_id]['status'] = 1
        with open("channel_config.json", "w") as file:
            file.write(json.dumps(self.__channel_config))

    async def __stop_channel(self, message):
        channel_id = str(message.channel.id)
        if channel_id not in self.__channel_config:
            return

        if channel_id not in self.__translators:
            return

        if channel_id not in self.__danmaku_senders:
            return

        await self.__translators[channel_id].close()
        del self.__translators[channel_id]

        await self.__danmaku_senders[channel_id].close()
        del self.__danmaku_senders[channel_id]

        await message.channel.send('Successfully stopped.')

        self.__channel_config[channel_id]['status'] = 0
        with open("channel_config.json", "w") as file:
            file.write(json.dumps(self.__channel_config))

    async def __set_config(self, message):
        params = message.content.strip().split()
        if len(params) < 2:
            return

        channel_id = str(message.channel.id)
        if channel_id not in self.__channel_config:
            self.__channel_config[channel_id] = {}
        elif self.__channel_config[channel_id].get('status', 0) == 1:
            return

        i = 2
        while i < len(params):
            key = params[i - 1].lower()
            self.__channel_config[channel_id][key] = params[i]
            i = i + 2

        self.__channel_config[channel_id]['status'] = 0

        if 'api' not in self.__channel_config[channel_id]:
            self.__channel_config[channel_id]['api'] = 'baidu'

        with open("channel_config.json", "w") as file:
            file.write(json.dumps(self.__channel_config))
