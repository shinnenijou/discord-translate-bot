from configparser import RawConfigParser

from .const import *


def log_error(msg: str):
    pass


def log_info(msg: str):
    pass


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
        while len(text) <= text_max_length:
            texts.append(prefix + text[:text_max_length] + suffix)
            text = text[text_max_length:]

    return texts
