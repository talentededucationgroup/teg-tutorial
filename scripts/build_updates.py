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



# Label "Info & promo terbaru" 15 bahasa (aturan multibahasa TEG; terjemahan selain ID/EN: versi bahasa Inggris yang berlaku)
_LANGS = ['id', 'en', 'th', 'vi', 'zh', 'ja', 'ko', 'km', 'fr', 'pt', 'es', 'de', 'it', 'nl', 'ru']
def _l(*v):
    return dict(zip(_LANGS, v))
WALL_LABELS = {
    "title": _l("Info & promo terbaru", "Latest updates & offers", "ข่าวและโปรโมชันล่าสุด", "Tin mới & ưu đãi", "最新资讯与优惠", "最新情報とキャンペーン", "최신 소식 & 프로모션", "ព័ត៌មាន និងប្រូម៉ូសិនថ្មីៗ", "Actualités et offres", "Novidades e ofertas", "Novedades y ofertas", "Neuigkeiten & Angebote", "Novità e offerte", "Nieuws & aanbiedingen", "Новости и акции"),
    "kinds": {
        "scholarship": _l("Beasiswa", "Scholarship", "ทุนการศึกษา", "Học bổng", "奖学金", "奨学金", "장학금", "អាហារូបករណ៍", "Bourse", "Bolsa de estudos", "Beca", "Stipendium", "Borsa di studio", "Beurs", "Стипендия"),
        "promo": _l("Promo", "Promo", "โปรโมชัน", "Ưu đãi", "优惠", "キャンペーン", "프로모션", "ប្រូម៉ូសិន", "Promo", "Promoção", "Promoción", "Aktion", "Promozione", "Actie", "Акция"),
        "sponsored": _l("Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored", "Sponsored"),
        "news": _l("Berita visa", "Visa news", "ข่าววีซ่า", "Tin visa", "签证新闻", "ビザニュース", "비자 뉴스", "ព័ត៌មានទិដ្ឋាការ", "Actualités visa", "Notícias de visto", "Noticias de visados", "Visa-News", "Notizie sui visti", "Visumnieuws", "Новости о визах"),
        "marketing": _l("Info Talented", "Talented info", "ข้อมูล Talented", "Thông tin Talented", "Talented 资讯", "Talented のお知らせ", "Talented 소식", "ព័ត៌មាន Talented", "Infos Talented", "Info Talented", "Info Talented", "Talented-Infos", "Info Talented", "Talented-info", "Новости Talented"),
        "jobs": _l("Loker", "Jobs", "งาน", "Việc làm", "工作", "求人", "채용", "ការងារ", "Emplois", "Vagas", "Empleos", "Jobs", "Lavoro", "Vacatures", "Вакансии"),
        "accommodation": _l("Akomodasi", "Accommodation", "ที่พัก", "Chỗ ở", "住宿", "宿泊先", "숙소", "កន្លែងស្នាក់នៅ", "Logement", "Acomodação", "Alojamiento", "Unterkunft", "Alloggio", "Huisvesting", "Жильё"),
        "airport": _l("Jemput bandara", "Airport pickup", "รับที่สนามบิน", "Đón sân bay", "机场接机", "空港送迎", "공항 픽업", "ទទួលពីព្រលានយន្តហោះ", "Accueil aéroport", "Traslado do aeroporto", "Recogida en el aeropuerto", "Flughafenabholung", "Transfer aeroporto", "Ophalen luchthaven", "Встреча в аэропорту"),
    },
}

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

L15 = ['id', 'en', 'th', 'vi', 'zh', 'ja', 'ko', 'km', 'fr', 'pt', 'es', 'de', 'it', 'nl', 'ru']


def full(v, prefix='', suffix=''):
    """Title dict in all 15 languages (fallback to en/id)."""
    return {l: prefix + txt(v, l) + suffix for l in L15}


def per(tmpl, **kw):
    return {l: tmpl[l].format(**kw) for l in L15}


