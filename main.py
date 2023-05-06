import discord
from configparser import RawConfigParser

import utils
from client import MyClient


def main():
    config = RawConfigParser()
    config.read('config.ini')
    if not utils.check_config(config):
        utils.log_error("[error]配置文件错误, 请检查配置文件")
        return

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    if not client.init_channel_config(config):
        utils.log_error("[error]频道设置初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    if not client.init_command_handler():
        utils.log_error("[error]指令处理初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    if not client.init_translator():
        utils.log_error("[error]翻译模块初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    if not client.init_danmaku_sender():
        utils.log_error("[error]弹幕模块初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    if not client.init_anti_shield():
        utils.log_error("[error]反屏蔽模块初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    token = config['discord']['token']
    client.run(token)


if __name__ == '__main__':
    main()
