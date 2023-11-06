import asyncio
from time import time

import aiohttp
import requests

from src import utils
from src.utils import ECommandResult
from .enums import *


class DanmakuSender:

    instance = {}

    def __new__(cls, *args, **kwargs):
        if len(args) > 0:
            _sessdata = args[0]
        else:
            _sessdata = kwargs.get('_sessdata', '')

        if _sessdata not in cls.instance:
            cls.instance[_sessdata] = object.__new__(cls)

        return cls.instance[_sessdata]

    def __init__(self, _sessdata: str, _bili_jct: str, _buvid3: str, _timeout_sec: int = 5):
        # requests config
        self.__url = "https://api.live.bilibili.com/msg/send"
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30',
            'Origin': f'https://live.bilibili.com',
            'Referer': f'https://live.bilibili.com'
        }

        # account config
        self.__csrf = _bili_jct
        self.__cookies = {'buvid3': _buvid3, 'SESSDATA': _sessdata, 'bili_jct': _bili_jct}
        self.__timeout_sec = _timeout_sec
        self.__session = None

        # danmaku config
        self.__mode = EDanmakuPosition.Roll
        self.__color = EDanmakuColor.White
        self.__name = ''

        # send queue control
        self.__send_queue = asyncio.Queue(maxsize=0)
        self.__send_lock = asyncio.Lock()
        self.__last_time = 0

        self.__timer = 0

    def init(self, room_id: str):
        if self.get_user_info() == '':
            utils.logger.log_error("获取用户信息失败, 请检查配置文件或网络状态")
            return ECommandResult.GetUserInfoError

        if self.get_danmaku_config(room_id) == (None, None):
            utils.logger.log_error("获取弹幕配置失败, 请检查配置文件")
            return ECommandResult.GetDanmakuConfigError

        return ECommandResult.Success

    async def close(self):
        if self.__session is not None:
            await self.__session.close()
            self.__session = None

    async def __post(self, url: str, data: dict, headers: dict):
        """
        POST包装方法, 用于捕获异常
        :param url: 请求地址
        :param data: post数据
        :return: 返回结果枚举与响应体
        """

        if self.__session is None:
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.__timeout_sec),
                cookies=self.__cookies
            )

        result = ESendResult.Error
        payload = None
        try:
            async with self.__session.post(url=url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    result = ESendResult.Success
                    payload = await resp.json()
                else:
                    payload = None
        except Exception as e:
            utils.logger.log_error(f"[DanmakuSender.__post]Post request {data.get('msg', '')} error: {str(e)}")

        return result, payload

    async def __get(self, url: str, header: dict, params: dict = None):
        """
        GET包装方法, 用于捕获异常
        :param url: 请求地址
        :param params: 请求参数
        :return: 返回结果枚举与响应体
        """
        result = ESendResult.Error
        payload = None
        try:
            async with self.__session.get(url=url, header=header, params=params) as resp:

                if resp.status == 200:
                    result = ESendResult.Success
                    payload = await resp.json()
                else:
                    payload = None
        except Exception as e:
            utils.logger.log_error(f"[DanmakuSender.__get]Get request error: {str(e)}")

        return result, payload

    async def __send(self, room_id: str, msg: str) -> tuple[ESendResult, dict]:
        data = {
            "color": self.__color,
            "fontsize": 25,
            "mode": self.__mode,
            "bubble": 0,
            "msg": msg,
            "roomid": room_id,
            "rnd": int(time()),
            "csrf_token": self.__csrf,
            "csrf": self.__csrf,
        }

        headers = self.__headers.copy()
        headers['Referer'] = f'https://live.bilibili.com/{room_id}'

        result, resp = await self.__post(self.__url, data, headers)
        if result == ESendResult.Success:
            result = resp.get('code', ESendResult.Success)

        return result, resp

    async def send(self, room_id: str, msg: str):
        """
        向直播间发送弹幕
        :param room_id: 发送弹幕的直播间id
        :param msg: 待发送的弹幕内容
        :return: 服务器返回的响应体
        """
        task = {'room_id': room_id, 'message': msg}
        await self.__send_queue.put(task)
        await self.__send_lock.acquire()
        task = await self.__send_queue.get()

        cur_ms_time = utils.get_ms_time()
        next_send_time = self.__last_time + utils.SEND_INTERVAL * 1000
        if cur_ms_time < next_send_time:
            await asyncio.sleep((next_send_time - cur_ms_time) / 1000)

        result, resp = await self.__send(task['room_id'], task['message'])
        if result != ESendResult.Success:
            if result in ErrorString:
                utils.logger.log_error(f"[Danmaku]消息{task['message']}： {ErrorString[result]}")
            else:
                utils.logger.log_error(f"[Danmaku]消息{task['message']}：未知错误： {result}")

        self.__last_time = utils.get_ms_time()
        self.__send_lock.release()

        return True

    def get_name(self):
        return self.__name

    def get_danmaku_config(self, room_id: str):
        """获取用户在直播间内的当前弹幕颜色、弹幕位置、发言字数限制等信息"""
        url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByUser"
        params = {"room_id": room_id}
        try:
            resp = requests.get(url=url, headers=self.__headers, params=params, cookies=self.__cookies)
        except:
            return None, None

        if resp.status_code == 200 and resp.json()['code'] == ESendResult.Success:
            danmaku_config = resp.json()["data"]["property"]["danmu"]
            self.__mode = danmaku_config["mode"]
            self.__color = danmaku_config["color"]

        return self.__mode, self.__color

    def set_danmu_config(self, room_id: str, color=None, mode=None):
        """设置用户在直播间内的弹幕颜色或弹幕位置
        :（颜色参数为十六进制字符串，颜色和位置不能同时设置）"""
        url = "https://api.live.bilibili.com/xlive/web-room/v1/dM/AjaxSetConfig"
        data = {
            "room_id": room_id,
            "color": color,
            "mode": mode,
            "csrf_token": self.__csrf,
            "csrf": self.__csrf,
        }
        try:
            resp = requests.post(url=url, headers=self.__headers, cookies=self.__cookies, data=data)
        except:
            return ESendResult.Error

        if resp.status_code == 200 and resp.json()['code'] == ESendResult.Success:
            self.__mode = mode
            self.__color = color

        return resp.json()['code']

    def get_user_info(self):
        """获取用户信息"""
        url = "https://api.bilibili.com/x/space/myinfo"
        try:
            resp = requests.get(url=url, headers=self.__headers, cookies=self.__cookies)
        except:
            return ""

        if resp.status_code == 200 and resp.json()['code'] == ESendResult.Success:
            self.__name = resp.json()['data']['name']

        return self.__name
