# T4 Tahap 1 - IELTS Listening: +3 sets per part (c-e) -> 5 per part. Talented-authored scripts.
import json, html, re
B = '/home/claude/teg-tutorial/mocktest/banks/'
F1 = 'Complete the form below. Write <b>ONE WORD AND/OR A NUMBER</b> for each answer.'
N1 = 'Complete the notes. Write <b>ONE WORD AND/OR A NUMBER</b> for each answer.'
def GQ(p, a, ex, g): return {'type': 'gap', 'prompt': p, 'answer': a if isinstance(a, list) else [a], 'explain': ex, 'group': g}
def MQ(p, opts, ans, ex, g): return {'type': 'mcq', 'group': g, 'prompt': p, 'options': opts, 'answer': ans, 'explain': ex}
V = {'au': ('en-AU-WilliamNeural', 'en-AU-NatashaNeural'), 'gb': ('en-GB-RyanNeural', 'en-GB-SoniaNeural'), 'us': ('en-US-GuyNeural', 'en-US-JennyNeural'),
     'nz': ('en-NZ-MitchellNeural', 'en-NZ-MollyNeural'), 'ca': ('en-CA-LiamNeural', 'en-CA-ClaraNeural')}
def S(sid, title, voices, script, qs): return dict(id=sid, title=title, voices=voices, script=script.strip(), questions=qs)

