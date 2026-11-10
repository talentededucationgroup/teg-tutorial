"""Update data/jobs.json from the Adzuna API (daily, run by GitHub Actions).

Rules (TEG): only postings whose original date (Adzuna `created`) is within 6 months (183 days),
still returned by the source (= still listed), approved source only, short factual
fields + link (no full descriptions, photos or logos), suspicious postings held.
Secrets: ADZUNA_APP_ID, ADZUNA_APP_KEY (GitHub repository secrets; never in code).
"""
import json, os, sys, time, hashlib, datetime, urllib.request, urllib.parse, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jobs_i18n import TITLE, SCHEDULE, DISCLAIMER as DISC_I18N
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'jobs.json')
LOG = os.path.join(ROOT, 'data', 'jobs-log.json')
ALERTS = os.path.join(ROOT, 'jobs-alerts.txt')  # read by the workflow, not committed
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(datetime.timezone.utc)
MAX_AGE_DAYS = 183  # pemilik TEG: boleh iklan sampai 6 bulan
STALE_HIDE_DAYS = 3  # hide if not re-verified for this many days (source failures)

CITIES = {
    'au': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Darwin', 'Canberra', 'Gold Coast'],
    'nz': ['Auckland', 'Hamilton', 'Wellington', 'Palmerston North', 'Dunedin', 'Invercargill', 'New Plymouth'],
    'ca': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa', 'Halifax'],
    'gb': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Edinburgh', 'Glasgow'],
    'de': ['Berlin', 'München', 'Hamburg', 'Frankfurt am Main', 'Köln'],
    'sg': ['Singapore'],
}
COUNTRY = {'au': ('Australia', 'AUD'), 'nz': ('New Zealand', 'NZD'), 'ca': ('Canada', 'CAD'),
           'gb': ('United Kingdom', 'GBP'), 'de': ('Germany', 'EUR'), 'sg': ('Singapore', 'SGD')}
# Jepang & Korea Selatan tidak didukung Adzuna API -> website menampilkan direktori portal resmi (data/directory.json)
QUERY_DE = 'Werkstudent Aushilfe Minijob Teilzeit Kellner Servicekraft Küchenhilfe Barista Verkäufer Lagerhelfer Reinigungskraft Student'
QUERY = 'casual part-time barista kitchen hand waiter waitress retail cleaner warehouse housekeeping café hospitality crew support worker'
PER_CITY = 50  # fetched per city; filtered to student-friendly roles below
STUDENT_KEYWORDS = ['barista', 'kitchen', 'cook', 'chef', 'dishwash', 'waiter', 'waitress', 'waitstaff', 'wait staff', 'food', 'hospitality',
                    'bar attendant', 'bartender', 'cafe', 'café', 'restaurant', 'crew', 'team member', 'retail', 'sales assistant',
                    'store', 'shop', 'customer service', 'cashier', 'checkout', 'cleaner', 'cleaning', 'housekeep', 'room attendant',
                    'laundry', 'warehouse', 'picker', 'packer', 'pick pack', 'storeperson', 'labourer', 'process worker',
                    'delivery', 'courier', 'driver', 'support worker', 'aged care', 'disability support', 'personal care',
                    'childcare', 'early childhood', 'educator', 'tutor', 'receptionist', 'admin assistant', 'administration assistant',
                    'data entry', 'casual', 'part time', 'part-time', 'student',
                    'werkstudent', 'aushilfe', 'minijob', 'teilzeit', 'kellner', 'servicekraft', 'küche', 'kuche', 'verkäufer',
                    'verkauf', 'kasse', 'lager', 'kommission', 'reinigung', 'fahrer', 'zusteller', 'studentische']
EXCLUDE_KEYWORDS = ['senior', 'manager', 'director', 'head of', 'lead ', 'principal', 'consultant', 'psychiatrist', 'doctor',
                    'registrar', 'specialist', 'engineer', 'lawyer', 'solicitor', 'accountant', 'planner', 'executive', 'officer',
                    'registered nurse', 'surgeon', 'physician', 'apprentice', 'therapist', 'teacher', 'locum', 'psycholog', 'citizen', 'pr only', 'permanent resident',
                    'leiter', 'leitung', 'ingenieur', 'arzt', 'singaporean only', 'singapore citizen']
SUSPICIOUS = ['upfront fee', 'registration fee', 'pay a fee', 'pay to apply', 'training fee', 'deposit required', 'telegram',
              'whatsapp only', 'bitcoin', 'crypto', 'western union', 'gift card', 'processing fee', 'send your passport',
              'bank details to apply', 'cash in hand guaranteed']
