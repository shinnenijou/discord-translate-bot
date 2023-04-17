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