g11 = 'Questions 11-15: Choose the correct letter, <b>A, B or C</b>.'
g21 = 'Questions 21-25: Choose the correct letter, <b>A, B or C</b>.'
L1 = [
 S('L1c', 'Part 1 · Bike hire', {'M': V['nz'][0], 'W': V['nz'][1]}, """
M: Good morning, Harbourside Bike Hire. How can I help you?
W: Hi. I'd like to hire a bike for next weekend, please.
M: No problem. Could I have your name?
W: It's Lina Wijaya. That's W-I-J-A-Y-A.
M: Thanks, Lina. Which day would you like to start?
W: Saturday the ninth, but I'll be away on Sunday afternoon, so just one day.
M: OK, one day. Would you like a city bike or an electric bike?
W: How much is the electric one?
M: Electric bikes are sixty dollars a day. City bikes are thirty-five.
W: I'll take the city bike, then. I'm only going around the waterfront.
M: Good choice. Do you need a helmet? It's required by law here.
W: Yes, please. Is that extra?
M: Helmets are free, but we do charge four dollars for a lock.
W: I'll take a lock as well.
M: And what time will you collect the bike?
W: Around half past eight in the morning.
M: We open at nine on Saturdays, I'm afraid.
W: Oh, then nine o'clock is fine.
M: Lastly, we need a contact number.
W: Sure, it's 0421 775 309.
M: Thanks. Please bring your driver's licence or passport as ID when you collect it.
W: My passport, then. Thanks very much.""",
  [GQ('Surname: ___', 'Wijaya', '"W-I-J-A-Y-A."', F1), GQ('Start date: Saturday ___', ['9', '9th', 'ninth'], 'Saturday the ninth.', F1), GQ('Hire length: ___ day(s)', ['1', 'one'], 'Away on Sunday afternoon, so one day.', F1),
   GQ('Type of bike: ___ bike', 'city', 'She chooses the city bike (electric is a distractor).', F1), GQ('Price per day: $___', ['35', 'thirty-five'], 'City bikes are thirty-five dollars.', F1), GQ('Helmet cost: ___', ['free', '0'], '"Helmets are free."', F1),
   GQ('Lock cost: $___', ['4', 'four'], '"Four dollars for a lock."', F1), GQ('Collection time: ___ a.m.', ['9', 'nine', '9:00'], '8:30 is too early; they open at nine.', F1), GQ('Phone: 0421 775 ___', '309', '"0421 775 309."', F1), GQ('ID to bring: ___', 'passport', 'She will bring her passport.', F1)]),
 S('L1d', 'Part 1 · Volunteer application', {'M': V['gb'][0], 'W': V['gb'][1]}, """
W: Hello, Greenfield Animal Shelter, Sophie speaking.
M: Hi, I saw your advertisement for volunteers. I'd like to apply.
W: Wonderful. Let me take some details. What's your name?
M: Daniel Hartono. H-A-R-T-O-N-O.
M: I'm a second-year student studying veterinary science.
W: That's very useful. Which days are you free?
M: Tuesdays and Thursdays, but Thursday mornings I have lectures, so Tuesdays are best.
W: Tuesday it is. We have three areas: dog walking, cleaning, and helping at reception.
M: I'd love to walk the dogs.
W: Great. Dog walkers start at seven thirty, before it gets too hot.
M: That's fine.
W: Have you worked with animals before?
M: Yes, I worked at a farm for six months last year.
W: Excellent. All volunteers must attend a training session. The next one is on the twenty-second.
M: The twenty-second is fine.
W: And you'll need to wear closed shoes. We provide a T-shirt, but not shoes.
M: Understood. How do I get there? I don't have a car.
W: Take bus number 48. It stops right outside the gate.
M: Perfect. Thanks, Sophie.""",
  [GQ('Surname: ___', 'Hartono', '"H-A-R-T-O-N-O."', F1), GQ('Studying: ___ science', 'veterinary', '"veterinary science".', F1), GQ('Year of study: ___', ['2', 'second', '2nd'], '"second-year student".', F1),
   GQ('Day available: ___', 'Tuesday', 'Thursday mornings he has lectures, so Tuesday.', F1), GQ('Preferred task: ___ walking', 'dog', '"walk the dogs".', F1), GQ('Start time: ___ a.m.', ['7:30', '7.30', 'seven thirty'], '"seven thirty".', F1),
   GQ('Experience: worked on a ___', 'farm', '"worked at a farm".', F1), GQ('Training date: the ___', ['22nd', '22', 'twenty-second'], '"the twenty-second".', F1), GQ('Must wear: closed ___', 'shoes', '"closed shoes".', F1), GQ('Bus number: ___', ['48', 'forty-eight'], '"bus number 48".', F1)]),
 S('L1e', 'Part 1 · Cooking class enquiry', {'M': V['ca'][0], 'W': V['ca'][1]}, """
M: Good afternoon, Spice Route Cooking School.
W: Hi, I'm calling about your evening cooking classes.
M: Sure. We have Thai, Italian and Indonesian courses at the moment.
W: I'm interested in the Thai course. How long does it run?
M: Six weeks, one evening a week, on Wednesdays.
W: And what time?
M: From six thirty to nine.
W: How much does it cost?
M: The full course is two hundred and forty dollars. That includes all ingredients.
W: Do I need to bring anything?
M: Just an apron. We supply knives and other equipment.
W: Great. Is there parking?
M: There's a car park behind the building, but it's quite small. Most students take the train; the station is a five-minute walk away.
W: OK. When does the next course start?
M: The next one begins on the fifth of March. The February course is already full.
W: The fifth of March, then. Can I book now?
M: Of course. Could I have your name?
W: Mei Ling Tan. T-A-N.
M: And an email address?
W: meiling dot tan at mailbox dot com.
M: Thanks. You'll receive a confirmation email today.""",
  [GQ('Course chosen: ___', 'Thai', '"interested in the Thai course".', F1), GQ('Length: ___ weeks', ['6', 'six'], '"Six weeks".', F1), GQ('Day: ___', 'Wednesday', '"on Wednesdays".', F1),
   GQ('Time: 6.30 to ___ p.m.', ['9', 'nine'], '"six thirty to nine".', F1), GQ('Total cost: $___', ['240', 'two hundred and forty'], '"two hundred and forty dollars".', F1), GQ('Bring: an ___', 'apron', '"Just an apron."', F1),
   GQ('Most students travel by ___', 'train', '"Most students take the train".', F1), GQ('Start date: ___ March', ['5', '5th', 'fifth'], '"the fifth of March" (February is full).', F1), GQ('Surname: ___', 'Tan', '"T-A-N".', F1), GQ('Confirmation sent by: ___', 'email', '"a confirmation email".', F1)]),
]

