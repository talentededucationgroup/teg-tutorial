#!/usr/bin/env python3
"""Openly licensed background photos for social cards (Wikimedia Commons).
Only CC0 / Public domain / CC BY (NO share-alike, NO non-commercial), landscape, >=1600px,
title must contain the landmark/city name. Chosen photos are cached in data/social-photos.json
and social/photos/*.jpg so each is picked once and can be reviewed/removed by hand
(set "blocked": true in the JSON to never use one again)."""
import json, os, re, hashlib, io, html, glob, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, 'data', 'social-photos.json')
DIR = os.path.join(ROOT, 'social', 'photos')
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'TEG-info-site/1.0 (https://info.talentededucationgroup.com)'}
PLACES = {
    'AU': ['Sydney Opera House', 'Melbourne skyline', 'Brisbane skyline', 'Perth skyline', 'Adelaide skyline'],
    'NZ': ['Auckland skyline', 'Wellington harbour', 'Queenstown', 'Christchurch'],
    'GB': ['London skyline', 'Tower Bridge', 'Edinburgh', 'Manchester'],
    'CA': ['Toronto skyline', 'Vancouver skyline', 'Montreal skyline'],
    'US': ['New York City skyline', 'Boston skyline', 'San Francisco skyline'],
    'IE': ['Dublin', 'Cork city'], 'DE': ['Berlin', 'Munich', 'Hamburg'], 'FR': ['Paris', 'Lyon'],
    'NL': ['Amsterdam', 'Rotterdam'], 'JP': ['Tokyo skyline', 'Kyoto'], 'KR': ['Seoul skyline', 'Busan'],
    'SG': ['Singapore skyline', 'Marina Bay'], 'TW': ['Taipei'], 'CN': ['Shanghai skyline', 'Beijing'],
    'SE': ['Stockholm'], 'HU': ['Budapest'], 'TR': ['Istanbul'], 'BN': ['Bandar Seri Begawan'],
    'ES': ['Madrid', 'Barcelona'], 'CH': ['Zurich', 'Geneva'], 'MY': ['Kuala Lumpur skyline'],
    'EU': ['Brussels', 'Vienna'], 'ANY': ['Sydney Opera House', 'London skyline', 'Toronto skyline', 'Auckland skyline'],
}
ALIAS = {'australia': 'AU', 'selandia baru': 'NZ', 'new zealand': 'NZ', 'inggris': 'GB', 'uk': 'GB', 'united kingdom': 'GB',
         'kanada': 'CA', 'canada': 'CA', 'amerika serikat': 'US', 'usa': 'US', 'irlandia': 'IE', 'ireland': 'IE',
         'jerman': 'DE', 'germany': 'DE', 'prancis': 'FR', 'france': 'FR', 'belanda': 'NL', 'netherlands': 'NL',
         'jepang': 'JP', 'japan': 'JP', 'korea selatan': 'KR', 'south korea': 'KR', 'singapura': 'SG', 'singapore': 'SG',
         'taiwan': 'TW', 'tiongkok': 'CN', 'china': 'CN', 'swedia': 'SE', 'hongaria': 'HU', 'türkiye': 'TR', 'turki': 'TR',
         'brunei darussalam': 'BN', 'spanyol': 'ES', 'spain': 'ES', 'swiss': 'CH', 'switzerland': 'CH', 'malaysia': 'MY',
         'eropa (multi-negara)': 'EU'}
LIC = {'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/', 'PUBLIC DOMAIN': '',
       'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0', 'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0',
       'CC BY 2.5': 'https://creativecommons.org/licenses/by/2.5', 'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0'}
BAD = re.compile(r'plaque|souvenir|memorial|monument aux|illustration|drawing|engraving|painting|vector|lithograph|map|logo|coin|stamp|flag|seal|crest|diagram|banknote|poster|1[89]\d\d|portrait|protest|police|fire|flood|accident|crash|riot|grave|cemetery|military|army|navy', re.I)


def code(country):
    c = (country or '').strip()
    if c.upper() in PLACES:
        return c.upper()
    return ALIAS.get(c.lower(), 'ANY')


def load():
    try:
        return json.load(open(META, encoding='utf-8'))
    except Exception:
        return {"note": "Foto latar kartu sosmed, lisensi CC0/PD/CC BY dari Wikimedia Commons. 'blocked': true = jangan dipakai.", "items": []}


def _api(**q):
    q.update(format='json', origin='*')
    with urllib.request.urlopen(urllib.request.Request(API + '?' + urllib.parse.urlencode(q), headers=UA), timeout=30) as r:
        return json.load(r)


