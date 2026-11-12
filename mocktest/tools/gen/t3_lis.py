# JLPT listening fix: 発話表現 (N5-N3, illustration + audio situation + audio options) and
# 即時応答 (N5-N1, audio trigger + audio options). Options are read in the audio in a fixed order,
# so they are never shuffled in the app (shuffle:false, aopts:true); the key is the position in that order.
# usage: python3 t3_lis.py bank   |   python3 t3_lis.py ssml
import json, sys, html, random, os, re
sys.path.insert(0, '/home/claude/w91')
from t3_svg import svg
ROOT = '/home/claude/teg-tutorial/mocktest/'
B = ROOT + 'banks/jlpt.json'
NAR = 'ja-JP-ShioriNeural'; MV = ['ja-JP-KeitaNeural', 'ja-JP-DaichiNeural', 'ja-JP-NaokiNeural']; FV = ['ja-JP-NanamiNeural', 'ja-JP-AoiNeural', 'ja-JP-MayuNeural']
WHO = {'M': '男', 'F': '女'}
NUM = ['いち', 'に', 'さん']

H = {  # 発話表現: (situation read by narrator, speaker under the arrow, scene, correct, [distractors], id, en)
 'N5': [
  ('あさ、がっこうで せんせいに あいました。やじるしの ひとは なんと いいますか。', 'F', 'school_morning', 'おはよう ございます。', ['おやすみなさい。', 'こんばんは。'], 'Pagi bertemu guru → おはようございます (selamat pagi).', 'Meeting a teacher in the morning → "Good morning."'),
  ('これから ごはんを たべます。やじるしの ひとは なんと いいますか。', 'M', 'meal', 'いただきます。', ['ごちそうさまでした。', 'いってきます。'], 'Sebelum makan → いただきます.', 'Before eating → "itadakimasu".'),
  ('いまから がっこうへ いきます。やじるしの ひとは なんと いいますか。', 'M', 'door_out', 'いってきます。', ['ただいま。', 'いってらっしゃい。'], 'Berangkat dari rumah → いってきます (saya berangkat).', 'Leaving home → "I’m off."'),
  ('みせで りんごが ほしいです。やじるしの ひとは なんと いいますか。', 'F', 'shop_fruit', 'りんごを ください。', ['りんごを どうぞ。', 'りんごは いかがですか。'], 'Meminta barang di toko → ～を ください.', 'Asking for something in a shop → "Apples, please."'),
  ('ともだちに プレゼントを もらいました。やじるしの ひとは なんと いいますか。', 'M', 'gift', 'ありがとう。', ['どう いたしまして。', 'おやすみなさい。'], 'Menerima hadiah → ありがとう (terima kasih).', 'Receiving a present → "Thank you."'),
  ('でんしゃで ひとの あしを ふみました。やじるしの ひとは なんと いいますか。', 'F', 'train_foot', 'あ、すみません。', ['どう いたしまして。', 'いただきます。'], 'Tidak sengaja menginjak kaki → すみません (maaf).', 'Stepping on someone’s foot → "Sorry."'),
  ('がっこうから いえに かえりました。やじるしの ひとは なんと いいますか。', 'F', 'door_in', 'ただいま。', ['いってきます。', 'おかえりなさい。'], 'Pulang ke rumah → ただいま (saya pulang).', 'Coming home → "I’m home."'),
  ('せんせいの へやに はいります。やじるしの ひとは なんと いいますか。', 'M', 'office_door', 'しつれいします。', ['いらっしゃいませ。', 'おかえりなさい。'], 'Masuk ruang guru → しつれいします (permisi).', 'Entering the teachers’ room → "Excuse me."'),
  ('よる、これから ねます。やじるしの ひとは なんと いいますか。', 'F', 'night', 'おやすみなさい。', ['おはよう ございます。', 'いってきます。'], 'Mau tidur → おやすみなさい (selamat tidur).', 'Going to bed → "Good night."'),
  ('ともだちの ペンを つかいたいです。やじるしの ひとは なんと いいますか。', 'F', 'pen', 'ペンを かして ください。', ['ペンを かりて ください。', 'ペンを かえして ください。'], 'Meminjam pena → かして ください (tolong pinjamkan).', 'Borrowing a pen → "Please lend me your pen."'),
 ],
 'N4': [
  ('友だちが びょうきで 入院して います。やじるしの 人は 帰る とき、何と 言いますか。', 'F', 'hospital', 'お大事に。', ['おめでとう。', 'いってきます。'], 'Pamit ke orang sakit → お大事に (semoga cepat sembuh).', 'Leaving a sick friend → "Take care of yourself."'),
  ('へやが 暑いです。まどを 開けて ほしいです。やじるしの 人は 何と 言いますか。', 'M', 'hot_room', 'まどを 開けて もらえませんか。', ['まどを 開けて あげましょうか。', 'まどを 開けても いいですよ。'], 'Meminta orang lain membuka jendela → ～て もらえませんか.', 'Asking someone to open the window → "Could you open the window?"'),
  ('雨が ふって きましたが、かさが ありません。やじるしの 人は 何と 言いますか。', 'F', 'rain', 'かさに 入れて もらえない？', ['かさを かして あげようか。', 'かさを 持って きたよ。'], 'Ingin ikut berpayung → かさに 入れて もらえない？', 'Asking to share an umbrella → "Can I come under your umbrella?"'),
  ('先生の 荷物が 重そうです。やじるしの 人は 何と 言いますか。', 'M', 'boxes', 'お持ちしましょうか。', ['持って いただけますか。', '持って くださいませんか。'], 'Menawarkan bantuan (sopan) → お持ちしましょうか.', 'Offering to carry → "Shall I carry that for you?"'),
  ('じゅぎょうに おくれて しまいました。やじるしの 人は 何と 言いますか。', 'M', 'late', 'おくれて すみません。', ['おくれても いいですか。', 'お先に しつれいします。'], 'Terlambat masuk kelas → おくれて すみません.', 'Arriving late → "Sorry I’m late."'),
  ('レストランで 水が ほしいです。やじるしの 人は 何と 言いますか。', 'F', 'restaurant', 'すみません、お水を ください。', ['お水は いかがですか。', 'お水を どうぞ。'], 'Meminta air di restoran → お水を ください.', 'Asking for water → "Excuse me, water please."'),
  ('ほかの 人に 写真を とって ほしいです。やじるしの 人は 何と 言いますか。', 'M', 'photo', 'すみません、写真を とって いただけませんか。', ['写真を とって あげましょうか。', '写真を とっても いいですよ。'], 'Minta difoto orang lain → ～て いただけませんか.', 'Asking a stranger to take a photo.'),
  ('仕事が 終わって、みんなより 先に 帰ります。やじるしの 人は 何と 言いますか。', 'M', 'office_leave', 'お先に しつれいします。', ['いってらっしゃい。', 'おじゃまします。'], 'Pulang lebih dulu dari kantor → お先に しつれいします.', 'Leaving work before others → "Excuse me for leaving first."'),
  ('友だちの 家に 入ります。やじるしの 人は 何と 言いますか。', 'M', 'visit', 'おじゃまします。', ['ただいま。', 'いらっしゃい。'], 'Masuk rumah teman → おじゃまします (permisi).', 'Entering someone’s home → "Sorry to intrude."'),
  ('駅へ 行きたいですが、道が わかりません。やじるしの 人は 何と 言いますか。', 'F', 'lost', 'すみません、駅は どちらですか。', ['駅まで 送りましょうか。', '駅へ 行きませんか。'], 'Bertanya arah → 駅は どちらですか.', 'Asking the way → "Excuse me, which way is the station?"'),
 ],
 'N3': [
  ('友達の家に遊びに来ています。そろそろ帰りたいです。矢印の人は何と言いますか。', 'F', 'leave_friend', 'そろそろ失礼します。', ['いただきます。', 'お先にどうぞ。'], 'Pamit dari rumah teman → そろそろ失礼します.', 'Leaving a friend’s home → "I should be going now."'),
  ('作った資料を先生に見てもらいたいです。矢印の人は何と言いますか。', 'M', 'teacher_doc', 'この資料を見ていただけませんか。', ['この資料を見てあげましょうか。', 'この資料を見せてください。'], 'Meminta guru memeriksa → ～ていただけませんか.', 'Politely asking the teacher to look at the document.'),
  ('電車で座っています。お年寄りが乗ってきました。矢印の人は何と言いますか。', 'F', 'seat', 'どうぞ、座ってください。', ['すみません、座ります。', '座ってもいいですか。'], 'Menawarkan kursi → どうぞ、座ってください.', 'Offering a seat → "Please, have a seat."'),
  ('仕事が終わりました。同僚より先に帰ります。矢印の人は何と言いますか。', 'M', 'office_leave', 'お先に失礼します。', ['ただいま。', 'お邪魔します。'], 'Pulang lebih dulu → お先に失礼します.', 'Leaving before colleagues → "Excuse me for leaving first."'),
 ]}

