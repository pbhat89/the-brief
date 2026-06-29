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
2026-06-17	PM Wong to attend ASEAN-Russia summit in Kazan, first Russia trip since sanctions	65499b01	lawrence wong,kazan,asean-russia summit,putin,ukraine sanctions
2026-06-17	Singapore retrenchments rose to 3,830 in the first quarter, highest since Q3 2023	ee632061	singapore,mom,retrenchments,labour market
2026-06-17	Singapore to trial roadside electronic parking in August and phase out ERP gantries	a052b573	singapore,lta,erp 2,roadside parking,gantries
2026-06-17	Jesus Christ Superstar musical given Advisory 16 rating over religious sensitivities	22cc0e0e	singapore,imda,jesus christ superstar,advisory 16,religion
2026-06-17	HCLTech to buy 10.46% stake in Sarvam AI for 1,427 crore rupees	98b98d5a	hcltech,sarvam ai,axonwise,series b,sovereign ai
2026-06-17	Vedanta's four demerged units begin trading, completing five-way split	12eaa8e6	vedanta,anil agarwal,demerger,nse,listing
2026-06-17	Supreme Court orders single-phase Tripura village committee polls on September 27	93328ce7	supreme court,tripura,ttaadc,pradyot deb barma,tipra motha
2026-06-17	Karnataka High Court dismisses PIL against Shivakumar cabinet, imposes 50,000 rupee cost	c3eddc02	karnataka high court,dk shivakumar,vibhu bakhru,pil,article 164
2026-06-17	Update: US says Iran has signed accord to end war as ships move through Hormuz	bd62150d	united states,iran,trump,strait of hormuz,blockade
2026-06-17	Norway crown prince's stepson jailed four years for rape	d866bc2f	marius borg hoiby,mette-marit,norway,oslo,rape conviction
2026-06-17	Africa CDC warns DR Congo Ebola outbreak could become worst in history	bd7f4362	dr congo,ebola,africa cdc,bundibugyo virus
2026-06-17	Mbappe brace fires France to 3-1 win over Senegal in World Cup opener	ff4d517e	kylian mbappe,france,senegal,barcola,world cup 2026
2026-06-17	Trump's Iran deal leaves Netanyahu isolated ahead of Israeli elections	f94e3ebf	trump,netanyahu,iran,israel,elections
2026-06-17	ChatGPT's market share slips below 50% for the first time as rivals gain	62ef6cb0	chatgpt,openai,gemini,claude,sensor tower
2026-06-17	Robinhood cuts about 10% of staff without citing AI	eecb124d	robinhood,vlad tenev,layoffs,ai
2026-06-17	NewCore launches with $66 million to give AI agents workplace identities	023258ba	newcore,ai agents,claude code,codex,mckinsey
2026-06-17	Startup Probably raises $9 million from a16z to build low-hallucination AI	ef609234	probably,andreessen horowitz,hallucinations,data science
2026-06-17	Malaysia's Respond.io raises $62.5 million Series B, eyes US and Europe deals	dbaded97	respond.io,camber partners,gerardo salandra,messaging,malaysia
2026-06-17	Update: Bank of Japan hikes rate to 1%, highest since 1995, in 7-1 vote	29cf9b17	bank of japan,toichiro asada,ueda,himino,interest rates
2026-06-17	Update: Dow closes at record near 52,000 as tech slides before Fed decision	cb254114	dow jones,s&p 500,nasdaq,kevin warsh,fed
2026-06-17	Update: Brent crude falls below $80 as US-Iran deal set to restore Gulf supply	9257af62	brent crude,wti,strait of hormuz,iran,oil
2026-06-17	Fox to acquire Roku for $160 a share in roughly $22 billion deal	b40f52ee	fox corporation,roku,m&a,streaming
2026-06-17	Dave & Buster's stock plunges 14% after first-quarter earnings miss	66eb0cc9	dave & buster's,earnings,comparable sales,eps
2026-06-17	🎾 Zverev survives Kopriva to equal Nadal's ATP 500 win record at Halle	75cde54f	zverev,kopriva,halle,atp 500,nadal
2026-06-17	🎾 Defending champion Bublik dumped out of Halle by qualifier Bellucci	1ffaffb7	bublik,bellucci,halle,medvedev,upset
2026-06-17	🏏 Sri Lanka beat New Zealand for first Women's T20 World Cup win over them	c2ffa9d9	sri lanka,new zealand,women's t20 world cup,nilakshika silva
2026-06-17	🏏 England restrict Ireland to 98 for 8 to seal second Women's T20 World Cup win	ebc0f10e	england,ireland,women's t20 world cup,sciver-brunt
2026-06-18	HDB launches 6,952 BTO flats across seven projects in June exercise	6734ade7	singapore,hdb,bto flats,housing
2026-06-18	Singapore's non-oil exports jump 38.4% in May on AI-driven electronics demand	06b63be5	singapore,nodx,exports,electronics
2026-06-18	MAS survey trims Singapore's 2026 growth forecast to 3.5% on geopolitical risk	e0bbea38	singapore,mas,gdp forecast,economy
2026-06-18	CNA tops Reuters Institute 2026 rankings for Singapore online news use	d2791e09	singapore,reuters institute,cna,news report
2026-06-18	Car and taxi collide outside Bendemeer MRT, driver flees as cabby hospitalised	145b431a	singapore,bendemeer mrt,accident,taxi
2026-06-18	NSE files for India's largest-ever IPO with up to 148.9 million shares on offer	0cf66d61	india,nse,ipo,sebi
2026-06-18	Delhi Police bust ISI-backed terror module linked to D-Company, seven arrested	92431f44	india,delhi police,isi,d-company,terror module
2026-06-18	India blocks Telegram until June 22 and curbs message editing before NEET re-exam	efa4bf3e	india,telegram,meity,neet
2026-06-18	Nifty tops 24,000 as Indian shares rise a fourth day before the Fed decision	e14177b9	india,nifty,sensex,markets
2026-06-18	G7 closes Evian summit with pledge to boost Ukraine air defences and Russia sanctions	7e6c6d95	g7,evian,ukraine,russia sanctions
2026-06-18	Update: US-Iran accord set to be signed June 19 with Hormuz toll-free for 60 days	09596557	united states,iran,strait of hormuz,memorandum
2026-06-18	Messi hat-trick equals Klose's World Cup goal record as Argentina beat Algeria 3-0	d72c399a	lionel messi,argentina,algeria,klose,world cup 2026
2026-06-18	England beat Croatia 4-2 in their World Cup opener as Kane scores twice	7e9f508d	england,croatia,harry kane,world cup 2026
2026-06-18	SpaceX to buy AI coding startup Cursor for $60 billion days after its IPO	1bdf2abf	spacex,cursor,anysphere,xai
2026-06-18	Snap unveils $2,195 Specs augmented-reality glasses as shares slide	ce0b7235	snap,specs,ar glasses
2026-06-18	World-model startup Odyssey raises $310 million at a $1.45 billion valuation	fae22d2f	odyssey,world models,amazon,series b
2026-06-18	Google launches its first Gemini-built smart speaker at $99.99	482bd108	google,gemini,home speaker
2026-06-18	Anthropic becomes first standalone AI firm to join Frontier carbon-removal group	af5112e1	anthropic,frontier,carbon removal
2026-06-18	Fed holds rates at 3.5-3.75% but hawkish projections signal a 2026 hike	9b4228a3	federal reserve,kevin warsh,interest rates,fomc
2026-06-18	Wall Street slides as hawkish Fed hits tech; Dow falls 507 points	e37a8b1f	dow jones,s&p 500,nasdaq,wall street
2026-06-18	US Treasury yields jump as Fed dot plot lifts bets on a 2026 rate hike	8a3b84d7	us treasury yields,federal reserve,bonds
2026-06-18	Yum! Brands sells Pizza Hut for $2.7 billion in two deals	b56658bf	yum brands,pizza hut,longrange capital,yum china
2026-06-18	Olin and Huntsman to merge in all-stock deal creating a $12 billion chemicals firm	dc8f399f	olin,huntsman,merger,chemicals
2026-06-18	India crush Afghanistan by 170 runs as Gill and Kishan hit centuries	2cd9fb35	india,afghanistan,shubman gill,ishan kishan,odi
2026-06-18	India post record 209 for 5 to beat Netherlands by 95 at Women's T20 World Cup	e4e0bcd1	india,netherlands,women's t20 world cup,mandhana
2026-06-18	Australia hold Bangladesh to 77 and win by nine wickets	da3ace69	australia,bangladesh,women's t20 world cup,voll
2026-06-18	Badosa fights back to upset Coco Gauff and reach Berlin quarterfinals	3c1418af	badosa,gauff,berlin,tennis
2026-06-18	Medvedev and Shelton advance at the Halle grass-court tournament	4dc68160	medvedev,shelton,halle,tennis
2026-06-19	Singapore reclaims top spot in IMD World Competitiveness Ranking 2026	1eecb93b	Singapore,IMD World Competitiveness Ranking,Hong Kong,Switzerland,reclaims
2026-06-19	NUS slips to 10th and NTU holds 12th in QS World University Rankings 2027	9036042f	National University of Singapore,Nanyang Technological University,QS World University Rankings,ranked
2026-06-19	Indonesia market rout sparks a cross-border Sell Singapore online feud	c32f4209	Sell Singapore,Sell Indonesia,rupiah,Jakarta,feud
2026-06-19	Singapore Air Force Museum reopens after revamp with augmented-reality exhibits	a674c6fd	Singapore Air Force Museum,RSAF,Zaqy Mohamad,Paya Lebar,reopens
2026-06-19	Update: Delhi High Court issues notice on Telegram's plea against India ban	d5fd39c3	Delhi High Court,Telegram,NEET,India ban,notice
2026-06-19	Six women killed as a speeding tractor hits an e-rickshaw in UP's Badaun	c5d989ad	Badaun,Uttar Pradesh,e-rickshaw,tractor,killed
2026-06-19	Rupee firms to 94.29 and Brent hits a three-month low as Hormuz reopens	87899d3b	rupee,Brent crude,Strait of Hormuz,US-Iran,firms
2026-06-19	Modi to release 2,400 crore rupees in job incentives under PM-VBRY scheme	120dc96f	Narendra Modi,PM-VBRY,employment incentives,India,disburses
2026-06-19	Update: Trump and Iran sign accord to end the war and reopen the Strait of Hormuz	ae612a77	Donald Trump,Masoud Pezeshkian,Strait of Hormuz,Iran,signed
2026-06-19	Ukraine launches its largest drone assault on Moscow, hitting an oil refinery	9e38e6ef	Ukraine,Moscow,Gazprom Neft,Zelenskyy,drone attack
2026-06-19	Hegseth orders a six-month review of US forces in Europe and demands a NATO overhaul	0d63d5d0	Pete Hegseth,NATO,Europe,Pentagon,review
2026-06-19	Gaza death toll since the October ceasefire passes 1,000, officials say	595fd350	Gaza,Israel,ceasefire,health ministry,death toll
2026-06-19	Vance warns Israel it cannot kill its way out of insecurity and is deeply isolated	85d44d35	JD Vance,Israel,Netanyahu,Iran deal,isolated
2026-06-19	Amazon in talks to sell its Nvidia-rival AI chips to outside customers	01798d6a	Amazon,AWS,Trainium,Nvidia,chips
2026-06-19	Transformer co-author Noam Shazeer leaves Google to join OpenAI	fa0f4f4b	Noam Shazeer,OpenAI,Google,Gemini,joins
2026-06-19	Intel jumps about 10% after Trump says it will make chips with Apple	c9a54695	Intel,Apple,Donald Trump,TSMC,shares
2026-06-19	General Intuition in talks to raise $300 million at a $2 billion valuation	be4c4eec	General Intuition,Medal,Jeff Bezos,Eric Schmidt,funding
2026-06-19	Pramaana Labs raises $27 million to bring formal verification to AI	4feb987a	Pramaana Labs,Khosla Ventures,formal verification,AI,funding
2026-06-19	EQT agrees to buy UK testing group Intertek for 60 pounds a share	82e5d49b	EQT,Intertek,London Stock Exchange,takeover,private equity
2026-06-19	Accenture shares slump to worst day in years on a weak revenue outlook	11bc3bcd	Accenture,Dragos,runZero,NetRise,shares fall
2026-06-19	Norway's Norges Bank holds its rate at 4.25% and signals another hike	2bac35d4	Norges Bank,Norway,policy rate,hold,hike
2026-06-19	SpaceX ends its first public week up about 37%, worth near $2.4 trillion	9c070f10	SpaceX,Nasdaq,IPO,market cap,Elon Musk
2026-06-19	Eala stuns world No. 2 Rybakina to reach the Berlin quarterfinals	0bdf75e6	Alexandra Eala,Elena Rybakina,Berlin Open,Svitolina,upset
2026-06-19	Zverev reaches the Halle quarterfinals as a Shelton-Fritz clash is set	5f98a54d	Alexander Zverev,Yannick Hanfmann,Taylor Fritz,Ben Shelton,Halle
2026-06-19	Keys beats Muchova to set a Berlin quarterfinal against Pegula	14486ee0	Madison Keys,Karolina Muchova,Jessica Pegula,Berlin Open,quarterfinal
2026-06-19	West Indies edge Scotland by seven runs at the Women's T20 World Cup	a9b7dda5	West Indies,Scotland,Stafanie Taylor,Women's T20 World Cup,Headingley
2026-06-19	South Africa edge Pakistan by two wickets in a Women's T20 World Cup thriller	5caf9e25	South Africa,Pakistan,Annerie Dercksen,Women's T20 World Cup,Birmingham
2026-06-20	COE premiums fall across most categories in the second June bidding exercise	b73b783b	coe,lta,category a,category b,premiums
2026-06-20	Singapore to review its waste blueprint as recycling slips and Semakau fills up	d25659a7	singapore,zero waste masterplan,semakau,recycling,review
2026-06-20	Singapore Cruise Centre to move ferry and cruise operations to a new HarbourFront terminal	7caca246	singapore cruise centre,harbourfront,ferry,cruise,relocation
2026-06-20	Singapore shares edge up as the Straits Times Index gains about 0.7%	8015571f	straits times index,sti,singapore stocks,rises
2026-06-20	Jio Platforms files for a mega IPO after its board clears the DRHP at the Reliance AGM	f616f524	jio platforms,reliance,mukesh ambani,ipo,drhp
2026-06-20	Sensex slides 608 points and the Nifty ends at 24,013 as IT stocks lead a selloff	1e4bed29	sensex,nifty,infosys,tcs,selloff
2026-06-20	South Delhi doctor arrested over the killing of his domestic helper	ad386df1	delhi,manish gupta,domestic helper,mount kailash,murder
2026-06-20	IMD says the monsoon will advance across more of east and central India by June 23	6bac4022	imd,monsoon,delhi,heatwave,forecast
2026-06-20	Meloni rejects Trump's claim she begged for a photo as Italy cancels a US visit	b5c1e9ea	giorgia meloni,donald trump,italy,tajani,g7
2026-06-20	Trump unveils a Qatar-gifted Boeing 747 as the new Air Force One	adb1fc84	donald trump,air force one,boeing 747,qatar,unveils
2026-06-20	Andy Burnham wins a by-election, returning to Parliament to set up a Starmer challenge	ca16c6ad	andy burnham,makerfield,by-election,keir starmer,labour
2026-06-20	Cuba's Communist Party approves an emergency plan to open the economy	426b5524	cuba,communist party,economy,private enterprise,reforms
2026-06-20	EU leaders agree their first joint Ukraine conclusions since early 2025	cc1a4be9	european union,brussels summit,ukraine,china,conclusions
2026-06-20	Waymo recalls nearly 4,000 robotaxis after cars drove into freeway construction zones	e34935db	waymo,robotaxis,recall,construction zones,software
2026-06-20	Meta strikes 1.6-gigawatt AI computing deals with data-centre firm Crusoe	3bedc5af	meta,crusoe,ai data centre,gigawatt,deal
2026-06-20	AI inference startup Baseten is reportedly raising $1.5 billion at a $13 billion valuation	ef8e02ab	baseten,ai inference,funding,valuation,series
2026-06-20	Apple's Tim Cook says price increases are unavoidable amid an AI-driven memory shortage	9040e7bf	apple,tim cook,memory chips,prices,shortage
2026-06-20	Bank of England holds its rate at 3.75% in a 7-2 vote as inflation eases	91d768aa	bank of england,interest rate,mpc,inflation,hold
2026-06-20	Wall Street rebounds as the Nasdaq jumps about 1.9% after the Fed-driven selloff	da9bf588	wall street,nasdaq,s&p 500,rebound,fed
2026-06-20	Kroger's quarterly sales top estimates at $46.1 billion as e-commerce jumps 19%	06b580d4	kroger,earnings,revenue,e-commerce,guidance
2026-06-20	Gold slips below $4,200 an ounce as a hawkish Fed offsets the Iran peace boost	641773fb	gold,brent crude,federal reserve,prices,fall
2026-06-20	Eala beats Svitolina to reach the Berlin Open semifinals	b676a72a	alexandra eala,elina svitolina,berlin open,semifinals,tennis
2026-06-20	Pegula edges Keys in two tiebreaks to make the Berlin semifinals	5c9a5d67	jessica pegula,madison keys,berlin open,semifinals,tennis
2026-06-20	Zverev saves two set points to reach the Halle semifinals	700a320b	alexander zverev,raphael collignon,halle,semifinals,tennis
2026-06-20	Fritz saves a match point against Shelton to set up a Zverev semifinal	ede7191c	taylor fritz,ben shelton,halle,semifinals,tennis
2026-06-20	New Zealand edge Ireland by four runs at the Women's T20 World Cup	d188f639	new zealand,ireland,women's t20 world cup,southampton,cricket
2026-06-21	PM Wong meets Putin at the ASEAN-Russia summit in Kazan	d36841c1	lawrence wong,putin,asean-russia summit,kazan,meets
2026-06-21	PM Wong and Erdogan agree to deepen ties in Istanbul talks	60540562	lawrence wong,erdogan,istanbul,turkey,ties
2026-06-21	Singapore enters its dengue peak season as weekly cases hit a 2026 high	cf23aa4f	singapore,dengue,nea,peak season,clusters
2026-06-21	Singapore households can claim $500 in CDC vouchers brought forward to June	17967343	singapore,cdc vouchers,cost of living,disbursement
2026-06-21	NEET-UG re-exam goes ahead for 22.79 lakh candidates under tight security	a1869b7c	neet-ug,re-exam,nta,paper leak,candidates
2026-06-21	Amit Shah reviews security for the Amarnath Yatra starting July 3	5d080ebc	amit shah,amarnath yatra,security,jammu kashmir,review
2026-06-21	Monsoon set to miss Delhi's normal June 27 onset as Mumbai gets a yellow alert	63321f78	imd,monsoon,delhi,mumbai,yellow alert
2026-06-21	Update: Iran declares the Strait of Hormuz closed over Israel's strikes in Lebanon	31800250	iran,strait of hormuz,israel,lebanon,closed
2026-06-21	Brazil beat Haiti 3-0 as Cunha scores twice at the World Cup	fe4c6444	brazil,haiti,cunha,vinicius,world cup
2026-06-21	United States beat Australia 2-0 to reach the World Cup knockout round	0a8a3486	united states,australia,world cup,knockout,pulisic
2026-06-21	Trump urges the EU to hit China and India with steep tariffs over Russia	c231612d	trump,european union,china,india,tariffs
2026-06-21	Manus's early backers reportedly plan a $2 billion buyback from Meta	ef7e5c1f	manus,meta,buyback,beijing,the information
2026-06-21	Oil rises on Friday but ends the week down about 8% as the Iran truce holds	3fcd367e	brent crude,wti,oil,iran,hormuz
2026-06-21	Asian markets end Friday mixed with US markets shut for Juneteenth	68a67f65	nikkei,hang seng,asian markets,juneteenth
2026-06-21	Indian rupee logs its best week in about 11 weeks on foreign inflows	bebba238	rupee,india,foreign inflows,currency,week
2026-06-21	Pegula beats Sabalenka to reach the Berlin Open final	97d31a85	jessica pegula,aryna sabalenka,berlin open,final,tennis
2026-06-21	Noskova ends Eala's run to set up a Berlin final with Pegula	bf180e92	linda noskova,alexandra eala,berlin open,final,tennis
2026-06-21	Fritz beats Zverev again to reach the Halle Open final	73e376b0	taylor fritz,alexander zverev,halle open,final,tennis
2026-06-21	Tiafoe routs Altmaier to set up an all-American Halle final	00f04f8c	frances tiafoe,daniel altmaier,halle open,final,tennis
2026-06-21	India sweep Afghanistan 3-0 as Jaiswal hits a century	47e10378	india,afghanistan,jaiswal,prasidh krishna,odi
2026-06-21	Australia thrash the Netherlands by 98 runs at the Women's T20 World Cup	cec6f532	australia,netherlands,womens t20 world cup,southampton,cricket
2026-06-22	Three Malaysians charged after collecting S$200,000 for a scam syndicate	c04daeca	malaysians,scam syndicate,singapore police,charged
2026-06-22	Singapore electricity tariff set to rise from July as gas prices climb	4ade349c	ema,electricity tariff,singapore,gas prices,rise
2026-06-22	HDB launches 6,952 BTO flats including the first ever in Lakeview	6502994b	hdb,bto flats,lakeview,singapore,launch
2026-06-22	Counterfeit Sanrio seller fined S$13,000 as director jailed eight months	404ea6da	sanrio,counterfeit,gem story biz,trade marks act,jailed
2026-06-22	Operation Sindhu evacuates over 4,400 Indians from Iran and Israel	bc0570fd	operation sindhu,india,iran,israel,evacuation
2026-06-22	Modi leads the 12th International Yoga Day at Kolkata's Red Road	f52edc45	narendra modi,international yoga day,kolkata,red road,leads
2026-06-22	Railway worker killed as Avadh Assam Express hits a trolley in Bihar	3eaa2b99	avadh assam express,bihar,katihar,railway,killed
2026-06-22	Update: IMD forecasts very heavy rain over northeast India as monsoon nears Delhi	9b54825c	imd,monsoon,northeast india,delhi,forecast
2026-06-22	Update: Starmer pressed to set a departure date as Burnham enters the Commons	6c0a11e4	keir starmer,andy burnham,labour,commons,departure
2026-06-22	Met Office issues an amber extreme-heat warning as June record is threatened	38614dfd	met office,heatwave,amber warning,england,record
2026-06-22	Farage breached MPs' rules 17 times over £384,000 in unregistered interests	b4118e19	nigel farage,reform uk,standards commissioner,interests,breach
2026-06-22	Tribunal finds an NHS trust discriminated against eight nurses over a changing room	85173074	employment tribunal,nhs trust,nurses,county durham,discrimination
2026-06-22	Russian-occupied Crimea halts civilian fuel sales after Ukrainian strikes	bff17566	crimea,ukraine,aksyonov,fuel,drone strikes
2026-06-22	Colombia votes in a knife-edge runoff between de la Espriella and Cepeda	cd3a19a8	colombia,de la espriella,ivan cepeda,runoff,election
2026-06-22	Poland strips Zelensky of its top honour in a WWII-era history dispute	1018a32b	poland,zelensky,nawrocki,order of the white eagle,dispute
2026-06-22	Zimbabwe parliament passes a bill scrapping direct presidential elections	f2c326c3	zimbabwe,national assembly,mnangagwa,constitution,elections
2026-06-22	Spain thrash Saudi Arabia 4-0 as Yamal and Oyarzabal star at the World Cup	52ae62b4	spain,saudi arabia,lamine yamal,oyarzabal,world cup
2026-06-22	Pacific Fusion's Series A tops $1 billion, the largest in the fusion sector	8afde4ef	pacific fusion,series a,fusion energy,funding,techcrunch
2026-06-22	Qualcomm in talks to buy Jim Keller's Tenstorrent for up to $10 billion	fb1313aa	qualcomm,tenstorrent,jim keller,acquisition,ai chips
2026-06-22	SpaceX agrees a $60 billion takeover of AI coding startup Cursor	b0031844	spacex,anysphere,cursor,takeover,bloomberg
2026-06-22	OpenAI reportedly prepares a confidential IPO filing at a $730 billion valuation	b3073f63	openai,ipo,valuation,filing,reuters
2026-06-22	Wall Street reopens after Juneteenth to a data-heavy week and a hawkish Fed	4c0666ad	wall street,federal reserve,juneteenth,gdp,inflation
2026-06-22	Oil holds near $80 as US-Iran talks in Geneva are abruptly postponed	bc290d83	brent crude,wti,oil,us-iran talks,geneva
2026-06-22	Update: SpaceX shares swing after a record IPO week as leveraged ETFs pile in	82bea967	spacex,spcx,ipo,leveraged etfs,shares
2026-06-22	Tiafoe beats Fritz to win his first grass title at the Halle Open	df599b10	frances tiafoe,taylor fritz,halle open,final,tennis
2026-06-22	Noskova beats Pegula in the Berlin final to close on the top 10	d561783b	linda noskova,jessica pegula,berlin open,final,tennis
2026-06-22	Cerundolo beats Paul for his first ATP 500 title at Queen's Club	95916d77	francisco cerundolo,tommy paul,queens club,final,tennis
2026-06-22	South Africa beat India by six wickets at the Women's T20 World Cup	903f827c	south africa,india,marizanne kapp,womens t20 world cup,cricket
2026-06-22	Antonelli leads the F1 title race as the Austrian Grand Prix looms	93f514d3	kimi antonelli,lewis hamilton,formula 1,austrian grand prix,standings
2026-06-22	JUNO neutrino observatory delivers a landmark first precision measurement	85ab4e41	juno,neutrino,oscillation,observatory,measurement
2026-06-22	Webb measures a black hole that formed before its own galaxy	5bca7e51	james webb space telescope,black hole,early universe,galaxy,nasa
2026-06-22	Ancient DNA shows plague was killing humans 5,500 years ago	410d8ba6	plague,ancient dna,lake baikal,siberia,nature
2026-06-22	Study finds developing neurons break their own DNA to build the brain	c6e7a6bd	neurons,dna,brain development,cerebral cortex,nature
2026-06-23	Three men charged over an alleged US$18 million fake 'made in Singapore' mattress scam	3e2c86ca	singapore,mattress scam,us tariffs,customs
2026-06-23	CNA tops Singapore's online news rankings, with Mothership second	a25e317c	singapore,reuters institute,cna,mothership
2026-06-23	Man jailed 11 weeks for filming upskirt videos of four women at VivoCity	2d500061	singapore,voyeurism,vivocity,court
2026-06-23	Yishun mother jailed four years for giving her teenage son methamphetamine	782f2fcf	singapore,drugs,methamphetamine,court
2026-06-23	India's top court reconsiders a 1908 rule excluding children of Parsi women	7d8f143b	india,supreme court,parsi,gender
2026-06-23	India records its driest June in over a century as the monsoon finally reaches Mumbai	d318b10b	india,monsoon,rainfall deficit,mumbai
2026-06-23	Modi commissions three indigenous warships in a single day at Kolkata	4ff68f55	india,modi,indian navy,warships
2026-06-23	India beat New Zealand 2-0 to win the FIH Women's Nations Cup	78a68596	india,womens hockey,fih nations cup,new zealand
2026-06-23	Update: Keir Starmer resigns as UK prime minister, triggering a Labour leadership contest	c7aa9efd	uk,keir starmer,labour,andy burnham
2026-06-23	UK borrowing hit GBP23.3 billion in May, GBP5.6bn above forecast	ed45cfbf	uk,public borrowing,ons,obr
2026-06-23	Met Office issues a rare red extreme-heat warning as the UK's June record looks set to fall	176b2d11	uk,met office,heatwave,temperature record
2026-06-23	Two men jailed over arson attacks on properties linked to Keir Starmer	54bb6427	uk,arson,starmer,old bailey
2026-06-23	Update: US and Iran agree a 60-day roadmap toward a final deal in Switzerland	c931c7e8	united states,iran,switzerland talks,nuclear
2026-06-23	Update: De la Espriella wins Colombia's presidential runoff as Cepeda vows to contest	843919d9	colombia,de la espriella,cepeda,election
2026-06-23	China adds 10 US firms, including rare-earth miners, to its export-control list	ebc09082	china,united states,rare earths,export controls
2026-06-23	France closes 845 schools as a second heat dome pushes Europe toward 44C	45383937	europe,france,heatwave,spain
2026-06-23	Two teenagers arrested after a school shooting in the Philippines kills three	ab0c1157	philippines,tacloban,school shooting
2026-06-23	SpaceX signs a compute deal worth up to $6.3 billion with open-source lab Reflection AI	08bb7340	spacex,reflection ai,nvidia,compute
2026-06-23	Groq confirms a $650 million raise and rebuilds after Nvidia's $20 billion talent deal	3fdea98e	groq,nvidia,funding,ai chips
2026-06-23	Google DeepMind invests $75 million in studio A24 to build AI filmmaking tools	e94bc8ae	google deepmind,a24,ai filmmaking,investment
2026-06-23	Microsoft and Chevron plan a 2.67-gigawatt gas plant to power a West Texas data centre	d14c5d83	microsoft,chevron,data center,texas
2026-06-23	Alphabet suffers its worst day in over a year as two top AI researchers defect	25395171	alphabet,google,ai talent,stocks
2026-06-23	AeroVironment sinks 11% on a restatement as Salesforce extends its losing streak	c7ced8d3	aerovironment,salesforce,super micro,stocks
2026-06-23	Jio Platforms files for what would be India's biggest-ever IPO	2c9616ae	jio platforms,reliance,ipo,sebi
2026-06-23	The yen languishes near multi-decade lows despite a $72.8 billion intervention and a BOJ hike	ba2d9a0a	japan,yen,bank of japan,intervention
2026-06-23	Mercedes weigh team orders for Russell and Antonelli as Hamilton's title threat grows	f702da4e	formula 1,mercedes,antonelli,hamilton
2026-06-23	West Indies beat Sri Lanka to move closer to the Women's T20 World Cup semis	e56d21ef	cricket,womens t20 world cup,west indies,sri lanka
2026-06-23	Bangladesh stun Pakistan as hosts England stay unbeaten at the Women's T20 World Cup	012cc227	cricket,womens t20 world cup,bangladesh,england
2026-06-23	Jack Draper wins his first match under new coach Andy Murray at Eastbourne	237f0bef	tennis,jack draper,andy murray,eastbourne
2026-06-23	NASA's Roman Space Telescope arrives in Florida for final launch preparations	a8a88d2d	nasa,roman space telescope,kennedy space center
2026-06-23	NASA's Lucy reveals a wobbling, peanut-shaped asteroid with signs of ancient water	13a32dc0	nasa,lucy,donaldjohanson,asteroid
2026-06-23	A tropical butterfly that barely ages could hold clues to longevity	6e81604a	heliconius,butterfly,longevity,ageing
2026-06-23	T. rex took about 40 years to reach full size, a new fossil study finds	8fb73f49	t rex,dinosaur,growth study,paleontology
2026-06-24	Civil servants to get a 0.45-month mid-year bonus, with extra payouts for junior officers	47289325	public service division, civil servants, mid-year bonus, singapore
2026-06-24	Just 14% of Singapore workers are engaged at work, the lowest rate in the region	499bcf87	gallup, singapore institute of directors, worker engagement, report
2026-06-24	Household refuse collection fees to rise from 1 July in the first revision since 2024	07c33e7f	nea, refuse collection fee, hdb, increase
2026-06-24	Driver jailed 32 weeks and fined S$6,000 over 73 mostly-staged traffic accidents	c2c6c02c	singapore, staged accidents, insurance fraud, jailed
2026-06-24	Man, 59, jailed 12 weeks for exposing himself to a police officer after a Sembawang molestation	ca2ec1f9	chandru suryakanth, sembawang, outrage of modesty, jailed
2026-06-24	George Kurian resigns as Union minister after his Rajya Sabha term ends, amid reshuffle buzz	e6f04b8b	george kurian, bjp, rajya sabha, resignation
2026-06-24	Sensex sinks 893 points to 76,201 in its biggest June fall as weak data hits sentiment	903a5759	sensex, nifty, stock market, selloff
2026-06-24	Vedanta slumps about 9% after a Rs 2,149-crore promoter block deal	82662baa	vedanta, twin star holdings, block deal, shares
2026-06-24	India's flash PMI eases to a three-month low as services growth slows to a 17-month low	0071d42d	hsbc, flash pmi, services, slowdown
2026-06-24	Kerala High Court admits the state's appeal to overturn Dileep's acquittal in the 2017 actress assault case	14964db5	kerala high court, dileep, actress assault case, appeal
2026-06-24	Update: Streeting backs Burnham as Labour's leadership race opens, raising the prospect of a coronation	e3ebbec8	andy burnham, wes streeting, labour leadership, starmer
2026-06-24	Bank of England scraps individual stablecoin holding limits and sets a 40 billion pound issuance cap	d02b8c35	bank of england, stablecoin, issuance cap, regulation
2026-06-24	Update: Met Office red extreme-heat warning takes effect as England and Wales near the all-time June record	76b210da	met office, red heat warning, heat dome, june record
2026-06-24	Labour sets out its leadership timetable, with nominations opening on 9 July and a new leader by September	aaf1ab05	labour party, leadership timetable, nominations, parliament
2026-06-24	US Senate passes the first war powers resolution to clear both chambers, seeking to halt the Iran campaign	f842e980	us senate, war powers resolution, iran, trump
2026-06-24	EU hosts a Taliban delegation in Brussels for the first time in talks on Afghan deportations	75745ed3	european union, taliban, brussels, afghan deportations
2026-06-24	Iran's President Pezeshkian makes his first post-war foreign trip, to Pakistan	333161f0	pezeshkian, iran, pakistan, islamabad memorandum
2026-06-24	Lebanon and Israel resume US-mediated talks as a fragile Hezbollah ceasefire holds	b70e7902	lebanon, israel, ceasefire, washington talks
2026-06-24	South Africa sees deadly anti-migrant attacks and mass repatriations ahead of a 30 June deadline	95935b32	south africa, xenophobia, repatriation, migrants
2026-06-24	Nvidia slips below a $5 trillion value as a chip-led selloff deepens on AI-spending worries	b6bd3f52	nvidia, micron, ai spending, selloff
2026-06-24	Menlo Ventures raises a record $3 billion on the back of its Anthropic bet	27f76ba4	menlo ventures, anthropic, venture fund, raise
2026-06-24	A startup, Subquadratic, emerges from stealth claiming a breakthrough on the LLM attention bottleneck	724f4364	subquadratic, llm, sparse attention, benchmark
2026-06-24	World-model startup Odyssey raises a $310 million round at a $1.45 billion valuation	3bd1d557	odyssey, world model, series b, valuation
2026-06-24	US Treasury issues a 60-day license letting Iran sell oil for the first time in 35 years	1efbe790	us treasury, iran, oil license, sanctions
2026-06-24	Oil falls to a three-month low as the Iran sales waiver eases supply fears	5e99c6bb	brent crude, wti, oil prices, iran waiver
2026-06-24	South Korea's KOSPI crashes nearly 10%, triggering a circuit breaker as Samsung and SK Hynix dive	869a74e6	kospi, south korea, circuit breaker, leveraged etfs
2026-06-24	Wall Street sinks as a chip rout drives bets on a second Fed rate hike	749aaf86	nasdaq, s&p 500, federal reserve, kevin warsh
2026-06-24	🏎️ F1 heads to the Red Bull Ring for the Austrian GP with Antonelli leading the title race	5ebd3aa3	formula 1, austrian grand prix, antonelli, red bull ring
2026-06-24	🎾 Naomi Osaka beats Mertens to reach her first quarter-final of 2026 at Bad Homburg	d02f299e	naomi osaka, bad homburg, wta, grass
2026-06-24	🏏 Australia thrash Pakistan to move to the brink of the Women's T20 World Cup semi-finals	5c26cc9a	australia, pakistan, womens t20 world cup, headingley
2026-06-24	🏏 Athapaththu century revives Sri Lanka's Women's T20 World Cup semi-final hopes	b4cb4df2	chamari athapaththu, sri lanka, ireland, womens t20 world cup
2026-06-24	🎾 Grigor Dimitrov notches his 50th career grass-court win in his Mallorca opener	a5330d39	grigor dimitrov, mallorca, atp, grass
2026-06-24	The first ticking 'nuclear clocks' arrive, promising timekeeping beyond today's best atomic clocks	8fb3e18a	nuclear clock, thorium-229, timekeeping, physics
2026-06-24	NASA's upgraded Cold Atom Lab makes quantum matter five times larger aboard the space station	a3187688	nasa, cold atom lab, bose-einstein condensate, iss
2026-06-24	ESA's Euclid mission releases a deep new survey of the Milky Way's inner bulge	34f52a54	esa, euclid, galactic bulge survey, exoplanets
2026-06-24	Stem-cell transplants put a severe spinal-cord and optic-nerve autoimmune disease into 15-year remission	21345b97	stem cell transplant, neuromyelitis optica, remission, autoimmune disease
2026-06-25	Two self-radicalised Singaporeans issued ISA orders over Gaza-linked extremism	b893bc46	isd,internal security act,tarmizi mohd taha,gaza
2026-06-25	Singapore faces a rare 'red' transboundary haze risk for the August-September window	487172fc	siia,transboundary haze,el nino,singapore
2026-06-25	NTUC offers cash and 150 jobs to about 400 migrant workers owed wages by two firms	b5aff4f3	ntuc,ng chee meng,kpa engineering,migrant workers
2026-06-25	Man jailed six months for molesting a Singapore Airlines stewardess mid-flight	bb7deea2	akash tiwari,singapore airlines,molestation,jailed
2026-06-25	Man who exploited a PayPal glitch for free laptops avoids a criminal record	89ea45d5	jonathan wee jianwei,paypal,detention order,laptops
2026-06-25	Sensex rebounds about 791 points and Nifty reclaims 24,000 on bank and IT buying	e481551a	sensex,nifty,stock market,rebound
2026-06-25	At least four killed as an under-construction Kolkata warehouse roof collapses	ae6efa41	kolkata,taratala,warehouse collapse,ndrf
2026-06-25	Parliament's monsoon session to run 21 July to 21 August, with Delimitation Bill set to return	e864d922	parliament,monsoon session,kiren rijiju,delimitation bill
2026-06-25	Goyal says a 50% US tariff is delaying the India-US trade deal	f11cfaba	piyush goyal,india-us trade deal,tariff,commerce
2026-06-25	Update: UK records its hottest June day at 36.1C as the heatwave shuts schools	b0dfab1d	met office,gosport,june heat record,heatwave
2026-06-25	Update: Burnham to pledge loyalty to Reeves' fiscal rules as he readies an economy plan	92a7a124	andy burnham,rachel reeves,fiscal rules,labour leadership
2026-06-25	Southern Water imposes a hosepipe ban on about a million customers as drought bites	4b254dc5	southern water,hosepipe ban,hampshire,drought
2026-06-25	Scotland orders an urgent review of 'anomalous' business rates after a near-500% rise	268d2788	jenny gilruth,business rates,scotland,review
2026-06-25	Niger becomes the third country to formally quit the International Criminal Court	cb9ee994	niger,international criminal court,rome statute,sahel
2026-06-25	Gunmen kill at least 21 farmers in a massacre in Nigeria's Plateau state	7b8a273c	nigeria,plateau state,bokkos,massacre
2026-06-25	Guyana boosts military surveillance as tensions with Venezuela over Essequibo rise	be554d40	guyana,venezuela,essequibo,omar khan
2026-06-25	Update: Russia launches an overnight drone barrage on Ukraine as rival ceasefire offers fail	01443ee8	russia,ukraine,crimea,drone strikes
2026-06-25	Update: Colombia's president-elect says the country will join a US-led anti-cartel bloc	32b531b7	colombia,de la espriella,shield of the americas,petro
2026-06-25	Qualcomm to buy AI-software firm Modular for about $3.9 billion to challenge Nvidia	a604014a	qualcomm,modular,chris lattner,nvidia
2026-06-25	AI inference startup Baseten raises $1.5 billion at a valuation of up to $13 billion	f08421ab	baseten,ai inference,altimeter,funding
2026-06-25	Tata Electronics confirms a breach after data from an Apple and Tesla supplier leaks	1ea61cce	tata electronics,apple,tesla,data breach
2026-06-25	Superhuman acquires AI-detection startup GPTZero	0c032485	superhuman,gptzero,edward tian,acquisition
2026-06-25	India's MoEngage buys AI-agent startup Aampe in an all-cash deal	7c2ecb86	moengage,aampe,ai agents,acquisition
2026-06-25	Micron guides to record $50 billion in quarterly revenue as AI memory demand booms	19f8a0ed	micron,hbm,earnings,ai memory
2026-06-25	Gold tumbles below $4,000 for the first time since November as the dollar jumps	4a938bd1	gold,silver,dollar,federal reserve
2026-06-25	FedEx beats on earnings but slides about 6% on a soft 2026 profit outlook	6eef0b7e	fedex,earnings,guidance,freight spin-off
2026-06-25	Wendy's jumps 26% as Reddit traders make it the latest meme stock	d734e652	wendys,meme stock,short squeeze,steven cirulis
2026-06-25	🏎️ Red Bull bring their biggest upgrade of the season to a tense home Austrian GP	5d203142	red bull,austrian grand prix,max verstappen,isack hadjar
2026-06-25	🏎️ Verstappen rejects a new Red Bull deal as exit-clause talk builds before Austria	a80670bd	max verstappen,red bull,contract,exit clause
2026-06-25	🎾 Emma Navarro stuns top seed Iga Swiatek at Bad Homburg	75968a35	emma navarro,iga swiatek,bad homburg,grass
2026-06-25	🎾 Jack Draper reaches the Eastbourne quarter-finals in his second event under Andy Murray	88794ec0	jack draper,jack pinnington jones,andy murray,eastbourne
2026-06-25	🏏 England become the first team into the Women's T20 World Cup semi-finals	69e09778	england,west indies,womens t20 world cup,lords
2026-06-25	Interstellar comet 3I/ATLAS may be up to 12 billion years old, older than the Sun	288783af	3i/atlas,james webb space telescope,martin cordiner,comet
2026-06-25	Hubble spots a tiny early galaxy that helped clear the universe's hydrogen fog	9e76ee0d	hubble space telescope,mxdfz4.4,reionization,galaxy
2026-06-25	DNA reveals why South Africa's Cape leopards shrank to half the usual size	4ea9ebd1	cape leopard,genome,south africa,adaptation
2026-06-25	CAR-T therapy drives deep responses in early myeloma but carries serious risks	81818af5	car-t,smoldering myeloma,nature medicine,cancer
2026-06-26	Motorcyclist, 25, and his 21-year-old pillion die in a Yio Chu Kang crash	ed232bfe	yio chu kang,motorcycle accident,singapore,fatal crash
2026-06-26	Property agent jailed over an Australian scheme that cost investors S$16 million	961e3bc6	wendy kwek,property scheme,mas,jailed
2026-06-26	Man gets a lifetime driving ban for a fourth drink-driving offence	5b88c14b	kenny yeap,drink driving,lifetime ban,tampines
2026-06-26	HDB launches about 6,900 June BTO flats, including 2,520 with short waits	7ece5931	hdb,bto,short wait flats,sembawang
2026-06-26	Operation Sindhu winds down after evacuating 4,415 Indians from Iran and Israel	3cd2264f	operation sindhu,mea,iran,israel
2026-06-26	India-China border trade resumes through the Lipulekh Pass after six years	3fe258b2	lipulekh pass,india,china,border trade
2026-06-26	Centre extends emergency powers to keep Tata's Mundra plant running on weak monsoon	29b5319f	tata power,mundra,section 11,electricity
2026-06-26	Supreme Court to hear a plea against surrendering 152 Tamil Nadu medical seats	13e56d91	supreme court,tamil nadu,medical seats,all-india quota
2026-06-26	Update: UK breaks its June temperature record for a second straight day at 36.7C	1bfd0ba5	june heat record,merryfield,somerset,heatwave
2026-06-26	UK private sector shrinks for a second month as the flash PMI hits a 14-month low	e84adc5b	s&p global,flash pmi,uk economy,contraction
2026-06-26	Resident doctors in England vote on a pay deal to end strikes, with the ballot closing today	21d9ecdc	resident doctors,bma,pay offer,strikes
2026-06-26	Met Office warns of thunderstorms, hail and flash flooding as the heatwave breaks	1fc2b6f8	thunderstorms,hail,flooding,lightning
2026-06-26	Twin earthquakes kill at least 188 in Venezuela as buildings collapse near Caracas	41094887	venezuela,caracas,earthquake,usgs
2026-06-26	Kenya arrests 355 as it marks two years since deadly Gen Z protests	eabc0b97	kenya,murkomen,gen z protests,nairobi
2026-06-26	Iran's IRGC rejects a new Oman-IMO shipping route through the Strait of Hormuz	ee927f94	iran,irgc,strait of hormuz,oman
2026-06-26	A US-backed push to unify Libya's rival governments gains ground in the east	40a60bb6	libya,massad boulos,haftar,united states
2026-06-26	OpenAI unveils Jalapeno, its first custom AI chip, built with Broadcom	b54ce532	openai,broadcom,jalapeno,ai chip
2026-06-26	Ex-Infosys chief Vishal Sikka launches Hang Ten Systems with $32 million	c721c88a	vishal sikka,hang ten systems,mayfield,it services
2026-06-26	AI revenue outpaces data-center depreciation for a second straight quarter	6cd78cc7	ai revenue,data centers,depreciation,capex
2026-06-26	Robotics startup HaloBraid raises $7 million to speed up salon hair-braiding	a8086db3	halobraid,seven seven six,robotics,funding
2026-06-26	US Supreme Court shields Bayer from Roundup cancer-warning lawsuits	628ef7c5	bayer,roundup,supreme court,monsanto
2026-06-26	The Fed's preferred inflation gauge hits a three-year high as May PCE reaches 4.1%	944108d8	pce,inflation,federal reserve,core pce
2026-06-26	Apple raises Mac and iPad prices as a memory-chip shortage bites	436c0c5e	apple,microsoft,memory shortage,prices
2026-06-26	Germany's Merck KGaA to buy Bio-Techne for $11.3 billion	949a9b39	merck kgaa,bio-techne,acquisition,life sciences
2026-06-26	Qualcomm jumps 15% as it unveils Dragonfly data-center chips with Meta and Microsoft	973adfb3	qualcomm,dragonfly,meta,microsoft
2026-06-26	🏎️ McLaren bring an upgraded rear wing to the Austrian GP, eyeing the top step	51aeefaf	mclaren,austrian grand prix,norris,red bull ring
2026-06-26	🏎️ The Austrian GP weekend opens at the Red Bull Ring with Hamilton a title threat	813bb997	formula 1,austrian grand prix,hamilton,ferrari
2026-06-26	🎾 Jack Draper thrashes Diallo 6-1, 6-4 to reach the Eastbourne semi-finals	1bbd6d35	jack draper,gabriel diallo,eastbourne,atp
2026-06-26	🎾 Naomi Osaka reaches the Bad Homburg semi-finals with a 6-2, 6-2 win	c64b5c23	naomi osaka,alexandrova,bad homburg,wta
2026-06-26	🏏 Shafali's 53 lifts India past Bangladesh by five wickets to keep semis alive	77ec92b3	shafali verma,india,bangladesh,womens t20 world cup
2026-06-26	AI screen turns up new antibiotics against drug-resistant gonorrhoea	11cfa088	gonorrhoea,antibiotics,machine learning,nature
2026-06-26	Burnt bones push possible human fire use back to 1.79 million years ago	b6e2e8e8	wonderwerk cave,fire,homo erectus,archaeology
2026-06-26	Summer sun fails to fix a year-round vitamin D shortfall in at-risk Britons	efba5ab0	vitamin d,newcastle university,nutrition,study
2026-06-26	Webb finds the first signs of salt clouds on a cold 'pink' world	20513f14	james webb space telescope,gj 504b,salt clouds,exoplanet
2026-06-27	Update: Venezuela earthquake death toll passes 920 as rescuers race the clock	aea51ac0	venezuela,earthquake,caracas,death-toll,rescue
2026-06-27	Update: US announces an Israel-Lebanon framework deal requiring Hezbollah to leave the south	58de25bf	israel,lebanon,hezbollah,rubio,framework-deal
2026-06-27	IAEA chief demands a strong verification system for Iran's nuclear programme	afb34621	iaea,grossi,iran,nuclear,verification
2026-06-27	Ukraine carries the war deep into Russia as Moscow says it downed 555 drones overnight	e3938d72	ukraine,russia,drones,overnight-strikes
2026-06-27	OpenAI leans toward delaying its IPO to 2027 as Altman holds firm on a $1 trillion valuation	e5665009	openai,ipo,altman,valuation
2026-06-27	Chip stocks slide again as fears mount over the cost of AI infrastructure	d6c13463	chip-stocks,softbank,micron,ai-infrastructure,selloff
2026-06-27	AI-linked tech layoffs mount in 2026 as Oracle and Meta restructure around data centres	a52592ce	oracle,meta,layoffs,ai,data-centres
2026-06-27	Oil drops below $70 after a cargo ship is struck near Oman and Iraq threatens to leave OPEC	f7a6ae56	oil,brent,wti,opec,iraq
2026-06-27	ON Semiconductor agrees to buy Synaptics in a $7 billion all-stock deal	efd4399c	on-semiconductor,synaptics,acquisition,chips
2026-06-27	Boeing wins a $3.62 billion freight-jet order from China Southern Airlines	23f07d99	boeing,china-southern,freight-jet,order
2026-06-27	Strait of Hormuz shipping recovers but stays fragile after the first post-truce ship attack	50fe8335	strait-of-hormuz,shipping,imo,ever-lovely
2026-06-27	🏎️ Antonelli completes a Friday sweep at the Austrian GP, topping both practice sessions	ff7049a0	f1,antonelli,austrian-gp,practice,fp2
2026-06-27	🏎️ Cadillac's big Austrian GP upgrade is derailed as Bottas' car catches fire in FP2	42839013	f1,cadillac,bottas,fire,austrian-gp
2026-06-27	🎾 Naomi Osaka reaches her first grass-court final, beating Wang Xinyu in Bad Homburg	adcf0c49	tennis,osaka,bad-homburg,final,wang-xinyu
2026-06-27	🎾 Wimbledon draw: Sinner defends with Alcaraz out injured as Serena Williams is handed a wildcard	59db6038	tennis,wimbledon,draw,sinner,serena-williams,alcaraz
2026-06-27	🎾 Jack Draper's Eastbourne run ends in the semi-finals against Ugo Humbert	8c21cb46	tennis,draper,eastbourne,humbert
2026-06-27	🏏 England reach the Women's T20 World Cup semis as India face a must-win decider with Australia	9a0a623e	cricket,womens-t20-world-cup,england,india,australia
2026-06-28	Singapore graduates take traineeships at half the median starting pay as hiring cools	0647e95d	singapore, graduates, grit, tan see leng, jobs
2026-06-28	Singapore-flagged cargo ship struck by a projectile while crossing the Strait of Hormuz	bbbb4ccd	singapore, evergreen marine, strait of hormuz, ukmto
2026-06-28	Analysts say Wong-Putin meeting does not signal Singapore softening on Russia	99870642	lawrence wong, vladimir putin, asean, russia
2026-06-28	New speed camera on the BKE near Woodlands goes live on 1 July	73186185	bukit timah expressway, traffic police, woodlands, speed camera
2026-06-28	Banks pledge an ATM or cashpoint within 500m of every HDB block by end-2027	75ae7dfb	association of banks in singapore, dbs, ocbc, uob, nets
2026-06-28	George Kurian resigns ahead of an expected Modi cabinet reshuffle this weekend	a122c780	george kurian, narendra modi, cabinet reshuffle, council of ministers
2026-06-28	S&P pegs India's FY27 growth at 6.6% as a weak monsoon clouds the outlook	230c411d	s&p global, india, gdp, monsoon, fy27
2026-06-28	GSTN flags e-invoice and e-way bill API changes; flood-hit Maharashtra gets filing relief	458950ed	gstn, cbic, gst, maharashtra, e-way bill
2026-06-28	Burnham becomes front-runner for Labour leadership after Starmer's resignation	19592cf6	keir starmer, andy burnham, labour party, leadership, makerfield
2026-06-28	Resident doctors' ballot on a 6.6% pay offer closes; result will decide the strikes	bd592d5d	resident doctors, bma, pay offer, nhs england, strikes
2026-06-28	OBR puts UK welfare spending at 314.9bn pounds, or 10.7% of GDP	a81a1fbc	obr, welfare trends report, uk, welfare spending, gdp
2026-06-28	Update: Venezuela quake toll passes 1,400 as the 72-hour rescue window closes	5655bbac	venezuela, caracas, earthquake, rescue
2026-06-28	Update: US strikes Iran for a second night after a tanker is hit near Hormuz	0a66843e	united states, iran, centcom, strait of hormuz, m/t kiku
2026-06-28	Germany sets an all-time heat record of 41.5C as Europe's heatwave shifts east	46a6c14d	germany, europe, heatwave, temperature record
2026-06-28	Aid groups warn of imminent atrocities as the RSF encircles Sudan's el-Obeid	afddd8ad	sudan, rsf, el-obeid, north kordofan, amnesty international
2026-06-28	Tropical Storm Mekkhala floods Taiwan, killing two before heading for Japan	1db74759	taiwan, japan, tropical storm mekkhala, flooding
2026-06-28	US clears Anthropic's Mythos 5 model for about 100 trusted partners	a66cd48c	anthropic, commerce department, howard lutnick, mythos 5, fable 5
2026-06-28	Asian AI labs rush out rival models as the US export curbs drag on	e78e2153	360, sakana ai, tulongfeng, fugu, export controls
2026-06-28	Despite the AI hype, engineering is the most resilient tech job, new data shows	6fcf2c18	signalfire, engineering, tech hiring, ai
2026-06-28	Cybersecurity startup NewCore raises $66m to give AI agents identities	68a96b1e	newcore, cyberstarts, ai agents, funding
2026-06-28	Equal-weight S&P 500 hits a record as the rally broadens away from chipmakers	2019e579	s&p 500 equal weight, s&p 500, nasdaq, rotation
2026-06-28	Caterpillar jumps about 6% as industrials carry the Dow to a record	06214c2b	caterpillar, dow jones, industrials, data centers
2026-06-28	Silver slides below $65 an ounce as the Fed flags a possible rate hike	04d2ebe7	silver, gold, federal reserve, us dollar
2026-06-28	Nasdaq logs a fifth straight loss as money rotates into defensives	afe11dc5	nasdaq composite, s&p 500, dow jones, markets
2026-06-28	🏎️ Russell takes a dramatic Austrian GP pole as Verstappen crashes out in Q3	eb116fe8	george russell, max verstappen, austrian grand prix, red bull ring, pole
2026-06-28	🏎️ Mercedes sweep Austrian practice as Russell pips Antonelli in final practice	10e02ca8	george russell, kimi antonelli, mercedes, austrian grand prix, practice
2026-06-28	🎾 Muchova wins her first grass title at Bad Homburg as Osaka retires in the final	c2af3d8d	karolina muchova, naomi osaka, bad homburg open, wimbledon
2026-06-28	🎾 Keys becomes a three-time Eastbourne champion without dropping a set	0f463c08	madison keys, tatjana maria, eastbourne open, wimbledon
2026-06-28	🏏 England rout New Zealand by nine wickets to knock out the holders	274f5417	england, new zealand, womens t20 world cup, danni wyatt-hodge
2026-06-28	🏏 West Indies reach the T20 World Cup semis despite Ireland's first-ever win	dc700fc1	west indies, ireland, womens t20 world cup, orla prendergast
2026-06-28	NASA prepares the first robotic rescue of a falling space telescope	3b406392	nasa, swift observatory, katalyst space, link, orbit boost
2026-06-28	Euclid maps the Milky Way's crowded heart, imaging more than 60 million stars	b9558562	esa, euclid, galactic bulge survey, exoplanets, milky way
2026-06-28	Adaptive deep brain stimulation cuts falls for Parkinson's patients in a trial	f647ff73	nature medicine, deep brain stimulation, parkinsons disease, gait
2026-06-28	NASA's Roman Space Telescope arrives in Florida for final launch preparations	a8a88d2d	nasa, roman space telescope, kennedy space center, dark energy
2026-06-29	Workers' Party keeps Pritam Singh as chief in a special cadre confidence vote	efb506cc	workers party,pritam singh,cadre vote,singapore
2026-06-29	Singapore's new Online Safety Commission opens, letting victims file harm reports online	0458016e	online safety commission,francis ng,singapore,online harms
2026-06-29	Stars Engrg director jailed over the 2021 Tuas blast that killed three workers	18949220	stars engrg,chua xing da,tuas explosion,singapore
2026-06-29	Singapore think-tank issues a rare 'red' haze alert for the August-September peak	b37e2cd7	siia,haze outlook,singapore,transboundary haze
2026-06-29	Modi gifts Seychelles a made-in-India patrol vessel and a 1,250-crore credit line	370d439e	narendra modi,seychelles,ps lespwar,line of credit
2026-06-29	CBI's Operation Chakra-VI raids 80-plus sites in 16 states over 'digital arrest' scams	deae947c	cbi,operation chakra-vi,digital arrest,scam
2026-06-29	Amarnath Yatra's Pratham Puja held as security tightens before the 3 July start	154187ad	amarnath yatra,pratham puja,project hawk eye,jammu and kashmir
2026-06-29	Centre reappoints RBI Deputy Governor Swaminathan Janakiraman for two more years	a033e480	rbi,swaminathan janakiraman,deputy governor,reappointment
2026-06-29	South East Water orders a Kent hosepipe ban for 850,000 customers from 3 July	20c2ae4d	south east water,hosepipe ban,kent,heatwave
2026-06-29	Update: Reeves backs Burnham as the Labour leadership race heads toward a coronation	f2c444c8	rachel reeves,andy burnham,labour party,leadership
2026-06-29	UK retail sales slump deepens as consumer confidence holds at minus 23	e614f050	cbi,gfk,retail sales,consumer confidence
2026-06-29	Reform UK extends its polling lead over Labour and the Conservatives	69baab5d	reform uk,labour,conservatives,polling
2026-06-29	DR Congo files a case against Rwanda at the World Court over decades of alleged abuses	199ef47e	dr congo,rwanda,icj,abuses
2026-06-29	Update: Hezbollah rejects the US-brokered Israel-Lebanon deal as 'null and void'	62feb339	hezbollah,naim qassem,israel,lebanon
2026-06-29	Morocco jails 29, including politicians and sports figures, in a major drug trial	bd0dbaef	morocco,drug trial,politicians,court
2026-06-29	USMCA faces a make-or-break review on 1 July as Trump hints he may not renew it	22154860	usmca,trump,trade,review
2026-06-29	Apple lobbies Washington to buy memory chips from blacklisted Chinese maker CXMT	f8006571	apple,cxmt,commerce department,memory chips
2026-06-29	A startup founder used Anthropic's Claude to read his cancer scans and skip radiotherapy	03485cc9	anthropic,claude,cancer scans,founder
2026-06-29	AI networking startup Netris raises a $15 million Series A led by a16z	0b85c9b0	netris,andreessen horowitz,funding,ai networking
2026-06-29	Menlo Ventures raises a record $3 billion fund on the strength of its Anthropic bet	d8a21a93	menlo ventures,anthropic,fund,venture capital
2026-06-29	SoftBank shares plunge over 12% on a report OpenAI may delay its IPO to 2027	bef46269	softbank,openai,ipo,shares
2026-06-29	Cyber firm Varonis weighs a sale after takeover interest from Blackstone and Thoma Bravo	3a6a7dc0	varonis,blackstone,thoma bravo,sale
2026-06-29	FedEx beats with $25 billion in quarterly revenue but shares slide about 6%	23ea71cb	fedex,earnings,revenue,shares
2026-06-29	Qualcomm is in advanced talks to buy AI-software firm Modular for about $4 billion	ceb844bd	qualcomm,modular,acquisition,ai
2026-06-29	🏎️ Russell holds off Verstappen to win the Austrian Grand Prix	9deb4dcf	george russell,max verstappen,austrian grand prix,f1
2026-06-29	🏎️ Antonelli stays top of the standings as F1 heads to a Silverstone sprint	6b37ccd5	kimi antonelli,standings,silverstone,f1
2026-06-29	🎾 Sinner opens his Wimbledon title defence against Kecmanovic as the draw begins	19f215d9	jannik sinner,wimbledon,kecmanovic,tennis
2026-06-29	🎾 Serena Williams returns on a wildcard as Alcaraz misses Wimbledon injured	4d59cd20	serena williams,carlos alcaraz,wimbledon,tennis
2026-06-29	🏏 Australia knock India out of the Women's T20 World Cup with a six-wicket win	df60100c	australia,india,womens t20 world cup,cricket
2026-06-29	🏏 Women's T20 World Cup semi-finals set as Australia and South Africa seal spots	ef8fda1d	womens t20 world cup,australia,south africa,semi-finals
2026-06-29	Great apes and humans have laughed to the same beat for 15 million years	1c427950	apes,humans,laughter,evolution
2026-06-29	Gene-editing's next act: switching genes off without cutting DNA	e2e68213	epigenetic editing,crispr,gene therapy,dna
2026-06-29	Hubble spots an early galaxy clearing the universe's primordial fog	1570323b	hubble,galaxy,reionization,nasa
2026-06-29	Scientists build the first ticking 'nuclear clocks'	895d845d	nuclear clock,thorium-229,timekeeping,physics
2026-06-30	Director of three firms in a migrant wage dispute returns to Singapore, passport impounded	abbfb868	ramu palani velu,mom,migrant workers,kpa engineering,returns
2026-06-30	Household refuse collection fees rise from 1 July, adding S$0.44 a month for HDB flats	c6aff938	nea,hdb,refuse collection fees,u-save,rise
2026-06-30	Singapore's regulated electricity tariff is set to rise significantly from July	7541b24f	ema,electricity tariff,natural gas,u-save,rise
2026-06-30	LTA enforcement blitz uncovers 380 illegal vehicle modifications islandwide	c90e84ed	lta,illegal modifications,number plates,enforcement,uncovers
2026-06-30	ERP 2 roadside electronic parking trial to begin at 644 car parks in August	838b50ca	lta,erp 2,roadside parking,gantries,trial
2026-06-30	Assam's first flood wave of 2026 affects 22,124 people as a Dhemaji rail bridge collapses	ac98d07e	assam,dhemaji,floods,simen bridge,affects
2026-06-30	Sensex falls 372 points to 76,728 as investors book profits amid US-Iran caution	0a032c31	sensex,nifty,rupee,profit-booking,falls
2026-06-30	Delhi court extends judicial custody of 10 NEET-UG paper-leak accused to 11 July	bead474c	neet-ug,rouse avenue court,cbi,paper leak,extends
2026-06-30	India's eight core industries grew just 0.5% in May as five sectors contracted	1e991b3c	core industries,steel,coal,commerce ministry,slows
2026-06-30	Arunachal Pradesh flash-flood toll rises to three as 12 districts are hit	684ac994	arunachal pradesh,keyi panyor,flash floods,ndrf,rises
2026-06-30	Update: Resident doctors in England vote to accept the 6.6% pay deal, ending the dispute	23b355c1	resident doctors,bma,pay deal,strikes,accept
2026-06-30	Mahmood to replace immigration judges with a public appeals body to clear the asylum backlog	c8bbbe5b	shabana mahmood,immigration appeals authority,asylum backlog,home office,replace
2026-06-30	England endures a third straight record-breaking June day before storms break the heatwave	05418b2d	met office,heatwave,ukhsa,temperature record,breaks
2026-06-30	Hosepipe bans hit millions as England endures its driest spring in over a century	892830f2	hosepipe ban,water companies,drought,southern england,impose
2026-06-30	Pakistan strikes inside Afghanistan as Kabul says 36 civilians were killed	db346fbc	pakistan,afghanistan,taliban,jamaat-ul-ahrar,strikes
2026-06-30	Six killed in a shooting at a youth welfare centre in Germany's Stade	bfe1dcc1	stade,germany,shooting,custody dispute,killed
2026-06-30	Russia kills at least eight in Ukraine as Putin rejects a mutual halt on long-range strikes	82c73212	russia,ukraine,putin,zelenskyy,strikes
2026-06-30	Update: Trump says the US and Iran will meet in Qatar, but Tehran denies talks are planned	63599267	trump,iran,qatar,doha,talks
2026-06-30	Google caps Meta's access to its Gemini models amid an AI compute crunch	da523a4d	google,meta,gemini,compute shortage,caps
2026-06-30	BIS warns an AI bust could spill from growth into credit markets	d4386cb5	bis,ai bust,hyperscalers,capex,warns
2026-06-30	South Korea lines up about $880 billion from Samsung and SK Hynix for AI chips	225962e1	south korea,samsung,sk hynix,chips,invest
2026-06-30	General Intuition raises $320 million to train AI agents on video-game footage	9c21c99b	general intuition,khosla ventures,gameplay,medal,raises
2026-06-30	OpenAI unveils its first in-house inference chip, co-designed with Broadcom	7612ce9f	openai,broadcom,inference chip,nvidia,unveils
2026-06-30	Comcast to split in two, spinning off NBCUniversal and Sky	89b3f0ff	comcast,nbcuniversal,sky,spin-off,splits
2026-06-30	Martin Marietta to buy Lhoist North America in a $13.5 billion deal	e2c02f5c	martin marietta,lhoist,limestone,acquisition,buys
2026-06-30	Rocket Lab agrees to buy Iridium in an $8 billion satellite deal	a89572d8	rocket lab,iridium,satellite,spectrum,acquires
2026-06-30	Dow closes above 52,000 for the first time as Alphabet joins the index	33650f9d	dow jones,alphabet,verizon,index,closes
2026-06-30	🎾 Sinner survives a five-set scare against Kecmanovic to open his title defence	580c5dbe	sinner,kecmanovic,wimbledon,five sets,survives
2026-06-30	🎾 Seeds Rublev and Ruud crash out on Wimbledon's opening day	2636e137	rublev,ruud,hurkacz,wimbledon,crash out
2026-06-30	🎾 Sabalenka and Gauff cruise into the Wimbledon second round	75f23862	sabalenka,gauff,wimbledon,second round,cruise
2026-06-30	🏏 Australia warned to fear Matthews ahead of their T20 World Cup semi-final	bec49eac	australia,west indies,gardner,matthews,semi-final
2026-06-30	🏎️ Red Bull boss Mekies admits uncertainty over Verstappen's 2027 future	14f03bc2	mekies,verstappen,red bull,exit clause,admits
2026-06-30	🏎️ F1 heads to a Silverstone sprint weekend with Antonelli 40 points clear	578aa91a	british grand prix,silverstone,antonelli,sprint,heads
2026-06-30	Astronomers find two Jupiter-sized 'super-puff' planets lighter than cotton candy	d0b789a4	tess,toi-791,exoplanet,low density,find
2026-06-30	Webb suggests interstellar comet 3I/ATLAS formed in an ancient, frigid part of the galaxy	f6c79db1	webb,3i/atlas,comet,deuterium,forms
2026-06-30	NASA's Lucy reveals a wobbling, peanut-shaped asteroid with signs of ancient water	13a32dc0	lucy,donaldjohanson,asteroid,ancient water,reveals
