# T4 Tahap 1 - PTE items with audio (Listening + RS/RL/ASQ/SGD/RTS). Talented-authored. Audio built from grouped SSML + silence split.
import json, re, html, sys
B = '/home/claude/teg-tutorial/mocktest/banks/'
VO = ['en-AU-WilliamNeural', 'en-GB-SoniaNeural', 'en-US-GuyNeural', 'en-AU-NatashaNeural', 'en-GB-RyanNeural', 'en-US-JennyNeural', 'en-CA-LiamNeural', 'en-NZ-MollyNeural', 'en-CA-ClaraNeural', 'en-NZ-MitchellNeural']
AUD = []  # (id, [(voice, text)])
k = 0
def mono(iid, text):
    global k
    AUD.append((iid, [(VO[k % len(VO)], text)])); k += 1
def A(iid): return f'audio/pte/{iid}.mp3'

sst = []
for n, t in ((4, "Today I want to talk about why so many young adults are choosing to rent rather than buy homes. The obvious reason is cost: in most large cities, house prices have grown much faster than wages, so saving for a deposit takes many years. But surveys show that it is not only about money. Renting gives people the flexibility to move for work or study, and many young professionals change jobs several times in their twenties. On the other hand, long-term renters face rising rents and less security, which is why some governments are now introducing longer leases and limits on rent increases."),
             (5, "In this lecture we'll look at the benefits of learning outdoors. Studies of schools that hold regular classes in parks or forests have found that children concentrate better afterwards and report lower levels of stress. Outdoor activities also encourage teamwork, because pupils often have to solve practical problems together, such as building a shelter or measuring a stream. However, teachers point out that outdoor learning requires careful planning, extra supervision and suitable clothing, and it can be difficult in very hot or wet weather. So most researchers recommend combining it with classroom teaching rather than replacing lessons completely.")):
    iid = f'SST{n}'; mono(iid, t)
    sst.append({'id': iid, 'title': 'Summarize spoken text', 'instructions': 'You will hear a short lecture. Write a summary for a fellow student. You have 10 minutes. Your response should be 50-70 words.', 'item_minutes': 10, 'audio': A(iid), 'transcript': t,
                'questions': [{'type': 'essay', 'min_words': 50, 'prompt': 'Write a summary of the lecture in 50-70 words.', 'checklist': ['50-70 words', 'Main idea + 2-3 key points', 'Own words, correct grammar and spelling'], 'model': 'Model: The speaker explains the main topic, gives two or three supporting points heard in the lecture and ends with the overall conclusion, in one or two well-linked sentences.'}]})

def multi_item(pref, n, title, ins, t, q, opts, ans):
    iid = f'{pref}{n}'; mono(iid, t)
    return {'id': iid, 'title': title, 'instructions': ins, 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'multi', 'prompt': q, 'options': opts, 'answer': ans, 'choose': len(ans), 'negative': True, 'explain': 'Listen for each detail; +1 correct, -1 incorrect (minimum 0).'}]}
lm = [multi_item('LM', 4, 'MC multiple answers (listening)', 'Listen to the recording and select all correct responses. Incorrect selections lose marks.',
        "Recent research on sleep and teenagers shows that their body clocks naturally shift later during adolescence. This means many teenagers are not able to fall asleep before eleven at night, even if they go to bed early. When schools start very early, students lose sleep, which affects their mood and their ability to concentrate. Some schools that moved their start time to around half past eight reported better attendance and fewer late arrivals.",
        'What does the speaker say about teenagers and sleep?', ['Their body clocks shift later.', 'They need less sleep than adults.', 'Early school starts can reduce concentration.', 'Later start times improved attendance in some schools.', 'Most schools now start after ten.'], [0, 2, 3]),
      multi_item('LM', 5, 'MC multiple answers (listening)', 'Listen to the recording and select all correct responses. Incorrect selections lose marks.',
        "Food trucks have become a popular part of city life. For new business owners, a truck is much cheaper to start than a restaurant, because there is no need to rent a building. Owners can also move to where customers are, such as festivals or office districts at lunchtime. The main challenges are strict health regulations and finding legal places to park, and many cities limit the number of permits they issue.",
        'Which points are made about food trucks?', ['They are cheaper to start than restaurants.', 'They can move to where customers are.', 'They do not need to follow health rules.', 'Parking can be a challenge.', 'Cities issue unlimited permits.'], [0, 1, 3])]

