# Listening standardisation (JLPT N5/N4 'l', HSK 1-3, TOPIK I, JLPT N3-N1 概要理解/統合理解).
#   python3 t5_std.py ssml   -> scratchpad/std_ssml.txt + STD_groups.json (sets per TTS file)
#   python3 t5_std.py apply  -> split TTS files, compose HSK (each item twice), update banks
import json, sys, re, html, os, subprocess
sys.path.insert(0, '/home/claude/w91')
from t4_common import VOICES, NAR
R = '/home/claude/teg-tutorial/mocktest/'
SP = '/tmp/claude-0/-home-claude/7600d9ee-aee0-5a14-abd7-7540cbf5f3d4/scratchpad/'
XL = {'ja': 'ja-JP', 'ko': 'ko-KR', 'zh': 'zh-CN'}
SPK = {'男': 'M', '女': 'F', '남자': 'M', '여자': 'F'}
LAB = {'ja': '{}ばん。', 'ko': '{}번.', 'zh': '第{}题。'}
# sets whose audio does not match the slot's standard (found in the audit): regenerate
TARGET = {('jlpt', 'n5l'): 'L5abcd', ('jlpt', 'n4l'): 'L4abcd', ('topik', 'listening'): 'TLabcd'}
HSK_SECS = ('h1l', 'h2l', 'h3l')
HSK_NOTE = '每题听两次。'

def esc(t): return html.escape(t, quote=False)
def load(t): return json.load(open(R + f'banks/{t}.json', encoding='utf-8'))

def items_of(st):
    blocks = re.split(r'<b>[^<]*</b>', st['transcript'])[1:]
    out = []
    for q, b in zip(st['questions'], blocks):
        lines = [re.sub('<[^>]+>', '', l).strip() for l in re.split(r'<br\s*/?>', b)]
        dlg = [(SPK[l.split(':')[0]], html.unescape(l.split(': ', 1)[1])) for l in lines if l.split(':')[0] in SPK]
        qp = re.sub(r'<small>.*?</small>', '', q['prompt'])
        qp = re.sub(r'\s*[（(][^)）]*[A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ][^)）]*[)）]', '', qp)  # drop pinyin / romanisation
        out.append((dlg, re.sub(r'^\d+\.\s*', '', re.sub('<[^>]+>', '', qp)).strip()))
    return out

def jobs():
    J = []  # (test, sec, set, lang, kind)
    for (t, sec), ids in TARGET.items():
        lang = 'ja' if t == 'jlpt' else 'ko'
        s = [x for x in load(t)['sections'] if x['id'] == sec][0]
        for st in s['slots'][0]['sets']:
            if st['id'][-1] in ids[2:]: J.append((t, sec, st, lang, 'qdq'))
    for s in load('hsk')['sections']:
        if s['id'] in HSK_SECS:
            for st in s['slots'][0]['sets']: J.append(('hsk', s['id'], st, 'zh', 'hsk'))
    return J

def ssml_set(k, st, lang, kind):
    m, f = VOICES[lang][k % 3]; nar = NAR[lang]; v = {'M': m, 'F': f}
    x, tr = '', ''
    for i, (dlg, q) in enumerate(items_of(st), 1):
        lab = LAB[lang].format(i)
        if kind == 'qdq':
            x += f"<voice name='{nar}'>{lab}{esc(q)}<break time='800ms'/></voice>"
            tr += f'<b>{lab}</b><br><i>🔊 {esc(q)}</i><br>'
        else:
            x += f"<voice name='{nar}'>{lab}<break time='600ms'/></voice>"
            tr += f'<b>{lab}</b><br>'
        for s, t in dlg:
            x += f"<voice name='{v[s]}'>{esc(t)}<break time='500ms'/></voice>"
            tr += f"{ {'ja': {'M': '男', 'F': '女'}, 'ko': {'M': '남자', 'F': '여자'}, 'zh': {'M': '男', 'F': '女'}}[lang][s]}: {esc(t)}<br>"
        if kind == 'qdq':
            x += f"<voice name='{nar}'>{esc(q)}<break time='2500ms'/></voice>"
            tr += f'<i>🔊 {esc(q)}</i><br><br>'
        else:  # HSK: question asked after the dialogue; whole item is played twice (composed after TTS)
            x += f"<voice name='{nar}'>问：{esc(q)}<break time='3600ms'/></voice>"
            tr += f'<i>🔊 问：{esc(q)}</i><br><i>（{HSK_NOTE[:-1]} · 2×）</i><br><br>'
    if kind == 'qdq': x = re.sub(r"<break time='2500ms'/></voice>$", "<break time='6000ms'/></voice>", x)
    return x, tr

