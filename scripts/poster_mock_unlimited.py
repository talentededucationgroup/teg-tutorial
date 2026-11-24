"""Poster khusus 'Free Mock Test UNLIMITED' (pemilik 25/11/2026).
Bagian atas dirender dari HTML/CSS (Playwright), bawah = footer standar Talented (QR linktree, Victory, badge, sosmed)
supaya lolos QA QR & seragam dengan poster otomatis lain. Hasil: social/custom/free-mock-test-unlimited.png
"""
import os, sys, base64
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from PIL import Image
FONTS = '/home/claude/teg-internal/assets/fonts'


def b64(p):
    return base64.b64encode(open(p, 'rb').read()).decode()


def fontface():
    out = []
    for fam, f, w in [('Mont', 'montserrat-latin-500-normal', 500), ('Mont', 'montserrat-latin-600-normal', 600), ('Mont', 'montserrat-latin-700-normal', 700),
                      ('Play', 'playfair-display-latin-700-italic', 700)]:
        p = os.path.join(FONTS, f + '.woff2')
        if os.path.exists(p):
            out.append(f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b64(p)}) format('woff2');font-weight:{w}{';font-style:italic' if 'italic' in f else ''}}}")
    return '\n'.join(out)


TESTS = [('IELTS', 'Academic'), ('PTE', 'Academic'), ('JLPT', 'N5 – N1'), ('TOPIK', 'Korea'), ('HSK', 'Mandarin')]


def html():
    logo = b64(os.path.join(ROOT, 'assets', 'brand', 'logo-talented-putih.png'))
    chips = ''.join(f'<div class="chip"><b>{a}</b><span>{b}</span></div>' for a, b in TESTS)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fontface()}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:930px;overflow:hidden;font-family:Mont,sans-serif;color:#fff;position:relative;
 background:radial-gradient(90% 70% at 85% 0%,#1f4d6e 0%,transparent 60%),radial-gradient(70% 60% at 0% 100%,#0d2a3f 0%,transparent 70%),linear-gradient(160deg,#0b1f30,#102b40 55%,#0e2638)}}
.inf{{position:absolute;right:-90px;top:120px;font:700 560px/1 Mont;color:transparent;-webkit-text-stroke:3px rgba(232,200,119,.18);letter-spacing:-20px}}
.grid{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1px);background-size:22px 22px;mask:linear-gradient(180deg,#000,transparent 75%)}}
.top{{position:absolute;left:64px;right:64px;top:52px;display:flex;align-items:center;justify-content:space-between}}
.top img{{height:92px}}
.badge{{border:1.5px solid rgba(232,200,119,.7);color:#f3dc9c;border-radius:999px;padding:10px 22px;font-weight:700;font-size:22px;letter-spacing:.14em}}
.eyebrow{{position:absolute;left:64px;top:205px;font-weight:700;letter-spacing:.32em;font-size:30px;color:#e8c877}}
h1{{position:absolute;left:58px;top:244px;font-weight:700;font-size:168px;line-height:1;letter-spacing:-.03em;
 background:linear-gradient(100deg,#fff 0%,#fff 55%,#f3dc9c 100%);-webkit-background-clip:text;color:transparent}}
.sub{{position:absolute;left:64px;top:428px;font-size:40px;font-weight:600;line-height:1.25}}
.sub em{{font-family:Play;font-style:italic;color:#e8c877;font-weight:700}}
.chips{{position:absolute;left:64px;right:64px;top:540px;display:grid;grid-template-columns:repeat(5,1fr);gap:14px}}
.chip{{background:rgba(255,255,255,.07);border:1px solid rgba(232,200,119,.45);border-radius:20px;padding:18px 10px 16px;text-align:center}}
.chip b{{display:block;font-size:36px;letter-spacing:.02em}}
.chip span{{display:block;margin-top:6px;font-size:19px;font-weight:500;color:#cfd9e2}}
.cta{{position:absolute;left:64px;top:752px;display:flex;align-items:center;gap:18px}}
.pill{{background:linear-gradient(135deg,#f3dc9c,#d9a441);color:#102b40;border-radius:999px;padding:18px 30px;font-weight:700;font-size:30px}}
.url{{font-size:25px;font-weight:600;color:#fff}}
.url small{{display:block;font-size:20px;font-weight:500;color:#cfd9e2;margin-top:4px}}
.foot{{position:absolute;left:64px;right:64px;top:872px;font-size:18px;color:rgba(255,255,255,.62)}}
</style></head><body><div class="grid"></div><div class="inf">∞</div>
<div class="top"><img src="data:image/png;base64,{logo}"><div class="badge">100% GRATIS</div></div>
<div class="eyebrow">FREE MOCK TEST</div>
<h1>UNLIMITED</h1>
<div class="sub">Ulangi tes <em>sepuasnya</em>, tanpa batas.<br>Tanpa daftar akun, tanpa biaya.</div>
<div class="chips">{chips}</div>
<div class="cta"><div class="pill">Mulai latihan sekarang →</div><div class="url">pricelist.talentededucationgroup.com<small>Menu “Free Mock Test” · HP & laptop</small></div></div>
<div class="foot">*Soal latihan buatan Talented sesuai format ujian, bukan soal resmi. Skor latihan = perkiraan.</div>
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
    build(os.path.join(ROOT, 'social', 'custom', 'free-mock-test-unlimited.png'))
