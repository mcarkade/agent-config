"""Merge reviewer replacements (narr/review_chNN.txt) into narr/chNN.new, then apply to the chapter script.

python tools/merge_review.py ch07 [--skip 012,018]
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ch = sys.argv[1]
skip = set(sys.argv[sys.argv.index('--skip') + 1].split(',')) if '--skip' in sys.argv else set()
rev = {}
for l in (ROOT / 'narr' / f'review_{ch}.txt').read_text(encoding='utf8').splitlines():
    m = re.match(r'^(\d{3})\|\s?(.*)$', l)
    if m and m.group(1) not in skip:
        rev[m.group(1)] = m.group(2).strip()
new_p = ROOT / 'narr' / f'{ch}.new'
lines = new_p.read_text(encoding='utf8').splitlines()
seen = set()
for i, l in enumerate(lines):
    m = re.match(r'^(\d{3})\|', l)
    if m and m.group(1) in rev:
        lines[i] = f'{m.group(1)}| {rev[m.group(1)]}'
        seen.add(m.group(1))
missing = set(rev) - seen
assert not missing, f'review lines not in .new: {missing}'
new_p.write_text('\n'.join(lines) + '\n', encoding='utf8')
print(ch, 'merged', len(rev))
subprocess.run([sys.executable, str(ROOT / 'tools' / 'narr.py'), 'apply', ch], check=True)
