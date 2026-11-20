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
ADV='https://pricelist.talentededucationgroup.com/advertise'
OG=SITE+'/assets/share/pricelist-share-v2.jpg'
e=html.escape
T={'id':{'blog':'Blog Talented','sub':'Berita visa pelajar & tips studi luar negeri - diperbarui setiap bulan','read':'Baca','share':'Bagikan','copy':'Salin link','copied':'Link disalin','sources':'Sumber resmi','back':'← Semua artikel','cta1':'Cek biaya studi','cta2':'Konsultasi gratis','cta3':'Untuk institusi: ajukan paket promosi','news':'Berita imigrasi terbaru','disc':N['disclaimer']['id'],'upd':'Diperbarui','lang':'English','langq':'en','other':'Artikel lain'},
   'en':{'blog':'Talented Blog','sub':'Student visa news & study abroad tips - updated monthly','read':'Read','share':'Share','copy':'Copy link','copied':'Link copied','sources':'Official sources','back':'← All articles','cta1':'Check study costs','cta2':'Free consultation','cta3':'For institutions: apply for a promotion package','news':'Latest immigration news','disc':N['disclaimer']['en'],'upd':'Updated','lang':'Bahasa Indonesia','langq':'id','other':'More articles'}}
CSS=""":root{--bg:#f4f6f3;--ink:#16231d;--muted:#5d6b64;--green:#14624a;--green9:#0e3b2e;--gold:#c9a227;--line:#e1e6e2;--card:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,"Segoe UI",Roboto,sans-serif}
a{color:var(--green)}.wrap{max-width:860px;margin:0 auto;padding:0 16px}
.top{background:#fff;border-bottom:1px solid var(--line)}.top .wrap{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-top:10px;padding-bottom:10px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--green9);text-decoration:none;line-height:1.15}.brand img{height:40px;width:auto}.brand small{display:block;font-weight:500;color:var(--muted);font-size:.72rem}
.lang{font-size:.85rem;font-weight:600;border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 13px;text-decoration:none;color:var(--green9);white-space:nowrap}
.hero{background:linear-gradient(135deg,var(--green) 0%,var(--green9) 100%);color:#fff;padding:30px 0 26px}.hero h1{margin:0 0 6px;font-size:clamp(1.7rem,4.8vw,2.5rem);line-height:1.15}.hero p{margin:0;color:#d6ece2;font-size:1rem}
.hero .meta{color:#cfe6dc}.hero a{color:#fff}
main.wrap{padding-top:22px;padding-bottom:10px}h2{font-size:1.2rem;margin:30px 0 12px;line-height:1.3;display:flex;align-items:center;gap:8px}
h2 .more{margin-left:auto;font-size:.85rem;font-weight:600;text-decoration:none}
.meta{color:var(--muted);font-size:.88rem}
.post{display:block;background:var(--card);border:1px solid var(--line);border-left:5px solid var(--gold);border-radius:16px;padding:18px 20px;text-decoration:none;color:inherit;box-shadow:0 4px 14px rgba(14,59,46,.06);transition:transform .15s,box-shadow .15s}
.post:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(14,59,46,.12)}.post .kick{font-size:.75rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#8a6d0f}
.post h3{margin:4px 0 8px;font-size:1.25rem;line-height:1.3;color:var(--green9)}.post p{margin:0 0 12px;color:var(--muted);font-size:.98rem}
.post .foot{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}.read{font-weight:700;color:var(--green);font-size:.95rem}
.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{font-size:.78rem;background:#eef4f0;color:var(--green9);border-radius:999px;padding:2px 10px}
.news{list-style:none;margin:0;padding:0;display:grid;gap:10px}.news li{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:grid;grid-template-columns:auto 1fr;gap:4px 12px;align-items:start}
.news .flag{font-size:1.5rem;line-height:1.2;grid-row:span 2}.news .t{font-weight:600;line-height:1.4}.news .s{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:.84rem;color:var(--muted)}
.news .s a{font-weight:600;text-decoration:none}
.tag{display:inline-block;font-size:.72rem;font-weight:700;border-radius:999px;padding:2px 9px;background:#e7efe9;color:var(--green)}
.tag-c{background:#fff3d6;color:#7a5200}.tag-u{background:#e3eefc;color:#1d4f91}.tag-x{background:#fde7e7;color:#8c1d1d}.tag-a{background:#efe7fb;color:#55308f}
.share{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0;align-items:center}.share .lbl{font-size:.82rem;color:var(--muted);margin-right:2px}
.share a,.share button{font:inherit;font-size:.82rem;font-weight:600;text-decoration:none;border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:999px;padding:6px 12px;cursor:pointer;min-height:36px;display:inline-flex;align-items:center;gap:4px}
.hero .share a,.hero .share button{background:rgba(255,255,255,.12);border-color:rgba(255,255,255,.3);color:#fff}.hero .share .lbl{color:#cfe6dc}
.share .wa{background:#1f8a4c!important;color:#fff!important;border-color:#1f8a4c!important}
.cta{display:grid;grid-template-columns:1.3fr 1fr;gap:12px;margin:30px 0 10px}.cta a{display:flex;flex-direction:column;justify-content:center;text-decoration:none;padding:16px 18px;border-radius:16px;font-weight:800;font-size:1.02rem;line-height:1.3}
.cta a small{font-weight:500;font-size:.82rem;opacity:.85;margin-top:3px}.cta .p{background:var(--green);color:#fff;box-shadow:0 6px 16px rgba(20,98,74,.25)}.cta .s{background:#fff;color:var(--green9);border:2px solid var(--green)}
.inst{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;background:#fbf6e6;border:1px solid #ecd994;border-radius:14px;padding:12px 16px;margin:12px 0 0;font-size:.92rem}
.inst a{font-weight:700;text-decoration:none;color:#7a5200;white-space:nowrap}
article h2{display:block}article p,article li{max-width:70ch}.src li{margin:4px 0;word-break:break-word}
.disc{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:12px;margin-top:28px}footer{padding:20px 16px 44px;color:var(--muted);font-size:.85rem;text-align:center}
#toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#18241f;color:#fff;padding:8px 14px;border-radius:8px;display:none}
@media(max-width:620px){.cta{grid-template-columns:1fr}.brand img{height:34px}.post{padding:16px}}"""
STLAB={'in_force':'tag-f','upcoming':'tag-u','announced':'tag-a','changed':'tag-x','consultation':'tag-c','proposed':'tag-c'}
def fmt(d,l):
    dt=datetime.date.fromisoformat(d)
    mi=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
    me=['January','February','March','April','May','June','July','August','September','October','November','December']
    return f"{dt.day} {(mi if l=='id' else me)[dt.month-1]} {dt.year}"
