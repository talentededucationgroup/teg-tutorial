#!/usr/bin/env python3
"""Talented social poster generator (1080x1350, feed 4:5) following social/PANDUAN-desain-caption.txt
(layout A/B/C/D, palettes P1-P6, flat design, Anton + Montserrat, original Talented logo, footer 03/04,
banner 08 above the footer, QR decode check, LOG rotation). Everything is drawn with PIL, no AI images.

make_card(kind, title, key, sub=None, country=None, provider=None, spec=None) -> public URL or None (QA failed)
spec (optional, from data/social-posts.json): {headline, hero, price, unit, info:[...], footnote}"""
import os, re, sys, json, math, random, hashlib, datetime, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'social', 'cards')
BASE = 'https://info.talentededucationgroup.com/social/cards/'
LOG = os.path.join(ROOT, 'data', 'social-log.json')
BR = lambda f: os.path.join(ROOT, 'assets', 'brand', f)
W, H, STAGE, FOOT_Y, M = 1080, 1350, 720, 930, 56
QR_URL = 'https://linktr.ee/talentededucationgroup'
PAL = {  # bg, text, accent, dark?
    'P1': ((0x17, 0x3F, 0x35), (255, 255, 255), (0xE9, 0xC4, 0x6A), True),
    'P2': ((0xF6, 0xF1, 0xE6), (0x17, 0x3F, 0x35), (0xC8, 0x90, 0x1A), False),
    'P3': ((0x1E, 0x1E, 0x24), (255, 255, 255), (0xE9, 0xC4, 0x6A), True),
    'P4': ((0xFF, 0xFF, 0xFF), (0x17, 0x3F, 0x35), (0xC8, 0x90, 0x1A), False),
    'P5': ((0xEE, 0xF3, 0xEC), (0x17, 0x3F, 0x35), (0xC8, 0x90, 0x1A), False),
    'P6': ((0x17, 0x3F, 0x35), (255, 255, 255), (0xE9, 0xC4, 0x6A), True),
    # pemilik 23/11/2026: warna berubah-ubah tiap posting. Palet tambahan (flat, kontras tinggi; logo & footer Talented tetap).
    'N1': ((0x14, 0x2B, 0x4C), (255, 255, 255), (0xFF, 0x7A, 0x59), True),   # navy + coral
    'N2': ((0xB8, 0x4A, 0x2C), (255, 255, 255), (0xFF, 0xD5, 0x80), True),   # terracotta + kuning lembut
    'N3': ((0x0B, 0x5F, 0x66), (255, 255, 255), (0xFF, 0xC8, 0x57), True),   # ocean teal + mustard
    'N4': ((0xE6, 0xF1, 0xFB), (0x12, 0x2E, 0x55), (0xF2, 0x6B, 0x3A), False),  # biru langit + oranye
    'N5': ((0xEE, 0xE8, 0xFB), (0x2D, 0x1B, 0x5E), (0xE8, 0x5D, 0x75), False),  # lavender + pink
    'N6': ((0x3B, 0x1F, 0x4F), (255, 255, 255), (0xFF, 0xB4, 0x4C), True),   # plum + oranye
    'N7': ((0xB3, 0x1B, 0x2B), (255, 255, 255), (0xFF, 0xE0, 0x66), True),   # merah promo + kuning
    'N8': ((0xE3, 0xF6, 0xEE), (0x0F, 0x4C, 0x3A), (0xFF, 0x7F, 0x3A), False),  # mint + oranye
    'N9': ((0x1C, 0x1F, 0x24), (255, 255, 255), (0xC6, 0xF2, 0x4E), True),   # charcoal + lime
    'N10': ((0xFF, 0xEE, 0xE2), (0x5A, 0x23, 0x10), (0xD9, 0x48, 0x34), False),  # peach + merah bata
    'N11': ((0x1B, 0x3A, 0x8C), (255, 255, 255), (0x7F, 0xE0, 0xD4), True),  # royal blue + tosca
    'N12': ((0xFF, 0xF6, 0xD6), (0x23, 0x2A, 0x5C), (0x2F, 0x6B, 0xFF), False),  # krem kuning + biru
}
# tinta per palet: warna gelap untuk panel & teks di atas warna aksen (dulu selalu hijau Talented)
INKS = {'N1': ((0x14, 0x2B, 0x4C), (0x22, 0x40, 0x6B)), 'N2': ((0x4A, 0x1E, 0x10), (0x93, 0x38, 0x20)),
        'N3': ((0x06, 0x3A, 0x3F), (0x13, 0x7A, 0x82)), 'N4': ((0x12, 0x2E, 0x55), (0x1F, 0x46, 0x7D)),
        'N5': ((0x2D, 0x1B, 0x5E), (0x45, 0x2F, 0x82)), 'N6': ((0x24, 0x12, 0x33), (0x55, 0x30, 0x70)),
        'N7': ((0x5A, 0x0A, 0x12), (0x8C, 0x14, 0x22)), 'N8': ((0x0F, 0x4C, 0x3A), (0x1B, 0x6B, 0x53)),
        'N9': ((0x1C, 0x1F, 0x24), (0x33, 0x38, 0x40)), 'N10': ((0x5A, 0x23, 0x10), (0x80, 0x36, 0x1E)),
        'N11': ((0x10, 0x24, 0x5C), (0x2B, 0x4F, 0xB0)), 'N12': ((0x23, 0x2A, 0x5C), (0x33, 0x3D, 0x80))}
BRAND_PALS = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')
GREEN, PANEL2 = (0x17, 0x3F, 0x35), (0x21, 0x58, 0x4A)
ACC = (0xE9, 0xC4, 0x6A)


PAL_BG = [(0x17, 0x3F, 0x35)]


def set_palette(pal):
    """warna tinta/panel/aksen global mengikuti palet yang dipilih (dipakai semua layout, story & reel)"""
    global GREEN, PANEL2, ACC
    PAL_BG[0] = PAL.get(pal, PAL['P1'])[0]
    GREEN, PANEL2 = INKS.get(pal, ((0x17, 0x3F, 0x35), (0x21, 0x58, 0x4A)))
    ACC = PAL.get(pal, PAL['P1'])[2]


DECOS = ['none', 'dots', 'rings', 'stripes', 'blob', 'grid', 'plus', 'arc']
CTAS = ['app', 'app', 'pill', 'split', 'ticket', 'sticker']
FONTS = ['anton', 'anton', 'mont', 'poppins']


def set_style(key):
    """font judul, ornamen latar & gaya ajakan (CTA) diacak per posting; tidak mengulang kombinasi posting sebelumnya"""
    rnd = random.Random('style' + key)
    try:
        prev = json.load(open(LOG, encoding='utf-8'))['items'][-3:]
    except Exception:
        prev = []
    def pick(opts, k):
        last = [i.get(k) for i in prev]
        pool = [o for o in opts if o not in last[-2:]] or opts
        return rnd.choice(pool)
    STYLE.update(font=pick(FONTS, 'font'), deco=pick(DECOS, 'deco'), cta=pick(CTAS, 'cta'))
    return dict(STYLE)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def base_canvas(bg):
    """kanvas warna + ornamen latar (di belakang foto & teks)"""
    im = Image.new('RGBA', (W, H), bg + (255,))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    dark = sum(bg) < 380
    soft = _mix(bg, (255, 255, 255) if dark else GREEN, 0.10) + (255,)
    acc = ACC + (110,)
    k = STYLE.get('deco', 'none')
    if k == 'dots':
        for yy in range(40, 400, 34):
            for xx in range(W - 380, W - 30, 34):
                d.ellipse([xx, yy, xx + 9, yy + 9], fill=acc)
    elif k == 'rings':
        for r in (300, 230, 160):
            d.ellipse([-r + 40, 720 - r, r + 40, 720 + r], outline=acc, width=10)
    elif k == 'stripes':
        for i in range(0, 900, 46):
            d.polygon([(W - 520 + i, 0), (W - 500 + i, 0), (W - 900 + i, 400), (W - 920 + i, 400)], fill=ACC + (70,))
    elif k == 'blob':
        d.ellipse([W - 520, 360, W + 260, 1140], fill=soft)
        d.ellipse([-180, -220, 300, 260], fill=soft)
    elif k == 'grid':
        for xx in range(0, W, 54):
            d.line([(xx, 0), (xx, 930)], fill=soft[:3] + (140,), width=2)
        for yy in range(0, 930, 54):
            d.line([(0, yy), (W, yy)], fill=soft[:3] + (140,), width=2)
    elif k == 'plus':
        r = random.Random(str(bg))
        for _ in range(16):
            x, y = r.randint(40, W - 40), r.randint(30, 700)
            d.rectangle([x - 14, y - 3, x + 14, y + 3], fill=acc); d.rectangle([x - 3, y - 14, x + 3, y + 14], fill=acc)
    elif k == 'arc':
        d.pieslice([W - 420, -420, W + 420, 420], 90, 180, fill=soft)
        d.arc([W - 470, -470, W + 470, 470], 90, 180, fill=ACC + (255,), width=12)
    im.alpha_composite(lay)
    return im


