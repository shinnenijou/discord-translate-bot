import random
import hashlib

import requests

import utils
from .translator import Translator


class BaiduTranslator(Translator):
    class EResult:
        SUCCESS = 52000
        TIMEOUT = 52001
        SERVERERROR = 52002
        UNAUTHUSER = 52003
        EMPTYPARAM = 54000
        SIGNERROR = 54001
        FREQLIMIT = 54003
        CREDITNOTENOUGH = 54004
        LONGQUERY = 54005
        ILLLEGALIPADDR = 58000
        LANGUAGENOTSUPPORT = 58001
        SERVICECLOSED = 58002
        AUTHNOTPASS = 90107

    ErrorString = {
        EResult.TIMEOUT: '请求超时',
        EResult.SERVERERROR: '系统错误',
        EResult.UNAUTHUSER: '未授权用户',
        EResult.EMPTYPARAM: '必填参数为空',
        EResult.SIGNERROR: '签名错误',
        EResult.FREQLIMIT: '访问频率受限',
        EResult.CREDITNOTENOUGH: '账户余额不足',
        EResult.LONGQUERY: '长query请求频繁',
        EResult.ILLLEGALIPADDR: '客户端IP非法',
        EResult.LANGUAGENOTSUPPORT: '译文语言方向不支持',
        EResult.SERVICECLOSED: '服务已关闭',
        EResult.AUTHNOTPASS: '认证未通过或未生效'
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
        api = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        super().__init__(_api=api, _id=_id, _key=_key,
                         rate_limit_type=Translator.RateLimitPeriod.QPS,
                         rate_limit=10)

    def _make_params(self, _q: str, _from: str, _to: str):
        salt = str(random.randint(10000000, 99999999))

        params = {
            'from': _from,
            'to': _to,
            'appid': self.id,
            'salt': salt,
            'sign': self._make_sign(_q, salt),
            'q': _q
        }

        return params

    def _make_headers(self, **kwargs):
        return {}

    def _make_sign(self, q: str, salt: str):
        sign = hashlib.md5((self.id + q + salt + self.key).encode('utf-8'))
        return sign.hexdigest()

    def _parse_response(self, data: dict) -> (int, list[str]):
        result = int(data.get('error_code', self.EResult.SUCCESS))
        if result != self.EResult.SUCCESS:
            return result, []

        text = [item['dst'] for item in data['trans_result']]
        return result, text

    async def translate(self, _src: list[str], _from: str = 'jp', _to: str = 'zh') -> list[str]:
        q = '\n'.join(_src)
        headers = self._make_headers()
        params = self._make_params(q, _from, _to)
        result, dst = await self._translate(headers, params)
        if result != self.EResult.SUCCESS:
            utils.logger.log_error(f"翻译失败: {self.ErrorString.get(result,  f'未知错误 {result}')}")
            return []

        return dst

    def _validate_config(self):
        params = self._make_params('hello', 'en', 'zh')
        resp = requests.get(url=self.api, params=params)
        if resp.status_code != 200:
            return False

        result, _ = self._parse_response(resp.json())

        return result == self.EResult.SUCCESS