KINDS = {
    "news": {"id": "Berita imigrasi", "en": "Immigration news", "th": "ข่าวตรวจคนเข้าเมือง", "vi": "Tin di trú", "zh": "移民新闻", "ja": "移民ニュース", "ko": "이민 뉴스", "km": "ព័ត៌មានអន្តោប្រវេសន៍", "fr": "Actualités immigration", "pt": "Notícias de imigração", "es": "Noticias de inmigración", "de": "Einwanderungsnews", "it": "Notizie immigrazione", "nl": "Immigratienieuws", "ru": "Иммиграционные новости"},
    "scholarship": {"id": "Beasiswa", "en": "Scholarships", "th": "ทุนการศึกษา", "vi": "Học bổng", "zh": "奖学金", "ja": "奨学金", "ko": "장학금", "km": "អាហារូបករណ៍", "fr": "Bourses", "pt": "Bolsas de estudo", "es": "Becas", "de": "Stipendien", "it": "Borse di studio", "nl": "Beurzen", "ru": "Стипендии"},
    "promo": {"id": "Promo", "en": "Promotions", "th": "โปรโมชัน", "vi": "Khuyến mãi", "zh": "优惠", "ja": "キャンペーン", "ko": "프로모션", "km": "ប្រូម៉ូសិន", "fr": "Promotions", "pt": "Promoções", "es": "Promociones", "de": "Aktionen", "it": "Promozioni", "nl": "Acties", "ru": "Акции"},
    "sponsored": {"id": "Sekolah & layanan unggulan", "en": "Featured schools & services", "th": "สถาบันและบริการแนะนำ", "vi": "Trường & dịch vụ nổi bật", "zh": "精选院校与服务", "ja": "注目の学校とサービス", "ko": "추천 학교 및 서비스", "km": "សាលា និងសេវាកម្មពិសេស", "fr": "Écoles et services à la une", "pt": "Escolas e serviços em destaque", "es": "Escuelas y servicios destacados", "de": "Empfohlene Schulen & Services", "it": "Scuole e servizi in evidenza", "nl": "Uitgelichte scholen & diensten", "ru": "Рекомендуемые школы и услуги"},
    "jobs": {"id": "Lowongan kerja", "en": "Jobs", "th": "งาน", "vi": "Việc làm", "zh": "工作机会", "ja": "求人", "ko": "채용", "km": "ការងារ", "fr": "Emplois", "pt": "Vagas", "es": "Empleos", "de": "Jobs", "it": "Lavoro", "nl": "Vacatures", "ru": "Вакансии"},
    "accommodation": {"id": "Akomodasi", "en": "Accommodation", "th": "ที่พัก", "vi": "Chỗ ở", "zh": "住宿", "ja": "住まい", "ko": "숙소", "km": "កន្លែងស្នាក់នៅ", "fr": "Logement", "pt": "Acomodação", "es": "Alojamiento", "de": "Unterkunft", "it": "Alloggio", "nl": "Huisvesting", "ru": "Жильё"},
    "airport": {"id": "Jemput bandara", "en": "Airport pickup", "th": "รับที่สนามบิน", "vi": "Đón sân bay", "zh": "接机", "ja": "空港送迎", "ko": "공항 픽업", "km": "ទទួលពីព្រលានយន្តហោះ", "fr": "Accueil à l’aéroport", "pt": "Traslado do aeroporto", "es": "Recogida en el aeropuerto", "de": "Flughafenabholung", "it": "Ritiro in aeroporto", "nl": "Ophalen van het vliegveld", "ru": "Встреча в аэропорту"}}
