"""Fetch English auto-subtitles (text only) of recent Physics Explained videos into ../pe_transcripts/."""
import sys, re, json
from pathlib import Path
import yt_dlp

OUT = Path(__file__).resolve().parent.parent / 'pe_transcripts'
OUT.mkdir(exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 15

with yt_dlp.YoutubeDL({'extract_flat': True, 'quiet': True, 'playlistend': 40}) as y:
    info = y.extract_info('https://www.youtube.com/@PhysicsExplainedVideos/videos', download=False)
ents = [e for e in info['entries'] if (e.get('duration') or 9999) > 480][:N]
print(len(ents), 'videos')

opts = {'skip_download': True, 'writesubtitles': True, 'writeautomaticsub': True, 'subtitleslangs': ['en', 'en-orig'],
        'subtitlesformat': 'vtt', 'outtmpl': str(OUT / '%(id)s.%(ext)s'), 'quiet': True, 'ignoreerrors': True}
with yt_dlp.YoutubeDL(opts) as y:
    y.download([e['url'] for e in ents])

titles = {e['id']: e.get('title', '') for e in ents}
for v in sorted(OUT.glob('*.vtt')):
    vid = v.name.split('.')[0]
    lines, prev = [], None
    for ln in v.read_text(encoding='utf8', errors='ignore').splitlines():
        if '-->' in ln or not ln.strip() or ln.startswith(('WEBVTT', 'Kind:', 'Language:')):
            continue
        t = re.sub(r'<[^>]+>', '', ln).strip()
        if t and t != prev:
            lines.append(t)
            prev = t
    # auto-subs repeat rolling lines; dedupe consecutive duplicates
    text = ' '.join(dict.fromkeys(lines))
    (OUT / f'{vid}.txt').write_text(f'# {titles.get(vid, vid)}\n{text}\n', encoding='utf8')
    v.unlink()
print('done', len(list(OUT.glob('*.txt'))))
