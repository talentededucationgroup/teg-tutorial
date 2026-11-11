/* Talented Education Group - Free Mock Test engine (static, no data sent to any server) */
(function(){
'use strict';
const $=(s,e=document)=>e.querySelector(s), $$=(s,e=document)=>[...e.querySelectorAll(s)];
const Q=new URLSearchParams(location.search);
const BASE=(window.MOCK_BASE||'');
const SHARE_URL=(window.MOCK_SHARE_URL||'https://pricelist.talentededucationgroup.com/');
const LANGS=['id','en','th','vi','zh','ja','ko','km','fr','pt','es','de','it','nl','ru'];
let LANG=(Q.get('lang')||'').slice(0,2); if(!LANGS.includes(LANG)) LANG='id';
let UI={}, BANK=null, IDX=null, RUN=null;
const t=k=>(UI[k]&&(UI[k][LANG]||UI[k].en))||k;
const store={get(k,d){try{const v=localStorage.getItem('tegmock:'+k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem('tegmock:'+k,JSON.stringify(v))}catch(e){}}};
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function rnd(n){if(window.crypto&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n}return Math.floor(Math.random()*n)}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=rnd(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
function norm(s){return String(s||'').toLowerCase().replace(/[’']/g,"'").replace(/[^\p{L}\p{N}' ]+/gu,' ').replace(/\s+/g,' ').trim()}
async function J(u){const r=await fetch(u+(u.includes('?')?'&':'?')+'v='+(window.MOCK_V||'1'));if(!r.ok)throw new Error(u+' '+r.status);return r.json()}
function fmt(sec){sec=Math.max(0,Math.round(sec));const m=Math.floor(sec/60),s=sec%60;return (m<10?'0':'')+m+':'+(s<10?'0':'')+s}
function L(o){if(o==null)return'';if(typeof o==='string')return o;return o[LANG]||o.en||o.id||''}
// ---------- pick (random, avoid recently seen) ----------
function pick(testId,slot,count){
  const seen=store.get('seen:'+testId,{});
  const pool=slot.sets||slot.items||[];
  const fresh=shuffle(pool.filter(x=>!seen[x.id])), old=shuffle(pool.filter(x=>seen[x.id])).sort((a,b)=>seen[a.id]-seen[b.id]);
  return fresh.concat(old).slice(0,count||1);
}
function markSeen(testId,ids){const seen=store.get('seen:'+testId,{});const now=Date.now();ids.forEach(i=>seen[i]=now);store.set('seen:'+testId,seen)}
// ---------- views ----------
const app=()=>$('#app');
function header(title,sub){return `<header class="top"><a class="brand" href="?lang=${LANG}"><img src="${BASE}logo.png" alt="" onerror="this.remove()">Talented Education Group</a><div class="lang"><label>🌐 <select id="langSel">${LANGS.map(l=>`<option value="${l}"${l===LANG?' selected':''}>${UI._langnames?UI._langnames[l]:l}</option>`).join('')}</select></label></div></header>
<div class="hero"><p class="eyebrow">${esc(t('free_mock'))}</p><h1>${esc(title)}</h1>${sub?`<p class="sub">${sub}</p>`:''}</div>`}
function bindLang(){const s=$('#langSel');if(s)s.onchange=()=>{Q.set('lang',s.value);location.search=Q.toString()}}
function home(){
  document.title=t('free_mock')+' - Talented Education Group';
  app().innerHTML=header(t('free_mock'),esc(t('home_sub')))+`<div class="grid">${IDX.tests.map(x=>`<a class="card test" href="?test=${x.id}&lang=${LANG}"><span class="flag">${x.icon||''}</span><b>${esc(x.title)}</b><small>${esc(L(x.desc))}</small><span class="status ${x.ready?'ok':'soon'}">${x.ready?esc(t('available')):esc(t('coming_soon'))}</span></a>`).join('')}</div>
  <section class="note">${esc(t('disclaimer'))}</section>`+footer();
  bindLang();
}
function footer(){return `<footer><p>${esc(t('footer_vsa'))}</p><p><a class="btn ghost" href="https://linktr.ee/talentededucationgroup" target="_blank" rel="noopener">${esc(t('ask_consultant'))}</a></p><p class="small">© Talented Education Group · ${esc(t('privacy'))}</p></footer>`}
function testPage(){
  document.title=BANK.title+' - '+t('free_mock');
  const secs=BANK.sections;
  const hist=store.get('hist:'+BANK.id,[]);
  app().innerHTML=header(BANK.title,esc(L(BANK.desc)))+`
  <section class="card"><h2>${esc(t('choose_section'))}</h2>
  ${BANK.levels?`<label class="lvl">${esc(t('level'))}: <select id="lvl">${BANK.levels.map(l=>`<option>${esc(l)}</option>`).join('')}</select></label>`:''}
  <label class="namef"><b>${esc(t('your_name'))}</b><input id="candName" maxlength="60" autocomplete="name" placeholder="${esc(t('name_ph'))}" value="${esc(store.get('name',''))}"><small>${esc(t('name_note'))}</small><span class="warn" id="nameWarn" hidden>${esc(t('name_required'))}</span></label>
  <div class="secs">${secs.map((s,i)=>`<div class="sec"><div><b>${esc(L(s.title))}</b><small>${s.minutes} ${esc(t('minutes'))}${s.review_minutes?` + ${s.review_minutes} ${esc(t('review_min'))}`:''} · ${s.auto?esc(t('auto_marked')):esc(t('practice_only'))}</small><small>${esc(L(s.desc))}</small></div><button class="btn" data-sec="${i}">${esc(t('start'))}</button></div>`).join('')}</div>
  <p class="small">${esc(t('rules'))}</p>
  <label class="chk"><input type="checkbox" id="examMode" checked> ${esc(t('exam_mode'))}</label></section>
  ${hist.length?`<section class="card"><h2>${esc(t('history'))}</h2><ul class="hist">${hist.slice(-8).reverse().map(h=>`<li>${new Date(h.at).toLocaleString()} · ${esc(h.sec)} · <b>${esc(h.score)}</b></li>`).join('')}</ul><p class="small">${esc(t('history_note'))}</p></section>`:''}
  <p><a href="?lang=${LANG}">← ${esc(t('all_tests'))}</a></p>`+footer();
  bindLang();
  $$('[data-sec]').forEach(b=>b.onclick=()=>{const inp=$('#candName');const nm=(inp.value||'').replace(/\s+/g,' ').trim();if(nm.length<2){$('#nameWarn').hidden=false;inp.focus();inp.scrollIntoView({block:'center'});return}store.set('name',nm);startSection(+b.dataset.sec,$('#examMode').checked)});
}
// ---------- run ----------
function startSection(i,exam){
  const sec=BANK.sections[i]; const parts=[]; const ids=[];
  (sec.slots||[]).forEach(sl=>{const got=pick(BANK.id,sl,sl.count||1);got.forEach(g=>{ids.push(g.id);parts.push(Object.assign({slot:sl.id,slotTitle:sl.title},JSON.parse(JSON.stringify(g))))})});
  let n=0; parts.forEach(p=>(p.questions||[]).forEach(q=>{q.n=++n; if(q.options&&q.shuffle!==false&&['mcq','multi'].includes(q.type)){const idx=shuffle(q.options.map((_,k)=>k));q._map=idx;q._opts=idx.map(k=>q.options[k])}else q._opts=q.options}));
  RUN={name:store.get('name',''),rid:'TEG-'+BANK.id.toUpperCase()+'-'+new Date().toISOString().slice(2,10).replace(/-/g,'')+'-'+(Date.now().toString(36).slice(-3)+rnd(1296).toString(36)).toUpperCase(),sec,secIdx:i,parts,ids,answers:{},exam,start:Date.now(),limit:(sec.minutes+(sec.review_minutes||0))*60,cur:0,done:false,audioPlayed:{}};
  window.onbeforeunload=()=>RUN&&!RUN.done?true:null;
  renderRun(); tick();
}
function tick(){if(!RUN||RUN.done)return;const left=RUN.limit-(Date.now()-RUN.start)/1000;const el=$('#timer');if(el){el.textContent=fmt(left);el.classList.toggle('warn',left<300)}if(left<=0){finish(true);return}setTimeout(tick,500)}
function qHTML(q,p){
  const a=RUN.answers[q.n];const nm='q'+q.n;
  const head=`<div class="qn">${q.n}</div>`;
  const pr=q.prompt?`<div class="qp">${q.prompt}</div>`:'';
  switch(q.type){
    case 'mcq': return `<div class="q">${head}<div>${pr}${q._opts.map((o,k)=>`<label class="opt"><input type="radio" name="${nm}" value="${k}"${a==k?' checked':''}> <span>${String.fromCharCode(65+k)}. ${o}</span></label>`).join('')}</div></div>`;
    case 'multi': return `<div class="q">${head}<div>${pr}<small>${esc(t('choose'))} ${q.choose}</small>${q._opts.map((o,k)=>`<label class="opt"><input type="checkbox" name="${nm}" value="${k}"${a&&a.includes(k)?' checked':''}> <span>${String.fromCharCode(65+k)}. ${o}</span></label>`).join('')}</div></div>`;
    case 'tfng': case 'match': { const opts=q.options||p.options||(q.type==='tfng'?['TRUE','FALSE','NOT GIVEN']:[]);
      return `<div class="q">${head}<div>${pr}<select name="${nm}"><option value="">—</option>${opts.map(o=>{const v=typeof o==='string'?o:o.v;const lab=typeof o==='string'?o:(o.v+' '+o.t);return `<option value="${esc(v)}"${a===v?' selected':''}>${esc(lab)}</option>`}).join('')}</select></div></div>`}
    case 'gap': return `<div class="q">${head}<div>${pr.replace('___',`<input class="gap" name="${nm}" value="${esc(a||'')}" autocomplete="off" autocapitalize="off" spellcheck="false">`)}${pr.includes('___')?'':`<input class="gap" name="${nm}" value="${esc(a||'')}" autocomplete="off" spellcheck="false">`}</div></div>`;
    case 'order': { const cur=a||shuffle(q.items.map((_,k)=>k)); RUN.answers[q.n]=cur;
      return `<div class="q">${head}<div>${pr}<ol class="order" data-n="${q.n}">${cur.map((k,pos)=>`<li><span>${q.items[k]}</span><span class="ob"><button type="button" data-mv="-1" data-pos="${pos}" aria-label="up">▲</button><button type="button" data-mv="1" data-pos="${pos}" aria-label="down">▼</button></span></li>`).join('')}</ol></div></div>`}
    case 'dictation': return `<div class="q">${head}<div>${pr}<textarea name="${nm}" rows="2" spellcheck="false">${esc(a||'')}</textarea></div></div>`;
    case 'highlight': { const sel=a||[]; return `<div class="q">${head}<div>${pr}<p class="hl" data-n="${q.n}">${q.text.split(' ').map((w,k)=>`<span data-k="${k}" class="${sel.includes(k)?'on':''}">${esc(w)}</span>`).join(' ')}</p></div></div>`}
    case 'cloze': { let k=0; const vals=a||{}; const html=q.text.replace(/\[\[(\d+)\]\]/g,(m,id)=>{const b=q.blanks[id];k++;return b.options?`<select data-cl="${q.n}" data-b="${id}"><option value="">—</option>${b.options.map(o=>`<option${vals[id]===o?' selected':''}>${esc(o)}</option>`).join('')}</select>`:`<input class="gap" data-cl="${q.n}" data-b="${id}" value="${esc(vals[id]||'')}" autocomplete="off" spellcheck="false">`});
      return `<div class="q">${head}<div>${pr}<p class="cloze">${html}</p></div></div>`}
    case 'essay': return `<div class="q wide">${head}<div>${pr}${q.table||''}<textarea class="essay" name="${nm}" rows="14">${esc(a||'')}</textarea><small class="wc" data-n="${q.n}">0 ${esc(t('words'))} · min ${q.min_words}</small></div></div>`;
    case 'speak': return `<div class="q wide">${head}<div>${pr}<small>${esc(t('prep'))}: ${q.prep||0}s · ${esc(t('speak_time'))}: ${q.speak||0}s</small><div class="rec" data-n="${q.n}"><button type="button" class="btn small" data-rec>${esc(t('record'))}</button> <span class="recst"></span></div></div></div>`;
  }
  return '';
}
function renderRun(){
  const p=RUN.parts[RUN.cur]; const sec=RUN.sec;
  const tabs=RUN.parts.map((x,k)=>`<button class="tab${k===RUN.cur?' on':''}" data-tab="${k}">${esc(L(x.title)||x.slotTitle||('Part '+(k+1)))}</button>`).join('');
  const groups=[]; (p.questions||[]).forEach(q=>{const g=q.group||'';if(!groups.length||groups[groups.length-1].g!==g)groups.push({g,qs:[]});groups[groups.length-1].qs.push(q)});
  const audio=p.audio?`<div class="audio"><audio id="aud" preload="auto" src="${esc(BASE+p.audio)}" ${RUN.exam?'':'controls'}></audio>${RUN.exam?`<button class="btn" id="play"${RUN.audioPlayed[p.id]?' disabled':''}>${RUN.audioPlayed[p.id]?esc(t('played')):'▶ '+esc(t('play_once'))}</button>`:''}<small>${esc(RUN.exam?t('audio_once'):t('audio_practice'))}</small></div>`:'';
  const passage=p.passage?`<article class="passage">${p.passage}</article>`:'';
  app().innerHTML=`<div class="runbar"><b>${esc(BANK.title)} · ${esc(L(sec.title))}</b><span id="timer" class="timer">--:--</span><button class="btn" id="submit">${esc(t('submit'))}</button></div>
  <nav class="tabs">${tabs}</nav>
  <div class="run ${p.passage?'split':''}">${passage}<div class="qs">${p.instructions?`<p class="ins">${p.instructions}</p>`:''}${audio}${groups.map(g=>`${g.g?`<p class="ins">${g.g}</p>`:''}${g.qs.map(q=>qHTML(q,p)).join('')}`).join('')}
  <div class="navbtns">${RUN.cur>0?`<button class="btn ghost" data-go="-1">← ${esc(t('prev'))}</button>`:''}${RUN.cur<RUN.parts.length-1?`<button class="btn" data-go="1">${esc(t('next'))} →</button>`:`<button class="btn" id="submit2">${esc(t('submit'))}</button>`}</div></div></div>
  <div id="confirm" class="modal" hidden><div class="box"><p>${esc(t('confirm_submit'))}</p><p id="unans" class="small"></p><button class="btn" id="yes">${esc(t('submit'))}</button> <button class="btn ghost" id="no">${esc(t('back'))}</button></div></div>`;
  bindRun(); tickOnce();
}
function tickOnce(){const left=RUN.limit-(Date.now()-RUN.start)/1000;const el=$('#timer');if(el)el.textContent=fmt(left)}
function save(e){const el=e.target;const m=(el.name||'').match(/^q(\d+)$/);
  if(m){const n=+m[1];if(el.type==='checkbox'){RUN.answers[n]=$$(`input[name="${el.name}"]:checked`).map(x=>+x.value)}else if(el.type==='radio'){RUN.answers[n]=+el.value}else RUN.answers[n]=el.value;}
  if(el.dataset.cl){const n=+el.dataset.cl;RUN.answers[n]=RUN.answers[n]||{};RUN.answers[n][el.dataset.b]=el.value}
  if(el.classList.contains('essay')){const w=el.value.trim()?el.value.trim().split(/\s+/).length:0;const n=el.name.slice(1);const s=$(`.wc[data-n="${n}"]`);if(s)s.textContent=w+' '+t('words')+' · min '+s.textContent.split('min ')[1]}
}
function bindRun(){
  app().addEventListener('input',save); app().addEventListener('change',save);
  $$('[data-tab]').forEach(b=>b.onclick=()=>{RUN.cur=+b.dataset.tab;renderRun();scrollTo(0,0)});
  $$('[data-go]').forEach(b=>b.onclick=()=>{RUN.cur+=+b.dataset.go;renderRun();scrollTo(0,0)});
  $$('.order button').forEach(b=>b.onclick=()=>{const ol=b.closest('.order');const n=+ol.dataset.n;const a=RUN.answers[n];const pos=+b.dataset.pos,to=pos+(+b.dataset.mv);if(to<0||to>=a.length)return;[a[pos],a[to]]=[a[to],a[pos]];renderRun()});
  $$('.hl span').forEach(s=>s.onclick=()=>{const n=+s.parentNode.dataset.n;const k=+s.dataset.k;const a=RUN.answers[n]=RUN.answers[n]||[];const i=a.indexOf(k);if(i>=0)a.splice(i,1);else a.push(k);s.classList.toggle('on')});
  $$('.essay').forEach(el=>save({target:el}));
  const pl=$('#play'),au=$('#aud');
  if(pl&&au){pl.onclick=()=>{const p=RUN.parts[RUN.cur];RUN.audioPlayed[p.id]=1;pl.disabled=true;pl.textContent=t('playing');au.play().catch(()=>{pl.disabled=false;RUN.audioPlayed[p.id]=0;pl.textContent='▶ '+t('play_once')});au.onended=()=>{pl.textContent=t('played')}}}
  $$('[data-rec]').forEach(b=>b.onclick=()=>record(b));
  const ask=()=>{const tot=countQ(),ans=Object.keys(RUN.answers).length;$('#unans').textContent=(RUN.sec.auto?`${ans}/${tot} `+t('answered'):'');$('#confirm').hidden=false};
  $('#submit').onclick=ask; const s2=$('#submit2'); if(s2)s2.onclick=ask;
  $('#no').onclick=()=>$('#confirm').hidden=true; $('#yes').onclick=()=>finish(false);
}
function countQ(){return RUN.parts.reduce((s,p)=>s+(p.questions||[]).length,0)}
let mediaRec=null;
async function record(b){const box=b.parentNode;const st=$('.recst',box);
  if(mediaRec&&mediaRec.state==='recording'){mediaRec.stop();return}
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true});const ch=[];mediaRec=new MediaRecorder(s);mediaRec.ondataavailable=e=>ch.push(e.data);
    mediaRec.onstop=()=>{s.getTracks().forEach(x=>x.stop());const url=URL.createObjectURL(new Blob(ch));st.innerHTML=`<audio controls src="${url}"></audio> <small>${esc(t('rec_local'))}</small>`;b.textContent=t('record_again')};
    mediaRec.start();b.textContent='■ '+t('stop');st.textContent=t('recording')}catch(e){st.textContent=t('mic_denied')}}
// ---------- scoring ----------
function scoreQ(q){const a=RUN.answers[q.n];
  switch(q.type){
    case 'mcq': return {got:(a!=null&&(q._map?q._map[a]:a)===q.answer)?1:0,max:1};
    case 'multi': {const sel=(a||[]).map(k=>q._map?q._map[k]:k);const right=sel.filter(k=>q.answer.includes(k)).length;const wrong=sel.length-right;return {got:q.negative?Math.max(0,right-wrong):(sel.length>q.choose?Math.max(0,right-(sel.length-q.choose)):right),max:q.answer.length}}
    case 'tfng': case 'match': return {got:a&&norm(a)===norm(q.answer)?1:0,max:1};
    case 'gap': {const acc=[].concat(q.answer).map(norm);return {got:acc.includes(norm(a))?1:0,max:1}}
    case 'order': {const ans=q.answer||q.items.map((_,k)=>k);let g=0;for(let i=0;i<ans.length-1;i++){const aa=a||[];const x=aa.indexOf(ans[i]);if(x>=0&&aa[x+1]===ans[i+1])g++}return {got:g,max:ans.length-1}}
    case 'dictation': {const want=norm(q.answer).split(' ');const have=norm(a).split(' ');const pool=have.slice();let g=0;want.forEach(w=>{const i=pool.indexOf(w);if(i>=0){g++;pool.splice(i,1)}});return {got:g,max:want.length}}
    case 'highlight': {const sel=a||[];const r=sel.filter(k=>q.answer.includes(k)).length;return {got:Math.max(0,r-(sel.length-r)),max:q.answer.length}}
    case 'cloze': {let g=0,m=0;Object.entries(q.blanks).forEach(([id,b])=>{m++;const v=(a||{})[id];if(v&&[].concat(b.answer).map(norm).includes(norm(v)))g++});return {got:g,max:m}}
  }
  return {got:0,max:0};
}
function conv(sec,raw,max){const sc=sec.score;if(!sc)return '';
  if(sc.type==='table'){const v=raw*(sc.base||max)/max;for(const [min,band] of sc.table){if(v>=min)return band}return sc.table[sc.table.length-1][1]}
  if(sc.type==='scale'){return Math.round(sc.min+(sc.max-sc.min)*raw/max)}
  if(sc.type==='pct'){return Math.round(100*raw/max)+'%'}
  return '';}
function finish(timeout){if(!RUN||RUN.done)return;RUN.done=true;window.onbeforeunload=null;if(mediaRec&&mediaRec.state==='recording')mediaRec.stop();
  const sec=RUN.sec;let raw=0,max=0;const rows=[];
  RUN.parts.forEach(p=>(p.questions||[]).forEach(q=>{if(!sec.auto){rows.push({q,p});return}const s=scoreQ(q);raw+=s.got;max+=s.max;rows.push({q,p,s})}));
  markSeen(BANK.id,RUN.ids);
  const est=sec.auto?conv(sec,raw,max):'';
  if(sec.auto){const h=store.get('hist:'+BANK.id,[]);h.push({at:Date.now(),sec:L(sec.title),score:`${raw}/${max}${est!==''?' · '+(sec.score.label||'')+' '+est:''}`});store.set('hist:'+BANK.id,h.slice(-30))}
  const used=Math.min(RUN.limit,(Date.now()-RUN.start)/1000);
  app().innerHTML=header(BANK.title+' · '+L(sec.title),'')+`<section class="card result">${timeout?`<p class="warn">${esc(t('time_up'))}</p>`:''}
  ${reportHTML(sec,raw,max,est,used,rows)}
  <div class="share"><b>${esc(t('send_result'))}</b> <a class="btn wa" id="shWA" target="_blank" rel="noopener">WhatsApp</a> <a class="btn ghost" id="shMail">Email</a> <button class="btn ghost" id="shPrint">PDF / ${esc(t('print'))}</button><small>${esc(t('send_note'))}</small></div>
  <p><button class="btn" id="again">${esc(t('try_again'))}</button> <a class="btn ghost" href="?test=${BANK.id}&lang=${LANG}">${esc(t('other_sections'))}</a> <a class="btn ghost" href="https://linktr.ee/talentededucationgroup" target="_blank" rel="noopener">${esc(sec.auto?t('ask_consultant'):t('ask_review'))}</a></p></section>
  <section class="card"><h2>${esc(t('review'))}</h2>${RUN.parts.map(p=>`<details${sec.auto?'':' open'}><summary>${esc(L(p.title)||p.slotTitle)}</summary>${p.transcript?`<details class="tr"><summary>${esc(t('transcript'))}</summary><div class="trx">${p.transcript}</div></details>`:''}
  ${(p.questions||[]).map(q=>{const r=rows.find(x=>x.q===q);return reviewRow(q,r&&r.s)}).join('')}</details>`).join('')}</section>`+footer();
  bindLang(); $('#again').onclick=()=>startSection(RUN.secIdx,RUN.exam); scrollTo(0,0);
  const txt=summaryText(sec,raw,max,est,used,rows);
  $('#shWA').href='https://wa.me/?text='+encodeURIComponent(txt.slice(0,1800));
  $('#shMail').href='mailto:?subject='+encodeURIComponent(t('free_mock')+' - '+BANK.title+' '+L(sec.title))+'&body='+encodeURIComponent(txt);
  $('#shPrint').onclick=()=>{$$('details').forEach(d=>d.open=true);window.print()};
}
function partStats(rows){const g=[];rows.forEach(r=>{if(!r.s)return;const k=r.p.slotTitle||L(r.p.title);let o=g.find(x=>x.k===k);if(!o){o={k,got:0,max:0};g.push(o)}o.got+=r.s.got;o.max+=r.s.max});return g}
function fbKey(p){return p>=0.8?'fb_strong':(p>=0.5?'fb_dev':'fb_focus')}
function reportHTML(sec,raw,max,est,used,rows){
  const d=new Date();const ps=sec.auto?partStats(rows):[];
  const sc=sec.auto?`<div class="rp-score"><div><small>${esc(sec.score&&sec.score.label||t('estimate'))}</small><b>${est!==''?esc(est):'-'}</b></div><div><small>${esc(t('score'))}</small><b>${raw} / ${max}</b></div><div><small>${esc(t('time_used'))}</small><b>${fmt(used)}</b></div></div>`:`<p class="rp-prac">${esc(t('practice_done'))}</p>`;
  const tb=ps.length?`<h3>${esc(t('breakdown'))}</h3><table class="rp-tb"><tr><th>${esc(t('section'))}</th><th>${esc(t('overall'))}</th><th></th><th>${esc(t('feedback'))}</th></tr>${ps.map(o=>{const p=o.max?o.got/o.max:0;return `<tr><td>${esc(o.k)}</td><td>${o.got}/${o.max}</td><td><span class="bar"><i style="width:${Math.round(p*100)}%"></i></span></td><td>${esc(t(fbKey(p)))}</td></tr>`}).join('')}</table>`:'';
  return `<div class="report" id="report"><div class="wm" aria-hidden="true"></div>
  <p class="rp-org">${esc(t('organiser'))}</p>
  <div class="rp-head"><img src="${BASE}logo.png" alt="Talented Education Group" onerror="this.remove()"><div><b>${esc(t('report_title'))}</b><span>${esc(BANK.title)} · ${esc(L(sec.title))}</span></div><img src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"></div>
  <dl class="rp-meta"><div><dt>${esc(t('candidate'))}</dt><dd class="rp-name">${esc(RUN.name||'-')}</dd></div><div><dt>${esc(t('date'))}</dt><dd>${d.toLocaleDateString(LANG,{day:'2-digit',month:'short',year:'numeric'})}</dd></div><div><dt>${esc(t('report_no'))}</dt><dd>${esc(RUN.rid)}</dd></div><div><dt>${esc(t('section'))}</dt><dd>${esc(L(sec.title))}</dd></div></dl>
  ${sc}${tb}
  <p class="small">${esc(L(sec.score&&sec.score.note)||t('estimate_note'))}</p>
  <div class="rp-foot"><img src="${BASE}qr-pricelist.png" alt="QR pricelist.talentededucationgroup.com"><p>${esc(t('try_free'))}<br><a href="${SHARE_URL}" target="_blank" rel="noopener">${esc(SHARE_URL.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></p></div>
  <p class="rp-off">${esc(t('not_official'))}</p></div>`}
function summaryText(sec,raw,max,est,used,rows){
  const lines=[`${t('report_title')} - ${BANK.title} · ${L(sec.title)}`,`${t('candidate')}: ${RUN.name||'-'}`,`${t('report_no')}: ${RUN.rid}`,`${t('date')}: ${new Date().toLocaleString()}`,t('organiser')];
  if(sec.auto){lines.push(`${t('score')}: ${raw}/${max}`+(est!==''?` · ${sec.score.label||t('estimate')}: ${est}`:''));lines.push(`${t('time_used')}: ${fmt(used)}`);
    partStats(rows).forEach(o=>lines.push(`- ${o.k}: ${o.got}/${o.max} (${t(fbKey(o.max?o.got/o.max:0))})`));
    const wrong=rows.filter(r=>r.s&&r.s.got<r.s.max).map(r=>`${r.q.n}: ${showAns(r.q)}`.slice(0,60));
    if(wrong.length){lines.push('');lines.push(t('to_review')+':');lines.push(...wrong.slice(0,25));if(wrong.length>25)lines.push('…')}
    lines.push('');lines.push(L(sec.score&&sec.score.note)||t('estimate_note'));
  } else {RUN.parts.forEach(p=>(p.questions||[]).forEach(q=>{const a=RUN.answers[q.n];if(q.type==='essay'){lines.push('');lines.push(`${q.n}. ${(q.prompt||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().slice(0,160)}`);lines.push(`(${yours(q)})`);if(a)lines.push(a)}}))}
  lines.push('');lines.push(t('not_official'));lines.push('');lines.push(t('try_free'));lines.push(SHARE_URL);
  return lines.join('\n');}
function showAns(q){switch(q.type){
  case 'mcq': return String.fromCharCode(65+(q._map?q._map.indexOf(q.answer):q.answer))+'. '+q.options[q.answer];
  case 'multi': return q.answer.map(k=>String.fromCharCode(65+(q._map?q._map.indexOf(k):k))+'. '+q.options[k]).join(' / ');
  case 'gap': return [].concat(q.answer)[0];
  case 'order': return (q.answer||q.items.map((_,k)=>k)).map(k=>q.items[k]).join(' → ');
  case 'highlight': return q.answer.map(k=>q.text.split(' ')[k]).join(', ');
  case 'cloze': return Object.values(q.blanks).map(b=>[].concat(b.answer)[0]).join(' / ');
  case 'essay': case 'speak': return '';
  default: return q.answer;}}
function yours(q){const a=RUN.answers[q.n];if(a==null||a===''||(Array.isArray(a)&&!a.length))return '—';
  switch(q.type){case 'mcq':return String.fromCharCode(65+a);case 'multi':return a.map(k=>String.fromCharCode(65+k)).join(', ');case 'order':return a.map(k=>q.items[k]).join(' → ');case 'highlight':return a.map(k=>q.text.split(' ')[k]).join(', ');case 'cloze':return Object.values(a).join(' / ');case 'essay':return (a.trim().split(/\s+/).length)+' '+t('words');default:return a}}
function reviewRow(q,s){const ok=s?(s.got===s.max?'ok':(s.got>0?'part':'no')):'na';
  return `<div class="rv ${ok}"><div class="qn">${q.n}</div><div>${q.prompt?`<div class="qp">${q.prompt.replace('___','____')}</div>`:''}
  ${q.type==='essay'||q.type==='speak'?`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q))}</p>${q.checklist?`<p><b>${esc(t('checklist'))}:</b></p><ul>${q.checklist.map(c=>`<li>${c}</li>`).join('')}</ul>`:''}${q.model?`<details><summary>${esc(t('model_answer'))}</summary><div class="model">${q.model}</div></details>`:''}`
  :`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q))} · <b>${esc(t('correct_answer'))}:</b> ${esc(showAns(q))}${s?` · ${s.got}/${s.max}`:''}</p>`}${q.explain?`<p class="small">${q.explain}</p>`:''}</div></div>`}
// ---------- boot ----------
(async function(){
  try{UI=await J(BASE+'banks/ui.json?t='+Math.floor(Date.now()/6e5));IDX=await J(BASE+'banks/index.json');window.MOCK_V=IDX.version||'1'}catch(e){app().innerHTML='<p>Load error. Please refresh.</p>';return}
  document.documentElement.lang=LANG;
  const id=Q.get('test');
  if(!id){home();return}
  const meta=IDX.tests.find(x=>x.id===id);
  if(!meta||!meta.ready){home();return}
  try{BANK=await J(BASE+'banks/'+meta.file)}catch(e){app().innerHTML='<p>Load error.</p>';return}
  testPage();
})();
})();
