/* Talented Education Group - Free Mock Test engine (static, no data sent to any server) */
(function(){
'use strict';
const $=(s,e=document)=>e.querySelector(s), $$=(s,e=document)=>[...e.querySelectorAll(s)];
const Q=new URLSearchParams(location.search);
const BASE=(window.MOCK_BASE||'');
const SHARE_URL=(window.MOCK_SHARE_URL||'https://pricelist.talentededucationgroup.com/');
const LANGS=['id','en','th','vi','zh','ja','ko','km','fr','pt','es','de','it','nl','ru'];
let LANG=(Q.get('lang')||'').slice(0,2); if(!LANGS.includes(LANG)) LANG='id';
let UI={}, BANK=null, IDX=null, RUN=null, FULL=null, CAND='', LAST=null, REPCTX={name:'',date:Date.now(),teacher:null}, FLASH='', TF=null;
const MODE=Q.get('mode')==='guru'?'guru':'';
const t=k=>(UI[k]&&(UI[k][LANG]||UI[k].en))||k;
try{localStorage.removeItem('tegmock:name')}catch(e){}
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
  app().innerHTML=header(t('free_mock'),esc(t('home_sub')))+`<div class="acts top"><a class="btn back" href="${SHARE_URL}" id="backSite">← ${esc(t('back_site'))}</a> ${fileBtn('hFile','📥 '+t('open_file'))}</div><div class="grid">${IDX.tests.map(x=>`<a class="card test" href="?test=${x.id}&lang=${LANG}"><span class="flag">${x.icon||''}</span><b>${esc(x.title)}</b><small>${esc(L(x.desc))}</small><span class="status ${x.ready?'ok':'soon'}">${x.ready?esc(t('available')):esc(t('coming_soon'))}</span></a>`).join('')}</div>
  <section class="note">${esc(t('disclaimer'))}<br><a href="?mode=guru&lang=${LANG}">👩‍🏫 ${esc(t('teacher_mode'))}</a></section>`+footer();
  bindLang(); bindFile('hFile',openStudentFile);
  $('#backSite').onclick=e=>{try{if(document.referrer&&new URL(document.referrer).host.includes('talentededucationgroup')&&history.length>1){e.preventDefault();history.back()}}catch(_){}};
}
function footer(){return `<footer><p>${esc(t('footer_vsa'))}</p><p><a class="btn gold" href="https://linktr.ee/talentededucationgroup" target="_blank" rel="noopener">💬 ${esc(t('ask_consultant'))}</a></p><p class="small">© Talented Education Group · ${esc(t('privacy'))}</p></footer>`}
function testPage(){
  try{history.replaceState({mock:'test'},'')}catch(e){}
  document.title=BANK.title+' - '+t('free_mock');
  const secs=BANK.sections;
  const hist=store.get('hist:'+BANK.id,[]);
  const saves=getSaves().filter(e=>e&&e.state&&BANK.sections[e.secIdx]);
  const flash=FLASH;FLASH='';
  app().innerHTML=header(BANK.title,esc(L(BANK.desc)))+`<div class="acts top"><a class="btn back" href="?lang=${LANG}">← ${esc(t('all_tests'))}</a> ${fileBtn('tFileS','📥 '+t('open_file'))}</div>
  ${flash?`<p class="flash" role="status">✓ ${esc(flash)}</p>`:''}
  ${saves.length?`<section class="card savecard" id="saveCard"><h2>💾 ${esc(t('saved_title'))}</h2><div class="secs">${saves.map(e=>{const f=e.fk!=null?fullsOf()[e.fk]:null;return `<div class="sec"><div><b>${esc(f?L(f.title):L(BANK.sections[e.secIdx].title))}</b><small>${esc(fmtDate(e.at,1))} · ${esc(L(BANK.sections[e.secIdx].title))}${f?` (${(e.pos||0)+1}/${f.sections.length})`:''} · ${esc(t('time_left'))} ${fmt(e.left)}</small></div><span class="sbtns"><button class="btn" data-res="${esc(e.id)}">${esc(t('resume'))}</button> <button class="btn ghost small" data-del="${esc(e.id)}" aria-label="${esc(t('del_save'))}">🗑 ${esc(t('del_save'))}</button></span></div>`}).join('')}</div>
  <p class="small">${esc(t('save_note'))}</p><button class="btn ghost" id="startNew">${esc(t('start_new'))}</button></section>`:''}
  <section class="card fullcard"><h2>${esc(t('full_test'))}</h2><p class="small">${esc(t('full_desc'))}</p><div class="secs">${fullsOf().map((f,k)=>`<div class="sec"><div><b>${esc(L(f.title))}</b><small>${f.sections.reduce((a,i)=>a+secs[i].minutes+(secs[i].review_minutes||0),0)} ${esc(t('minutes'))} · ${f.sections.length} ${esc(t('sections_n'))}: ${esc(f.sections.map(i=>L(secs[i].title)).join(' → '))}</small></div><button class="btn gold" data-full="${k}">${esc(t('start_full'))}</button></div>`).join('')}</div></section>
  <section class="card"><h2>${esc(t('choose_section'))}</h2>
  ${BANK.levels?`<label class="lvl">${esc(t('level'))}: <select id="lvl">${BANK.levels.map(l=>`<option>${esc(l)}</option>`).join('')}</select></label>`:''}
  <label class="namef"><b>${esc(t('your_name'))}</b><input id="candName" maxlength="60" autocomplete="name" placeholder="${esc(t('name_ph'))}" value="${esc(CAND)}"><small>${esc(t('name_note'))}</small><span class="warn" id="nameWarn" hidden>${esc(t('name_required'))}</span></label>
  <div class="secs">${secs.map((s,i)=>`<div class="sec"><div><b>${esc(L(s.title))}</b><small>${s.minutes} ${esc(t('minutes'))}${s.review_minutes?` + ${s.review_minutes} ${esc(t('review_min'))}`:''} · ${s.auto?esc(t('auto_marked')):esc(t('practice_only'))}</small><small>${esc(L(s.desc))}</small></div><button class="btn" data-sec="${i}">${esc(t('start'))}</button></div>`).join('')}</div>
  <p class="small">${esc(t('rules'))}</p>
  <label class="chk"><input type="checkbox" id="examMode" checked> ${esc(t('exam_mode'))}</label></section>
  ${hist.length?`<section class="card"><h2>${esc(t('history'))}</h2><ul class="hist">${hist.slice(-8).reverse().map(h=>`<li>${new Date(h.at).toLocaleString()} · ${esc(h.sec)} · <b>${esc(h.score)}</b></li>`).join('')}</ul><p class="small">${esc(t('history_note'))}</p></section>`:''}
`+footer();
  bindLang();
  const nameOk=()=>{const inp=$('#candName');const nm=(inp.value||'').replace(/\s+/g,' ').trim();if(nm.length<2){$('#nameWarn').hidden=false;inp.focus();inp.scrollIntoView({block:'center'});return false}CAND=nm;return true};
  $$('[data-sec]').forEach(b=>b.onclick=()=>{if(!nameOk())return;FULL=null;startSection(+b.dataset.sec,$('#examMode').checked)});
  $$('[data-full]').forEach(b=>b.onclick=()=>{if(!nameOk())return;const f=fullsOf()[+b.dataset.full];FULL={def:f,pos:0,results:[],rid:newRid(),exam:$('#examMode').checked};startSection(f.sections[0],FULL.exam)});
  $$('[data-res]').forEach(b=>b.onclick=()=>{const e=getSaves().find(x=>x.id===b.dataset.res);if(!e){testPage();return}if(!nameOk())return;
    try{restoreState(e.state,e.id)}catch(err){RUN=null;FULL=null;msgBox(fileErr(err),true)}});
  $$('[data-del]').forEach(b=>b.onclick=()=>{if(!confirm(t('del_confirm')))return;dropSave(b.dataset.del);testPage()});
  const sn=$('#startNew');if(sn)sn.onclick=()=>{$('#saveCard').hidden=true;const inp=$('#candName');inp.scrollIntoView({block:'center'});inp.focus()};
  bindFile('tFileS',openStudentFile);
}
// ---------- run ----------
function startSection(i,exam){
  try{history.pushState({mock:'run'},'')}catch(e){}
  const sec=BANK.sections[i]; const parts=[]; const ids=[];
  (sec.slots||[]).forEach(sl=>{const got=pick(BANK.id,sl,sl.count||1);got.forEach(g=>{ids.push(g.id);parts.push(Object.assign({slot:sl.id,slotTitle:sl.title},JSON.parse(JSON.stringify(g))))})});
  let n=0; parts.forEach(p=>(p.questions||[]).forEach(q=>{q.n=++n;q.kind=q.kind||p.slot;q._tr=p.transcript||'';q._pass=p.passage||''; if(q.options&&q.shuffle!==false&&['mcq','multi'].includes(q.type)){const idx=shuffle(q.options.map((_,k)=>k));q._map=idx;q._opts=idx.map(k=>q.options[k])}else q._opts=q.options}));
  RUN={name:CAND,rid:FULL?FULL.rid:newRid(),sec,secIdx:i,parts,ids,answers:{},exam,start:Date.now(),limit:(sec.minutes+(sec.review_minutes||0))*60,cur:0,done:false,audioPlayed:{},speech:{},saveId:FULL?FULL.saveId:null};
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
  app().innerHTML=`<div class="runbar"><b>${esc(BANK.title)} · ${esc(L(sec.title))}${FULL?` <span class="fullpos">(${FULL.pos+1}/${FULL.def.sections.length})</span>`:''}</b><span id="timer" class="timer">--:--</span><span class="rbtns"><button class="btn ghost small" id="saveTop" title="${esc(t('save_later'))}" aria-label="${esc(t('save_later'))}">💾</button> <button class="btn" id="submit">${esc(t('submit'))}</button></span></div>
  <nav class="tabs">${tabs}</nav>
  <div class="run ${p.passage?'split':''}">${passage}<div class="qs">${p.instructions?`<p class="ins">${p.instructions}</p>`:''}${BANK.ai&&(p.questions||[]).some(q=>q.type==='speak')?`<p class="small ainote">🤖 ${esc(t('speech_note'))}${(window.SpeechRecognition||window.webkitSpeechRecognition)?'':' <b>'+esc(t('speech_unsupported'))+'</b>'}</p>`:''}${audio}${groups.map(g=>`${g.g?`<p class="ins">${g.g}</p>`:''}${g.qs.map(q=>qHTML(q,p)).join('')}`).join('')}
  <div class="navbtns">${RUN.cur>0?`<button class="btn ghost" data-go="-1">← ${esc(t('prev'))}</button>`:''}${RUN.cur<RUN.parts.length-1?`<button class="btn" data-go="1">${esc(t('next'))} →</button>`:`<button class="btn" id="submit2">${esc(t('submit'))}</button>`}</div>
  <div class="toolrow"><button class="btn ghost" id="saveLater">💾 ${esc(t('save_later'))}</button> <button class="btn ghost" id="sendT">📤 ${esc(t('send_teacher'))}</button><small>${esc(t('save_note'))}</small></div></div></div>
  <div id="confirm" class="modal" hidden><div class="box"><p>${esc(t('confirm_submit'))}</p><p id="unans" class="small"></p><button class="btn" id="yes">${esc(t('submit'))}</button> <button class="btn ghost" id="no">${esc(t('back'))}</button></div></div>`;
  bindRun(); tickOnce();
}
function tickOnce(){const left=RUN.limit-(Date.now()-RUN.start)/1000;const el=$('#timer');if(el)el.textContent=fmt(left)}
function save(e){if(!RUN||RUN.done)return;const el=e.target;const m=(el.name||'').match(/^q(\d+)$/);
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
  $('#saveTop').onclick=saveLater; $('#saveLater').onclick=saveLater; $('#sendT').onclick=sendProgress;
}
function countQ(){return RUN.parts.reduce((s,p)=>s+(p.questions||[]).length,0)}
let mediaRec=null;
let recog=null,recTimer=null;
async function record(b){const box=b.parentNode;const st=$('.recst',box);const n=+box.dataset.n;const q=RUN.parts.flatMap(p=>p.questions||[]).find(x=>x.n===n);
  if(mediaRec&&mediaRec.state==='recording'){mediaRec.stop();return}
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true});const ch=[];mediaRec=new MediaRecorder(s);mediaRec.ondataavailable=e=>ch.push(e.data);
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;const sp=RUN.speech[n]={t0:Date.now(),secs:0,conf:0,pauses:0,unsupported:!SR&&!!BANK.ai};let finals=[],confs=[],lastEnd=Date.now();
    if(SR&&BANK.ai){try{recog=new SR();recog.lang='en-AU';recog.continuous=true;recog.interimResults=false;recog.maxAlternatives=1;
      recog.onresult=e=>{for(let k=e.resultIndex;k<e.results.length;k++){const r=e.results[k];if(r.isFinal){finals.push(r[0].transcript);if(r[0].confidence)confs.push(r[0].confidence);const now=Date.now();if(now-lastEnd>3000&&finals.length>1)sp.pauses++;lastEnd=now;sp.lastAt=now}}
        RUN.answers[n]=finals.join(' ').trim();sp.conf=confs.length?confs.reduce((x,y)=>x+y,0)/confs.length:0};
      recog.onerror=ev=>{if(ev.error==='not-allowed'||ev.error==='service-not-allowed'||ev.error==='audio-capture')sp.unsupported=true};
      recog.onend=()=>{if(mediaRec&&mediaRec.state==='recording'){try{recog.start()}catch(_){}}};
      recog.start()}catch(_){sp.unsupported=true}}
    mediaRec.onstop=()=>{clearTimeout(recTimer);sp.secs=(Date.now()-sp.t0)/1000;s.getTracks().forEach(x=>x.stop());const rr=recog;recog=null;if(rr){try{rr.stop()}catch(_){}}
      const url=URL.createObjectURL(new Blob(ch));
      setTimeout(()=>{const heard=RUN.answers[n];st.innerHTML=`<audio controls src="${url}"></audio> <small>${esc(t('rec_local'))}</small>${BANK.ai?`<br><small>${sp.unsupported?esc(t('speech_unsupported')):`${esc(t('ai_heard'))}: <i>${esc(heard||'—')}</i>`}</small>`:''}`},700);
      b.textContent=t('record_again')};
    mediaRec.start();b.textContent='■ '+t('stop');st.textContent=t('recording');
    if(q&&q.speak){clearTimeout(recTimer);recTimer=setTimeout(()=>{if(mediaRec&&mediaRec.state==='recording')mediaRec.stop()},q.speak*1000)}
  }catch(e){st.textContent=t('mic_denied')}}
