class EResult:
    ERROR = -1
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
    EResult.ERROR: '本地请求错误',
    EResult.SUCCESS: '成功',
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