L2 = [
 S('L2c', 'Part 2 · Museum audio tour', {'M': V['gb'][0], 'W': V['gb'][1]}, """
W: Welcome to the Maritime Museum. Before you start your visit, here is some practical information.
The museum has three floors. On the ground floor you'll find the ticket desk, the shop and our temporary exhibition, which this month is about lighthouses. The permanent collection of ship models is on the first floor, and the café and the rooftop viewing deck are on the second floor.
Please note that the rooftop deck closes at four o'clock, an hour before the museum itself, so if you want to enjoy the view, go there first.
Photography is allowed everywhere except in the temporary exhibition, because some of the objects are on loan from other museums.
If you would like a guided tour, they leave from the ticket desk at eleven and at two. They last about forty-five minutes and are free with your ticket.
Lockers for bags are available next to the shop. They cost one dollar, which you get back when you return the key.
Finally, families with young children might enjoy the activity trail. Pick up a trail sheet at the ticket desk; children who complete it receive a small prize in the shop.""",
  [MQ('This month, the temporary exhibition is about', ['ship models.', 'lighthouses.', 'famous sailors.'], 1, '"which this month is about lighthouses".', g11),
   MQ('The ship models are on the', ['ground floor.', 'first floor.', 'second floor.'], 1, '"permanent collection of ship models is on the first floor".', g11),
   MQ('The rooftop deck closes at', ['4 p.m.', '5 p.m.', '3 p.m.'], 0, '"closes at four o’clock, an hour before the museum".', g11),
   MQ('Photography is not allowed', ['on the rooftop.', 'in the temporary exhibition.', 'in the café.'], 1, '"except in the temporary exhibition".', g11),
   MQ('Guided tours', ['cost extra.', 'leave twice a day.', 'last two hours.'], 1, 'At eleven and at two; free; 45 minutes.', g11),
   GQ('Lockers are next to the ___.', 'shop', '"next to the shop".', N1), GQ('A locker costs ___ dollar(s), returned later.', ['1', 'one'], '"one dollar".', N1), GQ('Tours last about ___ minutes.', ['45', 'forty-five'], '"about forty-five minutes".', N1),
   GQ('Children collect a trail ___ at the ticket desk.', 'sheet', '"Pick up a trail sheet".', N1), GQ('Children who finish the trail get a small ___.', 'prize', '"receive a small prize".', N1)]),
 S('L2d', 'Part 2 · Campus safety talk', {'M': V['au'][0], 'W': V['au'][1]}, """
M: Hi everyone, I'm Josh from Campus Security. I just want to give you a few tips for your first weeks here.
First, the security office is in the basement of the library building, and it's open twenty-four hours a day, every day of the year.
If you're studying late, we run a free shuttle bus that takes students to the train station and the main car parks. It runs every twenty minutes from six p.m. until midnight. You can track it on the university app.
We also offer a safety escort service. If you don't feel comfortable walking alone, call us and a security officer will walk with you anywhere on campus.
Please register your bicycle with us. It only takes five minutes and it's free, and it helps us return stolen bikes to their owners.
Lost property is kept at the security office for one month. After that, items are donated to charity.
Finally, save our emergency number in your phone now. It's on the back of your student card. In an emergency, you can also use the blue phones located around campus; they connect directly to our office.""",
  [MQ('The security office is located', ['in the library basement.', 'next to the car park.', 'in the student centre.'], 0, '"in the basement of the library building".', g11),
   MQ('The shuttle bus runs', ['every 20 minutes in the evening.', 'all night.', 'only to the car parks.'], 0, '6 p.m. to midnight, every 20 minutes; also to the station.', g11),
   MQ('The escort service', ['is only for staff.', 'walks students anywhere on campus.', 'costs a small fee.'], 1, '"walk with you anywhere on campus".', g11),
   MQ('Bicycle registration', ['takes about an hour.', 'is free.', 'is required by law.'], 1, '"it’s free".', g11),
   MQ('Unclaimed lost property is', ['sold.', 'kept for a year.', 'given to charity after a month.'], 2, '"kept for one month ... donated to charity".', g11),
   GQ('The security office is open ___ hours a day.', ['24', 'twenty-four'], '"twenty-four hours a day".', N1), GQ('The shuttle stops running at ___.', 'midnight', '"until midnight".', N1), GQ('You can track the shuttle on the university ___.', 'app', '"on the university app".', N1),
   GQ('The emergency number is on the back of your student ___.', 'card', '"on the back of your student card".', N1), GQ('The ___ phones connect directly to security.', 'blue', '"the blue phones".', N1)]),
 S('L2e', 'Part 2 · Community festival radio announcement', {'M': V['us'][0], 'W': V['us'][1]}, """
W: And now, news about this weekend's Riverside Festival. The festival runs on Saturday and Sunday in Riverside Park, from ten in the morning until nine at night.
Entry is free, but some workshops need to be booked in advance on the festival website. The pottery workshop is especially popular and is already almost full.
This year there will be over forty food stalls, with food from more than fifteen countries. For the first time, all stalls must use reusable or compostable plates, and there will be free water refill stations instead of bottled water.
The main stage will host live music both days. The headline concert on Saturday evening starts at seven thirty. On Sunday, the main stage is reserved for local school bands in the afternoon.
Because parking near the park is very limited, organisers strongly recommend public transport. Extra trains will run on the Green Line, and there will be a free bike parking area at the north entrance.
If it rains, the music will move into the community hall, but the market will continue outdoors.
And remember, dogs are welcome, but they must be kept on a lead.""",
  [MQ('Entry to the festival', ['is free.', 'costs ten dollars.', 'must be booked online.'], 0, '"Entry is free".', g11),
   MQ('Which workshop is almost full?', ['Pottery', 'Painting', 'Cooking'], 0, '"The pottery workshop ... almost full".', g11),
   MQ('What is new this year?', ['Food from fifteen countries', 'Only reusable or compostable plates', 'Bottled water for sale'], 1, '"For the first time, all stalls must use reusable or compostable plates".', g11),
   MQ('On Sunday afternoon, the main stage is for', ['the headline concert.', 'local school bands.', 'food demonstrations.'], 1, '"reserved for local school bands".', g11),
   MQ('If it rains,', ['the whole festival is cancelled.', 'the music moves indoors.', 'the market moves to the hall.'], 1, '"music will move into the community hall".', g11),
   GQ('The festival finishes at ___ p.m. each day.', ['9', 'nine'], '"until nine at night".', N1), GQ('There will be over ___ food stalls.', ['40', 'forty'], '"over forty food stalls".', N1), GQ('Saturday’s headline concert starts at ___.', ['7:30', '7.30', 'seven thirty'], '"seven thirty".', N1),
   GQ('Extra trains will run on the ___ Line.', 'Green', '"the Green Line".', N1), GQ('Dogs must be kept on a ___.', 'lead', '"kept on a lead".', N1)]),
]

