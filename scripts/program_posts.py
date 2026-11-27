"""Promo jurusan otomatis untuk autopost (pemilik 23/11/2026): kurangi beasiswa, perbanyak promo jurusan
Bachelor & Master Australia, kadang VET, dan jurusan yang dibutuhkan di Australia.
Data: pricelist publik https://pricelist.talentededucationgroup.com/pricelist-data.json.gz (harga siswa, tanpa data internal).
Rotasi deterministik per tanggal (tidak mengulang sekolah dalam 14 hari)."""
import datetime, gzip, json, urllib.request

SRC = 'https://pricelist.talentededucationgroup.com/pricelist-data.json.gz'
SITE = 'https://pricelist.talentededucationgroup.com'
FIELDS = ['Business & Management', 'IT, Data & Cyber Security', 'Accounting & Finance', 'Health & Nursing',
          'Hospitality, Cookery & Tourism', 'Construction, Engineering & Trades', 'Education & Training',
          'Design, Media & Arts', 'Community Services & Early Childhood', 'Science & Environment', 'Law & Criminology']
# Jobs and Skills Australia, 2025 Occupation Shortage List: kesehatan, pendidikan, konstruksi/trades, engineering masih kekurangan tenaga.
SHORTAGE = ['Health & Nursing', 'Community Services & Early Childhood', 'Construction, Engineering & Trades', 'Education & Training']
FID = {'Business & Management': 'Bisnis & Manajemen', 'IT, Data & Cyber Security': 'IT, Data & Cyber Security',
       'Accounting & Finance': 'Akuntansi & Keuangan', 'Health & Nursing': 'Kesehatan & Keperawatan',
       'Hospitality, Cookery & Tourism': 'Hospitality, Cookery & Pariwisata', 'Construction, Engineering & Trades': 'Konstruksi, Teknik & Trades',
       'Education & Training': 'Pendidikan & Mengajar', 'Design, Media & Arts': 'Desain, Media & Seni',
       'Community Services & Early Childhood': 'Early Childhood & Community Services', 'Science & Environment': 'Sains & Lingkungan',
       'Law & Criminology': 'Hukum & Kriminologi'}
VET = ('Certificate III', 'Certificate IV', 'Diploma', 'Advanced Diploma')
PER = {'Term': 'term', 'Trimester': 'trimester', 'Semester': 'semester', 'Unit': 'unit', 'Tahun': 'tahun', 'Year': 'tahun'}
# foto topik per bidang (social/library/topic-<x>); bila library belum ada -> topik kampus 'school'
TOPIC = {'Health & Nursing': 'health', 'Hospitality, Cookery & Tourism': 'cookery', 'IT, Data & Cyber Security': 'it',
         'Construction, Engineering & Trades': 'construction', 'Business & Management': 'business', 'Accounting & Finance': 'business',
         'Community Services & Early Childhood': 'childcare', 'Education & Training': 'childcare'}


def topic_for(field, day, slot, country='AU'):
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    have = lambda t: any(f.endswith(('.jpg', '.png')) for f in os.listdir(os.path.join(root, 'social', 'library', 'topic-' + t))) if os.path.isdir(os.path.join(root, 'social', 'library', 'topic-' + t)) else False
    opts = [t for t in (TOPIC.get(field), 'school') if t and have(t)]  # QA 27/11/2026: foto kota umum bisa beda kota (Perth untuk Melbourne)
    if not opts:
        return 'school'
    return opts[(day.toordinal() + (slot == 'b')) % len(opts)]


NZ_CITIES = ['Auckland', 'Wellington', 'Hamilton', 'Dunedin', 'Palmerston North', 'Invercargill', 'Christchurch']
NZ_VET = ('Diploma', 'Certificate (NZ/negara lain)', 'Certificate IV', 'Graduate Diploma (NZ, Level 7)')
# QA 27/11/2026: harga di pricelist belum cocok dengan harga resmi / belum ada bukti promo -> jangan dipromosikan
# di sosmed sampai pemilik mengonfirmasi (pricelist sendiri tidak diubah). Hapus nama dari daftar setelah terverifikasi.
HOLD_SCHOOLS = ('Australian Agribusiness Institute', 'Asia Pacific International College', 'Albright Institute of Business and Language')
CITIES = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra', 'Gold Coast', 'Hobart', 'Darwin']