def lfib_item(n, t, blanks):
    iid = f'LF{n}'; mono(iid, t)
    text = t
    for i, w in enumerate(blanks):
        text = re.sub(r'\b' + re.escape(w) + r'\b', f'[[{i}]]', text, count=1)
    return {'id': iid, 'title': 'Fill in the blanks (listening)', 'instructions': 'You will hear a recording. Type the missing words in each blank.', 'audio': A(iid), 'transcript': t,
            'questions': [{'type': 'cloze', 'text': text, 'blanks': {str(i): {'answer': w} for i, w in enumerate(blanks)}, 'explain': 'Spelling must be correct.'}]}
lf = [lfib_item(5, 'Many students underestimate how much money they need for their first month abroad. Apart from rent and a bond, there are costs for furniture, transport cards and textbooks, so it is wise to keep an emergency fund.', ['underestimate', 'bond', 'textbooks', 'emergency']),
      lfib_item(6, 'Mangrove forests protect coastlines by reducing the force of waves during storms. Their roots also trap sediment and provide a nursery for young fish, which supports local fishing communities.', ['coastlines', 'storms', 'sediment', 'nursery']),
      lfib_item(7, 'The university library now offers extended opening hours during the examination period. Students can reserve group study rooms online, but each booking is limited to two hours per day.', ['extended', 'examination', 'reserve', 'limited']),
      lfib_item(8, 'Effective presentations usually begin with a clear outline. Speakers who maintain eye contact and use simple visuals tend to keep their audience engaged for longer.', ['outline', 'maintain', 'visuals', 'engaged']),
      lfib_item(9, 'Recycling electronic waste is important because old phones and computers contain valuable metals as well as harmful chemicals that can contaminate soil and water.', ['electronic', 'valuable', 'harmful', 'contaminate']),
      lfib_item(10, 'Researchers found that people who walked in green spaces for twenty minutes reported lower anxiety and improved creativity compared with those who walked along busy streets.', ['twenty', 'anxiety', 'creativity', 'busy'])]

def mcq_item(pref, n, title, ins, t, q, opts, ex):
    iid = f'{pref}{n}'; mono(iid, t)
    return {'id': iid, 'title': title, 'instructions': ins, 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'mcq', 'prompt': q, 'options': opts, 'answer': 0, 'explain': ex}]}
hc = [mcq_item('HC', 4, 'Highlight correct summary', 'Listen and select the paragraph that best summarises the recording.',
        "Many people think that multitasking helps them get more done. In fact, studies show that the brain switches rapidly between tasks rather than doing them at the same time. Each switch costs time and increases mistakes, so people who multitask often take longer and make more errors than those who focus on one task.",
        'Which summary is correct?', ['Multitasking involves switching between tasks, which wastes time and causes more errors.', 'The brain can easily perform several tasks at the same moment.', 'Multitasking is the best way to reduce mistakes.', 'People who focus on one task usually take longer.'], 'The speaker says switching costs time and increases mistakes.'),
      mcq_item('HC', 5, 'Highlight correct summary', 'Listen and select the paragraph that best summarises the recording.',
        "Community gardens are spreading in many cities. Apart from producing fresh vegetables, they bring together neighbours who might otherwise never meet, and they give children a chance to learn where food comes from. The main difficulty is finding land, because empty city space is expensive and often reserved for future buildings.",
        'Which summary is correct?', ['Community gardens provide food and social benefits, but suitable land is hard to find.', 'Community gardens mainly exist to make money for cities.', 'Children are not allowed in community gardens.', 'Land for gardens is cheap and easy to obtain.'], 'Benefits + difficulty finding land.')]
