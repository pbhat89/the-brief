# Companion editorial policy

## Mandatory source checklist · effective 26 October 2026

Before research and scripting, follow [the agreed-source coverage contract](SOURCE_COVERAGE.md). Attempt every member of the fresh X roster and every agreed source/category; independently sweep India politics, Modi/BJP/government, opposition, policy, economics and major national developments. Account for each discovered item and every blocked, partial or unvisited source. Concise news narration does not reduce the research obligation. Full upstream reconciliation is not full source coverage.

The private prepublication editorial audit must contain actual `source_coverage`; its existing CLI gate rejects missing checklists and routine-budget excuses for unattempted sources. Genuine source blocks yield explicitly partial coverage, never all-green or full-window cursor advancement. A hard platform failure needs structured evidence under the standing blocked-work rule. Retain pending work. The October25 historical audit remains partial; no recording is regenerated. No external saved prompt or schedule is changed by these repository instructions.


Effective for new editions from 20 October 2026. These companion-only rules implement the 19 October listener feedback. They do not rewrite an already published edition or change the original Claude brief, Gmail workflow, accounts, permissions, schedule or free-tier limits. Read this file and [editorial-policy.json](editorial-policy.json) at the start of each external run. Record the repository revision privately. The external task must be configured separately to load these files; a Worker redeploy alone cannot change narration.

## Conditions and substantive Singapore news

- Keep routine Singapore weather and air quality together to about **20–30 seconds**: the practical forecast and a concise air-quality observation with an observation time. Do not recite every region's PSI/PM2.5 or routinely add health/safety advice. Do not turn ordinary weather into several stories.
- Expand only for a verified, materially actionable official alert or major disruption. Record its primary-source URL and why the normal budget is insufficient. No inferred haze warning, stale numbers presented as current, or formulaic daily safety announcement.
- Research **2–3 substantive fresh Singapore stories** when supported: policy, economy, transport, housing, public services, technology, society or major local developments. Weather does not satisfy this target. Recheck the latest upstream general-news brief, then verify and fill genuine gaps from trusted original reporting. Cross-check prior editions for repeated events. Never pad; document a verified-news shortfall in the report.

## Selective insurance and reinsurance news

Research the latest **insurance and reinsurance developments, especially life and health**, without a daily story quota or guaranteed segment. Prioritize concrete, potentially useful AI applications and evidence: underwriting, claims, pricing, actuarial work, servicing, fraud detection and health outcomes. Explain what changed, who could use it, what evidence supports the benefit and its practical limits. Otherwise include only material industry news, such as consequential regulation, major transactions, solvency or capital developments, market shifts or significant product/coverage changes. Routine marketing, minor launches and generic AI commentary do not qualify merely because they mention insurance.

Verify against primary insurer, reinsurer or regulator publications and original research; use reputable reporting for discovery and context. Preserve the actual event/publication date. Attribute vendor or company claims explicitly and distinguish an announcement, pilot, deployment and measured outcome. A partnership or product launch is not proof of efficacy; report the measurement basis, limitations and uncertainty when citing benefits. Do not turn research findings into medical advice or recommendations about an individual's insurance.

Deduplicate the **underlying event across every section, source and available prior edition**, including AI, business, Singapore news and podcast recaps. An already covered event needs a named material new fact and a link to its earlier coverage; a different headline or source is not enough. Keep stable event IDs and evidence in the existing delivery ledger, and disclose missing history rather than claim complete dedup. Narrate a qualifying item once, briefly in the best-fitting business or AI passage, within the existing 10–12-minute target. When nothing new meets this threshold, omit it from both narration and report: no empty heading, “nothing new” announcement, filler or padding. Record any research access gaps privately.

## One useful expert lesson

Aim for **one 45–75-second learning insight**, rotating Andrej Karpathy, Andrew Ng, Yann LeCun and Naval Ravikant by value and novelty. It may be recent or evergreen. Useful themes include technical intuition, coding practice, the AI transition, learning and management. Explain the idea, its limits and one concrete application; clearly distinguish the expert's sourced view from editorial interpretation. An older source is labelled evergreen or given its original date, never presented as fresh news. Do not use a daily “nothing new from these experts” roll call.

Use [EXPERT_LEARNING_LOG.md](EXPERT_LEARNING_LOG.md) and the source-backed [expert-learning-log.json](expert-learning-log.json). Research can grow the candidate log. Before selection, complete the all-history semantic check, including near-equivalent lessons from another expert. A different URL or wording is not a new insight. Keep covered concepts permanently, without a 30-day expiry. Publish the delivered concept's dated usage only after the edition is published; uncertain publication is reconciled before retry. If nothing suitable is verified, omit the segment and disclose the source gap in the report, rather than fabricate or repeat it.

## Everyday AI and Big Technology