// ---------- scoring ----------
function scoreQ(q,ans,speech){const a=(ans||RUN.answers)[q.n];
  switch(q.type){
    case 'mcq': return {got:(a!=null&&(q._map?q._map[a]:a)===q.answer)?1:0,max:1};
    case 'multi': {const sel=(a||[]).map(k=>q._map?q._map[k]:k);const right=sel.filter(k=>q.answer.includes(k)).length;const wrong=sel.length-right;return {got:q.negative?Math.max(0,right-wrong):(sel.length>q.choose?Math.max(0,right-(sel.length-q.choose)):right),max:q.answer.length}}
    case 'tfng': case 'match': return {got:a&&norm(a)===norm(q.answer)?1:0,max:1};
    case 'gap': {const acc=[].concat(q.answer).map(norm);return {got:acc.includes(norm(a))?1:0,max:1}}
    case 'order': {const ans=q.answer||q.items.map((_,k)=>k);let g=0;for(let i=0;i<ans.length-1;i++){const aa=a||[];const x=aa.indexOf(ans[i]);if(x>=0&&aa[x+1]===ans[i+1])g++}return {got:g,max:ans.length-1}}
    case 'dictation': {const want=norm(q.answer).split(' ');const have=norm(a).split(' ');const pool=have.slice();let g=0;want.forEach(w=>{const i=pool.indexOf(w);if(i>=0){g++;pool.splice(i,1)}});return {got:g,max:want.length}}
    case 'highlight': {const sel=a||[];const r=sel.filter(k=>q.answer.includes(k)).length;return {got:Math.max(0,r-(sel.length-r)),max:q.answer.length}}
    case 'speak': case 'essay': if(BANK.ai) return aiScore(q,a,speech||(RUN&&RUN.speech)||{}); break;
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
// ---------- automatic estimate for PTE speaking & writing (in-browser, simplified - not Pearson's algorithm) ----------
const STOP=new Set('the a an and or but of to in on at for with by from is are was were be been being it its this that these those as than then so very can will would should could may might must have has had do does did not no yes you your we our they their he she his her i me my there here what which who whom when where why how about into over after before also more most less many much some such each other only just one two three'.split(' '));
const strip=h=>String(h||'').replace(/<[^>]+>/g,' ').replace(/&[a-z]+;/g,' ');
const toks=x=>norm(strip(x)).split(' ').filter(Boolean);
function keyw(x,lim){const c={};toks(x).forEach(w=>{if((w.length>3&&!STOP.has(w))||/^\d/.test(w))c[w]=(c[w]||0)+1});return Object.keys(c).sort((a,b)=>c[b]-c[a]).slice(0,lim||20)}
function lcs(a,b){const m=a.length,n=b.length;if(!m||!n)return 0;let prev=new Array(n+1).fill(0);for(let i=1;i<=m;i++){const cur=new Array(n+1).fill(0);for(let j=1;j<=n;j++)cur[j]=a[i-1]===b[j-1]?prev[j-1]+1:Math.max(prev[j],cur[j-1]);prev=cur}return prev[n]}
function cover(words,keys){if(!keys.length)return 0;const set=new Set(words);return keys.filter(k=>set.has(k)).length/keys.length}
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));const r1=x=>Math.round(x*10)/10;
function aiScore(q,a,speech){const txt=String(a||'').trim();const w=toks(txt);
  if(q.type==='speak'){const sp=(speech||{})[q.n]||{};const max=q.kind==='asq'?1:5;
    if(!w.length)return sp.unsupported?{got:0,max:0,ai:1,fb:t('speech_unsupported')}:{got:0,max,ai:1,fb:t('ai_nothing')};
    if(q.kind==='asq'){const ok=[].concat(q.model||[]).some(m=>norm(txt).includes(norm(m)));return {got:ok?1:0,max,ai:1,fb:ok?t('ai_ok'):t('ai_asq_no')}}
    let content;const ref=q.kind==='ra'?toks(q.prompt):q.kind==='rs'?toks(q.model):null;
    if(ref){content=2*lcs(ref,w)/ref.length}else{const keys=keyw(q.kind==='rl'?q._tr:q.prompt,20);content=2*clamp(cover(w,keys)/0.45,0,1)*clamp(w.length/35,0,1)}
    const secs=Math.max(1,sp.secs||q.speak||30);const ss=clamp(sp.lastAt?(sp.lastAt-sp.t0)/1000:secs,1,secs);const pen=clamp(1-(sp.pauses||0)*0.15,0.3,1);
    const amt=ref?clamp(1.25*lcs(ref,w)/ref.length,0,1):clamp(w.length/30,0,1);
    const flu=1.5*pen*amt*(ref?clamp((ref.length/2.3)/ss,0,1):(()=>{const wps=w.length/ss;return wps<=3.6?clamp(wps/1.6,0,1):clamp(1-(wps-3.6)/2,0,1)})());
    const conf=sp.conf>0?sp.conf:0.75;const pron=1.5*clamp(ref?(0.5*conf+0.5*lcs(ref,w)/w.length):conf,0,1)*(0.4+0.6*amt);
    const got=r1(clamp(content,0,2)+flu+pron);return {got,max,ai:1,fb:`${t('ai_content')} ${r1(clamp(content,0,2))}/2 · ${t('ai_fluency')} ${r1(flu)}/1.5 · ${t('ai_pron')} ${r1(pron)}/1.5`}}
  // writing
  const sents=txt.split(/[.!?]+(\s|$)/).filter(x=>x&&x.trim().length>1).length;const n=w.length;
  const src=q.kind==='swt'?q._pass:q.kind==='sst'?q._tr:q.prompt;const keys=keyw(src,q.kind==='es'?10:15);
  const cov=cover(w,keys);const ttr=n?new Set(w).size/n:0;
  const capOk=/^[A-Z]/.test(txt)?1:0,endOk=/[.!?]$/.test(txt)?1:0;
  let form,maxF,lo,hi;if(q.kind==='swt'){lo=5;hi=75;maxF=1;form=(n>=lo&&n<=hi&&sents<=1)?1:0}else if(q.kind==='sst'){lo=50;hi=70;maxF=2;form=n>=lo&&n<=hi?2:(n>=40&&n<=100?1:0)}else{lo=200;hi=300;maxF=2;form=n>=lo&&n<=hi?2:(n>=120&&n<=380?1:0)}
  if(!n)return {got:0,max:q.kind==='swt'?7:q.kind==='sst'?8:13,ai:1,fb:t('ai_nothing')};
  if(form===0&&q.kind!=='es'){/* PTE: wrong form = 0 for content-dependent traits */}
  const content=2*clamp(cov/(q.kind==='es'?0.35:0.25),0,1)*(form?1:0.3);
  const gram=2*(0.5*capOk+0.5*endOk)*clamp(n/lo,0,1)*clamp(q.kind==='swt'?1:sents/(q.kind==='sst'?2:8),0.3,1);
  const vocab=2*clamp((ttr-0.35)/0.3,0,1)*clamp(n/lo,0,1);
  let got=form+content+gram+vocab,max=maxF+6;
  if(q.kind==='es'){const paras=txt.split(/\n\s*\n|\n/).filter(x=>x.trim().length>20).length;const link=(norm(txt).match(/\b(however|moreover|furthermore|therefore|in addition|for example|for instance|on the other hand|in conclusion|although|whereas|firstly|secondly|finally)\b/g)||[]).length;
    const dev=2*clamp(paras/4,0,1)*0.6+2*clamp(link/5,0,1)*0.4;const range=2*clamp((n?w.filter(x=>x.length>=7).length/n:0)/0.18,0,1);got+=dev+range;max+=4;
    if(form===0){got=r1(got*0.5)}}
  else if(form===0){got=r1(gram*0.5)}
  return {got:r1(got),max,ai:1,fb:`${t('ai_form')} ${r1(form)}/${maxF} · ${t('ai_content')} ${r1(content)}/2 · ${t('ai_grammar')} ${r1(gram)}/2 · ${t('ai_vocab')} ${r1(vocab)}/2 · ${n} ${t('words')} (${lo}-${hi})`}}
