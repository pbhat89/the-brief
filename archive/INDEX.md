# Archive Index

Append-only log of headlines sent in past briefs. The daily routine writes to
this file at the end of Stage 4 (Publish & Archive), and reads from it at the
start of Stage 0 (Load history) to build the dedup EXCLUDE set covering the
last 2-3 days.

## Format

One item per line, tab-separated, four fields:

```
date<TAB>headline<TAB>short-hash<TAB>key-entities
```

- `date` — ISO date the item was sent, e.g. `2026-06-05`.
- `headline` — the headline as it appeared in the brief.
- `short-hash` — an 8-character hash derived from the canonical story (used
  for fast exact-match dedup).
- `key-entities` — comma-separated named entities (people, orgs, places,
  tickers) used for fuzzy dedup. See `dedup.md` for the matching rules.

## Example format

```
2026-06-03	Fed holds rates steady, signals one cut by year-end	a1b2c3d4	Federal Reserve, Jerome Powell, FOMC, USD
2026-06-03	Singapore GDP revised up to 3.4% on services strength	e5f6a7b8	MAS, MTI, Singapore, SGD
2026-06-04	OpenAI announces new enterprise tier with on-prem option	9c0d1e2f	OpenAI, Sam Altman, Microsoft, enterprise AI
```

The rows above are illustrative only. The real log begins below this line and
is empty until the first run.

