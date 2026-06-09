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
