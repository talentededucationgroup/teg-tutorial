// Service worker Kit Konten Tim v9 (26/11/2026): data selalu diambil dari jaringan; asisten.js & pembaca screenshot (ocr/) disimpan di cache agar tetap jalan saat sinyal lemah.
const CACHE='kit-tim-v9';
const PRE=['/tim/asisten.js?v=7'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(PRE)).catch(()=>{}))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==CACHE).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);
  if(u.pathname.startsWith('/tim/ocr/')){e.respondWith(caches.match(e.request).then(h=>h||fetch(e.request).then(r=>{if(r.ok){const c=r.clone();caches.open(CACHE).then(x=>x.put(e.request,c))}return r})));return}
  if(u.pathname==='/tim/asisten.js'){e.respondWith(fetch(e.request).then(r=>{if(r.ok){const c=r.clone();caches.open(CACHE).then(x=>x.put(e.request,c))}return r}).catch(()=>caches.match(e.request)));return}
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))});