def ao_sets():
    out = []
    for lv in ('t3_n3', 't3_n2', 't3_n1'):
        sys.argv = ['t3_build.py', 'none', lv]
        src = open('/home/claude/w91/t3_build.py').read().replace("{'bank': bank, 'ssml': ssml}[sys.argv[1]]()", '')
        g = {'__name__': 'x'}; exec(compile(src, 't3_build', 'exec'), g)
        sets, aud = g['listening_sets']()
        ids = {st['id'] for sl, st in sets if sl in g['AO']}
        out += [(sid, x.replace("<break time='3600ms'/></voice>", "<break time='6000ms'/></voice>")) for sid, x in aud if sid in ids]
    return out

def group(entries, lang):
    gs, cur, n, size = [], [], 0, 0
    for sid, x in entries:
        vv = x.count('<voice')
        if cur and (n + vv > 48 or size + len(x) > 4300): gs.append(cur); cur, n, size = [], 0, 0
        cur.append((sid, x)); n += vv; size += len(x)
    if cur: gs.append(cur)
    return [(lang, g) for g in gs]

def cmd_ssml():
    J = jobs(); E = {'qdq_ja': [], 'qdq_ko': [], 'hsk': []}
    meta = {}
    for k, (t, sec, st, lang, kind) in enumerate(J):
        x, tr = ssml_set(k, st, lang, kind)
        E['hsk' if kind == 'hsk' else f'qdq_{lang}'].append((st['id'], x)); meta[st['id']] = {'test': t, 'sec': sec, 'kind': kind, 'transcript': tr, 'n': len(st['questions'])}
    G = group(E['qdq_ja'] + ao_sets(), 'ja') + group(E['qdq_ko'], 'ko') + group(E['hsk'], 'zh')
    json.dump({'groups': [[s for s, _ in g] for _, g in G], 'meta': meta, 'hsk': [s for s, _ in E['hsk']]}, open('/home/claude/w91/STD_groups.json', 'w'), ensure_ascii=False)
    with open(SP + 'std_ssml.txt', 'w') as o:
        for i, (lang, g) in enumerate(G):
            body = ''.join(x for _, x in g)
            o.write(f"===== SG{i} {lang} ({len(body)} chars, {body.count('<voice')} voices): {','.join(s for s, _ in g)}\n<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{XL[lang]}'>{body}</speak>\n")
    print(len(J), 'sets +', len(ao_sets()), 'JLPT 概要/統合 sets in', len(G), 'groups')

def silences(src, sd):
    r = subprocess.run(['ffmpeg', '-i', src, '-af', f'silencedetect=noise=-45dB:d={sd}', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r); dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))
    return st, en, dur

def cut(src, a, b, dst):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{a:.2f}', '-to', f'{b:.2f}', '-i', src, '-ac', '1', '-ar', '24000', '-c:a', 'pcm_s16le', dst], check=True)

def enc(src, dst):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', 'loudnorm=I=-18:TP=-2', '-ac', '1', '-ar', '24000', '-b:a', '64k', dst + '.tmp.mp3'], check=True)
    os.replace(dst + '.tmp.mp3', dst)

