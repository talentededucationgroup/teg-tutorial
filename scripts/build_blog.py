#!/usr/bin/env python3
"""Build static blog pages from data/blog.json + data/news.json.
Output: blog/index.html, blog/<slug>/index.html, blog/feed.xml, sitemap.xml, robots.txt
Run from repo root: python3 scripts/build_blog.py"""
import json, os, html, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B=json.load(open(os.path.join(ROOT,'data/blog.json'),encoding='utf-8'))
N=json.load(open(os.path.join(ROOT,'data/news.json'),encoding='utf-8'))
SITE='https://info.talentededucationgroup.com'
PRICE='https://pricelist.talentededucationgroup.com/biaya-studi'
LINK='https://linktr.ee/talentededucationgroup'
FORM='https://form.jotform.com/263181709123050'
OG=SITE+'/assets/share/pricelist-share-v2.jpg'
e=html.escape
T={'id':{'blog':'Blog Talented','sub':'Berita visa pelajar & tips studi luar negeri - diperbarui setiap bulan','read':'Baca','share':'Bagikan','copy':'Salin link','copied':'Link disalin','sources':'Sumber resmi','back':'← Semua artikel','cta1':'Cek biaya studi','cta2':'Konsultasi gratis','cta3':'Untuk institusi: ajukan paket promosi','news':'Berita imigrasi terbaru','disc':N['disclaimer']['id'],'upd':'Diperbarui','lang':'English','langq':'en','other':'Artikel lain'},
   'en':{'blog':'Talented Blog','sub':'Student visa news & study abroad tips - updated monthly','read':'Read','share':'Share','copy':'Copy link','copied':'Link copied','sources':'Official sources','back':'← All articles','cta1':'Check study costs','cta2':'Free consultation','cta3':'For institutions: apply for a promotion package','news':'Latest immigration news','disc':N['disclaimer']['en'],'upd':'Updated','lang':'Bahasa Indonesia','langq':'id','other':'More articles'}}
CSS=""":root{--bg:#f4f7f5;--ink:#18241f;--muted:#5b6a63;--green:#1f5f4a;--line:#dbe3de;--card:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,"Segoe UI",sans-serif}
a{color:var(--green)}header,main,footer{max-width:820px;margin:0 auto;padding:0 16px}
header{padding-top:22px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-weight:800;color:var(--green);text-decoration:none;line-height:1.2}.brand small{display:block;font-weight:500;color:var(--muted);font-size:.72rem}
.lang{font-size:.9rem;border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;text-decoration:none}
h1{font-size:clamp(1.55rem,4.6vw,2.3rem);line-height:1.2;margin:18px 0 8px}h2{font-size:1.25rem;margin:28px 0 8px;line-height:1.3}
.meta{color:var(--muted);font-size:.9rem}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}
.card h3{margin:0 0 6px;font-size:1.12rem;line-height:1.35}.card p{margin:0 0 8px;color:var(--muted)}
.tag{display:inline-block;font-size:.72rem;font-weight:700;border-radius:999px;padding:2px 9px;vertical-align:middle;margin-left:4px;background:#e7efe9;color:var(--green)}
.tag-c{background:#fff3d6;color:#7a5200}.tag-u{background:#e3eefc;color:#1d4f91}.tag-x{background:#fde7e7;color:#8c1d1d}.tag-a{background:#efe7fb;color:#55308f}
.share{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}.share a,.share button{font:inherit;font-size:.9rem;font-weight:600;text-decoration:none;border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:10px;padding:9px 13px;cursor:pointer;min-height:44px;display:inline-flex;align-items:center}
.share .wa{background:#1f8a4c;color:#fff;border-color:#1f8a4c}.cta{display:grid;gap:10px;margin:24px 0}.cta a{display:block;text-align:center;font-weight:700;text-decoration:none;padding:14px;border-radius:12px;background:var(--green);color:#fff}
.cta a.alt{background:#fff;color:var(--green);border:2px solid var(--green)}.src li{margin:4px 0;word-break:break-word}
.disc{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:12px;margin-top:28px}footer{padding:24px 16px 48px;color:var(--muted);font-size:.85rem}
.news li{margin:6px 0}#toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#18241f;color:#fff;padding:8px 14px;border-radius:8px;display:none}"""
STLAB={'in_force':'tag-f','upcoming':'tag-u','announced':'tag-a','changed':'tag-x','consultation':'tag-c','proposed':'tag-c'}
def fmt(d,l):
    dt=datetime.date.fromisoformat(d)
    mi=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
    me=['January','February','March','April','May','June','July','August','September','October','November','December']
    return f"{dt.day} {(mi if l=='id' else me)[dt.month-1]} {dt.year}"
