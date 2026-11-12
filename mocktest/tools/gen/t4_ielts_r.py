# T4 Tahap 1 - IELTS Academic Reading: +3 passages per part (c-e) -> 5 per part. Talented-authored texts.
import json
B = '/home/claude/teg-tutorial/mocktest/banks/'
GT = 'Do the following statements agree with the information in the passage? Choose <b>TRUE</b>, <b>FALSE</b> or <b>NOT GIVEN</b>.'
GY = 'Do the following statements agree with the views of the writer? Choose <b>YES</b>, <b>NO</b> or <b>NOT GIVEN</b>.'
G2 = 'Complete the sentences. Write <b>NO MORE THAN TWO WORDS</b> from the passage.'
GM = 'Choose the correct letter, <b>A, B, C or D</b>.'
def TF(p, a, ex): return {'type': 'tfng', 'group': GT, 'prompt': p, 'answer': a, 'explain': ex}
def YN(p, a, ex): return {'type': 'tfng', 'group': GY, 'prompt': p, 'options': ['YES', 'NO', 'NOT GIVEN'], 'answer': a, 'explain': ex}
def GP(p, a, ex): return {'type': 'gap', 'group': G2, 'prompt': p, 'answer': a if isinstance(a, list) else [a], 'explain': ex}
def MC(p, opts, ex): return {'type': 'mcq', 'group': GM, 'prompt': p, 'options': opts, 'answer': 0, 'explain': ex}
def HD(heads, n0):
    g = f'Questions {n0}-{n0+5}: The passage has six paragraphs, <b>A-F</b>. Choose the correct heading for each paragraph from the list (i-viii).'
    return g, [{'v': v, 't': t} for v, t in heads]
def MT(g, opts, para, ans, ex): return {'type': 'match', 'group': g, 'options': opts, 'prompt': f'Paragraph {para}', 'answer': ans, 'explain': ex}
def P(paras): return ''.join(f'<p>{x}</p>' for x in paras)
def PL(paras): return ''.join(f'<p><b>{chr(65+i)}</b> {x}</p>' for i, x in enumerate(paras))

