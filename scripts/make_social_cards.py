#!/usr/bin/env python3
"""Poster-style 1080x1080 social cards. make_card(...) -> public URL of social/cards/<hash>.png.
Photo priority: provider brochure library > openly licensed Commons city photo > brand gradient.
Logo priority: assets/providers/<slug>.png (from brochures) > hosted partner logos (assets/sponsors)."""
import os, re, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'social', 'cards')
BASE = 'https://info.talentededucationgroup.com/social/cards/'
W = 1080
F = lambda w, s: ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', f'Poppins-{w}.ttf'), s)
GREEN, DEEP, GOLD, INK, RED = (0x14, 0x6B, 0x4A), (0x0B, 0x2E, 0x22), (0xF7, 0xC3, 0x3A), (0x10, 0x2A, 0x20), (0xE5, 0x3E, 0x45)
KIND = {"scholarship": ("BEASISWA", GOLD), "promo": ("PROMO", (0xFF, 0x8A, 0x5B)), "news": ("INFO VISA", (0x7F, 0xD6, 0xFF)),
        "sponsored": ("SPONSORED", GOLD), "jobs": ("LOKER PELAJAR", (0x9B, 0xE5, 0x8A)),
        "accommodation": ("AKOMODASI", (0xC9, 0xB6, 0xFF)), "marketing": ("STUDY ABROAD", GOLD)}
STICK = {"scholarship": "BEASISWA", "promo": "DISKON", "sponsored": "PROMO", "marketing": "SPESIAL"}
BUL = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
HL = re.compile(r'(\d{1,3}(?:[-–]\d{1,3})?%|(?:AUD|NZD|GBP|CAD|USD|EUR)\s?[\d.,]+[kK]?|GRATIS|gratis)')


def clean(t):
    t = re.sub(r'[\U0001F000-\U0001FFFF☀-➿⬀-⯿️‍]', '', t or '')
    return re.sub(r'\s+', ' ', t).strip(' :-|')


def idate(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    return f"{int(m.group(3))} {BUL[int(m.group(2)) - 1]} {m.group(1)}" if m else s


def split_title(t):
    m = re.search(r'\(?deadline\s*([0-9-]{10})\)?', t, re.I)
    dl = idate(m.group(1)) if m else None
    t = re.sub(r'\(?deadline\s*[0-9-]{10}\)?', '', t, flags=re.I)
    t = re.sub(r'^(Beasiswa dibuka|Beasiswa baru|Promo)\s*:\s*', '', t, flags=re.I)
    return clean(t), dl


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


def wrap(d, text, font, width):
    lines, cur = [], ''
    for w in text.split():
        nxt = (cur + ' ' + w).strip()
        if d.textlength(nxt, font=font) <= width:
            cur = nxt
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def fit(d, text, width, maxh, start=72, minsize=40, weight='Bold', lh=1.14):
    size = start
    while True:
        f = F(weight, size)
        ls = wrap(d, text, f, width)
        if len(ls) * size * lh <= maxh or size <= minsize:
            return f, ls[:5], size
        size -= 3


def cover(photo, w, h, fy=0.35):
    r = max(w / photo.width, h / photo.height)
    ph = photo.resize((int(photo.width * r) + 1, int(photo.height * r) + 1), Image.LANCZOS)
    l, t = (ph.width - w) // 2, int((ph.height - h) * fy)
    return ph.crop((l, t, l + w, t + h))


def shadowed(im, layer, xy, radius=14, alpha=110, off=(0, 10)):
    a = layer.split()[-1]
    sh = Image.new('RGBA', (layer.width + 4 * radius, layer.height + 4 * radius), (0, 0, 0, 0))
    m = Image.new('L', sh.size, 0)
    m.paste(a.point(lambda v: alpha if v else 0), (2 * radius, 2 * radius))
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(radius)))
    im.alpha_composite(sh, (xy[0] - 2 * radius + off[0], xy[1] - 2 * radius + off[1]))
    im.alpha_composite(layer, xy)


