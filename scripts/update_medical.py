#!/usr/bin/env python3
"""Cek otomatis bulanan data/medical.json (tab Medical & Biometrik website TEG).
- UK: baca tanggal 'public_updated_at' daftar klinik TB Indonesia di gov.uk (content API). Bila berubah dari yang tercatat,
  status klinik UK diturunkan ke 'to_confirm' (website menampilkan "cek ulang di daftar resmi") dan dicatat di medical-changes.json
  supaya sesi Claude bulanan memperbarui daftarnya.
- Semua URL resmi dicek (HTTP). Gagal = dicatat, data TIDAK diubah, tanggal 'updated' tidak dimajukan.
Tidak menyimpan data pribadi; hanya data publik klinik/kantor resmi."""
import json, datetime, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT/'data/medical.json'; C = ROOT/'data/medical-changes.json'
UK_API = 'https://www.gov.uk/api/content/government/publications/indonesia-tuberculosis-test-clinics-for-a-uk-visa/tuberculosis-testing-in-indonesia'
UA = {'User-Agent': 'Mozilla/5.0 (TEG data check; +https://info.talentededucationgroup.com)'}
def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, r.read()
d = json.loads(F.read_text()); today = datetime.date.today().isoformat(); log = {'run': today, 'changes': [], 'failed': []}
try:
    st, body = get(UK_API); uk = json.loads(body).get('public_updated_at', '')[:10]
    old = d.get('uk_list_updated')
    if old and uk and uk != old:
        for k in d['clinics']:
            if k.get('status', {}).get('GB') == 'official': k['status']['GB'] = 'to_confirm'
        log['changes'].append(f'Daftar klinik TB UK di gov.uk diperbarui {old} -> {uk}: status UK sementara "cek ulang" sampai daftar diperbarui')
    if uk: d['uk_list_updated'] = uk
except Exception as e:
    log['failed'].append(f'gov.uk API: {e}')
urls = set()
for c in d['countries']:
    urls |= {c.get('medical_official'), c.get('bio_official')} | {x.get('url') for x in c.get('centres', [])}
urls |= {k.get('web') for k in d['clinics']}
for u in sorted(x for x in urls if x):
    try:
        st, _ = get(u, 20)
        if st >= 400: log['failed'].append(f'{u} HTTP {st}')
    except Exception as e:
        log['failed'].append(f'{u}: {str(e)[:80]}')
if not [x for x in log['failed'] if x.startswith('gov.uk')]: d['updated'] = today
F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
hist = json.loads(C.read_text()) if C.exists() else []
hist = [log] + hist[:23]; C.write_text(json.dumps(hist, ensure_ascii=False, indent=1) + '\n')
print(json.dumps(log, ensure_ascii=False, indent=1))
