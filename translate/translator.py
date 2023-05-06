from abc import ABC, abstractmethod
from time import time

import aiohttp


class Translator(ABC):
    class CommonResult:
        REQUEST_SUCCESS = 0
        REQUEST_ERROR = 1

    CommonErrorString = {
        CommonResult.REQUEST_SUCCESS: "本地请求成功",
        CommonResult.REQUEST_ERROR: "本地请求错误"
    }

    def __init__(self, _api: str, _id: str, _key: str, _timeout_sec: int = 1800):
        self.__api = _api
        self.__id = _id
        self.__key = _key
        self.__timeout_sec = _timeout_sec
        self.__session = None
        self.__timer = 0

    @property
    def api(self) -> str:
        return self.__api

    @property
    def id(self) -> str:
        return self.__id

    @property
    def key(self) -> str:
        return self.__key

    @property
    def timeout_sec(self) -> int:
        return self.__timeout_sec

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.__session

    @property
    def timer(self) -> int:
        return self.__timer

    def init(self):
        if not self._validate_config():
            print("[error]翻译器配置错误, 请检查翻译器设置")
            return False

        return True

    async def close(self):
        if self.__session is not None:
            await self.__session.close()

    @abstractmethod
    def _make_params(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def _make_headers(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def _make_sign(self, **kwargs) -> str:
        pass

    @abstractmethod
    def _parse_response(self, data:dict) -> (int, list[str]):
        pass

    async def _get(self, url: str, **kwargs) -> (int, dict):
        cur_time = int(time())
        if cur_time > self.__timer:
            if self.__session is not None:
                await self.__session.close()
            self.__session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.__timeout_sec))
            self.__timer = cur_time + self.__timeout_sec - 60

        _headers = kwargs.get('headers', {})
        _params = kwargs.get('params', {})

        result = self.CommonResult.REQUEST_ERROR
        resp = {}
        try:
            async with self.__session.get(url, headers=_headers, params=_params) as resp:
                if resp.status == 200:
                    result = self.CommonResult.REQUEST_SUCCESS
                    resp = await resp.json()
                else:
                    resp = {}
        except aiohttp.ClientConnectionError:
            pass
        except aiohttp.ServerTimeoutError:
            pass
        except aiohttp.ClientError:
            pass

        return result, resp

    async def _translate(self, **kwargs) -> (int, list[str]):
        headers = self._make_headers(**kwargs)
        params = self._make_params(**kwargs)

        result, data = await self._get(self.__api, headers=headers, params=params)
        if result != self.CommonResult.REQUEST_SUCCESS:
            return result, []

        result, texts = self._parse_response(data)

        return result, [item.get('dst', '') for item in data.get('trans_result', [])]

    @abstractmethod
    async def translate(self, _texts: list[str], _from: str = 'auto', _to: str = 'zh') -> list[str]:
        pass

    @abstractmethod
    def _validate_config(self) -> bool:
        pass