S = {  # 即時応答: (speaker A, utterance, speaker B, correct reply, [distractors], id, en)
 'N5': [
  ('F', 'おなまえは？', 'M', 'やまだです。', ['げんきです。', 'にほんです。'], 'Ditanya nama → sebut nama.', 'Asked your name → give your name.'),
  ('M', 'いま なんじですか。', 'F', '3じです。', ['3かいです。', '3ばんです。'], 'なんじ = jam berapa.', 'なんじ = what time.'),
  ('F', 'いってらっしゃい。', 'M', 'いってきます。', ['ただいま。', 'おかえりなさい。'], 'いってらっしゃい → いってきます.', '"Have a good day" → "I’m off."'),
  ('M', 'この ほん、だれのですか。', 'F', 'わたしのです。', ['きのう かいました。', 'にほんごの ほんです。'], 'だれの = milik siapa.', 'だれの = whose.'),
  ('F', 'コーヒー、もう いっぱい いかがですか。', 'M', 'いいえ、もう けっこうです。', ['はい、コーヒーを のみました。', 'コーヒーは あついです。'], 'Menolak tawaran dengan sopan → もう けっこうです.', 'Politely declining another cup.'),
  ('M', 'しゅくだいは もう おわりましたか。', 'F', 'いいえ、まだです。', ['はい、まだです。', 'いいえ、しゅくだいです。'], 'もう ～ましたか → いいえ、まだです (belum).', '"Have you finished?" → "No, not yet."'),
  ('F', 'どこへ いきますか。', 'M', 'ぎんこうへ いきます。', ['ひとりで いきます。', 'バスで いきます。'], 'どこへ = ke mana (tempat).', 'どこへ asks where to.'),
  ('M', 'あした、いっしょに えいがを みませんか。', 'F', 'いいですね。みましょう。', ['はい、みませんでした。', 'えいがかんです。'], 'Ajakan ～ませんか → ～ましょう.', 'Invitation → "Sounds good, let’s."'),
  ('F', 'その かばん、すてきですね。', 'M', 'ありがとう ございます。', ['どう いたしまして。', 'いいえ、かばんです。'], 'Dipuji → ありがとう ございます.', 'Receiving a compliment → "Thank you."'),
  ('M', 'きのう、どこかへ いきましたか。', 'F', 'いいえ、どこへも いきませんでした。', ['いいえ、どこかへ いきます。', 'はい、どこへも いきません。'], 'どこかへ？ → いいえ、どこへも ～ません.', '"Did you go anywhere?" → "No, nowhere."'),
 ],
 'N4': [
  ('M', 'この 書類、明日までに コピーして もらえる？', 'F', 'うん、わかった。', ['うん、コピーして あげたよ。', '明日 コピーしたよ。'], 'Permintaan → menyanggupi.', 'A request → agree to do it.'),
  ('F', 'お先に しつれいします。', 'M', 'おつかれさまでした。', ['いってらっしゃい。', 'おかえりなさい。'], 'Rekan pulang duluan → おつかれさまでした.', 'A colleague leaves first → "Thanks for your work."'),
  ('M', 'すみません、この 席、空いて いますか。', 'F', 'ええ、どうぞ。', ['はい、空きました。', 'いいえ、どう いたしまして。'], 'Kursi kosong? → ええ、どうぞ.', '"Is this seat free?" → "Yes, go ahead."'),
  ('F', '週末は 何を する つもり？', 'M', '家で ゆっくり しようと 思って いるんだ。', ['週末に したよ。', 'とても 楽しかったよ。'], 'Rencana (つもり) → ～ようと 思って いる.', 'Asked about plans → state a plan.'),
  ('M', 'よかったら、この かさ、使って ください。', 'F', 'ありがとう ございます。助かります。', ['いいえ、使って ください。', 'どう いたしまして。'], 'Ditawari payung → 助かります.', 'Offered an umbrella → "Thank you, that helps."'),
  ('F', 'かぜは もう よく なりましたか。', 'M', 'おかげさまで、元気に なりました。', ['はい、かぜを ひきました。', 'はい、お大事に。'], 'Ditanya kesehatan → おかげさまで.', 'Asked if you’re better → "Yes, thanks."'),
  ('M', '駅まで 車で 送りましょうか。', 'F', 'いいんですか。じゃあ、お願いします。', ['はい、送って あげます。', '駅まで 送りました。'], 'Tawaran mengantar → お願いします.', 'Offer of a ride → accept.'),
  ('F', 'あれ、田中さん、今日は 来ないの？', 'M', 'うん、熱が あるらしいよ。', ['うん、来たよ。', '今日は 月曜日だよ。'], 'Kenapa tidak datang → alasan.', 'Why isn’t he coming → give the reason.'),
  ('M', 'その ケーキ、おいしそうですね。', 'F', 'よかったら、一つ どうぞ。', ['はい、おいしそうでした。', 'いいえ、ケーキです。'], 'Menawarkan → よかったら どうぞ.', 'Offer a piece.'),
  ('F', '電話を かけても、だれも 出ないんです。', 'M', 'もう 出かけたのかも しれませんね。', ['じゃあ、電話に 出ましょう。', 'はい、出て います。'], 'Tidak diangkat → mungkin sudah pergi.', 'No one answers → maybe they’ve gone out.'),
 ],
 'N3': [
  ('M', 'この荷物、ちょっと持ってもらえる？', 'F', 'うん、いいよ。どこに置く？', ['はい、持ってきました。', 'いいえ、持っていません。'], 'Permintaan tolong → menyanggupi.', 'A request for help → agree.'),
  ('F', '明日の会議、何時からだっけ？', 'M', '十時からだよ。', ['会議室でだよ。', '明日は休みだよ。'], '何時から → jam.', 'Asks what time.'),
  ('F', '遅くなってすみません。', 'M', 'いいえ、私も今来たところです。', ['はい、遅くなりました。', 'どういたしまして。'], 'Menjawab permintaan maaf.', 'Reply to an apology.'),
  ('M', 'このペン、借りてもいいですか。', 'F', 'ええ、どうぞ。', ['はい、貸してください。', 'いいえ、借りません。'], 'Izin meminjam → silakan.', 'Permission granted.'),
 ],
 'N2': [
  ('M', 'この書類、今日中に目を通しておいてもらえるかな。', 'F', 'はい、帰るまでに読んでおきます。', ['はい、目が痛いです。', 'いいえ、通っていません。'], '目を通す = membaca sekilas.', 'Agree to read it today.'),
  ('F', 'せっかく来てくれたのに、留守にしていてごめんね。', 'M', 'いえいえ、連絡しないで来た私が悪いんです。', ['はい、留守番をしていました。', 'どういたしまして。'], 'Menanggapi permintaan maaf.', 'Reply to an apology.'),
  ('M', '例の件、部長にはもう話を通してあるから。', 'F', 'ありがとうございます。それなら安心です。', ['では、部長に話してきます。', 'まだ通っていません。'], '話を通してある = sudah dibicarakan.', 'Already arranged with the manager.'),
  ('F', '雨、降りそうで降らないね。', 'M', 'うん、傘、持っていくかどうか迷うね。', ['うん、ひどい雨だね。', 'いや、もう止んだよ。'], 'Belum hujan tapi mendung.', 'Not raining yet.'),
 ],
 'N1': [
  ('M', 'この企画、もう少し練ってから出したほうがよかったんじゃない？', 'F', '確かに、詰めが甘かったかもしれません。', ['はい、もう出しました。', 'いえ、練習はしていません。'], '練る = mematangkan.', 'Admit it needed more work.'),
  ('F', 'お忙しいところ、恐れ入りますが。', 'M', 'いえ、どうぞ。何でしょうか。', ['はい、忙しいです。', '恐れ入りました。'], 'Pembuka permintaan sopan.', 'Polite opener.'),
  ('M', '今回の件は、君に一任するよ。', 'F', '承知しました。責任を持って進めます。', ['では、部長にお任せします。', 'いえ、一人ではありません。'], '一任 = menyerahkan sepenuhnya.', 'Accept responsibility.'),
  ('F', '今さら言っても始まらないけど、もっと早く相談してほしかったな。', 'M', '申し訳ありません。次からはすぐにご相談します。', ['はい、今から始めます。', '早く言ってよかったです。'], 'Menyesal; berjanji lain kali.', 'Apologise and promise.'),
 ]}

