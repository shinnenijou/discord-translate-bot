import random
import hashlib
import asyncio
from time import time

import aiohttp

import utils
from .enums import *


class BaiduTranslator:
    def __init__(self, _appid: str, _key: str, _timeout_sec: int = 1800):
        self.__appid = _appid
        self.__key = _key
        self.__timeout_sec = _timeout_sec
        self.__session = self.__session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.__timeout_sec))
        self.__timer = 0

    def init(self):
        if not self.validate_config():
            print("[error]翻译器配置错误, 请检查翻译器设置")
            return False

        return True

    async def __get(self, url: str, _params: dict):
        cur_time = int(time())
        if cur_time > self.__timer:
            if self.__session is not None:
                await self.__session.close()
            self.__session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.__timeout_sec))
            self.__timer = cur_time + self.__timeout_sec - 60

        result = EResult.ERROR
        resp = None
        try:
            async with self.__session.get(url, params=_params) as resp:
                if resp.status == 200:
                    result = EResult.SUCCESS
                    resp = await resp.json()
                else:
                    resp = None
        except aiohttp.ClientConnectionError:
            pass
        except aiohttp.ServerTimeoutError:
            pass
        except aiohttp.ClientError:
            pass

        return result, resp

    async def __translate(self, _texts: list[str], _from: str = 'auto', _to: str = 'zh'):
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

        result, data = await self.__get(api, params)
        if result != EResult.SUCCESS:
            return result, []

        result = int(data.get('error_code', EResult.SUCCESS))

        return result, [item.get('dst', '') for item in data.get('trans_result', [])]

    async def translate(self, _texts: list[str], _from: str = 'auto', _to: str = 'zh'):
        result, texts = await self.__translate(_texts, _from, _to)
        if result != EResult.SUCCESS:
            utils.log_error(f"[error]翻译失败, 错误代码: {result}")
            return []

        return texts

    async def validate_config(self):
        result, _ = asyncio.get_event_loop().run_until_complete(self.__translate([""]))
        return result == EResult.EMPTYPARAM
