import hashlib, hmac
from time import strftime, gmtime, time
from urllib.parse import urlencode

import requests

import utils
from .translator import Translator


class TencentTranslator(Translator):
    class EResult:
        Success = 'OK'
        LanguageRecognitionErr = 'FailedOperation.LanguageRecognitionErr'

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
        #api = "https://tmt.ap-tokyo.tencentcloudapi.com"
        api = "https://tmt.ap-beijing.tencentcloudapi.com"
        #api = "https://tmt.tencentcloudapi.com"
        super().__init__(_api=api, _id=_id, _key=_key,
                         rate_limit_type=Translator.RateLimitPeriod.QPS,
                         rate_limit=5)

        self.__headers = {
            'Host': 'tmt.tencentcloudapi.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-TC-Action': 'TextTranslate',
            'X-TC-Version': '2018-03-21',
            'X-TC-Region': 'ap-shanghai',
        }

        self.__service = 'tmt'
        self.__algorithm = 'TC3-HMAC-SHA256'

        http_request_method = 'GET'
        canonical_uri = '/'
        canonical_headers = \
            f"content-type:{self.__headers['Content-Type'].lower()}\n" + \
            f"host:{self.__headers['Host'].lower()}\n" + \
            f"x-tc-action:{self.__headers['X-TC-Action'].lower()}\n"
        signed_headers = 'content-type;host;x-tc-action'
        hashed_request_payload = self.__hash_sha256('')

        self.__canonical_request_prefix = \
            http_request_method + '\n' +\
            canonical_uri + '\n'

        self.__canonical_request_suffix = '\n' +\
            canonical_headers + '\n' +\
            signed_headers + '\n' +\
            hashed_request_payload

    def _make_params(self, _q: str, _from: str, _to: str):
        params = {
            'SourceText': _q,
            'Source': _from,
            'Target': _to,
            'ProjectId': 0,
        }

        return params

    def _make_headers(self, params: dict) -> dict:
        self.__headers['X-TC-Timestamp'] = str(int(time()))
        self.__headers['Authorization'] = self._make_sign(self.__headers, params)

        return self.__headers

    def _make_sign(self, headers: dict, params: dict) -> str:
        date = strftime('%Y-%m-%d', gmtime(int(headers['X-TC-Timestamp'])))

        canonical_request = self.__canonical_request(params)
        string_to_sign = self.__sign_string(headers, date, canonical_request)

        secret_date = self.__hmac_sha256(('TC3' + self.key).encode(encoding='utf-8'), date).digest()
        secret_service = self.__hmac_sha256(secret_date, self.__service).digest()
        secret_signing = self.__hmac_sha256(secret_service, 'tc3_request').digest()

        authorization = \
            self.__algorithm + ' ' + \
            f"Credential={self.id}/{date}/{self.__service}/tc3_request, " + \
            "SignedHeaders=content-type;host;x-tc-action, " + \
            f"Signature={self.__hmac_sha256(secret_signing, string_to_sign).hexdigest()}"

        return authorization

    def _parse_response(self, data:dict) -> (int, list[str]):
        result = data.get('Response', {}).get('Error', {}).get('Code', self.EResult.Success)
        if result != self.EResult.Success:
            return result, []

        text = data.get('Response', {}).get('TargetText', '').split()
        return result, text

    async def translate(self, _src: list[str], _from: str = 'ja', _to: str = 'zh') -> list[str]:
        q = '\n'.join(_src)
        params = self._make_params(q, _from, _to)
        headers = self._make_headers(params)
        result, dst = await self._translate(headers, params)
        if result != self.EResult.Success:
            utils.logger.log_error(f"翻译失败: {self.ErrorString.get(result, f'未知错误 {result}')}")
            return []

        return dst

    def _validate_config(self):
        params = self._make_params('hello', 'en', 'zh')
        headers = self._make_headers(params)
        resp = requests.get(url=self.api, headers=headers, params=params)
        if resp.status_code != 200:
            return False

        result, _ = self._parse_response(resp.json())

        return result == self.EResult.Success

    def __canonical_request(self, params: dict) -> str:
        canonical_query_string = urlencode(params)
        return self.__canonical_request_prefix + canonical_query_string + self.__canonical_request_suffix

    def __sign_string(self, headers: dict, date: str, canonical_query_string: str) -> str:
        algorithm = self.__algorithm
        requests_timestamp = headers['X-TC-Timestamp']
        credential_scope = f"{date}/{self.__service}/tc3_request"
        hashed_canonical_request = self.__hash_sha256(canonical_query_string)

        string_to_sign = \
            algorithm + '\n' + \
            requests_timestamp + '\n' + \
            credential_scope + '\n' + \
            hashed_canonical_request

        return string_to_sign

    @staticmethod
    def __hmac_sha256(key: bytes, msg: str):
        return hmac.new(key, msg.encode(encoding='utf-8'), hashlib.sha256)

    @staticmethod
    def __hash_sha256(msg: str) -> str:
        return hashlib.sha256(msg.encode(encoding='utf-8')).hexdigest().lower()
