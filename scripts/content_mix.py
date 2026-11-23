"""Variasi konten autopost (pemilik 24/11/2026): "jangan postingan yang sama terus - acak: testimoni, video, materi sekolah,
postingan sosmed kami, info penting terbaru". Satu postingan 'mix:' per hari dengan pilar berganti per hari (urutan
diacak per minggu supaya tidak monoton). Video asli Talented diatur terpisah lewat data/social-video-library.json.

Aturan: hanya fakta yang sudah terverifikasi di data Talented (rules.json, news.json, blog.json, pricelist) atau angka resmi
pemerintah yang dicantumkan sumbernya; testimoni hanya hasil asli siswa VSA tanpa nama/foto/ID; tanpa 'pasti visa'/'dijamin';
tanpa nama master agent/komisi. Foto mengikuti library resmi (brosur sekolah / foto Talented)."""
import datetime, gzip, json, os, random, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://pricelist.talentededucationgroup.com'
INFO = 'https://info.talentededucationgroup.com'
START = datetime.date(2026, 11, 25)
PILLARS = ['info', 'testimoni', 'sekolah', 'tips', 'blog', 'kuis', 'kami']


def load(name, default=None):
    try:
        return json.load(open(os.path.join(ROOT, 'data', name), encoding='utf-8'))
    except Exception:
        return default


def pillar_for(day):
    """urutan 7 pilar diacak tiap minggu (seed = minggu ISO), jadi hari Senin tidak selalu pilar yang sama"""
    y, w, wd = day.isocalendar()
    order = PILLARS[:]
    random.Random(f'mix-{y}-{w}').shuffle(order)
    return order[wd - 1]


