import os

import openai

import utils
from .translator import Translator


if os.getenv('GLOBAL_PROXY', ''):
    openai.proxy = {
        'http': os.getenv('PROXY'),
        'https': os.getenv('PROXY')
    }


class GPTTranslator(Translator):
    class EResult:
        Success = 0
        Error = 1

    ErrorString = {

    }

    Language = {
        'zh': "Simplified Chinese",
        'jp': "Japanese",
        'en': "English"
    }

    instance = {}

    def __new__(cls, *args, **kwargs):
        if len(args) > 1:
            _key = args[1]
        else:
            _key = kwargs.get('_key', '')

        if _key not in cls.instance:
            cls.instance[_key] = object.__new__(cls)

        return cls.instance[_key]

    def __init__(self, _id: str, _key: str):
        api = ""
        super().__init__(_api=api, _id=_id, _key=_key,
                         rate_limit_type=Translator.RateLimitPeriod.QPM,
                         rate_limit=3500)

    def _make_params(self, _q: str, _from: str, _to: str):
        return

    def _make_headers(self, **kwargs):
        return

    def _make_sign(self, q: str, salt: str):
        return

    def _parse_response(self, data: dict) -> (int, list[str]):
        return

    async def translate(self, _src: list[str], _from: str = 'jp', _to: str = 'zh') -> list[str]:
        if _from not in self.Language or _to not in self.Language:
            utils.logger.log_error(f"[GPT]Translate Failed: Language not support, {_from}->{_to})")
            return []

        contents = []
        src_text = "\n".join(_src)

        await self.wait_for_queue()

        # chat completion choices to generate default to 1, thus we have at least
        try:
            openai.api_key = self.key

            resp = await openai.ChatCompletion.acreate(
                model=self.id,
                messages=[
                    {"role": "user", "content": f"Translate this into {self.Language[_to]}: \n\n{src_text}"}
                ]
            )
        except Exception as e:
            utils.logger.log_error(f"[GPT]Translate Failed: {src_text}, due to {e})")
            return []

        choices = resp.get('choices')
        for choice in choices:
            content = choice.get('message').get('content')
            if content.isascii():
                continue

            contents.append(content)

        total_token = resp.get('usage', {}).get('total_tokens', 0)
        utils.logger.log_info(f'[GPT]Translate: {_src[0]} -> {contents[0]}, token: {total_token}')

        return contents

    def _validate_config(self):
        try:
            openai.api_key = self.key

            resp = openai.ChatCompletion.create(
                model=self.id,
                messages=[
                    {"role": "user", "content": "Hello"}
                ]
            )
        except Exception as e:
            utils.logger.log_error(f"[GPT]Validate Failed: {e})")
            return False

        choice = resp.get('choices')[0]
        content = choice.get('message', {}).get('content')

        total_token = resp.get('usage', {}).get('total_tokens', 0)
        utils.logger.log_info(f'[GPT]Validate: Hello -> {content}, token: {total_token}')

        return True