LANGS = ('en', 'th', 'vi', 'zh', 'ja', 'ko', 'km', 'fr', 'pt', 'es', 'de', 'it', 'nl', 'ru')


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': 'application/json',
                                                                              'User-Agent': 'TEG-student-site/1.0'}), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429:  # client/auth error: no point retrying
                raise
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def err_info(e):
    # short, secret-free description of an error (HTTP code + first part of the API's error message)
    if isinstance(e, urllib.error.HTTPError):
        msg = ''
        try:
            msg = e.read(300).decode('utf-8', 'replace')
        except Exception:
            pass
        for v in (os.environ.get('ADZUNA_APP_ID') or '', os.environ.get('ADZUNA_APP_KEY') or ''):
            if v:
                msg = msg.replace(v, '***')
        return f'HTTP {e.code} {msg[:200]}'.strip()
    return type(e).__name__


def parse_date(s):
    try:
        return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def load(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def transform(r, cc, city):
    country, cur = COUNTRY[cc]
    created = parse_date(r.get('created') or '')
    title = (r.get('title') or '').strip()
    company = ((r.get('company') or {}).get('display_name') or '').strip()
    desc = (r.get('description') or '').lower()
    pay = 'tidak dicantumkan'
    if str(r.get('salary_is_predicted', '0')) == '0' and (r.get('salary_min') or r.get('salary_max')):
        lo, hi = r.get('salary_min'), r.get('salary_max')
        pay = f"{cur} {lo:,.0f}" + (f" - {hi:,.0f}" if hi and hi != lo else '') + ' (satuan sesuai iklan asli)'
    jt = {'part_time': 'Part-time', 'full_time': 'Full-time'}.get(r.get('contract_time') or '', 'tidak dicantumkan')
    ct = {'permanent': 'Permanent', 'contract': 'Contract/Casual'}.get(r.get('contract_type') or '', '')
    item = {
        'id': hashlib.sha1(('adzuna:' + str(r.get('id'))).encode()).hexdigest()[:16],
        'source_id': 'adzuna', 'source_name': 'Jobs by Adzuna', 'external': True,
        'position': title or 'tidak dicantumkan', 'company': company or 'tidak dicantumkan',
        'country': country, 'country_code': cc.upper(), 'city': city, 'location': ((r.get('location') or {}).get('display_name') or city),
        'job_type': ', '.join(x for x in (jt, ct) if x), 'hours': 'tidak dicantumkan', 'pay': pay,
        'category': ((r.get('category') or {}).get('label') or ''),
        'requirements': 'lihat iklan asli', 'how_to_apply': 'Lamar di situs asli (link)',
        'link': r.get('redirect_url') or '',
        'posted_date': created.astimezone(WIB).date().isoformat() if created else '',
        'closing_date': 'tidak dicantumkan',
        'fetched_at': NOW.astimezone(WIB).isoformat(timespec='seconds'),
        'last_verified': NOW.astimezone(WIB).isoformat(timespec='seconds'),
        'verification_status': 'Pemeriksaan otomatis',
        'verification_checks': ['Sumber disetujui admin (Adzuna API resmi)', 'Tanggal posting asli dari sumber',
                                'Masih tercantum di sumber pada tanggal cek', 'Tidak ditemukan kata kunci indikasi penipuan'],
        'visa_note': 'Cek hak kerja di visa kamu sebelum melamar.',
        'visa_note_en': 'Check the work rights on your visa before applying.',
        'verification_status_en': 'Automated checks',
        'verification_checks_en': ['Admin-approved source (official Adzuna API)', 'Original posting date from the source',
                                   'Still listed at the source on the check date', 'No fraud-indicator keywords found'],
    }
    if pay == 'tidak dicantumkan': item['pay_en'] = 'not stated'
    else: item['pay_en'] = pay.replace('(satuan sesuai iklan asli)', '(unit as in the original ad)')
    reasons = []
    if not created:
        reasons.append('tanggal posting asli tidak ada')
    elif (NOW - created).days > MAX_AGE_DAYS:
        reasons.append('lebih dari 6 bulan')
    if not item['link'].startswith('https://'):
        reasons.append('link tidak valid')
    hits = [k for k in SUSPICIOUS if k in desc or k in title.lower()]
    if hits:
        reasons.append('indikasi penipuan: ' + ', '.join(hits))
    return item, reasons


def main():
    app_id, app_key = os.environ.get('ADZUNA_APP_ID'), os.environ.get('ADZUNA_APP_KEY')
    if not app_id or not app_key:
        print('Lewati: secret ADZUNA_APP_ID / ADZUNA_APP_KEY belum diisi (jobs.json tidak diubah)'); sys.exit(0)
    prev = load(OUT, {})
    # keep multilingual fixed texts (title_xx, disclaimer_xx, schedule_xx, labels_xx, item_text) across runs
    keep = {k: v for k, v in prev.items() if k == 'item_text' or (k.rsplit('_', 1)[-1] in LANGS and k.rsplit('_', 1)[0] == 'labels')}
    prev_items = {i['id']: i for i in prev.get('items', [])}
    items, held, failed, ok_cities, alerts = {}, [], [], set(), []
    for cc, cities in CITIES.items():
        for city in cities:
            q = urllib.parse.urlencode({'app_id': app_id, 'app_key': app_key, 'results_per_page': PER_CITY, 'where': city,
                                        'what_or': (QUERY_DE if cc == 'de' else QUERY), 'max_days_old': MAX_AGE_DAYS, 'sort_by': 'date', 'content-type': 'application/json'})
            try:
                data = get(f'https://api.adzuna.com/v1/api/jobs/{cc}/search/1?{q}')
                ok_cities.add(city)
            except Exception as e:
                info = err_info(e)
                print(f'Gagal {city}: {info}')
                failed.append({'city': city, 'error': info})
                if info.startswith('HTTP 401') or info.startswith('HTTP 403'):
                    alerts.append('Kunci API ditolak (401/403): cek secret ADZUNA_APP_ID & ADZUNA_APP_KEY dan status akun Adzuna.')
                    break
                continue
            kept = 0
            for r in data.get('results', []):
                t = (r.get('title') or '').lower()
                if not any(k in t for k in STUDENT_KEYWORDS) or any(k in t for k in EXCLUDE_KEYWORDS):
                    continue
                if kept >= 15:
                    break
                it, reasons = transform(r, cc, city)
                if it['id'] in items:
                    continue
                if reasons:
                    held.append({'id': it['id'], 'position': it['position'], 'company': it['company'], 'city': city,
                                 'posted_date': it['posted_date'], 'reason': '; '.join(reasons)})
                    if any(x.startswith('indikasi') for x in reasons):
                        alerts.append(f"Indikasi penipuan ditahan: {it['position']} - {it['company']} ({city})")
                    continue
                old = prev_items.get(it['id'])
                if old and old.get('posted_date'):
                    it['posted_date'] = old['posted_date']  # never refresh the original posting date
                    it['fetched_at'] = old.get('fetched_at', it['fetched_at'])
                items[it['id']] = it
                kept += 1
            time.sleep(3)  # batas per menit Adzuna
    # cities whose source check failed: keep previous items without refreshing last_verified; hide if stale
    for pid, old in prev_items.items():
        if pid in items or old.get('city') in ok_cities:
            continue
        lv = parse_date(old.get('last_verified', ''))
        if lv and (NOW - lv).days < STALE_HIDE_DAYS and (NOW.date() - datetime.date.fromisoformat(old['posted_date'])).days <= MAX_AGE_DAYS:
            old['verification_status'] = 'Belum berhasil diperiksa ulang'
            old['verification_status_en'] = 'Re-check not successful yet'
            items[pid] = old
    if failed:
        alerts.append('Sumber gagal diperiksa untuk kota: ' + ', '.join(f['city'] for f in failed))
    total_cities = sum(len(v) for v in CITIES.values())
    if len(failed) == total_cities or (failed and not ok_cities):
        print('ERROR: semua permintaan ke sumber gagal - data lama dipertahankan')
        write_log({'time': NOW.astimezone(WIB).isoformat(timespec='seconds'), 'result': 'gagal', 'failed': failed})
        with open(ALERTS, 'w', encoding='utf-8') as f: f.write('\n'.join(alerts))
        sys.exit(1)
    out = {'title': TITLE['id'], 'source': 'Jobs by Adzuna (https://www.adzuna.com)',
           'attribution': 'Jobs by Adzuna', 'schedule': SCHEDULE['id'],
           'countries': [v[0] for v in COUNTRY.values()],
           'updated_at': NOW.astimezone(WIB).isoformat(timespec='seconds'), 'posting_window_days': MAX_AGE_DAYS,
           'disclaimer': DISC_I18N['id'],
           'labels_en': {'tidak dicantumkan': 'not stated', 'lihat iklan asli': 'see original ad',
                         'Lamar di situs asli (link)': 'Apply on the original site (link)'},
           'count': len(items),
           'items': sorted(items.values(), key=lambda i: (i['country'], i['city'], i['posted_date']), reverse=False),
           'held_for_review': held}
    for lg in LANGS:
        out['title_' + lg], out['schedule_' + lg], out['disclaimer_' + lg] = TITLE[lg], SCHEDULE[lg], DISC_I18N[lg]
    for k, v in keep.items():
        out.setdefault(k, v)
    tmp = OUT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    json.load(open(tmp, encoding='utf-8'))
    os.replace(tmp, OUT)
    write_log({'time': out['updated_at'], 'result': 'berhasil', 'published': len(items), 'held': len(held), 'failed': failed,
               'added': len(set(items) - set(prev_items)), 'removed': len(set(prev_items) - set(items))})
    if alerts:
        with open(ALERTS, 'w', encoding='utf-8') as f: f.write('\n'.join(alerts))
    print(f'OK: {len(items)} lowongan, {len(held)} ditahan, {len(failed)} kota gagal')


def write_log(entry):
    log = load(LOG, {'runs': []})
    log['runs'] = ([entry] + log.get('runs', []))[:90]
    with open(LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
