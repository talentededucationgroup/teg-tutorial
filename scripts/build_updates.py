#!/usr/bin/env python3
"""Build data/updates.json (the "What's new" feed for the pricelist website) and,
when OneSignal secrets are set, send ONE short push notification per run.

Sources (all public data files in this repo):
  news.json, scholarships.json, banners.json, jobs.json, accommodation.json
State of what has already been announced: data/updates-state.json
No personal data is read or written. Safe to run many times (idempotent).
"""
import json, os, re, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda f: os.path.join(ROOT, 'data', f)
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(WIB)
TODAY = NOW.date().isoformat()
SITE = 'https://pricelist.talentededucationgroup.com'
MAX_ITEMS = 80
MAX_PUSH_PER_DAY = 3


def load(f, default=None):
    try:
        with open(D(f), encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return default


def txt(v, lang='en'):
    if isinstance(v, dict):
        return v.get(lang) or v.get('en') or v.get('id') or next(iter(v.values()), '')
    return v or ''


def entry(kind, key, title_id, title_en, tab, url_q=None, priority=1, extra=None):
    e = {"id": f"{kind}:{key}", "kind": kind, "date": TODAY, "priority": priority,
         "title": {"id": title_id, "en": title_en}, "tab": tab,
         "url": f"{SITE}/?tab={tab}" + (f"&q={urllib.parse.quote(url_q)}" if url_q else "")}
    if extra:
        e.update(extra)
    return e


import urllib.parse  # noqa: E402


def collect():
    """Return {kind: {key: entry}} for everything currently announceable."""
    out = {"news": {}, "scholarship": {}, "promo": {}, "sponsored": {}, "jobs": {}, "accommodation": {}, "airport": {}}
    n = load('news.json', {}) or {}
    for it in n.get('items', []):
        out['news'][it['id']] = entry('news', it['id'], '📰 ' + txt(it.get('title'), 'id'),
                                      '📰 ' + txt(it.get('title'), 'en'), 'news', priority=2,
                                      extra={"date": it.get('date') or TODAY, "country": it.get('country'),
                                             "source": next((l['url'] for l in it.get('links', []) if l.get('official')), None)})
    s = load('scholarships.json', {}) or {}
    for it in s.get('items', []):
        name = it.get('name', '')
        en = (it.get('i18n', {}).get('en', {}) or {}).get('name') or name
        st = it.get('status', '')
        key = it['id'] + ('|open' if st == 'Buka' else '')
        dl = it.get('deadline') or ''
        out['scholarship'][key] = entry(
            'scholarship', key,
            ('🎓 Beasiswa dibuka: ' if st == 'Buka' else '🎓 Beasiswa baru: ') + name + (f' (deadline {dl})' if dl else ''),
            ('🎓 Scholarship open: ' if st == 'Buka' else '🎓 New scholarship: ') + en + (f' (deadline {dl})' if dl else ''),
            'scholarships', url_q=name, priority=2 if st == 'Buka' else 1, extra={"country": it.get('country'), "provider": it.get('provider'), "source": it.get('url')})
    b = load('banners.json', {}) or {}
    for it in b.get('items', []):
        if not it.get('approved'):
            continue
        if it.get('start', '') > TODAY or it.get('end', '9999') < TODAY:
            continue
        prov = it.get('provider', '')
        hl_id, hl_en = txt(it.get('headline'), 'id'), txt(it.get('headline'), 'en')
        is_promo = any(w in (hl_en + ' ' + txt(it.get('text'), 'en')).lower()
                       for w in ('scholarship', 'bursary', 'discount', 'promo', '% ', 'award', 'free'))
        kind = 'promo' if is_promo else 'sponsored'
        pri = 3 if it.get('paid') else (2 if is_promo else 1)
        out[kind][it['id']] = entry(kind, it['id'], ('🔥 Promo: ' if is_promo else '⭐ ') + hl_id,
                                    ('🔥 Promo: ' if is_promo else '⭐ ') + hl_en, 'programs',
                                    url_q=(it.get('match') or {}).get('q') or prov, priority=pri,
                                    extra={"paid": bool(it.get('paid')), "provider": prov,
                                           "country": (it.get('match') or {}).get('country') or ('AU' if it.get('cricos') else None),
                                           "source": (it.get('source') if str(it.get('source') or '').startswith('http') else None) or it.get('website')})
    j = load('jobs.json', {}) or {}
    for it in j.get('items', []):
        out['jobs'][it['id']] = it.get('country') or 'other'
    c = load('community-postings.json', {}) or {}
    for it in c.get('jobs', []):
        out['jobs'][it['id']] = it.get('city') or it.get('country') or 'other'
    for it in c.get('accommodation', []):
        out['accommodation'][it['id']] = it.get('city') or it.get('country') or ''
    for it in c.get('airport_pickup', []):
        if not it.get('hidden'):
            out['airport'][it['id']] = it.get('city') or it.get('country') or ''
    a = load('accommodation.json', {}) or {}
    for it in (a.get('items') or []) + (a.get('postings') or []):
        if isinstance(it, dict) and it.get('id'):
            out['accommodation'][it['id']] = it.get('city') or it.get('country') or ''
    return out


def main():
    cur = collect()
    state = load('updates-state.json')
    feed = load('updates.json') or {}
    items = feed.get('items', [])
    first_run = state is None
    state = state or {"seen": {}, "push_log": [], "pending": []}
    new = []
    for kind, d in cur.items():
        seen = set(state['seen'].get(kind, []))
        fresh = [k for k in d if k not in seen]
        if not first_run and fresh:
            if kind in ('jobs', 'accommodation', 'airport'):
                # aggregate: one entry per run, never one per listing
                places = sorted({d[k] for k in fresh if d[k]})[:4]
                where_en = ', '.join(places)
                if kind == 'jobs':
                    e = entry('jobs', TODAY + '-' + str(len(fresh)), f'💼 {len(fresh)} lowongan kerja baru' + (f' ({where_en})' if where_en else ''),
                              f'💼 {len(fresh)} new part-time/student jobs' + (f' ({where_en})' if where_en else ''), 'jobs')
                elif kind == 'airport':
                    e = entry('airport', TODAY + '-' + str(len(fresh)), f'✈️ {len(fresh)} layanan jemput bandara baru' + (f' ({where_en})' if where_en else ''),
                              f'✈️ {len(fresh)} new airport pickup services' + (f' ({where_en})' if where_en else ''), 'airport')
                else:
                    e = entry('accommodation', TODAY + '-' + str(len(fresh)), f'🏠 {len(fresh)} info akomodasi baru' + (f' ({where_en})' if where_en else ''),
                              f'🏠 {len(fresh)} new accommodation listings' + (f' ({where_en})' if where_en else ''), 'accommodation')
                new.append(e)
            else:
                new.extend(d[k] for k in fresh)
        state['seen'][kind] = sorted(set(d) | seen)
    if first_run:
        # seed the feed with the most recent news (7 days) and today's paid/promo slides
        week = (NOW.date() - datetime.timedelta(days=7)).isoformat()
        n = load('news.json', {}) or {}
        recent = {i['id'] for i in n.get('items', []) if i.get('date', '') >= week}
        new = [e for k, e in cur['news'].items() if k in recent]
    flat = {e['id']: e for d in cur.values() for e in d.values() if isinstance(e, dict)}
    for i in items:
        if i['id'] in flat:
            for k in ('country', 'provider'):
                if flat[i['id']].get(k) and not i.get(k):
                    i[k] = flat[i['id']][k]
    existing = {i['id'] for i in items}
    new = [e for e in new if e['id'] not in existing]
    items = sorted(new + items, key=lambda e: (e['date'], e.get('priority', 1)), reverse=True)[:MAX_ITEMS]
    feed = {
        "version": NOW.strftime('%Y-%m-%dT%H:%M:%S+07:00'),
        "note": "Feed 'Yang baru' untuk website. Dibuat otomatis oleh scripts/build_updates.py (GitHub Actions). Jangan diedit manual.",
        "kinds": {
            "news": {"id": "Berita imigrasi", "en": "Immigration news"},
            "scholarship": {"id": "Beasiswa", "en": "Scholarships"},
            "promo": {"id": "Promo", "en": "Promotions"},
            "sponsored": {"id": "Sekolah & layanan unggulan", "en": "Featured schools & services"},
            "jobs": {"id": "Lowongan kerja", "en": "Jobs"},
            "accommodation": {"id": "Akomodasi", "en": "Accommodation"},
            "airport": {"id": "Jemput bandara", "en": "Airport pickup"}},
        "items": items}
    if new:
        state['pending'] = (state.get('pending', []) + [e['id'] for e in new])[-50:]
    maybe_push(state, items)
    write_rss(items)
    json.dump(feed, open(D('updates.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(state, open(D('updates-state.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f"new entries: {len(new)}; feed size: {len(items)}; pending push: {len(state.get('pending', []))}")


CLOSING = ("Talented Education Group | PT. Pilar Pendidikan Internasional\n"
           "Guiding Futures, Creating Opportunities.\n"
           "talentededucationgroup.com · S&K berlaku.\n"
           "IG/FB/YouTube @talented.e.g · TikTok @talented.education · X @group_talented\n"
           "Cek biaya kuliah Australia, NZ, Kanada, Inggris & Korea dalam semenit (dana awal, total biaya & saran rekening koran visa): "
           "https://pricelist.talentededucationgroup.com/ Bisa dipasang jadi App Talented, gratis. Free Mock Test IELTS/PTE/HSK/TOPIK/JLPT juga tersedia.")
LT = 'https://linktr.ee/talentededucationgroup'
HASH = {'AU': '#KuliahDiAustralia', 'NZ': '#KuliahDiNewZealand', 'GB': '#KuliahDiInggris', 'CA': '#KuliahDiKanada'}


SECRET = re.compile(r"yes\s*edu|yesedugroup|\baig\b|australian\s+international\s+group|upgrad|\bgsp\b|\bapg\b|asia\s+pacific\s+group|"
                    r"potongan\s+agen|komisi\s+agen|agent\s+commission|master\s+agent|harga\s+agen|agent\s+price|special\s+price\s+agent", re.I)


def official_link(e):
    """official source URL for terms that may need clarification; never a master-agent / partner-portal link"""
    u = (e.get('source') or '').strip()
    if not u.startswith('https://') or SECRET.search(u) or any(b in u.lower() for b in ('drive.google', 'dropbox', 'wetransfer', 'agent')):
        return None
    return u


def caption(e, t):
    """Universal caption (Panduan bagian M). Weekly marketing posts bring their own caption; closing is enforced."""
    from make_social_cards import credit_for, idate
    import re as _re
    cr = credit_for(e['id'])
    if e.get('caption'):
        c = e['caption'].strip()
        if 'Guiding Futures, Creating Opportunities.' not in c:
            c += '\n\n' + CLOSING
    else:
        from make_social_cards import split_title
        t2, dl0 = split_title(t)
        dl = idate(dl0, True) if dl0 else None
        k = e['kind']
        if k == 'scholarship':
            op = f"{t2} sedang dibuka" + (f", pendaftaran ditutup {dl}" if dl else '') + f". Info lengkap: {LT}"
            body = ("Syarat, besaran beasiswa dan cara daftarnya beda-beda tiap kampus atau lembaga. Tim Talented bisa bantu cek apakah kamu memenuhi syarat "
                    "dan menyiapkan berkasnya, gratis.\n\nScan QR di gambar atau klik link di bio untuk konsultasi.")
        elif k in ('promo', 'sponsored'):
            op = f"{t2}. Detail program dan biaya bisa dicek lewat {LT}"
            body = ("Biaya final selalu mengikuti offer letter resmi kampus. Kami bantu hitung total biaya, dana awal dan saran rekening koran untuk visa, gratis.\n\n"
                    "Scan QR di gambar atau klik link di bio.")
        elif k == 'news':
            op = f"{t2}. Ringkasan dan link sumber resminya ada di {LT}"
            body = ("Aturan visa bisa berubah, jadi selalu cek sumber resmi pemerintah. Kalau bingung apakah perubahan ini berpengaruh ke rencana kuliahmu, "
                    "tanya tim Talented, gratis.")
        elif k == 'accommodation':
            op = f"{t2}, lengkap dengan kisaran harga per minggu. Cek di {LT}"
            body = "Pilih yang dekat kampus dan cek dulu bond serta minimum stay. Jangan transfer uang sebelum lihat kamar atau kontrak resmi."
        else:
            op = f"{t2}. Cek di {LT}"
            body = "Lowongan yang asli tidak pernah minta biaya pendaftaran. Cek juga batas jam kerja visa pelajarmu."
        if len(op) > 230:
            op = op[:226 - len(LT)].rsplit(' ', 1)[0] + '... ' + LT
        c = op + '\n\n' + body + '\n\n' + CLOSING
        from social_photos import code as _cc
        tags = [HASH.get(_cc(e.get('country')), '#KuliahLuarNegeri'),
                '#BeasiswaLuarNegeri' if k == 'scholarship' else '#StudyAbroad', '#TalentedEducation']
        c += '\n\n' + ' '.join(tags)
    src = official_link(e)
    if src and src not in c:
        lab = {'news': 'Sumber resmi pemerintah', 'scholarship': 'Ketentuan resmi beasiswa'}.get(e['kind'], 'Ketentuan resmi')
        lines = c.split('\n\n')
        # insert before the fixed closing block
        i = next((k for k, b in enumerate(lines) if b.startswith('Talented Education Group | PT.')), len(lines))
        lines.insert(i, f'{lab}: {src}')
        c = '\n\n'.join(lines)
    if cr:
        c += '\n' + cr
    return c


def write_rss(items):
    """social-feed.xml: RSS for auto-posting tools (IFTTT/Zapier -> Buffer -> FB/IG/X/LinkedIn/Google Business).
    Only public, already-announced items. Links carry UTM so traffic is measurable."""
    from xml.sax.saxutils import escape as x
    import email.utils
    tags = {"scholarship": "#beasiswa #kuliahluarnegeri #studyabroad", "promo": "#promo #studyabroad",
            "news": "#visa #infoimigrasi #studyabroad", "sponsored": "#studyabroad #kuliahdiluarnegeri",
            "jobs": "#kerjapartime #studentjobs", "accommodation": "#akomodasi #studentaccommodation"}
    out, out_story, out_reel = [], [], []
    import urllib.parse as _up
    import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from make_social_cards import make_card, cleanup
    # extra ready-made marketing posts written by the weekly marketing task (data/social-posts.json)
    sp = load('social-posts.json', {}) or {}
    extra = []
    for p in sp.get('items', []):
        if p.get('date', '') <= TODAY and p.get('id') and p.get('title'):
            extra.append({"id": "post:" + p['id'], "kind": "marketing", "date": p['date'], "title": {"id": p['title']},
                          "caption": p.get('caption'), "sub": p.get('sub'), "spec": p.get('design'), "source": p.get('source_url'), "country": p.get('country') or 'ANY', "provider": p.get('provider'), "url": p.get('url') or SITE + '/'})
    for e in sorted(extra + items[:30], key=lambda e: e['date'], reverse=True)[:40]:
        if e.get('kind') == 'sponsored' and not e.get('paid'):
            continue  # unpaid third parties are never promoted as sponsored on social media
        link = e['url'] + ('&' if '?' in e['url'] else '?') + 'utm_source=social&utm_medium=autopost&utm_campaign=' + e['kind']
        try:
            d = datetime.datetime.fromisoformat(e['date']).replace(hour=9, tzinfo=WIB)
        except Exception:
            d = NOW
        t = e['title']['id']
        spec = e.get('spec')
        if e['kind'] == 'news' and not spec:
            from make_social_cards import idate as _idate
            dom = re.sub(r'^https?://(www\.)?([^/]+).*$', r'\2', e.get('source') or '')
            spec = {"info": [f"Diumumkan {_idate(e.get('date'))}"] + ([f"Sumber resmi: {dom}"] if dom else [])}
        img = make_card(e['kind'], t, e['id'], e.get('sub'), e.get('country') or 'ANY', e.get('provider'), spec)
        if not img:
            continue  # QA failed: never publish a broken design
        desc = caption(e, t)
        if SECRET.search(desc) or SECRET.search(t):
            print('BLOCKED (business secret in text):', e['id'])
            continue
        out.append(f"<item><title>{x(t)}</title><link>{x(link)}</link><guid isPermaLink=\"false\">{x(e['id'])}</guid>"
                   f"<pubDate>{email.utils.format_datetime(d)}</pubDate><category>{x(e['kind'])}</category>"
                   f"<description>{x(desc)}</description>"
                   f"<enclosure url=\"{x(img)}\" type=\"image/png\" length=\"0\"/></item>")
        base_file = os.path.join(ROOT, 'social', 'cards', _up.unquote(img.rsplit('/', 1)[1]))
        head = (f"<item><title>{x(t)}</title><link>{x(link)}</link><guid isPermaLink=\"false\">{x(e['id'])}</guid>"
                f"<pubDate>{email.utils.format_datetime(d)}</pubDate><category>{x(e['kind'])}</category>"
                f"<description>{x(desc)}</description>")
        if os.path.exists(base_file[:-4] + ' Story.png'):
            out_story.append(head + f"<enclosure url=\"{x(img[:-4] + '%20Story.png')}\" type=\"image/png\" length=\"0\"/></item>")
        if os.path.exists(base_file[:-4] + ' Reel.mp4'):
            sz = os.path.getsize(base_file[:-4] + ' Reel.mp4')
            out_reel.append(head + f"<enclosure url=\"{x(img[:-4] + '%20Reel.mp4')}\" type=\"video/mp4\" length=\"{sz}\"/></item>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
           '<title>Talented Education Group - Yang baru</title>'
           f'<link>{SITE}/</link><description>Beasiswa, promo, berita visa, lowongan kerja &amp; akomodasi pelajar</description>'
           f'<language>id</language><lastBuildDate>{email.utils.format_datetime(NOW)}</lastBuildDate>'
           + ''.join(out) + '</channel></rss>')
    open(os.path.join(ROOT, 'social-feed.xml'), 'w', encoding='utf-8').write(xml)
    for fn, lst, ttl in (('social-feed-story.xml', out_story, 'Story 9:16'), ('social-feed-reels.xml', out_reel, 'Reels 9:16')):
        open(os.path.join(ROOT, fn), 'w', encoding='utf-8').write(
            '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f'<title>Talented Education Group - {ttl}</title><link>{SITE}/</link><description>{ttl} otomatis</description>'
            f'<language>id</language><lastBuildDate>{email.utils.format_datetime(NOW)}</lastBuildDate>' + ''.join(lst) + '</channel></rss>')
    try:
        cleanup()
    except Exception:
        pass


def maybe_push(state, items):
    app_id, key = os.environ.get('ONESIGNAL_APP_ID'), os.environ.get('ONESIGNAL_REST_API_KEY')
    pend = state.get('pending', [])
    if not pend:
        return
    if not (app_id and key):
        print('OneSignal secrets not set: feed updated, push skipped (pending kept).')
        state['pending'] = pend[-50:]
        return
    if not (7 <= NOW.hour < 21):
        print('Quiet hours (21:00-07:00 WIB): push deferred.')
        return
    today_count = sum(1 for t in state.get('push_log', []) if t.startswith(TODAY))
    if today_count >= MAX_PUSH_PER_DAY:
        print('Daily push limit reached: deferred.')
        return
    by_id = {i['id']: i for i in items}
    es = [by_id[p] for p in pend if p in by_id]
    if not es:
        state['pending'] = []
        return
    es.sort(key=lambda e: e.get('priority', 1), reverse=True)
    top = es[0]
    more = len(es) - 1
    body_en = top['title']['en'] + (f' (+{more} more updates)' if more else '')
    body_id = top['title']['id'] + (f' (+{more} update lain)' if more else '')
    payload = {"app_id": app_id, "included_segments": ["Total Subscriptions"],
               "headings": {"en": "Talented: what's new", "id": "Talented: yang baru"},
               "contents": {"en": body_en, "id": body_id},
               "url": top['url'] if not more else SITE + '/?updates=1'}
    req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print('push sent', r.status)
        state['push_log'] = (state.get('push_log', []) + [NOW.isoformat()])[-30:]
        state['pending'] = []
    except Exception as ex:  # keep pending, try next run
        print('push failed:', str(ex)[:200])


if __name__ == '__main__':
    sys.exit(main())
