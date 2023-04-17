class ESendResult:
    """
    发送结果枚举,
    """
    Error = -1
    Success = 0
    HighFrequency = 10030         # 弹幕发送频率过高
    DuplicateMsg = 10031          # 短期内发送了两条内容完全相同的弹幕
    Unknown = 11000               # 弹幕被吞了（具体原因未知）
    RoomNotExist = 19002001       # 直播间不存在


class EDanmakuPosition:
    Roll = 1
    Bottom = 4
    Top = 5


class EDanmakuColor:
    White = 16777215
