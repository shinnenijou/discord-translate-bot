from .baidu import BaiduTranslator
from .tencent import TencentTranslator
from .openai import GPTTranslator

TRANSLATORS_MAP = {
    'baidu': BaiduTranslator,
    'tencent': TencentTranslator,
    'openai': GPTTranslator
}