---
2026-06-05	Singapore Airlines in talks to order at least 50 wide-body jets	d99e2ba0	Singapore Airlines,Airbus,Boeing,wide-body jet order
2026-06-05	221 people under police investigation in Singapore over S$9 million in scams	79929900	Singapore Police Force,scams,money mules
2026-06-05	Southwest monsoon reaches Kerala, three days later than normal	843571d4	IMD,Kerala,southwest monsoon
2026-06-05	RBI holds key interest rate at 5.25% for a third straight meeting	19ca801d	RBI,Sanjay Malhotra,repo rate,monetary policy
2026-06-05	Five Eyes alliance warns China is recruiting through fake job ads	e1a5b150	Five Eyes,China,espionage,LinkedIn
2026-06-05	Israel and Lebanon agree to a conditional ceasefire; Hezbollah rejects it	0bc272de	Israel,Lebanon,Hezbollah,ceasefire
2026-06-05	US House passes Russia sanctions and Ukraine aid bill, defying Trump	f8d1aff1	US House,Russia sanctions,Ukraine aid,Trump
2026-06-05	Apple's WWDC opens June 8 with a Gemini-powered Siri revamp expected	171b7b7b	Apple,WWDC,Siri,Google Gemini
2026-06-05	Broadcom shares drop despite surging AI chip revenue	76ec0b52	Broadcom,Hock Tan,AI chips,earnings
2026-06-05	Andreeva beats Kostyuk to reach her first French Open final	c7579b94	Mirra Andreeva,Marta Kostyuk,French Open,Roland Garros
2026-06-05	French Open men's title left wide open after Sinner, Alcaraz and Djokovic exits	5296841a	French Open,Alexander Zverev,Jannik Sinner,Carlos Alcaraz
2026-06-06	Singapore braces for warmer, drier weather and higher haze risk as El Niño develops	f4113d98	Meteorological Service Singapore,El Nino,haze
2026-06-06	HDB launches June BTO exercise with 6,900 flats as resale prices dip for first time since 2019	3a8d5061	HDB,BTO,resale prices
2026-06-06	India's economy grows 7.8% in Q4 and 7.7% for FY26, keeping its fastest-growing major economy tag	4aa46b26	India GDP,FY26,MoSPI
2026-06-06	Modi meets Venezuela's Delcy Rodríguez as India expands Venezuelan oil imports	d98bba0b	Modi,Delcy Rodriguez,Venezuela,oil
2026-06-06	Update: Southwest monsoon advances into Karnataka, Tamil Nadu and Goa	37824284	IMD,southwest monsoon,Karnataka,Tamil Nadu,Goa
2026-06-06	Government sets Parliament's monsoon session for July 21 to August 12	e96d57e5	Kiren Rijiju,Parliament,monsoon session,Operation Sindoor
2026-06-06	Update: Israel keeps striking southern Lebanon despite US-brokered deal, killing at least five	16eeb650	Israel,Lebanon,Hezbollah,ceasefire
2026-06-06	US House votes 215-208 to limit Trump's war powers on Iran	f04e6801	US House,Iran war,war powers resolution,Trump
2026-06-06	South Korea's ruling party sweeps local elections but loses Seoul	7cc167d5	South Korea,Democratic Party,local elections,Oh Se-hoon
2026-06-06	EU unveils tech sovereignty package to cut reliance on US and Chinese technology	47bdf16b	European Commission,tech sovereignty,Chips Act,cloud AI
2026-06-06	EU regulators put Nvidia's AI-chip business under antitrust scrutiny	3369d0e7	European Union,Nvidia,antitrust,AI chips
2026-06-06	US adds 172,000 jobs in May as unemployment holds at 4.3%	99510f9f	US jobs report,nonfarm payrolls,unemployment,Federal Reserve
2026-06-06	Brent crude hovers near $95 as Strait of Hormuz crisis keeps oil elevated	99fb2907	Brent crude,oil prices,Strait of Hormuz,Iran
2026-06-06	England set New Zealand 254 to win first Test as Black Caps reach 36-3	f862df0f	England,New Zealand,Lord's,Test cricket
2026-06-06	Update: Zverev reaches French Open final and will face Cobolli	9c5d03b7	French Open,Alexander Zverev,Flavio Cobolli,Roland Garros
2026-06-06	Hamilton leads Ferrari 1-2 in Monaco practice ahead of qualifying	7f5af0da	Monaco Grand Prix,Lewis Hamilton,Ferrari,Charles Leclerc
2026-06-07	Workers' Party calls special conference on Pritam Singh's future after court upholds conviction	d7805e18	Workers' Party,Pritam Singh,cadres conference,conviction
2026-06-07	Singapore to ease hotel restrictions at Boat Quay and Beach Road heritage precincts	38f59ace	Chee Hong Tat,Boat Quay,Beach Road,hotels
2026-06-07	Another Singaporean arrested in Malaysia over Cambodia-based scam syndicate	d64c8189	Singapore Police Force,Malaysia,Cambodia,scam syndicate
2026-06-07	Singapore to screen 2026 World Cup matches free at community venues	d2a74d8c	Singapore,FIFA World Cup,community clubs,free screenings
2026-06-07	India designates Surha Tal in Uttar Pradesh as its 100th Ramsar wetland site	a77dffdd	Surha Tal,Ramsar site,Uttar Pradesh,Narendra Modi
2026-06-07	Oil India reports second Andaman offshore gas discovery	df3a72ab	Oil India,Andaman,Vijayapuram-3,Hardeep Singh Puri
2026-06-07	Indian rupee hovers near record low against the dollar as markets stay cautious	fd789d6e	Indian rupee,US dollar,Sensex,Nifty
2026-06-07	India hosts 11th BRICS foreign-policy planning dialogue in New Delhi	37d178c3	India,BRICS,New Delhi,foreign policy dialogue
2026-06-07	Russia and Ukraine trade large overnight strikes; Kyiv hits St Petersburg	619fa17c	Russia,Ukraine,St Petersburg,Zelensky,Putin
2026-06-07	Peru holds presidential election this weekend in a polarized, tight race	68c85944	Peru,presidential election,Latin America
2026-06-07	Suno raises $400 million at a $5.4 billion valuation despite copyright lawsuits	06f4703a	Suno,AI music,Series D,copyright lawsuits
2026-06-07	Coralogix raises $200 million to monitor AI agents	9b75ecf1	Coralogix,AI agents,observability,funding
2026-06-07	Update: Apple's WWDC opens Monday with its biggest Siri overhaul in years	3b1aacec	Apple,WWDC,Siri,iOS 27
2026-06-07	Wall Street's chip stocks tumble, wiping over $1 trillion in value	d76de09a	Nasdaq,S&P 500,chip stocks,Nvidia
2026-06-07	Amazon unveils new warehouse robot as Big Tech AI layoffs continue	ed973a0e	Amazon,warehouse robot,Tye Brady,AI layoffs
2026-06-07	SpaceX sets fixed $135-a-share price in $75 billion IPO	4e1c1b03	SpaceX,IPO,Nasdaq,Elon Musk
2026-06-07	Update: Andreeva wins French Open for her first Grand Slam title	30ddcbf5	Mirra Andreeva,Maja Chwalinska,French Open,Roland Garros
2026-06-07	Update: Antonelli takes maiden Monaco pole as Leclerc crashes	522aa87f	Kimi Antonelli,Monaco Grand Prix,Max Verstappen,Charles Leclerc
2026-06-07	Update: England close on Lord's win as Robinson rips through New Zealand	fcab1a25	England,New Zealand,Lord's,Ollie Robinson
2026-06-08	Luxury superyacht Eagle Wings III partially sinks after fire at Sentosa Cove marina	684c564b	eagle wings iii,sentosa cove,one15 marina,scdf,yacht fire
2026-06-08	Singapore orders platforms to block inflammatory online posts targeting its Indian community	84078493	singapore,josephine teo,indian community,social media,police directions
2026-06-08	Singaporean, 20, dies in Malaysia crash days before his NS passing-out parade	fbd1fb3b	singaporean,malaysia,north-south expressway,national service,road accident
2026-06-08	Pashinyan's Civil Contract heads for big Armenia election win in early results	090463f1	nikol pashinyan,civil contract,armenia,parliamentary election
2026-06-08	Israel keeps up Gaza strikes as ceasefire talks resume in Cairo	e8b1c6f3	israel,gaza,hamas,cairo talks,ceasefire
2026-06-08	Drone strike on a North Kordofan market kills at least 11 in Sudan	25172bbd	sudan,north kordofan,abu zaeima,drone strike,rsf
2026-06-08	Update: WWDC opens with a Gemini-powered Siri overhaul expected	64fe0ef7	apple,wwdc,siri,google gemini,tim cook
2026-06-08	OPEC+ agrees a fourth output-target increase since the Strait of Hormuz closure	7f3666ee	opec+,oil output,strait of hormuz,brent crude
2026-06-08	Update: Zverev beats Cobolli in five sets for his first Grand Slam title at the French Open	78312969	alexander zverev,flavio cobolli,french open,roland garros
2026-06-08	Update: Antonelli wins chaotic Monaco Grand Prix as Verstappen retires on lap one	89e06c88	kimi antonelli,monaco grand prix,max verstappen,lewis hamilton
2026-06-08	Update: England beat New Zealand by 115 runs to win the first Test at Lord's	6e167120	england,new zealand,lords,ollie robinson,test cricket
2026-06-08	Shreyas Iyer named India's new T20I captain for the England and Ireland tour	d8f5f8ea	shreyas iyer,india t20i,england tour,vaibhav sooryavanshi
2026-06-09	PM Wong says AI can be a game changer for labour-short Singapore	d37791ee	lawrence wong,artificial intelligence,productivity,singapore
2026-06-09	Singapore eyes deeper ASEAN connectivity amid new US-China dynamic, says PM Wong	d246dc2a	singapore,asean,us-china,lawrence wong
2026-06-09	Sensex falls 719 points as Iran-Israel strikes spike crude and rattle markets	c2c7f543	sensex,nifty,iran-israel,crude oil
2026-06-09	India and US likely to sign first tranche of trade deal by July, says Goyal	820fa702	india,united states,trade deal,piyush goyal
2026-06-09	Delhi swelters as heat index tops 45 degrees with monsoon weeks away	5137b0af	delhi,heatwave,imd,monsoon
2026-06-09	Magnitude 7.8 earthquake strikes southern Philippines, killing at least 32	482aaf7f	philippines,earthquake,sarangani,tsunami
2026-06-09	Israel and Iran halt strikes after trading missile fire, leaving ceasefire on edge	a154a348	israel,iran,missile strikes,ceasefire
2026-06-09	Update: Peru's presidential runoff too close to call as Fujimori holds narrow lead	c2a14557	peru,presidential runoff,keiko fujimori,roberto sanchez
2026-06-09	Update: Apple unveils overhauled, Gemini-powered Siri and iOS 27 at WWDC	e2036b69	apple,wwdc,siri,ios 27,google gemini
2026-06-09	Apple stakes its AI future on Google's Gemini in multi-year Siri deal	7d0af034	apple,google gemini,siri,artificial intelligence
2026-06-09	Update: Wall Street rebounds as chip stocks recover and Micron jumps 10%	fdb3a42c	wall street,nasdaq,s&p 500,micron
2026-06-09	Brent crude whipsaws on Iran-Israel strikes, spiking above $97 before easing	d0e6b668	brent crude,oil,strait of hormuz,iran-israel
2026-06-09	Update: SpaceX sets June 12 Nasdaq debut as IPO roadshow gets under way	37a1772a	spacex,ipo,nasdaq,elon musk
2026-06-09	Update: MCC apologises for Lord's pitch after England's 115-run win over New Zealand	ac465d5e	mcc,lords,england,new zealand,ollie robinson
2026-06-09	Grass-court season opens at Queen's with Rybakina the top seed	09abf447	queens club,grass season,elena rybakina,wta
2026-06-10	HDB to offer about 6,900 BTO flats in June, 2,520 with sub-three-year waits	88a7b696	hdb,bto,sembawang,ang mo kio,housing
2026-06-10	Singapore steps up enforcement against illegal gambling during the World Cup	2399aff1	singapore,illegal gambling,world cup,mha,enforcement
2026-06-10	Wong says Singapore far from its 6.9 million population cap as fertility hits record low	8cf45818	lawrence wong,population,fertility,singapore,disinformation
2026-06-10	Singapore to pursue free trade deal with East African bloc, its first in Africa	498e92c0	singapore,east african community,free trade agreement,africa
2026-06-10	Update: Sensex rebounds 394 points as RBI forex measures lift bank stocks	d20eaa82	sensex,nifty,rbi,forex swap,psu banks
2026-06-10	IMD issues red alert for coastal Karnataka as monsoon strengthens over the south	bd3219f8	imd,karnataka,monsoon,red alert,kerala
2026-06-10	Air India Delhi-Bengaluru flight suffers tail strike on landing; DGCA opens probe	6e22b5b2	air india,bengaluru,tail strike,dgca,a321
2026-06-10	Studds shares jump as West Bengal helmet crackdown drives record May sales	7fde034a	studds,west bengal,helmet,shares
2026-06-10	Update: Israel strikes Lebanese port of Tyre after ordering the whole city to evacuate	ae67fb95	israel,lebanon,tyre,iran,evacuation
2026-06-10	Update: Peru runoff flips as leftist Roberto Sanchez edges ahead of Fujimori	8afe635c	peru,roberto sanchez,keiko fujimori,runoff
2026-06-10	Xi and Kim pledge closer ties at first China-North Korea summit in seven years	4530efe1	xi jinping,kim jong un,north korea,china,pyongyang
2026-06-10	Israeli strikes kill at least nine in Gaza as factions resume Cairo ceasefire talks	7ad475a1	israel,gaza,hamas,cairo,ceasefire
2026-06-10	Anthropic releases Claude Fable 5, opening its Mythos-class model to the public	4413c287	anthropic,claude fable 5,mythos,ai model
2026-06-10	OpenAI confirms confidential filing for a US stock market listing	fbbac8de	openai,ipo,sec,chatgpt
2026-06-10	Signal warns UK device-scanning plan would put everyone's privacy at risk	14290ff6	signal,uk,device scanning,privacy,starmer
2026-06-10	US adds Alibaba, Baidu and BYD to its list of Chinese military companies	ca37536d	united states,alibaba,baidu,byd,chinese military companies
2026-06-10	Update: Wall Street slips as chip rally fizzles and the S&P 500 eases	919a1b19	wall street,s&p 500,nasdaq,dow,chip stocks
2026-06-10	Update: SpaceX prices its IPO at $135 a share ahead of June 12 debut	ae7cbc3d	spacex,ipo,nasdaq,elon musk
2026-06-10	UK competition watchdog opens probe into Paramount's $110bn Warner Bros deal	b5a7c2ef	paramount,warner bros,cma,takeover
2026-06-10	Gold holds above $4,300 an ounce as geopolitical risk sustains safe-haven demand	acafc071	gold,safe haven,dollar,prices
2026-06-10	Bangladesh beat Australia by 86 runs in first ODI at Mirpur	2142f865	bangladesh,australia,odi,mosaddek hossain,mirpur
2026-06-10	Raducanu routs Blinkova 6-0, 6-3 in her Queen's opener	fc947d3f	raducanu,blinkova,queens,wta
2026-06-10	Mannarino ends Diallo's 's-Hertogenbosch title defence in three sets	09cd3a95	mannarino,diallo,s-hertogenbosch,libema open
2026-06-10	Antonelli wins chaotic Monaco Grand Prix to extend his title lead	4b4b2c81	antonelli,hamilton,verstappen,monaco,f1
2026-06-10	Pliskova fights back to beat Nottingham champion Kessler at Queen's	73f04546	pliskova,kessler,queens,wta
2026-06-11	Driver who staged 73 traffic accidents for insurance payouts jailed 32 weeks	d124ae7d	singapore,staged accidents,insurance fraud,court,jail
2026-06-11	Singapore lines up free World Cup screenings as Mediacorp airs 28 matches free-to-air	33b4dffb	singapore,world cup,mediacorp,community clubs,screenings
2026-06-11	Economists cut Singapore's 2026 growth forecast to 1.7% as Gulf conflict bites	f7c09369	singapore,mas survey,growth forecast,monetary policy
2026-06-11	Modi becomes India's longest-serving elected PM as NDA marks 12 years in power	0c023d36	narendra modi,nda,nehru,longest-serving pm,congress
2026-06-11	Fitch cuts India's FY27 growth forecast to 6.4%, citing the US-Iran war	278d7573	fitch,india,gdp forecast,us-iran war
2026-06-11	Monsoon advances into the northeast as Delhi braces for a wet spell	40815a28	monsoon,imd,northeast,delhi,western disturbance
2026-06-11	RBI deputy governor Swaminathan reappointed for two more years	9c967b78	rbi,swaminathan janakiraman,deputy governor,reappointment
2026-06-11	Update: US strikes Iran after Apache downed in Hormuz; Iran hits Gulf bases	1c880c45	united states,iran,strait of hormuz,gulf bases,apache
2026-06-11	Update: Israel keeps up Lebanon strikes, says its campaign is far from over	c4abe78f	israel,lebanon,tyre,katz,hezbollah
2026-06-11	UK leaders urge calm after Belfast stabbing sparks anti-immigration protests	5f8395cf	united kingdom,belfast,northern ireland,protests,stabbing
2026-06-11	Largest-ever World Cup kicks off as Mexico hosts South Africa	fcf274e1	fifa world cup,mexico,south africa,north america
2026-06-11	Update: Apple shares slide after WWDC as Wall Street splits on the Gemini-Siri bet	3d1a8030	apple,wwdc,siri,google gemini,shares
2026-06-11	Microsoft ships its largest-ever Patch Tuesday, fixing about 200 flaws	846def98	microsoft,patch tuesday,zero-day,windows,security
2026-06-11	Nvidia races to meet surging China demand for its H200 AI chips	05eb4919	nvidia,h200,china,tsmc,ai chips
2026-06-11	US inflation jumps to 4.2%, a three-year high, as energy costs surge	4cf3794b	united states,cpi,inflation,energy,federal reserve
2026-06-11	Update: Wall Street tumbles as hot CPI and US-Iran strikes hit stocks	7e9af41b	wall street,dow,nasdaq,s&p 500,cpi
2026-06-11	Oil swings as US-Iran strikes rattle the Strait of Hormuz	172b824f	brent crude,oil,strait of hormuz,us-iran,inventories
2026-06-11	Update: SpaceX IPO four times oversubscribed before its June 12 debut	3627055e	spacex,ipo,nasdaq,elon musk
2026-06-11	Maybank says it has funnelled $4.9 billion into the Johor-Singapore economic zone	82c3f833	maybank,johor-singapore sez,investment,family offices
2026-06-11	India lose Kohli and Hardik Pandya to injury before Afghanistan ODIs	974e3282	india,virat kohli,hardik pandya,afghanistan,injury
2026-06-11	India thrash Afghanistan by an innings and 300 runs in one-off Test	d97cb0c2	india,afghanistan,test,shubman gill,manav suthar
2026-06-11	Defending champion Tatjana Maria beats Sakkari at Queen's	ebc948ba	tatjana maria,maria sakkari,queens,wta
2026-06-11	Eala and Cirstea also reach the Queen's second round	c8d7fb91	alexandra eala,sorana cirstea,queens,wta
2026-06-12	Singapore brings forward S$500 CDC vouchers to June 11 as Gulf conflict lifts costs	90ea7f47	singapore,cdc vouchers,cost of living,fuel prices
2026-06-12	Workers told to reapply for overseas roles are still retrenched, MOM and NTUC say	54223fed	singapore,retrenchment,mom,ntuc,jobs
2026-06-12	Singapore police warn of resurgent concert-ticket and impersonation scams	9173956c	singapore,police,scams,ica,impersonation
2026-06-12	Singapore Airlines keeps Dubai route suspended as Gulf airspace stays volatile	a9c6a64a	singapore airlines,dubai,gulf conflict,airspace,scoot
2026-06-12	Three Indian seafarers killed in US strike on tanker off Oman; New Delhi summons US envoy	15211ac0	india,seafarers,mt settebello,oman,united states
2026-06-12	Naga body enforces 24-hour Manipur shutdown after six abducted villagers found dead	f80546a7	manipur,united naga council,shutdown,kangpokpi,kuki
2026-06-12	India's forex reserves rise to $682.32 billion in latest RBI data	771c1dd3	india,forex reserves,rbi,rupee
2026-06-12	West Bengal becomes 36th state to roll out Ayushman Bharat health scheme	a6bf9b17	west bengal,ayushman bharat,pm-jay,health insurance
2026-06-12	Update: Trump calls off Iran strikes, says ceasefire-and-Hormuz deal is close	ab897bb5	united states,iran,trump,strait of hormuz,ceasefire
2026-06-12	Update: Northern Ireland sees second night of unrest after Belfast stabbing	87e3212c	northern ireland,belfast,unrest,stabbing,protests
2026-06-12	Saudi Arabia lifts five-year ban on Lebanese imports in sign of thaw	00408ed8	saudi arabia,lebanon,import ban,mohammed bin salman,aoun
2026-06-12	China bars Philippine defence chief Teodoro over South China Sea remarks	503d73f2	china,philippines,teodoro,south china sea,sanctions
2026-06-12	Largest-ever World Cup opens as hosts Mexico beat South Africa 2-0	81b2de4b	fifa world cup,mexico,south africa,north america
2026-06-12	EU orders Meta to open WhatsApp to rival AI assistants	2a60cb54	european union,meta,whatsapp,digital markets act,ai
2026-06-12	OpenAI teams with Oracle to sell its models and Codex through OCI	3922a354	openai,oracle,oci,codex,cloud
2026-06-12	Qualcomm strikes ByteDance deal to supply AI data-centre chips	c2328726	qualcomm,bytedance,ai chips,data centre,doubao
2026-06-12	OpenAI says Chinese operations used ChatGPT for covert influence content	de9a5346	openai,chatgpt,china,influence operations,disinformation
2026-06-12	Update: Wall Street surges as Trump cancels Iran strikes	726f32ab	wall street,s&p 500,dow,nasdaq,iran
2026-06-12	Oracle shares slide about 8% on plan to raise $20 billion for AI build-out	7dfd9278	oracle,shares,ai capex,fundraising
2026-06-12	Update: Oil tumbles as Trump cancels Iran strikes and touts Hormuz deal	09b5e7cd	oil,brent crude,strait of hormuz,iran,us
2026-06-12	US wholesale prices post biggest annual jump in over three years	7a8aabc4	united states,producer prices,ppi,inflation,federal reserve
2026-06-12	Bangladesh beat Australia to clinch their first ODI series win over Australia	ed4d79d8	bangladesh,australia,odi series,mirpur,cricket
2026-06-12	Iva Jovic upsets Eala to reach her first Queen's quarter-final	e9576f78	iva jovic,alexandra eala,queens,wta,tennis
2026-06-12	Pliskova reaches Queen's quarter-finals after Mboko retires	1a45deca	karolina pliskova,victoria mboko,queens,wta,tennis
2026-06-12	Anisimova advances to the Queen's quarter-finals	812067ca	amanda anisimova,laura siegemund,queens,wta,tennis
2026-06-13	Three dead after supply boat sinks off Pasir Panjang Terminal in collision	0f3b10b0	singapore,pasir panjang,supply boat,collision,mpa
2026-06-13	Heavy downpours end Singapore's warm spell, bringing 2026's coolest day	7f5a0824	singapore,weather,rain,temperature
2026-06-13	PM Wong to deliver National Day Rally on Aug 23	2f33ba80	lawrence wong,national day rally,singapore
2026-06-13	India marks one year since the Air India AI-171 crash that killed 260	9d17a5e5	air india,ai-171,ahmedabad,crash,anniversary
2026-06-13	IMD issues red alert for Delhi as storms and heavy rain sweep 15 states	ea18b7e4	imd,delhi,red alert,rain,kerala
2026-06-13	FSSAI issues notices to Nestle, KFC and Flipkart over hygiene complaints	8670371e	fssai,nestle,kfc,flipkart,food safety
2026-06-13	Indian shares slip and rupee weakens as Middle East tensions and outflows weigh	a6f2f89e	sensex,rupee,fpi outflows,middle east,crude
2026-06-13	Update: Pakistan says final text of US-Iran deal reached as Trump eyes weekend signing	f4f77a71	united states,iran,pakistan,trump,ceasefire
2026-06-13	China arrests US scholar Min Zin on suspicion of espionage	cfc3c454	china,min zin,espionage,myanmar,united states
2026-06-13	Canada earn first World Cup point in 1-1 draw with Bosnia as USA open at home	b47affa8	fifa world cup,canada,bosnia,united states,larin
2026-06-13	Al-Qaeda-linked JNIM blockade pushes Mali's junta into deepening crisis	009303b3	mali,jnim,bamako,goita,blockade
2026-06-13	OpenAI acquires cloud startup Ona to power long-running Codex agents	101feb2e	openai,ona,gitpod,codex,acquisition
2026-06-13	Jeff Bezos's Prometheus raises $12 billion at a $41 billion valuation	033ab4c3	prometheus,jeff bezos,funding,physical ai,vik bajaj
2026-06-13	Datadog veterans launch AI coding startup Niteshift with $7 million seed	615ceb37	niteshift,datadog,ai coding,greylock,seed
2026-06-13	Jedify raises $24 million to give AI agents business context	a46ac5a5	jedify,norwest,ai agents,series a,enterprise
2026-06-13	Update: SpaceX soars 19% in record stock-market debut	86225484	spacex,ipo,spcx,nasdaq,elon musk
2026-06-13	Update: Wall Street rises a second day on US-Iran peace hopes	dfa3dfd6	wall street,s&p 500,dow,nasdaq,iran
2026-06-13	US Justice Department clears Paramount's $110 billion Warner Bros takeover	5b3ebd2d	paramount,warner bros,justice department,antitrust,merger
2026-06-13	Update: Oil extends slide toward $85 as US-Iran deal nears Hormuz reopening	63a12b0d	oil,crude,strait of hormuz,iran,us
2026-06-13	Boulter stuns top seed Rybakina to reach Queen's semi-finals	92d2bc8b	katie boulter,elena rybakina,queens,wta,tennis
2026-06-13	Teenager Jovic beats Anisimova for first top-five win at Queen's	3828ee1a	iva jovic,amanda anisimova,queens,wta,tennis
2026-06-13	Vekic downs Pliskova to complete Queen's semi-final lineup	fd14e9d3	donna vekic,karolina pliskova,queens,wta,tennis
2026-06-13	India begin first-ever ODI series against Afghanistan in Dharamsala	36c41ac8	india,afghanistan,odi series,dharamsala,cricket
2026-06-14	Six taken to hospital, about 120 evacuated after Sengkang HDB fire	03a16f6a	singapore,sengkang,hdb fire,evacuation
2026-06-14	About 80 firefighters battle chemical-waste warehouse blaze in Tuas	050ce2f2	singapore,tuas,warehouse fire,scdf
2026-06-14	HDB June BTO launch offers about 6,900 flats, including first Bishan project in 40 years	ef76cba2	singapore,hdb,bto,bishan
2026-06-14	Singapore's IMDA and Microsoft sign pact on safe access to frontier AI models	c8c4b04d	singapore,imda,microsoft,ai
2026-06-14	First batch of nine women officers commissioned at IMA in Dehradun	6c1768ff	india,ima,women officers,murmu
2026-06-14	India's retail inflation rises to 3.93% in May as food and fuel costs climb	edfbaeca	india,cpi,inflation,rbi
2026-06-14	Supreme Court calls homemakers 'nation builders', sets ₹30,000 notional income	225566ff	supreme court,homemakers,notional income,compensation
2026-06-14	Noida International Airport set to open to commercial flights on June 15	d9dfc8a5	india,noida airport,jewar,indigo
2026-06-14	Update: Trump says US-Iran deal to be signed Sunday; Iran disputes timeline	c1ddd2b1	united states,iran,trump,hormuz,ceasefire
2026-06-14	US strike kills Tren de Aragua gang leader 'Niño Guerrero', Trump says	e4dcc193	united states,venezuela,tren de aragua,nino guerrero
2026-06-14	Brazil held to 1-1 draw by Morocco at the World Cup	15071792	world cup,brazil,morocco,vinicius
2026-06-14	Qatar earn first-ever World Cup point in 1-1 draw with Switzerland	34f76634	world cup,qatar,switzerland,khoukhi
2026-06-14	Pope Leo XIV's plane grounded in Tenerife as Spain's king lends his jet	271eeb06	pope leo xiv,spain,tenerife,felipe vi
2026-06-14	US orders Anthropic to curb foreign access to its top AI models	366aaace	anthropic,us commerce department,ai models,export controls
2026-06-14	Nvidia pitches new Vera CPUs to Chinese clients as H200 sales stay frozen	92055ba9	nvidia,vera cpu,china,h200
2026-06-14	Coinbase debuts AI agents that can trade crypto and pay for research	90923681	coinbase,ai agents,crypto,x402
2026-06-14	Robinhood reports record traffic after SpaceX market debut	fbcf09d7	robinhood,spacex,trading,outage
2026-06-14	ECB raises rates for first time since 2023 to counter Iran-war inflation	2235ecb3	ecb,interest rates,inflation,iran war
2026-06-14	Bank of Japan's Ueda hospitalised, will miss June 15-16 policy meeting	ad0f083a	bank of japan,ueda,policy meeting,rate hike
2026-06-14	Gold slips below US$4,200, heading for a second straight weekly loss	c19e5c99	gold,commodities,us-iran,inflation
2026-06-14	Update: Oil caps about 6% weekly loss as US-Iran deal nears Hormuz reopening	89a5d426	oil,wti,strait of hormuz,iran
2026-06-14	India beat Afghanistan by 7 wickets in rain-hit 1st ODI	27b2404d	india,afghanistan,odi,gill,gurbaz
2026-06-14	Raducanu beats Jovic to reach her first grass-court final at Queen's	e1cd5b51	raducanu,jovic,queens,wta
2026-06-14	Russell wins Canadian GP sprint and takes pole for Sunday's race	7f9f0995	f1,canadian gp,russell,antonelli
2026-06-14	Shelton saves two match points to set up all-American Stuttgart final	25bfd804	shelton,fritz,stuttgart,atp
2026-06-15	URA to expand non-invasive utility detection after avoiding S$300m in costs	763b2a36	singapore,ura,underground utilities,chee hong tat
2026-06-15	Revised single family office framework takes effect in Singapore	2348a840	singapore,mas,single family office,framework
2026-06-15	NEA reports eight active dengue clusters as Singapore enters peak season	9d4d2bed	singapore,nea,dengue,clusters
2026-06-15	Singapore hosts World Dengue Day and 9th Asia Dengue Summit	bff099ea	singapore,world dengue day,asia dengue summit,health
2026-06-15	Telangana begins biggest electoral roll revision in over two decades	88e0e685	telangana,sir,electoral rolls,eci
2026-06-15	Gujarat unveils Industrial Policy 2026 with new ultra-mega investment tier	8a2ec741	gujarat,industrial policy,bhupendra patel
2026-06-15	India's wholesale inflation eases to 14-month low of 0.39% in May	74300d4d	india,wpi,inflation,wholesale prices
2026-06-15	Update: Commercial flights begin at Noida International Airport in Jewar	b765ac20	india,noida airport,jewar,indigo
2026-06-15	Update: Trump and Pakistan say US-Iran deal reached, signing set for June 19	fac36012	united states,iran,trump,pakistan,hormuz
2026-06-15	Orban re-elected Fidesz leader months after losing power in Hungary	f0d6bf9e	hungary,orban,fidesz,tisza
2026-06-15	Sweden scrambles Gripen jets to intercept Russian warplanes over Baltic	e93eb40e	sweden,russia,baltic,gripen
2026-06-15	Japan twice fight back to hold the Netherlands to a 2-2 World Cup draw	cd0e7068	world cup,japan,netherlands,kamada
2026-06-15	Scotland beat Haiti for first World Cup win in 36 years	0a680d7f	world cup,scotland,haiti,mcginn
2026-06-15	Coalition of 42 US state attorneys general subpoenas OpenAI	4c260324	openai,attorneys general,letitia james,subpoena
2026-06-15	KPMG withdraws agentic-AI report after firms dispute fabricated case studies	4437c804	kpmg,agentic ai,hallucination,report
2026-06-15	Anthropic's forced model shutdown fuels India's push for sovereign AI	99952ebc	anthropic,india,sovereign ai,tcs
2026-06-15	Warsh chairs his first Fed meeting with rates expected to hold	573b9d52	federal reserve,kevin warsh,interest rates,fomc
2026-06-15	Update: Bank of Japan meets with rate seen rising to 1% for first time since 1995	9fb27b0c	bank of japan,rate hike,ueda,himino
2026-06-15	Update: Oil set to extend losses as US-Iran deal nears Hormuz reopening	7e1f3fd7	oil,brent crude,strait of hormuz,iran
2026-06-15	Antonelli wins Canadian Grand Prix as Russell retires from the lead	b05fbe3a	f1,canadian gp,antonelli,russell
2026-06-15	Vekic overpowers Raducanu to win the Queen's Club title	ba70eba0	tennis,queens,vekic,raducanu
2026-06-15	Shelton beats Fritz for his first grass-court title in Stuttgart	fb42d5a8	tennis,stuttgart,shelton,fritz
2026-06-15	Australia win 3rd ODI by one wicket but Bangladesh take the series	2c5a4452	cricket,bangladesh,australia,connolly
2026-06-16	Singapore unveils OTC gold-clearing system and central-bank gold vaulting	06c42d1c	singapore,mas,sgx,gan kim yong,gold
2026-06-16	Sushil Sukumaran Nair appointed a Justice of Singapore's Court of Appeal	3e14deb9	singapore,court of appeal,sushil sukumaran nair,judiciary
2026-06-16	Most Singapore fresh graduates earn below their expected pay, MOM study finds	85edc31d	singapore,mom,graduates,salary
2026-06-16	Man, 28, jailed 8 years 9 months and caned for raping girl, 13, he met online	c29f105d	singapore,courts,rape,sentencing
2026-06-16	India's May trade deficit widens to $28.21 billion as record exports lag imports	d1d0fcca	india,trade deficit,exports,commerce ministry
2026-06-16	AAIB's final report on Air India AI-171 crash to come 'very soon', says minister	7f34eebc	india,aaib,air india,ai-171,ram mohan naidu
2026-06-16	Sensex jumps 736 points and the rupee firms as US-Iran deal sinks oil	b58c4f7d	india,sensex,nifty,rupee,us-iran
2026-06-16	Modi begins France visit, to join G7 outreach session at Evian	7b26220f	india,modi,g7,evian,macron
2026-06-16	IMD widens heavy-rain and thunderstorm alerts as monsoon advances across India	e2f472d1	india,imd,monsoon,weather
2026-06-16	Update: Trump says ships are moving through Hormuz as US-Iran signing set for Friday	b4530772	united states,iran,trump,hormuz,switzerland
2026-06-16	Russian strike sets historic Kyiv-Pechersk Lavra cathedral ablaze, killing at least 5	5f9f01da	russia,ukraine,kyiv pechersk lavra,zelensky
2026-06-16	G7 leaders open Evian summit and welcome the US-Iran deal	d926825b	g7,evian,macron,zelensky
2026-06-16	World Cup debutants Cape Verde hold Spain to a 0-0 draw	41dca315	world cup,spain,cape verde,vozinha
2026-06-16	Tunisia sack coach Sabri Lamouchi after 5-1 World Cup loss to Sweden	6ebf38b2	world cup,tunisia,sabri lamouchi,sweden
2026-06-16	Salesforce to acquire AI customer-service firm Fin for $3.6 billion	772704da	salesforce,fin,intercom,agentforce
2026-06-16	Nvidia sells $25 billion of bonds in its first debt offering since 2021	4431a666	nvidia,bonds,ai,debt
2026-06-16	UK to bar under-16s from social media, including TikTok and YouTube	8fd7f1fb	united kingdom,starmer,social media,tiktok
2026-06-16	SpaceX stock jumps 20% in its first full day of trading after record IPO	6504a358	spacex,ipo,nasdaq,stock
2026-06-16	Update: Bank of Japan set to raise rates to 1% today as Ueda misses meeting	bbe9e79d	bank of japan,ueda,himino,interest rates
2026-06-16	Nikkei 225 surges about 5% to a record high above 69,000	6813f6e1	nikkei,japan,equities,us-iran
2026-06-16	Wall Street rallies on US-Iran deal as S&P 500 climbs 1.65% and the Dow hits a record	078ae8ce	s&p 500,dow jones,wall street,us-iran
2026-06-16	Update: Oil slides further as US-Iran deal clears the way to reopen Hormuz	a7ae68a8	oil,crude,strait of hormuz,iran
2026-06-16	🏏 India beat Pakistan by 64 runs at the Women's T20 World Cup	c9b7ba5b	india,pakistan,women's t20 world cup,deepti sharma
2026-06-16	🏏 Bangladesh beat Netherlands by six wickets on the Dutch World Cup debut	0f236b18	bangladesh,netherlands,women's t20 world cup,ferdous
2026-06-16	🎾 Tiafoe upsets French Open finalist Cobolli in the Halle first round	b4310036	tennis,halle open,tiafoe,cobolli
2026-06-16	🏎️ Antonelli leads the F1 title race by 43 points as the season heads to Austria	b011016f	f1,antonelli,russell,austrian gp
