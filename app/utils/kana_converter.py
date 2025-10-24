"""
かな変換ユーティリティ

ひらがなをカタカナに変換する機能を提供します。
"""


def hiragana_to_katakana(text: str) -> str:
    """
    ひらがなをカタカナに変換

    Args:
        text: 変換対象のテキスト

    Returns:
        カタカナに変換されたテキスト
    """
    if not text:
        return text

    # ひらがな→カタカナ変換テーブル
    hiragana = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょっゎゐゑ'
    katakana = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォャュョッヮヰヱ'

    # 変換マップを作成
    conv_map = str.maketrans(hiragana, katakana)

    return text.translate(conv_map)
