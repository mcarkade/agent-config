"""Extract or replace the narration (first argument of every say call) in a chapter script.

python tools/narr.py extract ch01          -> narr/ch01.txt  ("NNN| text" per say, with on-screen ops as context)
python tools/narr.py apply ch01            <- narr/ch01.new  ("NNN| new text"; lines not listed keep their text)
"""
import ast, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NARR = ROOT / 'narr'
NARR.mkdir(exist_ok=True)


def says(src):
    out = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'say' and node.args \
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            out.append(node)
    return sorted(out, key=lambda n: (n.lineno, n.col_offset))


def offset(lines, ln, col):
    return sum(len(l) for l in lines[:ln - 1]) + col


def extract(ch):
    src = (ROOT / 'chapters' / f'{ch}.py').read_text(encoding='utf8')
    lines = src.splitlines(keepends=True)
    rows = []
    for i, n in enumerate(says(src)):
        a = offset(lines, n.args[1].lineno, n.args[1].col_offset) if len(n.args) > 1 else None
        b = offset(lines, n.end_lineno, n.end_col_offset)
        ops = re.sub(r'\s+', ' ', src[a:b - 1]) if a else ''
        rows.append(f'{i:03d}| {n.args[0].value}\n     [screen] {ops}\n')
    (NARR / f'{ch}.txt').write_text(''.join(rows), encoding='utf8')
    print(ch, len(rows), 'lines,', sum(len(n.args[0].value.split()) for n in says(src)), 'words')


def apply(ch):
    path = ROOT / 'chapters' / f'{ch}.py'
    src = path.read_text(encoding='utf8')
    new = {}
    for l in (NARR / f'{ch}.new').read_text(encoding='utf8').splitlines():
        m = re.match(r'^(\d{3})\|\s?(.*)$', l)
        if m:
            new[int(m.group(1))] = m.group(2).strip()
    lines = src.splitlines(keepends=True)
    nodes = says(src)
    bad = [k for k in new if k >= len(nodes)]
    assert not bad, f'indices out of range: {bad}'
    for i in sorted(new, reverse=True):          # edit from the end so offsets stay valid
        arg = nodes[i].args[0]
        a = offset(lines, arg.lineno, arg.col_offset)
        b = offset(lines, arg.end_lineno, arg.end_col_offset)
        src = src[:a] + repr(new[i]) + src[b:]
    ast.parse(src)
    path.write_text(src, encoding='utf8')
    print(ch, 'replaced', len(new), 'of', len(nodes))


if __name__ == '__main__':
    {'extract': extract, 'apply': apply}[sys.argv[1]](sys.argv[2])