def share(url,title,l):
    t=T[l]; u=e(url); q=lambda s: __import__('urllib.parse').parse.quote(s,safe='')
    return f"""<div class="share" aria-label="{t['share']}"><span class="lbl">{t['share']}:</span><button type="button" onclick="nshare()">📤</button>
<a class="wa" href="https://wa.me/?text={q(title+' '+url)}" target="talented_ext" rel="noopener">WhatsApp</a>
<a href="https://www.facebook.com/sharer/sharer.php?u={q(url)}" target="talented_ext" rel="noopener">Facebook</a>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={q(url)}" target="talented_ext" rel="noopener">LinkedIn</a>
<a href="https://twitter.com/intent/tweet?url={q(url)}&text={q(title)}" target="talented_ext" rel="noopener">X</a>
<a href="https://t.me/share/url?url={q(url)}&text={q(title)}" target="talented_ext" rel="noopener">Telegram</a>
<button type="button" onclick="copyl()">🔗 {t['copy']}</button></div>"""
JS=lambda l:f"""<div id="toast">{T[l]['copied']}</div><script>
function nshare(){{if(navigator.share){{navigator.share({{title:document.title,url:location.href}}).catch(()=>{{}})}}else copyl()}}
function copyl(){{const u=location.href;(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(()=>{{const t=document.getElementById('toast');t.style.display='block';setTimeout(()=>t.style.display='none',1800)}}).catch(()=>prompt('{T[l]['copy']}',u))}}
</script>"""
def page(l,title,desc,url,alt_url,body,jsonld='',hero=''):
    return f"""<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self' https://info.talentededucationgroup.com; img-src 'self' https: data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'self'; form-action 'self'"><meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(url)}">
<link rel="alternate" hreflang="{l}" href="{e(url)}"><link rel="alternate" hreflang="{T[l]['langq']}" href="{e(alt_url)}"><link rel="alternate" type="application/rss+xml" title="Talented Blog" href="{SITE}/blog/feed.xml">
<meta property="og:type" content="article"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:image" content="{OG}"><meta name="twitter:card" content="summary_large_image">
{jsonld}<style>{CSS}</style></head><body><div class="top"><div class="wrap"><a class="brand" href="{SITE}/blog/{'' if l=='id' else 'en/'}"><img src="{SITE}/mocktest/logo.png" alt="" width="53" height="40"><span>Talented Education Group<small>PT. Pilar Pendidikan Internasional</small></span></a><a class="lang" href="{e(alt_url)}">🌐 {T[l]['lang']}</a></div></div>
{hero}<main class="wrap">{body}</main><footer>© Talented Education Group · <a href="{LINK}">linktr.ee/talentededucationgroup</a></footer>{JS(l)}</body></html>"""
def url_post(s,l): return f"{SITE}/blog/{s}/" if l=='id' else f"{SITE}/blog/en/{s}/"
def url_idx(l): return f"{SITE}/blog/" if l=='id' else f"{SITE}/blog/en/"
posts=sorted(B['posts'],key=lambda p:p['date'],reverse=True)
def write(path,txt):
    os.makedirs(os.path.dirname(path),exist_ok=True); open(path,'w',encoding='utf-8').write(txt)
