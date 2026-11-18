#!/usr/bin/env python3
"""Fill missing photo{} on data/accommodation.json items with an openly licensed
CITY photo from Wikimedia Commons (CC0 / Public domain / CC BY / CC BY-SA),
with mandatory attribution. Only touches items that have no photo yet.
Strict rules: file title must contain the city name, JPEG, >= 1000px wide,
no maps/logos/coins/stamps/flags/old photos. If nothing passes: leave empty (icon)."""
import json, os, re, sys, urllib.parse, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data', 'accommodation.json')
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'TEG-info-site/1.0 (https://info.talentededucationgroup.com)'}
OK = [('CC0', 'http://creativecommons.org/publicdomain/zero/1.0/'), ('Public domain', ''),
      ('CC BY-SA 4.0', None), ('CC BY-SA 3.0', None), ('CC BY-SA 2.0', None),
      ('CC BY 4.0', None), ('CC BY 3.0', None), ('CC BY 2.0', None)]
BAD = re.compile(r'map|logo|coin|stamp|flag|seal|crest|diagram|chart|banknote|poster|sign\b|1[89]\d\d|portrait|interior|museum|statue|grave|cemetery|church|night', re.I)
TODAY = datetime.date.today().isoformat()


def api(**q):
    q.update(format='json', origin='*')
    with urllib.request.urlopen(urllib.request.Request(API + '?' + urllib.parse.urlencode(q), headers=UA), timeout=30) as r:
        return json.load(r)


def lic_url(short):
    for name, url in OK:
        if short.upper().replace('PUBLIC DOMAIN', 'Public domain'.upper()) == name.upper():
            if url is None:
                m = re.match(r'CC (BY(?:-SA)?) (\d\.\d)', name)
                return name, f"https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}"
            return name, url
    return None, None


def find(city):
    for q in (f'{city} skyline', f'{city} city centre', f'{city} street', city):
        d = api(action='query', generator='search', gsrnamespace=6, gsrlimit=20,
                gsrsearch=f'intitle:"{city}" {q} filetype:bitmap', prop='imageinfo',
                iiprop='url|size|extmetadata|mime', iiurlwidth=960)
        pages = sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 99))
        for p in pages:
            t = p['title']
            ii = (p.get('imageinfo') or [{}])[0]
            if city.lower() not in t.lower() or BAD.search(t):
                continue
            if ii.get('mime') != 'image/jpeg' or ii.get('width', 0) < 1000 or ii.get('width', 0) < ii.get('height', 0):
                continue
            md = ii.get('extmetadata', {})
            name, url = lic_url((md.get('LicenseShortName') or {}).get('value', ''))
            if not name:
                continue
            artist = re.sub('<[^>]+>', '', (md.get('Artist') or {}).get('value', '')).strip()[:80] or 'Unknown'
            src = ii.get('thumburl', '').split('?')[0]
            if not src.startswith('https://upload.wikimedia.org/'):
                continue
            return {"src": src, "file_page": ii.get('descriptionurl'), "author": artist, "license": name,
                    "license_url": url, "type": "city",
                    "label": {"id": "Foto kota (ilustrasi)", "en": "City photo (illustration)"},
                    "credit": f"Foto: {artist} / Wikimedia Commons, {name}", "checked": TODAY, "auto": True}
    return None


def main():
    A = json.load(open(P, encoding='utf-8'))
    changed = 0
    cache = {}
    for it in A.get('items', []):
        if it.get('photo') or not it.get('city'):
            continue
        c = it['city'].split(',')[0].strip()
        if c not in cache:
            try:
                cache[c] = find(c)
            except Exception as e:
                print('commons error', c, str(e)[:120]); cache[c] = None
        if cache[c]:
            it['photo'] = cache[c]; changed += 1
            print('photo added:', it.get('provider'), '->', cache[c]['file_page'])
    if changed:
        json.dump(A, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('photos added:', changed)


if __name__ == '__main__':
    sys.exit(main())
