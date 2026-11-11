/* Talented Education Group - Free Mock Test engine (static, no data sent to any server) */
(function(){
'use strict';
const $=(s,e=document)=>e.querySelector(s), $$=(s,e=document)=>[...e.querySelectorAll(s)];
const Q=new URLSearchParams(location.search);
const BASE=(window.MOCK_BASE||'');
const SHARE_URL=(window.MOCK_SHARE_URL||'https://pricelist.talentededucationgroup.com/');
const LANGS=['id','en','th','vi','zh','ja','ko','km','fr','pt','es','de','it','nl','ru'];
let LANG=(Q.get('lang')||'').slice(0,2); if(!LANGS.includes(LANG)) LANG='id';
let UI={}, BANK=null, IDX=null, RUN=null, FULL=null;
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
  <section class="card fullcard"><h2>${esc(t('full_test'))}</h2><p class="small">${esc(t('full_desc'))}</p><div class="secs">${fullsOf().map((f,k)=>`<div class="sec"><div><b>${esc(L(f.title))}</b><small>${f.sections.reduce((a,i)=>a+secs[i].minutes+(secs[i].review_minutes||0),0)} ${esc(t('minutes'))} · ${f.sections.length} ${esc(t('sections_n'))}: ${esc(f.sections.map(i=>L(secs[i].title)).join(' → '))}</small></div><button class="btn gold" data-full="${k}">${esc(t('start_full'))}</button></div>`).join('')}</div></section>
  <section class="card"><h2>${esc(t('choose_section'))}</h2>
  ${BANK.levels?`<label class="lvl">${esc(t('level'))}: <select id="lvl">${BANK.levels.map(l=>`<option>${esc(l)}</option>`).join('')}</select></label>`:''}
  <label class="namef"><b>${esc(t('your_name'))}</b><input id="candName" maxlength="60" autocomplete="name" placeholder="${esc(t('name_ph'))}" value="${esc(store.get('name',''))}"><small>${esc(t('name_note'))}</small><span class="warn" id="nameWarn" hidden>${esc(t('name_required'))}</span></label>
  <div class="secs">${secs.map((s,i)=>`<div class="sec"><div><b>${esc(L(s.title))}</b><small>${s.minutes} ${esc(t('minutes'))}${s.review_minutes?` + ${s.review_minutes} ${esc(t('review_min'))}`:''} · ${s.auto?esc(t('auto_marked')):esc(t('practice_only'))}</small><small>${esc(L(s.desc))}</small></div><button class="btn" data-sec="${i}">${esc(t('start'))}</button></div>`).join('')}</div>
  <p class="small">${esc(t('rules'))}</p>
  <label class="chk"><input type="checkbox" id="examMode" checked> ${esc(t('exam_mode'))}</label></section>
  ${hist.length?`<section class="card"><h2>${esc(t('history'))}</h2><ul class="hist">${hist.slice(-8).reverse().map(h=>`<li>${new Date(h.at).toLocaleString()} · ${esc(h.sec)} · <b>${esc(h.score)}</b></li>`).join('')}</ul><p class="small">${esc(t('history_note'))}</p></section>`:''}
  <p><a href="?lang=${LANG}">← ${esc(t('all_tests'))}</a></p>`+footer();
  bindLang();
  const nameOk=()=>{const inp=$('#candName');const nm=(inp.value||'').replace(/\s+/g,' ').trim();if(nm.length<2){$('#nameWarn').hidden=false;inp.focus();inp.scrollIntoView({block:'center'});return false}store.set('name',nm);return true};
  $$('[data-sec]').forEach(b=>b.onclick=()=>{if(!nameOk())return;FULL=null;startSection(+b.dataset.sec,$('#examMode').checked)});
  $$('[data-full]').forEach(b=>b.onclick=()=>{if(!nameOk())return;const f=fullsOf()[+b.dataset.full];FULL={def:f,pos:0,results:[],rid:newRid(),exam:$('#examMode').checked};startSection(f.sections[0],FULL.exam)});
}
// ---------- run ----------
function startSection(i,exam){
  const sec=BANK.sections[i]; const parts=[]; const ids=[];
  (sec.slots||[]).forEach(sl=>{const got=pick(BANK.id,sl,sl.count||1);got.forEach(g=>{ids.push(g.id);parts.push(Object.assign({slot:sl.id,slotTitle:sl.title},JSON.parse(JSON.stringify(g))))})});
  let n=0; parts.forEach(p=>(p.questions||[]).forEach(q=>{q.n=++n; if(q.options&&q.shuffle!==false&&['mcq','multi'].includes(q.type)){const idx=shuffle(q.options.map((_,k)=>k));q._map=idx;q._opts=idx.map(k=>q.options[k])}else q._opts=q.options}));
  RUN={name:store.get('name',''),rid:FULL?FULL.rid:newRid(),sec,secIdx:i,parts,ids,answers:{},exam,start:Date.now(),limit:(sec.minutes+(sec.review_minutes||0))*60,cur:0,done:false,audioPlayed:{}};
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
  app().innerHTML=`<div class="runbar"><b>${esc(BANK.title)} · ${esc(L(sec.title))}${FULL?` <span class="fullpos">(${FULL.pos+1}/${FULL.def.sections.length})</span>`:''}</b><span id="timer" class="timer">--:--</span><button class="btn" id="submit">${esc(t('submit'))}</button></div>
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
function newRid(){return 'TEG-'+BANK.id.toUpperCase()+'-'+new Date().toISOString().slice(2,10).replace(/-/g,'')+'-'+(Date.now().toString(36).slice(-3)+rnd(1296).toString(36)).toUpperCase()}
function fullsOf(){return BANK.fulls||[{id:'full',title:{id:'Full mock test '+BANK.title,en:'Full mock test '+BANK.title},sections:BANK.sections.map((_,i)=>i)}]}
function fullForSec(i){return fullsOf().find(f=>f.sections.includes(i))||fullsOf()[0]}
function repOf(f){return Object.assign({},BANK.report||{},f.report||{})}
function finish(timeout){if(!RUN||RUN.done)return;RUN.done=true;window.onbeforeunload=null;if(mediaRec&&mediaRec.state==='recording')mediaRec.stop();
  const sec=RUN.sec;let raw=0,max=0;const rows=[];
  RUN.parts.forEach(p=>(p.questions||[]).forEach(q=>{if(!sec.auto){rows.push({q,p});return}const s=scoreQ(q);raw+=s.got;max+=s.max;rows.push({q,p,s})}));
  markSeen(BANK.id,RUN.ids);
  const est=sec.auto?conv(sec,raw,max):'';
  const used=Math.min(RUN.limit,(Date.now()-RUN.start)/1000);
  const res={secIdx:RUN.secIdx,sec,raw,max,est,used,timeout,rows,parts:RUN.parts,answers:RUN.answers};
  if(sec.auto){const h=store.get('hist:'+BANK.id,[]);h.push({at:Date.now(),sec:L(sec.title),score:`${raw}/${max}${est!==''?' · '+(sec.score.label||'')+' '+est:''}`});store.set('hist:'+BANK.id,h.slice(-30))}
  if(FULL){FULL.results.push(res);FULL.pos++;if(FULL.pos<FULL.def.sections.length){interstitial(res);return}const f=FULL;FULL=null;showReport(f.results,f.def,true,f.rid);return}
  showReport([res],fullForSec(RUN.secIdx),false,RUN.rid);
}
function interstitial(res){const nx=BANK.sections[FULL.def.sections[FULL.pos]];
  app().innerHTML=header(L(FULL.def.title),'')+`<section class="card inter"><p class="okline">✓ ${esc(L(res.sec.title))} ${esc(t('section_done'))}${res.sec.auto?` · ${res.raw}/${res.max}`:''}</p>
  <p>${esc(t('next_section'))}: <b>${esc(L(nx.title))}</b> · ${nx.minutes} ${esc(t('minutes'))}</p><p class="small">${esc(t('full_break'))}</p>
  <p><button class="btn" id="goNext">${esc(t('start_next'))} →</button> <button class="btn ghost" id="stopFull">${esc(t('stop_full'))}</button></p></section>`+footer();
  bindLang();scrollTo(0,0);
  $('#goNext').onclick=()=>startSection(FULL.def.sections[FULL.pos],FULL.exam);
  $('#stopFull').onclick=()=>{const f=FULL;FULL=null;showReport(f.results,f.def,true,f.rid)};
}
function skillValues(results,rep){
  const lay=rep.layout||'generic';const sk=(rep.skills||[]).map(x=>Object.assign({},x,{v:null,raw:0,max:0,teacher:false,taken:false}));
  results.forEach(r=>{const ids=[].concat(r.sec.skill||r.sec.skills||[]);ids.forEach(id=>{const o=sk.find(x=>x.id===id);if(!o)return;o.taken=true;
    if(!r.sec.auto){o.teacher=true;return}
    if(lay==='pte'||lay==='ielts'){o.v=(typeof r.est==='number'?r.est:parseFloat(r.est))}else{o.raw+=r.raw;o.max+=r.max}})});
  if(!(lay==='pte'||lay==='ielts'))sk.forEach(o=>{if(o.max)o.v=Math.round(o.raw/o.max*(o.full||100))});
  return sk}
function overallOf(sk,rep){const lay=rep.layout||'generic';const nums=sk.filter(o=>typeof o.v==='number'&&!isNaN(o.v));const all=sk.length&&nums.length===sk.length;
  if(!nums.length)return {v:'-',note:''};
  if(lay==='ielts'){const m=nums.reduce((a,o)=>a+o.v,0)/nums.length;return {v:(Math.round(m*2)/2).toFixed(1),note:all?'':t('partial_overall')}}
  if(lay==='pte'){const m=nums.reduce((a,o)=>a+o.v,0)/nums.length;return {v:Math.round(m),note:all?'':t('partial_overall')}}
  const tot=nums.reduce((a,o)=>a+o.v,0);const mx=sk.reduce((a,o)=>a+(o.full||100),0);let res='';
  if(all&&rep.levels){for(const [min,lab] of rep.levels){if(tot>=min){res=lab;break}}if(!res)res=L(rep.fail_label)||t('not_pass')}
  else if(all&&rep.pass!=null){const okSec=sk.every(o=>o.min==null||o.v>=o.min);res=(tot>=rep.pass&&okSec)?(L(rep.pass_label)||t('pass')):(L(rep.fail_label)||t('not_pass'))}
  return {v:tot,max:mx,res,note:all?'':t('partial_overall')}}
function showReport(results,fdef,isFull,rid){
  const rep=repOf(fdef);const lay=rep.layout||'generic';const sk=skillValues(results,rep);const ov=overallOf(sk,rep);
  const title=isFull?L(fdef.title):(BANK.title+' · '+L(results[0].sec.title));
  const anyTimeout=results.some(r=>r.timeout);
  app().innerHTML=header(title,'')+`<section class="card result">${anyTimeout?`<p class="warn">${esc(t('time_up'))}</p>`:''}
  ${reportHTML(results,fdef,isFull,rid,rep,lay,sk,ov)}
  <div class="share"><b>${esc(t('send_result'))}</b> <a class="btn wa" id="shWA" target="_blank" rel="noopener">WhatsApp</a> <a class="btn ghost" id="shMail">Email</a> <button class="btn ghost" id="shPrint">PDF / ${esc(t('print'))}</button><small>${esc(t('send_note'))}</small></div>
  <p><a class="btn" href="?test=${BANK.id}&lang=${LANG}">${esc(t('other_sections'))}</a> <a class="btn ghost" href="https://linktr.ee/talentededucationgroup" target="_blank" rel="noopener">${esc(t('ask_consultant'))}</a></p></section>
  <section class="card review-wrap"><h2>${esc(t('review'))}</h2>${results.map(r=>`<details${r.sec.auto?'':' open'}><summary>${esc(L(r.sec.title))}${r.sec.auto?` · ${r.raw}/${r.max}`:''}</summary>${r.parts.map(p=>`<div class="rvp"><p class="rvh">${esc(L(p.title)||p.slotTitle)}</p>${p.transcript?`<details class="tr"><summary>${esc(t('transcript'))}</summary><div class="trx">${p.transcript}</div></details>`:''}${(p.questions||[]).map(q=>{const x=r.rows.find(y=>y.q===q);return reviewRow(q,x&&x.s,r.answers)}).join('')}</div>`).join('')}</details>`).join('')}</section>`+footer();
  bindLang();scrollTo(0,0);
  const txt=summaryText(results,title,rid,rep,sk,ov);
  $('#shWA').href='https://wa.me/?text='+encodeURIComponent(txt.slice(0,1800));
  $('#shMail').href='mailto:?subject='+encodeURIComponent(t('free_mock')+' - '+title)+'&body='+encodeURIComponent(txt);
  $('#shPrint').onclick=()=>window.print();
}
function partStats(results){const g=[];results.forEach(r=>r.rows.forEach(x=>{if(!x.s)return;const k=x.p.slotTitle||L(x.p.title);let o=g.find(y=>y.k===k);if(!o){o={k,got:0,max:0};g.push(o)}o.got+=x.s.got;o.max+=x.s.max}));return g}
function fbKey(p){return p>=0.8?'fb_strong':(p>=0.5?'fb_dev':'fb_focus')}
function cell(o,lay){if(o.teacher)return `<span class="tm">${esc(t('teacher_marked'))}</span>`;if(!o.taken||o.v==null||isNaN(o.v))return '<span class="na">—</span>';return lay==='ielts'?Number(o.v).toFixed(1):String(o.v)}
function reportHTML(results,fdef,isFull,rid,rep,lay,sk,ov){
  const d=new Date();const used=results.reduce((a,r)=>a+r.used,0);const ps=partStats(results);
  const dstr=d.toLocaleDateString(LANG,{day:'2-digit',month:'short',year:'numeric'});
  if(lay==='pte')return reportPTE(results,isFull,rid,rep,sk,ov,dstr,ps);
  if(lay==='ielts')return reportIELTS(results,isFull,rid,rep,sk,ov,dstr,ps);
  const skillsTitle=L(rep.skills_title)||t('skills_title');
  let block='';
  if(lay==='pte'){const sc=rep.scale||[10,90];
    block=`<h3>${esc(skillsTitle)}</h3><div class="rp-circles">${sk.map(o=>`<div class="c c-${esc(o.id)}"><span class="ring">${cell(o,lay)}</span><small>${esc(L(o.label))}</small></div>`).join('')}</div>
    <h3>${esc(t('skills_breakdown'))}</h3><table class="rp-bars"><tr><td>${esc(t('overall'))}</td><td class="num">${esc(String(ov.v))}</td><td><span class="bar big"><i style="width:${typeof ov.v==='number'?Math.round((ov.v-sc[0])/(sc[1]-sc[0])*100):0}%"></i></span></td></tr>${sk.map(o=>`<tr><td>${esc(L(o.label))}</td><td class="num">${cell(o,lay)}</td><td><span class="bar c-${esc(o.id)}"><i style="width:${typeof o.v==='number'&&!isNaN(o.v)?Math.round((o.v-sc[0])/(sc[1]-sc[0])*100):0}%"></i></span></td></tr>`).join('')}</table>`}
  else if(lay==='ielts'){block=`<h3>${esc(skillsTitle)}</h3><div class="rp-bands">${sk.map(o=>`<div><small>${esc(L(o.label))}</small><b>${cell(o,lay)}</b></div>`).join('')}<div class="ovb"><small>${esc(L(rep.overall_label)||t('overall'))}</small><b>${esc(String(ov.v))}</b></div></div>${rep.cefr&&ov.v!=='-'?`<p class="small">CEFR: ${esc(cefr(+ov.v,rep.cefr))}</p>`:''}`}
  else {block=`<h3>${esc(skillsTitle)}</h3><table class="rp-sect"><tr><th>${esc(t('section'))}</th><th>${esc(t('score'))}</th>${sk.some(o=>o.min!=null)?`<th>${esc(t('min_score'))}</th>`:''}</tr>${sk.map(o=>`<tr><td>${esc(L(o.label))}</td><td class="num">${cell(o,lay)} / ${o.full||100}</td>${sk.some(x=>x.min!=null)?`<td class="num">${o.min!=null?o.min:'—'}</td>`:''}</tr>`).join('')}<tr class="tot"><td>${esc(L(rep.total_label)||t('total'))}</td><td class="num">${esc(String(ov.v))} / ${ov.max||'-'}</td>${sk.some(o=>o.min!=null)?`<td class="num">${rep.pass!=null?rep.pass:''}</td>`:''}</tr></table>${ov.res?`<p class="rp-res">${esc(L(rep.result_label)||t('result'))}: <b>${esc(ov.res)}</b></p>`:''}`}
  const tb=ps.length?`<h3>${esc(t('breakdown'))}</h3><table class="rp-tb"><tr><th>${esc(t('section'))}</th><th>${esc(t('score'))}</th><th></th><th>${esc(t('feedback'))}</th></tr>${ps.map(o=>{const p=o.max?o.got/o.max:0;return `<tr><td>${esc(o.k)}</td><td class="num">${o.got}/${o.max}</td><td><span class="bar"><i style="width:${Math.round(p*100)}%"></i></span></td><td>${esc(t(fbKey(p)))}</td></tr>`}).join('')}</table>`:'';
  const ovLabel=L(rep.overall_label)||t('overall');
  return `<div class="report lay-${lay}" id="report"><div class="wm" aria-hidden="true"></div>
  <div class="rp-band"><img src="${BASE}logo.png" alt="Talented Education Group" onerror="this.remove()"><div class="rp-bt"><b>${esc(isFull?L(fdef.title).replace(/\s*-\s*Full mock test$/i,""):BANK.title)}</b><span>${esc(t('report_title'))}</span></div><div class="rp-code"><small>${esc(t('report_no'))}</small><span>${esc(rid)}</span></div></div>
  <div class="rp-top"><div class="rp-cand"><div class="rp-photo" aria-hidden="true">👤</div><div><div class="rp-name">${esc(RUN&&RUN.name||store.get('name','')||'-')}</div>
  <dl><div><dt>${esc(t('date'))}</dt><dd>${dstr}</dd></div><div><dt>${esc(t('test_mode'))}</dt><dd>${esc(isFull?t('full_test'):t('section_only')+' · '+L(results[0].sec.title))}</dd></div><div><dt>${esc(t('test_centre'))}</dt><dd>${esc(t('test_centre_v'))}</dd></div><div><dt>${esc(t('time_used'))}</dt><dd>${fmt(used)}</dd></div></dl></div></div>
  <div class="rp-ov"><small>${esc(ovLabel)}</small><b>${esc(String(ov.v))}</b>${ov.max?`<span>/ ${ov.max}</span>`:''}${ov.res?`<em>${esc(ov.res)}</em>`:''}</div></div>
  ${ov.note?`<p class="small rp-note">${esc(ov.note)}</p>`:''}
  ${block}${tb}
  <p class="small">${esc(L(rep.note)||t('estimate_note'))}</p>
  <div class="rp-foot"><img class="qr" src="${BASE}qr-pricelist.png" alt="QR"><div><p class="rp-org">${esc(t('organiser'))}</p><p class="small">${esc(t('try_free'))} <a href="${SHARE_URL}" target="_blank" rel="noopener">${esc(SHARE_URL.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></p></div><img class="vsa" src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"></div>
  <p class="rp-off">${esc(t('not_official'))}</p></div>`}
function reportPTE(results,isFull,rid,rep,sk,ov,dstr,ps){const sc=rep.scale||[10,90];const pc=v=>typeof v==='number'&&!isNaN(v)?Math.max(0,Math.min(100,Math.round((v-sc[0])/(sc[1]-sc[0])*100))):0;
  const nm=esc((RUN&&RUN.name)||store.get('name','')||'-');
  return `<div class="report lay-pte rp-pte" id="report"><div class="wm" aria-hidden="true"></div>
  <div class="pte-head"><img src="${BASE}logo.png" alt="" onerror="this.remove()"><span>Talented Education Group | PTE Academic <b>Mock Test</b> | ${esc(t('report_title'))}</span></div>
  <div class="pte-code">${esc(t('report_code'))}: <b>${esc(rid)}</b></div>
  <div class="pte-top"><div class="rp-photo" aria-hidden="true">👤</div><div class="pte-id"><div class="pte-name">${nm}</div><p><b>${esc(t('report_no'))}:</b> ${esc(rid)}</p><p><b>${esc(t('test_mode'))}:</b> ${esc(isFull?t('full_test'):t('section_only')+' · '+L(results[0].sec.title))}</p></div>
  <div class="pte-ov"><small>${esc(t('overall_score'))}</small><b>${esc(String(ov.v))}</b></div></div>
  ${ov.note?`<p class="small rp-note">${esc(ov.note)}</p>`:''}
  <h3 class="pte-h">${esc(t('skills_title'))}</h3>
  <div class="rp-circles">${sk.map(o=>`<div class="c c-${esc(o.id)}"><span class="ring">${cell(o,'pte')}</span><small>${esc(L(o.label))}</small></div>`).join('')}</div>
  <div class="pte-two"><div><h3 class="pte-h">${esc(t('skills_breakdown'))}</h3><div class="pte-bars" style="--ov:${pc(ov.v)}%"><div class="pte-ovl"><span>${esc(t('overall'))} <b>${esc(String(ov.v))}</b></span></div>${sk.map(o=>`<div class="pr"><span class="lb">${esc(L(o.label))}</span><span class="vv">${cell(o,'pte')}</span><span class="tr"><i class="c-${esc(o.id)}" style="width:${pc(o.v)}%"></i></span></div>`).join('')}<div class="pte-line"></div></div></div>
  <div><h3 class="pte-h">${esc(t('candidate_info'))}</h3><dl class="pte-dl"><div><dt>${esc(t('candidate'))}:</dt><dd>${nm}</dd></div><div><dt>${esc(t('language'))}:</dt><dd>${esc(UI._langnames?UI._langnames[LANG]:LANG)}</dd></div><div><dt>${esc(t('time_used'))}:</dt><dd>${fmt(results.reduce((a,r)=>a+r.used,0))}</dd></div></dl></div></div>
  <h3 class="pte-h">${esc(t('centre_info'))}</h3><div class="pte-two pte-ci"><dl class="pte-dl"><div><dt>${esc(t('test_centre'))}:</dt><dd>${esc(t('test_centre_v'))}</dd></div><div><dt>${esc(t('organiser_short'))}:</dt><dd>Talented Education Group · Victory Scholars Academy</dd></div></dl><dl class="pte-dl"><div><dt>${esc(t('date'))}:</dt><dd>${dstr}</dd></div><div><dt>${esc(t('valid_until'))}:</dt><dd>${esc(t('not_valid'))}</dd></div></dl></div>
  ${ps.length?breakdownTable(ps):''}
  ${footHTML(rep)}</div>`}
function reportIELTS(results,isFull,rid,rep,sk,ov,dstr,ps){const nm=esc((RUN&&RUN.name)||store.get('name','')||'-');const box=(lab,v,cls='')=>`<div class="if-f ${cls}"><span>${esc(lab)}</span><b>${v}</b></div>`;
  const band=id=>{const o=sk.find(x=>x.id===id);return o?cell(o,'ielts'):'—'};
  return `<div class="report lay-ielts rp-ielts" id="report"><div class="wm" aria-hidden="true"></div>
  <div class="if-top"><div><div class="if-brand">IELTS Academic · <span>Mock Test</span></div><div class="if-title">${esc(t('ielts_form'))}</div></div><div class="if-mod">ACADEMIC</div></div>
  <p class="if-note">${esc(t('ielts_note'))}</p>
  <div class="if-row">${box(t('centre'),'TEG Online')}${box(t('date'),dstr)}${box(t('report_no'),esc(rid))}</div>
  <h3 class="if-h">${esc(t('candidate_details'))}</h3>
  <div class="if-cand"><div class="if-fields">${box(t('candidate'),nm,'wide')}${box(t('test_mode'),esc(isFull?t('full_test'):t('section_only')+' · '+L(results[0].sec.title)),'wide')}${box(t('time_used'),fmt(results.reduce((a,r)=>a+r.used,0)))}</div><div class="rp-photo big" aria-hidden="true">👤</div></div>
  <h3 class="if-h">${esc(t('test_results'))}</h3>
  <div class="if-res"><span>Listening</span><b>${band('L')}</b><span>Reading</span><b>${band('R')}</b><span>Writing</span><b>${band('W')}</b><span>Speaking</span><b>${band('S')}</b><span class="ovl">${esc(t('overall_band'))}</span><b class="ovb">${esc(String(ov.v))}</b><span>CEFR</span><b>${rep.cefr&&ov.v!=='-'?esc(cefr(+ov.v,rep.cefr)):'—'}</b></div>
  ${ov.note?`<p class="small rp-note">${esc(ov.note)}</p>`:''}
  <div class="if-bottom"><div class="if-com"><b>${esc(t('consultant_comments'))}</b><div class="if-lines"></div></div><div class="if-ver">${esc(t('cannot_verify'))}</div><div class="if-stamp"><b>${esc(t('organiser_short'))}</b><img src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"><img src="${BASE}logo.png" alt="Talented Education Group" onerror="this.remove()"></div></div>
  ${ps.length?breakdownTable(ps):''}
  ${footHTML(rep)}</div>`}
function breakdownTable(ps){return `<h3>${esc(t('breakdown'))}</h3><table class="rp-tb"><tr><th>${esc(t('section'))}</th><th>${esc(t('score'))}</th><th></th><th>${esc(t('feedback'))}</th></tr>${ps.map(o=>{const p=o.max?o.got/o.max:0;return `<tr><td>${esc(o.k)}</td><td class="num">${o.got}/${o.max}</td><td><span class="bar"><i style="width:${Math.round(p*100)}%"></i></span></td><td>${esc(t(fbKey(p)))}</td></tr>`}).join('')}</table>`}
function footHTML(rep){return `<p class="small rp-n2">${esc(L(rep.note)||t('estimate_note'))}</p><div class="rp-foot"><img class="qr" src="${BASE}qr-pricelist.png" alt="QR"><div><p class="rp-org">${esc(t('organiser'))}</p><p class="small">${esc(t('try_free'))} <a href="${SHARE_URL}" target="_blank" rel="noopener">${esc(SHARE_URL.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></p></div><img class="vsa" src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"></div><p class="rp-off">${esc(t('not_official'))}</p>`}
function cefr(b,map){for(const [min,lab] of map){if(b>=min)return lab}return '-'}
function summaryText(results,title,rid,rep,sk,ov){
  const lay=rep.layout||'generic';
  const lines=[`${t('report_title')} - ${title}`,`${t('candidate')}: ${(RUN&&RUN.name)||store.get('name','')||'-'}`,`${t('report_no')}: ${rid}`,`${t('date')}: ${new Date().toLocaleString()}`,t('organiser'),''];
  sk.forEach(o=>lines.push(`${L(o.label)}: ${o.teacher?t('teacher_marked'):(o.v==null||isNaN(o.v)?'—':(lay==='ielts'?Number(o.v).toFixed(1):o.v)+(lay==='pte'||lay==='ielts'?'':' / '+(o.full||100)))}`));
  lines.push(`${L(rep.overall_label)||t('overall')}: ${ov.v}${ov.max?' / '+ov.max:''}${ov.res?' · '+ov.res:''}`);
  if(ov.note)lines.push(ov.note);
  results.forEach(r=>{if(r.sec.auto){lines.push('');lines.push(`${L(r.sec.title)}: ${r.raw}/${r.max}`);const wrong=r.rows.filter(x=>x.s&&x.s.got<x.s.max).map(x=>`${x.q.n}: ${showAns(x.q)}`.slice(0,60));if(wrong.length){lines.push(t('to_review')+':');lines.push(...wrong.slice(0,15));if(wrong.length>15)lines.push('…')}}
    else r.parts.forEach(p=>(p.questions||[]).forEach(q=>{const a=r.answers[q.n];if(q.type==='essay'){lines.push('');lines.push(`${q.n}. ${(q.prompt||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().slice(0,160)}`);lines.push(`(${yours(q,r.answers)})`);if(a)lines.push(a)}}))});
  lines.push('');lines.push(L(rep.note)||t('estimate_note'));lines.push(t('not_official'));lines.push('');lines.push(t('try_free'));lines.push(SHARE_URL);
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
function yours(q,ans){const a=(ans||RUN.answers)[q.n];if(a==null||a===''||(Array.isArray(a)&&!a.length))return '—';
  switch(q.type){case 'mcq':return String.fromCharCode(65+a);case 'multi':return a.map(k=>String.fromCharCode(65+k)).join(', ');case 'order':return a.map(k=>q.items[k]).join(' → ');case 'highlight':return a.map(k=>q.text.split(' ')[k]).join(', ');case 'cloze':return Object.values(a).join(' / ');case 'essay':return (a.trim().split(/\s+/).length)+' '+t('words');default:return a}}
function reviewRow(q,s,ans){const ok=s?(s.got===s.max?'ok':(s.got>0?'part':'no')):'na';
  return `<div class="rv ${ok}"><div class="qn">${q.n}</div><div>${q.prompt?`<div class="qp">${q.prompt.replace('___','____')}</div>`:''}
  ${q.type==='essay'||q.type==='speak'?`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q,ans))}</p>${q.checklist?`<p><b>${esc(t('checklist'))}:</b></p><ul>${q.checklist.map(c=>`<li>${c}</li>`).join('')}</ul>`:''}${q.model?`<details><summary>${esc(t('model_answer'))}</summary><div class="model">${q.model}</div></details>`:''}`
  :`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q,ans))} · <b>${esc(t('correct_answer'))}:</b> ${esc(showAns(q))}${s?` · ${s.got}/${s.max}`:''}</p>`}${q.explain?`<p class="small">${q.explain}</p>`:''}</div></div>`}
// ---------- boot ----------
(async function(){
  try{UI=await J(BASE+'banks/ui.json?t='+Math.floor(Date.now()/6e5));IDX=await J(BASE+'banks/index.json?t='+Math.floor(Date.now()/6e4));window.MOCK_V=IDX.version||'1';try{const lk=document.createElement('link');lk.rel='stylesheet';lk.href=BASE+'style.css?v='+encodeURIComponent(window.MOCK_V);document.head.appendChild(lk)}catch(_){}}catch(e){app().innerHTML='<p>Load error. Please refresh.</p>';return}
  document.documentElement.lang=LANG;
  const id=Q.get('test');
  if(!id){home();return}
  const meta=IDX.tests.find(x=>x.id===id);
  if(!meta||!meta.ready){home();return}
  try{BANK=await J(BASE+'banks/'+meta.file)}catch(e){app().innerHTML='<p>Load error.</p>';return}
  testPage();
})();
})();
