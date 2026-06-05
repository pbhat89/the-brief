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
2026-06-05	Workers' Party to hold special cadres conference on 28 June over Pritam Singh's future	9e196ff5	Workers' Party,Pritam Singh,cadres conference,secretary-general
2026-06-05	NParks to relocate Singapore's last wild cats - five leopard cats in Changi - from H2 2026	e4af7cb6	NParks,leopard cats,Changi,Singapore wildlife
2026-06-05	Singapore life expectancy rises to record 83.9 years in 2025, narrowing gap with Japan	1fa71293	SingStat,Singapore,life expectancy,Department of Statistics
2026-06-05	IMD issues orange alert as pre-monsoon storms bring heavy rain and lightning to seven states	ec932f2f	IMD,India,monsoon,orange alert
2026-06-05	Shubman Gill named India Test captain for one-off match against Afghanistan in New Chandigarh	e9e1f9f0	Shubman Gill,India,Afghanistan,Test cricket,BCCI
2026-06-05	Israel and Lebanon agree to conditional ceasefire; Hezbollah rejects the terms and vows to fight on	0027d2c2	Israel,Lebanon,Hezbollah,Naim Qassem,ceasefire
2026-06-05	US-Iran peace talks stall as both sides exchange strikes; Hormuz shipping stays at a fraction of normal	3a421510	US,Iran,Strait of Hormuz,peace talks,ceasefire
2026-06-05	Wired finds dormant facial-recognition pipeline - code-named NameTag - embedded in Meta's AI app	b9d441b8	Meta,NameTag,facial recognition,Ray-Ban,AI app
2026-06-05	Trump signs narrower AI executive order asking companies to voluntarily submit frontier models for pre-release review	97cb49bd	Trump,AI executive order,frontier models,national security
2026-06-05	Broadcom falls 15% as Q3 AI chip revenue guidance of $16bn misses Wall Street's $17.2bn estimate	d5998129	Broadcom,AVGO,AI chips,Hock Tan,earnings
2026-06-05	Brent eases below $97 on Israel-Lebanon ceasefire hopes, but Hormuz blockade keeps oil elevated	1e7a022e	Brent crude,oil prices,Strait of Hormuz,Iran,US-Iran
2026-06-05	RBI holds repo rate at 5.25% for third consecutive meeting, citing Iran-war inflation risk	75f2e4f3	RBI,repo rate,Sanjay Malhotra,MPC,India
2026-06-05	Mirra Andreeva beats Kostyuk 6-1, 6-3 to reach first Grand Slam final at Roland Garros	635b618d	Mirra Andreeva,Marta Kostyuk,Roland Garros,French Open,WTA
2026-06-05	George Russell snatches Canadian GP pole from team-mate Antonelli with final-lap effort; Mercedes lock out front row	65067bf7	George Russell,Kimi Antonelli,Canadian Grand Prix,F1,Mercedes
2026-06-05	Pakistan hold nerve to beat Australia by four wickets, clinch ODI series 2-1 in Lahore	fd5778a1	Pakistan,Australia,Shadab Khan,Shaheen Shah Afridi,ODI
