#!/usr/bin/env python3
"""Send new posts from social-feed*.xml to Buffer via the official Buffer GraphQL API (https://api.buffer.com).
Needs GitHub secret BUFFER_API_KEY (created by the owner at https://publish.buffer.com/settings/api).
Settings: data/social-autopost.json  (mode "draft" = lands in Buffer Drafts for approval, "queue" = Buffer queue).
State: data/buffer-sent.json (what was already sent, per channel). No personal data. Never raises."""
import json, os, re, sys, datetime, email.utils, urllib.request, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.buffer.com'
KEY = os.environ.get('BUFFER_API_KEY', '').strip()
CFG_P = os.path.join(ROOT, 'data', 'social-autopost.json')
SENT_P = os.path.join(ROOT, 'data', 'buffer-sent.json')
NOW = datetime.datetime.now(datetime.timezone.utc)


def load(p, d):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


def gql(query, variables=None):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.load(r)
    if out.get('errors'):
        raise RuntimeError(json.dumps(out['errors'])[:400])
    return out['data']


def feed(name):
    try:
        root = ET.parse(os.path.join(ROOT, name)).getroot()
    except Exception:
        return []
    items = []
    for it in root.iter('item'):
        g = lambda t: (it.findtext(t) or '').strip()
        enc = it.find('enclosure')
        try:
            pub = email.utils.parsedate_to_datetime(g('pubDate'))
        except Exception:
            pub = NOW
        items.append({"guid": g('guid'), "title": g('title'), "link": g('link'), "text": g('description'),
                      "media": enc.get('url') if enc is not None else None, "pub": pub})
    return items


def svc(s):
    s = (s or '').lower()
    for k in ('instagram', 'facebook', 'twitter', 'linkedin', 'google', 'tiktok', 'youtube', 'threads'):
        if k in s:
            return k
    return s


def x_text(i):
    t = re.sub(r'^[^\w]+', '', i['title'])[:200]
    return f"{t} {i['link']}"[:280]


def no_hashtags(t):
    return '\n'.join(l for l in t.split('\n') if not l.strip().startswith('#')).strip()


def build(kind, ch, i, cfg):
    """return createPost input or None if this channel does not take this kind"""
    s = svc(ch['service'])
    base = {"channelId": ch['id'], "schedulingType": "automatic",
            "mode": "shareNow" if cfg.get('post_mode') == 'now' and not cfg.get('_draft', True) else "addToQueue"}
    if cfg.get('_draft', True):
        base["saveToDraft"] = True
    if kind == 'feed':
        if s not in ('instagram', 'facebook', 'twitter', 'linkedin', 'google', 'threads'):
            return None
        text = x_text(i) if s in ('twitter', 'threads') else (no_hashtags(i['text']) if s == 'google' else i['text'])
        if s == 'google' and len(text) > 1490:
            text = text[:1490].rsplit('\n', 1)[0].rstrip()  # Google Business summary max 1500 chars
        p = dict(base, text=text, assets=[{"image": {"url": i['media']}}])
        if s == 'instagram':
            p['metadata'] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
        elif s == 'facebook':
            p['metadata'] = {"facebook": {"type": "post"}}
        elif s == 'google':
            p['metadata'] = {"google": {"type": "whats_new"}}
        return p
    if kind == 'story':
        # Story sebagai video 9:16 bermusik bila Reel-nya sudah live (pemilik 21/11/2026), selain itu gambar
        if i['media'].lower().endswith('.mp4'):
            asset = {"video": {"url": i['media']}}
        elif i.get('story_video') and cfg.get('story_video', True):
            asset = {"video": {"url": i['story_video']}}
        else:
            asset = {"image": {"url": i['media']}}
        if s == 'instagram' and cfg.get('stories', True):
            return dict(base, text='', assets=[asset],
                        metadata={"instagram": {"type": "story", "shouldShareToFeed": False}})
        if s == 'facebook' and cfg.get('stories', True):
            return dict(base, text='', assets=[asset], metadata={"facebook": {"type": "story"}})
        return None
    if kind == 'reel':
        if not cfg.get('reels', True):
            return None
        a = [{"video": {"url": i['media']}}]
        if s == 'instagram':
            return dict(base, text=i['text'], assets=a, metadata={"instagram": {"type": "reel", "shouldShareToFeed": True}})
        if s == 'facebook':
            return dict(base, text=i['text'], assets=a, metadata={"facebook": {"type": "reel"}})
        if s == 'tiktok':
            return dict(base, text=i['text'][:2000], assets=a)
        if s == 'youtube':
            return dict(base, text=i['text'][:4900], assets=a,
                        metadata={"youtube": {"title": re.sub(r'^[^\w]+', '', i['title'])[:95], "categoryId": "27"}})
    return None


