# Build JLPT N3/N2/N1 sections into jlpt.json + grouped SSML for listening audio.
# usage: python3 t3_build.py bank t3_n3   |   python3 t3_build.py ssml t3_n3
import json, sys, html, importlib
B = '/home/claude/teg-tutorial/mocktest/banks/'
mod = importlib.import_module(sys.argv[2]); LV = mod.LV
try:  # T4 expansion modules (t3x_n3/n2/n1) extend the same lists
    ext = importlib.import_module(sys.argv[2].replace('t3_', 't3x_'))
    for k in ('v', 'g', 'rs', 'rm', 'rl', 'ri', 'ri2', 'L'):
        if hasattr(ext, k): setattr(mod, k, getattr(mod, k, []) + getattr(ext, k))
except ModuleNotFoundError:
    pass
CFG = {'N3': dict(secs=[('v', '言語知識（文字・語彙）', 30), ('g', '言語知識（文法）・読解', 70), ('l', '聴解', 40)], pass_=95),
       'N2': dict(secs=[('k', '言語知識（文字・語彙・文法）・読解', 105), ('l', '聴解', 50)], pass_=90),
       'N1': dict(secs=[('k', '言語知識（文字・語彙・文法）・読解', 110), ('l', '聴解', 55)], pass_=100)}[LV]
lk, rd, ch = LV + 'lk', LV + 'rd', LV + 'ch'
NAR = 'ja-JP-ShioriNeural'; MV = ['ja-JP-KeitaNeural', 'ja-JP-DaichiNeural', 'ja-JP-NaokiNeural']; FV = ['ja-JP-NanamiNeural', 'ja-JP-AoiNeural', 'ja-JP-MayuNeural']
WHO = {'M': '男', 'F': '女'}
def D(i, e): return {'id': i, 'en': e}

def listening_sets():
    out, aud = [], []
    for k, (slot, sid, items) in enumerate(mod.L):
        m, f = MV[k % 3], FV[k % 3]
        tr, x, qs = '', '', []
        for i, (scene, dlg, q) in enumerate(items, 1):
            qtext = q['prompt']
            say_q = scene if slot == 'l4' else ('' if slot == 'l5' else qtext)
            tr += f'<b>{i}番</b><br>' + (f'<i>🔊 {html.escape(say_q)}</i><br>' if say_q else '') + ''.join(f'{WHO[s]}: {html.escape(t)}<br>' for s, t in dlg) + (f'<i>🔊 {html.escape(qtext)}</i><br>' if slot in ('l1', 'l2', 'l3', 'l6') else '') + '<br>'
            x += f"<voice name='{NAR}'>{i}番。{html.escape(say_q, quote=False)}<break time='800ms'/></voice>"
            for s, t in dlg:
                x += f"<voice name='{m if s == 'M' else f}'>{html.escape(t, quote=False)}<break time='500ms'/></voice>"
            if slot in ('l1', 'l2', 'l3', 'l6'):
                x += f"<voice name='{NAR}'>{html.escape(qtext, quote=False)}<break time='1500ms'/></voice>"
            else:
                x += f"<voice name='{NAR}'><break time='700ms'/></voice>"
            q = dict(q); q['prompt'] = f'{i}. ' + q['prompt']; qs.append(q)
        import re as _re
        x = _re.sub(r"<break time='\d+ms'/></voice>$", "<break time='3600ms'/></voice>", x)
        aud.append((sid, x))
        out.append((slot, {'id': sid, 'title': mod.LI[slot] + ' ' + sid[-1].upper(), 'audio': f'audio/jlpt/{sid}.mp3', 'instructions': mod.INS[slot], 'transcript': tr, 'questions': qs}))
    return out, aud

