"""Frame QA for a rendered video: per-frame change statistics and labelled contact sheets.

usage: python qa_frames.py stats VIDEO [--joins 1440,2880] [--k 4]
       python qa_frames.py sheet VIDEO OUT.png FRAME [FRAME ...] [--cols 4] [--width 640] [--crop X,Y,W,H]

stats decodes a small grey copy and lists runs of frames whose mean change from the previous frame exceeds k times the
median (and at least 6 of 255), near-black frames, and possible holds (a second or more of little change; a small subject
moving over a plain background also reads this way, so look before calling it a hold). Every run should match a designed
transition; segment joins (--joins, first frame of each later segment) should not appear. sheet pulls exact frames by index, optionally cropped in
source pixels, into one labelled image. Needs numpy, Pillow and ffmpeg (on PATH, in $FFMPEG, or from imageio-ffmpeg).
"""
import argparse
import os
import re
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw


def ffmpeg_exe():
    exe = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg_exe()


def info(path):
    err = subprocess.run([FF, '-hide_banner', '-i', path], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r'Video:.*?, (\d{2,5})x(\d{2,5})', err).groups())
    fps = float(re.search(r'([\d.]+) fps', err).group(1))
    return w, h, fps


def raw(path, vf, w, h, ch):
    p = subprocess.run([FF, '-loglevel', 'error', '-i', path, '-vf', vf, '-vsync', '0', '-f', 'rawvideo',
                        '-pix_fmt', 'gray' if ch == 1 else 'rgb24', '-'], capture_output=True, timeout=3600)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, ch)


def stats(a):
    W, H, fps = info(a.video)
    w = 160
    h = round(w * H / W / 2) * 2
    f = raw(a.video, f'scale={w}:{h}', w, h, 1)[..., 0].astype(np.int16)
    d = np.abs(np.diff(f, axis=0)).mean((1, 2))                      # d[i-1] = change into frame i
    med = float(np.median(d))
    thr = max(6., a.k * med)
    print(f'{a.video}: {len(f)} frames at {fps:g} fps, median change {med:.2f}, flag above {thr:.1f}')
    hot = np.flatnonzero(d > thr) + 1
    runs, start = [], None
    for k, i in enumerate(hot):
        start = i if start is None else start
        if k == len(hot) - 1 or hot[k + 1] != i + 1:
            runs.append((start, i))
            start = None
    for s, e in runs:
        print(f'  frames {s}-{e} ({s / fps:.2f}-{e / fps:.2f} s) peak {d[s - 1:e].max():.1f}')
    black = np.flatnonzero(f.mean((1, 2)) < 3)
    print(f'  near-black frames: {len(black)}' + (f' ({black[0]}..{black[-1]})' if len(black) else ''))
    holds, s = [], None
    for i, low in enumerate(np.append(d < max(.5, .25 * med), False)):
        if low and s is None:
            s = i
        elif not low and s is not None:
            if i - s >= fps:
                holds.append((s + 1, i))
            s = None
    print('  possible holds (1 s or more of little change): '
          + (', '.join(f'{a / fps:.2f}-{b / fps:.2f} s' for a, b in holds) or 'none'))
    for j in (int(v) for v in a.joins.split(',')) if a.joins else ():
        flag = 'JUMP' if d[j - 1] > thr else 'clean'
        print(f'  join at frame {j}: change {d[j - 1]:.1f} ({d[j - 1] / max(med, 1e-6):.1f}x median) {flag}')


def sheet(a):
    W, H, fps = info(a.video)
    fr = sorted({int(v) for v in a.frames})                           # select returns frames in stream order
    x, y, cw, chh = map(int, a.crop.split(',')) if a.crop else (0, 0, W, H)
    w = a.width
    h = round(w * chh / cw / 2) * 2
    sel = '+'.join(f'eq(n\\,{n})' for n in fr)
    im = raw(a.video, f"select='{sel}',crop={cw}:{chh}:{x}:{y},scale={w}:{h}", w, h, 3)
    if not len(im):
        raise SystemExit(f'no frames decoded: are the indices beyond the end of {a.video}?')
    rows = (len(im) + a.cols - 1) // a.cols
    out = Image.new('RGB', (a.cols * w, rows * (h + 18)), (40, 40, 40))
    draw = ImageDraw.Draw(out)
    for i, (n, img) in enumerate(zip(fr, im)):
        px, py = (i % a.cols) * w, (i // a.cols) * (h + 18)
        out.paste(Image.fromarray(img), (px, py + 18))
        draw.text((px + 4, py + 3), f'f{n}  {n / fps:.2f}s', fill=(255, 255, 0))
    out.save(a.out)
    print(a.out, f'{len(im)} of {len(fr)} frames')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('stats')
    s.add_argument('video')
    s.add_argument('--joins', help='comma-separated first frames of later segments')
    s.add_argument('--k', type=float, default=4.)
    t = sub.add_parser('sheet')
    t.add_argument('video')
    t.add_argument('out')
    t.add_argument('frames', nargs='+')
    t.add_argument('--cols', type=int, default=4)
    t.add_argument('--width', type=int, default=640)
    t.add_argument('--crop', help='X,Y,W,H in source pixels')
    a = ap.parse_args()
    stats(a) if a.cmd == 'stats' else sheet(a)


if __name__ == '__main__':
    main()
