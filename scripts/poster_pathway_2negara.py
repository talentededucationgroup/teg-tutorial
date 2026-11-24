"""Poster khusus 'Pathway 2 Negara' (pemilik 25/11/2026): kuliah di kampus universitas Australia di Malaysia/Singapura,
opsi pindah ke kampus Australia. Harga = tuition/tahun termurah jenjang Bachelor dari pricelist Talented (R131, 24/11/2026).
Fakta pindah kampus: Monash (monash.edu/admissions/internal-transfer), Curtin (curtin.edu.au/.../campus-transfers),
JCU (jcu.edu.sg inter-campus exchange) - dicek 25/11/2026. Footer standar Talented (QR) seperti poster otomatis."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from poster_mock_unlimited import fontface, b64
from PIL import Image

CAMPUS = [('Swinburne Sarawak', 'Malaysia', 'MYR 34.040'), ('UOW Malaysia', 'Malaysia', 'MYR 31.125'),
          ('Curtin Malaysia', 'Malaysia', 'MYR 51.100'), ('JCU Singapore', 'Singapura', 'SGD 32.373'),
          ('Monash Malaysia', 'Malaysia', 'cek konsultan')]


def html():
    logo = b64(os.path.join(ROOT, 'assets', 'brand', 'logo-talented-putih.png'))
    cards = ''.join(f'<div class="c"><b>{n}</b><span>{k}</span><em>{"mulai " + p + "/thn" if p[0].isupper() and p[:3] in ("MYR", "SGD") else p}</em></div>' for n, k, p in CAMPUS)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fontface()}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:930px;overflow:hidden;font-family:Mont,sans-serif;color:#fff;position:relative;
 background:radial-gradient(80% 60% at 100% 0%,#1f5a4c 0%,transparent 60%),linear-gradient(155deg,#0b2a24,#123f35 55%,#0c2f28)}}
.grid{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1px);background-size:22px 22px;mask:linear-gradient(180deg,#000,transparent 80%)}}
.top{{position:absolute;left:64px;right:64px;top:48px;display:flex;align-items:center;justify-content:space-between}}
.top img{{height:88px}}
.tag{{border:1.5px solid rgba(232,200,119,.75);color:#f3dc9c;border-radius:999px;padding:10px 22px;font-weight:700;font-size:21px;letter-spacing:.12em}}
.eyebrow{{position:absolute;left:64px;top:182px;font-weight:700;letter-spacing:.3em;font-size:26px;color:#e8c877}}
h1{{position:absolute;left:60px;top:220px;font-weight:700;font-size:92px;line-height:1;letter-spacing:-.03em}}
h1 span{{background:linear-gradient(100deg,#f3dc9c,#d9a441);-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:64px;right:64px;top:416px;font-size:29px;font-weight:600;line-height:1.3}}
.sub em{{font-family:Play;font-style:italic;color:#e8c877}}
.route{{position:absolute;left:64px;right:64px;top:510px;display:flex;align-items:center;gap:14px;font-size:25px;font-weight:700}}
.route .s{{background:rgba(255,255,255,.08);border:1px solid rgba(232,200,119,.5);border-radius:14px;padding:12px 18px;text-align:center;line-height:1.2}}
.route .s small{{display:block;font-size:17px;font-weight:500;color:#cfe0da}}
.route i{{font-style:normal;color:#e8c877;font-size:34px}}
.cards{{position:absolute;left:64px;right:64px;top:602px;display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}
.c{{background:#fff;color:#102b40;border-radius:16px;padding:10px 8px;text-align:center;height:100px}}
.c b{{display:block;font-size:18px;line-height:1.15;min-height:42px}}
.c span{{display:none}}
.c em{{display:block;font-style:normal;font-weight:700;font-size:15px;color:#8a6623;margin-top:4px}}
.pts{{position:absolute;left:64px;right:64px;top:748px;display:flex;gap:12px;font-size:20px;font-weight:600}}
.pts div{{flex:1;background:rgba(255,255,255,.08);border-radius:12px;padding:10px 12px}}
.foot{{position:absolute;left:64px;right:64px;top:850px;font-size:16px;line-height:1.35;color:rgba(255,255,255,.66)}}
</style></head><body><div class="grid"></div>
<div class="top"><img src="data:image/png;base64,{logo}"><div class="tag">ALTERNATIF CERDAS</div></div>
<div class="eyebrow">PATHWAY 2 NEGARA</div>
<h1>Mulai dekat,<br><span>lulus Australia</span></h1>
<div class="sub">Kuliah di <em>kampus resmi universitas Australia</em> di Malaysia & Singapura, dengan opsi pindah ke kampus Australia.</div>
<div class="route"><div class="s">🇮🇩 Indonesia<small>daftar lewat Talented</small></div><i>→</i><div class="s">🇲🇾 🇸🇬 Malaysia / Singapura<small>tahun awal, biaya lebih hemat</small></div><i>→</i><div class="s">🇦🇺 Australia<small>opsi pindah kampus*</small></div></div>
<div class="cards">{cards}</div>
<div class="pts"><div>🎓 Kampus resmi universitas Australia</div><div>💰 Tuition jauh di bawah kampus di Australia</div><div>✈️ Dekat dari Indonesia</div></div>
<div class="foot">*Pindah kampus (mis. Monash, Curtin, JCU) lewat seleksi universitas & tetap perlu visa pelajar Australia. Harga = tuition per tahun Bachelor termurah di pricelist Talented; final mengikuti offer letter.</div>
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
    build(os.path.join(ROOT, 'social', 'custom', 'pathway-2-negara.png'))
