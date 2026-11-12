# Shared helpers for T4 bank expansion (TEG-authored practice items)
import json, html
AUD = {}  # set id -> (lang, dialogues)

def E(id_txt, en_txt):
    return {'id': id_txt, 'en': en_txt}

def M(prompt, opts, group=None, explain=None):
    """Multiple choice; first option is the key (options are shuffled at runtime)."""
    q = {'type': 'mcq', 'prompt': prompt, 'options': opts, 'answer': 0}
    if group: q['group'] = group
    if explain: q['explain'] = explain
    return q

LAB = {'ja': '{}ばん。', 'ko': '{}번.', 'zh': '第{}题。'}
WHO = {'ja': {'M': '男', 'F': '女'}, 'ko': {'M': '남자', 'F': '여자'}, 'zh': {'M': '男', 'F': '女'}}

def listen_set(sid, title, instr, lang, items, qs, folder, extra=None):
    import re
    qt = [re.sub(r'^\d+\.\s*', '', re.sub('<[^>]+>', '', q.get('prompt', ''))) for q in qs]
    tr = ''
    for i, d in enumerate(items, 1):
        qq = qt[i - 1] if i - 1 < len(qt) else ''
        tr += f'<b>{LAB[lang].format(i)}</b><br>' + (f'<i>🔊 {html.escape(qq)}</i><br>' if qq else '') + ''.join(f'{WHO[lang][s]}: {html.escape(t)}<br>' for s, t in d) + (f'<i>🔊 {html.escape(qq)}</i><br>' if qq else '') + '<br>'
    AUD[sid] = (lang, items, qt)
    o = {'id': sid, 'title': title, 'audio': f'audio/{folder}/{sid}.mp3', 'instructions': instr, 'transcript': tr, 'questions': qs}
    if extra: o.update(extra)
    return o

# voices vary per set (male/female pairs alternate) - T4c
VOICES = {
 'ja': [('ja-JP-KeitaNeural', 'ja-JP-NanamiNeural'), ('ja-JP-DaichiNeural', 'ja-JP-AoiNeural'), ('ja-JP-NaokiNeural', 'ja-JP-MayuNeural')],
 'ko': [('ko-KR-InJoonNeural', 'ko-KR-SunHiNeural'), ('ko-KR-HyunsuNeural', 'ko-KR-JiMinNeural'), ('ko-KR-BongJinNeural', 'ko-KR-SeoHyeonNeural')],
 'zh': [('zh-CN-YunxiNeural', 'zh-CN-XiaoxiaoNeural'), ('zh-CN-YunjianNeural', 'zh-CN-XiaoyiNeural'), ('zh-CN-YunyangNeural', 'zh-CN-XiaochenNeural')],
}
NAR = {'ja': 'ja-JP-ShioriNeural', 'ko': 'ko-KR-YuJinNeural', 'zh': 'zh-CN-XiaohanNeural'}
XL = {'ja': 'ja-JP', 'ko': 'ko-KR', 'zh': 'zh-CN'}

def ssml(sid, lang, items, k, rate='-8%', qt=None):
    m, f = VOICES[lang][k % len(VOICES[lang])]
    qt = qt or []
    x = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{XL[lang]}'>"
    for i, d in enumerate(items, 1):
        qq = html.escape(qt[i - 1]) if i - 1 < len(qt) else ''
        x += f"<voice name='{NAR[lang]}'><prosody rate='{rate}'>{LAB[lang].format(i)}{qq}</prosody><break time='700ms'/></voice>"
        for s, t in d:
            x += f"<voice name='{m if s == 'M' else f}'><prosody rate='{rate}'>{html.escape(t)}</prosody><break time='500ms'/></voice>"
        x += f"<voice name='{NAR[lang]}'><break time='300ms'/><prosody rate='{rate}'>{qq}</prosody><break time='2500ms'/></voice>"
    return x + '</speak>'

def save_audio_json(path, rate='-8%'):
    out = {sid: ssml(sid, v[0], v[1], k, rate, v[2]) for k, (sid, v) in enumerate(AUD.items())}
    json.dump(out, open(path, 'w'), ensure_ascii=False)
    return out
