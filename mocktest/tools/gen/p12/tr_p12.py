"""Bank transcripts for the 10 P1/P2 sets: original 12g dialogue lines + the narrator questions exactly as spoken (text of the v2 narration, 57dedf7)."""
import json, re, subprocess
R = '/home/claude/teg-tutorial/mocktest/banks/'
P1 = ['L5c', 'L5d', 'L4c', 'L4d']; P2 = ['H1Lc', 'H1Ld', 'H2Lc', 'H2Ld', 'H3Lc', 'H3Ld']
INTRO = 'もんだい。はなしを きいて、しつもんに こたえて ください。'
def sets(rev, t):
    b = json.loads(subprocess.run(['git', '-C', R, 'show', f'{rev}:mocktest/banks/{t}.json'], capture_output=True, text=True, check=True).stdout)
    return {st['id']: st for s in b['sections'] for sl in s['slots'] for st in sl['sets']}
for t, ids in (('jlpt', P1), ('hsk', P2)):
    V2 = sets('57dedf7', t); b = json.load(open(R + t + '.json'))
    for s in b['sections']:
        for sl in s['slots']:
            for st in sl['sets']:
                if st['id'] not in ids: continue
                tr = st['transcript']; assert 'data-tr="full"' not in tr
                parts = re.split(r'(<b>[^<]+</b>)', tr); heads = parts[1::2]; bodies = parts[2::2]
                qv = re.findall(r'<i>🔊 ([^<]+)</i>', V2[st['id']]['transcript'])
                n = len(st['questions']); assert len(heads) == n, (st['id'], len(heads))
                if t == 'jlpt': assert len(qv) == 2 * n and qv[0::2] == qv[1::2], st['id']; qv = qv[0::2]
                else: assert len(qv) == n and all(q.startswith('问：') for q in qv), (st['id'], qv)
                out = ['<span data-tr="full"></span>'] + ([f'<i>{INTRO}</i><br><br>'] if t == 'jlpt' else [])
                for h, body, q in zip(heads, bodies, qv):
                    body = re.sub(r'^(<br>)+|(<br>)+$', '', body.strip())
                    out.append(f'{h}<br><i>🔊 {q}</i><br>{body}<br><i>🔊 {q}</i><br><br>' if t == 'jlpt' else f'{h}<br>{body}<br><i>🔊 {q}</i><br><br>')
                st['transcript'] = ''.join(out)
                print(st['id'], st['transcript'][:230])
    json.dump(b, open(R + t + '.json', 'w'), ensure_ascii=False, separators=(',', ':'))
