"""Gambar sampul artikel blog (1200x630) - dipakai di halaman artikel, og:image, dan feed RSS (GoDaddy External blog feed).
Foto latar: data/social-photos.json (Wikimedia, lisensi bebas; kredit penulis + lisensi dicetak di gambar). Deterministik per slug."""
import json, os, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = lambda n, s: ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', n), s)
NAVY, GOLD = (20, 33, 61), (201, 162, 39)
USED = set()
def _photo(slug, countries):
    ph = [x for x in json.load(open(os.path.join(ROOT, 'data/social-photos.json')))['items'] if not x.get('blocked') and os.path.exists(os.path.join(ROOT, x['file']))]
    want = [{'UK': 'GB'}.get(c, c) for c in (countries or [])] + ['ANY']
    for c in want:
        pool = [x for x in ph if x['country'] == c]
        if pool:
            pool = sorted(pool, key=lambda x: hashlib.md5((slug + x['file']).encode()).hexdigest())
            free = [x for x in pool if x['file'] not in USED]
            if not free and c != want[-1]: continue
            x = (free or pool)[0]; USED.add(x['file']); return x
    return None
def _chip(p):
    s = p['slug']
    if 'mock-test' in s: return 'TES BAHASA GRATIS'
    if 'ielts' in s or 'pte' in s: return 'TES BAHASA INGGRIS'
    if 'beasiswa' in s or 'scholarship' in s: return 'BEASISWA'
    if 'visa' in s: return 'VISA PELAJAR'
    return 'INFO STUDI LUAR NEGERI'
def _wrap(d, text, font, maxw):
    out, line = [], ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: line = t
        else: out.append(line); line = w
    out.append(line); return out
def make(p):
    rel = f"blog/{p['slug']}/cover.jpg"; W, H = 1200, 630
    x = _photo(p['slug'], p.get('countries'))
    if x:
        im = Image.open(os.path.join(ROOT, x['file'])).convert('RGB'); k = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1)); l, t = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((l, t, l + W, t + H))
    else: im = Image.new('RGB', (W, H), NAVY)
    ov = Image.new('L', (W, H)); od = ImageDraw.Draw(ov)
    for y in range(H): od.line([(0, y), (W, y)], fill=int(35 + 185 * (y / H) ** 1.6))
    im = Image.composite(Image.new('RGB', (W, H), NAVY), im, ov); d = ImageDraw.Draw(im)
    try:
        lg = Image.open(os.path.join(ROOT, 'assets/brand/logo-talented-putih.png')).convert('RGBA'); lg.thumbnail((210, 90)); im.paste(lg, (48, 40), lg)
    except Exception: pass
    title = p['title']['id']
    for size in (60, 54, 48, 42, 38):
        ft = F('Montserrat.ttf', size); ft.set_variation_by_name('Bold') if hasattr(ft, 'set_variation_by_name') else None
        lines = _wrap(d, title, ft, W - 120)
        if len(lines) <= 4: break
    lines = lines[:4]; lh = int(size * 1.18); y0 = H - 70 - lh * len(lines)
    cf = F('Montserrat.ttf', 24)
    try: cf.set_variation_by_name('Bold')
    except Exception: pass
    chip = _chip(p); cw = d.textlength(chip, font=cf) + 36
    d.rounded_rectangle([60, y0 - 62, 60 + cw, y0 - 18], radius=10, fill=GOLD); d.text((78, y0 - 55), chip, font=cf, fill=NAVY)
    for i, ln in enumerate(lines): d.text((60, y0 + i * lh), ln, font=ft, fill='white')
    sf = F('Montserrat.ttf', 18); d.text((60, H - 46), 'info.talentededucationgroup.com/blog', font=sf, fill=GOLD)
    if x and not x['license'].lower().startswith(('cc0', 'public')):
        cr = f"Foto: {x['author'][:48]} / {x['license']} (Wikimedia Commons)"; d.text((W - 40 - d.textlength(cr, font=F('Montserrat.ttf', 14)), H - 40), cr, font=F('Montserrat.ttf', 14), fill=(220, 220, 220))
    os.makedirs(os.path.join(ROOT, 'blog', p['slug']), exist_ok=True)
    im.save(os.path.join(ROOT, rel), 'JPEG', quality=86, optimize=True, progressive=True)
    return rel