ls = [mcq_item('LS', 4, 'MC single answer (listening)', 'Listen and select the correct response.',
        "Before you sign a rental agreement, read it carefully and take photos of the property, especially any damage. These photos can be important at the end of your lease, when the landlord decides how much of your bond to return.",
        'What is the speaker’s main advice?', ['Record the condition of a property before signing a lease.', 'Avoid paying a bond.', 'Always rent from friends.', 'Ask the landlord for a discount.'], 'Photos protect your bond.'),
      mcq_item('LS', 5, 'MC single answer (listening)', 'Listen and select the correct response.',
        "When preparing for an exam, many students simply reread their notes. Research suggests a better strategy is to test yourself, for example by answering practice questions without looking at the answers, because recalling information strengthens memory.",
        'What does the speaker recommend?', ['Testing yourself instead of only rereading notes', 'Studying all night', 'Reading notes many times', 'Avoiding practice questions'], 'Self-testing strengthens memory.')]
sw = [mcq_item('SW', 4, 'Select missing word', 'The last word of the recording is missing. Select the word that completes it.',
        "Plants need sunlight, water and carbon dioxide to make their food. This process takes place mainly in the leaves and is called",
        'Which word completes the recording?', ['photosynthesis', 'evaporation', 'digestion', 'pollution'], 'Topic: how plants make food.'),
      mcq_item('SW', 5, 'Select missing word', 'The last word of the recording is missing. Select the word that completes it.',
        "If you want to save money each month, start by writing down everything you spend. Then decide on a limit for each category. This simple plan is called a",
        'Which word completes the recording?', ['budget', 'salary', 'receipt', 'loan'], 'A spending plan with limits is a budget.')]

def hiw_item(n, orig, changed):
    iid = f'HW{n}'; mono(iid, orig)
    a, b = orig.split(' '), changed.split(' ')
    assert len(a) == len(b), iid
    ans = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    return {'id': iid, 'title': 'Highlight incorrect words', 'instructions': 'The transcript differs from what the speaker says. Click the words that are different.', 'audio': A(iid), 'transcript': orig,
            'questions': [{'type': 'highlight', 'text': changed, 'answer': ans, 'explain': '+1 for each correct word, -1 for each wrong click.'}]}
hw = [hiw_item(5, 'Many universities now offer short online courses that anyone can join for free. These courses are popular with working adults who want to update their skills without leaving their jobs.', 'Many universities now offer short online courses that anyone can join for money. These courses are popular with working adults who want to improve their skills without leaving their jobs.'),
      hiw_item(6, 'The city council has announced plans to build a new bridge across the river. The project will take three years to complete and is expected to reduce traffic in the city centre.', 'The city council has announced plans to build a new tunnel across the river. The project will take five years to complete and is expected to reduce traffic in the city centre.'),
      hiw_item(7, 'Kangaroos are the only large animals that move by hopping. Their strong back legs and long tail help them keep their balance and travel long distances using very little energy.', 'Kangaroos are the only large animals that move by hopping. Their strong front legs and long tail help them keep their balance and travel long distances using very much energy.'),
      hiw_item(8, 'Drinking enough water is important for concentration. Even mild dehydration can make people feel tired and reduce their ability to focus on difficult tasks.', 'Drinking enough water is important for concentration. Even severe dehydration can make people feel tired and reduce their ability to focus on simple tasks.'),
      hiw_item(9, 'The festival attracts thousands of visitors every summer. Local businesses benefit greatly, although some residents complain about noise and crowded streets.', 'The festival attracts hundreds of visitors every summer. Local businesses benefit greatly, although some residents complain about noise and empty streets.'),
      hiw_item(10, 'Scientists have developed a new type of battery that charges in just ten minutes. If it becomes widely available, it could make electric cars far more convenient.', 'Scientists have developed a new type of battery that charges in just two minutes. If it becomes widely available, it could make electric cars far more expensive.')]

