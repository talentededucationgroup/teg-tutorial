"""Buat events/teg-events.ics (kalender iCal publik) dari data/events.json.
Dipakai website GoDaddy talentededucationgroup.com (Events > Link a Calendar) & aplikasi kalender.
Hanya data publik: judul, waktu, tempat, peserta. Tanpa biaya stand/rekening/kontak panitia."""
import json, re, datetime as dt, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((R / 'data/events.json').read_text(encoding='utf-8'))
WIB = dt.timezone(dt.timedelta(hours=7))
def esc(s): return str(s).replace('\\', '\\\\').replace(';', r'\;').replace(',', r'\,').replace('\n', r'\n')
def fold(line):
    b = line.encode('utf-8'); out = []
    while len(b) > 74:
        i = 74
        while (b[i] & 0xC0) == 0x80: i -= 1
        out.append(b[:i].decode()); b = b' ' + b[i:]
    out.append(b.decode()); return '\r\n'.join(out)
def stamp(day, hm): 
    h, m = hm
    return dt.datetime.fromisoformat(day).replace(hour=h, minute=m, tzinfo=WIB).astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
now = re.sub(r'\D', '', str(d.get('updated') or '2026-11-27'))[:8] + 'T000000Z'  # stabil: file hanya berubah bila data berubah
L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Talented Education Group//Events//ID', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
     'X-WR-CALNAME:Talented Education Group - Event & Expo', 'X-WR-TIMEZONE:Asia/Jakarta']
for e in sorted(d['items'], key=lambda x: x['start']):
    t = re.findall(r'(\d{1,2})[.:](\d{2})', e.get('time') or '')
    end = e.get('end') or e['start']
    L += ['BEGIN:VEVENT', f"UID:{e['id']}@talentededucationgroup.com", f'DTSTAMP:{now}']
    if len(t) >= 2:
        L += [f"DTSTART:{stamp(e['start'], tuple(map(int, t[0])))}", f"DTEND:{stamp(end, tuple(map(int, t[1])))}"]
    else:
        nxt = (dt.date.fromisoformat(end) + dt.timedelta(days=1)).strftime('%Y%m%d')
        L += [f"DTSTART;VALUE=DATE:{e['start'].replace('-', '')}", f'DTEND;VALUE=DATE:{nxt}']
    title = e['title'].get('id') or e['title'].get('en')
    aud = (e.get('audience') or {}).get('id', '')
    days = e['start'] if end == e['start'] else f"{e['start']} s.d. {end}"
    desc = f"{aud}\nTanggal: {days}, {e.get('time','')}\nKonsultasi gratis bersama Talented Education Group (studi Australia & New Zealand).\nInfo & daftar: https://linktr.ee/talentededucationgroup"
    L += [fold('SUMMARY:' + esc(title)), fold('LOCATION:' + esc(e.get('venue') or e.get('city', ''))),
          fold('DESCRIPTION:' + esc(desc)), 'URL:https://info.talentededucationgroup.com/events/', 'STATUS:CONFIRMED', 'TRANSP:OPAQUE', 'END:VEVENT']
L.append('END:VCALENDAR')
(R / 'events/teg-events.ics').write_text('\r\n'.join(L) + '\r\n', encoding='utf-8', newline='')
print('events/teg-events.ics:', sum(1 for x in L if x == 'BEGIN:VEVENT'), 'event')