def load():
    req = urllib.request.Request(SRC, headers={'User-Agent': 'TalentedAutopost/1.0'})
    raw = urllib.request.urlopen(req, timeout=60).read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    d = json.loads(raw)['student']
    out = []
    for r in d['courses']:
        if r.get('side') != 'Offshore' or r.get('country') not in ('AU', 'NZ') or r.get('suspended') or r.get('expired'):
            continue
        if not r.get('tuition') or not r.get('annual') or r.get('city') not in (CITIES if r['country'] == 'AU' else NZ_CITIES):
            continue
        p = str(r.get('program') or '')
        if any(h.lower() in str(r.get('school') or '').lower() for h in HOLD_SCHOOLS):
            continue
        # QA 27/11/2026 (AIH Master of Research): harga per unit -> estimasi per tahun tidak andal; program riset bukan target promo
        if str(r.get('period') or '').split(' ')[0] == 'Unit' or 'research' in p.lower():
            continue
        if '+' in p or len(p) > 80 or '(' in p and '$' in p:
            continue  # paket / nama panjang: kurang jelas untuk postingan
        out.append(r)
    return out


import re as _re
def dur_id(t):
    t = str(t or '')
    for a, b in (('years', 'tahun'), ('year', 'tahun'), ('months', 'bulan'), ('month', 'bulan'), ('weeks', 'minggu'), ('week', 'minggu')):
        t = _re.sub(r'\b' + a + r'\b', b, t, flags=_re.I)
    return t


def money(n):
    return f"{n:,.0f}".replace(',', '.')


