"""Postingan kepercayaan Talented (pemilik 23/11/2026): tunjukkan bahwa Talented agen lengkap, terpercaya & bereputasi,
# 27/11/2026: maks 3 hashtag per caption (pemilik).
dengan fokus sekolah Australia & New Zealand. Satu postingan tiap 3 hari, tema bergilir.
Hanya fakta yang tercatat di data publik Talented (data/badges.json, alamat kantor di situs, jumlah program di pricelist);
tanpa klaim 'pasti visa', tanpa persentase keberhasilan, tanpa nama master agent/komisi."""
import datetime, gzip, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = 'https://pricelist.talentededucationgroup.com/pricelist-data.json.gz'
SITE = 'https://pricelist.talentededucationgroup.com'
START = datetime.date(2026, 11, 24)
EVERY = 3


def counts():
    """jumlah sekolah & program Australia/New Zealand di pricelist publik (fallback angka di situs)"""
    try:
        raw = urllib.request.urlopen(urllib.request.Request(SRC, headers={'User-Agent': 'TalentedAutopost/1.0'}), timeout=60).read()
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
        c = json.loads(raw)['student']['courses']
        au = [r for r in c if r.get('country') == 'AU']
        nz = [r for r in c if r.get('country') == 'NZ']
        # program unik (sekolah + program + kota), offshore & onshore dihitung sekali
        prog = {(r['school'], r['program'], r.get('city')) for r in au + nz}
        return {'au_s': len({r['school'] for r in au}), 'nz_s': len({r['school'] for r in nz}), 'prog': len(prog)}
    except Exception:
        return None


def themes(n):
    hub = f"{n['au_s'] + n['nz_s']}+" if n else '160+'
    prog = f"{n['prog']:,}".replace(',', '.') + '+' if n else '4.100+'
    return [
        {"head": "KONSELOR TERSERTIFIKASI PIER", "hero": "QEAC #10224", "logo": "assets/badges/qeac-10224.png",
         "info": ["Qualified Education Agent Counsellor", "Kuliah di Australia & New Zealand"],
         "cap": "✅ Konselor Talented tersertifikasi PIER Qualified Education Agent Counsellor (QEAC) #10224.\n\n"
                "Artinya konselor kami sudah lulus pelatihan & ujian tentang aturan pendidikan internasional dan visa pelajar Australia, "
                "dan wajib mengikuti pelatihan lanjutan tiap tahun. Kamu bisa cek nomor QEAC di direktori resmi PIER."},
        {"head": "AGEN TERVERIFIKASI", "hero": "PIER VERIFIED", "logo": "assets/badges/pier-verified-agency.png",
         "info": ["PIER Verified Agency", "Agen pendidikan Australia & New Zealand"],
         "cap": "🛡 Talented Education Group adalah PIER Verified Agency.\n\n"
                "Pilih agen yang identitas & kualifikasinya bisa dicek, bukan sekadar akun media sosial. Kami bantu dari pilih jurusan, "
                "daftar sekolah, sampai persiapan dokumen visa pelajar Australia & New Zealand."},
        {"head": "PAHAM ATURAN PERLINDUNGAN PELAJAR", "hero": "ESOS ACT", "logo": "assets/badges/agent-academy-esos.png",
         "info": ["ESOS Act & National Code (Agent Academy)", "Hak pelajar internasional di Australia"],
         "cap": "📘 Tim Talented menyelesaikan pelatihan ESOS Act & National Code (Agent Academy).\n\n"
                "ESOS adalah aturan resmi Australia yang melindungi pelajar internasional: hak refund, informasi kursus yang jujur, "
                "dan perlindungan bila sekolah tutup. Kami jelaskan hak-hakmu sebelum kamu tanda tangan offer letter."},
        {"head": "PARTNER RESMI PEARSON PTE", "hero": "PTE ELITE 2026", "logo": "assets/badges/pearson-pte-partner-2026.png",
         "info": ["Pearson PTE Elite Partner Program 2026", "Persiapan PTE untuk visa AU & NZ"],
         "cap": "🎯 Talented adalah partner Pearson PTE Elite Partner Program 2026.\n\n"
                "Skor PTE dipakai untuk visa pelajar Australia & New Zealand. Lewat Victory Scholars Academy (bagian dari Talented) "
                "kamu bisa ikut kelas & mock test PTE/IELTS gratis sebelum tes resmi."},
        {"head": "KANTOR DI AUSTRALIA & INDONESIA", "hero": "SYDNEY + KALBAR", "logo": None,
         "info": ["Sydney · Pontianak · Singkawang", "Tim di Indonesia & di Australia"],
         "cap": "📍 Talented punya kantor di Sydney (Level 21, 133 Castlereagh Street) dan di Kalimantan Barat (Pontianak & Singkawang).\n\n"
                "Konsultasi tatap muka di Indonesia, dan ada tim di Australia saat kamu sudah tiba. Konsultasi gratis."},
        {"head": f"{hub} SEKOLAH AUSTRALIA & NEW ZEALAND", "hero": f"{prog} PROGRAM", "logo": None,
         "info": ["Harga transparan, cek sendiri gratis", "Dana awal, total biaya & rekening koran"],
         "cap": f"📊 Pricelist Talented memuat {prog} program di {hub} sekolah & kampus Australia dan New Zealand.\n\n"
                f"Cek sendiri dana awal, total biaya studi, dan saran saldo rekening koran untuk visa, gratis: {SITE}\n"
                "Semua angka perkiraan; biaya final mengikuti offer letter resmi sekolah."},
        {"head": "PERSIAPAN BAHASA INGGRIS GRATIS", "hero": "MOCK TEST", "logo": "assets/badges/victory-scholars-academy-logo.png",
         "info": ["Victory Scholars Academy", "Mock test IELTS & PTE gratis"],
         "cap": "📝 Belum punya skor IELTS/PTE untuk kuliah di Australia atau New Zealand?\n\n"
                "Victory Scholars Academy (bagian dari Talented) menyediakan mock test IELTS & PTE gratis dengan penilaian otomatis, "
                "plus kelas persiapan di Pontianak, Singkawang & online."},
    ]


def posts(now, closing, back_days=3):
    out, n = [], None
    for back in range(back_days):
        day = now.date() - datetime.timedelta(days=back)
        k = (day - START).days
        if k < 0 or k % EVERY:
            continue
        if n is None:
            n = counts() or {}
        th = themes(n or None)
        t = th[(k // EVERY) % len(th)]
        cap = (t['cap'] + f"\n\nKonsultasi gratis: {closing['lt']}\nScan QR di gambar atau klik link di bio.\n\n" + closing['text']
               + "\n\n#KuliahDiAustralia #KuliahDiNewZealand #TalentedEducation")
        spec = {"headline": t['head'], "hero": t['hero'], "info": t['info'], "topic": "school",
                "footnote": "Talented Education Group · konsultasi gratis"}
        if t['logo'] and os.path.exists(os.path.join(ROOT, t['logo'])):
            spec['logo'] = t['logo']
        out.append({"id": f"trust:{day.isoformat()}", "kind": "promo", "date": day.isoformat(),
                    "title": {"id": t['head'].title() + ' - Talented Education Group'}, "caption": cap, "country": 'AU',
                    "provider": None, "spec": spec, "url": SITE, "source": None})
    return out