r1 = [
 {'id': 'R1c', 'title': 'Passage 1 · The return of the night train', 'passage': '<h3>The return of the night train</h3>' + P([
  'For much of the twentieth century, overnight trains were a normal way to travel across Europe. Passengers boarded in the evening, slept in a bunk and woke up in another country. From the 1990s, however, cheap flights and faster daytime trains made these services less popular, and many operators closed their sleeper routes because they were losing money.',
  'In the last decade the trend has started to reverse. In 2016 the Austrian national railway took over several routes that German railways had abandoned and rebranded them under a single name. Within a few years, the company reported that most of its night services were full in summer, and it ordered new carriages with private compartments and small showers.',
  'Several factors explain the revival. The most widely reported is concern about the climate impact of flying: a journey by electric train produces only a fraction of the carbon emissions of the same trip by plane. Night trains also save travellers the cost of a hotel, and they arrive in city centres rather than at airports far from town. Surveys suggest that younger travellers are particularly attracted by the idea of a slower, more memorable journey.',
  'Running night trains is still difficult. Sleeping carriages carry far fewer passengers than seated ones, so ticket prices must be relatively high. Trains often pass through several countries, each with its own rules, fees and electrical systems, which adds cost and complexity. In addition, routes must be planned so that trains do not arrive too early in the morning, which limits the distances that can be covered.',
  'Governments have begun to help. Some have reduced track access charges for overnight services, and the European Union has supported pilot routes. Even so, many experts believe that night trains will remain a small part of the travel market, suitable mainly for journeys of between 800 and 1,500 kilometres, where they compete most effectively with flying.']),
  'questions': [
   TF('Many sleeper routes closed because they were not profitable.', 'TRUE', 'Para 1: operators closed routes "because they were losing money".'),
   TF('The Austrian railway created its night services entirely from new routes.', 'FALSE', 'Para 2: it took over routes that German railways had abandoned.'),
   TF('The new Austrian carriages include private compartments.', 'TRUE', 'Para 2: "new carriages with private compartments and small showers".'),
   TF('Night trains are always cheaper than flying.', 'NOT GIVEN', 'The passage says they save hotel costs but never compares total ticket prices with flights in all cases.'),
   TF('Younger travellers appear especially interested in night trains.', 'TRUE', 'Para 3: surveys suggest younger travellers are particularly attracted.'),
   TF('Sleeping carriages carry more passengers than seated carriages.', 'FALSE', 'Para 4: they carry "far fewer passengers".'),
   TF('All EU countries now charge no fees for night trains.', 'NOT GIVEN', 'Only "some" governments reduced charges; no information about all countries charging nothing.'),
   GP('From the 1990s, cheap ___ reduced demand for sleeper services.', 'flights', 'Para 1: "cheap flights and faster daytime trains".'),
   GP('Night trains arrive in city ___ instead of distant airports.', ['centres', 'centers'], 'Para 3: "arrive in city centres".'),
   GP('Different countries have different rules, fees and ___ systems.', 'electrical', 'Para 4: "rules, fees and electrical systems".'),
   GP('Trains must not arrive too ___ in the morning.', 'early', 'Para 4: "do not arrive too early in the morning".'),
   GP('Some governments have reduced track ___ charges.', 'access', 'Para 5: "reduced track access charges".'),
   GP('The EU has supported ___ routes.', 'pilot', 'Para 5: "supported pilot routes".'),
  ]},
 {'id': 'R1d', 'title': 'Passage 1 · Seaweed on the menu', 'passage': '<h3>Seaweed on the menu</h3>' + P([
  'Seaweed has been eaten for centuries in East Asia, where it appears in soups, salads and the wrapping of sushi. In recent years it has attracted interest far beyond this region, not only as food but also as a possible solution to several environmental problems.',
  'Unlike most crops, seaweed needs no fresh water, no fertiliser and no land. It grows quickly in the sea, taking nutrients directly from the water around it. Some species can grow by up to half a metre in a single day under ideal conditions. Because it absorbs nitrogen and phosphorus, seaweed farming can help to clean coastal waters that have been polluted by run-off from agriculture.',
  'Seaweed also absorbs carbon dioxide as it grows. This has led some companies to propose growing very large amounts of it and sinking it to the deep ocean, where the carbon would stay for hundreds of years. Scientists warn, however, that the real benefit is uncertain, because it is difficult to measure how much carbon would remain locked away and what effects large-scale sinking would have on ocean life.',
  'As food, seaweed is rich in minerals such as iodine and calcium, and it contains protein and fibre. However, some types contain so much iodine that eating large quantities could be harmful, so health authorities in several countries recommend moderate consumption. Taste is another barrier: many consumers in Europe and North America find the flavour unfamiliar.',
  'Today, more than 95 per cent of the world’s farmed seaweed is produced in Asia, with China and Indonesia the largest producers. Farms in Norway, Scotland and the United States are expanding, but they remain small. Experts say that new products, such as seaweed snacks and plant-based burgers containing seaweed, could help the industry grow outside Asia.']),
  'questions': [
   TF('Seaweed has a long history as food in East Asia.', 'TRUE', 'Para 1: "eaten for centuries in East Asia".'),
   TF('Seaweed farming requires regular use of fertiliser.', 'FALSE', 'Para 2: seaweed needs "no fertiliser".'),
   TF('Every species of seaweed grows half a metre per day.', 'FALSE', 'Para 2: only "some species" can grow up to half a metre in ideal conditions.'),
   TF('Seaweed farms can reduce some forms of coastal pollution.', 'TRUE', 'Para 2: absorbing nitrogen and phosphorus helps clean polluted waters.'),
   TF('Scientists agree that sinking seaweed is the best way to store carbon.', 'FALSE', 'Para 3: scientists warn the benefit is uncertain.'),
   TF('Seaweed is more popular in Europe than in North America.', 'NOT GIVEN', 'Both regions are mentioned together; no comparison is made.'),
   TF('Indonesia is one of the largest seaweed producers.', 'TRUE', 'Para 5: "China and Indonesia the largest producers".'),
   GP('Seaweed takes ___ directly from the surrounding water.', 'nutrients', 'Para 2: "taking nutrients directly from the water".'),
   GP('Some companies want to sink seaweed to the deep ___.', 'ocean', 'Para 3: "sinking it to the deep ocean".'),
   GP('Some seaweed contains a very high level of ___.', 'iodine', 'Para 4: "so much iodine".'),
   GP('Health authorities recommend ___ consumption.', 'moderate', 'Para 4: "recommend moderate consumption".'),
   GP('Many Western consumers find the ___ unfamiliar.', 'flavour', 'Para 4: "find the flavour unfamiliar".'),
   GP('New products such as seaweed ___ could help the industry grow.', 'snacks', 'Para 5: "seaweed snacks and plant-based burgers".'),
  ]},
 {'id': 'R1e', 'title': 'Passage 1 · Learning from termites', 'passage': '<h3>Learning from termites</h3>' + P([
  'In parts of Africa and Australia, termites build mounds that can rise more than five metres above the ground. Although the insects themselves are tiny and almost blind, their colonies construct structures that stay at a fairly stable temperature and humidity, even when the air outside changes greatly between day and night.',
  'For many years scientists believed that the mounds worked like chimneys: warm air was thought to rise through a central shaft and escape at the top, pulling cooler air in at the bottom. More recent research, using sensors placed inside mounds, has shown that the process is more complex. The daily cycle of heating and cooling of the mound walls causes air to move in different directions at different times of day, slowly exchanging gases between the nest and the outside.',
  'Architects have been inspired by these findings. The best-known example is a large office and shopping building in Harare, Zimbabwe, completed in the 1990s. Instead of conventional air conditioning, it uses fans, chimneys and thick concrete walls that store heat during the day and release it at night. According to its designer, the building uses about ten per cent of the energy of a similar building with full air conditioning.',
  'Not everyone agrees that the building truly copies termites. Some biologists point out that it was designed according to the older chimney theory, which is now known to be incomplete. Nevertheless, they accept that the project helped to make the idea of "biomimicry" - learning from nature in design - popular among engineers.',
  'Researchers are now studying whether the porous walls of termite mounds could inspire new building materials that "breathe", allowing air and moisture to pass through slowly. Such materials might reduce the need for mechanical ventilation in hot climates, although none has yet been used in a large building.']),
  'questions': [
   TF('Some termite mounds are over five metres tall.', 'TRUE', 'Para 1: mounds "can rise more than five metres".'),
   TF('Termites have excellent eyesight.', 'FALSE', 'Para 1: the insects are "almost blind".'),
   TF('Conditions inside mounds stay relatively stable.', 'TRUE', 'Para 1: "fairly stable temperature and humidity".'),
   TF('Modern sensors confirmed the simple chimney theory.', 'FALSE', 'Para 2: research showed the process is "more complex".'),
   TF('The Harare building was the first building in Africa without air conditioning.', 'NOT GIVEN', 'The passage does not say it was the first.'),
   TF('Some biologists question whether the Harare building really copies termites.', 'TRUE', 'Para 4: "Not everyone agrees that the building truly copies termites."'),
   TF('Breathing building materials are already common in large buildings.', 'FALSE', 'Para 5: none has yet been used in a large building.'),
   GP('Air movement is caused by the daily heating and cooling of the mound ___.', 'walls', 'Para 2: "heating and cooling of the mound walls".'),
   GP('The Harare building has thick ___ walls that store heat.', 'concrete', 'Para 3: "thick concrete walls".'),
   GP('The building uses about ___ per cent of the energy of a similar building.', ['ten', '10'], 'Para 3: "about ten per cent".'),
   GP('Learning from nature in design is called ___.', 'biomimicry', 'Para 4: "biomimicry".'),
   GP('Researchers are studying the ___ walls of termite mounds.', 'porous', 'Para 5: "the porous walls".'),
   GP('New materials might reduce the need for mechanical ___.', 'ventilation', 'Para 5: "mechanical ventilation".'),
  ]},
]

