import asyncio
import os

import aiohttp

import discord

import utils
from utils import ECommandResult, config
from translate import TRANSLATORS_MAP
from bilibili import DanmakuSender, BiliLiveAntiShield, words, rules
from webhook import WebhookSender


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__translators = {}
        self.__danmaku_senders = {}
        self.__anti_shield = None
        self.__channel_config = {}
        self.__command_handler = {}
        self.__webhook_sender = WebhookSender()

    async def close(self) -> None:
        await super().close()

        if not self.__translators:
            for translator in self.__translators.values():
                await translator.close()

        if not self.__danmaku_senders:
            for danmaku_sender in self.__danmaku_senders.values():
                await danmaku_sender.close()

        await self.__webhook_sender.close()

    async def on_ready(self):
        pass

    async def on_message(self, message):
        elapse = utils.get_ms_time()

        if message.author == self.user:
            return

        content = message.content.strip()

        if content == '':
            return

        if content[0] == '!':
            result = await self.__handle_command(content, message)
            if result in utils.CommandResultString:
                await message.channel.send(utils.CommandResultString[result])
            return

        channel_id = str(message.channel.id)
        user = message.author.name

        if not config.get_user_config(channel_id, user, 'running', False):
            return

        language = config.get_user_config(channel_id, user, 'language', "jp->zh").split('->')

        if len(language) < 2:
            return

        contents = []

        for line in message.content.splitlines():
            contents.append(utils.text_processor.deal(line))

        if len(contents) == 0:
            return

        dst_texts = await self.__translators[channel_id].translate(contents, language[0], language[1])

        for i in range(len(dst_texts)):
            if dst_texts[i][-1] == '。':
                dst_texts[i] = dst_texts[i][:-1]

            dst_texts[i] = self.__anti_shield.deal(dst_texts[i])

        if config.get_user_config(channel_id, user, 'send', 'live') == 'live':
            # Wait for lag
            send_lag = int(config.get_user_config(channel_id, user, 'send_lag', utils.SEND_LAG))
            elapse = (utils.get_ms_time() - elapse) / 1000
            if elapse < send_lag:
                await asyncio.sleep(send_lag - elapse)

            for dst_text in dst_texts:
                texts = utils.slice_text(dst_text)

                for text in texts:
                    await self.__danmaku_senders[channel_id].send(
                        config.get_user_config(channel_id, user, 'room_id'), text)
        elif config.get_user_config(channel_id, user, 'send', 'live') == 'webhook':
            for dst_text in dst_texts:
                await self.__webhook_sender.send(
                    config.get_user_config(channel_id, user, 'webhook_url', ''), user, dst_text)

    async def __handle_command(self, content, message):
        if len(content) < 2:
            return ECommandResult.UnknownCommand

        command = content[1:].split(' ')[0].upper()
        if command in self.__command_handler:
            return await self.__command_handler[command](message)

        return ECommandResult.UnknownCommand

    def init_channels(self):
        for channel, channel_config in config.get_all_channels().items():
            for user, user_config in channel_config.items():

                if not user_config.get('running', False):
                    continue

                if not config.is_user_config_valid(channel, user):
                    config.set_user_config(channel, user, 'running', False)

                api = channel_config.get('api', 'baidu')

                if api not in TRANSLATORS_MAP:
                    continue

                self.__translators[channel] = TRANSLATORS_MAP[api](config.get_api_keys(api)[0], config.get_api_keys(api)[1])
                if not self.__translators[channel].init():
                    del self.__translators[channel]
                    config.set_user_config(channel, user, 'running', False)
                    continue

                utils.logger.log_info(f'[Successfully]Translator for {user} is ready.')

                if config.get_user_config(channel, user, 'send') == 'live':
                    _room_id = channel_config.get('room_id')
                    _sessdata = channel_config.get('sessdata')
                    _bili_jct = channel_config.get('bili_jct')
                    _buvid3 = channel_config.get('buvid3')

                    self.__danmaku_senders[channel] = DanmakuSender(_sessdata, _bili_jct, _buvid3)
                    if self.__danmaku_senders[channel].init(_room_id) != ECommandResult.Success:
                        del self.__translators[channel]
                        del self.__danmaku_senders[channel]
                        config.set_user_config(channel, user, 'running', False)
                        continue

                    utils.logger.log_info(f'[Successfully]Danmaku sender for {user}({_room_id}) started.')
                elif config.get_user_config(channel, user, 'send') == 'webhook':
                    utils.logger.log_info(f'[Successfully]Webhook for {user} started.')

        return True

    def init_anti_shield(self):
        self.__anti_shield = BiliLiveAntiShield(rules, words)
        return True

    def init_command_handler(self):
        self.__command_handler["SET"] = self.__set_config
        self.__command_handler["START"] = self.__start_user
        self.__command_handler["STOP"] = self.__stop_user
        self.__command_handler["QUERY"] = self.__query_setting
        self.__command_handler["RENAME"] = self.__rename

        return True

    async def __start_user(self, message):
        channel_id = str(message.channel.id)
        params = message.content.strip().split()[1:]

        if len(params) > 0:
            users = params
        else:
            users = []
            for user in config.get_channel(channel_id).keys():
                users.append(user)

        for user in users:
            if not config.get_user(channel_id, user):
                return ECommandResult.NoConfig

            if config.get_user_config(channel_id, user, 'running', False):
                return ECommandResult.SuccessStart

            if not config.is_user_config_valid(channel_id, user):
                return ECommandResult.NoConfig

            if config.get_user_config(channel_id, user, 'api') not in TRANSLATORS_MAP:
                return ECommandResult.InvalidAPI

        for user in users:
            api = config.get_user_config(channel_id, user, 'api')
            self.__translators[channel_id] = TRANSLATORS_MAP[api](config.get_api_keys(api)[0], config.get_api_keys(api)[1])

            if not self.__translators[channel_id].init():
                del self.__translators[channel_id]
                return ECommandResult.FailedStartTranslator

            if config.get_user_config(channel_id, user, 'send') == 'live':
                room_id = config.get_user_config(channel_id, user, 'room_id')
                sessdata = config.get_user_config(channel_id, user, 'sessdata')
                bili_jct = config.get_user_config(channel_id, user, 'bili_jct')
                buvid3 = config.get_user_config(channel_id, user, 'buvid3')

                self.__danmaku_senders[channel_id] = DanmakuSender(sessdata, bili_jct, buvid3)
                result = self.__danmaku_senders[channel_id].init(room_id)

                if result != ECommandResult.Success:
                    del self.__danmaku_senders[channel_id]
                    del self.__translators[channel_id]
                    return result

                await message.channel.send(
                    f"User: {user}, API: {api}, Room: {room_id}, Sender: {self.__danmaku_senders[channel_id].get_user_info()}"
                )
            elif config.get_user_config(channel_id, user, 'send') == 'webhook':
                await message.channel.send(f"User: {user}, API: {api}, send to webhook")

            config.set_user_config(channel_id, user, 'running', True)

        return ECommandResult.SuccessStart

    async def __stop_user(self, message):
        channel_id = str(message.channel.id)
        params = message.content.strip().split()[1:]

        if len(params) > 0:
            users = params
        else:
            users = []
            for user in config.get_channel(channel_id).keys():
                users.append(user)

        for user in users:
            if not config.get_user(channel_id, user):
                continue

            if not config.get_user_config(channel_id, user, 'running', False):
                continue

            await self.__translators[channel_id].close()
            del self.__translators[channel_id]

            if config.get_user_config(channel_id, user, 'send') == 'live':
                await self.__danmaku_senders[channel_id].close()
                del self.__danmaku_senders[channel_id]
            elif config.get_user_config(channel_id, user, 'send') == 'webhook':
                pass

            config.set_user_config(channel_id, user, 'running', False)
            await message.channel.send(f"User: {user} stopped.")

        return ECommandResult.SuccessStop

    @staticmethod
    async def __set_config(message):
        params = message.content.strip().split()

        if len(params) <= 2:
            return ECommandResult.InvalidParams

        channel_id = str(message.channel.id)
        user = params[1]

        if config.get_user_config(channel_id, user, 'running', False):
            return ECommandResult.ChannelRunning

        for param in params:
            kv = param.split('=')
            if len(kv) < 2:
                continue

            config.set_user_config(channel_id, user, kv[0], kv[1])

        return ECommandResult.SuccessSet

    @staticmethod
    async def __rename(message):
        params = message.content.strip().split()

        if len(params) <= 2:
            return ECommandResult.InvalidParams

        channel_id = str(message.channel.id)
        old_name = params[1]
        new_name = params[2]

        if not config.get_user(channel_id, old_name):
            return ECommandResult.UserNotFount

        config.rename_user(channel_id, old_name, new_name)

        return ECommandResult.SuccessSet

    @staticmethod
    async def __query_setting(message):
        channel_id = str(message.channel.id)
        if channel_id not in config.get_all_channels():
            return ECommandResult.NoConfig

        msg = "[Channel Setting]\n"
        for user, user_config in config.get_channel(channel_id).items():
            msg += f"[{user}]\n"
            for key, value in user_config.items():
                msg += f"{key}: {value}\n"

            msg += "\n"

        if msg:
            await message.channel.send(msg)

        return ECommandResult.Success