FLAG=lambda c:''.join(chr(0x1F1E6+ord(x)-65) for x in ('GB' if c=='UK' else c)) if c and len(c)==2 and c.isalpha() else '🌐'
def clean_title(title,cname):
    for pre in (cname+':',cname+' -'):
        if title.startswith(pre):
            t=title[len(pre):].strip(); return t[:1].upper()+t[1:]
    return title
def news_list(l,k=6):
    out=[]
    for it in sorted(N['items'],key=lambda x:x['date'],reverse=True)[:k]:
        st=N['statuses'][it['status']][l]; c=N['countries'][it['country']][l]
        off=[x for x in it['links'] if x.get('official')]
        a=f'<a href="{e(off[0]["url"])}" target="talented_ext" rel="noopener">{"Sumber resmi ↗" if l=="id" else "Official source ↗"}</a>' if off else ''
        title=clean_title(it["title"][l],c)
        dl=''
        if it.get('deadline') and not any(w in title.lower() for w in ('tutup','closes','closing')):
            dl=f' ({"tutup" if l=="id" else "closes"} {fmt(it["deadline"],l)})'
        out.append(f'<li><span class="flag" aria-hidden="true">{FLAG(it["country"])}</span><span class="t">{e(title)}{dl}</span><span class="s"><span class="tag {STLAB.get(it["status"],"")}">{e(st)}</span><strong>{e(c)}</strong><span>{fmt(it["date"],l)}</span>{a}</span></li>')
    return '<ul class="news">'+''.join(out)+'</ul>'
NEWSALL='https://pricelist.talentededucationgroup.com/?tab=news'
def cta(l):
    t=T[l]
    sub1='Biaya kuliah, hidup, visa & OSHC dalam satu estimasi' if l=='id' else 'Tuition, living, visa & OSHC in one estimate'
    sub2='Chat dengan konsultan Talented' if l=='id' else 'Chat with a Talented consultant'
    inst='Sekolah atau layanan pelajar? Tampil di pricelist kami.' if l=='id' else 'A school or student service? Get featured on our pricelist.'
    return f'<div class="cta"><a class="p" href="{PRICE}?lang={l}">💰 {t["cta1"]} →<small>{sub1}</small></a><a class="s" href="{LINK}">💬 {t["cta2"]}<small>{sub2}</small></a></div><div class="inst"><span>🏫 {inst}</span><a href="{ADV}?lang={l}">{t["cta3"]} →</a></div>'
