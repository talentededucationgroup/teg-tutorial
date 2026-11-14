"""Restore the 24 listening sets a-d (JLPT N5/N4, TOPIK I, HSK 1-3) to their 838677d / 2026-11-12g state: audio path, transcript, instructions.
Questions are untouched (verified identical)."""
import json, subprocess
R = '/home/claude/teg-tutorial/mocktest/banks/'
IDS = {a + b for a in ('L5', 'L4', 'TL', 'H1L', 'H2L', 'H3L') for b in 'abcd'}
done = []
for t in ('jlpt', 'topik', 'hsk'):
    old = json.loads(subprocess.run(['git', '-C', R, 'show', f'838677d:mocktest/banks/{t}.json'], capture_output=True, text=True, check=True).stdout)
    O = {st['id']: st for s in old['sections'] for sl in s['slots'] for st in sl['sets'] if st['id'] in IDS}
    raw = open(R + t + '.json').read(); b = json.loads(raw)
    for s in b['sections']:
        for sl in s['slots']:
            for st in sl['sets']:
                if st['id'] in O:
                    o = O[st['id']]
                    assert json.dumps(o['questions'], sort_keys=True) == json.dumps(st['questions'], sort_keys=True), st['id']
                    for k in ('audio', 'transcript', 'instructions'):
                        if k in o: st[k] = o[k]
                        elif k in st: del st[k]
                    assert set(st) == set(o), (st['id'], set(st) ^ set(o))
                    done.append(st['id'])
    json.dump(b, open(R + t + '.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(done), sorted(done))