SCH_OPEN = {"id": "🎓 Beasiswa dibuka: ", "en": "🎓 Scholarship open: ", "th": "🎓 เปิดรับทุน: ", "vi": "🎓 Học bổng đang mở: ", "zh": "🎓 奖学金开放申请：", "ja": "🎓 奨学金募集中：", "ko": "🎓 장학금 모집 중: ", "km": "🎓 អាហារូបករណ៍បើក៖ ", "fr": "🎓 Bourse ouverte : ", "pt": "🎓 Bolsa aberta: ", "es": "🎓 Beca abierta: ", "de": "🎓 Stipendium offen: ", "it": "🎓 Borsa aperta: ", "nl": "🎓 Beurs open: ", "ru": "🎓 Открыт приём на стипендию: "}
SCH_NEW = {"id": "🎓 Beasiswa baru: ", "en": "🎓 New scholarship: ", "th": "🎓 ทุนใหม่: ", "vi": "🎓 Học bổng mới: ", "zh": "🎓 新奖学金：", "ja": "🎓 新しい奨学金：", "ko": "🎓 새 장학금: ", "km": "🎓 អាហារូបករណ៍ថ្មី៖ ", "fr": "🎓 Nouvelle bourse : ", "pt": "🎓 Nova bolsa: ", "es": "🎓 Nueva beca: ", "de": "🎓 Neues Stipendium: ", "it": "🎓 Nuova borsa: ", "nl": "🎓 Nieuwe beurs: ", "ru": "🎓 Новая стипендия: "}
AGG = {
 "jobs": {"id": "💼 {n} lowongan kerja baru{w}", "en": "💼 {n} new part-time/student jobs{w}", "th": "💼 งานพาร์ทไทม์/นักเรียนใหม่ {n} ตำแหน่ง{w}", "vi": "💼 {n} việc làm bán thời gian/sinh viên mới{w}", "zh": "💼 {n} 个新的兼职/学生工作{w}", "ja": "💼 新しいアルバイト・学生向け求人 {n} 件{w}", "ko": "💼 새 파트타임/학생 일자리 {n}개{w}", "km": "💼 ការងារក្រៅម៉ោង/សិស្សថ្មី {n}{w}", "fr": "💼 {n} nouveaux jobs étudiants/temps partiel{w}", "pt": "💼 {n} novas vagas meio período/estudante{w}", "es": "💼 {n} nuevos empleos de medio tiempo/estudiante{w}", "de": "💼 {n} neue Teilzeit-/Studentenjobs{w}", "it": "💼 {n} nuovi lavori part-time/studenti{w}", "nl": "💼 {n} nieuwe bijbaantjes/studentenbanen{w}", "ru": "💼 {n} новых вакансий с частичной занятостью{w}"},
 "airport": {"id": "✈️ {n} layanan jemput bandara baru{w}", "en": "✈️ {n} new airport pickup services{w}", "th": "✈️ บริการรับที่สนามบินใหม่ {n} รายการ{w}", "vi": "✈️ {n} dịch vụ đón sân bay mới{w}", "zh": "✈️ {n} 个新的接机服务{w}", "ja": "✈️ 新しい空港送迎サービス {n} 件{w}", "ko": "✈️ 새 공항 픽업 서비스 {n}개{w}", "km": "✈️ សេវាទទួលពីព្រលានយន្តហោះថ្មី {n}{w}", "fr": "✈️ {n} nouveaux services d’accueil à l’aéroport{w}", "pt": "✈️ {n} novos serviços de traslado{w}", "es": "✈️ {n} nuevos servicios de recogida en aeropuerto{w}", "de": "✈️ {n} neue Flughafenabholungen{w}", "it": "✈️ {n} nuovi servizi di ritiro in aeroporto{w}", "nl": "✈️ {n} nieuwe ophaaldiensten vanaf het vliegveld{w}", "ru": "✈️ {n} новых услуг встречи в аэропорту{w}"},
 "accommodation": {"id": "🏠 {n} info akomodasi baru{w}", "en": "🏠 {n} new accommodation listings{w}", "th": "🏠 ที่พักใหม่ {n} รายการ{w}", "vi": "🏠 {n} chỗ ở mới{w}", "zh": "🏠 {n} 条新的住宿信息{w}", "ja": "🏠 新しい住まい情報 {n} 件{w}", "ko": "🏠 새 숙소 정보 {n}개{w}", "km": "🏠 កន្លែងស្នាក់នៅថ្មី {n}{w}", "fr": "🏠 {n} nouveaux logements{w}", "pt": "🏠 {n} novas opções de acomodação{w}", "es": "🏠 {n} nuevos alojamientos{w}", "de": "🏠 {n} neue Unterkünfte{w}", "it": "🏠 {n} nuovi alloggi{w}", "nl": "🏠 {n} nieuwe woonruimtes{w}", "ru": "🏠 {n} новых вариантов жилья{w}"}}


