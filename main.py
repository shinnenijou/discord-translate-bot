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
    if not client.init_translator(config['baidu']['appid'], config['baidu']['key']):
        utils.log_error("[error]翻译模块初始化失败, 请检查配置文件")
        return

    bili_conf = config['bilibili']
    if not client.init_danmaku_sender(bili_conf['room_id'], bili_conf['sessdata'], bili_conf['bili_jct'], bili_conf['buvid3']):
        utils.log_error("[error]翻译模块初始化失败, 请检查配置文件")
        return

    token = config['discord']['token']
    client.run(token)


if __name__ == '__main__':
    main()
