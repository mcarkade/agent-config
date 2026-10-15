"""Check delivered video files: streams, frames, size, loudness and true peak after the codec, A/V offset, phone translation.

usage: python check_delivery.py FILE.mp4 [FILE.mp4 ...] [--max-mb 180] [--ref MIX.wav] [--lufs -14] [--tp -1]

Loudness is BS.1770 integrated loudness of the decoded audio. --ref cross-correlates the decoded audio with the source mix
to measure the A/V offset. The phone model is a mono sum through a 350 Hz high-pass and a 9 kHz low-pass; 3 s windows that
lose 4 dB more than the median would thin out on phone speakers. Drops list falls of over 6 dB within 100 ms (momentary
loudness); each should be a designed moment. Needs numpy, scipy and ffmpeg (on PATH, in $FFMPEG, or from imageio-ffmpeg).
"""
import argparse
import os
import re
import shutil
import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, resample_poly, sosfilt

SR = 48000


def ffmpeg_exe():
    exe = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg_exe()


def ff(args, timeout=1800):
    return subprocess.run([FF, '-hide_banner', *args], capture_output=True, timeout=timeout)


def decode(path):
    p = ff(['-i', str(path), '-map', '0:a:0', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'])
    return np.frombuffer(p.stdout, np.float32).reshape(-1, 2).T.astype(np.float64)


def kweight(x):
    x = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585], x)
    return lfilter([1., -2., 1.], [1, -1.99004745483398, 0.99007225036621], x)


def power(kx, win, hop):
    """Channel-summed mean square of K-weighted audio in sliding windows."""
    w, h = int(win * SR), int(hop * SR)
    c = np.concatenate([[0.], np.cumsum((kx ** 2).sum(0))])
    i = np.arange(0, max(len(c) - w, 1), h)
    return (c[np.minimum(i + w, len(c) - 1)] - c[i]) / w


def db(z):
    return -0.691 + 10 * np.log10(z + 1e-20)


def integrated(kx):
    z = power(kx, .4, .1)
    z = z[db(z) > -70]
    if not len(z):
        return -np.inf
    return float(db(z[db(z) > db(z.mean()) - 10].mean()))


def offset_ms(x, ref_path):
    sr, r = wavfile.read(ref_path)
    r = r.astype(np.float64) / (np.iinfo(r.dtype).max if r.dtype.kind == 'i' else 1.)
    r = r.mean(1) if r.ndim == 2 else r
    if sr != SR:
        r = resample_poly(r, SR, sr)
    a, b = (resample_poly(s[:SR * 20], 1, 6) for s in (x.mean(0), r))     # first 20 s at 8 kHz
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    cc = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    lim = 4000                                                             # search +-0.5 s
    lags = np.concatenate([np.arange(0, lim), np.arange(-lim, 0)])
    k = int(np.argmax(np.concatenate([cc[:lim], cc[-lim:]])))
    return lags[k] / 8.


def probe(path):
    err = ff(['-i', str(path)]).stderr.decode(errors='replace')
    frames = ff(['-i', str(path), '-map', '0:v:0', '-c', 'copy', '-f', 'null', '-']).stderr.decode(errors='replace')
    n = re.findall(r'frame=\s*(\d+)', frames)
    return [ln.strip() for ln in err.splitlines() if 'Duration' in ln or 'Stream #' in ln], int(n[-1]) if n else 0


def check(path, a):
    mark = lambda ok: 'ok ' if ok else 'FAIL'
    size = os.path.getsize(path) / 1e6
    lines, frames = probe(path)
    print(f'\n{path}\n  {size:.1f} MB, {frames} video frames')
    for ln in lines:
        print('  ' + ln)
    if a.max_mb:
        print(f'  [{mark(size <= a.max_mb)}] size <= {a.max_mb} MB')
    x = decode(path)
    if not x.size:
        print('  [FAIL] no audio stream')
        return
    kx = kweight(x)
    L = integrated(kx)
    tp = 20 * np.log10(np.max(np.abs(resample_poly(x, 4, 1, axis=1))) + 1e-20)
    print(f'  [{mark(abs(L - a.lufs) <= .5)}] integrated {L:.2f} LUFS (target {a.lufs})')
    print(f'  [{mark(tp <= a.tp)}] true peak {tp:.2f} dBTP (ceiling {a.tp})')
    if a.ref:
        ms = offset_ms(x, a.ref)
        print(f'  [{mark(abs(ms) <= 1000 / 30)}] A/V offset against {os.path.basename(a.ref)}: {ms:+.1f} ms')

    mono = np.repeat(x.mean(0, keepdims=True), 2, 0)
    sos = np.vstack([butter(4, 350, 'hp', fs=SR, output='sos'), butter(2, 9000, 'lp', fs=SR, output='sos')])
    km, kp = kweight(mono), kweight(sosfilt(sos, mono, axis=1))
    print(f'  mono sum {integrated(km) - L:+.1f} dB, phone speaker {integrated(kp) - L:+.1f} dB')
    full, ph = db(power(kx, 3., 3.)), db(power(kp, 3., 3.))
    live = full > -35
    d = ph - full
    med = float(np.median(d[live])) if live.any() else 0.
    thin = [f'{3 * i:.0f}-{3 * i + 3:.0f}s ({d[i]:+.1f} dB)' for i in np.flatnonzero(live & (d < med - 4))]
    print(f'  phone-thin windows (median {med:+.1f} dB): {", ".join(thin) or "none"}')

    m = db(power(kx, .4, .05))
    drop = np.flatnonzero((m[:-2] > -40) & (m[2:] < m[:-2] - 6))
    starts = [i for k, i in enumerate(drop) if k == 0 or i - drop[k - 1] > 4]
    print(f'  drops > 6 dB in 100 ms at: {", ".join(f"{(i + 2) * .05 + .4:.2f}s" for i in starts) or "none"}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('files', nargs='+')
    ap.add_argument('--max-mb', type=float, default=0., help='size cap in MB (10^6 bytes)')
    ap.add_argument('--ref', help='source mix WAV for the A/V offset')
    ap.add_argument('--lufs', type=float, default=-14.)
    ap.add_argument('--tp', type=float, default=-1.)
    a = ap.parse_args()
    for f in a.files:
        check(f, a)


if __name__ == '__main__':
    main()
