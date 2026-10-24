# Agreed-source coverage gate

Effective for new editions from **26 October 2026**. Read this with the editorial policy before researching, not after scripting. Research breadth and concise spoken selection are separate obligations. A 32/32 upstream checklist, an accurate script, or successful audio/deployment tests do not establish that all agreed sources were researched.

## Required work

Freeze the current X Starter Pack roster and its retrieval time/content hash. Enumerate every canonical handle, including unattempted members. The observed count was 211 on October 25; future runs use the actual fresh roster, not a hard-coded denominator. Attempt every profile where permitted, preserving the earlier successful full-window boundary and unresolved gaps. A header, logged-out snapshot, pinned post, earliest/latest visible timestamp or HTTP200 does not establish complete timeline coverage. Non-roster sources are separate rows, not substitutes for missing roster members. Never bypass access restrictions.

Independently search India politics, Modi/BJP/government, opposition, government policy, economics and major national developments before selecting stories. Inspect public Inshorts national, politics and business surfaces, then trace consequential claims to original/primary sources. Record actual queries, candidates and dispositions. Upstream reconciliation is not an independent category sweep. This requires breadth, not a party quota, equal political airtime, a ten-story quota or padding.

Also account for independent Singapore, world, business, sports and science discovery; official weather, PSI, PM2.5 and advisories; Everyday AI Videos, Live, episodes, blog, AI News and newsletter; the current Big Technology original feed and any selected actual transcript; the expert knowledge log and selected primary contribution; and selective insurance/reinsurance discovery. The expert slot remains one useful insight drawn from four thinkers, not four daily lessons. RSS/original-source and transcript verification can establish a Big Technology selection; do not invent a daily YouTube obligation, or imply an unattempted channel was checked.

Enumerate every discovered item in the retained discovery set, including pending items. For video listings, keep video/episode IDs, displayed metadata, verified original versus upload identity, replay/reupload aliases, transcript access/provenance and the segments actually reviewed. Retrieving a listing is not watching every video; downloading a transcript is not reading every minute. Unknown dates remain null with a reason, or date-only with explicit precision, never guessed midnight or search-index/retrieval time.

## Private format and mechanical gate

`source-coverage.example.json` is **synthetic**, not a researched edition. `source-coverage-contract.mjs` exports pure validation and release checks. Put the real checklist inside the private measured editorial audit as `source_coverage`. The existing required command invokes this gate for editions on/after October26:

    node podcast/validate-editorial.mjs --audit /absolute/private/audit.json

If same-day upstream is unavailable after an actual check, record availability and reconciliation as `unavailable`, zero dispositions, the gap reason and independent current-news verification. Do not fabricate an available-item matrix.

The checklist includes edition, recorded time, requested window, fresh roster snapshot, one row per required surface/category/profile, item dispositions, upstream reconciliation, exact gaps and pending recovery work. Each source row preserves its prior full-window cursor and oldest unresolved gap, with an unresolved window that cannot be reset to yesterday’s partial checkpoint. Completion evidence must explicitly cover that entire window, separately from the run’s focus window. Each source row records attempts (URL/time/method/outcome), access status, scope, queries, item-derived counts and whether its full-window cursor may advance. `REQUIRED_SOURCE_IDS` defines agreed non-roster rows. Roster row IDs are lowercase `x:handle` and must reference the current snapshot hash. Additional source rows are allowed. Fixed Inshorts and Everyday surfaces must have attempts at their actual target URLs; visiting another tab or a fallback does not certify the required page.

Access status: `unattempted`, `blocked`, `header_only`, `partial_content`, `accessible`. Coverage scope: `full_window`, `bounded_snapshot`, `unknown`. Only accessible content with no pending items/gaps and explicit traversal/end-of-window evidence can be marked full-window. Counts derive from item rows: discovered = reviewed + pending; reviewed = retained + excluded. Retained, duplicate, stale, insufficiently verified, immaterial and pending remain separate decisions. Duplicates reference an earlier event; a material update states the specific new fact. Selected episode recaps require an original and actual reviewed transcript segments, alongside the existing episode-ledger gate.

Keep **three independent results**: upstream reconciliation, required-source attempts and full-window source coverage. The spoken selection has its own editorial/evidence checks. All required attempts can be complete while source coverage remains partial. Technical validators establish structural consistency, not factual truth, genuine browser activity, semantic dedup or listening quality; inspect the source evidence as well.

## Partial releases and pending work

- Unattempted mandatory sources fail the normal prepublication gate. A routine runtime budget, early freeze or short spoken duration is not a waiver.
- Genuine attempted access blocks or bounded content may permit a useful **PARTIAL** edition under the standing blocked-work instruction. State exact attempted/unvisited/blocked/pending denominators and unresolved windows in HTML, never “all sources checked” or “exhaustive.” Keep pending work rather than discarding it at the daily cutoff.
- A hard execution/platform failure preventing attempts requires a structured `platform_failure`: `kind: verified-platform-failure`, a code of `executor_unavailable`, `tool_service_outage` or `run_terminated`, actual occurrence time, failed operation, error, private evidence reference, exactly affected unattempted source IDs and `standing_blocked_work_rule: true`. This is evidence of an existing blocker, not a new permission or operator-written budget exception. Verify the evidence; the validator cannot authenticate it.
- Partial sources cannot advance full-window/profile/global cursors or erase historical gaps. Research observations, selection, rendering, publication and accepted delivery remain distinct states. Existing publication and delivery ledgers advance only after their required evidence.

The [October25 retrospective checklist](source-coverage/2026-10-25.html) records historical partial work without inventing attempts or changing the recording. Historical-format evidence can be valid while completeness fails. The new gate is not retroactive certification.

This repository contains contracts and instructions, not a bundled collector. The existing external task reads README, editorial policy, run feedback and improvements each run; those entry points now require this checklist. No saved external prompt, schedule, access setting or credentials were changed by this update, and code deployment does not prove a future run has performed the research.
