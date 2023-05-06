import random
import hashlib
from time import time

import aiohttp
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

    def __make_params(self, _q: str, _from: str, _to: str):
        salt = str(random.randint(10000000, 99999999))

        params = {
            'from': _from,
            'to': _to,
            'appid': self.__id,
            'salt': salt,
            'sign': self.__make_sign(q, salt),
            'q': _q
        }

        return params

    def __make_headers(self, **kwargs):
        return {}

    def __make_sign(self, q: str, salt: str):
        sign = hashlib.md5((self.__id + q + salt + self.__key).encode('utf-8'))
        return sign.hexdigest()

    def __parse_response(self, data:dict) -> (int, list[str]):
        result = int(data.get('error_code', self.EResult.SUCCESS))
        if result != self.EResult.SUCCESS:
            return result, []

        text = [item['dst'] for item in data['trans_result']]
        return result, text

    async def translate(self, _src: list[str], _from: str = 'auto', _to: str = 'zh') -> list[str]:
        q = '\n'.join([s for s in _src])
        result, dst = await self.__translate(_q=q, _from=_from, _to=_to)
        if result != self.EResult.SUCCESS:
            utils.log_error(f"[error]翻译失败: {self.ErrorString.get(result, '未知错误')}")
            return []

        return dst

    def validate_config(self):
        params = self.__make_params('', 'auto', 'zh')
        resp = requests.get(url=self.__api, params=params)
        if resp.status_code != 200:
            return False

        result, _ = self.__parse_response(resp.json())

        return result == self.EResult.EMPTYPARAM
