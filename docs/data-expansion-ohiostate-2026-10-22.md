# Ohio State CDS expansion — October 22, 2026

Scope: `src/data/schools/ohiostate.json`, Ohio State **Columbus Campus** only. No regional-campus numbers, application-code changes, registry changes, commits, or worktrees. Other agents' school changes were left alone.

## Official sources and year verification

The [Institutional Research and Planning archive](https://irp.osu.edu/institutional-data-and-reports) links all ten Columbus CDS years from 2016–2017 through its newest published report, 2025–2026. Every target year was found there; no Wayback or mirror fallback was needed. The institution and CDS year were checked inside each PDF, including rendered form-field headers for the recent reports. Year keys identify the CDS report, not the publication URL date, fall entry year alone, or the G1 expense year.

| CDS year | Official PDF | PDF pages | SHA-256 |
| --- | --- | ---: | --- |
| 2016–2017 | [Columbus 2016–2017](https://irp.osu.edu/media/192) | 19 | `381398ad7b8927386f9c463beeb845404c8f1131d894da3c109e9111543908a4` |
| 2017–2018 | [Columbus 2017–2018](https://irp.osu.edu/media/197) | 25 | `cf47b2a1d7d2d00190b12963bdaa7cb83d67d993d87ce807a7899a58989eca77` |
| 2018–2019 | [Columbus 2018–2019](https://irp.osu.edu/media/202) | 25 | `926df2a3cdcc9d441df6b1cc6f83162815884b33c43183aebe93ee20f3f5ab1f` |
| 2019–2020 | [Columbus 2019–2020](https://irp.osu.edu/media/208) | 28 | `37f19665c3c23001265c34740f991dfbb819ff7a038f7049d6e08b4fb4eca6b0` |
| 2020–2021 | [Columbus 2020–2021](https://irp.osu.edu/media/214) | 28 | `06d64a0726b544ffeb088f2ab67286ad0cd3d2cb4a5ec2fae627c0210b8b4644` |
| 2021–2022 | [Columbus 2021–2022](https://irp.osu.edu/media/220) | 28 | `64521177944cb8a4b7fa2d28588530cd88dc9badf56334022cefb70c5907d45c` |
| 2022–2023 | [Columbus 2022–2023](https://irp.osu.edu/media/264) | 38 | `7deb89de130d8c19bf9c5c4945d26ab1547f5f745a4c851295cd5237b7527a37` |
| 2023–2024 | [Columbus 2023–2024](https://irp.osu.edu/media/270) | 187 | `c9ed722686f331d4c75921642bd9dfecdd26ccbe4a8bf2562faa2354bfd96739` |
| 2024–2025 | [Columbus 2024–2025](https://irp.osu.edu/media/276) | 50 | `68ffa355be54488ceea66d53cc445a65b22ad830d423a9b29e9f87e3b53ce25b` |
| 2025–2026 | [Columbus 2025–2026](https://irp.osu.edu/sites/default/files/documents/2026/03/CDS-2025-2026-OSU-Columbus-Campus.pdf) | 50 | `47ad8c68770dc89275c5b7d3468b567cfdfdb2c8837d074b068bb418643e9d1a` |

All page references below are **1-based PDF page numbers**. Some printed footers differ: for example, 2022–2023 H2 is PDF page 29, printed page 37. The 2023–2024 official download has unusually expanded accessibility pagination; use PDF pages 7–10, 19–20, 26, 59–60, and 70–71 for the relevant data.

## Reproducible evidence and assembly

Gitignored evidence lives in `College-Data/ohiostate/`: downloaded PDFs; `sources.json` with URLs, hashes, sizes, and download times; archive `discovery.html`/`discovery.json`; prepared text/image pages and indexes; generated extractor prompts; `extract/<year>.primary.json`, `.secondary.json`, and `.final.json`; the baseline `before.json`; and merge/reconciliation audit files.

The repository add-college skill was followed with the user's GPT-only override. Primary extraction was completed without reading the secondary extraction. A separate T3 Codex child independently read the `prompt.py --extractor secondary` prompts and source pages for all ten years. Both used `gpt-6.1-sol`, with inherited options `reasoningEffort=high`, `serviceTier=default`. No Claude model and no `crosscheck.py` run were used. Reconciliation uses `compare.py --left primary --right secondary`; source-page decisions use `resolve.py` and are retained in finals.

The existing profile, including its historical residency methodology note, is preserved exactly. Factors were not republished from a different year. Because `assemble.py` replaces every year with a final file and can erase profile notes, selective assembly uses the same `fields.derive_year` function and merges missing leaves into the baseline. Only the explicitly documented aid/cost corrections may replace existing numbers. No stale final can overwrite an entire historical year. `merge_verified.py` and `merge-audit.json` retain the exact operation.

## Population and source-page decisions

| CDS year | C1 admissions | C9 scores | B1/B2 enrollment/race | H2 aid |
| --- | --- | --- | --- | --- |
| 2016–2017 | p4 | p6 | p2 | p14 |
| 2017–2018 | p6 | p8 | p2 | p19 |
| 2018–2019 | p6 | p8 | p2 | p19 |
| 2019–2020 | p7 | rates p9; scores p10 | p3 | A p21; D/H/J/K p22 |
| 2020–2021 | p7 | p10 | p3 | A/D/H p21; J/K p22 |
| 2021–2022 | p7 | p10 | p3 | A/D p21; H/J/K p22 |
| 2022–2023 | p9 | p12 | p4 | p29 |
| 2023–2024 | pp19–20 | p26 | undergraduate p8, graduate p9, race pp9–10 | A p70; D/H/J/K p71 |
| 2024–2025 | p13 | p19 | pp5–6 | p33 |
| 2025–2026 | p13 | p19 | pp5–6 | p33 |

- **C1:** gender enrollment includes the explicitly printed full-time and part-time rows. Total applications, offers, enrollments, acceptance rates, and yield are assembled from verified C1 inputs. No other/unknown-gender blank is changed to zero. For 2023–2024, C1 p19 reports 3,809 enrolled men (3,795 full-time plus 14 part-time), while B1 p7 has 13 part-time men; C1 governs admissions. The comparable 2024–2025 B1 p5 female part-time entry is 21 while C1 p13 has 22; C1 governs the admissions count of 5,025 women. Do not force these tables to agree.
- **B2:** use the rightmost total-undergraduate counts, including non-degree-seeking students. Do not substitute the degree-seeking or first-year columns. The new 2025–2026 undergraduate headcount is 46,627, not the degree-seeking subtotal 45,433.
- **H2:** use full-time undergraduates including first-years, not the first-year-only column. `percentReceivingAid` follows the site's H2 D/A convention (need-determined students awarded aid divided by full-time degree-seeking undergraduates); it does not count every recipient of merit-only aid. `percentNeedFullyMet` is H/D, not row I's average percentage of need met. J and K are the full-time undergraduate dollar amounts. H1 identifies these as source estimates; the extraction does not independently estimate amounts.
- **Stale aid captions:** 2017–2018 and 2018–2019 H2 p19 retain a Fall 2016 template phrase, but the report/H1 year and different current cohorts establish the report-year tables. The 2025–2026 H2 p33 row A retains a Fall 2024 caption; its 42,888 full-time degree-seeking total agrees with 2025 B1 p5. Keep the printed values and disclose the stale caption.
- **Form fields:** prepared text omits most 2024–2025 and 2025–2026 numeric cells. Rendered pp5–6, 13, 19, 29, and 33 were consulted; absence from text is not evidence of an empty source cell.
- **2016–2017 old SAT, p6:** Critical Reading 540/670 and Writing 560/660 are separate old-SAT sections, not the current EBRW field. They are not copied into `sat.readingWriting`; Math 620/740, ACT 27/31, and SAT/ACT submission fractions 0.32/0.84 are supported. No SAT composite or median is manufactured.
- **G1:** the new 2016–2017 report p13 explicitly supplies 2017–2018 expenses: undergraduate continuing/transfer tuition $10,036.80 and room/board $12,252. The required-fee cell is blank, so neither a fee zero nor a complete derived total is added. First-year tuition $10,591.40 is not used.
- **Recent G1:** 2024–2025 p29 explicitly supplies 2024–2025 costs while marking the next year's amounts unavailable. Its undergraduate cells are tuition $12,180, fees $1,064, and food/housing $14,810. The first-year tuition/fee combination $13,641 and food/housing $15,252 do not describe the selected undergraduate column. The new 2025–2026 p29 requests 2026–2027 costs, marks them unavailable with a July 1 availability note, yet prints undergraduate tuition $12,545, fees $1,096, and food/housing $16,222. Those amounts are transcribed from this report; the checked unavailability statement limits any claim about their expense-calendar year.

## Remaining gaps and retained legacy caveats

No target CDS year remains missing. ED is marked unavailable/not offered and its count cells are blank; EA is offered, but most years supply dates rather than applicant/admit counts; 2023-2024 p35 is the verified exception added here. No ED/EA zeros are introduced. Older C9 tables omit medians; 2016–2017 through 2018–2019 omit SAT composites. No percentile is interpolated or assembled from section percentiles. No new net-price statistic is inferred from unrelated aid fields.

The new years omit residency breakdowns because F1 percentages do not establish undergraduate in-state/out-of-state headcounts. The eight existing residency blocks and their profile note are retained from the earlier import; they remain documented estimates and are **not newly independently verified headcounts**.

The earlier cost series is also retained outside the narrowly evidenced 2024–2025 correction. Official undergraduate tuition is a range in 2017–2018 through 2022–2023 (G1 pp16, 16, 19, 18, 18, 24), and undergraduate housing is a range in 2019–2020 through 2022–2023. The earlier import often selected first-year amounts and used zero fees. This expansion creates no additional range endpoint, fee-zero, or first-year substitute. In 2023–2024 pp59–60, undergraduate tuition is $12,485, its housing cell is blank, and the printed $15,258 housing amount occupies the first-year column. That legacy cost block is left intact for a separate historical-cost cleanup rather than partially replacing it with mixed populations. The 2018–2019 p16 undergraduate housing cell is $12,434, versus $12,708 in the old first-year import; its complete legacy cost block likewise remains untouched. These retained blocks must not be cited as output of the current independent extraction.

No official-source retrieval failure remains. The first sandboxed archive request failed with `URLError: [WinError 10061] ... target machine actively refused it`; approved network execution succeeded. Initial sandboxed `uv` page preparation reported cache access denied at `...uv/cache/sdists-v9/.git`; approved cache access succeeded. Every manifest PDF downloaded directly from the official source; no HTML masquerading as PDF, unavailable archive year, failed mirror, or unresolved download was used.

## Published changes and validation


The publication expanded from **8 to 10 years** and **250 to 442 numeric leaves** outside the profile: **192 added numeric leaves**, plus **17 clearly evidenced corrections**. No existing numeric leaf was removed.

| CDS year | Before numeric leaves | After numeric leaves | Added leaves | Added content |
| --- | ---: | ---: | ---: | --- |
| 2016-2017 | 0 | 35 | 35 | New year: admissions and gender counts; supported SAT/ACT fields; enrollment and race; scalar costs; aid |
| 2017-2018 | 28 | 42 | 14 | Gender admissions; SAT/ACT section percentiles and submission rates |
| 2018-2019 | 28 | 42 | 14 | Gender admissions; SAT/ACT section percentiles and submission rates |
| 2019-2020 | 24 | 44 | 20 | Gender admissions; SAT/ACT percentiles and rates; four aid statistics |
| 2020-2021 | 24 | 44 | 20 | Gender admissions; SAT/ACT percentiles and rates; four aid statistics |
| 2021-2022 | 24 | 44 | 20 | Gender admissions; SAT/ACT percentiles and rates; four aid statistics |
| 2022-2023 | 38 | 48 | 10 | Gender admissions; four aid statistics |
| 2023-2024 | 42 | 50 | 8 | Gender admissions; two Early Action counts |
| 2024-2025 | 42 | 48 | 6 | Gender admissions |
| 2025-2026 | 0 | 45 | 45 | New year: admissions and gender counts; SAT/ACT percentiles and rates; enrollment and race; costs; aid |

### Exact corrections to previously populated fields

These changes replace an incorrect population/column or transcription, not a valid historical measurement. Aid uses H2 A/D/H/J/K in the full-time undergraduate column. The 2024-2025 J/K amounts and D/A ratio already agreed with that population and were preserved.

| CDS year | Field | Before | After | Source and decision |
| --- | --- | ---: | ---: | --- |
| 2017-2018 | `financialAid.averageAidPackage` | 14976 | 13960 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2017-2018 | `financialAid.averageNeedBasedGrant` | 11497 | 10325 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2017-2018 | `financialAid.percentReceivingAid` | 0.4795 | 0.4704 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2017-2018 | `financialAid.percentNeedFullyMet` | 0.2441 | 0.192 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2018-2019 | `financialAid.averageAidPackage` | 14925 | 14537 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2018-2019 | `financialAid.averageNeedBasedGrant` | 11692 | 11252 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2018-2019 | `financialAid.percentReceivingAid` | 0.4482 | 0.4592 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2018-2019 | `financialAid.percentNeedFullyMet` | 0.2723 | 0.2037 | H2 p19 full-time undergraduates; ratios D/A and H/D |
| 2023-2024 | `financialAid.averageAidPackage` | 18536 | 17890.04 | H2 A p70, D/H/J/K p71; preserve printed cents |
| 2023-2024 | `financialAid.averageNeedBasedGrant` | 16203 | 15188.27 | H2 A p70, D/H/J/K p71; preserve printed cents |
| 2023-2024 | `financialAid.percentReceivingAid` | 0.4279 | 0.4139 | H2 A p70, D/H/J/K p71; preserve printed cents |
| 2023-2024 | `financialAid.percentNeedFullyMet` | 0.2667 | 0.2275 | H2 A p70, D/H/J/K p71; preserve printed cents |
| 2024-2025 | `costs.tuition` | 13641 | 12180 | G1 p29 undergraduate column; total is 12180 + 1064 + 14810 |
| 2024-2025 | `costs.fees` | 0 | 1064 | G1 p29 undergraduate column; total is 12180 + 1064 + 14810 |
| 2024-2025 | `costs.roomAndBoard` | 15252 | 14810 | G1 p29 undergraduate column; total is 12180 + 1064 + 14810 |
| 2024-2025 | `costs.totalCOA` | 28893 | 28054 | G1 p29 undergraduate column; total is 12180 + 1064 + 14810 |
| 2024-2025 | `financialAid.percentNeedFullyMet` | 0.3409 | 0.3462 | H2 p33 H=5723, D=16532; H/D rounded to four decimals |

### Reconciliation decisions

The first comparison produced **347 agreed numeric inputs**, **11 numeric single-source inputs**, and **one numeric conflict**. The secondary also extracted 18 C7 factors in each year; all 180 factor single-source entries were dropped from these numeric finals to preserve the existing profile, rather than publishing unpaired factor changes. C7 source pages are 2016-2017 p5; 2017-2018/2018-2019 p7; 2019-2020/2020-2021/2021-2022 p8; 2022-2023 p10; 2023-2024 p22; 2024-2025/2025-2026 p16.

All numeric manual decisions were checked against the rendered source page:

| CDS year | Action | Fields/values | PDF page and reason |
| --- | --- | --- | --- |
| 2023-2024 | Accept three single-source inputs | C1 applied 70,028; admitted 35,588; enrolled 8,062 | p20 prints all-gender totals, agreeing with C1 gender counts on p19 |
| 2023-2024 | Accept two single-source additions | EA applied 48,937; admitted 29,573 | p35 explicitly reports Fall 2023 Early Action counts. The reported EA enrollment 7,128 has no schema field and is not published |
| 2024-2025 | Accept three single-source inputs | C1 applied 72,829; admitted 44,116; enrolled 9,607 | p14 prints all-gender totals; no residency category is substituted for an all-undergraduate demographic count |
| 2025-2026 | Accept three single-source inputs | C1 applied 81,392; admitted 40,047; enrolled 8,248 | p14 prints all-gender totals, matching p13 gender rows |
| 2025-2026 | Resolve conflict to primary | `raw.H2.d = 16579` | p33 clearly prints 16,579 in row D full-time undergraduates. Secondary had transposed it to 15,679. Keep A=42,888, H=2,548, J=$20,866, K=$17,614 |

All ten final files have zero unresolved conflicts and zero single-source entries after these decisions.

### Validation

`python -I scripts/cds/validate.py ohiostate` passed with **0 errors and 1 warning**:

```text
ohiostate: ok (0 errors, 1 warnings)
  warn  2024-2025: tuition fell from 13244 to 12180
```

The tuition-decline warning was rechecked against 2024-2025 G1 p29. $12,180 is the printed undergraduate tuition before $1,064 required fees. The preceding legacy $13,244 is the 2023-2024 first-year amount (p60), so the warning reflects the retained older cost convention meeting the corrected undergraduate column, not evidence to overwrite the verified value. No warning was suppressed.

The baseline scoped validator had 0 errors/0 warnings. Global Zod/schema/type checks and local page inspection are assigned to the parent task. The existing profile and residency note compare exactly to `before.json`. All baseline numeric leaves remain present; only the 17 corrections above differ.

