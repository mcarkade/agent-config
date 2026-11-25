"""Build chapters.

  python make.py ch03 --check     layout + maths check with estimated timing (fast, no audio)
  python make.py ch03 --sheet     --check plus contact sheets of every beat in review/ch03/
  python make.py ch03 --tts       cache the chapter voice before starting a render
  python make.py ch03 --render    voice + subtitles + video -> out/ch03.mp4
  python make.py --join NAME [ch01-ch08 ...]
                                  join out/ch*.mp4 (or the listed chapters) into out/NAME.mp4 with chapter
                                  markers, and write out/NAME_timestamps.txt (chapters + every question)
"""
import json, math, os, re, runpy, subprocess, sys, tempfile, time
from pathlib import Path
import studio

ROOT = Path(__file__).resolve().parent
CHAPTERS = ROOT / 'chapters'


def load(name):
    studio.say_target[0] = None
    source = CHAPTERS / f'{name}.py'
    if not source.is_file():
        raise SystemExit(f'{name}: chapter source missing at {source}')
    runpy.run_path(str(source), run_name='chapter')
    ch = studio.say_target[0]
    if ch is None:
        raise SystemExit(f'{name}: no Chapter(...) created')
    for i, (text, _, _) in enumerate(ch.beats):
        if text and not any(c.isalnum() for c in text):
            raise SystemExit(f'{name}: beat {i} has no spoken words: {text!r}; use wait() for a deliberate hold')
    return ch


def report(name, ch, st, est):
    words = sum(len(b[0].split()) for b in ch.beats)
    qs = sum(1 for b in ch.beats for op in b[1] if op.kind == 'question')
    longest = max((st.beat_ends[i] - (st.beat_ends[i - 1] if i else 0)) for i in range(len(st.beat_ends))) if st.beat_ends else 0
    print(f'{name}: {len(ch.beats)} beats, {words} words, {qs} questions, '
          f'{"estimated " if est else ""}length {st.total / 60:.1f} min, longest beat {longest:.1f} s')
    if st.errors:
        print(f'{len(st.errors)} PROBLEMS:')
        for e in st.errors[:60]:
            print('  -', e)
    else:
        print('layout OK')


def main():
    args = sys.argv[1:]
    if '--join' in args:
        rest = [a for a in args if a != '--join']
        join(rest[0] if rest else 'video', rest[1:]); return
    name = args[0]
    ch = load(name)
    if '--render' in args or '--tts' in args:
        texts = [b[0] for b in ch.beats if b[0]]
        t0 = time.time()
        studio.tts_batch(texts)
        print(f'tts done in {time.time() - t0:.0f}s')
        if '--render' not in args:
            return
        infos = {i: studio.tts_info(b[0]) for i, b in enumerate(ch.beats) if b[0]}
        durs = [infos[i][1] if i in infos else 0 for i in range(len(ch.beats))]
        st = studio.compile_chapter(ch, durs)
        report(name, ch, st, False)
        if st.errors:
            raise SystemExit(1)
        out = studio.WORK / 'out'
        out.mkdir(exist_ok=True)
        t0 = time.time()
        # PE_SPARSE=1 sends only the frames that change; the encoder restores constant frame rate
        # and the render fails if any frame is lost. Much faster on long static boards.
        sparse = os.environ.get('PE_SPARSE') == '1'
        studio.render(st, infos, out / f'{name}.mp4', sparse=sparse)
        studio._replace_bytes(out / f'{name}.questions.json', json.dumps(st.questions, ensure_ascii=False, indent=1).encode('utf-8'))
        print(f'rendered out/{name}.mp4 in {time.time() - t0:.0f}s')
        if '--sheet' in args:
            n = studio.contact_sheets(st, studio.WORK / 'review' / name)
            print(f'{n} beat stills in review/{name}/')
        return
    durs = [studio.estimate(b[0]) for b in ch.beats]
    st = studio.compile_chapter(ch, durs)
    report(name, ch, st, True)
    if '--sheet' in args:
        n = studio.contact_sheets(st, studio.WORK / 'review' / name)
        print(f'{n} beat stills in review/{name}/')
    if st.errors:
        raise SystemExit(1)


