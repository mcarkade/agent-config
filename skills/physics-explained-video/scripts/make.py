"""Build chapters.

  python make.py ch03 --check     layout + maths check with estimated timing (fast, no audio)
  python make.py ch03 --sheet     --check plus contact sheets of every beat in review/ch03/
  python make.py ch03 --render    voice + subtitles + video -> out/ch03.mp4
  python make.py --join NAME      join out/ch*.mp4 into out/NAME.mp4 with chapter markers
"""
import re, runpy, subprocess, sys, time
from pathlib import Path
import studio

ROOT = Path(__file__).resolve().parent


def load(name):
    studio.say_target[0] = None
    runpy.run_path(str(ROOT / 'chapters' / f'{name}.py'), run_name='chapter')
    ch = studio.say_target[0]
    if ch is None:
        raise SystemExit(f'{name}: no Chapter(...) created')
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
        join(rest[0] if rest else 'video'); return
    name = args[0]
    ch = load(name)
    if '--render' in args:
        texts = [b[0] for b in ch.beats if b[0]]
        t0 = time.time()
        studio.tts_batch(texts)
        print(f'tts done in {time.time() - t0:.0f}s')
        infos = {i: studio.tts_info(b[0]) for i, b in enumerate(ch.beats) if b[0]}
        durs = [infos[i][1] if i in infos else 0 for i in range(len(ch.beats))]
        st = studio.compile_chapter(ch, durs)
        report(name, ch, st, False)
        out = ROOT / 'out'
        out.mkdir(exist_ok=True)
        t0 = time.time()
        studio.render(st, infos, out / f'{name}.mp4')
        print(f'rendered out/{name}.mp4 in {time.time() - t0:.0f}s')
        if '--sheet' in args:
            n = studio.contact_sheets(st, ROOT / 'review' / name)
            print(f'{n} beat stills in review/{name}/')
        return
    durs = [studio.estimate(b[0]) for b in ch.beats]
    st = studio.compile_chapter(ch, durs)
    report(name, ch, st, True)
    if '--sheet' in args:
        n = studio.contact_sheets(st, ROOT / 'review' / name)
        print(f'{n} beat stills in review/{name}/')


def join(name='video'):
    out = ROOT / 'out'
    files = sorted(out.glob('ch[0-9][0-9].mp4'))
    lst = out / 'list.txt'
    lst.write_text(''.join(f"file '{f.name}'\n" for f in files))
    meta = [';FFMETADATA1']
    t = 0
    for f in files:
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                 capture_output=True, text=True).stdout)
        ch = load(f.stem)
        meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={int(t * 1000)}', f'END={int((t + d) * 1000)}',
                 f'title={ch.num}. {ch.title}']
        print(f'{int(t // 60):02d}:{int(t % 60):02d}  {ch.num}. {ch.title}')
        t += d
    (out / 'chapters.txt').write_text('\n'.join(meta) + '\n', encoding='utf8')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst),
                    '-i', str(out / 'chapters.txt'), '-map_metadata', '1', '-map_chapters', '1', '-c', 'copy',
                    str(out / f'{name}.mp4')], check=True)
    print('joined', out / f'{name}.mp4', f'{t / 60:.1f} min')


if __name__ == '__main__':
    main()