REVIEW_P = os.path.join(ROOT, 'data', 'social-review.json')
OAI = os.environ.get('OPENAI_API_KEY', '').strip()
CHECKLIST = """Kamu PEMERIKSA KEDUA (QA) postingan sosmed Talented Education Group (agen pendidikan luar negeri). Nilai SATU postingan.
Gagal salah satu = bukan LOLOS:
A. Fakta/angka/tanggal di judul, poster & caption harus cocok dengan TEKS SUMBER RESMI yang diberikan (bila ada). Sumber harus domain resmi kampus/pemerintah. Deadline/promo tidak boleh sudah lewat (tanggal hari ini diberikan). Biaya ditulis per semester/term/trimester bila ada biaya.
B. RAHASIA BISNIS: tidak boleh ada nama/link master agent atau agregator (Yes Education, yesedugroup, AIG, upGrad, GSP, APG, Asia Pacific Group), portal agen, komisi, harga agen, "potongan agent", catatan internal, data/foto siswa.
C. Tidak ada klaim "pasti visa", "dijamin", jaminan skor, "termurah se-...". "Sponsored" hanya untuk pengiklan berbayar.
D. Poster: logo Talented terlihat, teks tidak terpotong/bertabrakan parah, foto tanpa tulisan mengganggu, tidak menyesatkan.
E. Caption: bahasa Indonesia wajar, ada link resmi bila menyebut ketentuan, penutup Talented ada, maks 3 hashtag, tanpa nomor telepon.
Putusan: LOLOS (siap tayang), REVISI (ada masalah kecil yang harus diperbaiki dulu), TOLAK (salah fakta/rahasia bocor/menyesatkan).
Jawab HANYA JSON: {"verdict":"LOLOS|REVISI|TOLAK","reasons":["..."],"fix":"saran perbaikan singkat atau kosong"}"""


def page_text(url):
    if not url:
        return ''
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (TEG QA bot)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read(600000)
            ctype = r.headers.get('Content-Type', '')
        if 'pdf' in ctype or url.lower().endswith('.pdf'):
            try:
                import io
                from pypdf import PdfReader
                return ' '.join((pg.extract_text() or '') for pg in PdfReader(io.BytesIO(raw)).pages[:6])[:9000]
            except Exception:
                return ''
        t = raw.decode('utf-8', 'ignore')
        t = re.sub(r'(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>', ' ', t)
        t = re.sub(r'<[^>]+>', ' ', t)
        return re.sub(r'\s+', ' ', t)[:9000]
    except Exception as e:
        return f'(sumber tidak bisa dibuka: {str(e)[:80]})'


