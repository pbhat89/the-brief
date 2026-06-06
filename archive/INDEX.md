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