def _rr(d, box, r, **kw):
    try:
        d.rounded_rectangle(box, r, **kw)
    except Exception:
        d.rectangle(box, **kw)


def cta_band(canvas, top=740, bottom=916):
    """ajakan di atas footer; variasi gaya (pemilik 23/11/2026: desain jangan mirip semua)"""
    k = STYLE.get('cta', 'app')
    d = ImageDraw.Draw(canvas)
    x0, x1 = (W - 960) // 2, (W + 960) // 2
    if k == 'pill':
        _rr(d, [x0, top + 22, x1, bottom - 10], 72, fill=ACC)
        t1, t2 = 'CEK BIAYA KULIAH DALAM 1 MENIT', 'pricelist.talentededucationgroup.com'
        f1 = fit_font(d, t1, lambda s_: mont(s_, 'ExtraBold'), 860, 44, 24); f2 = mont(28, 'Bold')
        draw_t(d, ((W - tw(d, t1, f1)) // 2, top + 46), t1, f1, GREEN)
        draw_t(d, ((W - tw(d, t2, f2)) // 2, top + 46 + th(d, t1, f1) + 16), t2, f2, GREEN)
    elif k == 'split':
        mid = x0 + 520
        d.rectangle([x0, top + 24, mid, bottom - 8], fill=GREEN)
        d.rectangle([mid, top + 24, x1, bottom - 8], fill=ACC)
        f1 = fit_font(d, 'KONSULTASI GRATIS', anton, 460, 64, 30)
        draw_t(d, (x0 + 30, top + 24 + (152 - th(d, 'KONSULTASI GRATIS', f1)) // 2), 'KONSULTASI GRATIS', f1, (255, 255, 255))
        f2 = mont(30, 'ExtraBold'); f3 = mont(22, 'Bold')
        draw_t(d, (mid + 28, top + 56), 'Scan QR di bawah', f2, GREEN)
        draw_t(d, (mid + 28, top + 104), 'atau klik link di bio', f3, GREEN)
    elif k == 'ticket':
        _rr(d, [x0, top + 22, x1, bottom - 8], 26, fill=(255, 255, 255))
        cut = x1 - 250
        for yy in range(top + 40, bottom - 20, 18):
            d.line([(cut, yy), (cut, yy + 8)], fill=GREEN, width=3)
        f1 = fit_font(d, 'DOWNLOAD APP TALENTED', anton, cut - x0 - 60, 60, 28)
        draw_t(d, (x0 + 34, top + 44), 'DOWNLOAD APP TALENTED', f1, GREEN)
        draw_t(d, (x0 + 34, top + 50 + th(d, 'DOWNLOAD', f1) + 14), 'pricelist.talentededucationgroup.com', mont(26, 'Bold'), _mix(GREEN, (128, 128, 128), 0.3))
        fg = fit_font(d, 'GRATIS', anton, 200, 66, 30)
        _rr(d, [cut + 24, top + 50, x1 - 24, bottom - 34], 18, fill=ACC)
        draw_t(d, (cut + 24 + (x1 - cut - 48 - tw(d, 'GRATIS', fg)) // 2, top + 50 + (bottom - 84 - top - th(d, 'GRATIS', fg)) // 2), 'GRATIS', fg, GREEN)
    elif k == 'sticker':
        f1 = mont(34, 'ExtraBold'); t1 = 'Cek harga kuliah di app Talented'
        draw_t(d, (x0 + 10, top + 52), t1, fit_font(d, t1, lambda s_: mont(s_, 'ExtraBold'), 600, 34, 22), _mix(GREEN, (255, 255, 255), 0) if sum(PAL_BG[0]) > 380 else (255, 255, 255))
        draw_t(d, (x0 + 10, top + 104), 'pricelist.talentededucationgroup.com', mont(24, 'Bold'), ACC if sum(PAL_BG[0]) < 380 else GREEN)
        st = stamp('GRATIS', 'KONSULTASI', ACC, GREEN, angle=-8, size=70)
        canvas.alpha_composite(st, (x1 - st.width + 10, top + (bottom - top - st.height) // 2 + 6))
    else:
        bn = Image.open(BR('banner-app.png')).convert('RGBA')
        bn = bn.resize((960, int(bn.height * 960 / bn.width)), Image.LANCZOS)
        canvas.alpha_composite(bn, ((W - 960) // 2, bottom - bn.height))
CNAME = {'AU': 'AUSTRALIA', 'NZ': 'SELANDIA BARU', 'GB': 'INGGRIS', 'CA': 'KANADA', 'US': 'AMERIKA', 'IE': 'IRLANDIA',
         'DE': 'JERMAN', 'FR': 'PRANCIS', 'NL': 'BELANDA', 'JP': 'JEPANG', 'KR': 'KOREA', 'SG': 'SINGAPURA', 'TW': 'TAIWAN',
         'CN': 'TIONGKOK', 'SE': 'SWEDIA', 'HU': 'HONGARIA', 'TR': 'TURKI', 'BN': 'BRUNEI', 'ES': 'SPANYOL', 'CH': 'SWISS',
         'MY': 'MALAYSIA', 'EU': 'EROPA', 'ANY': 'LUAR NEGERI'}
BUL = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
HL = re.compile(r'(\d{1,3}(?:[-–]\d{1,3})?%|(?:AUD|NZD|GBP|CAD|USD|EUR)\s?[\d.,]+)')


STYLE = {'font': 'anton', 'deco': 'none', 'cta': 'app'}  # diatur per posting oleh set_style()


def anton(s):
    """font judul: bergilir per posting (Anton / Montserrat Black / Poppins Bold) supaya desain tidak mirip semua"""
    f = STYLE.get('font', 'anton')
    if f == 'mont':
        ft = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Montserrat.ttf'), int(s * 0.82))
        try:
            ft.set_variation_by_name('Black')
        except Exception:
            pass
        return ft
    if f == 'poppins':
        return ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Bold.ttf'), int(s * 0.84))
    return ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Anton.ttf'), s)


def mont(s, w='Bold'):
    f = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Montserrat.ttf'), s)
    try:
        f.set_variation_by_name(w)
    except Exception:
        pass
    return f


def clean(t):
    t = re.sub(r'[\U0001F000-\U0001FFFF☀-➿⬀-⯿️‍]', '', t or '')
    return re.sub(r'\s+', ' ', t).strip(' :-|')


def idate(s, long=False):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    if not m:
        return s
    return f"{int(m.group(3))} {(BULAN if long else BUL)[int(m.group(2)) - 1]} {m.group(1)}"


def split_title(t):
    t = clean(t)
    m = re.search(r'\(?deadline\s*([0-9-]{10})\)?', t, re.I)
    dl = m.group(1) if m else None
    t = re.sub(r'\(?deadline\s*[0-9-]{10}\)?', '', t, flags=re.I)
    t = re.sub(r'^(Beasiswa dibuka|Beasiswa baru|Promo)\s*:\s*', '', t, flags=re.I)
    return clean(t), dl


def short_provider(p):
    if not p:
        return ''
    m = re.search(r'\(([A-Z][A-Za-z]{1,6})\)', p)
    if m:
        return m.group(1)
    p = re.split(r'[,&/]| dan | and ', re.sub(r'\(.*?\)', '', p))[0].strip()
    w = p.split()[:3]
    while w and w[-1].lower() in ('dan', 'and', 'of', 'the', 'for', 'de', 'des'):
        w.pop()
    return ' '.join(w)


# ---------------------------------------------------------------- helpers
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def th(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[3] - b[1]


def draw_t(d, xy, s, f, fill):
    """draw text so that its ink box starts exactly at xy; returns (w, h)"""
    b = d.textbbox((0, 0), s, font=f)
    d.text((xy[0] - b[0], xy[1] - b[1]), s, font=f, fill=fill)
    return b[2] - b[0], b[3] - b[1]


def fit_font(d, s, maker, maxw, start, minsize=20):
    size = start
    while size > minsize and tw(d, s, maker(size)) > maxw:
        size -= 2
    return maker(size)


def wrap(d, text, f, maxw, maxlines=2):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        n = (cur + ' ' + w_).strip()
        if tw(d, n, f) <= maxw or not cur:
            cur = n
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        while tw(d, lines[-1] + '…', f) > maxw and ' ' in lines[-1]:
            lines[-1] = lines[-1].rsplit(' ', 1)[0]
        lines[-1] += '…'
    return lines


def fit_person(im, Wb, Hb):
    """crop to Wb x Hb without cutting the head (Panduan S)"""
    im = im.convert('RGB'); iw, ih = im.size
    s = max(Wb / iw, Hb / ih); cx, top = iw / 2, 0
    try:
        import cv2, numpy as np
        # OpenCV 5 tidak lagi membawa file cascade: pakai salinan di repo (24/11/2026), cadangan dari paket cv2
        xml = os.path.join(ROOT, 'assets', 'cv', 'haarcascade_frontalface_default.xml')
        if not os.path.exists(xml):
            xml = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        if not os.path.exists(xml):
            print('PERINGATAN: deteksi wajah tidak aktif (file cascade tidak ada)')
        g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
        f = cv2.CascadeClassifier(xml).detectMultiScale(g, 1.1, 5, minSize=(40, 40))
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            cx, top = x + w / 2, max(0, y - 0.7 * h)
    except Exception:
        pass
    r = im.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    left = min(max(cx * s - Wb / 2, 0), r.width - Wb)
    up = min(max(top * s - Hb * 0.08, 0), r.height - Hb)
    return r.crop((int(left), int(up), int(left) + Wb, int(up) + Hb))


def grain(im, amt=0.04, seed=1):
    rnd = random.Random(seed)
    noise = Image.effect_noise(im.size, 64).convert('L')
    n = Image.merge('RGB', (noise, noise, noise))
    return Image.blend(im.convert('RGB'), n, amt)


def darken(im, k=0.62):
    return Image.eval(im.convert('RGB'), lambda v: int(v * k))


def poly_paste(canvas, photo, poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    box = (min(xs), min(ys), max(xs), max(ys))
    ph = fit_person(photo, box[2] - box[0], box[3] - box[1])
    mask = Image.new('L', (box[2] - box[0], box[3] - box[1]), 0)
    ImageDraw.Draw(mask).polygon([(x - box[0], y - box[1]) for x, y in poly], fill=255)
    canvas.paste(ph, box[:2], mask)


def logo_talented(canvas, dark, h=150, plate=False):
    """dark bg: white logo 02 directly; light bg: colour logo 01; over a photo: logo 01 on a small white plate"""
    lg = Image.open(BR('logo-talented-warna.png' if (plate or not dark) else 'logo-talented-putih.png')).convert('RGBA')
    lg = lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS)
    if plate:
        pl = Image.new('RGBA', (lg.width + 28, h + 24), (255, 255, 255, 255))
        pl.alpha_composite(lg, (14, 12)); lg = pl
        canvas.alpha_composite(lg, (M - 14, M - 12))
    else:
        canvas.alpha_composite(lg, (M, M))
    return lg.width


def logo_provider(canvas, path, maxw=240, maxh=96):
    if not path:
        return
    if STYLE.get('logo_big'):
        maxw, maxh = 300, 170  # badge kredensial (postingan kepercayaan) lebih besar
    lg = Image.open(path).convert('RGBA')
    lg.thumbnail((maxw - 28, maxh - 24), Image.LANCZOS)
    bg = lg.convert('RGB').getpixel((1, 1))
    plate_col = bg if (sum(bg) < 600 and lg.getpixel((1, 1))[3] > 200) else (255, 255, 255)
    pw, ph = lg.width + 28, lg.height + 24
    plate = Image.new('RGBA', (pw, ph), plate_col + (255,))
    plate.alpha_composite(lg, (14, 12))
    canvas.alpha_composite(plate, (W - M - pw, M))


def find_logo(provider):
    if not provider:
        return None
    from social_photos import resolve_provider
    sl = resolve_provider(provider)
    if sl and os.path.exists(os.path.join(ROOT, 'assets', 'providers', sl + '.png')):
        return os.path.join(ROOT, 'assets', 'providers', sl + '.png')
    try:
        b = json.load(open(os.path.join(ROOT, 'data', 'banners.json'), encoding='utf-8'))
    except Exception:
        return None
    pl = provider.lower()
    for it in b.get('items', []):
        m = re.search(r'/assets/sponsors/([a-z0-9-]+)\.(webp|png|jpg)$', ((it.get('logo') or {}).get('src') or ''))
        if not m:
            continue
        k, bp = m.group(1), (it.get('provider') or '').lower()
        abbr = re.findall(r'\(([A-Za-z]{2,6})\)', it.get('provider') or '')
        if (bp and (bp in pl or pl in bp)) or re.search(rf'\b{k}\b', pl) or any(re.search(rf'\b{a.lower()}\b', pl) for a in abbr):
            p = os.path.join(ROOT, 'assets', 'sponsors', f'{k}.{m.group(2)}')
            if os.path.exists(p):
                return p
    return None


def watermark(canvas, dark):
    """anti-copy: faint diagonal repeated brand text over the stage + small copyright line above the banner"""
    W_, top = canvas.width, STAGE + 5
    layer = Image.new('RGBA', (W_ * 2, W_ * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = mont(30, 'Bold')
    txt = 'TALENTED EDUCATION GROUP  ·  talentededucationgroup.com  ·  '
    col = (255, 255, 255, 20) if dark else (23, 63, 53, 20)
    for y in range(0, W_ * 2, 130):
        d.text(((y // 130) % 2 * -220, y), txt * 4, font=f, fill=col)
    layer = layer.rotate(28, resample=Image.BICUBIC)
    l, t = (layer.width - W_) // 2, (layer.height - top) // 2
    canvas.alpha_composite(layer.crop((l, t, l + W_, t + top)), (0, 0))
    dd = ImageDraw.Draw(canvas)
    fc = mont(15, 'Bold')
    s_ = '© Talented Education Group · konten asli, dilarang menyalin tanpa izin'
    w_ = dd.textlength(s_, font=fc)
    dd.text((W_ - M - w_, 712), s_, font=fc, fill=(255, 255, 255, 235) if dark else (23, 63, 53, 235),
            stroke_width=2, stroke_fill=(0, 0, 0, 160) if dark else (255, 255, 255, 200))


def _recolor(img, src, dst, tol=22):
    import numpy as np
    a = np.array(img.convert('RGBA')).astype('int16')
    m = (abs(a[..., 0] - src[0]) + abs(a[..., 1] - src[1]) + abs(a[..., 2] - src[2])) < tol
    a[m, 0], a[m, 1], a[m, 2] = dst
    return Image.fromarray(a.astype('uint8'), 'RGBA')


def footer_and_banner(canvas, dark, accent):
    watermark(canvas, dark)
    ft = Image.open(BR('footer-hijau.png' if dark else 'footer-terang.png')).convert('RGBA')
    # footer ikut warna palet (isi: QR, PIER, Victory, sosmed tetap sama)
    try:
        ft = _recolor(ft, (23, 63, 53), GREEN) if dark else _recolor(ft, (246, 241, 230), PAL_BG[0] if sum(PAL_BG[0]) > 600 else (246, 241, 230))
    except Exception:
        pass
    canvas.alpha_composite(ft, (0, FOOT_Y))
    top = 916 - int(182 * 960 / 993)
    cta_band(canvas, top, 916)
    return top  # top of banner


def price_line(d, x, y, price, unit, color, size=44, maxw=600):
    """price + unit glued on one baseline (Panduan O1)"""
    if not price:
        return 0
    fp = fit_font(d, price, lambda s: mont(s, 'ExtraBold'), maxw * 0.75, size, 24)
    fu = mont(max(18, int(fp.size * 0.62)), 'Bold')
    asc_p = fp.getmetrics()[0]
    d.text((x, y), price, font=fp, fill=color)
    if unit:
        px = x + d.textlength(price + ' ', font=fp)
        d.text((px, y + asc_p - fu.getmetrics()[0]), unit, font=fu, fill=color)
    return sum(fp.getmetrics())


# ---------------------------------------------------------------- content
def derive(kind, title, sub, country, provider, spec):
    t, dl = split_title(clean(title))
    spec = dict(spec or {})
    from social_photos import code as _code
    cc = _code(country or 'ANY')
    cn = CNAME.get(cc, 'LUAR NEGERI')
    hero = spec.get('hero')
    if not hero:
        m = HL.search(t)
        if m and kind in ('scholarship', 'promo', 'sponsored', 'marketing'):
            hero = m.group(1).replace(' ', ' ')
    prov = short_provider(provider)
    head = spec.get('headline')
    if not head:
        if kind == 'scholarship':
            head = f'BEASISWA KULIAH DI {cn}'
        elif kind in ('promo', 'sponsored'):
            head = f'KULIAH DI {cn}' + (' HEMAT' if hero else '')
        elif kind == 'accommodation':
            head = f'AKOMODASI PELAJAR {cn}'
        elif kind == 'jobs':
            head = 'LOKER LUAR NEGERI'  # QA 24/11/2026: jangan klaim part-time/pelajar
        elif kind == 'news':
            head = 'UPDATE VISA PELAJAR ' + (cn if cc != 'ANY' else '')
        else:
            head = ' '.join(t.split()[:5])
    if kind == 'news' and not spec.get('headline'):
        # news: the news itself is the headline (country prefix kept short), up to 12 words
        tt = re.sub(r'^(Selandia Baru|New Zealand)\s*:', 'NZ:', t)
        tt = re.sub(r'^(Amerika Serikat|United States)\s*:', 'AS:', tt)
        head = ' '.join(tt.upper().split()[:12])
    else:
        head = ' '.join(head.upper().split()[:6])
    info = list(spec.get('info') or [])
    if not info and kind == 'jobs':
        # QA 24/11/2026: hindari teks terpotong; jumlah + negara singkat + atribusi wajib
        mm = re.search(r'(\d+)', t); cs = re.search(r'\(([^)]*)\)', t)
        cl = [c.strip() for c in (cs.group(1).split(',') if cs else []) if c.strip()]
        short = {'United Kingdom': 'UK', 'New Zealand': 'NZ', 'United States': 'AS', 'Switzerland': 'Swiss', 'Germany': 'Jerman', 'France': 'Prancis', 'Spain': 'Spanyol', 'Canada': 'Kanada', 'Singapore': 'Singapura'}
        cl = [short.get(c, c) for c in cl]
        if mm: info.append(f"{mm.group(1)} lowongan baru di {len(cl)} negara" if cl else f"{mm.group(1)} lowongan baru")
        if cl: info.append(', '.join(cl[:5]) + (f' +{len(cl) - 5}' if len(cl) > 5 else ''))
    if not info:
        prog = re.sub(r'^' + re.escape(prov) + r'\s*-\s*', '', t) if prov else t
        if hero:
            prog = clean(prog.replace(hero, '').replace('hingga', '').replace('  ', ' '))
            prog = re.sub(r'\(\s*\)', '', prog).strip(' -')
        if len(prog) < 14:
            prog = t
        info.append(prog[:70])
        where = sub or (cn.title() if cc != 'ANY' else '')
        if dl:
            info.append((where + ' · ' if where else '') + 'Deadline ' + idate(dl))
        elif where:
            info.append(where)
    foot = spec.get('footnote') or ('*Data: Jobs by Adzuna · syarat tiap lowongan berbeda.' if kind == 'jobs' else '*Syarat & ketentuan berlaku.' if kind != 'news' else '*Detail & link resmi di caption.')
    return {"t": t, "dl": dl, "hero": hero, "head": head, "info": info[:3], "price": spec.get('price'),
            "unit": spec.get('unit'), "foot": foot, "cc": cc, "prov": prov}


DARK_PALS = [p for p, v in PAL.items() if v[3] and p != 'P6']
LIGHT_PALS = [p for p, v in PAL.items() if not v[3]]
ALL_PALS = DARK_PALS + LIGHT_PALS
LAYOUTS = {  # name: (needs hero, needs deadline, allowed palettes)
    'A': (True, False, DARK_PALS), 'B': (False, False, ALL_PALS), 'C': (False, False, ALL_PALS),
    'D': (True, False, DARK_PALS), 'E': (False, False, LIGHT_PALS), 'F': (False, False, DARK_PALS),
    'G': (False, True, ALL_PALS), 'H': (False, False, ALL_PALS),
    'I': (False, False, ALL_PALS), 'J': (False, False, ALL_PALS), 'K': (False, False, ALL_PALS),
}
NEED_PHOTO = {'I', 'J', 'K'}  # layout baru hanya dipakai bila ada foto asli
LAYOUT_NAMES = {'T': 'Tipografi berita resmi', 'A': 'Foto kanan diagonal', 'B': 'Foto penuh + panel', 'C': 'Foto atas diagonal', 'D': 'Tipografi + foto miring',
                'E': 'Majalah/editorial', 'F': 'Tiket boarding pass', 'G': 'Kalender deadline', 'H': 'Tipografi bertumpuk + cap',
                'I': 'Foto lingkaran + blok warna', 'J': 'Kolase polaroid', 'K': 'Foto penuh + harga besar di bawah'}


def pick_style(key, has_hero, has_dl=False):
    """random rolling (seeded by key) across 8 layouts; never repeats the last 3 layouts; P1 max 2 in a row"""
    try:
        log = json.load(open(LOG, encoding='utf-8'))
    except Exception:
        log = {"note": "LOG desain sosmed otomatis (Panduan: layout/palet bergilir).", "items": []}
    for it in log['items']:
        if it.get('key') == key and it.get('v') in (9, 10):
            return it['layout'], it['palette'], log, True
    rnd = random.Random(hashlib.sha256(key.encode()).hexdigest())
    last = [i for i in log['items'] if i.get('key') != key][-5:]
    recent = {i['layout'] for i in last[-4:]}  # 12 layout: tidak mengulang 4 layout terakhir
    ok = [l for l, (nh, nd, _) in LAYOUTS.items() if (has_hero or not nh) and (has_dl or not nd)]
    pool = [l for l in ok if l not in recent] or ok
    if has_dl and 'G' in pool and rnd.random() < 0.4:
        lay = 'G'
    else:
        # layout foto baru (I/J/K) sedikit lebih sering supaya tampilan feed segar
        lay = rnd.choice(pool + [l for l in pool if l in NEED_PHOTO])
    pals = list(LAYOUTS[lay][2])
    # warna berganti tiap posting: tidak mengulang 5 palet terakhir; palet khas Talented ±25%
    recent_p = {i.get('palette') for i in last}
    fresh = [p for p in pals if p not in recent_p] or pals
    brand = [p for p in fresh if p in BRAND_PALS]
    other = [p for p in fresh if p not in BRAND_PALS]
    if brand and (not other or rnd.random() < 0.25):
        return lay, rnd.choice(brand), log, False
    return lay, rnd.choice(other or fresh), log, False


# ---------------------------------------------------------------- layouts
def render(c, lay, pal, photo, logo_path):
    set_palette(pal)
    if lay in NEED_PHOTO:
        return render_new(c, lay, pal, photo, logo_path)
    if lay == 'T':
        return render_news(c, pal)
    if lay in ('E', 'F', 'G', 'H'):
        return render_extra(c, lay, pal, photo, logo_path)
    bg, tx, ac, dark = PAL[pal]
    if lay == 'B':
        dark = True  # text sits on the solid green panel
    im = base_canvas(bg)
    d = ImageDraw.Draw(im)
    if photo is not None:
        photo = grain(photo, 0.035)
    if lay == 'A':
        if photo is not None:
            poly_paste(im, photo, [(640, 0), (1080, 0), (1080, FOOT_Y), (500, FOOT_Y)])
        else:
            d.polygon([(640, 0), (1080, 0), (1080, FOOT_Y), (500, FOOT_Y)], fill=PANEL2 if dark else (0xE4, 0xDC, 0xC8))
    elif lay == 'B':
        if photo is not None:
            im.paste(fit_person(photo, W, FOOT_Y), (0, 0))
        im.alpha_composite(Image.new('RGBA', (760, FOOT_Y - 440), GREEN + (255,)), (0, 440))
        d.rectangle([0, 434, 760, 440], fill=ACC)
        tx, ac = (255, 255, 255), ACC
    elif lay == 'C':
        if photo is not None:
            poly_paste(im, darken(photo, 0.8), [(0, 0), (1080, 0), (1080, 380), (0, 460)])
    elif lay == 'D':
        if photo is not None:
            pw, ph = 360, 450
            p = fit_person(photo, pw, ph).convert('RGBA')
            frame = Image.new('RGBA', (pw + 20, ph + 20), (255, 255, 255, 255) if dark else GREEN + (255,))
            frame.alpha_composite(p, (10, 10))
            frame = frame.rotate(-4, resample=Image.BICUBIC, expand=True)
            im.alpha_composite(frame, (W - M - frame.width + 10, 230))
    d = ImageDraw.Draw(im)
    on_photo = photo is not None and lay in ('B', 'C')
    lw = logo_talented(im, dark, 140 if on_photo else 150, plate=on_photo)
    logo_provider(im, logo_path)
    d = ImageDraw.Draw(im)
    banner_top = footer_and_banner(im, PAL[pal][3] if lay != 'B' else True, ac)
    d = ImageDraw.Draw(im)
    limit = banner_top - 18  # stage bottom for text
    sec = tx if tx != (255, 255, 255) else (255, 255, 255)

    if lay == 'A':
        x, y, maxw = M, 236, 500
        fh = fit_font(d, c['head'], anton, maxw, 70, 40)
        for ln in wrap(d, c['head'], fh, maxw, 2):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 12
        y += 10
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, 440, 250, 90)
            _, h_ = draw_t(d, (x, y), c['hero'], fhero, tx); y += h_ + 18
            d.rectangle([x, y, x + min(440, tw(d, c['hero'], fhero)), y + 10], fill=ac); y += 30
        y += price_line(d, x, y, c['price'], c['unit'], ac, 42, 470)
        fi = mont(30, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 450, 2 if i == 0 else 1):
                if y + 32 > limit - 30: break
                _, h_ = draw_t(d, (x, y), l2, fi, tx if i else ac); y += h_ + 10
        draw_t(d, (x, min(y + 6, limit - 20)), c['foot'], mont(18, 'Medium'), tx)
    elif lay == 'B':
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, 300, 170, 70)
            hw, hh = tw(d, c['hero'], fhero), th(d, c['hero'], fhero)
            bx0, by0 = 1080 - M - hw - 50, 250
            d.rectangle([bx0, by0, bx0 + hw + 50, by0 + hh + 50], fill=ACC)
            draw_t(d, (bx0 + 25, by0 + 25), c['hero'], fhero, GREEN)
        x, y, maxw = M, 470, 660
        fh = fit_font(d, c['head'], anton, maxw, 66, 40)
        for ln in wrap(d, c['head'], fh, maxw, 2):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 10
        y += 14
        y += price_line(d, x, y, c['price'], c['unit'], ac, 40, 640) + (8 if c['price'] else 0)
        fi = mont(28, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 650, 1):
                if y + 28 > limit - 26: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 10
        draw_t(d, (x, min(y + 4, limit - 18)), c['foot'], mont(18, 'Medium'), tx)
    elif lay == 'C':
        y0 = 500
        x = M
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, 480, 240, 90)
            hw, hh = draw_t(d, (x, y0), c['hero'], fhero, ac)
            x2 = x + hw + 36
        else:
            x2 = x
        maxw = W - M - x2
        y = y0
        fh = fit_font(d, c['head'], anton, maxw, 72 if not c['hero'] else 60, 34)
        for ln in wrap(d, c['head'], fh, maxw, 2):
            _, h_ = draw_t(d, (x2, y), ln, fh, tx); y += h_ + 8
        y += 10
        y += price_line(d, x2, y, c['price'], c['unit'], ac, 32, maxw) + (6 if c['price'] else 0)
        fi = mont(24 if not c['hero'] else 21, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, maxw, 2 if i == 0 else 1):
                if y + 26 > limit - 22: break
                _, h_ = draw_t(d, (x2, y), l2, fi, ac if i == 0 else tx); y += h_ + 8
        draw_t(d, (M, limit - 18), c['foot'], mont(18, 'Medium'), tx)
    elif lay == 'D':
        x, y = M, 236
        maxw = 580
        fh = fit_font(d, c['head'], anton, maxw, 64, 36)
        for ln in wrap(d, c['head'], fh, maxw, 2):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 10
        y += 16
        hero = c['hero']
        num, pct = (hero[:-1], '%') if hero.endswith('%') else (hero, '')
        fn = fit_font(d, num, anton, 470 if pct else 560, 300, 90)
        nw, nh = draw_t(d, (x, y), num, fn, tx)
        if pct:
            draw_t(d, (x + nw + 8, y), '%', anton(int(fn.size * 0.55)), ac)
        y += nh + 22
        if c['price']:
            fp = mont(34, 'ExtraBold')
            bw_ = min(560, tw(d, c['price'] + ' ' + (c['unit'] or ''), fp) + 36)
            d.rectangle([x, y, x + bw_, y + 58], fill=ac)
            price_line(d, x + 18, y + 9, c['price'], c['unit'], GREEN if dark else (255, 255, 255), 34, bw_ - 36)
            y += 74
        fi = mont(27, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 600, 1):
                if y + 28 > limit - 24: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 8
        draw_t(d, (x, min(y + 4, limit - 18)), c['foot'], mont(18, 'Medium'), tx)
    return im.convert('RGB')


def render_news(c, pal):
    """typography-only official news card: kicker, big title, announced date + official source domain"""
    if pal not in DARK_PALS:
        pal = 'P1'
    set_palette(pal)
    bg, tx, ac, dark = PAL[pal]
    im = base_canvas(bg)
    d = ImageDraw.Draw(im)
    d.polygon([(W - 300, 0), (W, 0), (W, 300)], fill=PANEL2)  # diagonal cut like the Talented logo
    banner_y = 916 - int(182 * 960 / 993)
    limit = banner_y - 24
    x, y = M, 240
    fk = mont(26, 'ExtraBold')
    kick = c['head']
    kw = tw(d, kick, fk)
    d.rectangle([x, y, x + kw + 36, y + 50], fill=ac)
    draw_t(d, (x + 18, y + 12), kick, fk, GREEN)
    y += 82
    t = re.sub(r'^(Australia|Selandia Baru|New Zealand|Inggris|Kanada|AS|Amerika Serikat|[A-Z]{2})\s*:\s*', '', c['t'])
    maxw, maxh = W - 2 * M, limit - y - 120
    size = 92
    while True:
        f = anton(size)
        ls = wrap(d, t.upper(), f, maxw, 6)
        if len(ls) * (size * 1.12) <= maxh or size <= 44:
            break
        size -= 4
    for ln in ls:
        _, h_ = draw_t(d, (x, y), ln, f, tx); y += int(size * 1.12)
    y += 14
    d.rectangle([x, y, x + 140, y + 8], fill=ac); y += 28
    fi = mont(28, 'Bold')
    for i, ln in enumerate(c['info'][:2]):
        for l2 in wrap(d, ln, fi, maxw, 1):
            if y + 34 > limit:
                break
            _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 12
    logo_talented(im, True, 150)
    footer_and_banner(im, True, ac)
    return im.convert('RGB')


def stamp(text, sub, fill, ink, angle=-7, size=150):
    """flat solid stamp, rotated 4-10 deg (Panduan L) - no shadow"""
    f = anton(size)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    w_, h_ = tw(tmp, text, f), th(tmp, text, f)
    fs = mont(26, 'ExtraBold')
    sw = tw(tmp, sub, fs) if sub else 0
    bw, bh = max(w_, sw) + 70, h_ + (60 if sub else 0) + 60
    st = Image.new('RGBA', (bw, bh), fill + (255,))
    d = ImageDraw.Draw(st)
    d.rectangle([8, 8, bw - 9, bh - 9], outline=ink + (255,), width=4)
    draw_t(d, ((bw - w_) // 2, 30), text, f, ink)
    if sub:
        draw_t(d, ((bw - sw) // 2, 30 + h_ + 18), sub, fs, ink)
    return st.rotate(angle, resample=Image.BICUBIC, expand=True)


def render_extra(c, lay, pal, photo, logo_path):
    bg, tx, ac, dark = PAL[pal]
    im = base_canvas(bg)
    d = ImageDraw.Draw(im)
    if photo is not None:
        photo = grain(photo, 0.035)
    alt = PANEL2 if dark else ((0xE6, 0xDE, 0xCB) if pal == 'P2' else (0xDD, 0xE7, 0xDA) if pal == 'P5' else (0xEE, 0xEE, 0xEA))
    banner_y = 916 - int(182 * 960 / 993)
    limit = banner_y - 18
    on_photo = False
    if lay == 'E':  # editorial: framed photo right, big left headline, highlighted word
        if photo is not None:
            d.rectangle([622, 232, 1040, 712], fill=GREEN)
            im.paste(fit_person(photo, 400, 470), (604, 214))
        x, y = M, 250
        words = c['head'].split()
        fh = anton(84)
        lines = wrap(d, c['head'], fh, 500, 3)
        while len(lines) > 3 or max(tw(d, l_, fh) for l_ in lines) > 500:
            fh = anton(fh.size - 4); lines = wrap(d, c['head'], fh, 500, 3)
        for i, ln in enumerate(lines):
            if i == len(lines) - 1:
                lw_ = tw(d, ln, fh); lh_ = th(d, ln, fh)
                d.rectangle([x - 10, y - 8, x + lw_ + 12, y + lh_ + 10], fill=ac)
                draw_t(d, (x, y), ln, fh, GREEN if not dark else bg)
            else:
                draw_t(d, (x, y), ln, fh, tx)
            y += th(d, ln, fh) + 18
        y += 16
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, 500, 150, 70)
            _, h_ = draw_t(d, (x, y), c['hero'], fhero, ac if dark else tx); y += h_ + 16
        y += price_line(d, x, y, c['price'], c['unit'], ac, 36, 500)
        fi = mont(27, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 520, 2 if i == 0 else 1):
                if y + 28 > limit - 22: break
                _, h_ = draw_t(d, (x, y), l2, fi, tx); y += h_ + 8
        draw_t(d, (x, min(y + 6, limit - 18)), c['foot'], mont(18, 'Medium'), tx)
    elif lay == 'F':  # boarding pass
        tk = (0xF6, 0xF1, 0xE6)
        x0, y0, x1, y1, cut = M, 236, W - M, 700, 700
        d.rectangle([x0, y0, x1, y1], fill=tk)
        for yy in (y0, y1):
            d.ellipse([cut - 22, yy - 22, cut + 22, yy + 22], fill=bg)
        for yy in range(y0 + 34, y1 - 30, 22):
            d.line([(cut, yy), (cut, yy + 10)], fill=(0xB9, 0xB0, 0x9C), width=3)
        if photo is not None:
            ph = fit_person(photo, x1 - cut - 24, y1 - y0 - 24)
            im.paste(ph, (cut + 12, y0 + 12))
        ink = GREEN
        fl = mont(20, 'ExtraBold')
        draw_t(d, (x0 + 34, y0 + 30), 'BOARDING PASS  ·  STUDY ABROAD', fl, (0xC8, 0x90, 0x1A))
        dest = CNAME.get(c['cc'], 'LUAR NEGERI')
        arrow = ' → ' if STYLE.get('font', 'anton') == 'anton' else ' - '  # Poppins/Montserrat tidak punya panah
        fr = fit_font(d, 'INDONESIA' + arrow + dest, anton, cut - x0 - 70, 64, 34)
        draw_t(d, (x0 + 34, y0 + 70), 'INDONESIA' + arrow + dest, fr, ink)
        y = y0 + 70 + th(d, 'INDONESIA', fr) + 26
        d.line([(x0 + 34, y), (cut - 34, y)], fill=(0xC8, 0x90, 0x1A), width=4); y += 22
        fh = fit_font(d, c['head'], anton, cut - x0 - 70, 44, 28)
        for ln in wrap(d, c['head'], fh, cut - x0 - 70, 2):
            _, h_ = draw_t(d, (x0 + 34, y), ln, fh, ink); y += h_ + 8
        y += 10
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, cut - x0 - 70, 120, 60)
            _, h_ = draw_t(d, (x0 + 34, y), c['hero'], fhero, (0xC8, 0x90, 0x1A)); y += h_ + 14
        y += price_line(d, x0 + 34, y, c['price'], c['unit'], ink, 30, cut - x0 - 70)
        fi = mont(24, 'Bold')
        for ln in c['info'][:2]:
            for l2 in wrap(d, ln, fi, cut - x0 - 70, 1):
                if y + 24 > y1 - 26: break
                _, h_ = draw_t(d, (x0 + 34, y), l2, fi, ink); y += h_ + 6
        draw_t(d, (M, limit - 18), c['foot'], mont(18, 'Medium'), tx)
    elif lay == 'G':  # calendar deadline
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', c['dl'] or '')
        day, mon, yr = (str(int(m.group(3))), BULAN[int(m.group(2)) - 1].upper(), m.group(1)) if m else ('', '', '')
        if photo is not None:
            poly_paste(im, photo, [(560, 0), (1080, 0), (1080, FOOT_Y), (700, FOOT_Y)])
        cx0, cy0, cw, ch = M, 240, 400, 420
        d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=(255, 255, 255))
        d.rectangle([cx0, cy0, cx0 + cw, cy0 + 86], fill=ac)
        fm = fit_font(d, f'{mon} {yr}', lambda s_: mont(s_, 'ExtraBold'), cw - 40, 34, 18)
        draw_t(d, (cx0 + (cw - tw(d, f'{mon} {yr}', fm)) // 2, cy0 + 26), f'{mon} {yr}', fm, GREEN)
        fd = anton(250)
        draw_t(d, (cx0 + (cw - tw(d, day, fd)) // 2, cy0 + 120), day, fd, GREEN)
        fdl = mont(24, 'ExtraBold')
        draw_t(d, (cx0 + (cw - tw(d, 'DEADLINE', fdl)) // 2, cy0 + ch - 50), 'DEADLINE', fdl, (0xC8, 0x90, 0x1A))
        x, y = M, cy0 + ch + 26
        maxw = 640
        fh = fit_font(d, c['head'], anton, maxw, 54, 30)
        for ln in wrap(d, c['head'], fh, maxw, 1):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 8
        fi = mont(26, 'Bold')
        for i, ln in enumerate(c['info'][:1]):
            for l2 in wrap(d, ln, fi, 640, 1):
                if y + 26 > limit - 20: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac); y += h_ + 6
        if c['hero']:
            st = stamp(c['hero'], None, ac, GREEN, angle=8, size=96)
            im.alpha_composite(st, (cx0 + cw - 40, cy0 + 60))
    elif lay == 'H':  # stacked typography + photo strip + stamp
        if photo is not None:
            im.paste(fit_person(photo, 400, FOOT_Y - 0), (W - 400, 0))
            d.rectangle([W - 412, 0, W - 400, FOOT_Y], fill=ac)
        x, y = M, 236
        words = c['head'].split()
        maxw = W - 400 - M - 40
        lines, cur = [], ''
        for w_ in words:  # 1-2 words per line, huge
            n = (cur + ' ' + w_).strip()
            if cur and (len(n.split()) > 2 or tw(d, n, anton(92)) > maxw):
                lines.append(cur); cur = w_
            else:
                cur = n
        lines.append(cur)
        lines = lines[:4]
        size = 120
        while size > 50 and (max(tw(d, l_, anton(size)) for l_ in lines) > maxw or len(lines) * size * 1.08 > 330):
            size -= 4
        fh = anton(size)
        hi = max(range(len(lines)), key=lambda i: len(lines[i])) if len(lines) > 1 else 0
        for i, ln in enumerate(lines):
            lh_ = th(d, ln, fh)
            if i == hi:
                d.rectangle([x - 10, y - 8, x + tw(d, ln, fh) + 12, y + lh_ + 10], fill=ac)
                draw_t(d, (x, y), ln, fh, GREEN)
            else:
                draw_t(d, (x, y), ln, fh, tx)
            y += lh_ + 20
        y += 6
        y += price_line(d, x, y, c['price'], c['unit'], ac, 34, maxw)
        fi = mont(26, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, maxw, 1):
                if y + 26 > limit - 20: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 6
        draw_t(d, (x, min(y + 6, limit - 18)), c['foot'], mont(18, 'Medium'), tx)
        if c['hero']:
            sz = 110
            while True:
                st = stamp(c['hero'], 'BEASISWA' if re.search('beasiswa|scholarship', c['t'], re.I) else None, ac, GREEN, angle=-7, size=sz)
                if st.width <= 380 or sz <= 50:
                    break
                sz -= 8
            im.alpha_composite(st, (W - 400 + max(0, (400 - st.width) // 2), 470))
        on_photo = photo is not None
    logo_talented(im, dark, 150)
    logo_provider(im, logo_path)
    footer_and_banner(im, dark, ac)
    return im.convert('RGB')


def _polaroid(photo, w, h, angle, ink):
    p = fit_person(photo, w, h).convert('RGBA')
    fr = Image.new('RGBA', (w + 28, h + 90), (255, 255, 255, 255))
    fr.alpha_composite(p, (14, 14))
    ImageDraw.Draw(fr).rectangle([0, 0, w + 27, h + 89], outline=ink + (60,), width=2)
    return fr.rotate(angle, resample=Image.BICUBIC, expand=True)


def _stack_head(d, text, x, y, maxw, col, lines=3, start=78, low=40):
    size = start
    while size > low:
        ls = wrap(d, text, anton(size), maxw, 9)
        if len(ls) <= lines and max(tw(d, l_, anton(size)) for l_ in ls) <= maxw:
            break
        size -= 4
    f = anton(size)
    for ln in wrap(d, text, f, maxw, lines):
        _, h_ = draw_t(d, (x, y), ln, f, col); y += h_ + 10
    return y


def render_new(c, lay, pal, photo, logo_path):
    """layout tambahan (pemilik 23/11/2026): I lingkaran foto, J kolase polaroid, K foto penuh + blok harga"""
    bg, tx, ac, dark = PAL[pal]
    photos = photo if isinstance(photo, list) else [photo]
    photos = [grain(p_, 0.03) for p_ in photos if p_ is not None]
    im = base_canvas(bg)
    d = ImageDraw.Draw(im)
    banner_y = 916 - int(182 * 960 / 993)
    limit = banner_y - 18
    rnd = random.Random(c['t'])
    plate = False
    if lay == 'I':
        cx, cy, r = 760, 330, 270
        if rnd.random() < 0.5:
            d.ellipse([cx - r - 40, cy - r + 60, cx - r + 120, cy - r + 220], fill=ac)  # titik aksen
        d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=ac)
        if photos:
            ph = fit_person(photos[0], 2 * r, 2 * r).convert('RGBA')
            mk = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(mk).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
            im.paste(ph, (cx - r, cy - r), mk)
        d = ImageDraw.Draw(im)
        x, y, maxw = M, 236, 430
        y = _stack_head(d, c['head'], x, y, maxw, tx) + 18
    elif lay == 'J':
        angs = [-6, 5, -2]
        spots = [(470, 190, 340, 300), (650, 360, 330, 290)] if len(photos) > 1 else [(520, 200, 430, 400)]
        for i, (px, py, pw, ph_) in enumerate(spots[:max(1, len(photos))]):
            if i < len(photos):
                pol = _polaroid(photos[i], pw, ph_, angs[i], GREEN)
                im.alpha_composite(pol, (px, py))
        d = ImageDraw.Draw(im)
        d.rectangle([560, 176, 660, 206], fill=ac + (255,))  # selotip
        x, y, maxw = M, 236, 400
        y = _stack_head(d, c['head'], x, y, maxw, tx) + 18
    else:  # K
        top = 520
        if photos:
            im.paste(fit_person(photos[0], W, top + 80), (0, 0))
        d = ImageDraw.Draw(im)
        d.polygon([(0, top), (W, top - 70), (W, H), (0, H)], fill=bg)
        d.polygon([(0, top - 8), (W, top - 78), (W, top - 64), (0, top + 6)], fill=ac)
        plate = bool(photos)
        x, y, maxw = M, top + 6, W - 2 * M
        fh = fit_font(d, c['head'], anton, maxw, 58, 32)
        for ln in wrap(d, c['head'], fh, maxw, 1):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 8
        y += 4
    maxw = W - M - x if lay == 'K' else 600
    if c['hero']:
        fhero = fit_font(d, c['hero'], anton, maxw if lay == 'K' else 430, 130 if lay == 'K' else 100, 56)
        hw, hh = tw(d, c['hero'], fhero), th(d, c['hero'], fhero)
        if y + hh + 30 < limit:
            d.rectangle([x - 12, y - 6, x + hw + 14, y + hh + 16], fill=ac)
            draw_t(d, (x, y), c['hero'], fhero, GREEN); y += hh + 30
    y += price_line(d, x, y, c['price'], c['unit'], ac, 34, 560)
    fi = mont(26, 'Bold')
    for i, ln in enumerate(c['info'][:2]):
        for l2 in wrap(d, ln, fi, maxw, 1):
            if y + 28 > limit - 22: break
            _, h_ = draw_t(d, (x, y), l2, fi, tx); y += h_ + 6
    draw_t(d, (x, min(y + 6, limit - 18)), c['foot'], mont(18, 'Medium'), tx)
    logo_talented(im, dark, 140 if plate else 150, plate=plate)
    logo_provider(im, logo_path)
    footer_and_banner(im, dark, ac)
    return im.convert('RGB')


def make_story(png_path):
    """1080x1920 story: poster centered on brand colour, flat bands (no AI, no gradients)"""
    po = Image.open(png_path).convert('RGB')
    st = Image.new('RGB', (1080, 1920), GREEN)
    d = ImageDraw.Draw(st)
    st.paste(po, (0, 285))
    f1 = mont(34, 'ExtraBold')
    t1 = 'INFO TERBARU DARI TALENTED'
    draw_t(d, ((1080 - tw(d, t1, f1)) // 2, 120), t1, f1, ACC)
    d.rectangle([440, 185, 640, 191], fill=ACC)
    f2 = mont(36, 'ExtraBold')
    t2 = 'Scan QR atau klik link di bio'
    draw_t(d, ((1080 - tw(d, t2, f2)) // 2, 1700), t2, f2, (255, 255, 255))
    f3 = mont(26, 'Bold')
    t3 = 'linktr.ee/talentededucationgroup'
    draw_t(d, ((1080 - tw(d, t3, f3)) // 2, 1770), t3, f3, ACC)
    out = png_path[:-4] + ' Story.png'
    st.save(out, optimize=True)
    return out


def make_reel(story_path, seconds=8):
    """vertical 9:16 MP4 (H.264, 30 fps): slow zoom on the story frame; adds a licensed track from
    assets/music/*.mp3 if the owner put one there (otherwise silent - music can be added in the app)."""
    import subprocess, glob as _g
    out = story_path.replace(' Story.png', ' Reel.mp4')
    tmp = out[:-4] + '.tmp.mp4'
    music = sorted(_g.glob(os.path.join(ROOT, 'assets', 'music', '*.mp3')))
    n = seconds * 30
    # gerakan kamera acak per posting (pemilik 23/11/2026): zoom masuk, zoom keluar, geser atas/bawah
    moves = [f"z='min(1+0.0004*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
             f"z='max(1.08-0.0004*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
             f"z='1.07':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{n}'",
             f"z='1.07':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{n})'"]
    mv = moves[int(hashlib.sha256(story_path.encode()).hexdigest(), 16) % len(moves)]
    vf = (f"scale=1296:2304,zoompan={mv}"
          f":d={n}:s=1080x1920:fps=30,fade=t=in:st=0:d=0.4,format=yuv420p")
    import shutil as _sh
    ff = _sh.which('ffmpeg')
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            print('reel skipped: no ffmpeg'); return None
    cmd = [ff, '-y', '-loglevel', 'error', '-loop', '1', '-i', story_path]
    if music:
        # lagu acak, hindari lagu yang dipakai baru-baru ini; mulai dari detik acak (pemilik 21/11/2026)
        import random as _r, json as _j
        rec_p = os.path.join(ROOT, 'social', 'music-recent.json')
        try:
            recent = _j.load(open(rec_p, encoding='utf-8'))
        except Exception:
            recent = []
        names = [os.path.basename(x) for x in music]
        keep = max(0, min(len(names) - 3, 10))
        pool = [x for x in music if os.path.basename(x) not in recent[-keep:]] if keep else music
        pick = _r.choice(pool or music)
        recent = (recent + [os.path.basename(pick)])[-30:]
        try:
            _j.dump(recent, open(rec_p, 'w', encoding='utf-8'), ensure_ascii=False)
        except Exception:
            pass
        try:
            dur = float(subprocess.run([ff.replace('ffmpeg', 'ffprobe') if 'ffmpeg' in os.path.basename(ff) and _sh.which('ffprobe') else 'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', pick], capture_output=True, text=True, timeout=30).stdout.strip() or 0)
        except Exception:
            dur = 0
        start = round(_r.uniform(0, max(0.0, dur - seconds - 1.5)), 2) if dur > seconds + 2 else 0
        cmd += ['-ss', str(start), '-i', pick, '-filter:a', f'afade=t=in:d=0.5,afade=t=out:st={seconds - 1}:d=1,volume=0.8', '-c:a', 'aac', '-b:a', '128k']
    cmd += ['-vf', vf, '-t', str(seconds), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-movflags', '+faststart']
    if music:
        cmd += ['-shortest']
    cmd += [tmp]
    try:
        subprocess.run(cmd, check=True, timeout=180)
        os.replace(tmp, out)
        return out
    except Exception as e:
        print('reel skipped:', str(e)[:120])
        if os.path.exists(tmp):
            os.remove(tmp)
        return None


def cleanup(days=75):
    """remove generated files older than N days (log date) so the repo stays small"""
    try:
        log = json.load(open(LOG, encoding='utf-8'))
    except Exception:
        return
    cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    keep = []
    for it in log['items']:
        if it.get('date', '9999') < cut:
            for suf in ('', ' Story.png', ' Reel.mp4'):
                f = os.path.join(OUT, it['file'] if not suf else it['file'][:-4] + suf)
                if os.path.exists(f):
                    os.remove(f)
        else:
            keep.append(it)
    log['items'] = keep
    json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def qa_qr(path):
    try:
        import cv2
        img = cv2.imread(path)
        crop = img[FOOT_Y:H, 700:W]
        return cv2.QRCodeDetector().detectAndDecode(crop)[0] == QR_URL
    except Exception as e:
        print('QR check unavailable:', e)
        return False


def file_name(c, kind, date):
    y, m = date.year, BULAN[date.month - 1]
    topic = {'scholarship': 'Beasiswa', 'promo': 'Promo', 'sponsored': 'Program', 'news': 'Info Visa',
             'accommodation': 'Akomodasi', 'jobs': 'Loker', 'marketing': 'Program'}.get(kind, 'Info')
    who = c['prov'] or CNAME.get(c['cc'], '').title()
    if kind == 'marketing' and not c['prov'] and c['cc'] == 'ANY':
        who, topic = 'Pricelist', ' '.join(c['head'].title().split()[:3])
    nm = re.sub(r'[^A-Za-z0-9 ]', '', f"Talented {who} {topic} {m} {y}")
    return re.sub(r'\s+', ' ', nm).strip()


def make_card(kind, title, key, sub=None, country=None, provider=None, spec=None):
    from social_photos import get_photo
    os.makedirs(OUT, exist_ok=True)
    c = derive(kind, title, sub, country, provider, spec)
    sig = hashlib.sha1(json.dumps([kind, title, sub, provider, spec], ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:12]
    lay, pal, log, known = pick_style(key, bool(c['hero']), bool(c['dl']))
    set_palette(pal)
    sty = set_style(key)
    if lay == 'D' and not c['hero']:
        lay = 'B'
    if known:
        rec = next(i for i in log['items'] if i.get('key') == key)
        p = os.path.join(OUT, rec['file'])
        # pengaman 24/11/2026 (poster CIHE tertimpa caption CDU): kartu lama hanya dipakai ulang bila isinya sama
        if os.path.exists(p) and rec.get('v') in (9, 10) and rec.get('sig', sig) == sig:
            if not os.path.exists(p[:-4] + ' Story.png'):
                try:
                    make_reel(make_story(p))
                except Exception as e:
                    print('story/reel skipped:', str(e)[:120])
            if 'sig' not in rec:
                rec['sig'] = sig
                json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            return BASE + urllib.parse.quote(rec['file'])
    # quality gate (owner 19/11/2026: 'lebih profesional, lebih natural'): only REAL photos of people/campus -
    # provider brochure photos, or Talented's own photos (social/library/talented-umum) for general posts.
    photo, credit = get_photo(country or 'ANY', key, provider) if provider else (None, None)
    topic_ok = False
    if not (credit and 'Wikimedia' not in credit) and kind == 'promo' and (spec or {}).get('topic') \
            and int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10 < 7:
        # promo jurusan tanpa foto brosur: 70% foto topik bidang/kota/kampus supaya gambar bervariasi (pemilik 23/11/2026)
        p_, c_ = get_photo(country or 'ANY', key, 'Topik ' + spec['topic'])
        if p_ is not None:
            photo, credit, topic_ok = p_, c_, True
    from social_photos import code as _ccode
    if not topic_ok and not (credit and 'Wikimedia' not in credit):
        # foto umum Talented (booth/banner 'Study in Australia') hanya untuk konten AU/NZ/umum - QA 24/11/2026:
        # beasiswa Belanda/Tiongkok/Irlandia tampil dengan banner Australia
        if _ccode(country) in ('AU', 'NZ', 'ANY') or kind not in ('scholarship', 'news'):
            photo, credit = get_photo(country or 'ANY', key, 'Talented Umum')
        else:
            photo, credit = None, None
        if not (credit and 'Wikimedia' not in credit) and kind in ('news', 'scholarship', 'promo'):
            # topic photo (curated CC0/PD/CC BY, no lettering) - owner 20/11/2026; fallback: typography card.
            # Scholarships/promos must post on the day they open (owner 20/11/2026), so they never wait for a provider photo.
            photo, credit = get_photo(country or 'ANY', key, 'Topik ' + ((spec or {}).get('topic') or {'news': 'visa', 'scholarship': 'school', 'promo': 'fees'}[kind]))
            if photo is None:
                photo, credit, lay = None, None, 'T'
        elif not (credit and 'Wikimedia' not in credit) and (spec or {}).get('topic'):
            photo, credit = get_photo(country or 'ANY', key, 'Topik ' + spec['topic'])
            if photo is None:
                need_photo('Topik ' + spec['topic'], key); return None
        elif not (credit and 'Wikimedia' not in credit):
            need_photo(provider or ('Talented Umum (' + kind + ')'), key)
            print('held (no real photo yet):', provider or kind)
            return None
        if not (credit and 'Wikimedia' in credit):
            credit = None  # foto sendiri Talented: tanpa kredit; foto CC BY tetap dikreditkan di caption
    if lay in NEED_PHOTO and photo is None:
        lay = 'H'
    if lay == 'J' and photo is not None and provider:
        p2, c2 = get_photo(country or 'ANY', key + '#2', provider)
        if p2 is not None and c2 and 'Wikimedia' not in c2 and p2.resize((16, 16)).tobytes() != photo.resize((16, 16)).tobytes():
            photo = [photo, p2]
    lg = (spec or {}).get('logo')
    STYLE['logo_big'] = bool(lg)
    im = render(c, lay, pal, photo, os.path.join(ROOT, lg) if lg and os.path.exists(os.path.join(ROOT, lg)) else find_logo(provider))
    today = datetime.date.today()
    base = file_name(c, kind, today)
    used = {i['file'] for i in log['items'] if i.get('key') != key}
    name, n = base + '.png', 2
    while name in used:
        name = f'{base} {n}.png'; n += 1
    path = os.path.join(OUT, name)
    im.save(path, optimize=True)
    if not qa_qr(path):
        print('QA failed (QR):', name); os.remove(path); return None
    try:
        sp = make_story(path)
        make_reel(sp)
    except Exception as e:
        print('story/reel skipped:', str(e)[:120])
    rec = {"no": len(log['items']) + 1 if not known else None, "date": today.isoformat(), "key": key, "file": name,
           "provider": c['prov'] or '-', "layout": lay, "palette": pal, "format": "Feed 4:5",
           "layout_name": LAYOUT_NAMES.get(lay), "photo": (credit or 'tanpa foto'), "v": 10, "credit": credit,
           "font": sty['font'], "deco": sty['deco'], "cta": sty['cta'], "sig": sig,
           "rendered_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec='seconds')}
    if known:
        for i in log['items']:
            if i.get('key') == key:
                rec['no'] = i.get('no'); i.update(rec)
    else:
        log['items'].append(rec)
    log['items'] = log['items'][-300:]
    json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return BASE + urllib.parse.quote(name)


def need_photo(provider, key):
    """list of providers whose posts wait for real brochure photos (reported to the owner)"""
    p = os.path.join(ROOT, 'data', 'social-need-photo.json')
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        d = {"note": "Postingan provider ini ditahan karena belum ada foto asli (brosur/foto sendiri). Kirim brosur ke chat Claude: 'masukkan ke library sosmed'.", "providers": {}}
    k = provider or '-'
    d['providers'].setdefault(k, [])
    if key not in d['providers'][k]:
        d['providers'][k].append(key)
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def credit_for(key):
    try:
        for i in json.load(open(LOG, encoding='utf-8'))['items']:
            if i.get('key') == key:
                return i.get('credit')
    except Exception:
        pass
    return None
