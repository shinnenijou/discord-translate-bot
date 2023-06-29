import openai

import utils
from .translator import Translator


class GPTTranslator(Translator):
    class EResult:
        Success = 0
        Error = 1

    ErrorString = {

    }

    instance = {}

    def __new__(cls, *args, **kwargs):
        if len(args) > 0:
            _id = args[0]
        else:
            _id = kwargs.get('_id', '')

        if _id not in cls.instance:
            cls.instance[_id] = object.__new__(cls)

        return cls.instance[_id]

    def __init__(self, _id: str, _key: str):
        api = ""
        super().__init__(_api=api, _id=_id, _key=_key,
                         rate_limit_type=Translator.RateLimitPeriod.QPM,
                         rate_limit=3)

    def _make_params(self, _q: str, _from: str, _to: str):
        return

    def _make_headers(self, **kwargs):
        return

    def _make_sign(self, q: str, salt: str):
        return

    def _parse_response(self, data: dict) -> (int, list[str]):
        return

    async def translate(self, _src: list[str], _from: str = 'jp', _to: str = 'zh') -> list[str]:
        src_text = "\n".join(_src)

        openai.api_key = self.key
        resp = openai.ChatCompletion.create(
            model=self.id,
            messages=[
                {"role": "user", "content": f"Translate this into Chinese: \n\n{src_text}"}
            ]
        )

        contents = []
        result = self.EResult.Error
        choices = resp.get('choices')
        for choice in choices:
            message = choice.get('message')
            contents.append(message.get('content'))
            result = self.EResult.Success

        if result != self.EResult.Success:
            utils.logger.log_error(f"翻译失败: {self.ErrorString.get(result, f'未知错误 {result}')}")

        return contents

    def _validate_config(self):
        openai.api_key = self.key
        resp = openai.ChatCompletion.create(
            model=self.api,
            messages=[
                {"role": "user", "content": f"Hello"}
            ]
        )

        result, dst = self._parse_response(resp)
        print(dst)

        return result == self.EResult.Success
