#!/usr/bin/env python3
"""Make 1080x1080 branded image cards for social posts (no third-party photos needed).
make_card(kind, title, key) -> public URL of social/cards/<hash>.png (created if missing)."""
import os, re, hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'social', 'cards')
BASE = 'https://info.talentededucationgroup.com/social/cards/'
F = lambda w, s: ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', f'Poppins-{w}.ttf'), s)
KIND = {"scholarship": ("BEASISWA", (0xF2, 0xC1, 0x4E)), "promo": ("PROMO", (0xFF, 0x7A, 0x59)),
        "news": ("INFO VISA & IMIGRASI", (0x7F, 0xD6, 0xFF)), "sponsored": ("SPONSORED", (0xF2, 0xC1, 0x4E)),
        "jobs": ("LOWONGAN KERJA PELAJAR", (0x9B, 0xE5, 0x8A)), "accommodation": ("AKOMODASI PELAJAR", (0xC9, 0xB6, 0xFF)),
        "marketing": ("TALENTED EDUCATION GROUP", (0xF2, 0xC1, 0x4E))}
TOP, BOT = (0x0F, 0x3D, 0x2E), (0x14, 0x6B, 0x4A)


def clean(t):
    t = re.sub(r'[\U0001F000-\U0001FFFF☀-➿️]', '', t or '')
    return re.sub(r'\s+', ' ', t).strip(' :-|')


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


def make_card(kind, title, key, sub=None):
    os.makedirs(OUT, exist_ok=True)
    title = clean(title)
    h = hashlib.sha256(f'{kind}|{title}|{sub}|v1'.encode()).hexdigest()[:16]
    path = os.path.join(OUT, h + '.png')
    if os.path.exists(path):
        return BASE + h + '.png'
    W = 1080
    im = Image.new('RGB', (W, W))
    d = ImageDraw.Draw(im)
    for y in range(W):
        t = y / W
        d.line([(0, y), (W, y)], fill=tuple(int(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)))
    d.ellipse([700, -220, 1300, 380], fill=(0x1B, 0x7F, 0x58))
    d.ellipse([-260, 820, 260, 1340], fill=(0x12, 0x55, 0x3D))
    try:
        lg = Image.open(os.path.join(ROOT, 'mocktest', 'logo.png')).convert('RGB')
        lg = lg.crop((0, 0, int(lg.width * 0.9), lg.height))
        lg.thumbnail((170, 128))
        card = Image.new('RGB', (lg.width + 28, lg.height + 28), 'white')
        card.paste(lg, (14, 14))
        im.paste(card, (72, 64))
    except Exception:
        pass
    label, col = KIND.get(kind, KIND['marketing'])
    fl = F('Bold', 34)
    lw = d.textlength(label, font=fl)
    d.rounded_rectangle([72, 300, 72 + lw + 56, 366], 33, fill=col)
    d.text((100, 307), label, font=fl, fill=(0x10, 0x2A, 0x20))
    size = 76
    while size > 44:
        ft = F('Bold', size)
        lines = wrap(d, title, ft, W - 150)
        if len(lines) * size * 1.22 <= 430:
            break
        size -= 4
    lines = lines[:7]
    y = 400
    for ln in lines:
        d.text((72, y), ln, font=ft, fill='white'); y += int(size * 1.22)
    if sub:
        d.text((72, y + 16), clean(sub)[:60], font=F('Medium', 34), fill=(0xD8, 0xF0, 0xE4))
    d.rounded_rectangle([72, 930, W - 72, 1010], 40, fill='white')
    cta = 'Info & konsultasi gratis  ->  pricelist.talentededucationgroup.com'
    fc = F('Medium', 30)
    while d.textlength(cta, font=fc) > W - 200: fc = F('Medium', fc.size - 1)
    d.text(((W - d.textlength(cta, font=fc)) / 2, 950), cta, font=fc, fill=TOP)
    im.save(path, optimize=True)
    return BASE + h + '.png'


if __name__ == '__main__':
    print(make_card('scholarship', '🎓 Beasiswa dibuka: Singapore International Graduate Award (SINGA) (deadline 2026-12-01)', 'test'))