# ---------- fakta terverifikasi (sumber resmi dicantumkan) ----------
TIPS = [
    {"head": "BOLEH KERJA SAMBIL KULIAH?", "hero": "48 JAM", "info": ["per 2 minggu saat kuliah berjalan", "Visa pelajar Australia (subclass 500)"],
     "cap": "Pemegang visa pelajar Australia boleh bekerja maksimal 48 jam per dua minggu selama periode kuliah berjalan, dan tanpa batas jam saat libur resmi kampus. Cek kondisi visamu sendiri di VEVO.",
     "src": "https://www.studyaustralia.gov.au/en/plan-your-move/your-guide-to-visas/student-visa-subclass-500.html", "topic": "work"},
    {"head": "BIAYA HIDUP UNTUK VISA AUSTRALIA", "hero": "AUD 29.710", "info": ["per tahun untuk pelajar", "Angka resmi Home Affairs untuk bukti dana"],
     "cap": "Untuk visa pelajar Australia, bukti dana biaya hidup yang diminta pemerintah adalah AUD 29.710 per tahun untuk pelajar (belum termasuk tuition, tiket, dan tanggungan). Di pricelist Talented saran saldo rekening koran sudah dihitung otomatis per program.",
     "src": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/student-500", "topic": "fees"},
    {"head": "SKOR PTE UNTUK VISA PELAJAR", "hero": "PTE 47", "info": ["Minimum visa 500 tanpa ELICOS (tes mulai 7 Agu 2025)", "Syarat kampus bisa lebih tinggi"],
     "cap": "Untuk tes PTE Academic mulai 7 Agustus 2025, skor minimum visa pelajar Australia tanpa ELICOS adalah 47 (39 bila ditambah ELICOS 10 minggu, 31 bila 20 minggu). Ingat: syarat kampus/jurusanmu sering lebih tinggi.",
     "src": "https://immi.homeaffairs.gov.au/help-support/meeting-our-requirements/english-language/student-visa", "topic": "visa"},
    {"head": "ASURANSI WAJIB PELAJAR AUSTRALIA", "hero": "OSHC", "info": ["Wajib selama masa visa pelajar", "Bandingkan 5 provider di pricelist Talented"],
     "cap": "Pelajar internasional di Australia wajib punya Overseas Student Health Cover (OSHC) selama masa visa. Di pricelist Talented kamu bisa membandingkan tarif ahm, Allianz Care, Bupa, Medibank dan nib per bulan.",
     "src": "https://www.privatehealth.gov.au/health_insurance/overseas/overseas_student_health_cover.htm", "topic": "health"},
    {"head": "BUKTI DANA VISA NEW ZEALAND", "hero": "NZD 20.000", "info": ["per tahun biaya hidup", "Atau NZD 1.667 per bulan bila < 1 tahun"],
     "cap": "Untuk visa pelajar New Zealand, bukti dana biaya hidup minimal NZD 20.000 per tahun (atau NZD 1.667 per bulan untuk kursus kurang dari setahun), di luar biaya kuliah dan tiket pulang.",
     "src": "https://www.immigration.govt.nz/new-zealand-visas/visas/visa/student-visa", "topic": "fees"},
    {"head": "CEK SEKOLAHMU TERDAFTAR CRICOS", "hero": "CRICOS", "info": ["Hanya kursus terdaftar CRICOS untuk visa pelajar", "Cek kode di pricelist Talented"],
     "cap": "Visa pelajar Australia hanya untuk kursus yang terdaftar di CRICOS. Sebelum bayar, cek kode CRICOS sekolah & kursusmu. Tab 'Sekolah lain' di pricelist Talented memuat data register CRICOS resmi.",
     "src": "https://cricos.education.gov.au/", "topic": "school"},
]
TESTI = [
    {"hero": "PTE 85", "info": ["Siswa VSA - Overall 85", "Speaking 90 · Listening 80"]},
    {"hero": "PTE 79", "info": ["Siswa VSA - Overall 79", "Speaking 84 · Reading 72"]},
    {"hero": "PTE 64", "info": ["Siswa VSA - Overall 64", "Speaking 67 · Listening 62"]},
]
SCHOOLS = ['massey-university', 'auckland-institute-of-studies', 'nzma', 'witt', 'sit-new-zealand', 'manukau-institute-of-technology',
           'laurus-education-nz', 'aibi-higher-education', 'kaplan-business-school', 'greenwich-college', 'charles-sturt-university',
           'sacred-heart-international-college']


def school_facts(names):
    try:
        raw = urllib.request.urlopen(urllib.request.Request(SITE + '/pricelist-data.json.gz', headers={'User-Agent': 'TalentedAutopost/1.0'}), timeout=60).read()
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
        c = json.loads(raw)['student']['courses']
    except Exception:
        return None
    low = [n.lower() for n in names]
    rows = [r for r in c if any(n in str(r.get('school', '')).lower() for n in low)]
    if not rows:
        return None
    progs = {(r['program'], r.get('city')) for r in rows}
    cities = sorted({r.get('city') for r in rows if r.get('city')})
    cur = 'NZD' if rows[0].get('country') == 'NZ' else 'AUD'
    return {'school': rows[0]['school'].split('\n')[0], 'n': len(progs), 'cities': cities, 'cur': cur,
            'country': rows[0].get('country') or 'AU'}


def build(day, closing):
    p = pillar_for(day)
    orig = p
    k = (day - START).days
    wk = day.isocalendar()[0] * 53 + day.isocalendar()[1]
    lt = closing['lt']
    base = {"kind": "marketing", "date": day.isoformat(), "provider": None, "country": 'AU', "url": SITE + '/', "source": None}
    if p == 'info':
        news = [n for n in (load('news.json', {}) or {}).get('items', [])
                if n.get('date', '') >= (day - datetime.timedelta(days=10)).isoformat() and n.get('date', '') <= day.isoformat()]
        if not news:
            p = 'tips'
        else:
            top = news[:3]
            lines = [f"{i+1}. {n['title']['id']}" for i, n in enumerate(top)]
            off = next((l['url'] for l in top[0].get('links', []) if l.get('official')), None)
            cap = ("📌 Rangkuman info visa & studi terbaru minggu ini, dari sumber resmi pemerintah:\n\n" + '\n'.join(lines) +
                   f"\n\nDetail lengkap & link resmi ada di tab Berita Imigrasi: {SITE}/?tab=news")
            return dict(base, id=f"mix:{day}:info", title={"id": "Info penting minggu ini"}, caption=cap, url=SITE + '/?tab=news', source=off,
                        country=top[0].get('country') or 'ANY',
                        spec={"headline": "INFO PENTING MINGGU INI", "hero": f"{len(top)} UPDATE", "info": [n['title']['id'][:46] for n in top[:2]],
                              "topic": top[0].get('category') or 'visa', "footnote": "Sumber resmi pemerintah · tab Berita Imigrasi"})
    if p == 'testimoni':
        t = TESTI[wk % len(TESTI)]
        cap = (f"🎉 Hasil asli Siswa VSA: {t['info'][0].split(' - ')[1]} di PTE Academic ({t['info'][1]}).\n\n"
               "Persiapan di Victory Scholars Academy (bagian dari Talented): kelas IELTS/PTE di Pontianak, Singkawang & online, plus mock test gratis. "
               "Hasil tiap siswa berbeda, tergantung kemampuan awal dan latihan.\n\n"
               f"Coba free mock test: {SITE}/?lang=id#mocktest")
        return dict(base, id=f"mix:{day}:testi", title={"id": "Hasil asli siswa VSA"}, caption=cap, url=SITE + '/?lang=id#mocktest', provider='Talented Umum',
                    spec={"headline": "HASIL ASLI SISWA VSA", "hero": t['hero'], "info": t['info'],
                          "logo": "assets/badges/victory-scholars-academy-logo.png", "topic": "school",
                          "footnote": "Hasil tiap siswa berbeda"})
    if p == 'sekolah':
        lib = (json.load(open(os.path.join(ROOT, 'social', 'library', 'providers.json'))) or {}).get('providers', {})
        keys = [s for s in SCHOOLS if s in lib]
        if keys:
            key = keys[wk % len(keys)]
            names = lib[key]['names']
            f = school_facts(names)
            if f:
                city = ', '.join(f['cities'][:3])
                cap = (f"🏫 Kenalan dengan {f['school']}: {f['n']} program di pricelist Talented ({city}).\n\n"
                       "Cek biaya per periode, dana awal, total biaya studi dan saran saldo rekening koran untuk visa, gratis di pricelist Talented. "
                       "Foto dari brosur resmi sekolah.\n\n" f"Lihat programnya: {SITE}/?tab=programs&q=" + urllib.request.quote(names[0]))
                return dict(base, id=f"mix:{day}:school:{key}", title={"id": f"Kenalan dengan {f['school']}"}, caption=cap,
                            provider=names[0], country=f['country'], url=SITE + '/?tab=programs&q=' + urllib.request.quote(names[0]),
                            spec={"headline": "KENALAN DENGAN SEKOLAH INI", "hero": f"{f['n']} PROGRAM", "info": [f['school'][:44], city[:44]],
                                  "footnote": "Harga perkiraan; final mengikuti offer letter resmi sekolah"})
        p = 'tips'
    if p == 'blog':
        posts = (load('blog.json', {}) or {}).get('posts', [])
        if posts:
            b = posts[wk % len(posts)]
            url = f"{INFO}/blog/{b['slug']}/"
            cap = f"📝 Dari blog Talented: {b['title']['id']}\n\n{b.get('description', {}).get('id', '')}\n\nBaca lengkap: {url}"
            return dict(base, id=f"mix:{day}:blog:{b['slug'][:40]}", title={"id": b['title']['id'][:90]}, caption=cap, url=url,
                        spec={"headline": "BACA DI BLOG TALENTED", "hero": "ARTIKEL", "info": [b['title']['id'][:46], "info.talentededucationgroup.com/blog"],
                              "topic": "visa", "footnote": "Ditulis dari sumber resmi"})
        p = 'tips'
    if p == 'kami':
        cap = ("📲 Semua info Talented di satu tempat: cek biaya kuliah 1 menit di pricelist (bisa dipasang jadi app gratis), beasiswa aktif, berita visa resmi, "
               "lowongan & akomodasi pelajar, sampai free mock test IELTS/PTE.\n\n"
               f"Simpan link ini & bagikan ke teman yang mau kuliah ke luar negeri: {SITE}/")
        return dict(base, id=f"mix:{day}:kami", title={"id": "Semua info Talented di satu tempat"}, caption=cap, country='ANY', provider='Talented Umum',
                    spec={"headline": "SEMUA INFO STUDI DI SATU APP", "hero": "GRATIS", "info": ["Biaya · Beasiswa · Visa · Mock test", "pricelist.talentededucationgroup.com"],
                          "topic": "school", "footnote": "Talented Education Group · konsultasi gratis"})
    tip = TIPS[(wk + PILLARS.index(orig)) % len(TIPS)]
    if p == 'kuis':
        opts = {'48 JAM': ['24 jam', '48 jam', 'tanpa batas'], 'AUD 29.710': ['AUD 21.041', 'AUD 29.710', 'AUD 35.000'],
                'PTE 47': ['PTE 42', 'PTE 47', 'PTE 58'], 'NZD 20.000': ['NZD 15.000', 'NZD 20.000', 'NZD 25.000']}.get(tip['hero'])
        if opts:
            q = tip['head'].rstrip('?').title() + '?'
            cap = (f"🤔 Kuis: {q}\nA) {opts[0]}  B) {opts[1]}  C) {opts[2]}\n\nTulis jawabanmu di komentar!\n\n"
                   f"Jawaban: B) {opts[1]}. {tip['cap']}")
            return dict(base, id=f"mix:{day}:kuis", title={"id": "Kuis: " + q}, caption=cap, source=tip['src'],
                        country='NZ' if 'NZD' in tip['hero'] else 'AU',
                        spec={"headline": "KUIS: " + tip['head'][:34], "hero": "A · B · C?", "info": [f"A) {opts[0]}", f"B) {opts[1]}   C) {opts[2]}"],
                              "topic": tip['topic'], "footnote": "Jawaban ada di caption"})
    cap = f"💡 {tip['cap']}"
    return dict(base, id=f"mix:{day}:tips", title={"id": tip['head'].title()}, caption=cap, source=tip['src'],
                country='NZ' if 'NZD' in tip['hero'] else 'AU',
                spec={"headline": tip['head'], "hero": tip['hero'], "info": tip['info'], "topic": tip['topic'],
                      "footnote": "Sumber resmi pemerintah · cek ulang sebelum apply"})


def posts(now, closing, back_days=3):
    out = []
    for back in range(back_days):
        day = now.date() - datetime.timedelta(days=back)
        if day < START:
            continue
        try:
            e = build(day, closing)
        except Exception as ex:
            print('mix skipped', day, str(ex)[:120]); continue
        if e:
            e['caption'] = e['caption'] + f"\n\nKonsultasi gratis: {closing['lt']}\nScan QR di gambar atau klik link di bio.\n\n" + closing['text'] + \
                "\n\n#KuliahDiAustralia #StudyAbroad #TalentedEducation"
            out.append(e)
    return out


if __name__ == '__main__':
    now = datetime.datetime(2026, 11, 25, 9)
    for i in range(14):
        d = START + datetime.timedelta(days=i)
        e = build(d, {'lt': 'L', 'text': 'T'})
        print(d, pillar_for(d), e['id'], '|', e['spec']['headline'], '|', e['spec']['hero'])
