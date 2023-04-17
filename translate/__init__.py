from queue import Queue
import random
import hashlib

import requests
from requests import exceptions

import utils
from .enums import *


class BaiduTranslator:
    def __init__(self, _appid: str, _key: str):
        self.__appid = _appid
        self.__key = _key

    def init(self):
        if not self.validate_config():
            print("[error]翻译器配置错误, 请检查翻译器设置")
            return False

        return True

    @staticmethod
    def __get(url: str, _params: dict):
        result = EResult.ERROR
        resp = None
        try:
            resp = requests.get(url, params=_params)

            if resp.status_code == 200:
                result = EResult.SUCCESS
                resp = resp.json()
            else:
                resp = None
        except exceptions.ConnectionError:
            pass
        except exceptions.Timeout:
            pass

        return result, resp

    def __translate(self, _texts: list[str], _from: str = 'auto', _to: str = 'zh'):
        api = "https://fanyi-api.baidu.com/api/trans/vip/translate"

        salt = str(random.randint(10000000, 99999999))
        q = '\n'.join([s for s in _texts])
        sign = hashlib.md5((self.__appid + q + salt + self.__key).encode('utf-8'))
        params = {
            'from': _from,
            'to': _to,
            'appid': self.__appid,
            'salt': salt,
            'sign': sign.hexdigest(),
            'q': q
        }

        result, data = self.__get(api, params)
        if result != EResult.SUCCESS:
            return result, []

        result = int(data.get('error_code', 0))

        return result, [item.get('dst', '') for item in data.get('trans_result', [])]

    def translate(self, _texts: list[str], _from: str = 'auto', _to: str = 'zh'):
        result, texts = self.__translate(_texts, _from, _to)
        if result != EResult.SUCCESS:
            utils.log_error(f"[error]翻译失败, 错误代码: {result}")
            return []

        return texts

    def validate_config(self):
        result, _ = self.__translate([""])
        return result == EResult.EMPTYPARAM