def share(url,title,l):
    t=T[l]; u=e(url); q=lambda s: __import__('urllib.parse').parse.quote(s,safe='')
    return f"""<div class="share" aria-label="{t['share']}"><button type="button" onclick="nshare()">📤 {t['share']}</button>
<a class="wa" href="https://wa.me/?text={q(title+' '+url)}" target="_blank" rel="noopener">WhatsApp</a>
<a href="https://www.facebook.com/sharer/sharer.php?u={q(url)}" target="_blank" rel="noopener">Facebook</a>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={q(url)}" target="_blank" rel="noopener">LinkedIn</a>
<a href="https://twitter.com/intent/tweet?url={q(url)}&text={q(title)}" target="_blank" rel="noopener">X</a>
<a href="https://t.me/share/url?url={q(url)}&text={q(title)}" target="_blank" rel="noopener">Telegram</a>
<button type="button" onclick="copyl()">🔗 {t['copy']}</button></div>"""
JS=lambda l:f"""<div id="toast">{T[l]['copied']}</div><script>
function nshare(){{if(navigator.share){{navigator.share({{title:document.title,url:location.href}}).catch(()=>{{}})}}else copyl()}}
function copyl(){{const u=location.href;(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>{{const t=document.getElementById('toast');t.style.display='block';setTimeout(()=>t.style.display='none',1800)}}).catch(()=>prompt('{T[l]['copy']}',u))}}
</script>"""
def page(l,title,desc,url,alt_url,body,jsonld=''):
    return f"""<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(url)}">
<link rel="alternate" hreflang="{l}" href="{e(url)}"><link rel="alternate" hreflang="{T[l]['langq']}" href="{e(alt_url)}"><link rel="alternate" type="application/rss+xml" title="Talented Blog" href="{SITE}/blog/feed.xml">
<meta property="og:type" content="article"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:image" content="{OG}"><meta name="twitter:card" content="summary_large_image">
{jsonld}<style>{CSS}</style></head><body><header><a class="brand" href="{SITE}/blog/{'' if l=='id' else 'en/'}">Talented Education Group<small>PT. Pilar Pendidikan Internasional</small></a><a class="lang" href="{e(alt_url)}">🌐 {T[l]['lang']}</a></header>
<main>{body}</main><footer>© Talented Education Group · <a href="{LINK}">linktr.ee/talentededucationgroup</a></footer>{JS(l)}</body></html>"""
def url_post(s,l): return f"{SITE}/blog/{s}/" if l=='id' else f"{SITE}/blog/en/{s}/"
def url_idx(l): return f"{SITE}/blog/" if l=='id' else f"{SITE}/blog/en/"
posts=sorted(B['posts'],key=lambda p:p['date'],reverse=True)
def write(path,txt):
    os.makedirs(os.path.dirname(path),exist_ok=True); open(path,'w',encoding='utf-8').write(txt)
def news_list(l,k=6):
    out=[]
    for it in sorted(N['items'],key=lambda x:x['date'],reverse=True)[:k]:
        st=N['statuses'][it['status']][l]; c=N['countries'][it['country']][l]
        off=[x for x in it['links'] if x.get('official')]
        a=f' · <a href="{e(off[0]["url"])}" target="_blank" rel="noopener">{"sumber resmi" if l=="id" else "official source"}</a>' if off else ''
        dl=f' ({"tutup" if l=="id" else "closes"} {fmt(it["deadline"],l)})' if it.get('deadline') else ''
        out.append(f'<li><span class="tag {STLAB.get(it["status"],"")}">{e(st)}</span> <strong>{e(c)}</strong> - {e(it["title"][l])}{dl}{a}</li>')
    return '<ul class="news">'+''.join(out)+'</ul>'