def logo_chip(path, h=104, pad=14):
    lg = Image.open(path).convert('RGBA')
    px = lg.convert('RGB').getpixel((2, 2))
    lg.thumbnail((int(h * 3.4), h - 2 * pad), Image.LANCZOS)
    bg = px if sum(px) < 600 else (255, 255, 255)
    chip = Image.new('RGBA', (lg.width + 2 * pad + 10, h), (0, 0, 0, 0))
    ImageDraw.Draw(chip).rounded_rectangle([0, 0, chip.width - 1, h - 1], 20, fill=bg + (255,))
    chip.alpha_composite(lg, ((chip.width - lg.width) // 2, (h - lg.height) // 2))
    return chip


def sticker(num, label, color=GOLD):
    S = 300
    st = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    pts = []
    import math
    for i in range(48):
        r = S / 2 - 4 if i % 2 == 0 else S / 2 - 22
        a = math.pi * 2 * i / 48
        pts.append((S / 2 + r * math.cos(a), S / 2 + r * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    d.ellipse([34, 34, S - 34, S - 34], outline=INK + (255,), width=3)
    size = 110
    while size > 40:
        f = F('Bold', size)
        if d.textlength(num, font=f) <= S - 90: break
        size -= 4
    tw = d.textlength(num, font=f)
    d.text(((S - tw) / 2, S / 2 - size * 0.78), num, font=f, fill=INK)
    fl = F('Bold', 30)
    lw = d.textlength(label, font=fl)
    d.text(((S - lw) / 2, S / 2 + size * 0.35), label, font=fl, fill=INK)
    return st.rotate(-10, resample=Image.BICUBIC, expand=False)


def make_card(kind, title, key, sub=None, country=None, provider=None):
    os.makedirs(OUT, exist_ok=True)
    raw = clean(title)
    h = hashlib.sha256(f'{kind}|{raw}|{sub}|{country}|{provider}|v5'.encode()).hexdigest()[:16]
    path = os.path.join(OUT, h + '.png')
    if os.path.exists(path):
        return BASE + h + '.png'
    from social_photos import get_photo
    photo, credit = get_photo(country, key, provider) if country is not None else (None, None)
    t, dl = split_title(raw)
    label, col = KIND.get(kind, KIND['marketing'])
    big = HL.search(t) if kind in STICK else None
    PH = 640
    im = Image.new('RGBA', (W, W), DEEP + (255,))
    if photo:
        im.alpha_composite(cover(photo, W, PH + 60).convert('RGBA'), (0, 0))
    else:
        g = Image.new('RGBA', (W, PH + 60), GREEN + (255,))
        gd = ImageDraw.Draw(g)
        gd.ellipse([560, -300, 1400, 540], fill=(0x1E, 0x86, 0x5E, 255))
        gd.ellipse([-200, 300, 400, 900], fill=(0x10, 0x55, 0x3C, 255))
        im.alpha_composite(g)
    top = Image.new('RGBA', (W, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    for y in range(200):
        td.line([(0, y), (W, y)], fill=(0, 0, 0, int(120 * (1 - y / 200))))
    im.alpha_composite(top)
    # bottom panel
    panel = Image.new('RGBA', (W, W - PH + 40), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([0, 0, W, panel.height + 60], 46, fill=DEEP + (255,))
    pd.rectangle([0, 0, 14, panel.height], fill=GOLD + (255,)) if False else None
    shadowed(im, panel, (0, PH - 40), radius=18, alpha=120, off=(0, -6))
    d = ImageDraw.Draw(im)
    # gold accent bar
    d.rounded_rectangle([60, PH - 6, 200, PH + 4], 5, fill=GOLD)
    # kind chip
    fl = F('Bold', 28)
    lw = d.textlength(label, font=fl)
    d.rounded_rectangle([60, PH + 22, 60 + lw + 44, PH + 74], 26, fill=col)
    d.text((82, PH + 28), label, font=fl, fill=INK)
    if dl:
        fd = F('Bold', 28)
        tx = f'DEADLINE {dl}'
        x0 = 60 + lw + 60
        d.rounded_rectangle([x0, PH + 22, x0 + d.textlength(tx, font=fd) + 44, PH + 74], 26, fill=RED)
        d.text((x0 + 22, PH + 28), tx, font=fd, fill=(255, 255, 255))
    # headline (numbers in gold)
    maxw = W - 120 - (0 if not big else 0)
    ft, ls, size = fit(d, t, maxw, 185, start=64, minsize=38)
    y = PH + 96
    for ln in ls:
        x = 60
        for part in HL.split(ln):
            if not part: continue
            d.text((x, y), part, font=ft, fill=GOLD if HL.fullmatch(part) else (255, 255, 255))
            x += d.textlength(part, font=ft)
        y += int(size * 1.14)
    if sub:
        d.text((60, min(y + 4, 900)), clean(sub)[:60], font=F('Medium', 28), fill=(0xC8, 0xE6, 0xD6))
    # CTA row
    yb = 950
    f1 = F('Bold', 32)
    cta = 'Konsultasi GRATIS'
    bw = int(d.textlength(cta, font=f1)) + 100
    d.rounded_rectangle([60, yb, 60 + bw, yb + 74], 37, fill=GOLD)
    d.text((88, yb + 15), cta, font=f1, fill=INK)
    d.polygon([(60 + bw - 46, yb + 24), (60 + bw - 46, yb + 50), (60 + bw - 24, yb + 37)], fill=INK)
    f2 = F('Medium', 23)
    u = 'pricelist.talentededucationgroup.com'
    d.text((W - 60 - d.textlength(u, font=f2), yb + 24), u, font=f2, fill=(220, 240, 230))
    # logos on photo
    shadowed(im, logo_chip(os.path.join(ROOT, 'mocktest', 'logo.png'), 104), (48, 40))
    lp = find_logo(provider)
    if lp:
        ch = logo_chip(lp, 104)
        shadowed(im, ch, (W - 48 - ch.width, 40))
    # sticker
    if big:
        st = sticker(big.group(1).upper(), STICK.get(kind, 'SPESIAL'))
        shadowed(im, st, (W - 330, PH - 250), radius=16, alpha=120)
    d = ImageDraw.Draw(im)
    if credit:
        fcr = F('Medium', 16)
        d.text((60, PH - 70), credit, font=fcr, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    im.convert('RGB').save(path, optimize=True)
    return BASE + h + '.png'
