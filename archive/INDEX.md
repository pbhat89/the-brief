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
2026-06-05	Singapore graduates earn less than expected in most fields, MOM data shows	f09a46bb	MOM,Singapore,graduates
2026-06-05	Three Chinese nationals charged with MBS robbery after their flight out of Singapore was recalled	3b72ea74	MBS,Singapore,robbery
2026-06-05	US strikes Iran's Qeshm Island; Iranian drones kill one at Kuwait airport and target Bahrain on Day 96	73533226	IRGC,Iran,Kuwait,Bahrain
2026-06-05	US House passes 215–208 war-powers resolution directing Trump to end Iran hostilities	d0698f91	US House,Trump,Iran,war-powers resolution
2026-06-05	Anthropic picks Morgan Stanley and Goldman Sachs for IPO, projecting $10.9B revenue in Q2	ea29888a	Anthropic,Morgan Stanley,Goldman Sachs,IPO
2026-06-05	Microsoft Build 2026: Suleyman aims to "eliminate" Anthropic costs as seven new models launch	f35448d1	Microsoft,Mustafa Suleyman,Anthropic,Build 2026
2026-06-05	Dow Jones surges 875 points to record 51,562 as investors rotate from tech to cyclicals	fbb8e958	Dow Jones,Broadcom,UnitedHealth,JPMorgan
2026-06-05	Quantinuum raises $1.68 billion in Nasdaq IPO, opens at $68 against $60 pricing	366337d3	Quantinuum,Honeywell,Nasdaq
2026-06-05	Roland Garros: Andreeva and qualifier Chwalinska reach women's final after contrasting semi-final wins	e216b866	Roland Garros,Mirra Andreeva,Maja Chwalinska,Anna Kalinskaya
2026-06-05	Kyle Jamieson takes 5 for 62 as England collapse to 140 in 1st Test at Lord's	3fdca8a8	Kyle Jamieson,England,New Zealand,Lord's