wd = []
for n, t in enumerate(['Students must submit their assignments before the due date.', 'The lecture will be recorded and uploaded to the website.', 'Most universities offer support services for international students.', 'Please collect your graduation gown from the student centre.', 'The research project was funded by a government grant.', 'Regular exercise improves both physical and mental health.', 'The seminar has been moved to a larger room on the second floor.'], start=9):
    iid = f'WD{n}'; mono(iid, t)
    wd.append({'id': iid, 'title': 'Write from dictation', 'instructions': 'Type the sentence exactly as you hear it.', 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'dictation', 'prompt': 'Type the sentence:', 'answer': t, 'explain': 'One point per correct word (spelling counts).'}]})

rs = []
for n, t in enumerate(['Please hand in your essay by Friday afternoon.', 'The library is open until ten tonight.', 'Our tutor will explain the assessment criteria.', 'Most students live within walking distance of campus.', 'The bus to the city leaves every fifteen minutes.', 'You can book a meeting with your lecturer online.', 'The final exam counts for half of the grade.', 'Remember to cite every source in your report.', 'The science building is next to the main car park.', 'Group presentations will take place next Wednesday.', 'Laboratory safety glasses must be worn at all times.', 'The orientation session starts at nine o’clock sharp.', 'Scholarships are available for high-achieving students.', 'Please switch off your phones during the lecture.', 'Feedback on your assignment will be emailed to you.', 'The cafeteria offers vegetarian options every day.', 'Student accommodation fills up quickly in summer.', 'This course includes a work placement in the final year.', 'You will need a calculator for tomorrow’s test.', 'Our study group meets every Tuesday in the library.', 'The deadline has been extended by one week.', 'All readings are available on the learning portal.', 'International students can work limited hours during term.', 'The museum is closed on public holidays.', 'Lectures are recorded for students who cannot attend.', 'Please register for the workshop before Monday.', 'The tutorial room has been changed to building five.', 'Many graduates find work within six months.', 'The professor published a new book last year.', 'Make sure your references follow the required style.', 'The campus shuttle runs until midnight on weekdays.', 'Volunteers are needed for the open day.', 'The results will be announced at the end of the month.', 'Each student must complete an online safety module.'], start=17):
    iid = f'RS{n}'; mono(iid, t)
    rs.append({'id': iid, 'title': 'Repeat sentence', 'instructions': 'Listen and repeat the sentence exactly.', 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'speak', 'prompt': 'Repeat the sentence you heard.', 'prep': 0, 'speak': 15, 'checklist': ['Clear pronunciation', 'Smooth, natural pace without long pauses', 'All content covered'], 'model': t}]})

rl = []
for n, t in ((3, "Today I'd like to talk about the history of the umbrella. Umbrellas were first used thousands of years ago in China and Egypt, but mainly to protect people from the sun, not the rain. Waterproof umbrellas became common in Europe only in the eighteenth century. At first, men who carried them in London were laughed at, because umbrellas were seen as a sign that a person could not afford a carriage. Today, of course, they are an everyday item around the world."),
             (4, "Let's look at why some animals hibernate. In winter, food becomes scarce, so animals such as bears and some bats reduce their activity to save energy. During hibernation, their heart rate and body temperature drop dramatically, and they live on fat stored during the autumn. Scientists study hibernation because it might one day help doctors protect patients during long operations, or even help astronauts on long space journeys."),
             (5, "This lecture is about the importance of bees in agriculture. Around one third of the food we eat depends on pollination, and bees are the most important pollinators. In recent decades, bee populations have declined in many countries because of pesticides, disease and the loss of wild flowers. To address this, some farmers now plant strips of flowers beside their fields and reduce chemical use, which helps both bees and crop yields.")):
    iid = f'RL{n}'; mono(iid, t)
    rl.append({'id': iid, 'title': 'Retell lecture', 'instructions': 'Listen to the lecture, then retell it in your own words. You have 10 seconds to prepare and 40 seconds to speak.', 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'speak', 'prompt': 'Retell the lecture.', 'prep': 10, 'speak': 40, 'checklist': ['Topic', 'Key points', 'Conclusion'], 'model': 'Model: The lecture was about ... It explained that ... It also mentioned ... Finally, the speaker concluded that ...'}]})

