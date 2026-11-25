"""Final QA of rendered chapters: duration, audio level, long silences, and stretches with no visual change."""
import re, subprocess, sys
import numpy as np

import studio
from make import probe_duration
OUT = studio.WORK / 'out'


def audio(f, sr=8000):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-xerror', '-i', str(f),
                          '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    if not raw:
        raise ValueError(f'{f}: no audio samples')
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32), sr


SIL_MIN = studio.PAUSE_HOLD + studio.PAD + 1.0   # longer than a question card's deliberate pause


def silences(a, sr, min_len=SIL_MIN):
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
    if start is not None and (n - start) / 10 >= min_len:
        runs.append((start / 10, (n - start) / 10))
    return runs


def still_stretches(f, duration, min_len=8.0):
    """Longest stretches with no visual change (scene score tiny), sampled at 2 fps."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-xerror', '-i', str(f),
                        '-vf', "fps=2,scale=320:-1,select='gt(scene,0.0015)',showinfo",
                        '-an', '-f', 'null', '-'], capture_output=True, text=True, errors='replace', check=True)
    ts = [float(t) for t in re.findall(r'pts_time:([\d.]+)', p.stderr)]
    ts = [0.0, *ts, duration]
    gaps = [(ts[i], ts[i + 1] - ts[i]) for i in range(len(ts) - 1) if ts[i + 1] - ts[i] >= min_len]
    return gaps


def main():
    want = sys.argv[1:]
    files = [OUT / f'{name}.mp4' for name in want] if want else sorted(OUT.glob('ch[0-9][0-9].mp4'))
    missing = [f.name for f in files if not f.is_file()]
    if missing or not files:
        raise SystemExit(f'missing chapter renders: {missing}' if missing else 'no chapter renders')
    total = 0
    for f in files:
        d = probe_duration(f)
        total += d
        a, sr = audio(f)
        rms = float(np.sqrt((a ** 2).mean()))
        peak = float(np.abs(a).max())
        sil = silences(a, sr)
        still = still_stretches(f, d)
        print(f'{f.stem}: {d / 60:5.1f} min  rms {rms:6.0f}  peak {peak:6.0f}  '
              f'silences>={SIL_MIN:.1f}s: {[(round(s, 1), l) for s, l in sil]}  '
              f'still>=8s: {[(round(s, 1), round(l, 1)) for s, l in still]}')
    print(f'TOTAL {total / 60:.1f} min')


if __name__ == '__main__':
    main()
