import os

import discord

from src import utils
from src.client import MyClient


def main():
    utils.logger.init(os.path.join(utils.DATA_PATH, "logs"))

    intents = discord.Intents.default()
    intents.message_content = True

    if os.getenv('PROXY', ''):
        client = MyClient(intents=intents, proxy=os.getenv('PROXY'))
    else:
        client = MyClient(intents=intents)

    if not client.init_command_handler():
        utils.logger.log_error("指令处理初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    client.init_channels()

    if not client.init_anti_shield():
        utils.logger.log_error("反屏蔽模块初始化失败, 请检查配置文件")
        utils.sync(client.close())
        return

    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()
