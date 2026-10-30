"""Letters-and-digits check of corpus.d/10-constitution.json against the PDF, read a second time with pypdf (the
parse uses poppler's pdftotext). Pages 3-16 (arrangement of sections), each page's running title and page number
are left out of the source; the Part/Division headings (structure) are cut out of the source in order, and the rest
must equal preamble + sections + schedules + endorsement, letter for letter and digit for digit.

    python -X utf8 check_letters.py [pdf]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import pypdf

HERE = Path(__file__).resolve().parent
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / '.cache' / 'BOUGAINVILLE_CONSTITUTION_2004.pdf'


def alnum(s: str) -> str:
    s = unicodedata.normalize('NFKC', s)
    return ''.join(c for c in s if c.isalnum())


def main() -> int:
    r = pypdf.PdfReader(str(PDF))
    src = []
    for i, page in enumerate(r.pages):
        if 2 <= i <= 15:
            continue
        lines = page.extract_text().replace('\r', '').split('\n')
        keep = []
        for l in lines:
            t = l.strip()
            if t == 'Constitution of the Autonomous Region of Bougainville.':
                continue
            if re.fullmatch(r'-\s*\d+\s*-', t):
                continue
            keep.append(l)
        src.append(alnum('\n'.join(keep)))
    S = ''.join(src)
    part = json.loads((HERE / 'corpus.d' / '10-constitution.json').read_text(encoding='utf-8'))
    units = part['acts'][0]['versions'][0]['units']
    # walk the source in document order: each unit's text must follow at the cursor; the Part/Division headings
    # (structure, in order) are consumed only where the next unit does not follow
    heads = [alnum(h.lstrip('# ')) for h in units['structure']['text'].splitlines()]
    order = ['preamble'] + sorted(k for k in units if k.startswith('sec-')) + sorted(
        k for k in units if k.startswith('sch-')) + ['endorsement']
    cur, hi = 0, 0
    for k in order:
        t = alnum(units[k]['text'].replace('# ', '', 1) if k.startswith('sec-') else units[k]['text'])
        while not S.startswith(t, cur) and hi < len(heads) and S.startswith(heads[hi], cur):
            cur += len(heads[hi]); hi += 1
        if not S.startswith(t, cur):
            j = next((i for i in range(min(len(t), len(S) - cur)) if S[cur + i] != t[i]), min(len(t), len(S) - cur))
            print(f'MISMATCH in {k} at {j}:'); print('source:', S[cur + j - 80:cur + j + 80]); print('repo:  ', t[j - 80:j + 80])
            return 1
        cur += len(t)
    while hi < len(heads) and S.startswith(heads[hi], cur):
        cur += len(heads[hi]); hi += 1
    if cur != len(S) or hi != len(heads):
        print(f'left over: source {len(S) - cur} characters, {len(heads) - hi} headings'); print(S[cur:cur + 200])
        return 1
    print(f'OK: all {len(S)} letters and digits of the source equal the repo text, in order '
          f'({len(order)} units + {len(heads)} headings)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
