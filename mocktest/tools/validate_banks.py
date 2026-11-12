#!/usr/bin/env python3
"""Validate TEG mock test banks (T4c): answer keys, duplicates, audio files, bank sizes.
Usage: python3 mocktest/tools/validate_banks.py [--table]
Exit code 1 when an error is found."""
import json, os, re, sys, collections, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANKS = ['ielts', 'pte', 'jlpt', 'topik', 'hsk']
errs, warns, rows = [], [], []

def plain(x):
    if isinstance(x, dict):
        x = x.get('en') or x.get('id') or ''
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(x or ''))).strip().lower()

def norm_opt(x):
    """Option text as a student sees it: HTML removed, NFKC (full/half width), no whitespace (incl. U+3000),
    no punctuation/symbols, lower case. Two options equal after this are duplicates."""
    if isinstance(x, dict): x = x.get('t') or x.get('v') or ''
    x = unicodedata.normalize('NFKC', re.sub(r'<[^>]+>', '', str(x)))
    x = ''.join(c for c in x if not c.isspace() and unicodedata.category(c)[0] not in 'PSZ')
    return x.lower()

def no_marks(x):
    # same text when dakuten/handakuten and other combining marks are ignored (e.g. は/ば) -> warning only
    return ''.join(c for c in unicodedata.normalize('NFD', x) if not unicodedata.combining(c))

def check_q(where, q):
    t = q.get('type')
    opts = q.get('options')
    if t == 'mcq':
        if not isinstance(opts, list) or len(opts) < 2: errs.append(f'{where}: mcq without options')
        elif not isinstance(q.get('answer'), int) or not 0 <= q['answer'] < len(opts): errs.append(f'{where}: mcq answer out of range')
        else:
            nn = [norm_opt(o) for o in opts]
            if len(set(nn)) != len(nn) or '' in nn: errs.append(f'{where}: duplicate/empty options after normalisation {opts}')
            elif len(set(map(no_marks, nn))) != len(nn): warns.append(f'{where}: options differ only by dakuten/marks {opts}')
    elif t == 'multi':
        a = q.get('answer')
        if not isinstance(a, list) or not a or any(not isinstance(k, int) or not 0 <= k < len(opts or []) for k in a): errs.append(f'{where}: multi answer invalid')
    elif t in ('tfng',):
        if q.get('answer') not in ('TRUE', 'FALSE', 'NOT GIVEN', 'YES', 'NO'): errs.append(f'{where}: tfng answer invalid')
    elif t == 'match':
        vs = [o['v'] if isinstance(o, dict) else o for o in (opts or [])]
        if q.get('answer') not in vs: errs.append(f'{where}: match answer not in options')
    elif t == 'gap':
        if not q.get('answer'): errs.append(f'{where}: gap without answer')
    elif t == 'order':
        it = q.get('items') or []
        a = q.get('answer', list(range(len(it))))
        if len(it) < 2 or sorted(a) != list(range(len(it))): errs.append(f'{where}: order answer invalid')
    elif t == 'dictation':
        if not q.get('answer'): errs.append(f'{where}: dictation without answer')
    elif t == 'highlight':
        n = len(str(q.get('text', '')).split(' '))
        if not q.get('answer') or any(not 0 <= k < n for k in q['answer']): errs.append(f'{where}: highlight answer invalid')
    elif t == 'cloze':
        ids = re.findall(r'\[\[(\d+)\]\]', q.get('text', ''))
        bl = q.get('blanks') or {}
        if sorted(ids) != sorted(bl.keys()): errs.append(f'{where}: cloze blanks mismatch')
        for k, b in bl.items():
            ans = [b.get('answer')] if isinstance(b.get('answer'), str) else (b.get('answer') or [])
            if b.get('options') and not set(ans) & set(b['options']):
                errs.append(f'{where}: cloze blank {k} answer not in options')
    elif t in ('essay', 'speak'):
        if not q.get('prompt') and t == 'essay': errs.append(f'{where}: essay without prompt')
    else:
        errs.append(f'{where}: unknown type {t}')

for b in BANKS:
    p = os.path.join(ROOT, 'banks', b + '.json')
    d = json.load(open(p, encoding='utf-8'))
    ids = collections.Counter()
    for si, s in enumerate(d['sections']):
        for sl in s.get('slots', []):
            pool = sl.get('sets') or sl.get('items') or []
            take = sl.get('count', 1)
            texts = collections.Counter()
            nq = 0
            for st in pool:
                ids[st['id']] += 1
                key = plain(st.get('passage') or st.get('transcript') or '') or ' | '.join(plain(q.get('prompt') or q.get('text') or '') for q in st.get('questions', []))
                texts[key] += 1
                if st.get('audio') and not os.path.exists(os.path.join(ROOT, st['audio'])):
                    errs.append(f"{b}/{st['id']}: audio missing {st['audio']}")
                for qi, q in enumerate(st.get('questions', [])):
                    nq += 1
                    check_q(f"{b}/{st['id']}#{qi+1}", q)
                    if q.get('img') and not os.path.exists(os.path.join(ROOT, q['img'])):
                        errs.append(f"{b}/{st['id']}#{qi+1}: image missing {q['img']}")
                    if q.get('aopts'):
                        # options are read in the audio in this fixed order: never shuffle, audio required
                        if q.get('shuffle') is not False: errs.append(f"{b}/{st['id']}#{qi+1}: aopts must have shuffle:false")
                        if not st.get('audio'): errs.append(f"{b}/{st['id']}#{qi+1}: aopts without audio")
            for k, c in texts.items():
                if k and c > 1: errs.append(f"{b}/{sl['id']} (section {si}): {c} sets with identical text: {k[:60]}")
            rows.append((b, plain(s.get('title'))[:34], sl['id'], take, len(pool), nq, len(pool) // take if take else 0))
    for k, c in ids.items():
        if c > 1: errs.append(f'{b}: duplicate set id {k}')

if '--table' in sys.argv:
    print(f"{'test':6} {'section':34} {'slot':6} {'take':>4} {'bank':>5} {'q':>5} {'tests w/o repeat':>16}")
    for r in rows: print(f'{r[0]:6} {r[1]:34} {r[2]:6} {r[3]:>4} {r[4]:>5} {r[5]:>5} {r[6]:>16}')
for w in warns: print('WARN', w)
for e in errs: print('ERROR', e)
print(f'{len(errs)} error(s), {len(rows)} slots checked')
sys.exit(1 if errs else 0)
