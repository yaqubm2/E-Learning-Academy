"""Curated starter curriculum, freely authored for this project.
Seven grade levels x seven subjects; each lesson has six assessment questions.
These are introductory practice items, not a complete accredited curriculum.
"""
from .store_constants import GRADES, SUBJECTS


def q(prompt, choices, correct):
    return {'prompt': prompt, 'choices': choices, 'answer': correct}

# A grade is represented by a different age-appropriate topic in each subject.
# Each subject row contains seven grade entries: (title, explanation, 6 question tuples).
BANK = {
'English': [
 ('Letters and Sounds','Letters have names and sounds. Listen to beginning sounds and look for familiar letters.',[
  ('Which is the letter A?',['A','C','D'],0),('Which starts with B?',['Ball','Apple','Sun'],0),('Which letter comes after A?',['D','B','E'],1),('Which word begins with C?',['Cat','Dog','Fish'],0),('Which is a vowel?',['A','B','T'],0),('Which is the last letter in CAT?',['C','A','T'],2)]),
 ('Phonics and Rhymes','Words may start with the same sound and end with rhyming sounds.',[
  ('Which rhymes with cat?',['Hat','Sun','Dog'],0),('Which begins with S?',['Sun','Ball','Apple'],0),('Which rhymes with log?',['Frog','Tree','Sky'],0),('How many letters in DOG?',['2','3','4'],1),('Which rhymes with bee?',['Tree','Hat','Cup'],0),('Which word starts with M?',['Moon','Star','Fish'],0)]),
 ('Nouns and Sentences','A noun names a person, place, animal or thing. Sentences begin with capital letters.',[
  ('Which is a noun?',['Run','Cat','Quickly'],1),('Which is a place?',['School','Jump','Happy'],0),('What ends a statement?',['Period','Comma','Question mark'],0),('Which is a person?',['Teacher','Blue','Run'],0),('Which is an animal?',['Tiger','Read','Big'],0),('Choose correct start of a sentence.',['i like apples.','I like apples.','i Like apples.'],1)]),
 ('Verbs and Adjectives','Verbs describe actions. Adjectives tell us more about a noun.',[
  ('Which is an action?',['Run','Blue','Table'],0),('Which describes the sky?',['Bright','Swim','Chair'],0),('Past tense of walk?',['Walked','Walking','Walks'],0),('Which is an adjective?',['Soft','Jump','Car'],0),('Which is a verb?',['Sing','Green','Book'],0),('Which sentence is a question?',['Where are you?','I am here.','The cat sleeps.'],0)]),
 ('Reading and Grammar','Understand short passages, pronouns, and punctuation.',[
  ('Which pronoun replaces Sara?',['She','They','It'],0),('Plural of box?',['Boxes','Boxs','Boxen'],0),('Which mark ends a question?',['?','.','!'],0),('Opposite of narrow?',['Wide','Tiny','Small'],0),('Synonym of happy?',['Glad','Angry','Sad'],0),('Which conjunction joins ideas?',['And','Red','Fast'],0)]),
 ('Tenses and Vocabulary','Use verb tenses and precise vocabulary in sentences.',[
  ('Past tense of go?',['Went','Goed','Going'],0),('Which word is an adverb?',['Quickly','Quick','Quicker'],0),('Opposite of ancient?',['Modern','Old','Past'],0),('Which is a compound word?',['Sunflower','Blue','Run'],0),('Which word is a preposition?',['Under','Laugh','Pretty'],0),('Which is a complete sentence?',['The birds fly.','In the park','Very tall'],0)]),
 ('Comprehension and Language','Explore context, meaning, and sentence structures.',[
  ('Which word means very big?',['Enormous','Tiny','Short'],0),('Which is a simile?',['As brave as a lion','The lion roared','A brave lion'],0),('Which sentence is passive?',['The cake was baked by Ali.','Ali baked the cake.','Ali is baking.'],0),('Antonym of scarce?',['Abundant','Rare','Limited'],0),('Which is a collective noun?',['Team','Player','Kick'],0),('Choose the correct sentence.',['Neither boy is late.','Neither boy are late.','Neither boys is late.'],0)])],
'Mathematics': [
 ('Counting and Shapes','Count objects, compare small numbers and identify basic shapes.',[
  ('⭐ ⭐ ⭐ How many stars?',['2','3','4'],1),('What comes after 4?',['3','5','7'],1),('Which shape has three sides?',['Triangle','Circle','Square'],0),('Which number is smaller?',['2','8','9'],0),('🍎 🍎 How many apples?',['1','2','3'],1),('Which shape is round?',['Circle','Rectangle','Triangle'],0)]),
 ('Numbers up to 20','Learn to add, subtract and compare numbers.',[
  ('7 + 2 = ?',['8','9','10'],1),('10 - 3 = ?',['7','6','8'],0),('Which is greatest?',['11','15','13'],1),('What comes before 12?',['10','11','13'],1),('5 + 5 = ?',['10','9','11'],0),('How many tens are in 20?',['1','2','3'],1)]),
 ('Adding and Subtracting','Addition combines groups. Subtraction finds what remains.',[
  ('8 + 5 = ?',['13','12','14'],0),('14 - 6 = ?',['7','8','9'],1),('9 + 7 = ?',['16','15','17'],0),('20 - 9 = ?',['10','11','12'],1),('7 + 6 = ?',['12','13','14'],1),('18 - 9 = ?',['8','9','10'],1)]),
 ('Multiplication and Division','Multiplication forms equal groups; division shares equally.',[
  ('3 × 4 = ?',['12','7','14'],0),('20 ÷ 5 = ?',['3','4','5'],1),('6 × 3 = ?',['18','12','21'],0),('24 ÷ 4 = ?',['5','6','8'],1),('7 × 2 = ?',['14','12','16'],0),('16 ÷ 2 = ?',['6','8','9'],1)]),
 ('Fractions and Measurement','Fractions describe equal parts. Measure lengths and time.',[
  ('Half of 18 is?',['9','8','6'],0),('1/4 of 20 is?',['4','5','10'],1),('How many cm in 1 metre?',['10','100','1000'],1),('3/4 is equivalent to?',['6/8','2/8','3/8'],0),('How many minutes in 1 hour?',['30','60','100'],1),('Which is longer?',['1 metre','50 cm','25 cm'],0)]),
 ('Decimals and Factors','Practice decimal arithmetic, factors and fractions.',[
  ('0.5 + 0.25 = ?',['0.75','0.30','0.55'],0),('Factor of 24?',['7','6','5'],1),('3/5 as a decimal is?',['0.6','0.3','0.8'],0),('12 × 8 = ?',['96','88','108'],0),('Which is prime?',['17','15','21'],0),('2.4 + 1.3 = ?',['3.5','3.7','3.9'],1)]),
 ('Percentages and Geometry','Connect fractions, percentages, area and geometry.',[
  ('25% of 80 = ?',['20','25','40'],0),('Area of rectangle 5 by 4?',['9','20','18'],1),('3/4 as a percentage?',['75%','25%','50%'],0),('A right angle measures?',['45°','90°','180°'],1),('0.2 × 10 = ?',['2','0.02','20'],0),('Perimeter of square side 6?',['12','24','36'],1)])],
'Urdu': [
 ('اردو کے حروف','اردو حروف ا، ب، پ، ت کو دیکھیں اور ان کی آوازیں بولیں۔',[
  ('اردو کا پہلا حرف کون سا ہے؟',['ب','ا','پ'],1),('لفظ بلی کس حرف سے شروع ہوتا ہے؟',['ب','ت','د'],0),('لفظ پانی کس حرف سے شروع ہوتا ہے؟',['پ','ا','س'],0),('ا کے بعد کون سا حرف آتا ہے؟',['پ','ب','ت'],1),('لفظ انار کا پہلا حرف؟',['ا','ن','ر'],0),('لفظ تتلی کس حرف سے شروع ہوتا ہے؟',['ب','ت','پ'],1)]),
 ('آسان الفاظ','آسان الفاظ پڑھیں اور اشیاء کے نام پہچانیں۔',[
  ('بلی کیا ہے؟',['جانور','پھل','رنگ'],0),('سیب کیا ہے؟',['سبزی','پھل','پرندہ'],1),('سرخ کیا ہے؟',['رنگ','جانور','موسم'],0),('کتاب کس کام آتی ہے؟',['پڑھنے','کھانے','پینے'],0),('پانی کس کام آتا ہے؟',['پینے','لکھنے','دوڑنے'],0),('سورج کب نظر آتا ہے؟',['دن','رات','ہمیشہ'],0)]),
 ('اسم اور فعل','اسم کسی شخص، جگہ یا چیز کا نام ہے۔ فعل کام کو ظاہر کرتا ہے۔',[
  ('ان میں سے اسم کون سا ہے؟',['کتاب','دوڑنا','سونا'],0),('ان میں سے فعل کون سا ہے؟',['لکھنا','میز','قلم'],0),('استاد کون ہے؟',['شخص','رنگ','موسم'],0),('پاکستان کیا ہے؟',['ملک','کھلونا','پھل'],0),('پڑھنا کیا ہے؟',['فعل','رنگ','چیز'],0),('کرسی کیا ہے؟',['چیز','کام','حالت'],0)]),
 ('جملے اور متضاد','چھوٹے جملے اور متضاد الفاظ کی مشق کریں۔',[
  ('دن کا متضاد کیا ہے؟',['رات','صبح','روشنی'],0),('بڑا کا متضاد؟',['چھوٹا','اونچا','لمبا'],0),('گرم کا متضاد؟',['ٹھنڈا','نرم','سخت'],0),('خوش کا متضاد؟',['اداس','ہنستا','اچھا'],0),('اوپر کا متضاد؟',['نیچے','سامنے','باہر'],0),('سچ کا متضاد؟',['جھوٹ','اچھا','درست'],0)]),
 ('واحد اور جمع','واحد اور جمع الفاظ کی پہچان کریں۔',[
  ('کتاب کی جمع کیا ہے؟',['کتابیں','کتابا','کتابوں کا'],0),('لڑکا کی جمع کیا ہے؟',['لڑکے','لڑکی','لڑکپن'],0),('بچہ کی جمع کیا ہے؟',['بچے','بچپن','بچی'],0),('قلم کی جمع کیا ہے؟',['قلم','قلمیں','قلمی'],0),('پھول کی جمع؟',['پھول','پھولا','پھولہ'],0),('لڑکی کی جمع کیا ہے؟',['لڑکیاں','لڑکے','لڑک'],0)]),
 ('الفاظ کا مفہوم','روزمرہ الفاظ کے معنی، مترادفات اور جملوں کو سمجھیں۔',[
  ('خوشی کا قریب ترین معنی؟',['مسرت','غم','غصہ'],0),('علم کا تعلق کس سے ہے؟',['جاننے','سونے','کھانے'],0),('بہادر کا متضاد؟',['بزدل','دلیر','نڈر'],0),('محنت کا مطلب؟',['کوشش','سستی','آرام'],0),('روشنی کا متضاد؟',['اندھیرا','چمک','اجالا'],0),('دوست کا مترادف؟',['رفیق','دشمن','اجنبی'],0)]),
 ('گرامر کی مشق','اسم، فعل اور صفات کی دہرائی کریں۔',[
  ('خوبصورت کس قسم کا لفظ ہے؟',['صفت','فعل','حرف'],0),('لکھنا کیا ظاہر کرتا ہے؟',['کام','جگہ','رنگ'],0),('شہر کس کی مثال ہے؟',['اسم','فعل','صفت'],0),('تیز کس کی مثال ہے؟',['صفت','شخص','جگہ'],0),('دوڑنا کیا ہے؟',['فعل','اسم','رنگ'],0),('کتاب کس کی مثال ہے؟',['اسم','فعل','صفت'],0)])],
'Science': [
 ('Our Five Senses','Our eyes, ears, nose, tongue and skin help us learn about the world.',[
  ('Which body part helps us see?',['Eyes','Ears','Hands'],0),('We hear with our?',['Nose','Ears','Feet'],1),('Which sense helps us smell?',['Nose','Eyes','Skin'],0),('Which part tastes food?',['Tongue','Hair','Elbow'],0),('Which sense detects touch?',['Skin','Teeth','Eyes'],0),('How many basic senses?',['3','5','7'],1)]),
 ('Plants and Animals','Living things need resources such as water and air.',[
  ('What do plants need to grow?',['Water','Plastic','Glass'],0),('Which animal can fly?',['Bird','Fish','Ant'],0),('What do roots absorb?',['Water','Sunlight','Wind'],0),('Which is living?',['Tree','Rock','Spoon'],0),('Which part of plant is often green?',['Leaf','Stone','Plate'],0),('A baby cat is called?',['Kitten','Puppy','Calf'],0)]),
 ('Living and Nonliving','Living things grow, need energy and respond to surroundings.',[
  ('Which is a living thing?',['Mushroom','Table','Stone'],0),('Which is nonliving?',['Pencil','Dog','Flower'],0),('Which helps plants make food?',['Sunlight','Moonlight','Plastic'],0),('What do many animals breathe?',['Air','Sand','Metal'],0),('Which grows from a seed?',['Plant','Toy car','Shoe'],0),('Which animal lays eggs?',['Chicken','Cat','Cow'],0)]),
 ('States of Matter','Matter can be solid, liquid or gas; changes in temperature affect its state.',[
  ('Ice is a?',['Solid','Gas','Liquid'],0),('Water vapor is a?',['Gas','Solid','Metal'],0),('When ice melts it becomes?',['Liquid water','Sand','Air'],0),('Which has fixed shape?',['Solid','Gas','Liquid'],0),('Boiling water can form?',['Steam','Ice cubes','Dust'],0),('Which is a liquid?',['Milk','Brick','Oxygen'],0)]),
 ('Forces and Energy','Forces push and pull. Energy causes changes and motion.',[
  ('A push is a type of?',['Force','Color','Taste'],0),('Which gives Earth light?',['Sun','Moon','Cloud'],0),('Friction generally slows?',['Motion','Time','Color'],0),('Which is a renewable energy source?',['Wind','Coal','Oil'],0),('A magnet attracts?',['Iron','Wood','Paper'],0),('Sound is produced by?',['Vibrations','Shadows','Smells'],0)]),
 ('Human Body Systems','Body systems work together for breathing, circulation and digestion.',[
  ('The heart pumps?',['Blood','Air','Food'],0),('Lungs help us?',['Breathe','See','Hear'],0),('Which organ controls thinking?',['Brain','Stomach','Liver'],0),('The skeleton supports the?',['Body','Cloud','Ocean'],0),('Food is broken down by?',['Digestion','Vision','Hearing'],0),('Which carries oxygen around body?',['Blood','Bones','Hair'],0)]),
 ('Earth and Space','Our solar system, Earth movements and ecosystems.',[
  ('How many planets orbit the Sun?',['8','7','9'],0),('Earth takes about how long to orbit Sun?',['1 year','1 day','1 week'],0),('Earth rotation causes?',['Day and night','Seasons only','Rain'],0),('The Moon is Earth’s?',['Natural satellite','Star','Planet'],0),('Which gas do plants use in photosynthesis?',['Carbon dioxide','Helium','Neon'],0),('Which organelle uses light to make sugar?',['Chloroplast','Nucleus','Ribosome'],0)])],
'General Knowledge': [
 ('My World','Learn about family, weather, days, and everyday places.',[
  ('How many days in a week?',['5','7','10'],1),('Which shines in daytime?',['Sun','Moon','Stars only'],0),('Where do we borrow books?',['Library','Hospital','Airport'],0),('Which is used in rain?',['Umbrella','Sunglasses','Fan'],0),('What color is grass usually?',['Green','Purple','Orange'],0),('Which helps us tell time?',['Clock','Spoon','Chair'],0)]),
 ('Community Helpers','People in a community help us stay safe, healthy and informed.',[
  ('Who helps put out fires?',['Firefighter','Chef','Pilot'],0),('Who treats sick people?',['Doctor','Painter','Driver'],0),('Where do students learn?',['School','Market','Garage'],0),('Who grows crops?',['Farmer','Pilot','Actor'],0),('Who delivers letters?',['Postal worker','Diver','Tailor'],0),('What color often means stop on traffic lights?',['Red','Green','Blue'],0)]),
 ('Maps and Places','Use maps to understand directions and places.',[
  ('Which direction is opposite north?',['South','East','West'],0),('Which shows locations?',['Map','Fork','Mirror'],0),('Which is a continent?',['Asia','Lahore','Nile'],0),('Where do airplanes land?',['Airport','Library','Museum'],0),('What is a globe?',['Model of Earth','Type of car','Instrument'],0),('Which is a natural body of water?',['River','Road','Bridge'],0)]),
 ('Countries and Landmarks','Explore world geography, oceans and famous landmarks.',[
  ('Capital of Pakistan?',['Islamabad','Lahore','Karachi'],0),('Largest ocean?',['Pacific','Arctic','Indian'],0),('Eiffel Tower is in?',['France','Italy','Spain'],0),('The Nile is a?',['River','Mountain','Desert'],0),('The Great Wall is in?',['China','Brazil','Egypt'],0),('Which is a desert?',['Sahara','Amazon River','Alps'],0)]),
 ('World Cultures','Learn about languages, places and cultural respect.',[
  ('Which language is widely spoken in Brazil?',['Portuguese','Japanese','Arabic'],0),('Which instrument helps find direction?',['Compass','Thermometer','Ruler'],0),('What is a continent?',['Large land region','Small vehicle','Ocean fish'],0),('Which is an island country?',['Japan','Nepal','Mongolia'],0),('Which is a world ocean?',['Atlantic','Sahara','Andes'],0),('Why respect cultures?',['Build understanding','Make fun of others','Avoid learning'],0)]),
 ('History and Inventions','Discover inventions and how people learn about the past.',[
  ('Which instrument measures temperature?',['Thermometer','Compass','Scale'],0),('Which invention helps communicate over distance?',['Telephone','Spoon','Chair'],0),('Who studies the past?',['Historian','Dentist','Pilot'],0),('What is a fossil?',['Preserved trace of ancient life','Modern phone','Type of cloud'],0),('Which invention is used to print books?',['Printing press','Telescope','Microscope'],0),('Where are historical objects displayed?',['Museum','Garage','Pool'],0)]),
 ('Global Awareness','Explore the environment, citizenship and global cooperation.',[
  ('Which action conserves water?',['Turn off unused tap','Leave tap open','Waste water'],0),('What does recycle mean?',['Process used materials','Burn all waste','Throw into rivers'],0),('Which helps protect biodiversity?',['Habitat conservation','Pollution','Deforestation'],0),('Which gas is a greenhouse gas?',['Carbon dioxide','Argon','Neon'],0),('What is an equator?',['Imaginary line around Earth','Mountain','River'],0),('Which organization promotes international cooperation?',['United Nations','Local bus stop','Sports shop'],0)])],
'Islamiyat': [
 ('Good Manners','Practice kindness, honesty, sharing and respect for others.',[
  ('Which is a kind action?',['Helping','Bullying','Hitting'],0),('When someone helps us we say?',['Thank you','Go away','Nothing'],0),('Which is honest?',['Telling truth','Lying','Cheating'],0),('What should we do with toys?',['Share fairly','Break them','Hide all'],0),('How should we speak to elders?',['Respectfully','Rudely','Loudly'],0),('Which is a good habit?',['Keeping clean','Throwing litter','Pushing'],0)]),
 ('Everyday Islamic Greetings','Learn respectful greetings, gratitude and good everyday habits.',[
  ('Muslim greeting is?',['Assalamu Alaikum','Good night only','Goodbye only'],0),('Reply to Assalamu Alaikum?',['Wa Alaikum Assalam','Hello again','Later'],0),('How do we express thanks to Allah?',['Alhamdulillah','Goodbye','Sorry'],0),('Before starting something good we say?',['Bismillah','Never mind','Later'],0),('How should we treat neighbors?',['With kindness','With rudeness','Ignore always'],0),('Why wash hands before eating?',['Cleanliness','To make noise','To waste water'],0)]),
 ('Pillars of Islam','An introduction to five pillars of Islam.',[
  ('How many pillars of Islam?',['5','3','7'],0),('Salah refers to?',['Prayer','Travel','Food'],0),('Sawm refers to?',['Fasting','Shopping','Sleeping'],0),('Zakat relates to?',['Giving to eligible people','Buying toys','Playing games'],0),('Hajj is associated with?',['Makkah','London','Paris'],0),('Shahadah is the?',['Declaration of faith','Type of food','Book title'],0)]),
 ('Prophets and Values','Learn key names and values taught in Islam.',[
  ('Which prophet built the Ark?',['Nuh (AS)','Musa (AS)','Yusuf (AS)'],0),('Which prophet is associated with the staff miracle?',['Musa (AS)','Nuh (AS)','Ibrahim (AS)'],0),('Which prophet is regarded as the final prophet in Islam?',['Muhammad ﷺ','Adam (AS)','Yusuf (AS)'],0),('What is a valued quality?',['Patience','Cruelty','Dishonesty'],0),('Which is encouraged?',['Charity','Bullying','Waste'],0),('How should we treat animals?',['Kindly','Cruelly','Carelessly'],0)]),
 ('Worship and Community','Introduce prayer, Ramadan and community responsibility.',[
  ('How many daily obligatory prayers?',['5','4','6'],0),('Muslims fast in which month?',['Ramadan','Shawwal only','Muharram only'],0),('Prayer direction is toward?',['Kaaba','Any building','A tree'],0),('Where is the Kaaba?',['Makkah','Madinah','Cairo'],0),('What helps community?',['Giving and helping','Being selfish','Littering'],0),('What should we avoid?',['Wastefulness','Honesty','Kindness'],0)]),
 ('Islamic History and Ethics','Practice ethical decision-making and key Islamic history basics.',[
  ('Hijrah refers to migration to?',['Madinah','Damascus','Cairo'],0),('Which holy book is central to Islam?',['Quran','Dictionary','Atlas'],0),('What does amanah relate to?',['Trust','Noise','Haste'],0),('Which is a good use of resources?',['Avoid waste','Waste food','Waste water'],0),('What strengthens relationships?',['Forgiveness','Revenge','Dishonesty'],0),('What is encouraged when making decisions?',['Justice','Favoritism','Cruelty'],0)]),
 ('Faith and Responsibility','Review beliefs, community and respectful conduct.',[
  ('Islam teaches how many pillars of faith (iman)?',['6','5','3'],0),('Which angel is associated with revelation?',['Jibril (AS)','Mikail (AS)','Israfil (AS)'],0),('What is a central value?',['Justice','Oppression','Arrogance'],0),('What should accompany knowledge?',['Responsible action','Arrogance','Rudeness'],0),('Which is a charitable attitude?',['Helping people in need','Ignoring need','Mocking others'],0),('What is respectful disagreement?',['Listen and speak kindly','Insult others','Shout always'],0)])],
'Computer': [
 ('Meet the Computer','Computers help us learn, draw and play. Ask an adult before using apps.',[
  ('Which device has a screen?',['Laptop','Spoon','Cup'],0),('What helps us type?',['Keyboard','Ball','Plate'],0),('Which moves the cursor?',['Mouse','Book','Pencil'],0),('What shows pictures?',['Monitor','Shoes','Hat'],0),('Should we share passwords with strangers?',['No','Yes','Always'],0),('Who can help if a website feels strange?',['Trusted adult','Unknown stranger','Nobody'],0)]),
 ('Computer Parts','Learn the main parts of a computer and safe usage.',[
  ('Which plays sound?',['Speaker','Keyboard','Mouse'],0),('Which is used to click?',['Mouse','Printer paper','Screen cleaner'],0),('Which displays pictures?',['Monitor','Keyboard','Cable'],0),('Which makes printed pages?',['Printer','Speaker','Microphone'],0),('What should we do with food near computers?',['Keep it away','Spill it','Hide in keyboard'],0),('A tablet often uses what input?',['Touchscreen','Only pedals','Steering wheel'],0)]),
 ('Files and Folders','Organize digital work using files, folders and simple tools.',[
  ('Where do we organize files?',['Folders','Shoes','Cups'],0),('Which creates pictures?',['Drawing app','Calculator only','Clock'],0),('What does Save do?',['Stores work','Deletes everything','Turns off screen'],0),('Which device captures a photo?',['Camera','Keyboard','Speaker'],0),('Which is used to record a voice?',['Microphone','Monitor','Mouse'],0),('Why use a strong password?',['Protect accounts','Make noise','Increase screen size'],0)]),
 ('Internet Basics','The internet connects devices and information; stay safe online.',[
  ('What opens websites?',['Web browser','Paintbrush','Stapler'],0),('What is a URL?',['Web address','Keyboard key','Battery'],0),('What should you do with unknown links?',['Ask an adult','Click immediately','Share widely'],0),('Which is personal information?',['Home address','Favorite shape','Weather'],0),('What do search engines help find?',['Information','Shoes physically','Electricity'],0),('Should children talk to strangers online?',['No, tell a trusted adult','Yes, always','Share address'],0)]),
 ('Algorithms and Patterns','Algorithms are sequences of clear steps.',[
  ('An algorithm is a set of?',['Steps','Colors','Sounds'],0),('Which is an input?',['Keyboard typing','Printed output','Speaker sound'],0),('Which is an output?',['Screen message','Mouse movement','Key press'],0),('Repeating actions is called a?',['Loop','Folder','Pixel'],0),('Which is a condition?',['If it rains, take umbrella','Three chairs','Red apple'],0),('Why debug code?',['Fix mistakes','Add noise','Hide work'],0)]),
 ('Digital Literacy','Build healthy and responsible digital habits.',[
  ('What is a phishing message?',['Attempt to trick you','A printer type','A game reward'],0),('What protects accounts?',['Unique password','Sharing password','Posting password'],0),('What is a backup?',['Extra copy of data','Deleted file','Virus'],0),('What does copyright protect?',['Creative work','Keyboard size','Screen color'],0),('Should we verify online information?',['Yes','No','Never'],0),('What helps eye comfort?',['Regular breaks','No breaks','Dark room always'],0)]),
 ('Coding Concepts','Explore variables, functions, decisions and digital citizenship.',[
  ('What stores a value in code?',['Variable','Speaker','Printer'],0),('What reuses instructions?',['Function','Wallpaper','Cursor'],0),('What is a bug?',['Error in program','Small monitor','Save icon'],0),('Which statement makes a choice?',['If','Print only','Color'],0),('What does a loop do?',['Repeats actions','Shuts all apps','Draws once'],0),('What should programmers do with user data?',['Protect privacy','Publish secrets','Ignore security'],0)])]
}

EMOJIS = {'English':'🔤','Mathematics':'🧮','Urdu':'🌙','Science':'🔬','General Knowledge':'🌍','Islamiyat':'🤲','Computer':'💻'}

def starter_lessons():
    for subject, entries in BANK.items():
        for grade, (title, explanation, questions) in zip(GRADES, entries):
            yield grade,subject,title,explanation,EMOJIS[subject],[q(*item) for item in questions]
