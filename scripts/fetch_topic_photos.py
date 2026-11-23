#!/usr/bin/env python3
"""Fetch CANDIDATE topic photos for immigration-news posts from Wikimedia Commons (CC0 / Public domain / CC BY only,
no share-alike), into social/photos/candidates/<topic>/ with a meta.json per topic. A human/Claude reviews them and
moves approved ones into social/library/topic-<topic>/ (only those are ever used)."""
import json, os, re, io, html, hashlib, urllib.parse, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'TEG-info-site/1.0 (https://info.talentededucationgroup.com)'}
TOPICS = {
    'visa': ['airplane window wing sky', 'airport departure hall travellers', 'passport travel luggage', 'aircraft take off runway'],
    'policy': ['parliament house canberra', 'government building columns', 'university campus students walking', 'graduation caps'],
    'fees': ['calculator notebook desk', 'piggy bank coins', 'student laptop study desk', 'budget planning notebook'],
    'work': ['barista coffee machine', 'cafe kitchen work', 'warehouse worker', 'retail shop interior'],
    'school': ['university library reading room', 'lecture hall students', 'university campus lawn', 'graduation ceremony'],
    # per bidang untuk promo jurusan (pemilik 23/11/2026)
    'health': ['nursing students simulation lab', 'nurse hospital ward', 'nursing training mannequin', 'aged care nurse'],
    'cookery': ['chef cooking commercial kitchen', 'culinary students kitchen', 'pastry chef plating', 'chef kitchen brigade'],
    'it': ['students coding laptops', 'computer lab students', 'programmer working code screen', 'data center server room'],
    'construction': ['construction workers site helmets', 'carpenter apprentice', 'electrician working', 'construction site crane'],
    'business': ['business meeting office team', 'students group project discussion', 'office coworking space', 'presentation meeting room'],
    'childcare': ['kindergarten classroom children playing', 'preschool teacher children', 'early childhood education classroom', 'children painting classroom'],
    'city-au': ['Sydney Harbour Bridge Opera House', 'Melbourne Flinders Street', 'Brisbane river skyline', 'Adelaide city', 'Perth Elizabeth Quay'],
}
LIC = {'CC0', 'PUBLIC DOMAIN', 'CC BY 4.0', 'CC BY 3.0', 'CC BY 2.5', 'CC BY 2.0'}
BAD = re.compile(r'map|logo|coin of|stamp|flag|seal|crest|diagram|chart|poster|sign|1[89]\d\d|protest|police|military|army|navy|crash|accident|fire|grave|nude|drawing|illustration|painting|engraving|vector|screenshot', re.I)


def api(**q):
    q.update(format='json', origin='*')
    with urllib.request.urlopen(urllib.request.Request(API + '?' + urllib.parse.urlencode(q), headers=UA), timeout=40) as r:
        return json.load(r)


def main():
    only = [t.strip() for t in os.environ.get('TOPICS', '').split(',') if t.strip()]
    for topic, queries in TOPICS.items():
        if only and topic not in only:
            continue
        out = os.path.join(ROOT, 'social', 'photos', 'candidates', topic)
        os.makedirs(out, exist_ok=True)
        meta, seen = [], set()
        for q in queries:
            try:
                d = api(action='query', generator='search', gsrnamespace=6, gsrlimit=25, gsrsearch=f'{q} filetype:bitmap',
                        prop='imageinfo', iiprop='url|size|extmetadata|mime', iiurlwidth=1600)
            except Exception as e:
                print('search error', q, e); continue
            got = 0
            for p in sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 99)):
                ii = (p.get('imageinfo') or [{}])[0]
                t = p['title']
                if BAD.search(t) or ii.get('mime') != 'image/jpeg' or ii.get('width', 0) < 1600:
                    continue
                if not (1.1 <= ii['width'] / max(1, ii['height']) <= 1.9):
                    continue
                md = ii.get('extmetadata', {})
                lic = (md.get('LicenseShortName') or {}).get('value', '').strip().upper()
                yr = re.search(r'(19\d\d|20\d\d)', (md.get('DateTimeOriginal') or md.get('DateTime') or {}).get('value', '') or '')
                if lic not in LIC or not yr or int(yr.group(1)) < 2005 or ii['descriptionurl'] in seen:
                    continue
                cats = (md.get('Categories') or {}).get('value', '').lower()
                if re.search(r'illustration|drawing|painting|vector|sign|logo|text', cats):
                    continue
                artist = html.unescape(re.sub('<[^>]+>', ' ', (md.get('Artist') or {}).get('value', ''))).strip()
                artist = re.sub(r'\s+', ' ', artist)[:60] or 'Unknown author'
                try:
                    with urllib.request.urlopen(urllib.request.Request(ii['thumburl'], headers=UA), timeout=40) as r:
                        im = Image.open(io.BytesIO(r.read())).convert('RGB')
                except Exception:
                    continue
                h = hashlib.sha256(ii['descriptionurl'].encode()).hexdigest()[:10]
                im.thumbnail((1600, 1600)); im.save(os.path.join(out, f'{h}.jpg'), quality=86)
                seen.add(ii['descriptionurl'])
                meta.append({"file": f'{h}.jpg', "query": q, "title": t, "page": ii['descriptionurl'], "author": artist,
                             "license": 'Public domain' if lic == 'PUBLIC DOMAIN' else lic})
                got += 1
                if got >= 4:
                    break
        json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
        print(topic, len(meta))


if __name__ == '__main__':
    main()
