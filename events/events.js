/* Talented - Event & expo mendatang (data: https://info.talentededucationgroup.com/data/events.json).
   Dipakai halaman info.talentededucationgroup.com/events/ (bisa di-embed di website lain) dan web pricelist.
   Event yang sudah lewat (end < hari ini WIB) otomatis tidak tampil. */
(function () {
  const SRC = 'https://info.talentededucationgroup.com/data/events.json';
  const LOC = {id: 'id-ID', en: 'en-AU', th: 'th-TH', vi: 'vi-VN', zh: 'zh-CN', ja: 'ja-JP', ko: 'ko-KR', km: 'km-KH', fr: 'fr-FR', pt: 'pt-BR', es: 'es-ES', de: 'de-DE', it: 'it-IT', nl: 'nl-NL', ru: 'ru-RU'};
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const code = l => { l = String(l || 'id').toLowerCase(); if (l.startsWith('pt')) return 'pt'; return LOC[l] ? l : (LOC[l.split('-')[0]] ? l.split('-')[0] : 'en'); };
  const loc = (o, l) => o && typeof o === 'object' ? (o[l] || o.en || o.id || '') : (o || '');
  const todayWIB = () => new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10);
  const css = `.tev{margin:18px 0}.tev h2{margin:0 0 10px;font-size:1.25rem}.tev-list{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr))}
.tev-card{display:flex;gap:14px;background:#fff;border:1px solid #e4e0d6;border-top:4px solid #c9a227;border-radius:14px;padding:14px;color:#1d2b3a;min-width:0}
.tev-date{flex:none;width:76px;text-align:center;background:#14213d;color:#fff;border-radius:12px;padding:8px 4px;align-self:flex-start}
.tev-date b{display:block;font-size:1.6rem;line-height:1.05}.tev-date span{display:block;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.tev-body{min-width:0;display:flex;flex-direction:column;gap:5px}.tev-body h3{margin:0;font-size:1.02rem;line-height:1.3}
.tev-meta{font-size:.88rem;color:#4b5563;overflow-wrap:anywhere}.tev-booth{font-size:.86rem;font-weight:700;color:#7a5a00;background:#fff7e0;border-radius:8px;padding:5px 8px}
.tev-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}.tev-btns a,.tev-btns button{font:inherit;font-size:.86rem;font-weight:700;border-radius:9px;padding:8px 12px;cursor:pointer;text-decoration:none;border:1.5px solid #14213d}
.tev-btns .tev-ask{background:#14213d;color:#fff}.tev-btns .tev-ics{background:#fff;color:#14213d}.tev-none{color:#6b7280}`;
  let cache = null;
  const load = () => cache || (cache = fetch(SRC + '?t=' + Math.floor(Date.now() / 3600e3), {cache: 'no-store'}).then(r => r.json()));
  function fmt(d, l, o) { try { return new Date(d + 'T00:00:00+07:00').toLocaleDateString(LOC[l], Object.assign({timeZone: 'Asia/Jakarta'}, o)); } catch (e) { return d; } }
  function range(e, l) { return e.start === e.end ? fmt(e.start, l, {weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'}) : fmt(e.start, l, {day: 'numeric', month: 'long'}) + ' – ' + fmt(e.end, l, {day: 'numeric', month: 'long', year: 'numeric'}); }
  function ics(e, l) {
    const d = s => s.replace(/-/g, ''), end = new Date(e.end + 'T00:00:00Z'); end.setUTCDate(end.getUTCDate() + 1);
    const t = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Talented Education Group//Events//ID', 'BEGIN:VEVENT', 'UID:' + e.id + '@talentededucationgroup.com',
      'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z', 'DTSTART;VALUE=DATE:' + d(e.start), 'DTEND;VALUE=DATE:' + end.toISOString().slice(0, 10).replace(/-/g, ''),
      'SUMMARY:' + loc(e.title, l).replace(/[,;]/g, ' '), 'LOCATION:' + (e.venue || '').replace(/[,;]/g, ' '), 'DESCRIPTION:' + (e.time || '') + ' - Talented Education Group https://linktr.ee/talentededucationgroup', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    return 'data:text/calendar;charset=utf-8,' + encodeURIComponent(t);
  }
  async function mount(box, lang, opt = {}) {
    if (!box) return; const l = code(lang);
    if (!document.getElementById('tev-css')) { const s = document.createElement('style'); s.id = 'tev-css'; s.textContent = css; document.head.append(s); }
    try {
      const data = await load(), L = data.labels || {}, t = todayWIB();
      const up = (data.items || []).filter(e => (e.end || e.start) >= t).sort((a, b) => a.start.localeCompare(b.start));
      if (!up.length) { box.innerHTML = opt.showEmpty ? `<section class="tev"><h2>${esc(loc(L.heading, l))}</h2><p class="tev-none">${esc(loc(L.none, l))}</p></section>` : ''; box.hidden = !opt.showEmpty; return; }
      box.hidden = false;
      box.innerHTML = `<section class="tev" aria-label="${esc(loc(L.heading, l))}">${opt.noHeading ? '' : `<h2>📅 ${esc(loc(L.heading, l))}</h2>`}<div class="tev-list">${up.map(e => `
        <article class="tev-card"><div class="tev-date"><b>${esc(fmt(e.start, l, {day: 'numeric'}))}${e.end !== e.start ? '–' + esc(fmt(e.end, l, {day: 'numeric'})) : ''}</b><span>${esc(fmt(e.start, l, {month: 'short'}))} ${esc(e.start.slice(0, 4))}</span></div>
        <div class="tev-body"><h3>${esc(loc(e.title, l))}</h3>
        <div class="tev-meta">🗓️ ${esc(range(e, l))} · ⏰ ${esc(e.time || '')}</div>
        <div class="tev-meta">📍 ${esc(e.venue || e.city || '')}</div>
        ${e.audience ? `<div class="tev-meta">🎓 ${esc(loc(L.who, l))}: ${esc(loc(e.audience, l))} · ${esc(loc(L.free, l))}</div>` : ''}
        <div class="tev-booth">⭐ ${esc(loc(L.booth, l))}</div>
        <div class="tev-btns"><a class="tev-ask" href="https://linktr.ee/talentededucationgroup" target="_blank" rel="noopener">💬 ${esc(loc(L.ask, l))}</a><a class="tev-ics" href="${ics(e, l)}" download="${esc(e.id)}.ics">📅 ${esc(loc(L.calendar, l))}</a></div></div></article>`).join('')}</div></section>`;
    } catch (err) { box.innerHTML = ''; box.hidden = true; }
  }
  window.TalentedEvents = {mount, load};
})();
