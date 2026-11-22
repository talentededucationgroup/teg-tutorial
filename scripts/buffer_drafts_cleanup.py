#!/usr/bin/env python3
"""One-off/maintenance: delete Buffer DRAFT posts created by the autopost before 20/11/2026 21:00 WIB
(when the pipeline still saved everything to Drafts). Owner approved 20/11/2026. Only drafts, never queued/sent posts.
Mode: env MODE=inspect (print schema hints) or MODE=delete. Prints counts only, no post text."""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_to_buffer import gql, KEY
CUT = datetime.datetime(2026, 11, 20, 14, 0, tzinfo=datetime.timezone.utc)  # 21:00 WIB
MODE = os.environ.get('MODE', 'inspect')
if not KEY:
    print('no key'); sys.exit(0)
def fields(t):
    d = gql('query T($n:String!){__type(name:$n){name kind fields{name args{name type{name kind ofType{name kind ofType{name}}}} type{name kind ofType{name kind}}} inputFields{name type{name kind ofType{name kind ofType{name}}}} enumValues{name}}}', {"n": t})
    return d['__type']
if MODE == 'inspect':
    q = fields('Query'); m = fields('Mutation')
    print('QUERY', [ (f['name'], [a['name'] for a in f['args']]) for f in q['fields'] if 'post' in f['name'].lower()])
    print('MUTATION', [ (f['name'], [a['name'] for a in f['args']]) for f in m['fields'] if 'post' in f['name'].lower() or 'draft' in f['name'].lower()])
    for t in ('PostsInput', 'PostsFiltersInput', 'PostFiltersInput', 'PostStatus', 'Post', 'DeletePostInput', 'PostsFilterInput'):
        try:
            x = fields(t)
            if x: print(t, x['kind'], [f['name'] for f in (x.get('fields') or x.get('inputFields') or [])] or [e['name'] for e in (x.get('enumValues') or [])])
        except Exception as e:
            print(t, 'ERR', str(e)[:120])
    sys.exit(0)
if MODE == 'recent':
    # cek status 30 postingan terbaru per organisasi: tayang / error / link (tanpa teks lengkap)
    pf = fields('Post')
    names = {f['name'] for f in pf['fields']}
    print('Post fields:', sorted(names))
    want = [n for n in ('id', 'status', 'channelId', 'channelService', 'createdAt', 'dueAt', 'sentAt', 'externalLink', 'schedulingType', 'shareMode', 'via') if n in names]
    err = ' error { message }' if 'error' in names else ''
    orgs = gql("query { account { organizations { id } } }")['account']['organizations']
    for o in orgs:
        d = gql("query P($o:OrganizationId!){ posts(input:{organizationId:$o, sort:[{field: createdAt, direction: desc}]}, first:40){ edges{ node{ " + ' '.join(want) + err + " text } } } }", {"o": o['id']})['posts']
        for e in d['edges']:
            n = e['node']; n['text'] = (n.get('text') or '')[:50]
            print('POST', json.dumps(n, ensure_ascii=False))
    sys.exit(0)