h_c = [('i', 'A practice with ancient roots'), ('ii', 'Measuring the benefits'), ('iii', 'Opposition from local residents'), ('iv', 'How the system works'), ('v', 'Spreading to new cities'), ('vi', 'Unexpected costs'), ('vii', 'A response to rising temperatures'), ('viii', 'Choosing the right plants')]
g_c, o_c = HD(h_c, 14)
h_d = [('i', 'Early attempts that failed'), ('ii', 'Why the problem matters'), ('iii', 'A simple tool with big results'), ('iv', 'Training local workers'), ('v', 'Funding the project'), ('vi', 'Lessons for other countries'), ('vii', 'The role of mobile phones'), ('viii', 'Remaining challenges')]
g_d, o_d = HD(h_d, 14)
h_e = [('i', 'A surprising discovery in a laboratory'), ('ii', 'From laboratory to market'), ('iii', 'Different explanations'), ('iv', 'A common everyday habit'), ('v', 'Advice for students'), ('vi', 'Effects on mood'), ('vii', 'How long the effect lasts'), ('viii', 'Risks of too much')]
g_e, o_e = HD(h_e, 14)
r2 = [
 {'id': 'R2c', 'title': 'Passage 2 · Green roofs', 'passage': '<h3>Green roofs</h3>' + PL([
  'Covering roofs with soil and plants is not a new idea. Houses with grass roofs were built in Scandinavia more than a thousand years ago, where the thick layer of turf helped to keep heat inside during long winters.',
  'Modern green roofs are designed for a different purpose. As cities grow hotter, partly because concrete and asphalt absorb the sun’s heat, planners are looking for ways to cool buildings and streets. A planted roof can be up to 30 degrees cooler than a dark roof on a summer afternoon.',
  'A typical modern green roof has several layers: a waterproof membrane to protect the building, a drainage layer, a lightweight growing medium and, finally, the plants themselves. The drainage layer stores some rainwater for the plants and allows the rest to flow slowly away.',
  'Not all plants are suitable. Roofs are windy and dry, and the soil is usually shallow, so designers often use hardy succulents that store water in their leaves. Larger roofs with deeper soil can support grasses, small shrubs and even vegetables.',
  'Researchers have tried to calculate the advantages. Studies in several cities have found that green roofs reduce the energy needed for air conditioning in the floors directly below, slow the flow of stormwater into drains and provide habitats for insects and birds. The size of these benefits varies greatly depending on climate and design.',
  'Following early projects in Germany, cities such as Toronto, Copenhagen and Singapore now require or encourage green roofs on certain new buildings. Some offer tax reductions or grants to building owners who install them.']),
  'questions': [MT(g_c, o_c, 'A', 'i', 'Grass roofs in Scandinavia over a thousand years ago.'), MT(g_c, o_c, 'B', 'vii', 'Cities growing hotter; roofs to cool buildings.'), MT(g_c, o_c, 'C', 'iv', 'Describes the layers and how drainage works.'), MT(g_c, o_c, 'D', 'viii', 'Which plants are suitable.'), MT(g_c, o_c, 'E', 'ii', 'Researchers calculate the advantages.'), MT(g_c, o_c, 'F', 'v', 'Toronto, Copenhagen, Singapore adopting green roofs.'),
   MC('Why were grass roofs used in Scandinavia?', ['To keep heat inside in winter', 'To cool houses in summer', 'To grow food', 'To collect rainwater'], 'Paragraph A: turf helped keep heat inside.'),
   MC('What is the purpose of the drainage layer?', ['It stores some water and lets the rest flow away', 'It protects the building from fire', 'It provides nutrients', 'It keeps out insects'], 'Paragraph C.'),
   MC('Why are succulents often chosen?', ['They store water in their leaves', 'They grow very tall', 'They need deep soil', 'They attract birds'], 'Paragraph D.'),
   GP('A planted roof can be up to ___ degrees cooler than a dark roof.', ['30', 'thirty'], 'Paragraph B.'),
   GP('The bottom layer is a waterproof ___.', 'membrane', 'Paragraph C.'),
   GP('Green roofs slow the flow of ___ into drains.', 'stormwater', 'Paragraph E.'),
   GP('Some cities give tax reductions or ___ to owners.', 'grants', 'Paragraph F.'),
  ]},
 {'id': 'R2d', 'title': 'Passage 2 · Clean water for rural schools', 'passage': '<h3>Clean water for rural schools</h3>' + PL([
  'In many rural areas of the world, schools have no safe drinking water. Children who drink untreated water often suffer from stomach illnesses, which cause them to miss classes. Studies have linked poor water and sanitation to lower attendance, especially among girls.',
  'Previous efforts to solve the problem were not always successful. Some projects built expensive filtration systems that broke down after a few months because no one had been trained to repair them, and spare parts were not available locally.',
  'One organisation took a different approach. Instead of large machines, it gave schools simple ceramic filters, which remove most bacteria as water passes slowly through them. Each filter costs only a few dollars and can supply enough drinking water for a classroom for two years.',
  'The organisation also trained teachers and older pupils to clean the filters and to recognise when they needed replacing. Local potters were taught to produce the filters themselves, creating jobs and making replacements easy to obtain.',
  'Teachers now send a short text message each month reporting whether the filters are working. This allows the organisation to identify problems quickly and to send help only where it is needed, keeping costs low.',
  'However, filters alone cannot solve every problem. They do not remove chemical pollution, and they depend on schools having a regular supply of water to filter. In dry seasons, some schools still have to rely on water carried from distant rivers.']),
  'questions': [MT(g_d, o_d, 'A', 'ii', 'Explains why lack of safe water matters for attendance.'), MT(g_d, o_d, 'B', 'i', 'Earlier projects broke down.'), MT(g_d, o_d, 'C', 'iii', 'Cheap ceramic filters with big impact.'), MT(g_d, o_d, 'D', 'iv', 'Training teachers, pupils and potters.'), MT(g_d, o_d, 'E', 'vii', 'Monthly text messages.'), MT(g_d, o_d, 'F', 'viii', 'Problems filters cannot solve.'),
   MC('Why did some earlier systems fail?', ['No one could repair them', 'They were too small', 'Schools did not want them', 'They removed too much water'], 'Paragraph B.'),
   MC('What do the ceramic filters remove?', ['Most bacteria', 'Chemical pollution', 'All minerals', 'Salt'], 'Paragraph C; chemicals are not removed (F).'),
   MC('How do teachers report on the filters?', ['By text message', 'By email', 'By letter', 'At an annual meeting'], 'Paragraph E.'),
   GP('Poor water has been linked to lower ___, especially among girls.', 'attendance', 'Paragraph A.'),
   GP('One filter can serve a classroom for ___ years.', ['two', '2'], 'Paragraph C.'),
   GP('Local ___ were taught to make the filters.', 'potters', 'Paragraph D.'),
   GP('In dry seasons, some schools carry water from distant ___.', 'rivers', 'Paragraph F.'),
  ]},
 {'id': 'R2e', 'title': 'Passage 2 · The science of the afternoon nap', 'passage': '<h3>The science of the afternoon nap</h3>' + PL([
  'In a 1990s study, researchers testing pilots on long flights noticed something unexpected: pilots who were allowed a short planned rest in the cockpit made fewer mistakes later in the flight than those who stayed awake.',
  'Napping in the early afternoon is common in many cultures. In parts of southern Europe and Latin America, the traditional midday rest is linked to the hottest time of the day, but people everywhere tend to feel sleepy after lunch, even when they have not eaten a large meal.',
  'Scientists offer several explanations for this afternoon dip. One is that the body’s internal clock naturally produces a small drop in alertness about seven or eight hours after waking. Another is that the pressure to sleep builds up gradually during the day.',
  'A short nap of 10 to 20 minutes appears to improve alertness for up to three hours. Longer naps can lead to "sleep inertia", a feeling of grogginess that may last half an hour after waking, because the sleeper has entered a deeper stage of sleep.',
  'Some studies have found that people report feeling calmer and less irritable after a nap. However, these results depend on self-reports, which may be influenced by what participants expect to feel.',
  'Experts warn that frequent long naps can make it harder to fall asleep at night. They advise those who have trouble sleeping at night to avoid napping after mid-afternoon.']),
  'questions': [MT(g_e, o_e, 'A', 'i', 'An unexpected finding in a pilot study.'), MT(g_e, o_e, 'B', 'iv', 'Napping is common across cultures.'), MT(g_e, o_e, 'C', 'iii', 'Several explanations for the afternoon dip.'), MT(g_e, o_e, 'D', 'vii', 'How long alertness improves; inertia.'), MT(g_e, o_e, 'E', 'vi', 'Feeling calmer and less irritable.'), MT(g_e, o_e, 'F', 'viii', 'Frequent long naps disturb night sleep.'),
   MC('What did the pilot study find?', ['Pilots who rested made fewer mistakes', 'Pilots preferred to stay awake', 'Rest made pilots slower', 'Long flights caused no tiredness'], 'Paragraph A.'),
   MC('According to the passage, people feel sleepy after lunch', ['even after a small meal', 'only after a large meal', 'only in hot countries', 'only if they slept badly'], 'Paragraph B.'),
   MC('Why might the results in paragraph E be unreliable?', ['They are based on what people say they feel', 'The groups were too small', 'They used only pilots', 'They were not published'], 'Paragraph E: self-reports.'),
   GP('Alertness drops about seven or eight hours after ___.', 'waking', 'Paragraph C.'),
   GP('A short nap improves alertness for up to ___ hours.', ['three', '3'], 'Paragraph D.'),
   GP('Grogginess after a long nap is called sleep ___.', 'inertia', 'Paragraph D.'),
   GP('Poor sleepers should avoid napping after ___.', 'mid-afternoon', 'Paragraph F.'),
  ]},
]