function skillEstOf(sec,rows){let skillEst=null;if(sec.auto&&sec.skill_by_type){skillEst={};const agg={};rows.forEach(x=>{if(!x.s||!x.s.max)return;const k=sec.skill_by_type[x.q.type];if(!k)return;agg[k]=agg[k]||[0,0];agg[k][0]+=x.s.got;agg[k][1]+=x.s.max});Object.entries(agg).forEach(([k,v])=>skillEst[k]=conv(sec,v[0],v[1]))}return skillEst}
function repOf(f){return Object.assign({},BANK.report||{},f.report||{})}
function finish(timeout){if(!RUN||RUN.done)return;RUN.done=true;window.onbeforeunload=null;if(mediaRec&&mediaRec.state==='recording')mediaRec.stop();
  const sec=RUN.sec;let raw=0,max=0;const rows=[];
  RUN.parts.forEach(p=>(p.questions||[]).forEach(q=>{if(!sec.auto){rows.push({q,p});return}const s=scoreQ(q);raw+=s.got;max+=s.max;rows.push({q,p,s})}));
  markSeen(BANK.id,RUN.ids);
  const est=sec.auto?conv(sec,raw,max):'';
  const skillEst=skillEstOf(sec,rows);
  const used=Math.min(RUN.limit,(Date.now()-RUN.start)/1000);
  raw=r1(raw);const res={secIdx:RUN.secIdx,sec,raw,max,est,skillEst,used,timeout,rows,parts:RUN.parts,answers:RUN.answers,speech:RUN.speech||{}};
  if(sec.auto){const h=store.get('hist:'+BANK.id,[]);h.push({at:Date.now(),sec:L(sec.title),score:`${raw}/${max}${est!==''?' · '+(sec.score.label||'')+' '+est:''}`});store.set('hist:'+BANK.id,h.slice(-30))}
  if(FULL){FULL.results.push(res);FULL.pos++;if(FULL.pos<FULL.def.sections.length){interstitial(res);return}const f=FULL;FULL=null;dropSave(f.saveId);showReport(f.results,f.def,true,f.rid);return}
  dropSave(RUN.saveId);
  showReport([res],fullForSec(RUN.secIdx),false,RUN.rid);
}
function interstitial(res){const nx=BANK.sections[FULL.def.sections[FULL.pos]];
  app().innerHTML=header(L(FULL.def.title),'')+`<section class="card inter"><p class="okline">✓ ${esc(L(res.sec.title))} ${esc(t('section_done'))}${res.sec.auto?` · ${res.raw}/${res.max}`:''}</p>
  <p>${esc(t('next_section'))}: <b>${esc(L(nx.title))}</b> · ${nx.minutes} ${esc(t('minutes'))}</p><p class="small">${esc(t('full_break'))}</p>
  <p><button class="btn" id="goNext">${esc(t('start_next'))} →</button> <button class="btn ghost" id="stopFull">${esc(t('stop_full'))}</button></p>
  <div class="toolrow"><button class="btn ghost" id="saveLater">💾 ${esc(t('save_later'))}</button> <button class="btn ghost" id="sendT">📤 ${esc(t('send_teacher'))}</button><small>${esc(t('save_note'))}</small></div></section>`+footer();
  bindLang();scrollTo(0,0);
  $('#goNext').onclick=()=>startSection(FULL.def.sections[FULL.pos],FULL.exam);
  $('#stopFull').onclick=()=>{const f=FULL;FULL=null;dropSave(f.saveId);showReport(f.results,f.def,true,f.rid)};
  $('#saveLater').onclick=saveLater; $('#sendT').onclick=sendProgress;
}
function skillValues(results,rep){
  const lay=rep.layout||'generic';const sk=(rep.skills||[]).map(x=>Object.assign({},x,{v:null,raw:0,max:0,teacher:false,taken:false}));
  const tc=REPCTX&&REPCTX.teacher;
  results.forEach((r,ri)=>{const ids=[].concat(r.sec.skill||r.sec.skills||[]);ids.forEach(id=>{const o=sk.find(x=>x.id===id);if(!o)return;o.taken=true;
    const m=tc&&tc.secs&&tc.secs[ri]&&tc.secs[ri].skills&&tc.secs[ri].skills[id];if(m&&typeof m.v==='number'&&!isNaN(m.v)){o.v=m.v;o.tm=true;o.teacher=false;return}
    if(o.tm)return;
    if(!r.sec.auto){o.teacher=true;return}
    if(r.skillEst){if(r.skillEst[id]!=null)o.v=+r.skillEst[id];return}
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
function buildReport(results,fdef,isFull,rid){
  const rep=repOf(fdef);const lay=rep.layout||'generic';const sk=skillValues(results,rep);const ov=overallOf(sk,rep);
  const title=isFull?L(fdef.title):(BANK.title+' · '+L(results[0].sec.title));
  let html=reportHTML(results,fdef,isFull,rid,rep,lay,sk,ov);
  if(REPCTX.teacher){html=html.replace('<div class="wm" aria-hidden="true"></div>',m=>m+tmBadge(REPCTX.teacher)).replace('<div class="rp-foot">',m=>tmBlock(results,REPCTX.teacher,rep)+m)}
  return {html,title,rep,sk,ov}}
function showReport(results,fdef,isFull,rid,ctx){
  REPCTX=ctx||{name:(RUN&&RUN.name)||CAND||'',date:Date.now(),teacher:null};
  LAST={results,fdef,isFull,rid,ctx:REPCTX};
  const B=buildReport(results,fdef,isFull,rid);const {title,rep,sk,ov}=B;
  const anyTimeout=results.some(r=>r.timeout);
  app().innerHTML=header(title,'')+`<section class="card result">${anyTimeout?`<p class="warn">${esc(t('time_up'))}</p>`:''}
  ${B.html}
  <div class="share"><b>${esc(t('send_result'))}</b> <a class="btn wa" id="shWA" target="_blank" rel="noopener">WhatsApp</a> <a class="btn mail" id="shMail">Email</a> <button class="btn pdf" id="shPrint">PDF / ${esc(t('print'))}</button> <button class="btn" id="shTeach">📤 ${esc(t('send_teacher'))}</button><small>${esc(t('send_note'))} ${esc(t('send_teacher_note'))}</small></div>
  <div class="acts"><a class="btn back" href="?test=${BANK.id}&lang=${LANG}">← ${esc(t('back_tests'))}</a> <button class="btn" id="retry">↻ ${esc(t('try_again'))}</button></div></section>
  <section class="card review-wrap"><h2>${esc(t('review'))}</h2>${results.map(r=>`<details${r.sec.auto?'':' open'}><summary>${esc(L(r.sec.title))}${r.sec.auto?` · ${r.raw}/${r.max}`:''}</summary>${r.parts.map(p=>`<div class="rvp"><p class="rvh">${esc(L(p.title)||p.slotTitle)}</p>${p.transcript?`<details class="tr"><summary>${esc(t('transcript'))}</summary><div class="trx">${p.transcript}</div></details>`:''}${(p.questions||[]).map(q=>{const x=r.rows.find(y=>y.q===q);return reviewRow(q,x&&x.s,r.answers)}).join('')}</div>`).join('')}</details>`).join('')}</section>`+footer();
  bindLang();scrollTo(0,0);
  const txt=summaryText(results,title,rid,rep,sk,ov);
  $('#shWA').href='https://wa.me/?text='+encodeURIComponent(txt.slice(0,1800));
  $('#shMail').href='mailto:?subject='+encodeURIComponent(t('free_mock')+' - '+title)+'&body='+encodeURIComponent(txt);
  $('#shPrint').onclick=()=>window.print();
  $('#shTeach').onclick=sendResult;
  $('#retry').onclick=()=>{if(isFull){FULL={def:fdef,pos:0,results:[],rid:newRid(),exam:true};startSection(fdef.sections[0],true)}else startSection(results[0].secIdx,true)};
}
function partStats(results){const g=[];results.forEach(r=>r.rows.forEach(x=>{if(!x.s)return;const k=x.p.slotTitle||L(x.p.title);let o=g.find(y=>y.k===k);if(!o){o={k,got:0,max:0};g.push(o)}o.got+=x.s.got;o.max+=x.s.max}));return g.filter(o=>o.max>0)}
function fbKey(p){return p>=0.8?'fb_strong':(p>=0.5?'fb_dev':'fb_focus')}
function cell(o,lay){if(o.teacher)return `<span class="tm">${esc(t('teacher_marked'))}</span>`;if(!o.taken||o.v==null||isNaN(o.v))return '<span class="na">—</span>';return (lay==='ielts'?Number(o.v).toFixed(1):String(o.v))+(o.tm?'<sup class="tmk" title="Teacher marked">✎</sup>':'')}
function reportHTML(results,fdef,isFull,rid,rep,lay,sk,ov){
  const d=new Date(REPCTX.date||Date.now());const used=results.reduce((a,r)=>a+r.used,0);const ps=partStats(results);
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
  <div class="rp-top"><div class="rp-cand"><div class="rp-photo" aria-hidden="true">👤</div><div><div class="rp-name">${esc(REPCTX.name||'-')}</div>
  <dl><div><dt>${esc(t('date'))}</dt><dd>${dstr}</dd></div><div><dt>${esc(t('test_mode'))}</dt><dd>${esc(isFull?t('full_test'):t('section_only')+' · '+L(results[0].sec.title))}</dd></div><div><dt>${esc(t('test_centre'))}</dt><dd>${esc(t('test_centre_v'))}</dd></div><div><dt>${esc(t('time_used'))}</dt><dd>${fmt(used)}</dd></div></dl></div></div>
  <div class="rp-ov"><small>${esc(ovLabel)}</small><b>${esc(String(ov.v))}</b>${ov.max?`<span>/ ${ov.max}</span>`:''}${ov.res?`<em>${esc(ov.res)}</em>`:''}</div></div>
  ${ov.note?`<p class="small rp-note">${esc(ov.note)}</p>`:''}
  ${block}${tb}
  <p class="small">${esc(L(rep.note)||t('estimate_note'))}</p>
  <div class="rp-foot"><img class="qr" src="${BASE}qr-pricelist.png" alt="QR"><div><p class="rp-org">${esc(t('organiser'))}</p><p class="small">${esc(t('try_free'))} <a href="${SHARE_URL}" target="_blank" rel="noopener">${esc(SHARE_URL.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></p></div><img class="vsa" src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"></div>
  <p class="rp-off">${esc(t('not_official'))}</p></div>`}
function reportPTE(results,isFull,rid,rep,sk,ov,dstr,ps){const sc=rep.scale||[10,90];const pc=v=>typeof v==='number'&&!isNaN(v)?Math.max(0,Math.min(100,Math.round((v-sc[0])/(sc[1]-sc[0])*100))):0;
  const nm=esc(REPCTX.name||'-');
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
function reportIELTS(results,isFull,rid,rep,sk,ov,dstr,ps){const nm=esc(REPCTX.name||'-');const box=(lab,v,cls='')=>`<div class="if-f ${cls}"><span>${esc(lab)}</span><b>${v}</b></div>`;
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
  <div class="if-bottom"><div class="if-com"><b>${esc(t('consultant_comments'))}</b>${REPCTX.teacher&&REPCTX.teacher.overall?`<div class="if-ctext">${esc(REPCTX.teacher.overall)}</div>`:'<div class="if-lines"></div>'}</div><div class="if-ver">${esc(t('cannot_verify'))}</div><div class="if-stamp"><b>${esc(t('organiser_short'))}</b><img src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"><img src="${BASE}logo.png" alt="Talented Education Group" onerror="this.remove()"></div></div>
  ${ps.length?breakdownTable(ps):''}
  ${footHTML(rep)}</div>`}
function breakdownTable(ps){return `<h3>${esc(t('breakdown'))}</h3><table class="rp-tb"><tr><th>${esc(t('section'))}</th><th>${esc(t('score'))}</th><th></th><th>${esc(t('feedback'))}</th></tr>${ps.map(o=>{const p=o.max?o.got/o.max:0;return `<tr><td>${esc(o.k)}</td><td class="num">${o.got}/${o.max}</td><td><span class="bar"><i style="width:${Math.round(p*100)}%"></i></span></td><td>${esc(t(fbKey(p)))}</td></tr>`}).join('')}</table>`}
function footHTML(rep){return `<p class="small rp-n2">${esc(L(rep.note)||t('estimate_note'))}</p><div class="rp-foot"><img class="qr" src="${BASE}qr-pricelist.png" alt="QR"><div><p class="rp-org">${esc(t('organiser'))}</p><p class="small">${esc(t('try_free'))} <a href="${SHARE_URL}" target="_blank" rel="noopener">${esc(SHARE_URL.replace(/^https?:\/\//,'').replace(/\/$/,''))}</a></p></div><img class="vsa" src="${BASE}vsa-logo.png" alt="Victory Scholars Academy" onerror="this.remove()"></div><p class="rp-off">${esc(t('not_official'))}</p>`}
function cefr(b,map){for(const [min,lab] of map){if(b>=min)return lab}return '-'}
function summaryText(results,title,rid,rep,sk,ov){
  const lay=rep.layout||'generic';
  const lines=[`${t('report_title')} - ${title}`,`${t('candidate')}: ${REPCTX.name||'-'}`,`${t('report_no')}: ${rid}`,`${t('date')}: ${new Date(REPCTX.date||Date.now()).toLocaleString()}`,t('organiser'),''];
  sk.forEach(o=>lines.push(`${L(o.label)}: ${o.teacher?t('teacher_marked'):(o.v==null||isNaN(o.v)?'—':(lay==='ielts'?Number(o.v).toFixed(1):o.v)+(lay==='pte'||lay==='ielts'?'':' / '+(o.full||100)))}`));
  lines.push(`${L(rep.overall_label)||t('overall')}: ${ov.v}${ov.max?' / '+ov.max:''}${ov.res?' · '+ov.res:''}`);
  if(ov.note)lines.push(ov.note);
  results.forEach(r=>{if(r.sec.auto){lines.push('');lines.push(`${L(r.sec.title)}: ${r.raw}/${r.max}`);const wrong=r.rows.filter(x=>x.s&&x.s.got<x.s.max).map(x=>`${x.q.n}: ${showAns(x.q)}`.slice(0,60));if(wrong.length){lines.push(t('to_review')+':');lines.push(...wrong.slice(0,15));if(wrong.length>15)lines.push('…')}}
    else r.parts.forEach(p=>(p.questions||[]).forEach(q=>{const a=r.answers[q.n];if(q.type==='essay'){lines.push('');lines.push(`${q.n}. ${(q.prompt||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().slice(0,160)}`);lines.push(`(${yours(q,r.answers)})`);if(a)lines.push(a)}}))});
  const tc=REPCTX.teacher;if(tc){lines.push('');lines.push('✎ Teacher marked'+(tc.by?' · '+tc.by:''));results.forEach((r,i)=>{const x=tc.secs[i];if(x&&x.comment)lines.push(L(r.sec.title)+': '+x.comment)});if(tc.overall)lines.push(t('overall_comment')+': '+tc.overall)}
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
  ${q.type==='essay'||q.type==='speak'?`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q,ans))}</p>${s&&s.ai?`<p class="aifb"><b>🤖 ${esc(t('ai_score'))}: ${s.got}/${s.max}</b><br><small>${esc(s.fb||'')}</small></p>`:''}${q.checklist?`<p><b>${esc(t('checklist'))}:</b></p><ul>${q.checklist.map(c=>`<li>${c}</li>`).join('')}</ul>`:''}${q.model?`<details><summary>${esc(t('model_answer'))}</summary><div class="model">${q.model}</div></details>`:''}`
  :`<p><b>${esc(t('your_answer'))}:</b> ${esc(yours(q,ans))} · <b>${esc(t('correct_answer'))}:</b> ${esc(showAns(q))}${s?` · ${s.got}/${s.max}`:''}</p>`}${q.explain?`<p class="small">${q.explain}</p>`:''}</div></div>`}
// ---------- save & continue (this device only) ----------
const FV=1, SAVE_MAX=10;
function saveKey(){return 'tegmock:save:'+BANK.id}
function getSaves(){try{const a=JSON.parse(localStorage.getItem(saveKey())||'[]');return Array.isArray(a)?a:[]}catch(e){return []}}
function putSaves(a){try{if(a.length)localStorage.setItem(saveKey(),JSON.stringify(a));else localStorage.removeItem(saveKey());return true}catch(e){return false}}
function dropSave(id){if(!id||!BANK)return;putSaves(getSaves().filter(x=>x.id!==id))}
function fmtDate(x,withTime){const d=new Date(typeof x==='string'?Date.parse(x):x);if(isNaN(d))return '';try{return withTime?d.toLocaleString(LANG,{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}):d.toLocaleDateString(LANG,{day:'2-digit',month:'short',year:'numeric'})}catch(e){return d.toISOString().slice(0,16).replace('T',' ')}}
const plainTxt=s=>String(s||'').replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&').replace(/\s+/g,' ').trim();
// Questions are stored as set id + order/shuffle only; content is always rebuilt from this site's bank (a file can never inject HTML).
function packParts(parts){return parts.map(p=>({id:p.id,slot:p.slot,q:(p.questions||[]).map(q=>({n:q.n,map:q._map||null,text:plainTxt(q.prompt||q.text||'').slice(0,240)}))}))}
function findSet(sec,id){for(const sl of (sec.slots||[])){const it=(sl.sets||sl.items||[]).find(x=>x.id===id);if(it)return {sl,it}}return null}
function bankErr(){const e=new Error('bank');e.code='bank';return e}
function unpackParts(secIdx,packed){const sec=BANK.sections[secIdx];if(!sec||!Array.isArray(packed)||!packed.length)throw bankErr();
  return packed.map(pp=>{const f=findSet(sec,pp&&pp.id);if(!f)throw bankErr();const p=Object.assign({slot:f.sl.id,slotTitle:f.sl.title},JSON.parse(JSON.stringify(f.it)));const qs=p.questions||[];const pq=Array.isArray(pp.q)?pp.q:[];if(pq.length!==qs.length)throw bankErr();
    qs.forEach((q,k)=>{const x=pq[k]||{};q.n=+x.n;q.kind=q.kind||p.slot;q._tr=p.transcript||'';q._pass=p.passage||'';if(!Number.isInteger(q.n)||q.n<1)throw bankErr();const m=x.map;
      if(Array.isArray(m)&&q.options&&m.length===q.options.length&&m.slice().sort((a,b)=>a-b).every((v,i)=>v===i)){q._map=m;q._opts=m.map(i=>q.options[i])}else q._opts=q.options});return p})}
function cleanAns(parts,ans){const out={};if(!ans||typeof ans!=='object')return out;const isI=v=>Number.isInteger(v)&&v>=0&&v<1000;
  parts.forEach(p=>(p.questions||[]).forEach(q=>{const a=ans[q.n];if(a==null)return;
    switch(q.type){case 'mcq':if(isI(a))out[q.n]=a;break;
      case 'multi':case 'highlight':if(Array.isArray(a))out[q.n]=a.filter(isI);break;
      case 'order':if(Array.isArray(a)&&a.length===q.items.length&&a.slice().sort((x,y)=>x-y).every((v,i)=>v===i))out[q.n]=a;break;
      case 'cloze':if(typeof a==='object'&&!Array.isArray(a)){const o={};Object.keys(q.blanks||{}).forEach(k=>{if(typeof a[k]==='string')o[k]=a[k].slice(0,500)});out[q.n]=o}break;
      default:if(typeof a==='string')out[q.n]=a.slice(0,20000)}}));return out}
function cleanSpeech(sp){const o={};if(!sp||typeof sp!=='object')return o;Object.keys(sp).slice(0,200).forEach(k=>{const x=sp[k];if(!x||typeof x!=='object'||!/^\d+$/.test(k))return;const y={};['t0','secs','conf','pauses','lastAt'].forEach(f=>{const v=+x[f];if(Number.isFinite(v))y[f]=v});if(x.unsupported)y.unsupported=true;o[k]=y});return o}
function packRes(r){return {secIdx:r.secIdx,section:L(r.sec.title),auto:!!r.sec.auto,raw:r.raw,max:r.max,est:r.est,used:Math.round(r.used||0),timeout:!!r.timeout,parts:packParts(r.parts),answers:r.answers,speech:cleanSpeech(r.speech)}}
function unpackRes(o){if(!o||!Number.isInteger(o.secIdx))throw bankErr();const sec=BANK.sections[o.secIdx];if(!sec)throw bankErr();const parts=unpackParts(o.secIdx,o.parts);const ans=cleanAns(parts,o.answers);const speech=cleanSpeech(o.speech);
  let raw=0,max=0;const rows=[];parts.forEach(p=>(p.questions||[]).forEach(q=>{if(!sec.auto){rows.push({q,p});return}const s=scoreQ(q,ans,speech);raw+=s.got;max+=s.max;rows.push({q,p,s})}));raw=Math.round(raw*10)/10;
  const lim=(sec.minutes+(sec.review_minutes||0))*60;return {secIdx:o.secIdx,sec,raw,max,est:sec.auto&&max?conv(sec,raw,max):'',skillEst:skillEstOf(sec,rows),speech,used:Math.max(0,Math.min(lim,+o.used||0)),timeout:!!o.timeout,rows,parts,answers:ans}}
function packState(){const st={run:null,full:null};
  if(RUN&&!RUN.done)st.run={secIdx:RUN.secIdx,rid:RUN.rid,parts:packParts(RUN.parts),answers:RUN.answers,exam:!!RUN.exam,elapsed:Math.round(Math.min(RUN.limit,(Date.now()-RUN.start)/1000)),cur:RUN.cur,audioPlayed:RUN.audioPlayed,speech:cleanSpeech(RUN.speech)};
  if(FULL)st.full={k:fullsOf().indexOf(FULL.def),pos:FULL.pos,rid:FULL.rid,exam:!!FULL.exam,results:FULL.results.map(packRes)};
  return st}
function secLimit(i){const s=BANK.sections[i];return (s.minutes+(s.review_minutes||0))*60}
function makeEntry(st,id){const f=st.full?fullsOf()[st.full.k]:null;const secIdx=st.run?st.run.secIdx:f.sections[st.full.pos];
  return {id,at:Date.now(),v:IDX.version,secIdx,left:st.run?Math.max(0,secLimit(secIdx)-(+st.run.elapsed||0)):secLimit(secIdx),fk:f?st.full.k:null,pos:f?st.full.pos:null,state:st}}
// throws if the state cannot be restored with this bank
function checkState(st){if(!st||typeof st!=='object')throw new Error('data');let f=null;
  if(st.full){f=fullsOf()[st.full.k];if(!f||!Number.isInteger(st.full.pos)||st.full.pos<0||st.full.pos>=f.sections.length)throw bankErr();if(!Array.isArray(st.full.results))throw new Error('data');st.full.results.forEach(unpackRes)}
  if(st.run){if(!Number.isInteger(st.run.secIdx)||!BANK.sections[st.run.secIdx])throw bankErr();if(f&&f.sections[st.full.pos]!==st.run.secIdx)throw bankErr();unpackParts(st.run.secIdx,st.run.parts)}
  else if(!(f&&st.full.results.length))throw new Error('data')}
function restoreState(st,saveId){checkState(st);RUN=null;FULL=null;
  if(st.full){const f=fullsOf()[st.full.k];FULL={def:f,pos:st.full.pos,results:st.full.results.map(unpackRes),rid:String(st.full.rid||newRid()).slice(0,40),exam:st.full.exam!==false,saveId}}
  try{history.pushState({mock:'run'},'')}catch(e){}
  if(st.run){const r=st.run;const sec=BANK.sections[r.secIdx];const parts=unpackParts(r.secIdx,r.parts);const lim=secLimit(r.secIdx);const el=Math.max(0,Math.min(lim,+r.elapsed||0));
    RUN={name:CAND,rid:FULL?FULL.rid:String(r.rid||newRid()).slice(0,40),sec,secIdx:r.secIdx,parts,ids:parts.map(p=>p.id),answers:cleanAns(parts,r.answers),exam:r.exam!==false,start:Date.now()-el*1000,limit:lim,cur:Math.max(0,Math.min(parts.length-1,+r.cur||0)),done:false,audioPlayed:(r.audioPlayed&&typeof r.audioPlayed==='object')?r.audioPlayed:{},speech:cleanSpeech(r.speech),saveId};
    window.onbeforeunload=()=>RUN&&!RUN.done?true:null;renderRun();tick();scrollTo(0,0);return}
  interstitial(FULL.results[FULL.results.length-1])}
function leaveRun(){if(RUN)RUN.done=true;window.onbeforeunload=null;try{const au=$('#aud');if(au)au.pause()}catch(e){}if(mediaRec&&mediaRec.state==='recording')mediaRec.stop();RUN=null;FULL=null}
function goTestPage(){if(history.state&&history.state.mock==='run'){history.back()}else{testPage();scrollTo(0,0)}}
function saveLater(){if(!BANK||(!(RUN&&!RUN.done)&&!FULL))return;
  const st=packState();const id=(FULL&&FULL.saveId)||(RUN&&RUN.saveId)||('s'+Date.now().toString(36)+rnd(1296).toString(36));
  const a=getSaves().filter(x=>x.id!==id);a.unshift(makeEntry(st,id));
  if(!putSaves(a.slice(0,SAVE_MAX))){msgBox(t('save_fail'),true);return}
  leaveRun();FLASH=t('saved_ok');goTestPage()}
// ---------- .tegmock files (downloaded / opened by the user; nothing is uploaded) ----------
function fileBase(kind,name,rid){return {format:'tegmock',fv:FV,app:IDX.version,kind,test:BANK.id,testTitle:BANK.title,lang:LANG,created:new Date().toISOString(),name:String(name||'').slice(0,60),rid:String(rid||'')}}
function download(o){const slug=(o.name||'candidate').normalize('NFKD').replace(/[^\w]+/g,'-').replace(/^-|-$/g,'').slice(0,30)||'candidate';
  const fn=`${slug}_${o.rid||o.test}${o.kind==='progress'?'_progress':''}${o.teacher?'_marked':''}.tegmock`;const blob=new Blob([JSON.stringify(o)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=fn;a.rel='noopener';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},4000);return fn}
function sendProgress(){if(!BANK||(!(RUN&&!RUN.done)&&!FULL))return;const st=packState();
  const o=Object.assign(fileBase('progress',(RUN&&RUN.name)||CAND,(FULL&&FULL.rid)||(RUN&&RUN.rid)),{section:L(BANK.sections[st.run?st.run.secIdx:FULL.def.sections[FULL.pos]].title),state:st});
  const fn=download(o);msgBox(fn+' — '+t('send_teacher_note'))}
function resultFile(x,teacher){return Object.assign(fileBase('result',x.ctx.name,x.rid),{date:new Date(x.ctx.date||Date.now()).toISOString(),full:!!x.isFull,fk:fullsOf().indexOf(x.fdef),results:x.results.map(packRes),teacher:teacher||null})}
function sendResult(){if(!LAST)return;const fn=download(resultFile(LAST,LAST.ctx.teacher));msgBox(fn+' — '+t('send_teacher_note'))}
function fileBtn(id,label){return `<label class="btn ghost filebtn">${esc(label)}<input type="file" id="${id}" class="vh"></label>`}
function bindFile(id,cb){const inp=$('#'+id);if(!inp)return;inp.onchange=()=>{const f=inp.files&&inp.files[0];inp.value='';if(!f)return;
  if(f.size>5e6){msgBox(t('file_err_parse'),true);return}
  const rd=new FileReader();rd.onerror=()=>msgBox(t('file_err_parse'),true);
  rd.onload=()=>{let o;try{o=JSON.parse(String(rd.result).replace(/^﻿/,''))}catch(e){msgBox(t('file_err_parse'),true);return}const er=checkFile(o);if(er){msgBox(er,true);return}Promise.resolve(cb(o)).catch(e=>msgBox(fileErr(e),true))};rd.readAsText(f)}}
function checkFile(o){if(!o||typeof o!=='object'||Array.isArray(o)||o.format!=='tegmock')return t('file_err_type');
  if(o.fv!==FV)return t('file_err_version').replace('{v}',String(o.fv==null?'?':o.fv).slice(0,10)+(o.app?' / '+String(o.app).slice(0,20):''));
  const meta=IDX.tests.find(x=>x.id===o.test);if(!meta||!meta.ready)return t('file_err_test');
  if(o.kind==='result'){if(!Array.isArray(o.results)||!o.results.length)return t('file_err_data')}
  else if(o.kind==='progress'){if(!o.state||typeof o.state!=='object')return t('file_err_data')}
  else return t('file_err_type');return ''}
function fileErr(e){return e&&e.code==='bank'?t('file_err_bank'):t('file_err_data')}
async function loadBankFor(id){if(BANK&&BANK.id===id)return;const meta=IDX.tests.find(x=>x.id===id);BANK=await J(BASE+'banks/'+meta.file)}
async function openStudentFile(o){
  try{await loadBankFor(o.test)}catch(e){msgBox(t('file_err_test'),true);return}
  if(o.kind==='result'){let results,fdef;try{results=o.results.map(unpackRes);fdef=fullsOf()[o.fk]||fullForSec(results[0].secIdx)}catch(e){msgBox(fileErr(e),true);return}
    try{history.replaceState(null,'','?test='+BANK.id+'&lang='+LANG)}catch(e){}
    showReport(results,fdef,!!o.full,String(o.rid||'').slice(0,40)||newRid(),{name:String(o.name||'').slice(0,60),date:Date.parse(o.date)||Date.now(),teacher:cleanTeacher(o.teacher,results)});return}
  try{checkState(o.state)}catch(e){msgBox(fileErr(e),true);return}
  const nm=String(o.name||'').replace(/\s+/g,' ').trim().slice(0,60);if(nm)CAND=nm;
  try{history.replaceState(null,'','?test='+BANK.id+'&lang='+LANG)}catch(e){}
  const id='f'+Date.now().toString(36)+rnd(1296).toString(36);const a=getSaves();a.unshift(makeEntry(o.state,id));
  if(putSaves(a.slice(0,SAVE_MAX))){FLASH=t('file_loaded');testPage();scrollTo(0,0)}
  else{if(!CAND)CAND='-';restoreState(o.state,null)}}
function msgBox(text,err){let m=$('#msgbox');if(m)m.remove();m=document.createElement('div');m.id='msgbox';m.className='modal';
  m.innerHTML=`<div class="box${err?' err':''}" role="alertdialog" aria-modal="true"><p>${err?'⚠️ ':'✓ '}${esc(text)}</p><button class="btn" type="button">OK</button></div>`;
  document.body.appendChild(m);const b=$('button',m);b.onclick=()=>m.remove();try{b.focus()}catch(e){}}
// ---------- teacher marking ----------
function skLabel(rep,id){const o=(rep.skills||[]).find(x=>x.id===id);return o?L(o.label):id}
function rubricOf(rep,skill){const lay=rep.layout||'generic';
  if(lay==='ielts')return {type:'crit',crit:skill==='S'?['FC','LR','GRA','P']:['TA','CC','LR','GRA'],min:0,max:9};
  if(lay==='pte')return {type:'score',min:(rep.scale||[10,90])[0],max:(rep.scale||[10,90])[1]};
  const o=(rep.skills||[]).find(x=>x.id===skill);return {type:'score',min:0,max:(o&&o.full)||100}}
function critBand(rb,crit){const v=rb.crit.map(c=>crit[c]);if(v.some(x=>typeof x!=='number'))return null;return Math.floor(v.reduce((a,b)=>a+b,0)/v.length*2)/2}
function cleanTeacher(tc,results){if(!tc||typeof tc!=='object')return null;const s=(v,n)=>typeof v==='string'?v.slice(0,n):'';
  const out={by:s(tc.by,80),at:s(tc.at,40),overall:s(tc.overall,5000),secs:{}};const src=(tc.secs&&typeof tc.secs==='object')?tc.secs:{};
  Object.keys(src).forEach(k=>{const i=+k;if(!Number.isInteger(i)||!results[i])return;const x=src[k]||{};const o={comment:s(x.comment,5000),skills:{}};
    Object.keys((x.skills&&typeof x.skills==='object')?x.skills:{}).slice(0,6).forEach(id=>{const m=x.skills[id]||{};const crit={};Object.keys((m.crit&&typeof m.crit==='object')?m.crit:{}).slice(0,6).forEach(c=>{const y=+m.crit[c];if(Number.isFinite(y)&&y>=0&&y<=9)crit[String(c).slice(0,4)]=y});
      const v=+m.v;o.skills[String(id).slice(0,10)]={v:(m.v!=null&&m.v!==''&&Number.isFinite(v)&&v>=0&&v<=100)?v:null,crit}});out.secs[i]=o});
  const has=out.overall||Object.values(out.secs).some(x=>x.comment||Object.values(x.skills).some(m=>m.v!=null));return has?out:null}
function tmBadge(tc){return `<div class="tm-badge">✎ Teacher marked${LANG!=='en'?' · '+esc(t('tm_label')):''}${tc.by?' · '+esc(tc.by):''}${tc.at?' · '+esc(fmtDate(tc.at)):''}</div>`}
function tmBlock(results,tc,rep){
  const rows=results.map((r,i)=>{const x=tc.secs[i];if(!x)return '';const marks=Object.entries(x.skills||{}).filter(([k,m])=>m.v!=null).map(([k,m])=>`${skLabel(rep,k)}: ${rep.layout==='ielts'?Number(m.v).toFixed(1):m.v}${Object.keys(m.crit||{}).length?' ('+Object.entries(m.crit).map(([c,y])=>c+' '+y).join(', ')+')':''}`).join(' · ');
    if(!marks&&!x.comment)return '';return `<div class="tmr"><b>${esc(L(r.sec.title))}</b>${marks?`<p class="tmm">${esc(marks)}</p>`:''}${x.comment?`<p class="tmc">${esc(x.comment)}</p>`:''}</div>`}).join('');
  return `<h3>✎ ${esc(t('teacher_comments'))}</h3><div class="tm-block">${rows}${tc.overall?`<div class="tmr"><b>${esc(t('overall_comment'))}</b><p class="tmc">${esc(tc.overall)}</p></div>`:''}</div>`}
function teacherPage(){
  document.title=t('teacher_mode')+' - '+t('free_mock');
  app().innerHTML=header('👩‍🏫 '+t('teacher_mode'),esc(t('teacher_sub')))+`<div class="acts top"><a class="btn back" href="?lang=${LANG}">← ${esc(t('all_tests'))}</a> ${fileBtn('tFile','📥 '+t('teacher_open'))}</div>
  <div id="tBody">${TF?teacherBody():`<section class="card"><p>${esc(t('teacher_how'))}</p></section>`}</div>`+footer();
  bindLang();bindFile('tFile',openTeacherFile);if(TF)bindTeacher()}
async function openTeacherFile(o){if(o.kind!=='result'){msgBox(t('not_finished'),true);return}
  try{await loadBankFor(o.test)}catch(e){msgBox(t('file_err_test'),true);return}
  let results,fdef;try{results=o.results.map(unpackRes);fdef=fullsOf()[o.fk]||fullForSec(results[0].secIdx)}catch(e){msgBox(fileErr(e),true);return}
  const tc=cleanTeacher(o.teacher,results)||{by:'',at:'',overall:'',secs:{}};
  TF={o,results,fdef,isFull:!!o.full,rid:String(o.rid||'').slice(0,40),name:String(o.name||'').slice(0,60),date:Date.parse(o.date)||Date.now(),teacher:tc};
  teacherPage();scrollTo(0,0)}
function teacherBody(){const rep=repOf(TF.fdef);const tc=TF.teacher;
  const head=`<section class="card"><h2>${esc(TF.name||'-')}</h2><p class="small">${esc(TF.isFull?L(TF.fdef.title):BANK.title+' · '+t('section_only')+' · '+L(TF.results[0].sec.title))} · ${esc(fmtDate(TF.date,1))} · ${esc(t('report_no'))} ${esc(TF.rid)}</p>
  <label class="tf"><b>${esc(t('teacher_name'))}</b><input id="tBy" maxlength="80" autocomplete="off" value="${esc(tc.by)}"></label></section>`;
  const secs=TF.results.map((r,i)=>{const x=tc.secs[i]||{};
    const ai=r.sec.auto&&r.sec.skill_by_type;
    const body=ai?`<p><b>🤖 ${esc(t('ai_score'))}:</b> ${Object.entries(r.skillEst||{}).map(([k,v])=>esc(skLabel(rep,k))+' '+esc(String(v))).join(' · ')||'—'}</p><p class="small">${esc(t('teacher_override'))}</p>${answersBlock(r)}<h3 class="th">${esc(t('rubric'))}</h3>${[].concat(r.sec.skill||r.sec.skills||[]).map(sid=>rubricHTML(rep,r,i,sid,x)).join('')}`
      :r.sec.auto?`<p><b>${esc(t('auto_section'))}:</b> ${r.raw}/${r.max}${r.est!==''?' · '+esc(r.sec.score&&r.sec.score.label||'')+' '+esc(String(r.est)):''}</p><details><summary>${esc(t('review'))}</summary>${r.parts.map(p=>`<div class="rvp"><p class="rvh">${esc(L(p.title)||p.slotTitle)}</p>${(p.questions||[]).map(q=>{const y=r.rows.find(z=>z.q===q);return reviewRow(q,y&&y.s,r.answers)}).join('')}</div>`).join('')}</details>`
      :`${answersBlock(r)}<h3 class="th">${esc(t('rubric'))}</h3>${[].concat(r.sec.skill||r.sec.skills||[]).map(sid=>rubricHTML(rep,r,i,sid,x)).join('')}`;
    return `<section class="card tsec"><h2>${esc(L(r.sec.title))}</h2>${body}<label class="tf"><b>${esc(t('comment'))}</b><textarea data-cm="${i}" rows="3">${esc(x.comment||'')}</textarea></label></section>`}).join('');
  return head+secs+`<section class="card"><label class="tf"><b>${esc(t('overall_comment'))}</b><textarea id="tOv" rows="4">${esc(tc.overall)}</textarea></label>
  <div class="acts"><button class="btn ghost" id="tPrev">${esc(t('preview_report'))}</button> <button class="btn" id="tDl">💾 ${esc(t('download_marked'))}</button></div><p class="small">${esc(t('marked_hint'))}</p></section><div id="tPrevBox"></div>`}
function answersBlock(r){let spk=false;const out=r.parts.map(p=>`<div class="rvp"><p class="rvh">${esc(L(p.title)||p.slotTitle)}</p>${(p.questions||[]).map(q=>{const a=r.answers[q.n];
  const y0=r.rows.find(z=>z.q===q);const aifb=y0&&y0.s&&y0.s.ai?`<p class="aifb"><b>🤖 ${esc(t('ai_score'))}: ${y0.s.got}/${y0.s.max}</b><br><small>${esc(y0.s.fb||'')}</small></p>`:'';
  if(q.type==='speak'){spk=true;return `<div class="rv na"><div class="qn">${q.n}</div><div>${q.prompt?`<div class="qp">${q.prompt}</div>`:''}${a?`<p class="small"><b>${esc(t('ai_heard'))}:</b></p><div class="tans">${esc(a)}</div>`:''}${aifb}</div></div>`}
  if(q.type==='essay'){const w=a&&a.trim()?a.trim().split(/\s+/).length:0;return `<div class="rv na"><div class="qn">${q.n}</div><div>${q.prompt?`<details><summary>${esc(t('task'))}</summary><div class="qp">${q.prompt}</div>${q.table||''}</details>`:''}<p class="small"><b>${esc(t('your_answer'))}:</b> ${w} ${esc(t('words'))}${q.min_words?' · min '+q.min_words:''}</p><div class="tans">${a?esc(a):'—'}</div>${aifb}${q.model?`<details><summary>${esc(t('model_answer'))}</summary><div class="model">${q.model}</div></details>`:''}</div></div>`}
  const y=r.rows.find(z=>z.q===q);return reviewRow(q,y&&y.s,r.answers)}).join('')}</div>`).join('');
  return (spk?`<p class="ins">🎙 ${esc(t('audio_not_in_file'))}</p>`:'')+out}
function rubricHTML(rep,r,i,sid,x){const rb=rubricOf(rep,sid);const m=(x.skills&&x.skills[sid])||{crit:{},v:null};const key=i+'|'+sid;
  if(rb.type==='crit')return `<div class="rub"><b>${esc(skLabel(rep,sid))}</b><div class="rgrid">${rb.crit.map(c=>`<label>${esc(t('crit_'+c))} <span class="small">(${c})</span><select data-cr="${key}|${c}"><option value="">—</option>${[0,1,2,3,4,5,6,7,8,9].map(v=>`<option value="${v}"${m.crit&&m.crit[c]===v?' selected':''}>${v}</option>`).join('')}</select></label>`).join('')}</div><p class="small">${esc(t('section_score'))}: <b data-bv="${key}">${m.v!=null?Number(m.v).toFixed(1):'—'}</b> · ${esc(t('band_rule'))}</p></div>`;
  return `<div class="rub"><label><b>${esc(skLabel(rep,sid))}</b> <input type="number" inputmode="numeric" min="${rb.min}" max="${rb.max}" step="1" data-sv="${key}" value="${m.v!=null?m.v:''}"> <span class="small">${rb.min}–${rb.max}</span></label><span class="warn" data-sw="${key}" hidden>${esc(t('score_range'))} ${rb.min}–${rb.max}</span></div>`}
function tSec(i){const tc=TF.teacher;return tc.secs[i]=tc.secs[i]||{comment:'',skills:{}}}
function bindTeacher(){const rep=repOf(TF.fdef);const tc=TF.teacher;
  $('#tBy').oninput=e=>{tc.by=e.target.value.slice(0,80)};$('#tOv').oninput=e=>{tc.overall=e.target.value.slice(0,5000)};
  $$('[data-cm]').forEach(el=>el.oninput=()=>{tSec(+el.dataset.cm).comment=el.value.slice(0,5000)});
  $$('[data-cr]').forEach(el=>el.onchange=()=>{const [i,sid,c]=el.dataset.cr.split('|');const s=tSec(+i);const m=s.skills[sid]=s.skills[sid]||{crit:{},v:null};
    if(el.value==='')delete m.crit[c];else m.crit[c]=+el.value;m.v=critBand(rubricOf(rep,sid),m.crit);const b=$(`[data-bv="${i}|${sid}"]`);if(b)b.textContent=m.v!=null?m.v.toFixed(1):'—'});
  $$('[data-sv]').forEach(el=>el.oninput=()=>{const [i,sid]=el.dataset.sv.split('|');const rb=rubricOf(rep,sid);const s=tSec(+i);const m=s.skills[sid]=s.skills[sid]||{crit:{},v:null};const v=el.value===''?null:Math.round(+el.value);
    const bad=v!=null&&(!Number.isFinite(v)||v<rb.min||v>rb.max);$(`[data-sw="${i}|${sid}"]`).hidden=!bad;m.v=bad?null:v});
  $('#tPrev').onclick=()=>{const cl=cleanTeacher(Object.assign({},tc,{at:new Date().toISOString()}),TF.results);REPCTX={name:TF.name,date:TF.date,teacher:cl};LAST=null;
    $('#tPrevBox').innerHTML=`<section class="card result">${buildReport(TF.results,TF.fdef,TF.isFull,TF.rid).html}<div class="acts"><button class="btn pdf" id="tPrint">PDF / ${esc(t('print'))}</button></div></section>`;
    $('#tPrint').onclick=()=>{document.body.classList.add('tprint');window.print();setTimeout(()=>document.body.classList.remove('tprint'),500)};$('#tPrevBox').scrollIntoView({block:'start'})};
  $('#tDl').onclick=()=>{if($$('[data-sw]').some(w=>!w.hidden)){msgBox(t('score_range'),true);return}
    const cl=cleanTeacher(Object.assign({},tc,{at:new Date().toISOString()}),TF.results);if(!cl){msgBox(t('nothing_marked'),true);return}
    const fn=download(resultFile({ctx:{name:TF.name,date:TF.date},rid:TF.rid,isFull:TF.isFull,fdef:TF.fdef,results:TF.results},cl));msgBox(fn+' — '+t('marked_hint'))}}
// ---------- boot ----------
window.addEventListener('popstate',()=>{if(!BANK||MODE)return;
  if(RUN&&!RUN.done){if(!confirm(t('leave_confirm'))){try{history.pushState({mock:'run'},'')}catch(e){}return}RUN.done=true;window.onbeforeunload=null;if(mediaRec&&mediaRec.state==='recording')mediaRec.stop()}
  FULL=null;RUN=null;testPage();scrollTo(0,0)});
(async function(){
  try{UI=await J(BASE+'banks/ui.json?t='+Math.floor(Date.now()/6e5));IDX=await J(BASE+'banks/index.json?t='+Math.floor(Date.now()/6e4));window.MOCK_V=IDX.version||'1';try{const lk=document.createElement('link');lk.rel='stylesheet';lk.href=BASE+'style.css?v='+encodeURIComponent(window.MOCK_V);document.head.appendChild(lk)}catch(_){}}catch(e){app().innerHTML='<p>Load error. Please refresh.</p>';return}
  document.documentElement.lang=LANG;
  if(MODE==='guru'){teacherPage();return}
  const id=Q.get('test');
  if(!id){home();return}
  const meta=IDX.tests.find(x=>x.id===id);
  if(!meta||!meta.ready){home();return}
  try{BANK=await J(BASE+'banks/'+meta.file)}catch(e){app().innerHTML='<p>Load error.</p>';return}
  testPage();
})();
})();
