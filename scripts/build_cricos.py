import csv, json, collections, re, glob, os, sys
RAW='raw'; OUT='out'
DATE='2026-11-02'
def rd(f): return list(csv.DictReader(open(f'{RAW}/{f}',encoding='utf-8-sig')))
inst=rd('CRICOS Institutions.csv'); courses=rd('CRICOS Courses.csv'); cl=rd('CRICOS Course Locations.csv')
def money(s):
    s=(s or '').replace('$','').replace(',','').strip()
    try: return round(float(s))
    except: return None
VET={'Certificate I','Certificate II','Certificate III','Certificate IV','Diploma','Advanced Diploma','Vocational Short Course'}
HE={'Bachelor Degree','Bachelor Honours Degree','Masters Degree (Coursework)','Masters Degree (Research)','Masters Degree (Extended)','Doctoral Degree','Graduate Diploma','Graduate Certificate','Associate Degree'}
SCH={'Senior Secondary Certificate of Education','Primary School Studies','Junior Secondary Studies'}
def sector(c):
    lv=c['Course Level']; det=c['Field of Education 1 Detailed Field']
    if 'ELICOS' in det: return 'ELICOS'
    if lv in SCH: return 'Schools'
    if lv in ('Graduate Diploma','Graduate Certificate') and c['VET National Code']: return 'VET'
    if lv in VET: return 'VET'
    if lv in HE: return 'Higher Education'
    if c['Foundation Studies']=='Yes': return 'Foundation'
    return 'Other'
locs=collections.defaultdict(set)
for r in cl: locs[r['CRICOS Course Code']].add((r['Location City'].title(), r['Location State']))
# partner flags (internal research list)
yes=set()
for f in glob.glob('/home/claude/yes/results/*.json'):
    for r in json.load(open(f)):
        if r.get('country')=='Australia':
            for code in re.findall(r'\b(0\d{4}[A-Z])\b', str(r.get('provider_code',''))+' '+str(r.get('official_name',''))):
                yes.add(code)
prov={}
for i in inst:
    code=i['CRICOS Provider Code'].strip()
    if not code: continue
    w=i['Website'].strip()
    if w and not w.startswith('http'): w='https://'+w
    prov[code]={'code':code,'name':i['Institution Name'].strip(),'trading_name':i['Trading Name'].strip(),'type':i['Institution Type'],
                'website':w,'capacity':i['Institution Capacity'],'courses':0,'sectors':set(),'states':set(),'cities':set(),
                'teg_partner':code in yes,'min_total':None}
bycode=collections.defaultdict(list)
for c in courses:
    if c['Expired']!='No': continue
    p=c['CRICOS Provider Code'].strip()
    if p not in prov: continue
    sec=sector(c); L=sorted(locs.get(c['CRICOS Course Code'],[]))
    item={'code':c['CRICOS Course Code'],'name':c['Course Name'].strip(),'vet_code':c['VET National Code'],'level':c['Course Level'],'sector':sec,
          'field':re.sub(r'^\d+ - ','',c['Field of Education 1 Broad Field']),'field_narrow':re.sub(r'^\d+ - ','',c['Field of Education 1 Narrow Field']),
          'weeks':int(c['Duration (Weeks)']) if c['Duration (Weeks)'].isdigit() else None,'tuition':money(c['Tuition Fee']),'non_tuition':money(c['Non Tuition Fee']),
          'total':money(c['Estimated Total Course Cost']),'work_component':c['Work Component']=='Yes','language':c['Course Language'],
          'locations':[{'city':a,'state':b} for a,b in L]}
    bycode[p].append(item)
    P=prov[p]; P['courses']+=1; P['sectors'].add(sec)
    for a,b in L: P['states'].add(b); P['cities'].add(a)
    if item['total'] and (P['min_total'] is None or item['total']<P['min_total']): P['min_total']=item['total']
os.makedirs(f'{OUT}/cricos',exist_ok=True)
plist=[]
for code,P in sorted(prov.items(), key=lambda x:x[1]['name'].lower()):
    if P['courses']==0: continue
    P['sectors']=sorted(P['sectors']); P['states']=sorted(P['states']); P['cities']=sorted(P['cities'])
    P['courses_file']=f'https://info.talentededucationgroup.com/data/cricos/{code}.json'
    plist.append(P)
    json.dump({'provider':code,'name':P['name'],'data_date':DATE,'courses':sorted(bycode[code],key=lambda x:(x['sector'],x['level'],x['name']))},
              open(f'{OUT}/cricos/{code}.json','w'),ensure_ascii=False,separators=(',',':'))
idx={'source':'CRICOS Provider Export (Department of Education, Australian Government) - snapshot','data_date':DATE,
     'live_search':'https://cricos.education.gov.au/','updated_at':'2026-11-11T03:00:00+07:00',
     'label_id':'Harga resmi CRICOS (indikatif) - bukan harga TEG; dana awal & jadwal bayar mengikuti offer letter. Hubungi konsultan TEG untuk penawaran.',
     'label_en':'Official CRICOS price (indicative) - not a TEG quote; upfront payment & schedule follow the offer letter. Contact a TEG consultant for a quote.',
     'note_id':'Terdaftar CRICOS memenuhi syarat dasar visa pelajar, bukan jaminan visa.','note_en':'CRICOS registration meets the basic student visa requirement; it is not a visa guarantee.',
     'counts':{'providers':len(plist),'courses':sum(p['courses'] for p in plist)},
     'providers':plist}
