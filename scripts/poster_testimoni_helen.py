"""Poster testimoni Helen Anggraeni (ulasan Google 5 bintang, Nov 2026; nama & foto dipakai dengan persetujuan siswa,
dikonfirmasi pemilik 25/11/2026; wajah tetap tertutup seperti unggahan aslinya).
Output: social/custom/testimoni-helen.png (feed 1080x1350, footer standar) + testimoni-helen-720.jpg (galeri testimoni website)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from poster_mock_unlimited import fontface, b64
from PIL import Image

PHOTO = os.path.join(ROOT, 'social', 'custom', 'src', 'helen-sydney.jpg')
QUOTE = ("This is my second time using this agency, and once again, they’ve exceeded my expectations! "
         "They are incredibly responsible, reliable, and professional. Their responses are super quick and communication is excellent. "
         "Definitely an agency you can trust! Highly, highly recommended!")


def html(w, h, small=False):
    logo = b64(os.path.join(ROOT, 'assets', 'brand', 'logo-talented-putih.png'))
    ph = b64(PHOTO)
    if small:
        return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fontface()}
*{{box-sizing:border-box;margin:0;padding:0}}body{{width:{w}px;height:{h}px;overflow:hidden;font-family:Mont,sans-serif;background:#102b40;color:#fff;display:flex}}
.ph{{width:300px;height:100%;background:url(data:image/jpeg;base64,{ph}) center 45%/cover}}
.tx{{flex:1;padding:34px 30px;display:flex;flex-direction:column;gap:14px;background:linear-gradient(160deg,#102b40,#0b1f30)}}
.st{{color:#e8c877;font-size:28px;letter-spacing:4px}}h2{{font:700 34px/1 Mont;letter-spacing:.06em}}
.q{{font:700 italic 21px/1.4 Play;color:#f6efe0}}.q::before{{content:'“';display:block;font:700 70px/.5 Play;color:#e8c877;margin:10px 0 8px}}
.n{{margin-top:auto;font-weight:700;font-size:22px;color:#f3dc9c}}.n small{{display:block;font-weight:500;font-size:15px;color:#cfd9e2;margin-top:4px}}
img.l{{position:absolute;right:24px;bottom:22px;height:58px}}</style></head><body><div class="ph"></div><div class="tx"><div class="st">★★★★★</div><h2>TESTIMONY</h2>
<div class="q">{QUOTE}</div><div class="n">— Helen Anggraeni<small>Ulasan Google · Sydney, Australia</small></div></div><img class="l" src="data:image/png;base64,{logo}"></body></html>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fontface()}
*{{box-sizing:border-box;margin:0;padding:0}}body{{width:{w}px;height:{h}px;overflow:hidden;font-family:Mont,sans-serif;color:#fff;position:relative;background:#0b1f30}}
.ph{{position:absolute;left:0;top:0;width:470px;height:100%;background:url(data:image/jpeg;base64,{ph}) 32% 40%/cover}}
.ph::after{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent 70%,#0b1f30)}}
.tx{{position:absolute;left:500px;right:56px;top:46px;bottom:30px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}.top img{{height:74px}}
.tag{{border:1.5px solid rgba(232,200,119,.75);color:#f3dc9c;border-radius:999px;padding:8px 16px;font-weight:700;font-size:16px;letter-spacing:.12em}}
.st{{margin-top:34px;color:#e8c877;font-size:40px;letter-spacing:6px}}
h1{{font-weight:700;font-size:54px;line-height:1.05;margin-top:8px}}h1 span{{background:linear-gradient(100deg,#f3dc9c,#d9a441);-webkit-background-clip:text;color:transparent}}
.q{{margin-top:22px;font:700 italic 25px/1.42 Play;color:#f6efe0}}.q::before{{content:'“';display:block;font:700 90px/.5 Play;color:#e8c877;margin:16px 0 10px}}
.n{{margin-top:auto;padding-bottom:70px;font-weight:700;font-size:26px;color:#f3dc9c}}.n small{{display:block;font-weight:500;font-size:18px;color:#cfd9e2;margin-top:6px}}
.g{{position:absolute;left:24px;bottom:26px;background:rgba(255,255,255,.92);color:#102b40;border-radius:999px;padding:10px 18px;font-weight:700;font-size:18px}}
</style></head><body><div class="ph"></div><div class="g">★ 5.0 · Ulasan Google</div><div class="tx"><div class="top"><img src="data:image/png;base64,{logo}"><div class="tag">CERITA SISWA</div></div>
<div class="st">★★★★★</div><h1>Kedua kalinya,<br><span>tetap puas!</span></h1><div class="q">{QUOTE}</div>
<div class="n">— Helen Anggraeni<small>Siswa Talented di Sydney, Australia</small></div></div></body></html>"""


def shot(doc, w, h, path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg.set_content(doc); pg.wait_for_timeout(500); pg.screenshot(path=path); b.close()


def build():
    out = os.path.join(ROOT, 'social', 'custom', 'testimoni-helen.png')
    tmp = out + '.top.png'
    shot(html(1080, 930), 1080, 930, tmp)
    import make_social_cards as m
    canvas = Image.new('RGBA', (1080, 1350), (246, 241, 230, 255))
    canvas.alpha_composite(Image.open(tmp).convert('RGBA'), (0, 0))
    m.watermark(canvas, True)
    canvas.alpha_composite(Image.open(os.path.join(ROOT, 'assets', 'brand', 'footer-terang.png')).convert('RGBA'), (0, m.FOOT_Y))
    canvas.convert('RGB').save(out, optimize=True); os.remove(tmp)
    print(out, 'QR ok' if m.qa_qr(out) else 'QR GAGAL')
    small = os.path.join(ROOT, 'social', 'custom', 'testimoni-helen-720.png')
    shot(html(720, 720, True), 720, 720, small)
    Image.open(small).convert('RGB').save(small[:-4] + '.jpg', quality=88); os.remove(small)
    print(small[:-4] + '.jpg')


if __name__ == '__main__':
    build()
