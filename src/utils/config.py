import os
import json
import dotenv


DATA_PATH = "./data"
dotenv.load_dotenv(os.path.join(DATA_PATH, ".env"))


class Config:
    __instance = None

    # 功能拓展
    __VALID_FIELDS = {
        'room_id': '',
        'sessdata': '',
        'bili_jct': '',
        'buvid3': '',
        'running': False,
        'api': '',
        'send': '',  # 'live', 'webhook'
        'webhook_url': '',
        'send_lag': '',
        'language': '',
    }

    # 运行基本功能所必须的字段, 如果没有配置这些字段, 则应当拒绝启动
    __REQUIRE_FIELDS = {
        'api': '',
        'send': '',
    }

    __LIVE_FIELDS = {
        'sessdata': '',
        'bili_jct': '',
        'buvid3': '',
        'room_id': '',
    }

    __WEBHOOK_FIELDS = {
        'webhook_url': ''
    }

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__filename = os.path.join(DATA_PATH, 'config.json')

        if not os.path.exists(self.__filename):
            with open(self.__filename, 'w') as file:
                file.write("{}")

        with open(self.__filename, 'r') as file:
            self.__channel_config = json.loads(file.read())

        self.__api_config = {}
        # 默认的API ID/KEY都从环境变量中读取
        if os.getenv("BAIDU_ID", None) is not None and os.getenv("BAIDU_KEY", None) is not None:
            self.__api_config['baidu'] = (os.getenv("BAIDU_ID"), os.getenv("BAIDU_KEY"))

        if os.getenv("TENCENT_ID", None) is not None and os.getenv("TENCENT_KEY", None) is not None:
            self.__api_config['tencent'] = (os.getenv("TENCENT_ID"), os.getenv("TENCENT_KEY"))

        if os.getenv("OPENAI_ID", None) is not None and os.getenv("OPENAI_KEY", None) is not None:
            self.__api_config['openai'] = (os.getenv("OPENAI_ID"), os.getenv("OPENAI_KEY"))

    def save(self):
        with open(self.__filename, 'w') as file:
            file.write(json.dumps(self.__channel_config, indent=4))

    def reload(self):
        with open(self.__filename, 'r') as file:
            self.__channel_config = json.loads(file.read())

    def get_api_keys(self, api_name: str) -> tuple[str, str]:
        return self.__api_config.get(api_name.lower(), ('', ''))

    def get_user_config(self, channel: str, user: str, key: str, _fallback: any = None) -> dict:
        return self.__channel_config.get(channel, {}).get(user, {}).get(key, _fallback)

    def get_user(self, channel: str, user: str) -> dict:
        return self.__channel_config.get(channel, {}).get(user, {})

    def get_channel(self, channel: str) -> dict:
        return self.__channel_config.get(channel, {})

    def get_all_channels(self):
        return self.__channel_config

    # 只检查是否配置了必须字段, 不对字段内容有效性进行检查(使用者自行检查)
    def is_user_config_valid(self, channel: str, user: str) -> bool:
        user_config = self.get_user(channel, user)

        for key, value in self.__REQUIRE_FIELDS.items():
            if key not in user_config:
                return False

        if user_config['send'] == 'live':
            for key, value in self.__LIVE_FIELDS.items():
                if key not in user_config:
                    return False
        elif user_config['send'] == 'webhook':
            for key, value in self.__WEBHOOK_FIELDS.items():
                if key not in user_config:
                    return False
        else:
            return False

        return True

    def set_user_config(self, channel: str, user: str, key: str, value: str) -> bool:
        if key not in self.__VALID_FIELDS:
            return False

        if channel not in self.__channel_config:
            self.__channel_config[channel] = {}

        if user not in self.__channel_config[channel]:
            self.__channel_config[channel][user] = {}
            self.__channel_config[channel][user]['running'] = False
            self.__channel_config[channel][user]['api'] = 'baidu'

        self.__channel_config[channel][user][key] = value

        self.save()

    def rename_user(self, channel: str, old_name: str, new_name: str):
        if old_name == new_name:
            return

        if channel not in self.__channel_config:
            return

        if old_name not in self.__channel_config[channel]:
            return

        self.__channel_config[channel][new_name] = self.__channel_config[channel][old_name]
        del self.__channel_config[channel][old_name]

        self.save()


config = Config()