L3 = [
 S('L3c', 'Part 3 · Presentation on food waste', {'T': V['gb'][1], 'A': V['au'][1], 'B': V['au'][0]}, """
T: So, Priya and Ben, how is your presentation on food waste coming along?
A: Mostly fine, Professor Grant. We decided to focus on university cafés rather than households, because we could collect our own data there.
T: Good idea. How did you collect it?
B: We weighed the food that was thrown away at two cafés for a week. We wanted to do three, but one café didn't give permission.
T: And what did you find?
A: The biggest category was bread and pastries, not cooked meals as we'd expected. Cafés bake too much in the morning.
T: Interesting. What are you recommending?
B: We think cafés should sell leftover items at a discount in the last hour. Priya also suggested a donation scheme.
A: But donations are complicated because of food safety rules, so we'll only mention that briefly.
T: That's sensible. What about the structure of the presentation?
B: We'll start with a short video, then present the data. We were going to put the recommendations at the end, but we think it's better to finish with questions for the audience.
T: How long is it?
A: Fifteen minutes, but we're running at about twenty, so we need to cut something.
T: I'd shorten the background section. The audience will already know why food waste matters.
B: Yes, that makes sense. And the slides?
T: Use more charts and less text. People can't read and listen at the same time.""",
  [MQ('Why did the students focus on university cafés?', ['They could collect their own data.', 'Households produce less waste.', 'Their tutor asked them to.'], 0, '"because we could collect our own data there".', g21),
   MQ('How many cafés did they study?', ['One', 'Two', 'Three'], 1, 'They wanted three, but one refused, so two.', g21),
   MQ('The largest category of waste was', ['cooked meals.', 'bread and pastries.', 'fruit.'], 1, '"bread and pastries, not cooked meals".', g21),
   MQ('Why will they only briefly mention donations?', ['Food safety rules make them complicated.', 'Cafés refused.', 'There is no time.'], 0, '"donations are complicated because of food safety rules".', g21),
   MQ('The presentation will finish with', ['recommendations.', 'a video.', 'questions for the audience.'], 2, '"better to finish with questions for the audience".', g21),
   GQ('They weighed waste for one ___.', 'week', '"for a week".', N1), GQ('Recommendation: sell leftovers at a ___ in the last hour.', 'discount', '"at a discount".', N1), GQ('Required length: ___ minutes.', ['15', 'fifteen'], '"Fifteen minutes".', N1),
   GQ('The tutor suggests shortening the ___ section.', 'background', '"shorten the background section".', N1), GQ('Slides should use more ___ and less text.', 'charts', '"more charts and less text".', N1)]),
 S('L3d', 'Part 3 · Choosing a dissertation topic', {'T': V['us'][0], 'A': V['us'][1]}, """
T: Hi Sarah, come in. You wanted to talk about your dissertation topic?
A: Yes, Dr Morris. I'm choosing between two ideas: one on tourism in small island countries and one on electric scooters in cities.
T: Both sound interesting. Which do you prefer?
A: Honestly, the tourism one, because I'm from Fiji and I know the context well. But I'm worried there isn't enough recent research.
T: That can actually be an advantage. If there's a gap, your work is more original. What about data?
A: I could interview hotel managers when I go home in July.
T: That's good, but remember you'll need ethics approval before any interviews. That usually takes about six weeks.
A: Six weeks? Then I need to apply soon.
T: Yes, I'd submit the application this month. What would the scooter project involve?
A: Mostly analysing existing city data. It would be quicker, but I'm less excited about it.
T: Motivation matters a lot for a project that lasts a whole year. I'd go with tourism.
A: OK. How long should the literature review be?
T: Around three thousand words. And try to include sources from the region, not only from Europe and America.
A: That's helpful. Should I meet you again?
T: Yes, send me a one-page proposal by Friday and we'll meet next Tuesday.""",
  [MQ('Why does Sarah prefer the tourism topic?', ['She knows the context well.', 'There is a lot of recent research.', 'It would be quicker.'], 0, '"because I’m from Fiji and I know the context well".', g21),
   MQ('What does Dr Morris say about the lack of research?', ['It is a serious problem.', 'It may make the work more original.', 'She should choose another topic.'], 1, '"your work is more original".', g21),
   MQ('Before interviews, Sarah must', ['get ethics approval.', 'buy a recorder.', 'contact the government.'], 0, '"you’ll need ethics approval".', g21),
   MQ('The scooter project would mainly involve', ['interviews.', 'existing city data.', 'a survey of riders.'], 1, '"analysing existing city data".', g21),
   MQ('Why does Dr Morris recommend tourism?', ['It is cheaper.', 'Motivation is important for a long project.', 'It is easier to publish.'], 1, '"Motivation matters a lot".', g21),
   GQ('Sarah will interview hotel ___.', 'managers', '"interview hotel managers".', N1), GQ('She can do interviews in ___.', 'July', '"when I go home in July".', N1), GQ('Ethics approval usually takes about ___ weeks.', ['6', 'six'], '"about six weeks".', N1),
   GQ('The literature review should be about ___ words.', ['3000', '3,000', 'three thousand'], '"three thousand words".', N1), GQ('Send a one-page ___ by Friday.', 'proposal', '"a one-page proposal".', N1)]),
 S('L3e', 'Part 3 · Group project on water saving', {'T': V['nz'][1], 'A': V['nz'][0], 'B': V['ca'][1]}, """
T: Right, Aaron and Nina, let's look at your project on saving water in student housing.
A: We surveyed residents in two buildings. The main finding was that showers use far more water than anything else.
B: Yes, average showers were nearly eleven minutes long, which surprised us.
T: What solution did you test?
A: We put small timers in twenty bathrooms. They show a light after four minutes.
B: Water use in those bathrooms fell by about a fifth over a month.
T: That's impressive. Were there any problems?
A: A few students removed the timers. We think it was because the light was too bright at night.
T: Could you change that?
B: We've found a model with a softer light. It costs a bit more, but it's still cheap.
T: Good. What about the report? It's due in three weeks.
A: We've written the method and results. The discussion is the hard part.
T: In the discussion, compare your results with other studies, and be honest about the limitations - for example, one month is a short time.
B: Should we include photos of the timers?
T: Yes, in the appendix, not in the main text.""",
  [MQ('What used the most water?', ['Washing machines', 'Showers', 'Kitchen taps'], 1, '"showers use far more water".', g21),
   MQ('What surprised the students?', ['The length of showers', 'The number of residents', 'The cost of water'], 0, '"nearly eleven minutes long, which surprised us".', g21),
   MQ('Why did some students remove the timers?', ['The light was too bright at night.', 'They were noisy.', 'They broke easily.'], 0, '"the light was too bright at night".', g21),
   MQ('What does the tutor say about one month?', ['It is a limitation.', 'It is long enough.', 'It should be extended to a year.'], 0, '"one month is a short time" (limitation).', g21),
   MQ('Where should photos go?', ['In the appendix', 'In the results', 'In the introduction'], 0, '"in the appendix".', g21),
   GQ('Average showers lasted nearly ___ minutes.', ['11', 'eleven'], '"nearly eleven minutes".', N1), GQ('Timers were placed in ___ bathrooms.', ['20', 'twenty'], '"twenty bathrooms".', N1), GQ('The light comes on after ___ minutes.', ['4', 'four'], '"after four minutes".', N1),
   GQ('Water use fell by about a ___.', 'fifth', '"about a fifth".', N1), GQ('The report is due in ___ weeks.', ['3', 'three'], '"due in three weeks".', N1)]),
]

