// Service worker Kit Konten Tim: hanya agar bisa dipasang sebagai aplikasi; data selalu diambil dari jaringan.
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{});