def cmd_apply():
    S = json.load(open('/home/claude/w91/STD_groups.json')); meta = S['meta']; hs = set(S['hsk'])
    subprocess.run(['git', '-C', R + '..', 'fetch', '-q', 'origin', 'tts-audio:refs/remotes/origin/tts-audio'], check=True)
    T = SP + 'std/'; os.makedirs(T, exist_ok=True)
    done = {}
    for gi, ids in enumerate(S['groups']):
        src = f'{T}SG{gi}.mp3'
        open(src, 'wb').write(subprocess.run(['git', '-C', R + '..', 'show', f'origin/tts-audio:mock-std/SG{gi}.mp3'], capture_output=True, check=True).stdout)
        if ids[0] in hs:  # split into items (3.6 s gaps), each set = n items
            st, en, dur = silences(src, 3.3); n_items = sum(meta[s]['n'] for s in ids)
            print(f'SG{gi} hsk items={n_items} gaps={len(st)}')
            assert len(st) in (n_items - 1, n_items), st
            starts = [0.0] + en; k = 0
            for sid in ids:
                parts = []
                for j in range(meta[sid]['n']):
                    a = max(0, starts[k] - 0.15) if k else 0.0; b = st[k] + 0.3 if k < len(st) else dur
                    w = f'{T}{sid}_{j}.wav'; cut(src, a, b, w); parts.append(w); k += 1
                # compose: item, 1.5 s, item again, 3 s (each item twice, like the official HSK recording)
                lst = f'{T}{sid}.txt'; sil = f'{T}sil15.wav'; sil3 = f'{T}sil30.wav'
                for d, f in ((1.5, sil), (3.0, sil3)):
                    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono', '-t', str(d), '-c:a', 'pcm_s16le', f], check=True)
                open(lst, 'w').write(''.join(f"file '{p}'\nfile '{sil}'\nfile '{p}'\nfile '{sil3}'\n" for p in parts))
                full = f'{T}{sid}_full.wav'
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', full], check=True)
                dst = R + f'audio/hsk/v2/{sid}.mp3'; os.makedirs(os.path.dirname(dst), exist_ok=True); enc(full, dst); done[sid] = f'audio/hsk/v2/{sid}.mp3'
        else:
            st, en, dur = silences(src, 4.5); print(f'SG{gi} sets={len(ids)} gaps={len(st)}')
            assert len(st) in (len(ids) - 1, len(ids)), st
            starts = [0.0] + en
            for k, sid in enumerate(ids):
                a = max(0, starts[k] - 0.15) if k else 0.0; b = st[k] + 0.3 if k < len(st) else dur
                t = meta[sid]['test'] if sid in meta else 'jlpt'
                w = f'{T}{sid}.wav'; cut(src, a, b, w)
                dst = R + f'audio/{t}/v2/{sid}.mp3'; os.makedirs(os.path.dirname(dst), exist_ok=True); enc(w, dst); done[sid] = f'audio/{t}/v2/{sid}.mp3'
    # update banks (JLPT 概要/統合 sets are already written by t3_build with v2 paths)
    for t in ('jlpt', 'hsk', 'topik'):
        j = load(t); ch = 0
        for s in j['sections']:
            for sl in s['slots']:
                for st in sl['sets']:
                    if st['id'] in meta and st['id'] in done:
                        st['audio'] = done[st['id']]; st['transcript'] = meta[st['id']]['transcript']; ch += 1
                        if meta[st['id']]['kind'] == 'hsk' and HSK_NOTE not in st['instructions']: st['instructions'] = st['instructions'].rstrip('。') + '。' + HSK_NOTE
        json.dump(j, open(R + f'banks/{t}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(t, 'updated sets', ch)
    print('files', len(done))

{'ssml': cmd_ssml, 'apply': cmd_apply}[sys.argv[1]]()
