#!/usr/bin/env python3
"""Eye-catching 1080x1080 social cards. make_card(...) -> public URL of social/cards/<hash>.png.
Template 'bold' (big highlighted number) for scholarships/promos with a % or amount, else 'hero'
(full-bleed photo). Provider logo (hosted partner logos in assets/sponsors) shown when known."""
import os, re, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'social', 'cards')
BASE = 'https://info.talentededucationgroup.com/social/cards/'
W = 1080
F = lambda w, s: ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', f'Poppins-{w}.ttf'), s)
GREEN, DEEP, GOLD, INK = (0x14, 0x6B, 0x4A), (0x0B, 0x2E, 0x22), (0xF5, 0xC2, 0x3E), (0x10, 0x2A, 0x20)
KIND = {"scholarship": ("BEASISWA", GOLD), "promo": ("PROMO", (0xFF, 0x8A, 0x5B)),
        "news": ("INFO VISA", (0x7F, 0xD6, 0xFF)), "sponsored": ("SPONSORED", GOLD),
        "jobs": ("LOKER PELAJAR", (0x9B, 0xE5, 0x8A)), "accommodation": ("AKOMODASI", (0xC9, 0xB6, 0xFF)),
        "marketing": ("TALENTED", GOLD)}
BUL = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
HL = re.compile(r'(\d{1,3}(?:[-–]\d{1,3})?%|AUD\s?[\d.,]+|NZD\s?[\d.,]+|GBP\s?[\d.,]+|CAD\s?[\d.,]+|USD\s?[\d.,]+|gratis|GRATIS|full|penuh)', re.I)


def clean(t):
    t = re.sub(r'[\U0001F000-\U0001FFFF☀-➿⬀-⯿️‍]', '', t or '')
    return re.sub(r'\s+', ' ', t).strip(' :-|')


def idate(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    return f"{int(m.group(3))} {BUL[int(m.group(2)) - 1]} {m.group(1)}" if m else s


def split_title(t):
    """-> (title without deadline, deadline str or None)"""
    m = re.search(r'\(?deadline\s*([0-9-]{10})\)?', t, re.I)
    dl = idate(m.group(1)) if m else None
    t = re.sub(r'\(?deadline\s*[0-9-]{10}\)?', '', t, flags=re.I)
    t = re.sub(r'^(Beasiswa dibuka|Beasiswa baru|Promo)\s*:\s*', '', t, flags=re.I)
    return clean(t), dl


def find_logo(provider):
    if not provider:
        return None
    try:
        b = json.load(open(os.path.join(ROOT, 'data', 'banners.json'), encoding='utf-8'))
    except Exception:
        return None
    pl = provider.lower()
    for it in b.get('items', []):
        src = ((it.get('logo') or {}).get('src') or '')
        m = re.search(r'/assets/sponsors/([a-z0-9-]+)\.(webp|png|jpg)$', src)
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


def fit(d, text, width, maxh, start=84, minsize=44, weight='Bold', lh=1.15):
    size = start
    while True:
        f = F(weight, size)
        ls = wrap(d, text, f, width)
        if len(ls) * size * lh <= maxh or size <= minsize:
            return f, ls[:6], size
        size -= 4


def draw_rich(d, x, y, line, font, base, hi):
    """draw a line with soft shadow, highlighting money/percent tokens"""
    sx = x
    for part in HL.split(line):
        if part:
            d.text((sx + 3, y + 4), part, font=font, fill=(0, 0, 0, 140)); sx += d.textlength(part, font=font)
    for part in HL.split(line):
        if not part:
            continue
        col = hi if HL.fullmatch(part) else base
        d.text((x, y), part, font=font, fill=col)
        x += d.textlength(part, font=font)


def cover(photo, w, h):
    r = max(w / photo.width, h / photo.height)
    ph = photo.resize((int(photo.width * r) + 1, int(photo.height * r) + 1), Image.LANCZOS)
    l, t = (ph.width - w) // 2, (ph.height - h) // 2
    return ph.crop((l, t, l + w, t + h))


def pill_logo(im, path, box_h, xy, anchor='tl', pad=16):
    lg = Image.open(path).convert('RGBA')
    lg.thumbnail((int(box_h * 3.2), box_h - 2 * pad), Image.LANCZOS)
    card = Image.new('RGBA', (lg.width + 2 * pad + 8, box_h), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, card.width - 1, box_h - 1], 22, fill=(255, 255, 255, 255))
    card.alpha_composite(lg, ((card.width - lg.width) // 2, (box_h - lg.height) // 2))
    x, y = xy
    if anchor == 'tr':
        x -= card.width
    sh = Image.new('RGBA', (card.width + 40, card.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, card.width + 20, card.height + 20], 22, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    im.alpha_composite(sh, (x - 20, y - 20))
    im.alpha_composite(card, (x, y))
    return card.width


def gradient(w, h, top, bottom):
    g = Image.new('RGBA', (w, h))
    gd = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        gd.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4)))
    return g


def footer(im, d, y=944):
    f1 = F('Bold', 34)
    cta = 'Konsultasi GRATIS'
    bw = int(d.textlength(cta, font=f1)) + 110
    d.rounded_rectangle([60, y, 60 + bw, y + 78], 39, fill=GOLD)
    d.text((92, y + 17), cta, font=f1, fill=INK)
    d.polygon([(60 + bw - 52, y + 26), (60 + bw - 52, y + 52), (60 + bw - 30, y + 39)], fill=INK)
    f2 = F('Medium', 24)
    u = 'pricelist.talentededucationgroup.com'
    d.text((W - 60 - d.textlength(u, font=f2), y + 26), u, font=f2, fill=(255, 255, 255))