def yt(t):
    """YouTube timestamp: mm:ss, or h:mm:ss from one hour."""
    t = int(t)
    h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m:02d}:{s:02d}'


def chapter_names(specs):
    """'ch01-ch08' or 'ch03' -> ['ch01', ..., 'ch08']."""
    names = []
    for s in specs:
        a, _, b = s.partition('-')
        lo, hi = int(a[2:]), int((b or a)[2:])
        names += [f'ch{i:02d}' for i in range(lo, hi + 1)]
    return names


def probe_duration(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                            capture_output=True, text=True, check=True)
    d = float(result.stdout)
    if not math.isfinite(d) or d <= 0:
        raise ValueError(f'{path.name}: invalid media duration {d}')
    return d


def join(name='video', specs=()):
    out = studio.WORK / 'out'
    files = [out / f'{c}.mp4' for c in chapter_names(specs)] if specs else sorted(out.glob('ch[0-9][0-9].mp4'))
    missing = [f.name for f in files if not f.exists()]
    if not files:
        raise SystemExit('no renders to join')
    if missing:
        raise SystemExit(f'missing renders: {missing}')
    meta = [';FFMETADATA1']
    chaps, qs = [], []
    t = 0
    for f in files:
        d = probe_duration(f)
        ch = load(f.stem)
        meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={int(t * 1000)}', f'END={int((t + d) * 1000)}',
                 f'title={ch.num}. {ch.title}']
        print(f'{yt(t)}  {ch.num}. {ch.title}')
        chaps.append(f'{yt(t)} {ch.title}')
        qf = out / f'{f.stem}.questions.json'
        if qf.exists():
            questions = json.loads(qf.read_text(encoding='utf8'))
            expected = [(op.title or '', ' '.join(studio.stem_text(item) for item in op.stem))
                        for _, ops, _ in ch.beats for op in ops if op.kind == 'question']
            starts = [start for start, _, _ in questions]
            if ([(title, ' '.join(stem.split())) for _, title, stem in questions]
                    != [(title, ' '.join(stem.split())) for title, stem in expected]
                    or starts != sorted(set(starts))
                    or any(not 0 <= start < d for start in starts)):
                raise SystemExit(f'{qf.name} does not match the source questions or media duration')
            qs += [f'{yt(t + s)} [{title}] {" ".join(stem.split())}' for s, title, stem in questions]
        else:
            print(f'  ({qf.name} missing: re-render {f.stem} to list its questions)')
        t += d
    if t >= 12 * 60 * 60:
        raise SystemExit(f'joined runtime {yt(t)} exceeds YouTube\'s 12-hour upload limit')
    with tempfile.TemporaryDirectory(dir=out, prefix='join-') as scratch:
        scratch = Path(scratch)
        lst = scratch / 'list.txt'
        lst.write_text(''.join(f"file '../{f.name}'\n" for f in files), encoding='utf8')
        markers = scratch / 'chapters.txt'
        markers.write_text('\n'.join(meta) + '\n', encoding='utf8')
        joined = scratch / 'joined.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst),
                        '-i', str(markers), '-map_metadata', '1', '-map_chapters', '1', '-c', 'copy',
                        '-movflags', '+faststart', str(joined)], check=True)
        if abs(probe_duration(joined) - t) > 1:
            raise RuntimeError('joined runtime differs from the chapter media durations')
        joined.replace(out / f'{name}.mp4')
    lines = ['# Chapters', *chaps, '', '# Questions (raw stems: rewrite each as one short plain line)', *qs]
    (out / f'{name}_timestamps.txt').write_text('\n'.join(lines) + '\n', encoding='utf8')
    print('joined', out / f'{name}.mp4', f'{t / 60:.1f} min;', len(qs), f'questions in out/{name}_timestamps.txt')


if __name__ == '__main__':
    main()
