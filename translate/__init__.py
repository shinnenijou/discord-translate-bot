from .baidu import BaiduTranslator
from .tencent import TencentTranslator

TRANSLATORS_MAP = {
    'baidu': BaiduTranslator,
    'tencent': TencentTranslator
}