INS = {'N5': {'l4': 'えを みながら しつもんを きいて ください。→（やじるし）の ひとは なんと いいますか。1から3の なかから、いちばん いい ものを ひとつ えらんで ください。',
              'l5': 'えなどが ありません。ぶんを きいて、1から3の なかから、いちばん いい ものを ひとつ えらんで ください。'},
       'N4': {'l4': '絵を 見ながら 質問を 聞いて ください。→（やじるし）の 人は 何と 言いますか。1から3の 中から、いちばん いい ものを 一つ えらんで ください。',
              'l5': '絵などが ありません。文を 聞いて、1から3の 中から、いちばん いい ものを 一つ えらんで ください。'}}
for lv in ('N3', 'N2', 'N1'):
    INS[lv] = {'l4': '絵を見ながら質問を聞いてください。→（矢印）の人は何と言いますか。1から3の中から、最もよいものを一つ選んでください。',
               'l5': '問題用紙に何も印刷されていません。まず文を聞いてください。それから、それに対する返事を聞いて、1から3の中から、最もよいものを一つ選んでください。'}
TITLE = {'l4': '発話表現', 'l5': '即時応答'}
QP = {'N5': 'へんじとして いちばん いい ものは どれですか。', 'N4': '返事として いちばん いい ものは どれですか。'}
NUMLBL = ['いち', 'に', 'さん']
# pronunciation fixes for audio only (checked with ASR): text on screen keeps the kanji
SAY = {'練って': 'ねって', '今来た': 'いま来た', '今日中に': 'きょうじゅうに'}
def say(t):
    for a, b in SAY.items(): t = t.replace(a, b)
    return t.replace(' ', '')

