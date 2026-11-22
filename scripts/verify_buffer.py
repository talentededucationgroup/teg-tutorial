#!/usr/bin/env python3
"""Cek apakah postingan Buffer BENAR-BENAR tayang (pemilik 22/11/2026: "selalu pastikan feed dan story terpublish").
Menulis data/buffer-verify.json: per channel postingan terakhir yang tayang per jenis (feed/reel/story) + link,
postingan error / belum tayang padahal sudah lewat jadwal. Dibaca tugas QA Claude untuk memberi tahu pemilik.
Tanpa teks lengkap postingan (hanya 50 karakter pertama)."""
import json, os, sys, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_to_buffer import gql, KEY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'buffer-verify.json')
WAIT = int(os.environ.get('VERIFY_WAIT_SECONDS', '0'))
WATCH = {'instagram', 'facebook'}          # channel yang wajib dipantau (feed + story)
NEED = {'instagram': ('feed', 'story'), 'facebook': ('feed', 'story')}
GRACE = datetime.timedelta(minutes=20)     # lewat jadwal > 20 menit dan belum tayang = masalah

if not KEY:
    print('no BUFFER_API_KEY'); sys.exit(0)
if WAIT:
    time.sleep(WAIT)

now = datetime.datetime.now(datetime.timezone.utc)
P = lambda s: datetime.datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None


def kind_of(n):
    link = n.get('externalLink') or ''
    if '/stories/' in link:
        return 'story'
    if '/reel' in link or 'shorts' in link or 'tiktok.com' in link:
        return 'reel'
    if link:
        return 'feed'
    md = json.dumps(n.get('metadata') or {}).lower()
    if '"story"' in md:
        return 'story'
    if '"reel"' in md:
        return 'reel'
    return 'feed'


posts = []
orgs = gql("query { account { organizations { id } } }")['account']['organizations']
body = "{ edges{ node{ id status channelId channelService dueAt sentAt externalLink error { message } text } } } }"
for o in orgs:
    try:
        d = gql("query P($o:OrganizationId!){ posts(input:{organizationId:$o, sort:[{field: createdAt, direction: desc}]}, first:100)" + body, {"o": o['id']})['posts']
    except Exception:
        d = gql("query P($o:OrganizationId!){ posts(input:{organizationId:$o}, first:100)" + body, {"o": o['id']})['posts']
    posts += [e['node'] for e in d['edges']]

last, problems = {}, []
for n in posts:
    sv = (n.get('channelService') or '').lower()
    k = kind_of(n)
    st = (n.get('status') or '').lower()
    if st == 'sent' and n.get('sentAt'):
        key = f'{sv}|{k}'
        if key not in last or P(n['sentAt']) > P(last[key]['sentAt']):
            last[key] = {'sentAt': n['sentAt'], 'link': n.get('externalLink'), 'text': (n.get('text') or '')[:50]}
    err = (n.get('error') or {}).get('message') if isinstance(n.get('error'), dict) else n.get('error')
    due = P(n.get('dueAt'))
    if sv in WATCH and (err or st == 'error' or (st not in ('sent', 'draft') and due and now - due > GRACE)):
        problems.append({'service': sv, 'kind': k, 'status': st, 'dueAt': n.get('dueAt'), 'error': err,
                         'text': (n.get('text') or '')[:50]})

stale = []
for sv, kinds in NEED.items():
    for k in kinds:
        x = last.get(f'{sv}|{k}')
        if not x or now - P(x['sentAt']) > datetime.timedelta(hours=24):
            stale.append(f'{sv} {k}: tidak ada yang tayang dalam 24 jam' + (f" (terakhir {x['sentAt']})" if x else ''))

res = {'note': 'Ditulis scripts/verify_buffer.py setelah setiap kiriman Buffer. ok=false = ada postingan IG/FB gagal/belum tayang atau feed/story kosong > 24 jam.',
       'checked_at': now.isoformat(timespec='seconds'), 'ok': not problems and not stale,
       'last_sent': dict(sorted(last.items())), 'problems': problems[:20], 'stale': stale}
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ('ok', 'problems', 'stale')}, ensure_ascii=False, indent=1))
for k, v in sorted(last.items()):
    print('TAYANG', k, v['sentAt'], v['link'])
