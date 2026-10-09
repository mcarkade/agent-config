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
    minimal_sheet = data.get('theme') == 'white_minimal' and data.get('mode') == 'cram'
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
            if not minimal_sheet:
                if 'Abhinav Pullela . mcarkade' not in text:
                    errors.append(f'Page {page.number + 1}: missing branding')
                if f'{page.number + 1} / {len(doc)}' not in text:
                    errors.append(f'Page {page.number + 1}: wrong footer page count')
            if '\ufffd' in text or '\u25a0' in text:
                errors.append(f'Page {page.number + 1}: possible missing glyph')
            leaks = r'(?:[A-Za-z]:[\\/]|file://|SKILL\.md|AGENTS\.md|layout_metrics\.json|As an AI|AI-generated|Co-Authored-By)'
            if re.search(leaks, text, re.I):
                errors.append(f'Page {page.number + 1}: internal path or attribution')
            page_spans=[]
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        page_spans.append(span)
                        x0, y0, x1, y1 = span['bbox']
                        if x0 < 47 or x1 > page.rect.width - 47 or y0 < 10 or y1 > page.rect.height - 10:
                            errors.append(f'Page {page.number + 1}: text outside margins')
            if minimal_sheet:
                title=data.get('title','')
                title_lines=[span for span in page_spans if span['text'].strip()==title and span['bbox'][1]<90]
                if page.number==0 and len(title_lines)!=1:
                    errors.append('Standalone sheet title must appear once at the top of page 1')
                if page.number>0 and title_lines:
                    errors.append(f'Page {page.number + 1}: repeated standalone title')
                if any(span['bbox'][1]>page.rect.height-35 for span in page_spans):
                    errors.append(f'Page {page.number + 1}: standalone sheet has footer text')
            links = page.get_links()
            footer_links = []
            for link in links:
                obj = doc.xref_object(link['xref'])
                match = re.search(r'/Dest\s*\[\s*(\d+) 0 R', obj)
                if match:
                    dest = xrefs.get(int(match[1]))
                    if dest is None:
                        errors.append(f'Page {page.number + 1}: invalid internal destination')
                    xyz = re.search(r'/XYZ\s+([-\d.]+)\s+([-\d.]+)\s+null', obj)
                    if not xyz or abs(float(xyz[1])) > .01 or abs(float(xyz[2]) - page.rect.height) > .01:
                        errors.append(f'Page {page.number + 1}: internal link does not explicitly land at page top')
                    if link['from'].y0 > page.rect.height - 45:
                        footer_links.append(dest)
                    elif page.number == 0 and data['mode'] == 'full':
                        all_links.append(dest)
                elif link.get('kind') == fitz.LINK_URI:
                    if urlsplit(link.get('uri', '')).scheme not in ('http', 'https'):
                        errors.append(f'Page {page.number + 1}: non-web source link')
                else:
                    errors.append(f'Page {page.number + 1}: unresolved link')
            if minimal_sheet:
                if footer_links:
                    errors.append(f'Page {page.number + 1}: standalone sheet has a footer link')
            elif footer_links != [1]:
                errors.append(f'Page {page.number + 1}: incorrect return link')
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(
                str(render_dir / f'page_{page.number + 1:03}.png'))
        if data['mode'] == 'full' and len(all_links) == 2 * len(data['units']):
            paired_links=[]
            for index in range(0,len(all_links),2):
                if all_links[index] != all_links[index+1]:
                    errors.append('Index title and page links have different destinations')
                paired_links.append(all_links[index])
            all_links=paired_links
        if data['mode'] == 'full' and all_links != [u['page'] for u in data['units']]:
            errors.append('Index links differ from unit pages')
        for b in data['blocks']:
            if b['bottom'] < 48 or b['top'] > doc[0].rect.height - 42:
                errors.append(f"Page {b['page']}: block outside content bounds")
            if b['kind'] == 'eq' and b['scale'] < .80:
                errors.append(f"Page {b['page']}: equation is too small")
        if len({u['page'] for u in data['units']}) != len(data['units']):
            errors.append('Full module/question units must each begin a fresh page')
        first_content = 2 if data['mode'] == 'full' else 1
        if {b['page'] for b in data['blocks']} != set(range(first_content, len(doc) + 1)):
            errors.append('Accidental blank content page')
        for unit_index,u in enumerate(data['units']):
            rows = [b for b in data['blocks'] if b['unit'] == u['id']]
            inset=82 if minimal_sheet and unit_index==0 else 42
            expected_top=doc[0].rect.height-inset
            if abs(u.get('start_top', expected_top) - expected_top) > .01:
                errors.append(f"{u['id']}: module/question heading is not at the fresh-page start")
            for i, b in enumerate(rows[:-1]):
                if b['kind'] in ('question', 'example_label', 'solution_label') and b['page'] != rows[i + 1]['page']:
                    errors.append(f"{u['id']}: detached opening or solution label on page {b['page']}")
                if b['kind'] == 'solution_label':
                    stem = next((v for v in reversed(rows[:i]) if v['kind'] in ('question', 'example_label')), None)
                    if stem and stem['page'] != b['page']:
                        errors.append(f"{u['id']}: question stem separated from Solution")
            minutes = u.get('estimated_minutes')
            if minutes is not None:
                label = '~' + format(minutes, 'g') + ' min'
                occurrences = sum(p.get_text().splitlines().count(label) for p in doc)
                expected_count = sum(v.get('estimated_minutes') == minutes for v in data['units'])
                if occurrences != expected_count:
                    errors.append('Unit estimates repeated or missing')
            if sum(p.get_text().count(u['id'] + ' ' + u['title']) for p in doc) != 1:
                errors.append(f"{u['id']}: repeated or missing continuation heading")
        minutes = sum(u.get('estimated_minutes') or 0 for u in data['units'])
        if data.get('estimated_minutes', minutes) != minutes:
            errors.append('Total estimate differs from unit sum')
        if data['mode'] == 'full' and minutes and doc[0].get_text().splitlines().count('~' + format(minutes, 'g') + ' min total') != 1:
            errors.append('Missing or inconsistent total estimate')
        boxes_path = manifest.parent / 'boxes.json'
        if boxes_path.exists():
            for b in json.loads(boxes_path.read_text(encoding='utf8')):
                if b['bottom'] < 48 or b['top'] > doc[0].rect.height - 42 or b['left'] < 36 or b['left'] + b['width'] > doc[0].rect.width - 36:
                    errors.append(f"Page {b['page']}: fitted box outside content bounds")
        palette_path = manifest.parent / 'palette.json'
        if palette_path.exists():
            palette = json.loads(palette_path.read_text(encoding='utf8'))
            amber = tuple(int(palette['link'][i:i + 2], 16) / 255 for i in (1, 3, 5))
            amber_int = int(palette['link'][1:], 16)
            for page in doc:
                rules = []
                for drawing in page.get_drawings():
                    color = drawing.get('color')
                    if color and max(abs(a - b) for a, b in zip(color, amber)) < .01 and abs(drawing['width'] - .35) < .01:
                        for item in drawing['items']:
                            if item[0] == 'l' and abs(item[1].y - item[2].y) < .1:
                                rules.append((min(item[1].x, item[2].x), max(item[1].x, item[2].x), item[1].y))
                spans = [s for b in page.get_text('dict')['blocks'] for line in b.get('lines', []) for s in line['spans']]
                for link in page.get_links():
                    for span in spans:
                        if fitz.Rect(span['bbox']).intersects(link['from']):
                            x0, _, x1, _ = span['bbox']; baseline = span['origin'][1]
                            if span['color'] != amber_int or not any(a <= x0 + 1 and b >= x1 - 1 and baseline - .5 <= y <= baseline + 4 for a, b, y in rules):
                                errors.append(f"Page {page.number + 1}: clickable text lacks thin amber underline")
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
