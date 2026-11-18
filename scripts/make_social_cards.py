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
}
GREEN, PANEL2 = (0x17, 0x3F, 0x35), (0x21, 0x58, 0x4A)
CNAME = {'AU': 'AUSTRALIA', 'NZ': 'SELANDIA BARU', 'GB': 'INGGRIS', 'CA': 'KANADA', 'US': 'AMERIKA', 'IE': 'IRLANDIA',
         'DE': 'JERMAN', 'FR': 'PRANCIS', 'NL': 'BELANDA', 'JP': 'JEPANG', 'KR': 'KOREA', 'SG': 'SINGAPURA', 'TW': 'TAIWAN',
         'CN': 'TIONGKOK', 'SE': 'SWEDIA', 'HU': 'HONGARIA', 'TR': 'TURKI', 'BN': 'BRUNEI', 'ES': 'SPANYOL', 'CH': 'SWISS',
         'MY': 'MALAYSIA', 'EU': 'EROPA', 'ANY': 'LUAR NEGERI'}
BUL = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
HL = re.compile(r'(\d{1,3}(?:[-–]\d{1,3})?%|(?:AUD|NZD|GBP|CAD|USD|EUR)\s?[\d.,]+)')


def anton(s):
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
        xml = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
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


def footer_and_banner(canvas, dark, accent):
    ft = Image.open(BR('footer-hijau.png' if dark else 'footer-terang.png')).convert('RGBA')
    canvas.alpha_composite(ft, (0, FOOT_Y))
    bn = Image.open(BR('banner-app.png')).convert('RGBA')
    bw = 960
    bn = bn.resize((bw, int(bn.height * bw / bn.width)), Image.LANCZOS)
    canvas.alpha_composite(bn, ((W - bw) // 2, 916 - bn.height))
    return 916 - bn.height  # top of banner


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
            head = 'LOKER PART-TIME PELAJAR'
        elif kind == 'news':
            head = 'UPDATE VISA PELAJAR ' + (cn if cc != 'ANY' else '')
        else:
            head = ' '.join(t.split()[:5])
    head = ' '.join(head.upper().split()[:6])
    info = list(spec.get('info') or [])
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
    foot = spec.get('footnote') or ('Syarat berlaku. Info lengkap & biaya di caption.' if kind != 'news'
                                     else 'Sumber resmi pemerintah. Detail di caption.')
    return {"t": t, "dl": dl, "hero": hero, "head": head, "info": info[:3], "price": spec.get('price'),
            "unit": spec.get('unit'), "foot": foot, "cc": cc, "prov": prov}


def pick_style(key, has_hero):
    try:
        log = json.load(open(LOG, encoding='utf-8'))
    except Exception:
        log = {"note": "LOG desain sosmed otomatis (Panduan: layout/palet bergilir).", "items": []}
    for it in log['items']:
        if it.get('key') == key:
            return it['layout'], it['palette'], log, True
    last = log['items'][-3:]
    lays = ['A', 'B', 'C', 'D'] if has_hero else ['B', 'C']
    prev = last[-1]['layout'] if last else None
    order = ['A', 'B', 'C', 'D']
    start = (order.index(prev) + 1) if prev in order else 0
    lay = next(order[(start + i) % 4] for i in range(4) if order[(start + i) % 4] in lays and order[(start + i) % 4] != prev)
    p1run = len(last) >= 2 and all(i['palette'] == 'P1' for i in last[-2:])
    if lay == 'B':
        pal = 'P6' if p1run else 'P1'
    elif p1run:
        others = ['P3', 'P2', 'P5', 'P4']
        pal = others[len(log['items']) % 4]
    else:
        pal = 'P1'
    return lay, pal, log, False


# ---------------------------------------------------------------- layouts
def render(c, lay, pal, photo, logo_path):
    bg, tx, ac, dark = PAL[pal]
    if lay == 'B':
        dark = True  # text sits on the solid green panel
    im = Image.new('RGBA', (W, H), bg + (255,))
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
        d.rectangle([0, 434, 760, 440], fill=PAL['P1'][2])
        tx, ac = (255, 255, 255), PAL['P1'][2]
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
        fi = mont(26, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 450, 2 if i == 0 else 1):
                if y + 32 > limit - 30: break
                _, h_ = draw_t(d, (x, y), l2, fi, tx if i else ac); y += h_ + 10
        draw_t(d, (x, min(y + 6, limit - 20)), c['foot'], mont(17, 'Medium'), tx)
    elif lay == 'B':
        if c['hero']:
            fhero = fit_font(d, c['hero'], anton, 300, 170, 70)
            hw, hh = tw(d, c['hero'], fhero), th(d, c['hero'], fhero)
            bx0, by0 = 1080 - M - hw - 50, 250
            d.rectangle([bx0, by0, bx0 + hw + 50, by0 + hh + 50], fill=PAL['P1'][2])
            draw_t(d, (bx0 + 25, by0 + 25), c['hero'], fhero, GREEN)
        x, y, maxw = M, 470, 660
        fh = fit_font(d, c['head'], anton, maxw, 66, 40)
        for ln in wrap(d, c['head'], fh, maxw, 2):
            _, h_ = draw_t(d, (x, y), ln, fh, tx); y += h_ + 10
        y += 14
        y += price_line(d, x, y, c['price'], c['unit'], ac, 40, 640) + (8 if c['price'] else 0)
        fi = mont(24, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 650, 1):
                if y + 28 > limit - 26: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 10
        draw_t(d, (x, min(y + 4, limit - 18)), c['foot'], mont(16, 'Medium'), tx)
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
        draw_t(d, (M, limit - 18), c['foot'], mont(16, 'Medium'), tx)
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
        fi = mont(23, 'Bold')
        for i, ln in enumerate(c['info'][:2]):
            for l2 in wrap(d, ln, fi, 600, 1):
                if y + 28 > limit - 24: break
                _, h_ = draw_t(d, (x, y), l2, fi, ac if i == 0 else tx); y += h_ + 8
        draw_t(d, (x, min(y + 4, limit - 18)), c['foot'], mont(16, 'Medium'), tx)
    return im.convert('RGB')


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
    nm = re.sub(r'[^A-Za-z0-9 ]', '', f"Talented {who} {topic} {m} {y}")
    return re.sub(r'\s+', ' ', nm).strip()


def make_card(kind, title, key, sub=None, country=None, provider=None, spec=None):
    from social_photos import get_photo
    os.makedirs(OUT, exist_ok=True)
    c = derive(kind, title, sub, country, provider, spec)
    lay, pal, log, known = pick_style(key, bool(c['hero']))
    if lay == 'D' and not c['hero']:
        lay = 'B'
    if known:
        rec = next(i for i in log['items'] if i.get('key') == key)
        p = os.path.join(OUT, rec['file'])
        if os.path.exists(p) and rec.get('v') == 7:
            return BASE + urllib.parse.quote(rec['file'])
    photo, credit = get_photo(country or 'ANY', key, provider)
    im = render(c, lay, pal, photo, find_logo(provider))
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
    rec = {"no": len(log['items']) + 1 if not known else None, "date": today.isoformat(), "key": key, "file": name,
           "provider": c['prov'] or '-', "layout": lay, "palette": pal, "format": "Feed 4:5",
           "photo": (credit or 'tanpa foto'), "v": 7, "credit": credit}
    if known:
        for i in log['items']:
            if i.get('key') == key:
                rec['no'] = i.get('no'); i.update(rec)
    else:
        log['items'].append(rec)
    log['items'] = log['items'][-300:]
    json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return BASE + urllib.parse.quote(name)


def credit_for(key):
    try:
        for i in json.load(open(LOG, encoding='utf-8'))['items']:
            if i.get('key') == key:
                return i.get('credit')
    except Exception:
        pass
    return None
