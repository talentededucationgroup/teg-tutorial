# SSML for the new N3-N1 listening sets (c, d, e); groups limited to 48 <voice> tags and 4300 chars (Azure limits)
import sys, json, re, runpy
sys.path.insert(0, '/home/claude/w91')
new = []
for lv in ('t3_n3', 't3_n2', 't3_n1'):
    sys.argv = ['t3_build.py', 'none', lv]
    src = open('/home/claude/w91/t3_build.py').read().replace("{'bank': bank, 'ssml': ssml}[sys.argv[1]]()", '')
    g = {'__name__': 'x'}; exec(compile(src, 't3_build', 'exec'), g)
    _, aud = g['listening_sets']()
    new += [(sid, x) for sid, x in aud if sid[-1] in 'cde']
src = open('/home/claude/w91/t3_lis.py').read().replace("{'bank': bank, 'ssml': ssml}[sys.argv[1]]()", '')
g = {'__name__': 'x'}; exec(compile(src, 't3_lis', 'exec'), g)
new += [(st['id'], x) for lv, slot, st, x in g['all_sets']() if lv in ('N3', 'N2', 'N1') and st['id'][-1] in 'cde']
groups, cur, n, size = [], [], 0, 0
for sid, x in new:
    v = x.count('<voice')
    if cur and (n + v > 48 or size + len(x) > 4300): groups.append(cur); cur, n, size = [], 0, 0
    cur.append((sid, x)); n += v; size += len(x)
if cur: groups.append(cur)
json.dump([[s for s, _ in gr] for gr in groups], open('/home/claude/w91/X_groups.json', 'w'))
out = open('/tmp/claude-0/-home-claude/7600d9ee-aee0-5a14-abd7-7540cbf5f3d4/scratchpad/x_ssml.txt', 'w')
for i, gr in enumerate(groups):
    body = ''.join(x for _, x in gr)
    out.write(f"===== XG{i} ({len(body)} chars, {body.count('<voice')} voices): {','.join(s for s, _ in gr)}\n<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>{body}</speak>\n")
print(len(new), 'sets in', len(groups), 'groups')