def review(i, cfg):
    """independent check by an OpenAI model (ChatGPT) - returns dict verdict/reasons/fix"""
    import base64, urllib.parse as up
    src = re.findall(r'(?:Ketentuan resmi(?: beasiswa)?|Sumber resmi pemerintah):\s*(https?://\S+)', i['text'])
    stext = page_text(src[0]) if src else ''
    img = None
    if i['media']:
        f = os.path.join(ROOT, 'social', 'cards', up.unquote(i['media'].rsplit('/', 1)[1]))
        if os.path.exists(f):
            img = 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    content = [{"type": "text", "text": f"Tanggal hari ini: {NOW.date().isoformat()}\nJUDUL: {i['title']}\nLINK: {i['link']}\n"
                f"CAPTION:\n{i['text']}\n\nSUMBER RESMI ({src[0] if src else 'tidak ada'}):\n{stext or '(tidak ada teks sumber)'}"}]
    if img:
        content.append({"type": "image_url", "image_url": {"url": img}})
    body = {"model": cfg.get('reviewer_model', 'gpt-4o'), "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": CHECKLIST}, {"role": "user", "content": content}]}
    req = urllib.request.Request('https://api.openai.com/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + OAI})
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.load(r)
    v = json.loads(out['choices'][0]['message']['content'])
    v['verdict'] = str(v.get('verdict', 'REVISI')).upper()
    v['checked_at'] = NOW.isoformat(); v['model'] = body['model']; v['source'] = src[0] if src else None
    return v


MUT = """mutation P($input: CreatePostInput!) { createPost(input: $input) {
  ... on PostActionSuccess { post { id } }
  ... on MutationError { message } } }"""


def queued_counts(orgs):
    """jumlah postingan terjadwal (belum tayang) per channel di Buffer; None bila API tidak bisa dibaca"""
    try:
        counts = {}
        for o in orgs:
            after = None
            for _ in range(20):
                d = gql("""query P($o:OrganizationId!,$a:String){ posts(input:{organizationId:$o, filter:{status:[scheduled]}}, first:100, after:$a){ edges{ node{ id channelId } } pageInfo{ hasNextPage endCursor } } }""",
                        {"o": o['id'], "a": after})['posts']
                for e in d['edges']:
                    c = e['node'].get('channelId')
                    counts[c] = counts.get(c, 0) + 1
                if not d['pageInfo']['hasNextPage']:
                    break
                after = d['pageInfo']['endCursor']
        return counts
    except Exception as e:
        print('queue lookup failed:', str(e)[:300])
        return None


def main():
    cfg = load(CFG_P, {})
    if not KEY:
        print('BUFFER_API_KEY not set: autopost skipped.')
        return 0
    if not cfg.get('enabled', True):
        print('autopost disabled in data/social-autopost.json')
        return 0
    sent = load(SENT_P, {"note": "Postingan yang sudah dikirim ke Buffer (guid|kind|channel).", "sent": []})
    done = set(sent['sent'])
    try:
        orgs = gql("query { account { organizations { id name } } }")['account']['organizations']
        chans = []
        for o in orgs:
            chans += gql("query C($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name displayName service isQueuePaused } }",
                         {"o": o['id']})['channels']
    except Exception as e:
        # some schemas type organizationId as String
        try:
            chans = []
            for o in orgs:
                chans += gql("query C($o: String!) { channels(input: {organizationId: $o}) { id name displayName service isQueuePaused } }",
                             {"o": o['id']})['channels']
        except Exception as e2:
            print('Buffer channel lookup failed:', str(e2)[:300])
            return 0
    allow = set(cfg.get('services') or [])
    chans = [c for c in chans if not c.get('isQueuePaused') and (not allow or svc(c['service']) in allow)]
    print('channels:', [(svc(c['service']), c.get('displayName') or c.get('name')) for c in chans])
    # wait until freshly built posters are live on GitHub Pages (Buffer must be able to download them)
    import time
    def live(u):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, method='HEAD'), timeout=20) as r:
                return r.status == 200
        except Exception:
            return False
    want = {i['media'] for f in ('social-feed.xml', 'social-feed-story.xml', 'social-feed-reels.xml') for i in feed(f)
            if i['media'] and i['pub'] <= NOW and (NOW - i['pub']).days <= int(cfg.get('max_age_days', 10))}
    deadline = time.time() + int(os.environ.get('WAIT_MEDIA_SECONDS', '0') or 0)
    ready = {u for u in want if live(u)}
    while len(ready) < len(want) and time.time() < deadline:
        time.sleep(20)
        ready |= {u for u in want - ready if live(u)}
    if len(ready) < len(want):
        print(f'media not live yet: {len(want) - len(ready)} (will retry next run)')
    limit, n, errors = int(cfg.get('max_per_run', 6)), 0, []
    waiting = set()
    reviews = load(REVIEW_P, {"note": "Hasil cek otomatis ChatGPT (OpenAI) per postingan sebelum tayang.", "items": {}})
    auto = cfg.get('mode') == 'auto_reviewed'
    if auto and not OAI:
        # owner 20/11/2026: no Drafts - verdicts come from the Claude QA scheduled task (data/social-review.json);
        # posts without a verdict wait for the next review run.
        print('mode auto_reviewed: no OPENAI_API_KEY, using verdicts written by the Claude QA reviewer.')
    # Pilih sedikit tapi bermutu (pemilik 22/11/2026): urut skor (jenis + skor QA + kebaruan), 1 format per postingan
    # per channel (Reel ATAU feed), batas harian kecil, dan tidak menambah bila antrean Buffer channel itu masih penuh.
    prio = cfg.get('priority', {})
    # Fokus negara (pemilik 22/11/2026): AU, CA, NZ, JP, KR lebih sering; negara lain jarang (pelengkap).
    cf = cfg.get('country_focus', {})
    focus = {c.upper() for c in cf.get('priority', ['AU', 'CA', 'NZ', 'JP', 'KR'])}
    ALIAS = {'AUSTRALIA': 'AU', 'KANADA': 'CA', 'CANADA': 'CA', 'NEW ZEALAND': 'NZ', 'SELANDIA BARU': 'NZ', 'JEPANG': 'JP',
             'JAPAN': 'JP', 'KOREA': 'KR', 'KOREA SELATAN': 'KR', 'SOUTH KOREA': 'KR', 'AU & NZ': 'AU'}
    try:
        upd = {x['id']: x.get('country') for x in load(os.path.join(ROOT, 'data', 'updates.json'), {}).get('items', [])}
    except Exception:
        upd = {}
    def ctry(i):
        c = upd.get(i['guid'])
        if not c:
            return None  # umum / tanpa negara = tidak dibatasi
        c = str(c).strip().upper()
        return ALIAS.get(c, c)
    def other(i):
        c = ctry(i)
        return c is not None and c not in focus and c != 'ANY'
    def score(kind, i):
        rv = reviews['items'].get(i['guid']) or {}
        base = next((int(v) for k, v in prio.items() if i['guid'].startswith(k)), int(prio.get('default', 50)))
        c = ctry(i)
        if c in focus:
            base += int(cf.get('priority_bonus', 15))
        elif other(i):
            base -= int(cf.get('other_penalty', 30))
        q = rv.get('score')
        return base + (int(q) - 3) * 10 if isinstance(q, (int, float)) else base, -(NOW - i['pub']).total_seconds()
    oth_day = sent.setdefault('daily_other', {}).setdefault(NOW.date().isoformat(), [])
    oth_max = int(cf.get('other_max_per_day', 1))
    kinds_order = {'reel': 0, 'feed': 1, 'story': 2}
    cands = []
    for kind, fname in (('feed', 'social-feed.xml'), ('story', 'social-feed-story.xml'), ('reel', 'social-feed-reels.xml')):
        for i in feed(fname):
            cands.append((score(kind, i), kinds_order[kind], kind, i))
    cands.sort(key=lambda c: (-c[0][0], -c[0][1], c[1]))
    queued = queued_counts(orgs)
    if queued is None:
        print('antrean Buffer tidak terbaca: hanya batas harian yang dipakai')
    else:
        print('antrean Buffer saat ini:', {svc(c['service']) + ':' + c['id'][-4:]: queued.get(c['id'], 0) for c in chans})
    max_q = int(cfg.get('max_queue_per_channel', 2))
    run_count = {}
    max_age = int(cfg.get('max_age_days', 10))
    min_q = int(cfg.get('min_quality_score', 3))
    for (sc, _), _o, kind, i in cands:
        if True:
            if not i['media'] or i['media'] not in ready or i['pub'] > NOW or (NOW - i['pub']).days > max_age:
                continue
            # immigration news: only post while fresh (announced today or yesterday) - owner 20/11/2026
            if i['guid'].startswith('news:') and (NOW - i['pub']).days > int(cfg.get('news_max_age_days', 1)):
                continue
            if kind == 'story' and i['media'].endswith('%20Story.png'):
                alt = i['media'][:-len('%20Story.png')] + '%20Reel.mp4'
                i['story_video'] = alt if alt in ready else None
            cfg['_draft'] = True
            rv0 = reviews['items'].get(i['guid']) or {}
            if isinstance(rv0.get('score'), (int, float)) and rv0['score'] < min_q:
                continue  # kurang menarik menurut QA: tidak diposting
            instant = any(i['guid'].startswith(x) for x in cfg.get('instant_prefixes', []))
            if auto and instant and (reviews['items'].get(i['guid']) or {}).get('verdict') not in ('REVISI', 'TOLAK'):
                cfg['_draft'] = False  # official scholarship/immigration news: post at once (owner 20/11/2026), QA checks afterwards
            elif auto:
                rv = reviews['items'].get(i['guid'])
                if not rv and kind == 'feed' and OAI:
                    try:
                        rv = review(i, cfg); reviews['items'][i['guid']] = rv
                        print('review', i['guid'], rv['verdict'], '; '.join(rv.get('reasons', []))[:200])
                    except Exception as e:
                        errors.append(f"review/{i['guid']}: {str(e)[:160]}"); continue
                if not rv:
                    waiting.add(i['guid'])
                    continue  # waits for a QA verdict (story/reel follow the feed verdict)
                if rv['verdict'] != 'LOLOS':
                    continue  # held: shown to the owner in the daily WA report
                cfg['_draft'] = False
            elif cfg.get('mode') == 'queue':
                cfg['_draft'] = False
            if other(i) and i['guid'] not in oth_day and len(oth_day) >= oth_max:
                continue  # negara pelengkap: maks. other_max_per_day postingan per hari
            for ch in chans:
                k = f"{i['guid']}|{kind}|{ch['id']}"
                if k in done:
                    continue
                # satu format per postingan per channel: sudah jadi Reel -> jangan dikirim lagi sebagai feed (dan sebaliknya)
                if kind in ('feed', 'reel') and f"{i['guid']}|{'reel' if kind == 'feed' else 'feed'}|{ch['id']}" in done:
                    continue
                sv = svc(ch['service'])
                day = sent.setdefault('daily', {}).setdefault(NOW.date().isoformat(), {})
                ck = ch['id'] + '|' + kind
                cap = (cfg.get('daily_caps_by_kind', {}).get(kind) or {}).get(sv)
                if cap is not None and day.get(ck, 0) >= int(cap):
                    continue  # batas harian per jenis (feed/reel/story terpisah)
                rk = ch['id'] + '|' + kind
                if run_count.get(rk, 0) >= int(cfg.get('max_per_channel_per_run', 1)):
                    continue  # disebar ke beberapa run per hari
                if cfg.get('post_mode') != 'now' and kind != 'story' and queued is not None and queued.get(ch['id'], 0) >= max_q:
                    continue  # antrean Buffer channel ini masih ada; tunggu tayang dulu
                if n >= limit:
                    continue
                inp = build(kind, ch, i, cfg)
                if not inp:
                    continue
                try:
                    r = gql(MUT, {"input": inp})['createPost']
                    if r.get('message') and inp.get('mode') == 'shareNow':
                        print('shareNow ditolak, pakai antrean:', r['message'][:120])
                        inp['mode'] = 'addToQueue'
                        r = gql(MUT, {"input": inp})['createPost']
                    if r.get('message'):
                        raise RuntimeError(r['message'])
                    done.add(k); n += 1
                    if other(i) and i['guid'] not in oth_day:
                        oth_day.append(i['guid'])
                    day[ck] = day.get(ck, 0) + 1
                    run_count[rk] = run_count.get(rk, 0) + 1
                    if kind != 'story' and queued is not None:
                        queued[ch['id']] = queued.get(ch['id'], 0) + 1
                    print('sent', kind, sv, i['guid'], 'skor', sc)
                except Exception as e:
                    errors.append(f"{kind}/{sv}/{i['guid']}: {str(e)[:160]}")
    json.dump(reviews, open(REVIEW_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sent['sent'] = sorted(done)[-3000:]
    sent['daily_other'] = {d: v for d, v in sent.get('daily_other', {}).items() if d >= (NOW.date() - datetime.timedelta(days=7)).isoformat()}
    sent['daily'] = {d: v for d, v in sent.get('daily', {}).items() if d >= (NOW.date() - datetime.timedelta(days=7)).isoformat()}
    sent['last_run'] = NOW.isoformat()
    sent['last_errors'] = errors[-20:]
    sent['waiting_review'] = sorted(waiting)
    json.dump(sent, open(SENT_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'sent {n}; errors {len(errors)}; waiting for QA verdict {len(waiting)}')
    for e in errors[:10]:
        print(' !', e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