for l in ('id','en'):
    t=T[l]
    for p in posts:
        u=url_post(p['slug'],l); alt=url_post(p['slug'],t['langq'])
        others=''.join(f'<li><a href="{url_post(o["slug"],l)}">{e(o["title"][l])}</a></li>' for o in posts if o is not p)[:4000]
        src=''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>' for s in p['sources'])
        ld=json.dumps({"@context":"https://schema.org","@type":"Article","headline":p['title'][l],"description":p['description'][l],"datePublished":p['date'],"dateModified":p.get('updated',p['date']),"inLanguage":l,"mainEntityOfPage":u,"image":OG,"author":{"@type":"Organization","name":"Talented Education Group"},"publisher":{"@type":"Organization","name":"Talented Education Group"}},ensure_ascii=False)
        body=f"""<p class="meta"><a href="{url_idx(l)}">{t['back']}</a></p><h1>{e(p['title'][l])}</h1><p class="meta">{t['upd']}: {fmt(p.get('updated',p['date']),l)}</p>
{share(u,p['title'][l],l)}<article>{p['body'][l]}</article><h2>{t['sources']}</h2><ul class="src">{src}</ul>
<div class="cta"><a href="{PRICE}?lang={l}">{t['cta1']}</a><a class="alt" href="{LINK}">{t['cta2']}</a><a class="alt" href="{FORM}">{t['cta3']}</a></div>
{share(u,p['title'][l],l)}{('<h2>'+t['other']+'</h2><ul>'+others+'</ul>') if others else ''}<p class="disc">{e(t['disc'])}</p>"""
        write(os.path.join(ROOT,'blog' if l=='id' else 'blog/en',p['slug'],'index.html'),page(l,p['title'][l]+' | Talented',p['description'][l],u,alt,body,f'<script type="application/ld+json">{ld}</script>'))
    cards=''.join(f'<div class="card"><h3><a href="{url_post(p["slug"],l)}">{e(p["title"][l])}</a></h3><p>{e(p["description"][l])}</p><span class="meta">{fmt(p["date"],l)}</span></div>' for p in posts)
    body=f"""<h1>{t['blog']}</h1><p class="meta">{t['sub']}</p>{share(url_idx(l),t['blog'],l)}{cards}<h2>{t['news']}</h2>{news_list(l)}
<div class="cta"><a href="{PRICE}?lang={l}">{t['cta1']}</a><a class="alt" href="{LINK}">{t['cta2']}</a><a class="alt" href="{FORM}">{t['cta3']}</a></div><p class="disc">{e(t['disc'])}</p>"""
    write(os.path.join(ROOT,'blog' if l=='id' else 'blog/en','index.html'),page(l,t['blog']+' - Talented Education Group',t['sub'],url_idx(l),url_idx(t['langq']),body))
# RSS
items=''.join(f"<item><title>{e(p['title']['id'])}</title><link>{url_post(p['slug'],'id')}</link><guid>{url_post(p['slug'],'id')}</guid><pubDate>{datetime.datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y 08:00:00 +0700')}</pubDate><description>{e(p['description']['id'])}</description></item>" for p in posts)
write(os.path.join(ROOT,'blog/feed.xml'),f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Talented Blog</title><link>{SITE}/blog/</link><description>{e(T["id"]["sub"])}</description>{items}</channel></rss>')
urls=[url_idx('id'),url_idx('en')]+[url_post(p['slug'],l) for p in posts for l in ('id','en')]+[SITE+'/panduan/']
last={url_post(p['slug'],l):p.get('updated',p['date']) for p in posts for l in ('id','en')}
sm=''.join(f'<url><loc>{u}</loc><lastmod>{last.get(u,posts[0]["date"])}</lastmod></url>' for u in urls)
write(os.path.join(ROOT,'sitemap.xml'),f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
write(os.path.join(ROOT,'robots.txt'),f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
print('built',len(posts),'posts')