if MODE == 'resync_sent':
    # Pemilik 22/11/2026: setelah antrean dikosongkan, data/buffer-sent.json hanya mencatat feed/reel yang BENAR-BENAR
    # sudah tayang (dicocokkan dengan postingan status sent di Buffer), supaya yang terhapus bisa dipilih ulang tanpa dobel.
    import re
    from post_to_buffer import feed, x_text, no_hashtags, SENT_P
    norm = lambda t: re.sub(r'[\s*]+', ' ', t or '').strip()[:60]
    pub = set()
    orgs = gql("query { account { organizations { id } } }")['account']['organizations']
    for o in orgs:
        after = None
        for _ in range(30):
            d = gql("""query P($o:OrganizationId!,$a:String){ posts(input:{organizationId:$o, filter:{status:[sent]}}, first:100, after:$a){ edges{ node{ channelId text } } pageInfo{ hasNextPage endCursor } } }""", {"o": o['id'], "a": after})['posts']
            for e in d['edges']:
                if e['node'].get('text'):
                    pub.add((e['node']['channelId'], norm(e['node']['text'])))
            if not d['pageInfo']['hasNextPage']:
                break
            after = d['pageInfo']['endCursor']
    items = {}
    for f in ('social-feed.xml', 'social-feed-story.xml', 'social-feed-reels.xml'):
        for i in feed(f):
            items[i['guid']] = i
    sent = json.load(open(SENT_P, encoding='utf-8'))
    keep, drop = [], []
    for k in sent['sent']:
        parts = k.split('|'); guid = '|'.join(parts[:-2]); kind = parts[-2]; ch = parts[-1]
        i = items.get(guid)
        if kind == 'story' or not i:
            keep.append(k); continue
        texts = {norm(i['text']), norm(no_hashtags(i['text'])), norm(x_text(i))}
        (keep if any((ch, t) in pub for t in texts) else drop).append(k)
    sent['sent'] = sorted(keep)
    sent['note'] = sent.get('note', '') + ' Diselaraskan 22/11/2026 setelah antrean Buffer dikosongkan: hanya yang sudah tayang.'
    json.dump(sent, open(SENT_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'published texts {len(pub)}; kept {len(keep)}; dropped {len(drop)}')
    sys.exit(0)
if MODE == 'sent_list':
    # daftar postingan yang SUDAH tayang (channelId + awal teks) untuk menyelaraskan data/buffer-sent.json
    orgs = gql("query { account { organizations { id } } }")['account']['organizations']
    for o in orgs:
        after = None
        for _ in range(20):
            d = gql("""query P($o:OrganizationId!,$a:String){ posts(input:{organizationId:$o, filter:{status:[sent]}}, first:100, after:$a){ edges{ node{ id status channelId text } } pageInfo{ hasNextPage endCursor } } }""", {"o": o['id'], "a": after})['posts']
            for e in d['edges']:
                n = e['node']
                print('SENT', json.dumps({"c": n.get('channelId'), "t": (n.get('text') or '')[:90]}, ensure_ascii=False))
            if not d['pageInfo']['hasNextPage']:
                break
            after = d['pageInfo']['endCursor']
    sys.exit(0)
if MODE in ('count_queue', 'delete_queue'):
    # Pemilik 22/11/2026: kosongkan antrean Buffer (postingan terjadwal yang belum tayang) agar tidak menumpuk;
    # postingan baru setelah ini langsung tayang (post_mode now). Tidak menyentuh postingan yang sudah tayang.
    orgs = gql("query { account { organizations { id } } }")['account']['organizations']
    seen = deleted = 0; per = {}
    for o in orgs:
        for _ in range(50):
            d = gql("""query P($o:OrganizationId!){ posts(input:{organizationId:$o, filter:{status:[scheduled]}}, first:100){ edges{ node{ id status channelId } } pageInfo{ hasNextPage endCursor } } }""", {"o": o['id']})['posts']
            nodes = [e['node'] for e in d['edges'] if e['node']['status'] == 'scheduled']
            seen += len(nodes)
            for n in nodes:
                per[n.get('channelId')] = per.get(n.get('channelId'), 0) + 1
            if MODE == 'count_queue' or not nodes:
                break
            for n in nodes:
                gql("mutation D($i:PostId!){ deletePost(input:{id:$i}){ __typename } }", {"i": n['id']})
                deleted += 1
    print(f'antrean terjadwal per channel: {per}')
    print(f'scheduled seen {seen}; deleted {deleted}')
    sys.exit(0)
# delete mode
orgs = gql("query { account { organizations { id } } }")['account']['organizations']
total = deleted = 0
for o in orgs:
    after = None
    while True:
        d = gql("""query P($o:OrganizationId!,$a:String){ posts(input:{organizationId:$o, filter:{status:[draft]}}, first:50, after:$a){ edges{ node{ id status createdAt } } pageInfo{ hasNextPage endCursor } } }""", {"o": o['id'], "a": after})['posts']
        for e in d['edges']:
            n = e['node']; total += 1
            ts = datetime.datetime.fromisoformat(n['createdAt'].replace('Z', '+00:00'))
            if n['status'] == 'draft' and ts < CUT:
                r = gql("mutation D($i:PostId!){ deletePost(input:{id:$i}){ __typename } }", {"i": n['id']})
                deleted += 1
        if not d['pageInfo']['hasNextPage']:
            break
        after = d['pageInfo']['endCursor']
print(f'drafts seen {total}; deleted {deleted}')