def bank():
    d = json.load(open(B + 'jlpt.json', encoding='utf-8'))
    d['sections'] = [s for s in d['sections'] if not s['id'].startswith(LV.lower())]
    d['fulls'] = [f for f in d['fulls'] if f['id'] != LV]
    ls, _ = listening_sets()
    lslots = []
    for slot in sorted(mod.LI):
        sets = [s for sl, s in ls if sl == slot]
        if sets: lslots.append({'id': slot, 'title': mod.LI[slot], 'count': 1, 'sets': sets})
    rslots = [{'id': 'rs', 'title': '内容理解（短文）', 'count': 1, 'sets': mod.rs}, {'id': 'rm', 'title': '内容理解（中文）', 'count': 1, 'sets': mod.rm}]
    if getattr(mod, 'rl', None): rslots.append({'id': 'rl', 'title': '内容理解（長文）', 'count': 1, 'sets': mod.rl})
    if getattr(mod, 'ri2', None): rslots.append({'id': 'rt', 'title': '統合理解・主張理解', 'count': 1, 'sets': mod.ri2})
    rslots.append({'id': 'ri', 'title': '情報検索', 'count': 1, 'sets': mod.ri})
    nr = sum(len(s['sets'][0]['questions']) for s in rslots)
    new = []
    if LV == 'N3':
        new.append({'id': 'n3v', 'title': f'{LV} · 言語知識（文字・語彙）', 'minutes': 30, 'auto': True, 'skill': lk, 'desc': D(f'{len(mod.v[0]["questions"])*2} soal kanji, kosakata & makna (2 set acak).', f'{len(mod.v[0]["questions"])*2} kanji & vocabulary items (2 random sets).'),
                    'slots': [{'id': 'v', 'title': '文字・語彙', 'count': 2, 'sets': mod.v}], 'score': {'type': 'pct'}})
        new.append({'id': 'n3g', 'title': f'{LV} · 言語知識（文法）・読解', 'minutes': 70, 'auto': True, 'skill': [lk, rd], 'skill_by_slot': {'g': lk, 'rs': rd, 'rm': rd, 'rl': rd, 'ri': rd},
                    'desc': D(f'Tata bahasa ({len(mod.g[0]["questions"])*2} soal) + 4 bacaan (pendek, sedang, panjang, 情報検索).', f'Grammar ({len(mod.g[0]["questions"])*2} items) + 4 readings (short, mid, long, information retrieval).'),
                    'slots': [{'id': 'g', 'title': '文法', 'count': 2, 'sets': mod.g}] + rslots, 'score': {'type': 'pct'}})
    else:
        new.append({'id': LV.lower() + 'k', 'title': f'{LV} · 言語知識（文字・語彙・文法）・読解', 'minutes': CFG['secs'][0][2], 'auto': True, 'skill': [lk, rd], 'skill_by_slot': {'v': lk, 'g': lk, 'rs': rd, 'rm': rd, 'rl': rd, 'rt': rd, 'ri': rd},
                    'desc': D(f'Kosakata ({len(mod.v[0]["questions"])*2}) + tata bahasa ({len(mod.g[0]["questions"])*2}) + bacaan.', f'Vocabulary ({len(mod.v[0]["questions"])*2}) + grammar ({len(mod.g[0]["questions"])*2}) + reading.'),
                    'slots': [{'id': 'v', 'title': '文字・語彙', 'count': 2, 'sets': mod.v}, {'id': 'g', 'title': '文法', 'count': 2, 'sets': mod.g}] + rslots, 'score': {'type': 'pct'}})
    lm = CFG['secs'][-1][2]
    new.append({'id': LV.lower() + 'l', 'title': f'{LV} · 聴解（Listening）', 'minutes': lm, 'auto': True, 'skill': ch, 'desc': D(f'{len(lslots)} tipe soal resmi, {len(lslots)*2} soal, audio diputar 1 kali.', f'{len(lslots)} official task types, {len(lslots)*2} items, audio plays once.'),
                'slots': lslots, 'score': {'type': 'pct'}})
    d['sections'] += new
    order = {'n5': 0, 'n4': 1, 'n3': 2, 'n2': 3, 'n1': 4}
    d['sections'].sort(key=lambda s: order.get(s['id'][:2], 9))
    idx = [i for i, s in enumerate(d['sections']) if s['id'].startswith(LV.lower())]
    d['fulls'].append({'id': LV, 'title': {'id': f'JLPT {LV} - Full mock test', 'en': f'JLPT {LV} - Full mock test'}, 'sections': idx,
                       'report': {'skills': [{'id': lk, 'label': '言語知識（文字・語彙・文法）', 'full': 60, 'min': 19}, {'id': rd, 'label': '読解', 'full': 60, 'min': 19}, {'id': ch, 'label': '聴解', 'full': 60, 'min': 19}], 'pass': CFG['pass_']}})
    # recompute section indexes of all fulls after sorting
    ids = [s['id'] for s in d['sections']]
    for f in d['fulls']:
        pre = f['id'].lower()
        f['sections'] = [i for i, x in enumerate(ids) if x.startswith(pre)]
    d['fulls'].sort(key=lambda f: order.get(f['id'].lower(), 9))
    json.dump(d, open(B + 'jlpt.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('sections', ids, 'fulls', [(f['id'], f['sections']) for f in d['fulls']])

def ssml():
    _, aud = listening_sets()
    groups, cur, size = [], [], 0
    for sid, x in aud:
        if cur and size + len(x) > 4300: groups.append(cur); cur, size = [], 0
        cur.append((sid, x)); size += len(x)
    if cur: groups.append(cur)
    json.dump([[s for s, _ in g] for g in groups], open(f'/home/claude/w91/{LV}_groups.json', 'w'))
    for gi, g in enumerate(groups):
        print(f'===== {LV}G{gi}: ' + ','.join(s for s, _ in g))
        print("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>" + ''.join(x for _, x in g) + '</speak>')

{'bank': bank, 'ssml': ssml}[sys.argv[1]]()