aq = []
for n, (t, a) in enumerate([('What do we call the person who flies an aeroplane?', 'pilot'), ('What do we call a baby cat?', 'a kitten'), ('What is frozen water called?', 'ice'), ('What do you use to unlock a door?', 'a key'), ('What do you call a book of maps?', 'an atlas'), ('Which season comes after autumn?', 'winter'), ('Which animal is known as the king of the jungle?', 'the lion'), ('What do bees make?', 'honey'), ('How many sides does a triangle have?', 'three'), ('What do we call a doctor who treats teeth?', 'a dentist'), ('Which planet is known as the red planet?', 'Mars'), ('What is the opposite of expensive?', 'cheap'), ('Where do you go to borrow books?', 'a library')], start=13):
    iid = f'AQ{n}'; mono(iid, t)
    aq.append({'id': iid, 'title': 'Answer short question', 'instructions': 'Listen and answer with a single word or a few words.', 'audio': A(iid), 'transcript': t, 'questions': [{'type': 'speak', 'prompt': 'Answer the question.', 'prep': 0, 'speak': 10, 'checklist': ['One word or short phrase'], 'model': a}]})

SGV = ['en-AU-WilliamNeural', 'en-GB-SoniaNeural', 'en-US-GuyNeural']
sg = []
for n, (topic, lines) in enumerate([
  ('Should first-year students live on campus?', ["Speaker A: I think living on campus is the best choice for first-year students. You meet people easily, and you're close to classes and the library.", "Speaker B: That's true, but campus housing is often expensive. Sharing a house off campus can be much cheaper, especially in big cities.", "Speaker C: I agree with both of you in a way. Maybe the ideal is to live on campus for the first semester, then move out once you've made friends and know the area."]),
  ('Is homework useful for primary school children?', ["Speaker A: In my view, a small amount of homework helps children build good study habits early.", "Speaker B: I'm not convinced. Young children need time to play and rest, and research shows homework has little effect on their results at that age.", "Speaker C: Perhaps the answer is reading at home instead of worksheets. It's enjoyable and it really does improve language skills."]),
  ('Should cities ban cars from the centre?', ["Speaker A: Banning cars would make city centres cleaner and safer for pedestrians.", "Speaker B: But many people, like older residents or tradespeople, depend on cars. A complete ban would be unfair to them.", "Speaker C: A compromise could work: limit cars at busy times and improve public transport first, so people have real alternatives."]),
  ('Are online exams as reliable as traditional exams?', ["Speaker A: Online exams are convenient, but I worry that it's easier to cheat at home.", "Speaker B: Modern software can monitor students with cameras, and open-book questions make cheating less useful anyway.", "Speaker C: I think both formats have a place. Practical skills might be better tested in person, while essays can work well online."]),
  ('Should universities make internships compulsory?', ["Speaker A: Yes, compulsory internships give every student real work experience and make them more employable.", "Speaker B: The problem is that many internships are unpaid, so students who need to earn money would be disadvantaged.", "Speaker C: Universities could solve that by partnering with employers to offer paid placements and by giving course credit for them."]),
  ('Is it better to learn a language in the country where it is spoken?', ["Speaker A: Living in the country forces you to use the language every day, so you improve much faster.", "Speaker B: That's true, but it's expensive, and with online tutors and apps you can make good progress at home.", "Speaker C: I'd say start at home to build a foundation, then spend time abroad to develop fluency and confidence."])], start=5):
    iid = f'SG{n}'
    AUD.append((iid, [(SGV[i % 3], re.sub(r'^Speaker [ABC]: ', '', l)) for i, l in enumerate(lines)]))
    sg.append({'id': iid, 'title': 'Summarize group discussion', 'instructions': "You will hear three people discussing a topic. You have 10 seconds to prepare and 2 minutes to summarise the discussion, including each speaker's main points and where they agree or disagree.", 'audio': A(iid),
               'transcript': f'<b>Topic: {html.escape(topic)}</b><br>' + '<br>'.join(html.escape(l) for l in lines),
               'questions': [{'type': 'speak', 'prompt': 'Summarise the discussion.', 'prep': 10, 'speak': 120, 'kind': 'sgd', 'checklist': ['Topic of the discussion', 'Main point of each speaker', 'Agreement / disagreement', 'Clear conclusion'], 'model': 'Model: The speakers discussed ... Speaker A argued ..., while Speaker B ... . Speaker C suggested ... . In the end, they agreed that ...'}]})

