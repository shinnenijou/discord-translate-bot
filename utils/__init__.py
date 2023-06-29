from configparser import RawConfigParser
import asyncio
import time
import os

from .const import *


class Logger:
    def __init__(self):
        self.__log_dir = None

    def init(self, dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        self.__log_dir = dir_path

    def log_error(self, msg: str):
        with open(os.path.join(self.__log_dir, f"{get_date()}.log"), "a") as file:
            file.write(f"[{get_hms_time()}][error]{msg}\n")

    def log_info(self,msg: str):
        with open(os.path.join(self.__log_dir, f"{get_date()}.log"), "a") as file:
            file.write(f"[{get_hms_time()}][info]{msg}\n")


def get_ms_time():
    return int(time.time() * 1000)


def get_date():
    return time.strftime("%Y-%m-%d", time.gmtime())


def get_hms_time():
    return time.strftime("%H-%M-%S", time.gmtime())


def check_config(config: RawConfigParser) -> bool:
    for field, _dict in CONFIG_FIELDS.items():
        if not config.has_section(field):
            return False

        for option, _ in _dict.items():
            if not config.has_option(field, option):
                return False

    return True


def slice_text(text: str, max_length: int = 20, prefix: str = '机翻【', suffix: str = '】') -> list:
    texts = []
    text_max_length = max_length - len(prefix) - len(suffix)
    if len(text) <= text_max_length:
        texts.append(prefix + text + suffix)
    else:
        while len(text) > text_max_length:
            texts.append(prefix + text[:text_max_length] + suffix)
            text = text[text_max_length:]

        texts.append(prefix + text + suffix)

    return texts


def sync(coroutine):
    return asyncio.get_event_loop().run_until_complete(coroutine)


class TextProcessor:
    def __init__(self):
        self.__words = {}
        self.load_words()

    def load_words(self):
        self.__words = {}
        from dictionary import REPLACE_MAP
        for _old, _new in REPLACE_MAP.items():
            self.__words[_old] = _new

    def deal(self, text: str) -> str:
        for _old, _new in self.__words.items():
            text = text.replace(_old, _new)

        return text


text_processor = TextProcessor()
logger = Logger()