r3 = [
 {'id': 'R3c', 'title': 'Passage 3 · Should cities ban cars from their centres?', 'passage': '<h3>Should cities ban cars from their centres?</h3>' + P([
  'Over the past twenty years, a growing number of cities have closed parts of their centres to private cars. Oslo removed most on-street parking from its central area; Madrid restricted access for vehicles that do not meet emission standards; and many smaller towns have turned their main streets into pedestrian zones. Supporters argue that the results speak for themselves: cleaner air, fewer accidents and busier shops.',
  'It is certainly true that air quality usually improves when traffic falls. Yet I believe the claim that businesses always benefit deserves more careful examination. Studies of pedestrian zones show mixed results. Cafés and clothes shops often do well, because people walking slowly are more likely to stop and browse. Businesses that sell heavy or bulky goods, such as furniture or hardware, may lose customers who cannot carry their purchases to a distant car park.',
  'Equally important is the question of who is affected. Car-free centres are easiest to accept for people who live close by or have good public transport. For residents of outer suburbs, where buses may run only once an hour, losing the option of driving into the centre can mean losing access to jobs and services. In my view, any city that restricts cars without first improving public transport is simply moving the problem elsewhere.',
  'There is also a risk that bans are introduced too quickly. Several cities have seen strong public protests when restrictions appeared without warning or consultation. By contrast, places that introduced changes gradually - starting with trial days, then weekends, then permanent closures - have generally found that opposition fades once residents experience the benefits.',
  'None of this means that reducing car traffic is a mistake. The evidence that it saves lives and improves health is strong. But the most successful schemes are those that treat the car ban as one part of a wider plan, including better buses, safe cycle routes and delivery arrangements for businesses. A ban on its own is not a transport policy.']),
  'questions': [
   YN('Air quality generally gets better when there is less traffic.', 'YES', 'Para 2: "It is certainly true that air quality usually improves".'),
   YN('All businesses benefit from pedestrian zones.', 'NO', 'Para 2: the writer questions this; some businesses lose customers.'),
   YN('Restricting cars without better public transport is unfair to suburban residents.', 'YES', 'Para 3: "simply moving the problem elsewhere".'),
   YN('Madrid’s scheme has been more successful than Oslo’s.', 'NOT GIVEN', 'The writer does not compare the two schemes.'),
   YN('Reducing car traffic is a mistake.', 'NO', 'Para 5: "None of this means that reducing car traffic is a mistake."'),
   MC('Which businesses may lose customers in pedestrian zones?', ['Shops selling heavy or bulky goods', 'Cafés', 'Clothes shops', 'Bookshops'], 'Para 2: furniture or hardware.'),
   MC('Why do cafés often do well in pedestrian zones?', ['People walk slowly and stop to browse', 'Rent is cheaper', 'They receive government support', 'They open later'], 'Para 2.'),
   MC('According to the writer, opposition to car bans usually fades when', ['changes are introduced gradually', 'fines are increased', 'parking becomes free', 'shops close early'], 'Para 4.'),
   MC('What is the writer’s main argument?', ['Car bans work best as part of a wider transport plan', 'Car bans should be cancelled', 'Only large cities should ban cars', 'Businesses should decide on bans'], 'Para 5: "A ban on its own is not a transport policy."'),
   MC('What does the writer say about residents of outer suburbs?', ['They may lose access to jobs and services', 'They prefer car-free centres', 'They have better buses', 'They rarely visit the centre'], 'Para 3.'),
   GP('Oslo removed most on-street ___ from its centre.', 'parking', 'Para 1.'),
   GP('In outer suburbs, buses may run only once an ___.', 'hour', 'Para 3.'),
   GP('Successful cities started with trial ___.', 'days', 'Para 4.'),
   GP('Wider plans include delivery arrangements for ___.', 'businesses', 'Para 5.'),
  ]},
 {'id': 'R3d', 'title': 'Passage 3 · The value of boredom', 'passage': '<h3>The value of boredom</h3>' + P([
  'Few people enjoy being bored. Faced with a queue, a delayed train or a dull meeting, most of us now reach immediately for a phone. Some psychologists argue that this habit may be costing us something valuable, because boredom, uncomfortable as it is, may encourage creative thinking.',
  'In one frequently cited experiment, participants who first completed a deliberately tedious task - copying numbers from a telephone directory - later produced more ideas when asked to think of uses for a pair of plastic cups than participants who had not been bored. The researchers suggested that boredom pushes the mind to wander, and that mind-wandering helps people make unusual connections.',
  'I find this explanation attractive, but the evidence is not as strong as popular articles often suggest. Several later studies have failed to repeat the original result, and many experiments use small groups of university students, who may not represent the wider population. It is also unclear whether a short burst of boredom in a laboratory resembles the long periods of boredom people experience in real life.',
  'Moreover, boredom is not harmless for everyone. Research on prisoners, patients in hospital and workers in repetitive jobs links chronic boredom with stress, poor health and risky behaviour. To celebrate boredom as a source of creativity without recognising this darker side would, in my view, be irresponsible.',
  'Perhaps the most useful lesson is a modest one. Occasional short periods without entertainment - a walk without headphones, a few minutes looking out of a window - may give the mind space to wander. Whether this makes us more creative remains an open question, but it is unlikely to do us harm.']),
  'questions': [
   YN('Most people today try to avoid boredom by using their phones.', 'YES', 'Para 1: "most of us now reach immediately for a phone".'),
   YN('The evidence that boredom increases creativity is very strong.', 'NO', 'Para 3: "the evidence is not as strong as popular articles often suggest".'),
   YN('University students are always good representatives of the general population.', 'NO', 'Para 3: they "may not represent the wider population".'),
   YN('Chronic boredom can be harmful.', 'YES', 'Para 4: linked with stress, poor health and risky behaviour.'),
   YN('Workers in repetitive jobs are more creative than other workers.', 'NOT GIVEN', 'Not discussed.'),
   MC('In the experiment, bored participants', ['produced more ideas for using plastic cups', 'copied numbers faster', 'refused to complete the task', 'remembered more numbers'], 'Para 2.'),
   MC('The researchers believed boredom helps creativity because it', ['makes the mind wander', 'reduces stress', 'improves memory', 'increases motivation to work'], 'Para 2.'),
   MC('What problem does the writer mention about later studies?', ['They could not repeat the original result', 'They were too expensive', 'They used only prisoners', 'They lasted too long'], 'Para 3.'),
   MC('The writer thinks celebrating boredom without mentioning its risks would be', ['irresponsible', 'creative', 'scientific', 'necessary'], 'Para 4.'),
   MC('What does the writer recommend in the final paragraph?', ['Occasional short periods without entertainment', 'Long periods of boredom every day', 'Avoiding all phones', 'More laboratory studies of students'], 'Para 5.'),
   GP('Participants copied numbers from a telephone ___.', 'directory', 'Para 2.'),
   GP('Boredom may help people make unusual ___.', 'connections', 'Para 2.'),
   GP('Research on prisoners links chronic boredom with ___.', ['stress', 'poor health', 'risky behaviour'], 'Para 4.'),
   GP('One suggestion is a walk without ___.', 'headphones', 'Para 5.'),
  ]},
 {'id': 'R3e', 'title': 'Passage 3 · Rewilding', 'passage': '<h3>Rewilding</h3>' + P([
  '"Rewilding" is a term used for conservation projects that aim to restore natural processes rather than manage land in detail. Instead of planting trees in neat rows or removing every unwanted species, rewilding projects may reintroduce large animals, remove fences and allow rivers to flood naturally, then let nature take its course.',
  'Supporters point to striking examples. When wolves were returned to a large national park in North America in the 1990s, they reduced the number of deer and changed their behaviour, allowing young trees to grow along rivers. In parts of Europe, beavers reintroduced after centuries of absence have built dams that slow floods and create wetlands for birds and insects.',
  'I support many of these projects, but I am uneasy about how they are sometimes presented. The wolf story, for example, is often told as a simple chain of cause and effect, when scientists still disagree about how much of the change was due to wolves and how much to other factors, such as drought and hunting by humans.',
  'There are also practical conflicts. Farmers living near rewilding areas may lose livestock to predators or crops to wild animals, and compensation schemes do not always cover their losses. If local people feel that decisions are imposed by distant organisations, projects are likely to face resistance. In my opinion, rewilding succeeds only when local communities share in the benefits, for example through tourism.',
  'Finally, rewilding is not suitable everywhere. In small or crowded countries, there may simply not be enough space for large animals to roam. In such places, smaller projects - restoring a meadow, reconnecting a river to its floodplain - may achieve more than ambitious plans to reintroduce bears or lynx.']),
  'questions': [
   YN('Rewilding focuses on restoring natural processes.', 'YES', 'Para 1.'),
   YN('The effect of wolves in the national park is fully understood by scientists.', 'NO', 'Para 3: scientists still disagree.'),
   YN('Compensation schemes always cover farmers’ losses.', 'NO', 'Para 4: they "do not always cover their losses".'),
   YN('Rewilding works best when local people benefit from it.', 'YES', 'Para 4.'),
   YN('Bears should be reintroduced to every European country.', 'NO', 'Para 5: not suitable in small or crowded countries.'),
   MC('What did the wolves do in the national park?', ['They reduced deer numbers and changed their behaviour', 'They planted young trees', 'They increased flooding', 'They attracted more deer'], 'Para 2.'),
   MC('How have beavers helped in Europe?', ['Their dams slow floods and create wetlands', 'They reduce the number of birds', 'They eat crops', 'They remove fences'], 'Para 2.'),
   MC('Why is the writer uneasy about the wolf story?', ['It is often told too simply', 'It is completely false', 'It happened in Europe', 'It ignored beavers'], 'Para 3.'),
   MC('Which factor is mentioned as an alternative explanation for changes in the park?', ['Drought', 'Tourism', 'Beavers', 'Farming'], 'Para 3: drought and hunting by humans.'),
   MC('What does the writer suggest for small or crowded countries?', ['Smaller restoration projects', 'Reintroducing lynx', 'Building more fences', 'Stopping all conservation'], 'Para 5.'),
   GP('Rewilding projects may allow rivers to ___ naturally.', 'flood', 'Para 1.'),
   GP('Wolves were returned to the park in the ___.', ['1990s', 'nineteen nineties'], 'Para 2.'),
   GP('Local communities can benefit through ___.', 'tourism', 'Para 4.'),
   GP('One small project is reconnecting a river to its ___.', 'floodplain', 'Para 5.'),
  ]},
]

if __name__ == '__main__':
    d = json.load(open(B + 'ielts.json', encoding='utf-8'))
    for slot, sets in (('P1', r1), ('P2', r2), ('P3', r3)):
        sl = [x for x in d['sections'][1]['slots'] if x['id'] == slot][0]; have = {x['id'] for x in sl['sets']}
        sl['sets'] += [x for x in sets if x['id'] not in have]
    json.dump(d, open(B + 'ielts.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('ok')