rt = []
for n, t in enumerate(["Your flatmate, Alex, often plays loud music late at night, and you have an important exam next week. Speak to Alex, explain the problem politely and suggest a solution.",
                       "You missed a group meeting for your project because you were sick. Speak to your group leader, Mia, apologise, explain what happened and ask how you can catch up.",
                       "You bought a jacket online, but it arrived in the wrong size. Call the shop, explain the problem and ask for an exchange.",
                       "Your lecturer, Dr Kim, has given you a lower mark than you expected on an assignment. Speak to Dr Kim, ask politely for feedback and how you could improve.",
                       "A new international student, Ravi, has just moved into your building and looks lost. Speak to Ravi, welcome him and offer some useful information about the area.",
                       "You need to leave your part-time job early on Friday to attend a family event. Speak to your manager, Lisa, explain the situation and suggest how your shift could be covered."], start=5):
    iid = f'RT{n}'; mono(iid, t)
    rt.append({'id': iid, 'title': 'Respond to a situation', 'instructions': 'Listen to the situation. You have 20 seconds to prepare and 40 seconds to respond as if you are speaking to the person.', 'audio': A(iid), 'transcript': t,
               'questions': [{'type': 'speak', 'prompt': 'Respond to the situation.', 'prep': 20, 'speak': 40, 'kind': 'rts', 'checklist': ['Speak directly to the person (first person)', 'Cover every point in the situation', 'Polite, suitable tone'], 'model': 'Model: Hi ..., I’m really sorry / I wanted to ask ... (cover each point, suggest a solution, polite closing).'}]})

ADD = {'sst': sst, 'lmcm': lm, 'lfib': lf, 'hcs': hc, 'lmcs': ls, 'smw': sw, 'hiw': hw, 'wfd': wd, 'rs': rs, 'rl': rl, 'asq': aq, 'sgd': sg, 'rts': rt}
GAP = 3000
def groups(maxchars=4200):
    out, cur, size = [], [], 0
    for iid, parts in AUD:
        x = ''.join(f"<voice name='{v}'>{html.escape(t, quote=False)}<break time='600ms'/></voice>" for v, t in parts) + f"<voice name='en-AU-WilliamNeural'><break time='{GAP}ms'/></voice>"
        if cur and size + len(x) > maxchars:
            out.append(cur); cur, size = [], 0
        cur.append((iid, x)); size += len(x)
    if cur: out.append(cur)
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'bank':
        d = json.load(open(B + 'pte.json', encoding='utf-8'))
        for s in d['sections']:
            for sl in s['slots']:
                if sl['id'] in ADD:
                    pool = sl.get('sets') if 'sets' in sl else sl['items']; have = {x['id'] for x in pool}
                    pool += [x for x in ADD[sl['id']] if x['id'] not in have]
        json.dump(d, open(B + 'pte.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('bank ok', len(AUD))
    elif cmd == 'ssml':
        G = groups()
        json.dump([[i for i, _ in g] for g in G], open('/home/claude/w91/t4_pte_groups.json', 'w'))
        for gi, g in enumerate(G):
            print(f'===== G{gi} ({len(g)}): ' + ','.join(i for i, _ in g))
            print("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-AU'>" + ''.join(x for _, x in g) + '</speak>')