def sets_for(lv, slot):
    data = (H if slot == 'l4' else S).get(lv, [])
    out = []
    for si in range(0, len(data), 2):
        letter = 'abcdefghij'[si // 2]
        sid = f'{lv}L{slot[1]}{letter}'
        m, f = MV[(si // 2) % 3], FV[(si // 2) % 3]
        voice = {'M': m, 'F': f}
        tr, x, qs = '', '', []
        for i, it in enumerate(data[si:si + 2], 1):
            if slot == 'l4':
                sit, who, scene_, ok, ng, eid, een = it
            else:
                wa, trig, who, ok, ng, eid, een = it
            opts = [ok] + ng
            rng = random.Random(f'{sid}-{i}')
            order = list(range(3)); rng.shuffle(order)
            options = [opts[k] for k in order]; ans = order.index(0)
            nar = lambda s: f"<voice name='{NAR}'>{html.escape(say(s), quote=False)}"
            if slot == 'l4':
                x += nar(f'{i}番。') + "<break time='400ms'/>" + html.escape(say(sit), quote=False) + "<break time='1200ms'/></voice>"
                tr += f'<b>{i}番</b><br><i>🔊 {html.escape(sit)}</i><br>'
            else:
                x += nar(f'{i}番。') + "<break time='600ms'/></voice>"
                x += f"<voice name='{voice[wa]}'>{html.escape(say(trig), quote=False)}<break time='1000ms'/></voice>"
                tr += f'<b>{i}番</b><br>{WHO[wa]}: {html.escape(trig)}<br>'
            for k, o in enumerate(options):
                x += nar(f'{NUMLBL[k]}。') + "<break time='250ms'/></voice>"
                x += f"<voice name='{voice[who]}'>{html.escape(say(o), quote=False)}<break time='{900 if k < 2 else 2500}ms'/></voice>"
                tr += f'{WHO[who]}: {k+1}. {html.escape(o)}<br>'
            tr += '<br>'
            q = {'type': 'mcq', 'prompt': f'{i}. ' + (sit if slot == 'l4' else QP.get(lv, '返事として最もよいものはどれですか。')), 'options': options, 'answer': ans,
                 'shuffle': False, 'aopts': True, 'explain': {'id': f'Jawaban: {ans+1}. {ok} — {eid}', 'en': f'Answer: {ans+1}. {ok} — {een}'}}
            if slot == 'l4':
                q['img'] = f'img/jlpt/{sid}_{i}.svg'
                q['_scene'] = scene_
            qs.append(q)
        x = re.sub(r"<break time='2500ms'/></voice>$", "<break time='3600ms'/></voice>", x)
        out.append(({'id': sid, 'title': TITLE[slot] + ' ' + letter.upper(), 'audio': f'audio/jlpt/v2/{sid}.mp3', 'instructions': INS[lv][slot], 'transcript': tr, 'questions': qs}, x))
    return out

def all_sets():
    r = []
    for lv in ('N5', 'N4', 'N3', 'N2', 'N1'):
        for slot in ('l4', 'l5'):
            r += [(lv, slot, st, x) for st, x in sets_for(lv, slot)]
    return r

def bank():
    d = json.load(open(B, encoding='utf-8'))
    os.makedirs(ROOT + 'img/jlpt', exist_ok=True)
    by = {}
    for lv, slot, st, _ in all_sets():
        for q in st['questions']:
            if 'img' in q: open(ROOT + q['img'], 'w').write(svg(q.pop('_scene')))
        by.setdefault((lv, slot), []).append(st)
    for s in d['sections']:
        lv = s['id'][:2].upper()
        if not s['id'].endswith('l'): continue
        slots = s['slots']
        if lv in ('N5', 'N4'):
            slots = [sl for sl in slots if sl['id'] == 'l']
            slots[0]['title'] = '課題理解・ポイント理解'
        for slot in ('l4', 'l5'):
            if (lv, slot) not in by: continue
            ex = [sl for sl in slots if sl['id'] == slot]
            if ex: ex[0]['sets'] = by[(lv, slot)]; ex[0]['title'] = TITLE[slot]
            else: slots.append({'id': slot, 'title': TITLE[slot], 'count': 1, 'sets': by[(lv, slot)]})
        s['slots'] = slots
        if lv in ('N5', 'N4'):
            s['desc'] = {'id': '課題理解・ポイント理解 (4 soal) + 発話表現 dengan ilustrasi (2) + 即時応答 (2). Pilihan 発話表現 & 即時応答 hanya dibacakan di audio; audio diputar 1 kali.',
                         'en': 'Task & point comprehension (4) + utterance expressions with illustrations (2) + quick response (2). Choices for the last two are audio only; audio plays once.'}
    json.dump(d, open(B, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump([[st['id'] for st in g] for g in groups()], open('/home/claude/w91/LIS_groups.json', 'w'))
    print('ok', {k: len(v) for k, v in by.items()})

def groups():
    gs, cur, size = [], [], 0
    for lv, slot, st, x in all_sets():
        if cur and size + len(x) > 4300: gs.append(cur); cur, size = [], 0
        cur.append(st); st['_x'] = x; size += len(x)
    if cur: gs.append(cur)
    return gs

def ssml():
    for gi, g in enumerate(groups()):
        body = ''.join(st['_x'] for st in g)
        print(f'===== LISG{gi} ({len(body)}): ' + ','.join(st['id'] for st in g))
        print("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='ja-JP'>" + body + '</speak>')

{'bank': bank, 'ssml': ssml}[sys.argv[1]]()
