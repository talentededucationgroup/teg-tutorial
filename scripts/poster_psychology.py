"""Poster khusus 'Kuliah Psikologi' (pemilik 25/11/2026: banyak siswa mencari). Harga = tuition per tahun dari
pricelist Talented R131 (24/11/2026), Offshore. Footer standar Talented (QR)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from poster_mock_unlimited import fontface, b64
from PIL import Image

COLS = [('Diploma', 'mulai IELTS 5.5', [('CDU Darwin', 'Diploma of Psychology', 'AUD 33.208'), ('Massey Auckland 🇳🇿', 'Diploma in Arts – Psychology', 'NZD 35.250')]),
        ('Bachelor', '3–4 tahun', [('ACU Canberra', 'Psychological Science', 'AUD 32.392'), ('CDU Darwin', 'Psychological Science', 'AUD 33.208'),
                                 ('Western Sydney Uni', 'Psychology (Hons)', 'AUD 37.052')]),
        ('Master', 'lanjut karier', [('Western Sydney Uni', 'Psychotherapy & Counselling', 'AUD 34.776'), ('ACU Canberra', 'Psychology (Clinical)', 'AUD 37.152'),
                                     ('AUT Auckland 🇳🇿', 'MA in Psychology', 'NZD 37.500')])]


def html():
    logo = b64(os.path.join(ROOT, 'assets', 'brand', 'logo-talented-putih.png'))
    cols = ''.join(f'<div class="col"><h3>{t}<small>{s}</small></h3>' + ''.join(f'<div class="r"><b>{n}</b><span>{p}</span><br><em style="margin-left:0">{c}<i>/thn</i></em></div>' for n, p, c in rows) + '</div>' for t, s, rows in COLS)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fontface()}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:930px;overflow:hidden;font-family:Mont,sans-serif;color:#fff;position:relative;
 background:radial-gradient(70% 60% at 100% 0%,#5b3f86 0%,transparent 62%),linear-gradient(155deg,#1d1540,#2a2163 55%,#1a1438)}}
.grid{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1px);background-size:22px 22px;mask:linear-gradient(180deg,#000,transparent 80%)}}
.brain{{position:absolute;right:40px;top:120px;font-size:230px;opacity:.16;filter:grayscale(.2)}}
.top{{position:absolute;left:64px;right:64px;top:48px;display:flex;align-items:center;justify-content:space-between}}
.top img{{height:88px}}
.tag{{border:1.5px solid rgba(232,200,119,.75);color:#f3dc9c;border-radius:999px;padding:10px 22px;font-weight:700;font-size:21px;letter-spacing:.12em}}
.eyebrow{{position:absolute;left:64px;top:182px;font-weight:700;letter-spacing:.3em;font-size:26px;color:#e8c877}}
h1{{position:absolute;left:60px;top:220px;font-weight:700;font-size:84px;line-height:1;letter-spacing:-.03em}}
h1 span{{background:linear-gradient(100deg,#f3dc9c,#d9a441);-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:64px;right:64px;top:388px;font-size:27px;font-weight:600;line-height:1.3}}
.sub em{{font-family:Play;font-style:italic;color:#e8c877}}
.cols{{position:absolute;left:64px;right:64px;top:434px;align-items:start;display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}
.col{{background:#fff;color:#1d1540;border-radius:18px;padding:14px 14px 8px}}
.col h3{{font-size:24px;display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #e8c877;padding-bottom:6px;margin-bottom:4px}}
.col h3 small{{font-size:14px;color:#6b6489;font-weight:600}}
.r{{padding:5px 0;border-bottom:1px solid #ece9f4;line-height:1.25}}
.r:last-child{{border-bottom:0}}
.r b{{display:block;font-size:16px;line-height:1.2}}
.r span{{display:inline;font-size:13.5px;color:#5f5a78;line-height:1.2}}
.r em{{display:inline;font-style:normal;font-weight:700;font-size:15px;color:#8a6623;margin-left:6px}}
.r em i{{font-style:normal;font-weight:500;font-size:12px;color:#8a85a3;margin-left:2px}}
.pts{{position:absolute;left:64px;right:64px;top:752px;display:flex;gap:12px;font-size:20px;font-weight:600}}.pts div{{flex:1;background:rgba(255,255,255,.09);border-radius:12px;padding:10px 12px}}
.foot{{position:absolute;left:64px;right:64px;top:850px;font-size:16px;line-height:1.35;color:rgba(255,255,255,.68)}}
</style></head><body><div class="grid"></div><div class="brain">🧠</div>
<div class="top"><img src="data:image/png;base64,{logo}"><div class="tag">JURUSAN FAVORIT</div></div>
<div class="eyebrow">KULIAH PSIKOLOGI</div>
<h1>Psychology di<br><span>Australia & NZ</span></h1>
<div class="sub">Dari Diploma sampai Master, <em>tuition mulai AUD 32 ribu/tahun</em>.</div>
<div class="cols">{cols}</div>
<div class="pts"><div>🎓 Jalur Diploma → Bachelor</div><div>🗣 Syarat IELTS mulai 5.5</div><div>💼 Bisa lanjut Master</div></div><div class="foot">Tuition per tahun dari pricelist Talented (24 Nov 2026), final mengikuti offer letter. Jadi psikolog terdaftar di Australia perlu jalur studi terakreditasi + praktik terawasi: tanya konsultan Talented.</div>
</body></html>"""


def build(out):
    from playwright.sync_api import sync_playwright
    tmp = out + '.top.png'
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 930}, device_scale_factor=1)
        pg.set_content(html()); pg.wait_for_timeout(500); pg.screenshot(path=tmp); b.close()
    import make_social_cards as m
    canvas = Image.new('RGBA', (1080, 1350), (246, 241, 230, 255))
    canvas.alpha_composite(Image.open(tmp).convert('RGBA'), (0, 0))
    m.watermark(canvas, True)
    canvas.alpha_composite(Image.open(os.path.join(ROOT, 'assets', 'brand', 'footer-terang.png')).convert('RGBA'), (0, m.FOOT_Y))
    canvas.convert('RGB').save(out, optimize=True); os.remove(tmp)
    print(out, 'QR ok' if m.qa_qr(out) else 'QR GAGAL')


if __name__ == '__main__':
    build(os.path.join(ROOT, 'social', 'custom', 'kuliah-psikologi.png'))
