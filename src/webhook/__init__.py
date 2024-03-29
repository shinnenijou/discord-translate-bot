import asyncio
import os

import aiohttp

from src import utils


class WebhookSender:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__session = None
        self.__lock = asyncio.Lock()
        self.__message_queue = asyncio.Queue(maxsize=0)

        self.__name_map = {
            '308': '魔狼咪莉娅'
        }

    async def close(self):
        if self.__session is not None:
            await self.__session.close()

    async def send(self, url, name, content):
        if not url or not content:
            return

        if self.__session is None:
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=int(os.getenv('session_timeout', 5))))

        if name in self.__name_map:
            name = self.__name_map[name]

        send_request = (url, name, content)
        #await self.__message_queue.put(send_request)

        # sync lock
        #await self.__lock.acquire()

        #send_request = await self.__message_queue.get()

        payload = {
            'content': send_request[2],
            'username': send_request[1]
        }

        try:
            async with self.__session.post(send_request[0], json=payload, proxy=os.getenv('PROXY', None)) as resp:
                pass
        except Exception as e:
            utils.logger.log_error("[WebhookSender:send]" + str(e))

        #self.__lock.release()
