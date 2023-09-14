from configparser import RawConfigParser
import asyncio
import time
import os

from .const import *
from .config import *

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
        self.__replace_words = {}
        self.__punctuation = {}
        self.__no_meaning_punctuation = {}
        self.__katakana = {}
        self.__hiragana = {}
        self.__no_meaning_words = {}
        self.__ng_words = {}
        self.load_words()

    def load_words(self):
        if not os.path.exists("dictionary.py"):
            return

        from dictionary import REPLACE_MAP, PUNCTUATION, NO_MEANING_PUNCTUATION, KATAKANA, HIRAGANA, NO_MEANING_WORDS, NG_WORDS

        self.__replace_words = {}
        for _old, _new in REPLACE_MAP.items():
            self.__replace_words[_old] = _new

        self.__punctuation = PUNCTUATION
        self.__no_meaning_punctuation = NO_MEANING_PUNCTUATION
        self.__katakana = KATAKANA
        self.__hiragana = HIRAGANA
        self.__no_meaning_words = NO_MEANING_WORDS
        self.__ng_words = NG_WORDS

    def deal(self, text: str) -> str:


        temp_text = text
        if text[-1] in self.__punctuation or text[-1] in self.__no_meaning_punctuation:
            temp_text = text[:-1]

        if temp_text in self.__katakana or temp_text in self.__hiragana or temp_text in self.__no_meaning_words:
            return ''

        if text[-1] in self.__no_meaning_punctuation:
            text = text[:-1]

        for word, _ in self.__ng_words.items():
            if text.find(word) != -1:
                return ''

        for _old, _new in self.__replace_words.items():
            text = text.replace(_old, _new)

        return text


text_processor = TextProcessor()
logger = Logger()
