"""Final QA of rendered chapters: duration, audio level, long silences, and stretches with no visual change."""
import subprocess, sys
from pathlib import Path
import numpy as np

import studio
OUT = studio.WORK / 'out'


def audio(f, sr=8000):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(f), '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32), sr


def silences(a, sr, min_len=4.0):
    win = sr // 10
    n = len(a) // win
    rms = np.sqrt((a[:n * win].reshape(n, win) ** 2).mean(1))
    quiet = rms < 150
    runs, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) / 10 >= min_len:
                runs.append((start / 10, (i - start) / 10))
            start = None
    return runs


def still_stretches(f, min_len=8.0):
    """Longest stretches with no visual change (scene score tiny), sampled at 2 fps."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(f), '-vf', "fps=2,scale=320:-1,select='gt(scene,0.0015)',showinfo",
                        '-an', '-f', 'null', '-'], capture_output=True, text=True, errors='ignore')
    import re
    ts = [float(t) for t in re.findall(r'pts_time:([\d.]+)', p.stderr)]
    ts = [0.0] + ts
    gaps = [(ts[i], ts[i + 1] - ts[i]) for i in range(len(ts) - 1) if ts[i + 1] - ts[i] >= min_len]
    return gaps


total = 0
want = set(sys.argv[1:])                          # optional: python qa.py ch01 ch02 ...
for f in sorted(OUT.glob('ch[0-9][0-9].mp4')):
    if want and f.stem not in want:
        continue
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                             capture_output=True, text=True).stdout)
    total += d
    a, sr = audio(f)
    rms = float(np.sqrt((a ** 2).mean()))
    peak = float(np.abs(a).max())
    sil = silences(a, sr)
    still = still_stretches(f)
    print(f'{f.stem}: {d / 60:5.1f} min  rms {rms:6.0f}  peak {peak:6.0f}  '
          f'silences>=4s: {[(round(s), l) for s, l in sil][:6]}  still>=8s: {[(round(s), round(l, 1)) for s, l in still][:6]}')
print(f'TOTAL {total / 60:.1f} min')
