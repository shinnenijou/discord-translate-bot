from abc import ABC, abstractmethod
from time import time
from asyncio import sleep, Lock
from queue import Queue

import aiohttp

import utils


class Translator(ABC):
    class CommonResult:
        REQUEST_SUCCESS = 0
        REQUEST_ERROR = 1

    CommonErrorString = {
        CommonResult.REQUEST_SUCCESS: "本地请求成功",
        CommonResult.REQUEST_ERROR: "本地请求错误"
    }

    class RateLimitPeriod:
        QPS = 1
        QPM = 60

    def __init__(self, _api: str, _id: str, _key: str,
                 rate_limit_type: int,
                 rate_limit:int,
                 _timeout_sec: int = 1800):
        self.__api = _api
        self.__id = _id
        self.__key = _key
        self.__timeout_sec = _timeout_sec
        self.__session = None
        self.__timer = 0

        # rate limit control
        self.__query_queue = Queue(maxsize=rate_limit)
        self.__query_period = rate_limit_type * 1000 + 200
        self.__query_lock = Lock()

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

    # rate limit control
    async def wait_for_queue(self):

        await self.__query_lock.acquire()

        while self.__query_queue.full():
            elapse = utils.get_ms_time() - self.__query_queue.get()

            if elapse <= self.__query_period:
                utils.logger.log_info("请求频率超过限制...等待重置计时...")
                wait_time = self.__query_period - elapse
                await sleep(wait_time / 1000)

        self.__query_lock.release()
        self.__query_queue.put(utils.get_ms_time())

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

        await self.wait_for_queue()

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

    async def _translate(self, headers: dict, params: dict) -> (int, list[str]):
        result, data = await self._get(self.__api, headers=headers, params=params)
        if result != self.CommonResult.REQUEST_SUCCESS:
            return result, []

        return self._parse_response(data)

    @abstractmethod
    async def translate(self, _texts: list[str], _from: str, _to: str) -> list[str]:
        pass

    @abstractmethod
    def _validate_config(self) -> bool:
        pass
