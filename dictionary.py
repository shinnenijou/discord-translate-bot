REPLACE_MAP = {
    'メディア': 'ミリヤ',
    'ミディア': 'ミリヤ',
    'みや': 'ミリヤ',
    'みーや': 'ミリヤ',
    'ミーヤ': 'ミリヤ',
    '宮': 'ミリヤ',
    '星熊売る': '星熊ウル',
    'ワンシャンハオ': 'こんばんは',
}

PUNCTUATION = {
    '？': True,
    '?': True,
    '！': True,
    '!': True,
}

NO_MEANING_PUNCTUATION = {
    '。': True,
    '.': True,
    '，': True,
    ',': True
}

KATAKANA = {
    'ア': True, 'イ': True, 'ウ': True, 'エ': True, 'オ': True,
    'カ': True, 'キ': True, 'ク': True, 'ケ': True, 'コ': True,
    'サ': True, 'シ': True, 'ス': True, 'セ': True, 'ソ': True,
    'タ': True, 'チ': True, 'ツ': True, 'テ': True, 'ト': True,
    'ナ': True, 'ニ': True, 'ヌ': True, 'ネ': True, 'ノ': True,
    'ハ': True, 'ヒ': True, 'フ': True, 'ヘ': True, 'ホ': True,
    'マ': True, 'ミ': True, 'ム': True, 'メ': True, 'モ': True,
    'ヤ': True, 'ユ': True, 'ヨ': True,
    'ラ': True, 'リ': True, 'ル': True, 'レ': True, 'ロ': True,
    'ワ': True, 'ヲ': True,
    'ン': True,

    'ガ': True, 'ギ': True, 'グ': True, 'ゲ': True, 'ゴ': True,
    'ザ': True, 'ジ': True, 'ズ': True, 'ゼ': True, 'ゾ': True,
    'ダ': True, 'ヂ': True, 'ヅ': True, 'デ': True, 'ド': True,
    'バ': True, 'ビ': True, 'ブ': True, 'ベ': True, 'ボ': True,
    'パ': True, 'ピ': True, 'プ': True, 'ペ': True, 'ポ': True,

    'キャ': True, 'キュ': True, 'キョ': True,
    'ギャ': True, 'ギュ': True, 'ギョ': True,
    'シャ': True, 'シュ': True, 'ショ': True,
    'ジャ': True, 'ジュ': True, 'ジョ': True,
    'ニャ': True, 'ニュ': True, 'ニョ': True,
    'ミャ': True, 'ミュ': True, 'ミョ': True,
    'リャ': True, 'リュ': True, 'リョ': True,

    'ァ': True, 'ィ': True, 'ゥ': True, 'ェ': True, 'ォ': True,
    'ッ': True,
    'ャ': True, 'ュ': True, 'ョ': True,
}

HIRAGANA = {
    'あ': True, 'い': True, 'う': True, 'え': True, 'お': True,
    'か': True, 'き': True, 'く': True, 'け': True, 'こ': True,
    'さ': True, 'し': True, 'す': True, 'せ': True, 'そ': True,
    'た': True, 'ち': True, 'つ': True, 'て': True, 'と': True,
    'な': True, 'に': True, 'ぬ': True, 'ね': True, 'の': True,
    'は': True, 'ひ': True, 'ふ': True, 'へ': True, 'ほ': True,
    'ま': True, 'み': True, 'む': True, 'め': True, 'も': True,
    'や': True, 'ゆ': True, 'よ': True,
    'ら': True, 'り': True, 'る': True, 'れ': True, 'ろ': True,
    'わ': True, 'を': True,
    'ん': True,

    'が': True, 'ぎ': True, 'ぐ': True, 'げ': True, 'ご': True,
    'ざ': True, 'じ': True, 'ず': True, 'ぜ': True, 'ぞ': True,
    'だ': True, 'ぢ': True, 'づ': True, 'で': True, 'ど': True,
    'ば': True, 'び': True, 'ぶ': True, 'べ': True, 'ぼ': True,
    'ぱ': True, 'ぴ': True, 'ぷ': True, 'ぺ': True, 'ぽ': True,

    'きゃ': True, 'きゅ': True, 'きょ': True,
    'ぎゃ': True, 'ぎゅ': True, 'ぎょ': True,
    'しゃ': True, 'しゅ': True, 'しょ': True,
    'じゃ': True, 'じゅ': True, 'じょ': True,
    'にゃ': True, 'にゅ': True, 'にょ': True,
    'みゃ': True, 'みゅ': True, 'みょ': True,
    'りゃ': True, 'りゅ': True, 'りょ': True,

    'ぁ': True, 'ぃ': True, 'ぅ': True, 'ぇ': True, 'ぉ': True,
    'っ': True,
    'ゃ': True, 'ゅ': True, 'ょ': True,
}

NO_MEANING_WORDS = {
    'はい': True, 'よし': True, 'んー': True, 'ああ': True, 'やあ': True, 'うん': True, 'えっ': True, 'ねえ': True,
    'わー': True, 'うーん': True,
}

NG_WORDS = {
    'Amara.org': True,
}