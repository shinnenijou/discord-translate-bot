import json, hashlib, hmac, asyncio, queue
from time import strftime, gmtime, time
import random

import requests, aiohttp

import utils
from .translator import Translator


class TencentTranslator(Translator):
    class EResult:
        SUCCESS = 52000

    ErrorString = {

    }

    def __init__(self, _id: str, _key: str):
        api = "https://tmt.ap-tokyo.tencentcloudapi.com"
        super().__init__(_api=api, _id=_id, _key=_key)

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

    def _parse_response(self, data:dict) -> (int, list[str]):
        result = int(data.get('error_code', self.EResult.SUCCESS))
        if result != self.EResult.SUCCESS:
            return result, []

        text = [item['dst'] for item in data['trans_result']]
        return result, text

    async def translate(self, _src: list[str], _from: str = 'auto', _to: str = 'zh') -> list[str]:
        q = '\n'.join([s for s in _src])
        result, dst = await self._translate(_q=q, _from=_from, _to=_to)
        if result != self.EResult.SUCCESS:
            utils.log_error(f"[error]翻译失败: {self.ErrorString.get(result, '未知错误')}")
            return []

        return dst

    def _validate_config(self):
        params = self._make_params('', 'auto', 'zh')
        resp = requests.get(url=self.api, params=params)
        if resp.status_code != 200:
            return False

        result, _ = self._parse_response(resp.json())

        return result == self.EResult.EMPTYPARAM




# Request HEADERS
# Timestamp and authorization will be appended after
TEXT_TRANSLATE_HEADERS = {
    'Host': 'tmt.tencentcloudapi.com',
    'Content-Type': 'application/json; charset=utf-8',
    'X-TC-Action': 'TextTranslate',
    'X-TC-Version': '2018-03-21',
    'X-TC-Region': f'{REGION}',
    #
}


# Sign function
def _cononical_request(headers: dict, signed_headers: str, payload: str) -> str:
    ret = \
        'POST' + '\n' + \
        '/' + '\n' + \
        '' + '\n'
    for key in sorted(headers.keys()):
        ret += f'{key.lower()}:{headers[key].lower()}' + '\n'
    ret += '\n' + signed_headers + '\n'
    ret += hashlib.sha256(payload.encode()).hexdigest().lower()
    return ret


def _string_to_sign(
        algorithm: str,
        timestamp: str,
        date: str,
        service: str,
        cononicalRequest: str) -> str:
    ret = \
        algorithm + '\n' + \
        timestamp + '\n' + \
        f'{date}/{service}/tc3_request' + '\n'
    ret += hashlib.sha256(cononicalRequest.encode()).hexdigest().lower()
    return ret


def _sign(
        secret_key: str,
        date: str,
        service: str,
        string_to_sign: str) -> str:
    def hmac_sha256(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode(encoding='utf-8'), hashlib.sha256).digest()

    secret_date = hmac_sha256(('TC3' + secret_key).encode(), date)
    secret_service = hmac_sha256(secret_date, service)
    secret_signing = hmac_sha256(secret_service, 'tc3_request')
    signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature.lower()


def _authorization(
        algorithm: str,
        secret_id: str,
        secret_key: str,
        timestamp: str,
        service: str,
        headers: dict,
        payload: str):
    date = strftime('%Y-%m-%d', gmtime(int(timestamp)))
    cred = date + '/' + service + '/tc3_request'
    signed_headers = ';'.join(key.lower() for key in sorted(headers.keys()))
    cononical_request = _cononical_request(headers, signed_headers, payload)
    string_to_sign = _string_to_sign(algorithm, timestamp, date, service, cononical_request)
    signature = _sign(secret_key, date, service, string_to_sign)
    auth = \
        algorithm + ' ' + \
        'Credential=' + secret_id + '/' + cred + ', ' + \
        'SignedHeaders=' + signed_headers + ', ' + \
        'Signature=' + signature
    return auth


def _make_payload(sourceText: str, source: str, target: str, projectID: int = 0) -> str:
    return json.dumps({'SourceText': sourceText, 'Source': source,
                       'Target': target, 'ProjectId': projectID})


def _make_headers(payload: str) -> dict:
    # Append timestamp
    timestamp = str(int(time()))
    headers = TEXT_TRANSLATE_HEADERS.copy()
    headers['X-TC-Timestamp'] = timestamp
    headers['Authorization'] = _authorization(
        algorithm=SIGN_ALGORITHM,
        secret_id=SECRETID,
        secret_key=SECRETKEY,
        timestamp=timestamp,
        service=SERVICE,
        headers=headers,
        payload=payload
    )
    return headers


class TranslateTasker():

    def __init__(self, source: str, target: str, source_texts: list[str]):
        self.source = source
        self.target = target
        self.source_texts = source_texts
        self.task_queue = queue.Queue()
        self.target_texts = [""] * len(source_texts)
        self.session = aiohttp.ClientSession(timeout=TIMEOUT)
        for i in range(len(source_texts)):
            self.task_queue.put(i)

    async def post(self):
        task_id = self.task_queue.get()
        payload = _make_payload(self.source_texts[task_id], self.source, self.target)
        headers = _make_headers(payload)
        async with self.session.post(url=ENDPOINT, data=payload, headers=headers) as resp:
            try:
                self.target_texts[task_id] = (await resp.json())['Response']['TargetText']
            except:
                logger.error(f'翻译No.{task_id}发生错误, 等待重试')
                self.task_queue.put(task_id)
        return self

    async def post_all(self):
        while self.task_queue.qsize() > LIMIT_PER_SECOND:
            tasks = []
            for _ in range(LIMIT_PER_SECOND):
                tasks.append(asyncio.create_task(self.post()))
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)
        tasks = []
        for _ in range(self.task_queue.qsize()):
            tasks.append(asyncio.create_task(self.post()))
        await asyncio.gather(*tasks)
        return self

    def get_target_texts(self):
        return self.target_texts

    async def close(self):
        await self.session.close()


async def translate(source: str, target: str, *source_texts) -> list[str]:
    tasker = TranslateTasker(source, target, source_texts)
    await tasker.post_all()
    target_texts = tasker.get_target_texts()
    await tasker.close()
    return target_texts