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
    base = {"channelId": ch['id'], "schedulingType": "automatic", "mode": "addToQueue"}
    if cfg.get('_draft', True):
        base["saveToDraft"] = True
    if kind == 'feed':
        if s not in ('instagram', 'facebook', 'twitter', 'linkedin', 'google', 'threads'):
            return None
        text = x_text(i) if s in ('twitter', 'threads') else (no_hashtags(i['text']) if s == 'google' else i['text'])
        p = dict(base, text=text, assets=[{"image": {"url": i['media']}}])
        if s == 'instagram':
            p['metadata'] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
        elif s == 'facebook':
            p['metadata'] = {"facebook": {"type": "post"}}
        return p
    if kind == 'story':
        if s == 'instagram' and cfg.get('stories', True):
            return dict(base, text='', assets=[{"image": {"url": i['media']}}],
                        metadata={"instagram": {"type": "story", "shouldShareToFeed": False}})
        if s == 'facebook' and cfg.get('stories', True):
            return dict(base, text='', assets=[{"image": {"url": i['media']}}], metadata={"facebook": {"type": "story"}})
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
    limit, n, errors = int(cfg.get('max_per_run', 6)), 0, []
    reviews = load(REVIEW_P, {"note": "Hasil cek otomatis ChatGPT (OpenAI) per postingan sebelum tayang.", "items": {}})
    auto = cfg.get('mode') == 'auto_reviewed' and bool(OAI)
    if cfg.get('mode') == 'auto_reviewed' and not OAI:
        print('mode auto_reviewed but OPENAI_API_KEY not set: posts go to Buffer Drafts instead.')
    for kind, fname in (('feed', 'social-feed.xml'), ('story', 'social-feed-story.xml'), ('reel', 'social-feed-reels.xml')):
        for i in sorted(feed(fname), key=lambda x: x['pub']):
            if not i['media'] or i['pub'] > NOW or (NOW - i['pub']).days > int(cfg.get('max_age_days', 10)):
                continue
            # immigration news: only post while fresh (announced today or yesterday) - owner 20/11/2026
            if i['guid'].startswith('news:') and (NOW - i['pub']).days > int(cfg.get('news_max_age_days', 1)):
                continue
            cfg['_draft'] = True
            if auto:
                rv = reviews['items'].get(i['guid'])
                if not rv and kind == 'feed':
                    try:
                        rv = review(i, cfg); reviews['items'][i['guid']] = rv
                        print('review', i['guid'], rv['verdict'], '; '.join(rv.get('reasons', []))[:200])
                    except Exception as e:
                        errors.append(f"review/{i['guid']}: {str(e)[:160]}"); continue
                if not rv:
                    continue  # story/reel wait for the feed verdict
                if rv['verdict'] != 'LOLOS':
                    continue  # held: shown to the owner in the daily WA report
                cfg['_draft'] = False
            elif cfg.get('mode') == 'queue':
                cfg['_draft'] = False
            for ch in chans:
                k = f"{i['guid']}|{kind}|{ch['id']}"
                caps = cfg.get('daily_caps', {})
                day = sent.setdefault('daily', {}).setdefault(NOW.date().isoformat(), {})
                sv = svc(ch['service'])
                if sv in caps and day.get(ch['id'], 0) >= int(caps[sv]) and k not in done:
                    continue
                if k in done or n >= limit * max(1, len(chans)):
                    continue
                inp = build(kind, ch, i, cfg)
                if not inp:
                    continue
                try:
                    r = gql(MUT, {"input": inp})['createPost']
                    if r.get('message'):
                        raise RuntimeError(r['message'])
                    done.add(k); n += 1
                    day[ch['id']] = day.get(ch['id'], 0) + 1
                    print('sent', kind, svc(ch['service']), i['guid'])
                except Exception as e:
                    errors.append(f"{kind}/{svc(ch['service'])}/{i['guid']}: {str(e)[:160]}")
    json.dump(reviews, open(REVIEW_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sent['sent'] = sorted(done)[-3000:]
    sent['daily'] = {d: v for d, v in sent.get('daily', {}).items() if d >= (NOW.date() - datetime.timedelta(days=7)).isoformat()}
    sent['last_run'] = NOW.isoformat()
    sent['last_errors'] = errors[-20:]
    json.dump(sent, open(SENT_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'sent {n}; errors {len(errors)}')
    for e in errors[:10]:
        print(' !', e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
