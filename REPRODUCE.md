# How this repository was made (Autonomous Region of Bougainville)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Autonomous Bougainville Government: Bougainville Constitution (PDF) | <https://abg.gov.pg/government/constitution> | 2026-10-30 | No licence statement on the site; reproduced as an official publication with attribution. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of the Autonomous Region of Bougainville | 1 | 2004-11-12 to 2004-11-12 |

The build made 1 commits:

| Commits | Kind |
| ---: | --- |
| 1 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 1 laws in the record.
- 2 tags.

## Dates

Each commit is dated at noon (Pacific/Bougainville) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: The Constitution is dated by the day the Bougainville Constituent Assembly adopted it (12 November 2004), as its certificate gives; it came into operation in stages on days the published text does not state. https://abg.gov.pg/uploads/documents/BOUGAINVILLE_CONSTITUTION_2004.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `d41038c44b124d4ddbffe7c290291977630364ee48ff1865c53ac6f02b7a067b` (537572 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `35388bee5aa05369f7da68f5a8fa015ea8d442b8`, `check.py` `5d719354ea4c62d240c93d2cae446307d81d9e81`, `on.py` `aff48cf1b68d50c7ba8f399ca32261871c301824`.
- Python 3.14.4; git version 2.53.0.

## Checks

1 versions of 1 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- One version: the Constitution as adopted on 12 November 2004, the text the Autonomous Bougainville Government publishes. It is dated by the adoption day its certificate gives, because the gazettal and return-of-writs days on which it came into operation are not stated in the source.
- Amendments made since 2004 (the ABG lists a Bougainville Constitution (Amendment) Act 2015) are not online as text from an official source, so they are not recorded; the record ends at the 2004 text.
- Text is read with Xpdf pdftotext -layout, page by page. The running title and page number of every page and the arrangement of sections (pages 3-16) are left out; the arrangement inside Schedule 10 is kept, as printed. Part and Division headings are kept in structure.md, not in the section files.
- Paragraphs are rebuilt from the layout: a new paragraph starts at a subsection or paragraph marker, at an all-capitals heading, or at a flush-left line after a list item. Words hyphenated at a line end are joined. Curly quotes become straight quotes.
- Each Schedule is one file. Under Section 10(2), Schedules 3, 4, 6.1, 7, 8 and 9 repeat provisions of National Constitutional Laws for ease of reference; they are kept as printed in the Bougainville Constitution.
- The table of electoral offences in Schedule 10, Section 142 is read with pdftotext -table and written one row per line, "offence | punishment" (the " | " is added; the words are as printed).
- Two places where the layout reading order differs from the printed sense are put right: the paragraph number 5.7.1, printed level with the second line of the heading of Schedule 5.7, goes before its paragraph; and "Sec. 187", printed beside the heading "SCHEDULE 6.", goes after it, as in the other Schedules.
- Checked: the letters and digits of every unit and heading, in order, equal those of the PDF read a second time with pypdf (pages 3-16, running titles and page numbers left out).

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- A model (Claude) wrote the parse code and chose the layout; it wrote no law text. Every word of law comes from the Autonomous Bougainville Government's PDF.