def entry(kind, key, title_id, title_en, tab, url_q=None, priority=1, extra=None, title=None):
    e = {"id": f"{kind}:{key}", "kind": kind, "date": TODAY, "priority": priority,
         "title": title or {"id": title_id, "en": title_en}, "tab": tab,
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
                                      '📰 ' + txt(it.get('title'), 'en'), 'news', priority=2, title=full(it.get('title'), '📰 '),
                                      extra={"date": it.get('date') or TODAY, "country": it.get('country'),
                                             "source": next((l['url'] for l in it.get('links', []) if l.get('official')), None),
                                             "category": it.get('category')})
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
            'scholarships', url_q=name, priority=2 if st == 'Buka' else 1,
            title={l: (SCH_OPEN if st == 'Buka' else SCH_NEW)[l] + (name if l == 'id' else en) + (f' (deadline {dl})' if dl else '') for l in L15}, extra={"country": it.get('country'), "provider": it.get('provider'), "source": it.get('url')})
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
                                    title=full(it.get('headline'), '🔥 Promo: ' if is_promo else '⭐ '),
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
                              f'💼 {len(fresh)} new part-time/student jobs' + (f' ({where_en})' if where_en else ''), 'jobs',
                              title=per(AGG['jobs'], n=len(fresh), w=(f' ({where_en})' if where_en else '')))
                elif kind == 'airport':
                    e = entry('airport', TODAY + '-' + str(len(fresh)), f'✈️ {len(fresh)} layanan jemput bandara baru' + (f' ({where_en})' if where_en else ''),
                              f'✈️ {len(fresh)} new airport pickup services' + (f' ({where_en})' if where_en else ''), 'airport',
                              title=per(AGG['airport'], n=len(fresh), w=(f' ({where_en})' if where_en else '')))
                else:
                    e = entry('accommodation', TODAY + '-' + str(len(fresh)), f'🏠 {len(fresh)} info akomodasi baru' + (f' ({where_en})' if where_en else ''),
                              f'🏠 {len(fresh)} new accommodation listings' + (f' ({where_en})' if where_en else ''), 'accommodation',
                              title=per(AGG['accommodation'], n=len(fresh), w=(f' ({where_en})' if where_en else '')))
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
            for k in ('country', 'provider', 'source'):
                if flat[i['id']].get(k) and not i.get(k):
                    i[k] = flat[i['id']][k]
    for i in items:
        if i['id'] in flat and len(flat[i['id']].get('title', {})) > len(i.get('title', {})):
            i['title'] = flat[i['id']]['title']
    existing = {i['id'] for i in items}
    new = [e for e in new if e['id'] not in existing]
    items = sorted(new + items, key=lambda e: (e['date'], e.get('priority', 1)), reverse=True)[:MAX_ITEMS]
    feed = {
        "version": NOW.strftime('%Y-%m-%dT%H:%M:%S+07:00'),
        "note": "Feed 'Yang baru' untuk website. Dibuat otomatis oleh scripts/build_updates.py (GitHub Actions). Jangan diedit manual.",
        "kinds": KINDS,
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
            if str(e.get('id', '')).endswith('|open'):
                op = f"{t2} sedang dibuka" + (f", pendaftaran ditutup {dl}" if dl else '') + f". Info lengkap: {LT}"
            else:
                # not open now (status 'Segera dibuka' / 'Tahunan'): never claim it is open (QA 22/11/2026)
                op = f"Info beasiswa: {t2}. Pendaftaran belum dibuka saat ini, jadwal berikutnya belum diumumkan. Info lengkap: {LT}"
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
    # anti copy-paste attribution (owner 20/11/2026)
    attr = ('Dirangkum oleh Talented Education Group dari sumber resmi. Boleh dibagikan dengan menyebut sumber '
            '@talented.e.g, dilarang menyalin ulang tanpa izin.')
    if attr not in c:
        lines = c.split('\n\n')
        i = next((k for k, b in enumerate(lines) if b.startswith('Talented Education Group | PT.')), len(lines))
        lines.insert(i, attr)
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
    out, out_story, out_reel, wall = [], [], [], []
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
    # website promotion 3x per week (owner 20/11/2026): rotate data/site-promo.json
    sp2 = load('site-promo.json', {}) or {}
    if sp2.get('items'):
        for back in range(0, 3):
            dd = NOW.date() - datetime.timedelta(days=back)
            if dd.weekday() not in sp2.get('weekdays', [1, 4, 6]):
                continue
            n_ = (dd.toordinal() // 7) * 3 + sp2.get('weekdays', [1, 4, 6]).index(dd.weekday())
            it = sp2['items'][n_ % len(sp2['items'])]
            cap = it['opening'] + '\n\n' + it['body'] + '\n\nScan QR di gambar atau klik link di bio.\n\n' + CLOSING + '\n\n#StudyAbroad #KuliahLuarNegeri #TalentedEducation'
            extra.append({"id": f"site:{dd.isoformat()}:{it['key']}", "kind": "marketing", "date": dd.isoformat(),
                          "title": {"id": it['title']}, "caption": cap, "country": 'ANY', "provider": None,
                          "spec": it['design'], "url": it['url']})
    # promo jurusan otomatis (pemilik 23/11/2026): Bachelor & Master Australia, kadang VET, jurusan yang dibutuhkan di Australia
    try:
        from program_posts import posts as _program_posts
        extra += _program_posts(NOW, {'lt': LT, 'text': CLOSING})
    except Exception as _e:
        print('program posts skipped:', str(_e)[:160])
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
            spec = {"topic": e.get('category') or 'visa',
                    "info": [f"Diumumkan {_idate(e.get('date'))}"] + ([f"Sumber resmi: {dom}"] if dom else [])}
        img = make_card(e['kind'], t, e['id'], e.get('sub'), e.get('country') or 'ANY', e.get('provider'), spec)
        if not img:
            continue  # QA failed: never publish a broken design
        desc = caption(e, t)
        if SECRET.search(desc) or SECRET.search(t):
            print('BLOCKED (business secret in text):', e['id'])
            continue
        wall.append({"id": e['id'], "kind": e['kind'], "date": e['date'], "title": re.sub(r'^[^\w]+', '', t).strip(),
                     "image": img, "link": e.get('url') or SITE + '/', "source": official_link(e),
                     "caption": (desc.split('\n\n')[0])[:300], "country": e.get('country')})
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
    # video milik Talented (data/social-video-library.json): Reels bergiliran, caption bergantian (pemilik 21/11/2026)
    vl = load('social-video-library.json', {}) or {}
    for v in vl.get('items', []):
        fp = os.path.join(ROOT, v.get('file', ''))
        if not os.path.exists(fp) or not v.get('captions'):
            continue
        try:
            st = datetime.date.fromisoformat(v.get('start', TODAY))
        except Exception:
            continue
        every = max(3, int(v.get('every_days', 14)))
        for back in range(0, 3):
            dd = NOW.date() - datetime.timedelta(days=back)
            k = (dd - st).days
            if k < 0 or k % every:
                continue
            capv = v['captions'][(k // every) % len(v['captions'])]
            desc = capv + '\n\n' + CLOSING + '\n\n' + v.get('hashtags', '#StudyAbroad #TalentedEducation')
            if SECRET.search(desc):
                print('BLOCKED (business secret in text):', v['id']); continue
            vurl = 'https://info.talentededucationgroup.com/' + _up.quote(v['file'])
            link = v.get('url', SITE + '/') + ('&' if '?' in v.get('url', '') else '?') + 'utm_source=social&utm_medium=autopost&utm_campaign=video'
            d = datetime.datetime.combine(dd, datetime.time(10, 0), tzinfo=WIB)
            out_reel.append(f"<item><title>{x(v['title'])}</title><link>{x(link)}</link><guid isPermaLink=\"false\">video:{x(v['id'])}:{dd.isoformat()}</guid>"
                            f"<pubDate>{email.utils.format_datetime(d)}</pubDate><category>marketing</category>"
                            f"<description>{x(desc)}</description>"
                            f"<enclosure url=\"{x(vurl)}\" type=\"video/mp4\" length=\"{os.path.getsize(fp)}\"/></item>")
            if v.get('story', True):
                out_story.append(f"<item><title>{x(v['title'])}</title><link>{x(link)}</link><guid isPermaLink=\"false\">video:{x(v['id'])}:{dd.isoformat()}</guid>"
                                 f"<pubDate>{email.utils.format_datetime(d)}</pubDate><category>marketing</category>"
                                 f"<description>{x(desc)}</description>"
                                 f"<enclosure url=\"{x(vurl)}\" type=\"video/mp4\" length=\"{os.path.getsize(fp)}\"/></item>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
           '<title>Talented Education Group - Yang baru</title>'
           f'<link>{SITE}/</link><description>Beasiswa, promo, berita visa, lowongan kerja &amp; akomodasi pelajar</description>'
           f'<language>id</language><lastBuildDate>{email.utils.format_datetime(NOW)}</lastBuildDate>'
           + ''.join(out) + '</channel></rss>')
    open(os.path.join(ROOT, 'social-feed.xml'), 'w', encoding='utf-8').write(xml)
    # public wall for the pricelist website: only posts that are live / approved (owner 20/11/2026)
    rv = (load('social-review.json', {}) or {}).get('items', {})
    mode = (load('social-autopost.json', {}) or {}).get('mode')
    import urllib.parse as _u2
    live = []
    for w_ in wall:
        if w_['date'] > TODAY:
            continue
        if mode == 'auto_reviewed' and rv and rv.get(w_['id'], {}).get('verdict') not in (None, 'LOLOS'):
            continue
        base = w_['image'][:-4]
        fbase = os.path.join(ROOT, 'social', 'cards', _u2.unquote(base.rsplit('/', 1)[1]))
        w_['story'] = base + '%20Story.png' if os.path.exists(fbase + ' Story.png') else None
        w_['reel'] = base + '%20Reel.mp4' if os.path.exists(fbase + ' Reel.mp4') else None
        live.append(w_)
    json.dump({"version": NOW.strftime('%Y-%m-%dT%H:%M:%S+07:00'),
               "note": "Postingan sosmed Talented terbaru untuk ditampilkan di website (dibuat otomatis, sama dengan yang tayang di sosmed).",
               "labels": WALL_LABELS,
               "items": live[:24]}, open(D('social-wall.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
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