for l in ('id','en'):
    t=T[l]
    for p in posts:
        u=url_post(p['slug'],l); alt=url_post(p['slug'],t['langq'])
        others=''.join(f'<li><a href="{url_post(o["slug"],l)}">{e(o["title"][l])}</a></li>' for o in posts if o is not p)[:4000]
        src=''.join(f'<li><a href="{e(s["url"])}" target="talented_ext" rel="noopener">{e(s["label"])}</a></li>' for s in p['sources'])
        ld=json.dumps({"@context":"https://schema.org","@type":"Article","headline":p['title'][l],"description":p['description'][l],"datePublished":p['date'],"dateModified":p.get('updated',p['date']),"inLanguage":l,"mainEntityOfPage":u,"image":OG,"author":{"@type":"Organization","name":"Talented Education Group"},"publisher":{"@type":"Organization","name":"Talented Education Group"}},ensure_ascii=False)
        hero=f"""<section class="hero"><div class="wrap"><p class="meta"><a href="{url_idx(l)}">{t['back']}</a></p><h1>{e(p['title'][l])}</h1><p class="meta">{t['upd']}: {fmt(p.get('updated',p['date']),l)}</p>{share(u,p['title'][l],l)}</div></section>"""
        body=f"""<article>{p['body'][l]}</article><h2>{t['sources']}</h2><ul class="src">{src}</ul>
{cta(l)}
{share(u,p['title'][l],l)}{('<h2>'+t['other']+'</h2><ul>'+others+'</ul>') if others else ''}<p class="disc">{e(t['disc'])}</p>"""
        write(os.path.join(ROOT,'blog' if l=='id' else 'blog/en',p['slug'],'index.html'),page(l,p['title'][l]+' | Talented',p['description'][l],u,alt,body,f'<script type="application/ld+json">{ld}</script>',hero))
    def chips(p): return ''.join(f'<span class="chip">{FLAG(c)} {e(N["countries"].get(c,{}).get(l,c))}</span>' for c in p.get('countries',[])[:6])
    kick='Artikel terbaru' if l=='id' else 'Latest article'
    cards=''.join(f'<a class="post" href="{url_post(p["slug"],l)}"><span class="kick">{kick if i==0 else fmt(p["date"],l)}</span><h3>{e(p["title"][l])}</h3><p>{e(p["description"][l])}</p><span class="foot"><span class="chips">{chips(p)}</span><span class="read">{t["read"]} →</span></span></a>' for i,p in enumerate(posts))
    hero=f"""<section class="hero"><div class="wrap"><h1>{t['blog']}</h1><p>{t['sub']}</p>{share(url_idx(l),t['blog'],l)}</div></section>"""
    allnews='Semua berita →' if l=='id' else 'All news →'
    body=f"""{cards}<h2>📰 {t['news']}<a class="more" href="{NEWSALL}&lang={l}">{allnews}</a></h2>{news_list(l)}{cta(l)}<p class="disc">{e(t['disc'])}</p>"""
    write(os.path.join(ROOT,'blog' if l=='id' else 'blog/en','index.html'),page(l,t['blog']+' - Talented Education Group',t['sub'],url_idx(l),url_idx(t['langq']),body,'',hero))
# RSS
items=''.join(f"<item><title>{e(p['title']['id'])}</title><link>{url_post(p['slug'],'id')}</link><guid>{url_post(p['slug'],'id')}</guid><pubDate>{datetime.datetime.fromisoformat(p['date']).strftime('%a, %d %b %Y 08:00:00 +0700')}</pubDate><description>{e(p['description']['id'])}</description></item>" for p in posts)
write(os.path.join(ROOT,'blog/feed.xml'),f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Talented Blog</title><link>{SITE}/blog/</link><description>{e(T["id"]["sub"])}</description>{items}</channel></rss>')
urls=[url_idx('id'),url_idx('en')]+[url_post(p['slug'],l) for p in posts for l in ('id','en')]+[SITE+'/panduan/',SITE+'/les/']
last={url_post(p['slug'],l):p.get('updated',p['date']) for p in posts for l in ('id','en')}
sm=''.join(f'<url><loc>{u}</loc><lastmod>{last.get(u,posts[0]["date"])}</lastmod></url>' for u in urls)
write(os.path.join(ROOT,'sitemap.xml'),f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
write(os.path.join(ROOT,'robots.txt'),f'User-agent: *\nAllow: /\nDisallow: /data/\nDisallow: /sponsor/\nDisallow: /tim/\nSitemap: {SITE}/sitemap.xml\n\n# Mesin pencari & asisten AI boleh membaca halaman publik (bukan /data/)\nUser-agent: GPTBot\nUser-agent: OAI-SearchBot\nUser-agent: ChatGPT-User\nUser-agent: ClaudeBot\nUser-agent: Claude-SearchBot\nUser-agent: PerplexityBot\nUser-agent: Google-Extended\nUser-agent: Applebot-Extended\nUser-agent: CCBot\nAllow: /\nDisallow: /data/\nDisallow: /sponsor/\nDisallow: /tim/\n')
print('built',len(posts),'posts')