def make_card(kind, title, key, sub=None, country=None, provider=None):
    os.makedirs(OUT, exist_ok=True)
    raw = clean(title)
    h = hashlib.sha256(f'{kind}|{raw}|{sub}|{country}|{provider}|v4'.encode()).hexdigest()[:16]
    path = os.path.join(OUT, h + '.png')
    if os.path.exists(path):
        return BASE + h + '.png'
    from social_photos import get_photo
    photo, credit = get_photo(country, key, provider) if country is not None else (None, None)
    t, dl = split_title(raw)
    label, col = KIND.get(kind, KIND['marketing'])
    logo = find_logo(provider)
    big = HL.search(t) if kind in ('scholarship', 'promo', 'sponsored', 'marketing') else None
    im = Image.new('RGBA', (W, W), DEEP + (255,))
    d = ImageDraw.Draw(im)

    if big:  # ---------- BOLD template: photo right, gold panel left with giant number
        if photo:
            im.alpha_composite(cover(photo, W, W).convert('RGBA'))
            im.alpha_composite(gradient(W, W, (11, 46, 34, 120), (11, 46, 34, 235)))
        else:
            im.alpha_composite(gradient(W, W, GREEN + (255,), DEEP + (255,)))
        d = ImageDraw.Draw(im)
        panel = Image.new('RGBA', (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(panel).polygon([(0, 150), (700, 150), (600, 560), (0, 560)], fill=GOLD + (255,))
        im.alpha_composite(panel)
        num = big.group(1).upper().replace(' ', ' ')
        fnum, _, _ = fit(d, num, 540, 240, start=230, minsize=90)
        d.text((60, 175), num, font=fnum, fill=INK)
        fl = F('Bold', 40)
        lab2 = {'scholarship': 'BEASISWA', 'promo': 'DISKON', 'sponsored': 'PROMO'}.get(kind, 'SPESIAL')
        d.text((66, 470), lab2, font=fl, fill=INK)
        rest = clean(HL.sub('', t, count=1).replace('hingga', '').replace('  ', ' '))
        rest = re.sub(r'\s*-\s*$|^\s*-\s*', '', rest)
        ft, ls, size = fit(d, rest, W - 130, 250, start=62, minsize=40)
        y = 600
        for ln in ls:
            draw_rich(d, 60, y, ln, ft, (255, 255, 255), GOLD); y += int(size * 1.15)
    else:  # ---------- HERO template: full-bleed photo, bottom gradient, big title
        if photo:
            im.alpha_composite(cover(photo, W, W).convert('RGBA'))
        else:
            im.alpha_composite(gradient(W, W, GREEN + (255,), DEEP + (255,)))
            ImageDraw.Draw(im).ellipse([620, -260, 1340, 460], fill=(0x1E, 0x86, 0x5E, 255))
        im.alpha_composite(gradient(W, 160, (0, 0, 0, 110), (0, 0, 0, 0)), (0, 0))
        im.alpha_composite(gradient(W, 700, (11, 46, 34, 0), (11, 46, 34, 255)), (0, 380))
        im.alpha_composite(gradient(W, 600, (11, 46, 34, 0), (11, 46, 34, 110)), (0, 480))
        d = ImageDraw.Draw(im)
        fl = F('Bold', 34)
        lw = d.textlength(label, font=fl)
        d.rounded_rectangle([60, 470, 60 + lw + 52, 532], 31, fill=col)
        d.text((86, 476), label, font=fl, fill=INK)
        ft, ls, size = fit(d, t, W - 120, 330, start=84, minsize=46)
        y = 900 - 40 - len(ls) * int(size * 1.15) if dl else 900 - len(ls) * int(size * 1.15)
        y = max(y, 552)
        for ln in ls:
            draw_rich(d, 60, y, ln, ft, (255, 255, 255), GOLD); y += int(size * 1.15)
    d = ImageDraw.Draw(im)
    # deadline chip
    if dl:
        fd = F('Bold', 30)
        txt = f'DEADLINE  {dl}'
        tw = d.textlength(txt, font=fd)
        y0 = 868
        d.rounded_rectangle([60, y0, 60 + tw + 50, y0 + 56], 28, fill=(0xE5, 0x48, 0x4D))
        d.text((85, y0 + 8), txt, font=fd, fill=(255, 255, 255))
    if sub:
        d.text((60, 880 if not dl else 830), clean(sub)[:60], font=F('Medium', 30), fill=(0xD8, 0xF0, 0xE4))
    # logos
    pill_logo(im, os.path.join(ROOT, 'mocktest', 'logo.png'), 110, (60, 40))
    if logo:
        pill_logo(im, logo, 110, (W - 60, 40), anchor='tr', pad=18)
    d = ImageDraw.Draw(im)
    if credit:
        fcr = F('Medium', 17)
        cw = d.textlength(credit, font=fcr)
        d.text((W - 60 - cw, 1040), credit, font=fcr, fill=(205, 225, 215))
    footer(im, d)
    im.convert('RGB').save(path, optimize=True)
    return BASE + h + '.png'
