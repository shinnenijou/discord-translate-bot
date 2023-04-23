from configparser import RawConfigParser
import asyncio

from .const import *


def log_error(msg: str):
    print("[ERROR]" + msg)


def log_info(msg: str):
    print("[INFO]" + msg)


def check_config(config: RawConfigParser) -> bool:
    for field, _dict in CONFIG_FIELDS.items():
        if not config.has_section(field):
            return False

        for option, _ in _dict.items():
            if not config.has_option(field, option):
                return False

    return True


def slice_text(text: str, max_length: int = 20, prefix: str = '【', suffix: str = '】') -> list:
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

def replace(text: str) -> str:
    text.replace('メディア', 'ミリヤ')
    text.replace('ミディア', 'ミリヤ')

    return text