def _search(place, used):
    key = place.split()[0]
    d = _api(action='query', generator='search', gsrnamespace=6, gsrlimit=30,
             gsrsearch=f'intitle:"{key}" {place} filetype:bitmap', prop='imageinfo',
             iiprop='url|size|extmetadata|mime', iiurlwidth=1600)
    for p in sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 99)):
        t, ii = p['title'], (p.get('imageinfo') or [{}])[0]
        if key.lower() not in t.lower() or BAD.search(t) or ii.get('descriptionurl') in used:
            continue
        if ii.get('mime') != 'image/jpeg' or ii.get('width', 0) < 1600 or not (1.2 <= ii.get('width', 0) / max(1, ii.get('height', 1)) <= 2.0):
            continue
        md = ii.get('extmetadata', {})
        yr = re.search(r'(1[89]\d\d|20\d\d)', (md.get('DateTimeOriginal') or md.get('DateTime') or {}).get('value', '') or '')
        if not yr or int(yr.group(1)) < 2005:
            continue
        cats = (md.get('Categories') or {}).get('value', '').lower()
        if re.search(r'illustration|drawing|painting|engraving|vector|plaque|memorial|night', cats):
            continue
        lic = (md.get('LicenseShortName') or {}).get('value', '').strip().upper()
        if lic not in LIC:
            continue
        artist = html.unescape(re.sub('<[^>]+>', ' ', (md.get('Artist') or {}).get('value', ''))).strip()
        artist = re.sub(r'\s+', ' ', artist)
        artist = re.sub(r'^(.+?)\s*\1$', r'\1', artist)
        artist = re.sub(r'^Unknown author.*', 'Unknown author', artist)[:60] or 'Unknown author'
        name = 'Public domain' if lic == 'PUBLIC DOMAIN' else lic
        return {"place": place, "file_page": ii['descriptionurl'], "thumb": ii.get('thumburl'), "author": artist,
                "license": name, "license_url": LIC[lic]}
    return None


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', (t or '').lower()).strip('-')


def resolve_provider(provider):
    """provider text -> library slug (social/library/providers.json), or None"""
    if not provider:
        return None
    try:
        reg = json.load(open(os.path.join(ROOT, 'social', 'library', 'providers.json'), encoding='utf-8'))['providers']
    except Exception:
        return None
    for k, v in reg.items():
        for n in v.get('names', []):
            if len(n) <= 4 and n.isupper():
                if re.search(rf'(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])', provider):
                    return k
            elif re.search(rf'\b{re.escape(n.lower())}\b', provider.lower()):
                return k
    return None


def get_photo(country, seed, provider=None):
    """Return (PIL.Image or None, credit str or None). Never raises.
    1) social/library/<provider-slug>/*.jpg|png = official brochure/marketing images supplied by the
       provider to Talented as their agent (uploaded by the owner) -> used first, credit = provider.
    2) openly licensed Wikimedia Commons city photo for the country."""
    try:
        from PIL import Image
        if provider:
            sl = resolve_provider(provider) or slug(provider)
            lib = sorted(glob.glob(os.path.join(ROOT, 'social', 'library', sl, '*.[jp][pn]g')))
            if lib:
                pick = lib[int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(lib)]
                cr = f"Foto: {provider}"
                try:
                    cj = json.load(open(os.path.join(os.path.dirname(pick), 'credits.json'), encoding='utf-8'))
                    cr = cj.get(os.path.basename(pick), {}).get('credit') or cr
                except Exception:
                    pass
                return Image.open(pick).convert('RGB'), cr
        m = load()
        cc = code(country)
        pool = [i for i in m['items'] if i.get('country') == cc and not i.get('blocked')]
        if len(pool) < 3:  # top up the pool (only works where Commons is reachable, e.g. GitHub Actions)
            used = {i['file_page'] for i in m['items']}
            for place in PLACES[cc]:
                if len([i for i in m['items'] if i.get('country') == cc and not i.get('blocked')]) >= 3:
                    break
                try:
                    f = _search(place, used)
                except Exception:
                    f = None
                if not f:
                    continue
                with urllib.request.urlopen(urllib.request.Request(f['thumb'], headers=UA), timeout=40) as r:
                    im = Image.open(io.BytesIO(r.read())).convert('RGB')
                im.thumbnail((1600, 1600))
                os.makedirs(DIR, exist_ok=True)
                h = hashlib.sha256(f['file_page'].encode()).hexdigest()[:16]
                im.save(os.path.join(DIR, h + '.jpg'), quality=85)
                f.update(country=cc, file=f'social/photos/{h}.jpg'); f.pop('thumb', None)
                m['items'].append(f); used.add(f['file_page'])
            json.dump(m, open(META, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            pool = [i for i in m['items'] if i.get('country') == cc and not i.get('blocked')]
        if not pool:
            return None, None
        pick = pool[int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(pool)]
        im = Image.open(os.path.join(ROOT, pick['file'])).convert('RGB')
        return im, f"Foto: {pick['author']} / Wikimedia Commons, {pick['license']}"
    except Exception as e:
        print('photo skipped:', str(e)[:120])
        return None, None
