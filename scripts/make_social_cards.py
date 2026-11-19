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
    foot = spec.get('footnote') or ('*Syarat & ketentuan berlaku.' if kind != 'news' else '*Sumber resmi pemerintah.')
    return {"t": t, "dl": dl, "hero": hero, "head": head, "info": info[:3], "price": spec.get('price'),
            "unit": spec.get('unit'), "foot": foot, "cc": cc, "prov": prov}


LAYOUTS = {  # name: (needs hero, needs deadline, allowed palettes)
    'A': (True, False, ['P1', 'P3']), 'B': (False, False, ['P6']), 'C': (False, False, ['P1', 'P2', 'P3', 'P5']),
    'D': (True, False, ['P1', 'P3']), 'E': (False, False, ['P2', 'P4', 'P5']), 'F': (False, False, ['P1', 'P3']),
    'G': (False, True, ['P1', 'P2', 'P3', 'P5']), 'H': (False, False, ['P1', 'P3', 'P2', 'P4']),
}
LAYOUT_NAMES = {'A': 'Foto kanan diagonal', 'B': 'Foto penuh + panel', 'C': 'Foto atas diagonal', 'D': 'Tipografi + foto miring',
                'E': 'Majalah/editorial', 'F': 'Tiket boarding pass', 'G': 'Kalender deadline', 'H': 'Tipografi bertumpuk + cap'}


def pick_style(key, has_hero, has_dl=False):
    """random rolling (seeded by key) across 8 layouts; never repeats the last 3 layouts; P1 max 2 in a row"""
    try:
        log = json.load(open(LOG, encoding='utf-8'))
    except Exception:
        log = {"note": "LOG desain sosmed otomatis (Panduan: layout/palet bergilir).", "items": []}
    for it in log['items']:
        if it.get('key') == key and it.get('v') == 8:
            return it['layout'], it['palette'], log, True
    rnd = random.Random(hashlib.sha256(key.encode()).hexdigest())
    last = [i for i in log['items'] if i.get('key') != key][-3:]
    recent = {i['layout'] for i in last}
    ok = [l for l, (nh, nd, _) in LAYOUTS.items() if (has_hero or not nh) and (has_dl or not nd)]
    pool = [l for l in ok if l not in recent] or ok
    if has_dl and 'G' in pool and rnd.random() < 0.5:
        lay = 'G'
    else:
        lay = rnd.choice(pool)
    pals = list(LAYOUTS[lay][2])
    p1run = len(last) >= 2 and all(i['palette'] in ('P1', 'P6') for i in last[-2:])
    if p1run and len([p for p in pals if p not in ('P1', 'P6')]):
        pals = [p for p in pals if p not in ('P1', 'P6')]
    elif 'P1' in pals and rnd.random() < 0.5:
        pals = ['P1']  # signature colour about half of the time
    if last and len(pals) > 1 and last[-1]['palette'] in pals:
        pals.remove(last[-1]['palette'])
    return lay, rnd.choice(pals), log, False


# ---------------------------------------------------------------- layouts
def render(c, lay, pal, photo, logo_path):
    if lay in ('E', 'F', 'G', 'H'):
        return render_extra(c, lay, pal, photo, logo_path)
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
            d.rectangle([bx0, by0, bx0 + hw + 50, by0 + hh + 50], fill=PAL['P1'][2])
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
    im = Image.new('RGBA', (W, H), bg + (255,))
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
        fr = fit_font(d, 'INDONESIA → ' + dest, anton, cut - x0 - 70, 64, 34)
        draw_t(d, (x0 + 34, y0 + 70), 'INDONESIA → ' + dest, fr, ink)
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


def make_story(png_path):
    """1080x1920 story: poster centered on brand colour, flat bands (no AI, no gradients)"""
    po = Image.open(png_path).convert('RGB')
    st = Image.new('RGB', (1080, 1920), GREEN)
    d = ImageDraw.Draw(st)
    st.paste(po, (0, 285))
    f1 = mont(34, 'ExtraBold')
    t1 = 'INFO TERBARU DARI TALENTED'
    draw_t(d, ((1080 - tw(d, t1, f1)) // 2, 120), t1, f1, PAL['P1'][2])
    d.rectangle([440, 185, 640, 191], fill=PAL['P1'][2])
    f2 = mont(36, 'ExtraBold')
    t2 = 'Scan QR atau klik link di bio'
    draw_t(d, ((1080 - tw(d, t2, f2)) // 2, 1700), t2, f2, (255, 255, 255))
    f3 = mont(26, 'Bold')
    t3 = 'linktr.ee/talentededucationgroup'
    draw_t(d, ((1080 - tw(d, t3, f3)) // 2, 1770), t3, f3, PAL['P1'][2])
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
    vf = (f"scale=1296:2304,zoompan=z='min(1+0.0004*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={seconds * 30}:s=1080x1920:fps=30,fade=t=in:st=0:d=0.4,format=yuv420p")
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
        pick = music[int(hashlib.sha256(story_path.encode()).hexdigest(), 16) % len(music)]
        cmd += ['-i', pick, '-filter:a', f'afade=t=in:d=0.5,afade=t=out:st={seconds - 1}:d=1,volume=0.8', '-c:a', 'aac', '-b:a', '128k']
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
    nm = re.sub(r'[^A-Za-z0-9 ]', '', f"Talented {who} {topic} {m} {y}")
    return re.sub(r'\s+', ' ', nm).strip()


def make_card(kind, title, key, sub=None, country=None, provider=None, spec=None):
    from social_photos import get_photo
    os.makedirs(OUT, exist_ok=True)
    c = derive(kind, title, sub, country, provider, spec)
    lay, pal, log, known = pick_style(key, bool(c['hero']), bool(c['dl']))
    if lay == 'D' and not c['hero']:
        lay = 'B'
    if known:
        rec = next(i for i in log['items'] if i.get('key') == key)
        p = os.path.join(OUT, rec['file'])
        if os.path.exists(p) and rec.get('v') == 8:
            if not os.path.exists(p[:-4] + ' Story.png'):
                try:
                    make_reel(make_story(p))
                except Exception as e:
                    print('story/reel skipped:', str(e)[:120])
            return BASE + urllib.parse.quote(rec['file'])
    # quality gate (owner 19/11/2026: 'lebih profesional, lebih natural'): only REAL photos of people/campus -
    # provider brochure photos, or Talented's own photos (social/library/talented-umum) for general posts.
    photo, credit = get_photo(country or 'ANY', key, provider) if provider else (None, None)
    if not (credit and 'Wikimedia' not in credit):
        photo, credit = get_photo(country or 'ANY', key, 'Talented Umum')
        if not (credit and 'Wikimedia' not in credit):
            need_photo(provider or ('Talented Umum (' + kind + ')'), key)
            print('held (no real photo yet):', provider or kind)
            return None
        credit = None
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
    try:
        sp = make_story(path)
        make_reel(sp)
    except Exception as e:
        print('story/reel skipped:', str(e)[:120])
    rec = {"no": len(log['items']) + 1 if not known else None, "date": today.isoformat(), "key": key, "file": name,
           "provider": c['prov'] or '-', "layout": lay, "palette": pal, "format": "Feed 4:5",
           "layout_name": LAYOUT_NAMES.get(lay), "photo": (credit or 'tanpa foto'), "v": 8, "credit": credit}
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