L4 = [
 S('L4c', 'Part 4 · Lecture: the history of tea', {'L': V['gb'][0]}, """
L: Today's lecture is about the history of tea, one of the most widely consumed drinks in the world after water.
Tea comes from the leaves of a single plant, Camellia sinensis. Green, black and oolong tea all come from the same plant; the difference lies in how the leaves are processed, especially how long they are exposed to air, which is called oxidation.
Tea was first drunk in China, probably as a medicine. By the eighth century, it had become a popular everyday drink, and a scholar called Lu Yu wrote the first book entirely about tea.
Tea reached Europe in the early seventeenth century, brought by Dutch traders. At first it was very expensive and drunk mainly by the wealthy. In Britain, high taxes led to widespread smuggling until the tax was greatly reduced in 1784.
In the nineteenth century, the British began growing tea in India, partly to reduce their dependence on China. Large plantations were established in Assam and later in Darjeeling, and India eventually became one of the world's largest producers.
Today, the biggest producer is China, followed by India and Kenya. Interestingly, the country that drinks the most tea per person is not in Asia at all; it is Turkey.""",
  [GQ('All tea comes from one ___.', 'plant', '"a single plant".', N1), GQ('The difference between teas depends on ___.', 'oxidation', '"which is called oxidation".', N1), GQ('Tea was probably first used as a ___.', 'medicine', '"probably as a medicine".', N1),
   GQ('Lu Yu wrote the first ___ about tea.', 'book', '"the first book entirely about tea".', N1), GQ('Tea reached Europe with ___ traders.', 'Dutch', '"Dutch traders".', N1), GQ('High taxes in Britain caused ___.', 'smuggling', '"widespread smuggling".', N1),
   GQ('The tax was reduced in ___.', '1784', '"in 1784".', N1), GQ('Early Indian plantations were in Assam and ___.', 'Darjeeling', '"Assam and later in Darjeeling".', N1), GQ('The third-largest producer today is ___.', 'Kenya', '"China, followed by India and Kenya".', N1), GQ('The highest tea drinking per person is in ___.', 'Turkey', '"it is Turkey".', N1)]),
 S('L4d', 'Part 4 · Lecture: urban heat islands', {'L': V['au'][1]}, """
L: This morning I'd like to explain the urban heat island effect - the reason cities are often several degrees warmer than the surrounding countryside.
The main cause is surface materials. Dark roads and roofs absorb sunlight during the day and release the heat slowly at night, which is why the difference between city and countryside is often greatest after sunset.
A second cause is the lack of vegetation. Trees cool the air through shade and through evaporation of water from their leaves. Cities with fewer trees lose this natural cooling.
Third, heat is produced directly by human activity: vehicles, factories and, increasingly, air conditioners, which push hot air out of buildings.
The effects are serious. Heatwaves are more dangerous in cities, especially for elderly people, and higher temperatures increase electricity demand.
What can be done? One cheap solution is painting roofs white or light grey to reflect sunlight. Another is planting trees along streets; studies show that a tree-lined street can be up to five degrees cooler at midday. Some cities are also replacing car parks with small parks, and using permeable pavements that hold water and cool the surface as it evaporates.
In the next lecture, we'll look at how one city, Melbourne, has set a target of covering forty per cent of its area with tree canopy.""",
  [GQ('Cities can be several ___ warmer than the countryside.', 'degrees', '"several degrees warmer".', N1), GQ('Dark surfaces release heat slowly at ___.', 'night', '"release the heat slowly at night".', N1), GQ('The difference is often greatest after ___.', 'sunset', '"greatest after sunset".', N1),
   GQ('Trees cool the air through shade and ___.', 'evaporation', '"through evaporation".', N1), GQ('Air conditioners push hot air out of ___.', 'buildings', '"out of buildings".', N1), GQ('Heatwaves are especially dangerous for ___ people.', 'elderly', '"especially for elderly people".', N1),
   GQ('A cheap solution is painting roofs ___ or light grey.', 'white', '"white or light grey".', N1), GQ('Tree-lined streets can be up to ___ degrees cooler.', ['5', 'five'], '"up to five degrees cooler".', N1), GQ('Permeable pavements hold ___.', 'water', '"hold water".', N1), GQ('Melbourne’s canopy target is ___ per cent.', ['40', 'forty'], '"forty per cent".', N1)]),
 S('L4e', 'Part 4 · Lecture: how memory works', {'L': V['us'][0]}, """
L: Today we're going to look at how memory works, and what this means for studying.
Psychologists usually describe three stages. First, information enters sensory memory, which lasts less than a second. If we pay attention to it, it moves into working memory, which can hold only around four items at a time and fades within about twenty seconds unless we repeat it.
To keep information for longer, it has to be transferred into long-term memory. This happens best when we connect new information to something we already know - a process called elaboration.
One of the most reliable findings in memory research is the spacing effect. Studying the same material in several short sessions spread over days is far more effective than one long session the night before an exam.
Another powerful technique is retrieval practice, which simply means testing yourself. Trying to recall information, for example with flashcards, strengthens memory more than reading your notes again.
Sleep is also essential. During sleep, especially deep sleep, the brain replays and stabilises what we learned during the day.
Finally, a common myth: many students believe they have a fixed learning style, such as visual or auditory. Research has found little evidence that matching teaching to these styles improves results.""",
  [GQ('Sensory memory lasts less than a ___.', 'second', '"less than a second".', N1), GQ('Working memory holds around ___ items.', ['4', 'four'], '"around four items".', N1), GQ('Working memory fades within about ___ seconds.', ['20', 'twenty'], '"about twenty seconds".', N1),
   GQ('Linking new information to existing knowledge is called ___.', 'elaboration', '"a process called elaboration".', N1), GQ('Studying in several short sessions is the ___ effect.', 'spacing', '"the spacing effect".', N1), GQ('Testing yourself is called retrieval ___.', 'practice', '"retrieval practice".', N1),
   GQ('One example tool for recall is ___.', 'flashcards', '"with flashcards".', N1), GQ('Memory is stabilised especially during ___ sleep.', 'deep', '"especially deep sleep".', N1), GQ('A common myth is that people have a fixed learning ___.', 'style', '"a fixed learning style".', N1), GQ('There is little ___ for matching teaching to styles.', 'evidence', '"little evidence".', N1)]),
]