def slots(day):
    """Rencana per tanggal: slot A setiap hari (Bachelor/Master bergantian, Sabtu VET), slot B tiap 2 hari = jurusan dibutuhkan."""
    o = day.toordinal()
    a_level = 'VET' if day.weekday() == 5 else ('Bachelor' if o % 2 == 0 else 'Master')
    plan = [('a', a_level, FIELDS[(o // 2) % len(FIELDS)], CITIES[o % 5])]
    if o % 2 == 1:
        lv = ['Bachelor', 'VET', 'Master'][(o // 2) % 3]
        plan.append(('b', lv, SHORTAGE[(o // 2) % len(SHORTAGE)], CITIES[(o // 2) % 4]))
    elif day >= datetime.date(2026, 11, 24):  # pemilik 23/11/2026: fokus Australia & New Zealand -> selang sehari promo jurusan New Zealand
        lv = ['Bachelor', 'Master', 'VET'][(o // 2) % 3]
        plan.append(('n', lv, FIELDS[(o // 2 + 3) % len(FIELDS)], NZ_CITIES[(o // 2) % 3]))
    return plan


def pick(rows, level, field, city, used):
    vet = NZ_VET + VET if city in NZ_CITIES else VET
    lv = (lambda r: r['level'] in vet) if level == 'VET' else (lambda r: r['level'] == level)
    cities = NZ_CITIES if city in NZ_CITIES else CITIES
    for c in [city] + [x for x in cities if x != city]:
        cand = [r for r in rows if lv(r) and r['field'] == field and r['city'] == c and r['school'] not in used]
        if cand:
            promo = [r for r in cand if 'promo' in str(r.get('note', '')).lower() or (r.get('scholarship') or {}).get('type') not in (None, 'Tidak ada')]
            pool = promo if promo and min(x['annual'] for x in promo) <= 1.3 * min(x['annual'] for x in cand) else cand
            return sorted(pool, key=lambda r: (r['annual'], r['school']))[0]
    return None


def posts(now, closing, back_days=3):
    rows = load()
    out = []
    # sekolah yang dipakai 14 hari terakhir (dihitung ulang secara deterministik)
    hist = {}
    # titik awal TETAP (bukan now-16 hari) supaya pilihan sekolah per hari tidak bergeser antar build
    # (24/11/2026: program:2026-11-23:b berubah dari CIHE ke CDU, poster lama tertimpa caption baru)
    start = datetime.date(2026, 11, 1)
    used = []
    for k in range(0, (now.date() - start).days + 1):
        day = start + datetime.timedelta(days=k)
        for slot, level, field, city in slots(day):
            ex = set(u for d0, u in used if (day - d0).days < 14)
            pool_f = (SHORTAGE if slot == 'b' else FIELDS)
            r = None
            for f2 in [field] + [x for x in pool_f[pool_f.index(field) + 1:] + pool_f[:pool_f.index(field)]]:
                r = pick(rows, level, f2, city, ex)
                if r:
                    field = f2
                    break
            if not r:
                continue
            used.append((day, r['school']))
            hist[(day, slot)] = (level, field, r)
    for back in range(back_days):
        day = now.date() - datetime.timedelta(days=back)
        for slot, level, field, city in slots(day):
            if (day, slot) not in hist:
                continue
            level, field, r = hist[(day, slot)]
            per = PER.get(str(r['period']).split(' ')[0], 'term')
            lvl_id = {'Bachelor': 'S1', 'Master': 'S2', 'Certificate (NZ/negara lain)': 'Certificate',
                      'Graduate Diploma (NZ, Level 7)': 'Graduate Diploma', 'Graduate Certificate/Diploma (AU, AQF 8)': 'Graduate Diploma',
                      'Postgraduate Certificate/Diploma (NZ & negara lain)': 'Postgraduate Diploma'}.get(r['level'], r['level'])
            fid = FID.get(field, field)
            if field == 'Community Services & Early Childhood':  # QA 27/11/2026: judul sesuai program
                pl_ = str(r['program']).lower()
                fid = 'Early Childhood' if 'early childhood' in pl_ else 'Community Services' if 'community' in pl_ else fid
            head = f"{lvl_id} {fid} di {r['city']}"
            cur = r.get('currency') or ('NZD' if r['country'] == 'NZ' else 'AUD')
            hero = f"{cur} {money(r['tuition'])}"
            promo = str(r.get('note', '')) if 'promo' in str(r.get('note', '')).lower() else ''
            sch = (r.get('scholarship') or {}).get('type')
            q = urllib.request.quote(r['school'])
            url = f"{SITE}/?lang=id&q={q}"
            lines = []
            if slot == 'n':
                lines.append(f"🇳🇿 {head} mulai {hero}/{per}! Kuliah di New Zealand: kampus aman & ramah, boleh kerja paruh waktu sesuai aturan visa pelajar. Info: {closing['lt']}")
            elif slot == 'b':
                lines.append(f"🇦🇺 Jurusan yang dibutuhkan di Australia: {fid}.\nMenurut Jobs and Skills Australia (Occupation Shortage List 2025), bidang kesehatan, pendidikan, konstruksi & trades termasuk yang masih kekurangan tenaga kerja. Info: {closing['lt']}")
            else:
                lines.append(f"🔥 {head} mulai {hero}/{per}! Info: {closing['lt']}")
            det = [f"🏫 {r['school']}", f"📚 {r['program']}", f"⏱ {dur_id(r['duration'])} · estimasi ± {cur} {money(r['annual'])}/tahun"]
            if promo:
                det.append(f"🎁 {promo}")
            elif sch == 'Seleksi':
                det.append("🎓 Ada beasiswa kampus (seleksi)")
            if r.get('english'):
                det.append(f"🗣 Bahasa Inggris: {str(r['english'])[:70]}")
            lines.append('\n'.join(det))
            lines.append(f"Cek dana awal, total biaya studi & saran rekening koran untuk visa di pricelist Talented (gratis): {url}\n\n*Perkiraan. Biaya final mengikuti offer letter resmi sekolah.")
            lines.append("Scan QR di gambar atau klik link di bio untuk konsultasi gratis.")
            tags = '#KuliahDiNewZealand #StudyInNewZealand #TalentedEducation' if r['country'] == 'NZ' else '#KuliahDiAustralia #StudyInAustralia #TalentedEducation'
            cap = '\n\n'.join(lines) + '\n\n' + closing['text'] + '\n\n' + tags
            info = [r['school'], f"per {per} · ± {cur} {money(r['annual'])}/tahun"]  # QA 27/11/2026: nama sekolah jangan terpotong
            if slot == 'b':
                info.insert(0, 'Jurusan dibutuhkan di Australia')
            out.append({"id": f"program:{day.isoformat()}:{slot}", "kind": "promo", "date": day.isoformat(),
                        "title": {"id": head + ' mulai ' + hero + '/' + per}, "caption": cap, "country": r['country'], "provider": r['school'],
                        "spec": {"headline": head.upper(), "hero": hero, "info": info[:3],
                                 "footnote": "*Perkiraan. pricelist.talentededucationgroup.com", "topic": topic_for(field, day, slot, r['country'])},
                        "url": url, "source": None})
    return out