json.dump(idx,open(f'{OUT}/cricos.json','w'),ensure_ascii=False,separators=(',',':'))
print(idx['counts'], 'teg partners flagged', sum(p['teg_partner'] for p in plist), 'idx KB', os.path.getsize(f'{OUT}/cricos.json')//1024)
L={
'th':("ราคาทางการจาก CRICOS (โดยประมาณ) - ไม่ใช่ใบเสนอราคาของ TEG; เงินชำระล่วงหน้าและกำหนดการชำระเป็นไปตาม offer letter ติดต่อที่ปรึกษา TEG เพื่อขอใบเสนอราคา","การลงทะเบียน CRICOS เป็นเงื่อนไขพื้นฐานของวีซ่านักเรียน ไม่ใช่การรับประกันวีซ่า"),
'vi':("Giá chính thức theo CRICOS (tham khảo) - không phải báo giá của TEG; khoản trả trước và lịch thanh toán theo offer letter. Liên hệ tư vấn viên TEG để nhận báo giá.","Đăng ký CRICOS đáp ứng điều kiện cơ bản của visa du học, không phải là bảo đảm visa."),
'zh':("CRICOS 官方价格（参考）——并非 TEG 报价；首付款及付款安排以 offer letter 为准。请联系 TEG 顾问获取报价。","在 CRICOS 注册符合学生签证的基本要求，但不保证获签。"),
'ja':("CRICOS公式価格（目安）- TEGの見積もりではありません。初期費用と支払いスケジュールは offer letter に従います。見積もりは TEG コンサルタントへお問い合わせください。","CRICOS登録は学生ビザの基本要件を満たすものであり、ビザを保証するものではありません。"),
'ko':("CRICOS 공식 가격(참고용) - TEG 견적이 아닙니다. 초기 납부금과 납부 일정은 offer letter를 따릅니다. 견적은 TEG 상담사에게 문의하세요.","CRICOS 등록은 학생 비자의 기본 요건을 충족한다는 의미이며 비자를 보장하지 않습니다."),
'km':("តម្លៃផ្លូវការ CRICOS (ប្រហាក់ប្រហែល) - មិនមែនជាសម្រង់តម្លៃរបស់ TEG ទេ ការបង់ប្រាក់ដំបូង និងកាលវិភាគបង់ប្រាក់អនុវត្តតាម offer letter ។ សូមទាក់ទងអ្នកប្រឹក្សា TEG ដើម្បីទទួលសម្រង់តម្លៃ។","ការចុះបញ្ជី CRICOS បំពេញលក្ខខណ្ឌមូលដ្ឋាននៃទិដ្ឋាការសិស្ស មិនមែនជាការធានាទិដ្ឋាការទេ។"),
'fr':("Prix officiel CRICOS (indicatif) - pas un devis TEG ; le paiement initial et l'échéancier suivent l'offer letter. Contacte un conseiller TEG pour un devis.","L'enregistrement CRICOS remplit la condition de base du visa étudiant ; ce n'est pas une garantie de visa."),
'pt':("Preço oficial CRICOS (indicativo) - não é uma cotação da TEG; pagamento inicial e cronograma seguem a offer letter. Fale com um consultor TEG para uma cotação.","O registro no CRICOS atende ao requisito básico do visto de estudante; não é garantia de visto."),
'es':("Precio oficial CRICOS (indicativo) - no es una cotización de TEG; el pago inicial y el calendario siguen la offer letter. Contacta a un asesor de TEG para una cotización.","El registro en CRICOS cumple el requisito básico de la visa de estudiante; no garantiza la visa."),
'de':("Offizieller CRICOS-Preis (Richtwert) - kein TEG-Angebot; Anzahlung und Zahlungsplan richten sich nach dem Offer Letter. Wende dich für ein Angebot an eine TEG-Beratung.","Die CRICOS-Registrierung erfüllt die Grundvoraussetzung für das Studentenvisum; sie ist keine Visumsgarantie."),
'it':("Prezzo ufficiale CRICOS (indicativo) - non è un preventivo TEG; acconto e piano di pagamento seguono l'offer letter. Contatta un consulente TEG per un preventivo.","La registrazione CRICOS soddisfa il requisito di base del visto per studenti; non è una garanzia di visto."),
'nl':("Officiële CRICOS-prijs (indicatief) - geen offerte van TEG; aanbetaling en betaalschema volgen de offer letter. Neem contact op met een TEG-consulent voor een offerte.","CRICOS-registratie voldoet aan de basisvoorwaarde voor het studentenvisum; het is geen visumgarantie."),
'ru':("Официальная цена CRICOS (ориентировочно) - это не предложение TEG; первый платёж и график оплаты указаны в offer letter. Обратитесь к консультанту TEG за расчётом.","Регистрация в CRICOS отвечает базовому требованию студенческой визы, но не гарантирует визу."),
}
for k,(a,b) in L.items(): idx['label_'+k]=a; idx['note_'+k]=b
json.dump(idx,open(f'{OUT}/cricos.json','w'),ensure_ascii=False,separators=(',',':'))
print('langs ok')