Check Everyday AI first, across videos/live and official episode/blog/newsletter surfaces. Use genuinely new originals and actual accessible transcripts with references. Exclude Start Here, reruns, reuploads and previously covered episodes, even if a recent upload lacks a replay label.

When no eligible Everyday AI episode is available, use **Big Technology Podcast with Alex Kantrowitz**. Read [PODCAST_LEARNING.md](PODCAST_LEARNING.md), [podcast-learning-ledger.json](podcast-learning-ledger.json) and the initial [source review](big-technology-source-review.json). Initially capture a fixed queue of the most recent three verified originals, newest first within that frozen set. Cover at most one episode in an edition and at most one new recap per Singapore date; a retry or revised edition does not get another slot. An eligible Everyday AI episode pauses the fallback queue. Preserve the queue across days rather than reinitializing it on every run. Once that finite queue is exhausted, use only the latest unseen eligible original. Do not refill the old backlog.

Both shows require original publication identity/date separate from a later upload, a stable episode key, an actual transcript and segment references. Descriptions and titles establish discovery, never a substantive recap. An inaccessible transcript stays pending or blocked, never covered. Mark covered only after publication and reconcile uncertain publication before retry. Put access diagnostics and source counts in HTML/evidence, not spoken filler.

## Tight ending and private quality gate

Finish with a short sourced interesting fact and a brief sign-off, **20 seconds maximum in total**. A single useful improvement sentence is optional and must fit inside that budget. Omit process narration, repeated summaries, rambling transitions and routine safety reminders. Keep encouragement in the opening only.

Keep the coherent order: welcome/mindset, concise conditions, Singapore/India/world/business/sports, AI and podcast learning with the expert insight, interesting fact and close. Measure the rendered audio, with 10–12 minutes as a target rather than permission to pad. Preserve the one-voice, pronunciation, volume, private-publishing and mobile requirements in the companion README.

Before publication, copy the explicitly synthetic [editorial-audit.example.json](editorial-audit.example.json) format into private runtime storage and replace every value with real checks; the example is not edition evidence. Keep this private editorial audit containing measured chapter seconds, source-backed Singapore story IDs, any exception/shortfall reasons, expert concept IDs and recap identity. Run `node podcast/validate-editorial.mjs --audit /absolute/private/audit.json`. This required CLI checks the selected expert ID against the current log: it must be an unused candidate marked `reviewed_no_match`, with the matching directly checked primary source. For a recap, also supply `podcast_selection_context` using the context contract in `PODCAST_LEARNING.md`, and add `transcript_source_url` and `transcript_provenance` to the recap. The CLI checks the Singapore date, current source/dedup evidence, eligible canonical episode, one-per-day state and exact transcript provenance against the podcast ledger. Calling only the low-level audit-format function does not perform these cross-log checks. Never commit the personalized transcript, private audit, listener URLs or receipts. The checks validate supplied measurements and contracts; they cannot verify that measurements are truthful, that an insight is good, or that two differently worded ideas are semantically distinct. The operator must read/listen and review sources.

Run the dependency-free checks with `node podcast/validate-editorial.mjs`, `node podcast/validate-expert-learning.mjs`, `node podcast/validate-podcast-learning.mjs` and `node --test podcast/*.test.mjs`. CI runs these alongside existing publication and player checks. A passing deployment verifies the tested player build, not the next episode's editorial quality or physical-phone playback.


## Audible structure and intuitive explanation · 21 October 2026

Apply the latest listener feedback to both news and topic podcasts. Open with a short roadmap, group related points into clearly introduced sections, and use brief spoken transitions plus audible pauses between them. A heading in HTML is not a substitute for a transition in the recording. End a substantive learning section with one concise takeaway before moving on; avoid repetitive wrap-ups or padding.

Explain intuition first, illustrate it with a simple concrete example, connect it explicitly to a business decision or workflow, and then add technical detail where it improves understanding. Preserve nuance and evidence limits. Distinguish the source's claims from editorial examples and applications. Do not assume expertise makes intuitive explanation unnecessary. Check the final script and measured chapter breaks, while treating listener comprehension as distinct from structural validation. Earlier recordings are not regenerated solely for this change.


## Headline-first news and complete intake reconciliation · 22 October 2026

Latest listener feedback supersedes deeper treatment of news items: each NEWS item gets a broad headline and at most one short factual context sentence. Do not insert assistant opinions, takes, analogies or business advice between news items. Preserve coherent section handoffs and audible pauses. Distinct podcast/expert learning segments retain intuitive explanations, simple examples and clearly separated applications.

Use the same-day upstream HTML as a complete intake checklist, including every sports item. Account for every item as covered, materially updated, duplicate, stale or insufficiently verified with evidence and a reason; do not arbitrarily choose one of several sports stories. The checklist does not override factual verification, date accuracy or permanent delivered-event dedup. If upstream is absent, use only its format and independently verify current reporting. Do not regenerate delivered audio merely for this wording change.
