"""Parse the Constitution of the Autonomous Region of Bougainville (2004, as adopted) from the PDF published by the
Autonomous Bougainville Government into corpus.d/10-constitution.json.

    python -X utf8 parse.py <pdf>

Reads the PDF with Xpdf's pdftotext (-layout; -table for the table of electoral offences in Schedule 10). Page by page: the running title (first line) and the page number
(last line) are dropped; the arrangement of sections (pages 3-16) is left out. One unit per section, per schedule,
for the preamble and for the endorsement and certificate; Part and Division headings go in `structure`.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / '.cache' / 'BOUGAINVILLE_CONSTITUTION_2004.pdf'
URL = 'https://abg.gov.pg/uploads/documents/BOUGAINVILLE_CONSTITUTION_2004.pdf'
RUNNING = 'Constitution of the Autonomous Region of Bougainville.'
DIVISION = re.compile(r'^Division\s+(?:\d+\.?\s*)?[–-]|^Division\s+\d+\.\s+[A-Z]')
MARK = re.compile(r'^["“]?\((?:[0-9]+[A-Za-z]?|[a-z]{1,2}|[ivxl]+)\)')


def pages(pdf: Path) -> list[list[str]]:
    out = subprocess.run(['pdftotext', '-enc', 'UTF-8', '-layout', str(pdf), '-'], capture_output=True, check=True)
    text = out.stdout.decode('utf-8')
    res = []
    for p in text.split('\f'):
        lines = [l.rstrip() for l in p.replace('\r', '').split('\n')]
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip():
            lines.pop(0)
        if not lines:
            continue
        if lines[-1].strip() and re.fullmatch(r'-\s*\d+\s*-', lines[-1].strip()):
            lines.pop()
        if lines and lines[0].strip() == RUNNING:
            lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
        res.append(lines)
    return res


def norm(s: str) -> str:
    s = s.replace(' ', ' ').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', s).strip()


def is_upper(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def paragraphs(lines: list[str], preamble: bool = False) -> list[str]:
    """Join layout lines into paragraphs. A paragraph starts at a subsection or paragraph marker, at an
    all-capitals line (a heading), or, after a list item, at a flush-left line (the words closing the list).
    In the preamble each recital starts flush left."""
    paras: list[list] = []  # [text, start indent, is heading]
    pending = None
    for raw in lines:
        if not raw.strip():
            continue
        ind = len(raw) - len(raw.lstrip())
        s = norm(raw)
        upper = (is_upper(s) and len(s) < 200) or bool(DIVISION.match(s))
        new = False
        if raw.startswith(ROW):
            s = norm(raw[len(ROW):])
            new, upper = True, False
        elif not paras:
            new = True
        elif MARK.match(s):
            new = True
        elif upper:
            # heading lines: a wrapped heading continues while the line before it has no closing full stop
            prev = paras[-1]
            new = bool(DIVISION.match(s) or SEC.match(s)
                       or (re.match(r'^PART\b', s) and prev[0].endswith(('.', ',')))) or not (
                prev[2] and not prev[0].endswith('.'))
        elif paras[-1][2] and DIVISION.match(paras[-1][0]) and not paras[-1][0].endswith('.'):
            new = False  # a Division heading wrapped onto a second line
        elif paras[-1][2]:
            new = True
        elif preamble and ind == 0:
            new = True
        elif paras[-1][1] >= 14 and ind < 5:
            new = True
        moved = re.match(r'^(\d+(?:\.\d+)+)\s+(.+)$', s) if (upper and not new) else None
        if moved:
            own = re.match(r'^(\d+(?:\.\d+)*)\.?\s', paras[-1][0])
            if not (own and moved.group(1).startswith(own.group(1) + '.')):
                moved = None
        if moved:
            # a paragraph number printed at the start of a heading's second line (Schedule 5.7.1): it belongs to
            # the paragraph after the heading
            pending, s = moved.group(1), moved.group(2)
        elif new and pending:
            s, pending = f'{pending} {s}', None
        if new:
            paras.append([s, ind, upper])
        else:
            prev = paras[-1]
            if re.search(r'[A-Za-z]-$', prev[0]) and s[:1].isalpha():
                prev[0] = prev[0] + s
            else:
                prev[0] = prev[0] + ' ' + s
    return [p[0] for p in paras]


ROW = '\x00row '
TABLE_HEAD = 'Column 1. – Offences'


def offences_table(pdf: Path, first: int, last: int) -> list[str]:
    """The two-column table of Schedule 10, Section 142 (pdf pages first..last), read with pdftotext -table: one line
    per row, "offence | punishment"; a row starts where column 1 starts with its number."""
    out = subprocess.run(['pdftotext', '-enc', 'UTF-8', '-table', '-f', str(first), '-l', str(last), str(pdf), '-'],
                         capture_output=True, check=True).stdout.decode('utf-8')
    lines = [l.rstrip() for l in out.replace(chr(13), '').replace(chr(12), chr(10)).split(chr(10))]
    a = next(i for i, l in enumerate(lines) if l.strip().startswith(TABLE_HEAD))
    b = next(i for i, l in enumerate(lines) if re.match(r'143\.\s+PROHIBITION', l.strip()))
    rows: list[list[list[str]]] = []
    head = [p.strip() for p in re.split(r'\s{2,}', lines[a].strip())]
    for l in lines[a + 1:b]:
        t = l.strip()
        if not t or t == RUNNING or re.fullmatch(r'-\s*\d+\s*-', t):
            continue
        ind = len(l) - len(l.lstrip())
        if ind >= 30:
            c1, c2 = '', t
        else:
            parts = re.split(r'\s{2,}', t, maxsplit=1)
            c1, c2 = parts[0], (parts[1] if len(parts) > 1 else '')
        if re.match(r'^\d+\.', c1):
            rows.append([[c1], [c2] if c2 else []])
        else:
            if c1:
                rows[-1][0].append(c1)
            if c2:
                rows[-1][1].append(c2)
    res = [ROW + ' | '.join(head)]
    for c1, c2 in rows:
        res.append(ROW + norm(' '.join(c1)) + ' | ' + norm(' '.join(c2)))
    return res


SEC = re.compile(r'^(\d+)([A-Z]?)\.\s+(.+)$')
SCH = re.compile(r'^(?:Secs?\.\s.*?\s{2,})?\s*SCHEDULE\s+(\d+)\.?\s*$')


def main() -> None:
    raw = PDF.read_bytes()
    pg = pages(PDF)
    # the preamble: pages 1-2; the arrangement of sections up to the page that opens with PART I.
    body_start = next(i for i, p in enumerate(pg) if i > 2 and p and norm(p[0]).startswith('PART I.'))
    pre = [l for p in pg[:2] for l in p]
    toc_at = next(i for i, l in enumerate(pre) if norm(l) == 'ARRANGEMENT OF SECTIONS') if any(
        norm(l) == 'ARRANGEMENT OF SECTIONS' for l in pre) else len(pre)
    pre = pre[:toc_at]
    body = [l for p in pg[body_start:] for l in p]
    # split off the endorsement and certificate (last two pages)
    end_at = next(i for i, l in enumerate(body) if norm(l).startswith('ENDORSEMENT OF THE CONSTITUTION'))
    endorse, body = body[end_at:], body[:end_at]
    # the table of electoral offences (Schedule 10, Section 142): rebuilt row by row from its two columns
    ta = next(i for i, l in enumerate(body) if l.strip().startswith(TABLE_HEAD))
    tb = next(i for i, l in enumerate(body) if l.strip().startswith('143. PROHIBITION'))
    tpage = next(i for i, p in enumerate(pg) if any(l.strip().startswith(TABLE_HEAD) for l in p)) + 1
    body[ta:tb] = offences_table(PDF, tpage, tpage + 2)
    sch_at = next(i for i, l in enumerate(body) if norm(l) == 'SCHEDULES.')
    secs_lines, sch_lines = body[:sch_at], body[sch_at:]

    units: dict[str, dict] = {}
    pre_paras = paragraphs(pre, preamble=True)
    units['preamble'] = {'label': 'Preamble', 'kind': 'preamble', 'text': '\n'.join(pre_paras) + '\n'}

    structure: list[str] = []
    paras = paragraphs(secs_lines)
    cur = None
    last = 0
    for p in paras:
        m = SEC.match(p)
        if m and is_upper(m.group(3)) and int(m.group(1)) in (last, last + 1) and (int(m.group(1)) == last + 1 or m.group(2)):
            n, suf = int(m.group(1)), m.group(2)
            key = f'sec-{n:03d}' + (f'-{suf.lower()}' if suf else '')
            cur = key
            last = n
            units[key] = {'label': f'Section {n}{suf}', 'kind': 'sec', 'lines': [f'# {p}']}
        elif (is_upper(p) and p.startswith('PART ')) or DIVISION.match(p):
            structure.append(f'# {p}')
            if cur:
                units[cur].setdefault('after', []).append(p)
        elif re.match(r'^Division\b', p):
            structure.append(f'# {p}')
        elif cur is None:
            structure.append(f'# {p}')
        else:
            units[cur]['lines'].append(p)
    # Part/Division headings sit between sections; keep them only in `structure`
    for k, u in list(units.items()):
        if k.startswith('sec-'):
            u.pop('after', None)
            u['text'] = '\n'.join(u.pop('lines')) + '\n'

    # schedules: one unit each, split at the "SCHEDULE N." lines; Schedule 10 opens with its own arrangement
    blocks: list[tuple[int, list[str]]] = []
    head: list[str] = []
    for l in sch_lines:
        m = SCH.match(l.strip()) or SCH.match(l)
        if m:
            n = int(m.group(1))
            if blocks and blocks[-1][0] == n:
                blocks[-1][1].append(l)  # the second "SCHEDULE 10." heading after its arrangement
                continue
            pre = re.match(r'^\s*(Secs?\.\s.*?)\s{2,}SCHEDULE', l)
            # "Sec. 187   SCHEDULE 6." (layout order): the heading first, then its section reference
            blocks.append((n, [f'SCHEDULE {n}.', pre.group(1)] if pre else [l]))
        elif blocks:
            blocks[-1][1].append(l)
        else:
            head.append(l)
    nums = [b[0] for b in blocks]
    if nums != list(range(1, len(nums) + 1)):
        raise SystemExit(f'schedules out of order: {nums}')
    structure.extend(f'# {p}' for p in paragraphs(head))
    for n, ls in blocks:
        units[f'sch-{n:02d}'] = {'label': f'Schedule {n}', 'kind': 'schedule', 'text': '\n'.join(paragraphs(ls)) + '\n'}
    units['endorsement'] = {'label': 'Endorsement and certificate', 'kind': 'certificate',
                            'text': '\n'.join(paragraphs(endorse)) + '\n'}
    units['structure'] = {'label': 'Structure', 'kind': 'headings', 'text': '\n'.join(structure) + '\n'}

    secs = [k for k in units if k.startswith('sec-')]
    print(f'{len(secs)} sections ({secs[0]}..{secs[-1]}), {len(blocks)} schedules, {len(structure)} headings',
          file=sys.stderr)

    part = {
        'country': {
            'code': 'PG-NSB', 'name': 'Autonomous Region of Bougainville', 'slug': 'papua-new-guinea-bougainville',
            'lang': 'en', 'tz': 'Pacific/Bougainville', 'future_branch': 'future',
            'publisher': {'name': 'Autonomous Bougainville Government (abg.gov.pg)', 'email': 'abg@abg.gov.pg.invalid'},
            'default_in_force_rule': {
                'text': 'The Constitution is dated by the day the Bougainville Constituent Assembly adopted it '
                        '(12 November 2004), as its certificate gives; it came into operation in stages on days '
                        'the published text does not state.',
                'source': URL},
            'licence_note': 'Text: Constitution of the Autonomous Region of Bougainville, as published by the '
                            'Autonomous Bougainville Government (abg.gov.pg). The site carries no licence statement; '
                            'the text is reproduced as an official publication, with attribution.',
        },
        'sources': [{
            'name': 'Autonomous Bougainville Government: Bougainville Constitution (PDF)',
            'url': 'https://abg.gov.pg/government/constitution',
            'retrieved': '2026-10-30',
            'licence': 'No licence statement on the site; reproduced as an official publication with attribution.',
            'notes': f'{URL}, sha256 {hashlib.sha256(raw).hexdigest()}.',
        }],
        'laws': {
            'constitution-2004': {
                'label': 'Bougainville Constitution 2004',
                'title': 'Constitution of the Autonomous Region of Bougainville, adopted by the Bougainville '
                         'Constituent Assembly at Buin on 12 November 2004',
                'kind': 'law', 'enacted': '2004-11-12', 'published': None, 'url': URL,
                'temporary_until': None, 'restores': None, 'note': None},
        },
        'acts': [{
            'slug': 'constitution',
            'short': 'Bougainville Constitution',
            'title': 'Constitution of the Autonomous Region of Bougainville',
            'url': URL,
            'first_law': 'constitution-2004',
            'earlier_laws': [],
            'versions': [{
                'from': '2004-11-12',
                'source_url': URL,
                'sha256': hashlib.sha256(raw).hexdigest(),
                'units': {k: {kk: vv for kk, vv in v.items()} for k, v in sorted(units.items())},
                'credits': {},
                'note': 'The text as adopted by the Bougainville Constituent Assembly on 12 November 2004, as the '
                        'Autonomous Bougainville Government publishes it. Under its preamble Part XXV came into '
                        'operation on the day after its publication in the National Gazette following endorsement '
                        'by the Head of State, and the rest on the day fixed for the return of the writs in the '
                        'first general election; the published text gives neither day. Later amendments, such as '
                        'the Bougainville Constitution (Amendment) Act 2015, are not included.',
            }],
        }],
        'decisions': [
            'One version: the Constitution as adopted on 12 November 2004, the text the Autonomous Bougainville '
            'Government publishes. It is dated by the adoption day its certificate gives, because the gazettal and '
            'return-of-writs days on which it came into operation are not stated in the source.',
            'Amendments made since 2004 (the ABG lists a Bougainville Constitution (Amendment) Act 2015) are not '
            'online as text from an official source, so they are not recorded; the record ends at the 2004 text.',
            'Text is read with Xpdf pdftotext -layout, page by page. The running title and page number of every page and '
            'the arrangement of sections (pages 3-16) are left out; the arrangement inside Schedule 10 is kept, as '
            'printed. Part and Division headings are kept in structure.md, not in the section files.',
            'Paragraphs are rebuilt from the layout: a new paragraph starts at a subsection or paragraph marker, at '
            'an all-capitals heading, or at a flush-left line after a list item. Words hyphenated at a line end are '
            'joined. Curly quotes become straight quotes.',
            'Each Schedule is one file. Under Section 10(2), Schedules 3, 4, 6.1, 7, 8 and 9 repeat provisions of '
            'National Constitutional Laws for ease of reference; they are kept as printed in the Bougainville '
            'Constitution.',
            'The table of electoral offences in Schedule 10, Section 142 is read with pdftotext -table and written '
            'one row per line, "offence | punishment" (the " | " is added; the words are as printed).',
            'Two places where the layout reading order differs from the printed sense are put right: the paragraph '
            'number 5.7.1, printed level with the second line of the heading of Schedule 5.7, goes before its '
            'paragraph; and "Sec. 187", printed beside the heading "SCHEDULE 6.", goes after it, as in the other '
            'Schedules.',
            'Checked: the letters and digits of every unit and heading, in order, equal those of the PDF read a '
            'second time with pypdf (pages 3-16, running titles and page numbers left out).',
        ],
        'ai_use': ['A model (Claude) wrote the parse code and chose the layout; it wrote no law text. Every word of '
                   'law comes from the Autonomous Bougainville Government\'s PDF.'],
    }
    out = HERE / 'corpus.d' / '10-constitution.json'
    tmp = out.with_suffix('.tmp')
    tmp.write_text(json.dumps(part, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    os.replace(tmp, out)
    print('wrote', out, file=sys.stderr)


if __name__ == '__main__':
    main()
