DISCORD_FIELDS = {
    'token': ''
}

BAIDU_FIELDS = {
    'id': '',
    'key': ''
}

TENCENT_FIELDS = {
    'id': '',
    'key': ''
}

BILIBILI_FIELDS = {
    'room_id': '',
    'sessdata': '',
    'bili_jct': '',
    'buvid3': ''
}

CONFIG_FIELDS = {
    'discord': DISCORD_FIELDS,
    'baidu': BAIDU_FIELDS,
    'tencent': TENCENT_FIELDS,
}

SEND_INTERVAL = 1
SEND_LAG = 3


class ECommandResult:
    Success = 0
    Failed = 1
    NoConfig = 2
    InvalidParams = 3
    InvalidAPI = 4
    FailedStartDanmaku = 5
    FailedStartTranslator = 6
    ChannelRunning = 7
    SuccessSet = 8
    UnknownCommand = 9
    SuccessStart = 10
    SuccessStop = 11
    GetUserInfoError = 12
    GetDanmakuConfigError = 13


CommandResultString = {
    ECommandResult.SuccessStart: "Successfully Started.",
    ECommandResult.SuccessStop: "Successfully Stopped.",
    ECommandResult.NoConfig: "Please set config before starting(requires bilibili account cookies / user/ room_id).",
    ECommandResult.InvalidParams: "Param Error. Syntax: !SET <key> <value>.",
    ECommandResult.InvalidAPI: "Invalid API. Now only support baidu and tencent.",
    ECommandResult.FailedStartDanmaku: "Failed to start Danmaku Sender. Please check bilibili account cookies again.",
    ECommandResult.FailedStartTranslator: "Failed to start Translator. Please check API id and key again.",
    ECommandResult.ChannelRunning: "Cannot set config while running. Please stop firstly.",
    ECommandResult.SuccessSet: "Successfully set config.",
    ECommandResult.UnknownCommand: "Unknown Command.",
    ECommandResult.GetUserInfoError: "Failed to get user info. Please check bilibili account cookies again.",
    ECommandResult.GetDanmakuConfigError: "Failed to get danmaku config. Please check bilibili room_id again."
}