def ssml(s):
    out = ["<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-AU'>"]; cur = None
    for line in s['script'].split('\n'):
        line = line.strip()
        if not line: continue
        m = re.match(r'^([A-Z]):\s*(.*)', line)
        if m: cur, txt = m.group(1), m.group(2)
        else: txt = line
        out.append(f"<voice name='{s['voices'][cur]}'>{html.escape(txt, quote=False)}<break time='600ms'/></voice>")
    return ''.join(out) + '</speak>'

if __name__ == '__main__':
    d = json.load(open(B + 'ielts.json', encoding='utf-8'))
    sc = {}
    for slot, sets in (('P1', L1), ('P2', L2), ('P3', L3), ('P4', L4)):
        sl = [x for x in d['sections'][0]['slots'] if x['id'] == slot][0]; have = {x['id'] for x in sl['sets']}
        for s in sets:
            sc[s['id']] = ssml(s)
            o = {'id': s['id'], 'title': s['title'], 'audio': f"audio/ielts/{s['id']}.mp3", 'transcript': html.escape(s['script']), 'questions': s['questions']}
            if s['id'] not in have: sl['sets'].append(o)
    json.dump(d, open(B + 'ielts.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(sc, open('/home/claude/w91/t4_ielts_ssml.json', 'w'), ensure_ascii=False)
    print({k: len(v) for k, v in sc.items()})
