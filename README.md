# Autonomous Region of Bougainville: law in git

The law of the Autonomous Region of Bougainville (Papua New Guinea) in git: one file per section of its Constitution, in the form the Autonomous Bougainville Government publishes it. `git blame` and `tools/on.py` work as in the other repositories of the shared design.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `pg-nsb/`. The national law is in [lexifina/papua-new-guinea-law](https://github.com/lexifina/papua-new-guinea-law).

The text is in English, the language of the official text.

## What this repository holds

**The Constitution as adopted in 2004, and nothing later yet.** One act, one version: the Constitution of the Autonomous Region of Bougainville, as adopted by the Bougainville Constituent Assembly at Buin on 12 November 2004. Amendments made since then (the Autonomous Bougainville Government lists a Bougainville Constitution (Amendment) Act 2015) are not included, because their text is not published online by an official source. The Acts of the Bougainville House of Representatives are not included yet: the Government's site lists their titles only.

| Folder | Act | Files | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the Autonomous Region of Bougainville | 253 | as adopted, dated 12 November 2004 |

## Source

"Bougainville Constitution", the PDF published by the Autonomous Bougainville Government at
<https://abg.gov.pg/government/constitution>. It is the fair copy certified by the Chairman of the Bougainville
Constituent Assembly, followed by the Governor-General's endorsement.

## Dates

- The Constitution has one commit, dated at **noon, Pacific/Bougainville**, on 12 November 2004, the day the Bougainville Constituent Assembly adopted it, as its certificate gives. It is credited to that adoption.
- It came into operation in stages: Part XXV on the day after its publication in the National Gazette following endorsement by the Head of State, and the rest on the day fixed for the return of the writs in the first general election. The published text gives neither day, so the record uses the adoption day.

## Files

`constitution/sec-007.md` is Section 7, `sch-05.md` Schedule 5, `preamble.md` the Preamble, `endorsement.md` the Governor-General's endorsement and the Chairman's certificate; `structure.md` holds the Part and Division headings. The first line of a section file is its number and heading; then one paragraph per line. Schedules 3, 4, 6.1, 7, 8 and 9 repeat provisions of the National Constitution and Organic Laws, as printed in the Bougainville Constitution (Section 10). The table of electoral offences in Schedule 10, Section 142 is written one row per line, "offence | punishment".

## How it is checked

- The Constitution is read back from git on the day of its version and the day before (`tools/check_repo.py`); both must match `corpus.json`.
- The letters and digits of the whole repository text (preamble, sections, headings, schedules and the endorsement, in order) equal those of the PDF body, read a second time with a separate PDF parser.

## Limits

This is not an official publication. It records the Constitution as adopted in 2004 only: it does not show the amendments made since, so it is not the text in force today. Check the current text with the Autonomous Bougainville Government before relying on it.
