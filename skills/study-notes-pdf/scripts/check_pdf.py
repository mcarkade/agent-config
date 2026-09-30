"""Check the exported PDF and render every page for human review."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import fitz


def check(pdf, manifest, render_dir):
    data = json.loads(manifest.read_text(encoding='utf8'))
    errors = []
    with fitz.open(pdf) as doc:
        if len(doc) != data['pages']:
            errors.append('Page count differs from layout manifest')
        expected = [(u['id'] + ' ' + u['title'], u['page']) for u in data['units']]
        if data['mode'] == 'full':
            expected.insert(0, ('Index', 1))
        actual = [(entry[1], entry[2]) for entry in doc.get_toc()]
        if actual != expected:
            errors.append('Bookmark destinations differ from units')
        if len(doc.get_toc()) != len(data['units']) + (data['mode'] == 'full'):
            errors.append('Missing or extra bookmarks')
        xrefs = {page.xref: page.number + 1 for page in doc}
        all_links = []
        for page in doc:
            text = page.get_text()
            if 'Abhinav Pullela . mcarkade' not in text:
                errors.append(f'Page {page.number + 1}: missing branding')
            if f'{page.number + 1} / {len(doc)}' not in text:
                errors.append(f'Page {page.number + 1}: wrong footer page count')
            if '\ufffd' in text or '\u25a0' in text:
                errors.append(f'Page {page.number + 1}: possible missing glyph')
            leaks = r'(?:[A-Za-z]:[\\/]|file://|SKILL\.md|AGENTS\.md|layout_metrics\.json|As an AI|AI-generated|Co-Authored-By)'
            if re.search(leaks, text, re.I):
                errors.append(f'Page {page.number + 1}: internal path or attribution')
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        x0, y0, x1, y1 = span['bbox']
                        if x0 < 47 or x1 > page.rect.width - 47 or y0 < 10 or y1 > page.rect.height - 10:
                            errors.append(f'Page {page.number + 1}: text outside margins')
            links = page.get_links()
            footer_links = []
            for link in links:
                obj = doc.xref_object(link['xref'])
                match = re.search(r'/Dest\s*\[\s*(\d+) 0 R', obj)
                if match:
                    dest = xrefs.get(int(match[1]))
                    if dest is None:
                        errors.append(f'Page {page.number + 1}: invalid internal destination')
                    if link['from'].y0 > page.rect.height - 45:
                        footer_links.append(dest)
                    elif page.number == 0 and data['mode'] == 'full':
                        all_links.append(dest)
                elif link.get('kind') == fitz.LINK_URI:
                    if urlsplit(link.get('uri', '')).scheme not in ('http', 'https'):
                        errors.append(f'Page {page.number + 1}: non-web source link')
                else:
                    errors.append(f'Page {page.number + 1}: unresolved link')
            if footer_links != [1]:
                errors.append(f'Page {page.number + 1}: incorrect return link')
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(
                str(render_dir / f'page_{page.number + 1:03}.png'))
        if data['mode'] == 'full' and all_links != [u['page'] for u in data['units']]:
            errors.append('Index links differ from unit pages')
        for b in data['blocks']:
            if b['bottom'] < 48 or b['top'] > doc[0].rect.height - 42:
                errors.append(f"Page {b['page']}: block outside content bounds")
            if b['kind'] == 'eq' and b['scale'] < .80:
                errors.append(f"Page {b['page']}: equation is too small")
        report = dict(pages=len(doc), units=len(data['units']),
                      index_links=len(all_links), errors=errors,
                      remaining='Inspect every rendered page; verify mathematics, source coverage and external URLs.')
    (render_dir / 'checks.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    if errors:
        raise ValueError('\n'.join(errors))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pdf', type=Path)
    ap.add_argument('--manifest', required=True, type=Path)
    ap.add_argument('--render-dir', required=True, type=Path)
    args = ap.parse_args()
    args.render_dir.mkdir(parents=True, exist_ok=True)
    print(json.dumps(check(args.pdf, args.manifest, args.render_dir), indent=2))


if __name__ == '__main__':
    main()
