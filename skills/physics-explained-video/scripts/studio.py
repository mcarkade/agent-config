"""Studio: author and render black-board derivation videos (Physics-Explained-like visual grammar).

Authors write chapters/chNN.py with `say(narration, *ops)` beats. Layout is automatic: items stack
down the board; a figure takes the left half and items flow in the right column; when the board is full,
everything not pinned fades out and the flow restarts at the top. See the skill's references/authoring.md.
"""
import asyncio, hashlib, io, json, math, os, re, subprocess, tempfile, textwrap
from bisect import insort
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from functools import lru_cache
from itertools import islice
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
# Bulky intermediates (TTS cache, renders, review stills) go to PE_WORK; point it at scratch storage.
WORK = Path(os.environ.get('PE_WORK', ROOT))
CACHE = WORK / 'cache'
CACHE.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1920, 1080, 30
VOICE, RATE = 'en-US-AndrewNeural', '+0%'      # natural 1x pace; viewers speed up on YouTube
FADE, MOVE, PAD, STAGGER = 0.25, 0.45, 0.30, 0.12
PAUSE_HOLD = 5.0                        # silent seconds on a QUESTION card, so the viewer can start the problem
BOARD = (100, 92, 1820, 968)          # content region x0, y0, x1, y1 (subtitle band below)
FIG_ZONE = (60, 960)                   # x range used by a figure; items then flow in (1000, 1820)
RIGHT_COL = (1000, 1820)
GAP = 24
SUB_Y = 1022

# palette
EQ = '#F4EEE2'
CAPTION = '#ECE2D0'
NOTE = '#E8C4A0'
TEALH = '#40A0B8'
REDH = '#E06666'
GREY = '#8A8A8A'
BLUE, ORANGE, PINK, GREEN, YELLOW = '#6FA8DC', '#E69138', '#D27FD0', '#93C47D', '#F1C232'
PALETTE = dict(eq=EQ, caption=CAPTION, note=NOTE, teal=TEALH, red=REDH, blue=BLUE, orange=ORANGE,
               pink=PINK, green=GREEN, yellow=YELLOW, grey=GREY)


def _rgb(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


matplotlib.rcParams.update({
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Cambria', 'mathtext.it': 'Cambria:italic',
    'mathtext.bf': 'Cambria:bold', 'mathtext.sf': 'Segoe UI', 'mathtext.fallback': 'stix',
    'font.family': 'Segoe UI', 'text.color': EQ, 'axes.facecolor': 'none', 'figure.facecolor': 'none',
    'savefig.transparent': True,
})


class AuthorError(Exception):
    pass


# =========================================================== rasterisers
def _prep_tex(tex):
    tex = re.sub(r'\\frac', r'\\dfrac', tex)          # cannot match inside \dfrac (no backslash before 'frac')
    tex = re.sub(r'\\(dot|ddot)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])', r'\\\1{\2}', tex)    # \dot x -> \dot{x}
    acc = r'(\\(?:dot|ddot)\{(?:[^{}]|\{[^{}]*\})*\})'                          # allows \dot{\mathbf{R}}
    tex = re.sub(acc + r'\^', r'\1{}^', tex)
    tex = re.sub(acc + r'_', r'\1{}_', tex)
    # inside exponents and subscripts keep operators tight (n - 1 stays n-1)
    tex = re.sub(r'([\^_]\{)([^{}]*)(\})', lambda m: m.group(1) + re.sub(r'\s*([+-])\s*', r'\1', m.group(2)) + m.group(3), tex)
    tex = re.sub(r' ([+-]|\\pm|\\approx|\\to|\\Rightarrow) ', r'\\;\1\\;', tex)   # spaced binary ops
    tex = re.sub(r'\s*(?<![<>!\\])=\s*', r'\\;=\\;', tex)            # airy equals, as in his videos
    tex = re.sub(r'(^|\\;=\\;|\(|\{)\s*-', r'\1{-}', tex)             # unary minus stays tight
    tex = re.sub(r'\{-\}\s*\\dfrac', r'{-}\\,\\dfrac', tex)           # but keep it off a fraction bar
    # a thin space before a named function after a symbol, so "a cosh" never reads as "acosh"
    tex = re.sub(r'(?<=[A-Za-z0-9}])\\(sinh|cosh|tanh|coth|sin|cos|tan|cot|sec|csc|ln|exp)(?![a-zA-Z])', r'\\,\\\1', tex)
    return tex


def _render_mpl_text(s, size, color, ha='left', italic=False, linespacing=1.25):
    """Render a string (may contain $math$) on a big transparent canvas, no cropping. Cached."""
    key = hashlib.md5(f'r4|{s}|{size}|{color}|{ha}|{italic}'.encode()).hexdigest()
    p = CACHE / f't_{key}.png'
    if not p.exists():
        nlines = s.count('\n') + 1
        longest = max(len(l) for l in s.split('\n'))
        wpx = int(size * 0.75 * max(longest, 4)) + 300
        hpx = int(size * (2.3 * nlines + 2.4))
        fig = plt.figure(figsize=(wpx / 100, hpx / 100), dpi=100)
        x = 0.5 if ha == 'center' else 30 / wpx
        try:
            fig.text(x, 0.5, s, fontsize=size, color=color, ha=ha, va='center', multialignment='center',
                     style='italic' if italic else 'normal', linespacing=linespacing)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
        except Exception as e:
            plt.close(fig)
            raise AuthorError(f'cannot render {s!r}: {str(e).splitlines()[-1] if str(e) else e}')
        plt.close(fig)
        buf.seek(0)
        Image.open(buf).convert('RGBA').save(p)
    return Image.open(p).convert('RGBA')


def _crop_ink(im, pad=6, box=None):
    bb = box or im.getchannel('A').getbbox()
    if not bb:
        raise AuthorError('empty render')
    return im.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))


def math_parts(parts, size=50, color=EQ):
    """Render an equation given as a list of tex parts. Returns (images per prefix, x-bounds of each prefix).
    All prefix images share the full equation's vertical ink range and left edge."""
    full = _render_mpl_text('$' + _prep_tex(''.join(parts)) + '$', size, color)
    bb = full.getchannel('A').getbbox()
    if not bb:
        raise AuthorError(f'empty equation {parts}')
    pad = 6
    imgs, bounds = [], [pad]
    for k in range(1, len(parts) + 1):
        pre = _render_mpl_text('$' + _prep_tex(''.join(parts[:k])) + '$', size, color)
        pb = pre.getchannel('A').getbbox()
        right = pb[2] if pb else bb[0]
        imgs.append(pre.crop((bb[0] - pad, bb[1] - pad, right + pad, bb[3] + pad)))
        bounds.append(right - bb[0] + pad)
    return imgs, bounds


def _visible(t):
    """Approximate the printed width of caption text: a TeX command counts as one glyph, markup counts as nothing."""
    def m(g):
        body = re.sub(r'\\[a-zA-Z]+', 'x', g.group(1))
        return 'x' * max(1, len(re.sub(r'[{}^_\\ ]', '', body)))
    return re.sub(r'\$([^$]*)\$', m, t)


def text_item(s, size, color, width, italic=False):
    """Caption text (may contain $math$), wrapped to `width` px, centred lines."""
    def wrapped(limit):
        lines = []
        for para in s.split('\n'):
            cur = ''
            for token in re.findall(r'\$[^$]*\$|\S+', para):
                trial = (cur + ' ' + token).strip()
                if len(_visible(trial)) * size * 0.54 > limit and cur:
                    lines.append(cur)
                    cur = token
                else:
                    cur = trial
            lines.append(cur)
        return '\n'.join(lines)

    img = _crop_ink(_render_mpl_text(wrapped(width), size, color, ha='center', italic=italic))
    if img.width > width:
        limit = int(width * width / img.width * 0.90)
        img = _crop_ink(_render_mpl_text(wrapped(limit), size, color, ha='center', italic=italic))
    return img


@lru_cache(maxsize=256)
def sub_img(s):
    font = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 34)
    w = int(font.getlength(s)) + 40
    im = Image.new('RGBA', (w, 56), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 6), s, font=font, fill=(205, 205, 205, 255))
    return im


def fig_layer(draw, size, axes, base):
    """Draw one figure layer with matplotlib. `axes` fixes limits/aspect so layers align."""
    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    ax = fig.add_axes([0.06, 0.08, 0.90, 0.86])
    ax.set_facecolor('none')
    a = dict(axes or {})
    ax.set_xlim(*a.get('xlim', (0, 1)))
    ax.set_ylim(*a.get('ylim', (0, 1)))
    if a.get('equal'):
        ax.set_aspect('equal', adjustable='box')
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    if base and a.get('frame', True):
        ox, oy = a.get('origin', (a.get('xlim', (0, 1))[0], 0))
        xl, yl = a.get('xlim', (0, 1)), a.get('ylim', (0, 1))
        ax.annotate('', xy=(xl[1], oy), xytext=(xl[0], oy),
                    arrowprops=dict(arrowstyle='-|>', color='#D8D8D8', lw=1.6, mutation_scale=18))
        ax.annotate('', xy=(ox, yl[1]), xytext=(ox, yl[0]),
                    arrowprops=dict(arrowstyle='-|>', color='#D8D8D8', lw=1.6, mutation_scale=18))
        if a.get('xlabel'):
            ax.text(xl[1], oy - 0.06 * (yl[1] - yl[0]), a['xlabel'], color='#D8D8D8', fontsize=26, ha='right', va='top')
        if a.get('ylabel'):
            ax.text(ox + 0.02 * (xl[1] - xl[0]), yl[1], a['ylabel'], color='#D8D8D8', fontsize=26, ha='left', va='top')
    if draw:
        draw(ax)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert('RGBA')


def _rect(w, h, color, width=3):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rectangle([1, 1, im.size[0] - 2, im.size[1] - 2], outline=_rgb(color) + (255,), width=width)
    return im


def _ellipse(w, h, color, width=4):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([2, 2, im.size[0] - 3, im.size[1] - 3], outline=_rgb(color) + (255,), width=width)
    return im


def _line(p0, p1, color, width=3, head=False):
    """Returns (image, top-left) of a straight line/arrow between absolute points."""
    pad = 18
    x0, y0 = p0; x1, y1 = p1
    left, top = min(x0, x1) - pad, min(y0, y1) - pad
    im = Image.new('RGBA', (int(abs(x1 - x0) + 2 * pad), int(abs(y1 - y0) + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a, b = (x0 - left, y0 - top), (x1 - left, y1 - top)
    d.line([a, b], fill=_rgb(color) + (255,), width=width)
    if head:
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); L = 15
        d.polygon([b, (b[0] - L * math.cos(ang - 0.4), b[1] - L * math.sin(ang - 0.4)),
                   (b[0] - L * math.cos(ang + 0.4), b[1] - L * math.sin(ang + 0.4))], fill=_rgb(color) + (255,))
    return im, (left, top)


# =========================================================== author-facing op constructors
class Op:
    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)


def M(tex, id=None, size=50, color=EQ):
    """Equation line. `tex` may be a list of parts so CIRCLE/STRIKE/UNDER can target terms by index."""
    parts = tex if isinstance(tex, (list, tuple)) else [tex]
    return Op('item', sub='math', parts=list(parts), id=id, size=size, color=color)


def KEY(tex, id=None, size=54):
    """Key result: equation with a teal box."""
    return Op('key', inner=M(tex, id=id, size=size))


def T(text, id=None, size=36, color=CAPTION, italic=False):
    """Caption (white-cream sans). Inline math allowed with $...$."""
    return Op('item', sub='text', text=text, id=id, size=size, color=color, italic=italic)


def N(text, id=None, size=34):
    """Explanatory note in soft peach."""
    return T(text, id=id, size=size, color=NOTE)


def LABEL(text, id=None):
    """Small teal label (e.g. 'Newton's second law', 'Step 2')."""
    return T(text, id=id, size=30, color=TEALH)


def G(id, parts, k, size=50, color=EQ):
    """Grow equation `id` to show the first k parts. First call places it (space for the full equation)."""
    return Op('grow', id=id, parts=list(parts), k=k, size=size, color=color)


def ROW(*items, arrows=True, id=None):
    """Put items side by side on one line, with teal arrows between them if arrows=True."""
    return Op('row', items=list(items), arrows=arrows, id=id)


def BOX(id, color=TEALH):
    return Op('deco', sub='box', target=id, color=color)


def CIRCLE(id, terms=None, color=REDH):
    return Op('deco', sub='circle', target=id, terms=terms, color=color)


def STRIKE(id, terms=None, color=REDH):
    return Op('deco', sub='strike', target=id, terms=terms, color=color)


def UNDER(id, label, terms=None):
    """Teal underline under a term with a short peach label below it."""
    return Op('deco', sub='under', target=id, terms=terms, label=label, color=TEALH)


def ARROW(a, b, color=TEALH):
    """Arrow from item a to item b (top-to-bottom if stacked, side-to-side if on one row)."""
    return Op('arrow', a=a, b=b, color=color)


def OUT(*ids):
    """Fade out specific items (they leave a gap; prefer CLEAR)."""
    return Op('out', ids=list(ids))


def CLEAR(*keep):
    """Fade out everything except `keep` ids, which slide up to the top in the given order."""
    return Op('clear', keep=list(keep))


def PIN(*ids):
    """Pinned items survive automatic overflow clears (like a question stem)."""
    return Op('pin', ids=list(ids))


def FIG(id, draw=None, axes=None, size=(880, 640)):
    """Figure on the left half. draw(ax) uses matplotlib; axes=dict(xlim, ylim, equal, frame, xlabel, ylabel, origin).
    While a figure is visible, items flow in the right column."""
    return Op('fig', id=id, draw=draw, axes=axes, size=size)


def FIGADD(fig_id, id, draw):
    """Add a layer drawn on the same axes as figure `fig_id` (e.g. an energy line, a new curve)."""
    return Op('figadd', fig=fig_id, id=id, draw=draw)


def ANIM(fig_id, id, draw, dur=3.0):
    """Animated layer on figure `fig_id`: draw(ax, u) with u from 0 to 1 over `dur` seconds, then holds."""
    return Op('anim', fig=fig_id, id=id, draw=draw, dur=dur)


def QUESTION(*stem, title=None, fig=None):
    """Clear the board and pose a question: header, stem items, 'Pause and try'. Stem is pinned.
    fig=FIG(...) puts the diagram on the left first, so the stem wraps in the right column."""
    return Op('question', stem=list(stem), title=title, fig=fig)


def SOLVE():
    """Remove the 'Pause and try' prompt; solution items then flow under the stem."""
    return Op('solve')


def HOOK(text, sub=None):
    """Clear and show a big hook question in the centre (chapter openers)."""
    return Op('hook', text=text, sub=sub)


def DIAGRAM(id, name, height=520):
    """A ready-made diagram from the study guide (diagrams/NAME.png), placed as a figure."""
    return Op('diagram', id=id, name=name, height=height)


# =========================================================== timeline model
class El:
    def __init__(self, img, x, y, kind, t0, fade=FADE, solid=True):
        self.img, self.kind, self.solid = img, kind, solid
        self.anims = []
        self.cur = {'alpha': 0.0, 'x': x, 'y': y}
        self.x0, self.y0 = x, y
        self.frames = None          # (t0, dur, [imgs]) for animations
        self.decos = []
        self.pad = 6 if kind in ('item',) else 0
        self.animate('alpha', 1.0, t0, fade)

    def animate(self, attr, v1, t0, dur):
        v0 = self.cur[attr]
        self.anims.append((t0, t0 + dur, attr, v0, v1))
        self.cur[attr] = v1

    def val(self, attr, t):
        v = {'alpha': 0.0, 'x': self.x0, 'y': self.y0}[attr]
        for (t0, t1, a, v0, v1) in self.anims:
            if a != attr or t < t0:
                continue
            u = min(max((t - t0) / max(t1 - t0, 1e-6), 0), 1)
            u = u * u * (3 - 2 * u)
            v = v0 + (v1 - v0) * u
        return v

    @property
    def w(self):
        return self.img.size[0]

    @property
    def h(self):
        return self.img.size[1]

    def ink(self, at_target=True):
        x, y = (self.cur['x'], self.cur['y'])
        p = self.pad
        return (x + p, y + p, x + self.w - p, y + self.h - p)


def _ease(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)


class Chapter:
    def __init__(self, num, title):
        self.num, self.title = num, title
        self.beats = []
        say_target[0] = self

    def say(self, text, *ops, hold=0.0):
        self.beats.append((text.strip(), list(ops), hold))

    def wait(self, sec, *ops):
        self.beats.append(('', list(ops), sec))


say_target = [None]


def say(text, *ops, hold=0.0):
    say_target[0].say(text, *ops, hold=hold)


def wait(sec, *ops):
    say_target[0].wait(sec, *ops)


# =========================================================== compiler (layout + timing)
class Stage:
    def __init__(self, chapter, durations):
        self.ch = chapter
        self.durations = durations     # list of (speech seconds, words) per beat
        self.els = []                  # all elements ever
        self.ids = {}                  # id -> El (live)
        self.flow = []                 # live flow items, top to bottom
        self.cursor = BOARD[1]
        self.fig = None                # live figure El (left half)
        self.pinned = set()
        self.qcount = 0
        self.audio = []                # (t, beat index)
        self.subs = []                 # (t0, t1, text)
        self.errors = []
        self.beat_ends = []
        self.cur_beat = 0
        self.anon = 0

    # ---------- helpers
    def err(self, msg):
        b = self.cur_beat
        txt = self.ch.beats[b][0][:70] if b < len(self.ch.beats) else ''
        self.errors.append(f'beat {b} ("{txt}"): {msg}')

    def col(self):
        return RIGHT_COL if self.fig is not None else (BOARD[0], BOARD[2])

    def new_id(self, id):
        if id:
            return id
        self.anon += 1
        return f'_a{self.anon}'

    def live(self, id):
        e = self.ids.get(id)
        if e is None or e.cur['alpha'] <= 0:
            self.err(f'"{id}" is not on screen')
            return None
        return e

    def add_el(self, img, x, y, kind, t, id=None, solid=True):
        e = El(img, x, y, kind, t, solid=solid)
        self.els.append(e)
        if id:
            self.ids[id] = e
        return e

    @staticmethod
    def tree(e):
        out, stack = [], [e]
        while stack:
            x = stack.pop()
            if x in out:
                continue
            out.append(x)
            stack.extend(x.decos)
        return out

    def fade_out(self, e, t):
        for d in self.tree(e):
            if d.cur['alpha'] > 0:
                d.animate('alpha', 0.0, t, FADE)

    def clear(self, t, keep=()):
        missing = [k for k in keep if k not in self.ids or self.ids[k].cur['alpha'] <= 0]
        if missing:
            self.err(f'CLEAR keep ids not on screen: {missing}')
        keep_els = [self.ids[k] for k in keep if k not in missing]
        # a kept id may be a row member: keep its row holder instead
        keep_els = [next((h for h in self.flow if e in self.tree(h)), e) for e in keep_els]
        safe = set()
        for k in keep_els:
            safe.update(map(id, self.tree(k)))
        for e in self.els:
            if id(e) in safe or e.kind == 'tag' or e.cur['alpha'] <= 0:
                continue
            e.animate('alpha', 0.0, t, FADE)
        if self.fig is not None and self.fig not in keep_els:
            self.fig = None
        self.flow = [e for e in self.flow if e in keep_els]
        self.pinned = {p for p in self.pinned if p in keep_els}
        self.restack(t)

    def restack(self, t):
        """Slide live flow items up to the top, keeping order."""
        y = BOARD[1]
        c0, c1 = self.col()
        for e in self.flow:
            nx = (c0 + c1) / 2 - e.w / 2
            if getattr(e, 'row_w', None):
                nx = (c0 + c1) / 2 - e.row_w / 2 + (e.cur['x'] - e.row_x0)
            ty = y + getattr(e, 'y_off', 0)
            if abs(e.cur['y'] - ty) > 1 or abs(e.cur['x'] - nx) > 1:
                dx, dy = nx - e.cur['x'], ty - e.cur['y']
                if getattr(e, 'row_w', None):
                    e.row_x0 += dx
                for d in self.tree(e):
                    d.animate('x', d.cur['x'] + dx, t, MOVE); d.animate('y', d.cur['y'] + dy, t, MOVE)
            y += getattr(e, 'row_h', e.h) + GAP + getattr(e, 'extra_h', 0)
        self.cursor = y

    def overflow(self, t):
        # carry the newest line up: the next step almost always works on it
        last = [e for e in self.flow if e not in self.pinned][-1:]
        keep = [e for e in self.flow if e in self.pinned] + last
        for e in self.flow:
            if e not in keep:
                self.fade_out(e, t)
        self.flow = keep
        self.restack(t)

    def fit_math(self, op, width):
        size = op.size
        while True:
            imgs, bounds = math_parts(op.parts, size, op.color)
            if imgs[-1].size[0] <= width or size <= 30:
                return imgs, bounds, size
            size -= 4

    def make_item(self, op, width):
        if op.sub == 'math':
            imgs, bounds, size = self.fit_math(op, width)
            if size < 36:
                self.err(f'math shrunk to {size}px (hard to read on a phone): split the line')
            return imgs[-1], bounds
        return text_item(op.text, op.size, op.color, width - 20, op.italic), None

    def place_block(self, h, t):
        """Reserve vertical space h in the flow; returns y."""
        if self.cursor + h > BOARD[3]:
            self.overflow(t)
            if self.cursor + h > BOARD[3]:
                self.err(f'item of height {h}px does not fit even after clearing; split it or pin less')
        y = self.cursor
        self.cursor += h + GAP
        return y

    # ---------- op handlers
    def op_item(self, op, t, flow=True):
        c0, c1 = self.col()
        img, bounds = self.make_item(op, c1 - c0)
        y = self.place_block(img.size[1], t)
        e = self.add_el(img, (c0 + c1) / 2 - img.size[0] / 2, y, 'item', t, op.id)
        e.bounds = bounds
        self.flow.append(e)
        return e

    def op_key(self, op, t):
        op.inner.id = op.inner.id or self.new_id(None)
        e = self.op_item(op.inner, t)
        self.cursor += 12
        self.deco(Op('deco', sub='box', target=op.inner.id, color=TEALH), t + 0.25)

    def op_grow(self, op, t):
        c0, c1 = self.col()
        old = self.ids.get(op.id)
        imgs, bounds, size = self.fit_math(op, c1 - c0)
        k = max(1, min(op.k, len(op.parts)))
        if old is None or old.cur['alpha'] <= 0:
            full_w = imgs[-1].size[0]
            x = (c0 + c1) / 2 - full_w / 2
            y = self.place_block(imgs[-1].size[1], t)
            e = self.add_el(imgs[k - 1], x, y, 'item', t, op.id)
            e.bounds, e.grow = bounds[:k + 1], (op.parts, size, op.color)
            self.flow.append(e)
        else:
            e = self.add_el(imgs[k - 1], old.cur['x'], old.cur['y'], 'item', t, op.id)
            e.bounds = bounds[:k + 1]
            old.animate('alpha', 0.0, t + FADE, 0.01)
            e.decos = old.decos
            self.flow[self.flow.index(old)] = e
            if old in self.pinned:
                self.pinned.add(e)

    def op_row(self, op, t):
        c0, c1 = self.col()
        width = c1 - c0
        n = len(op.items)
        arrow_w = 90 if op.arrows else 50
        per = (width - arrow_w * (n - 1)) / n
        made = [self.make_item(it, per) for it in op.items]
        hmax = max(im.size[1] for im, _ in made)
        total = sum(im.size[0] for im, _ in made) + arrow_w * (n - 1)
        y = self.place_block(hmax, t)
        x = (c0 + c1) / 2 - total / 2
        row_els, arrows = [], []
        x_start = x
        for i, ((im, bounds), it) in enumerate(zip(made, op.items)):
            e = self.add_el(im, x, y + (hmax - im.size[1]) / 2, 'item', t + i * 0.35, it.id or self.new_id(None))
            e.bounds = bounds
            row_els.append(e)
            if op.arrows and i < n - 1:
                ax0, ax1 = x + im.size[0] + 14, x + im.size[0] + arrow_w - 14
                aim, (lx, ly) = _line((ax0, y + hmax / 2), (ax1, y + hmax / 2), TEALH, 3, True)
                arrows.append(self.add_el(aim, lx, ly, 'deco', t + i * 0.35 + 0.2, solid=False))
            x += im.size[0] + arrow_w
        # the row moves as one block: the first element carries the others
        holder = row_els[0]
        holder.decos.extend(row_els[1:] + arrows)
        holder.row_h, holder.row_w, holder.row_x0 = hmax, total, x_start
        holder.y_off = (hmax - holder.h) / 2
        self.flow.append(holder)
        if op.id:
            self.ids[op.id] = holder

    def span(self, e, terms):
        x0, y0, x1, y1 = e.ink()
        if terms is None:
            return x0, y0, x1, y1
        b = getattr(e, 'bounds', None)
        if not b or terms[1] >= len(b) or terms[0] < 0:
            self.err('terms=(i, j) needs an equation given as a list of parts with j <= number of shown parts')
            return x0, y0, x1, y1
        ex = e.cur['x']
        return ex + b[terms[0]] + (4 if terms[0] else 0), y0, ex + b[terms[1]], y1

    def deco(self, op, t):
        e = self.live(op.target)
        if e is None:
            return
        x0, y0, x1, y1 = self.span(e, getattr(op, 'terms', None))
        if op.sub == 'box':
            im = _rect(x1 - x0 + 28, y1 - y0 + 24, op.color)
            d = self.add_el(im, x0 - 14, y0 - 12, 'deco', t, solid=False)
        elif op.sub == 'circle':
            im = _ellipse(x1 - x0 + 30, y1 - y0 + 26, op.color)
            d = self.add_el(im, x0 - 15, y0 - 13, 'deco', t, solid=False)
        elif op.sub == 'strike':
            im, (lx, ly) = _line((x0, y1 - 4), (x1, y0 + 4), op.color, 4)
            d = self.add_el(im, lx, ly, 'deco', t, solid=False)
        elif op.sub == 'under':
            im, (lx, ly) = _line((x0, y1 + 8), (x1, y1 + 8), op.color, 3)
            d = self.add_el(im, lx, ly, 'deco', t, solid=False)
            lab = text_item(op.label, 30, NOTE, 600)
            l = self.add_el(lab, (x0 + x1) / 2 - lab.size[0] / 2, y1 + 14, 'deco', t + 0.1, solid=True)
            e.decos.append(l)
            e.extra_h = getattr(e, 'extra_h', 0) + lab.size[1] + 22
            if self.flow and self.flow[-1] is e:
                self.cursor = max(self.cursor, y1 + 14 + lab.size[1] + GAP)
            l.kind = 'label'
        e.decos.append(d)

    def op_arrow(self, op, t):
        a, b = self.live(op.a), self.live(op.b)
        if not a or not b:
            return
        ax0, ay0, ax1, ay1 = a.ink(); bx0, by0, bx1, by1 = b.ink()
        if by0 >= ay1 - 4:
            p0, p1 = ((ax0 + ax1) / 2, ay1 + 6), ((bx0 + bx1) / 2, by0 - 6)
        else:
            p0, p1 = (ax1 + 10, (ay0 + ay1) / 2), (bx0 - 10, (by0 + by1) / 2)
        im, (lx, ly) = _line(p0, p1, op.color, 3, True)
        d = self.add_el(im, lx, ly, 'deco', t, solid=False)
        b.decos.append(d)

    def op_fig(self, op, t):
        if self.fig is not None:
            self.fade_out(self.fig, t)
        # items currently in a full-width flow are cleared to make room
        for e in self.flow:
            if e not in self.pinned:
                self.fade_out(e, t)
        self.flow = [e for e in self.flow if e in self.pinned]
        img = fig_layer(op.draw, op.size, op.axes, True)
        x = (FIG_ZONE[0] + FIG_ZONE[1]) / 2 - img.size[0] / 2
        if img.size[0] > FIG_ZONE[1] - FIG_ZONE[0]:
            x = (BOARD[0] + BOARD[2]) / 2 - img.size[0] / 2  # wide figure: centre on the board
        y = max(BOARD[1], (BOARD[1] + BOARD[3]) / 2 - img.size[1] / 2)
        e = self.add_el(img, x, y, 'fig', t, op.id)
        e.fig_spec = (op.size, op.axes)
        self.fig = e
        self.restack(t)

    def op_diagram(self, op, t):
        p = ROOT / 'diagrams' / f'{op.name}.png'
        if not p.exists():
            self.err(f'no diagram named {op.name}')
            return
        img = Image.open(p).convert('RGBA')
        sc = min(op.height / img.size[1], 860 / img.size[0])
        img = img.resize((int(img.size[0] * sc), int(img.size[1] * sc)), Image.LANCZOS)
        if self.fig is not None:
            self.fade_out(self.fig, t)
        for e in self.flow:
            if e not in self.pinned:
                self.fade_out(e, t)
        self.flow = [e for e in self.flow if e in self.pinned]
        x = (FIG_ZONE[0] + FIG_ZONE[1]) / 2 - img.size[0] / 2
        y = max(BOARD[1], (BOARD[1] + BOARD[3]) / 2 - img.size[1] / 2)
        e = self.add_el(img, x, y, 'fig', t, op.id)
        e.fig_spec = None
        self.fig = e
        self.restack(t)

    def op_figadd(self, op, t):
        f = self.live(op.fig)
        if f is None:
            return
        if not getattr(f, 'fig_spec', None):
            self.err('FIGADD needs a FIG, not a DIAGRAM')
            return
        size, axes = f.fig_spec
        img = fig_layer(op.draw, size, axes, False)
        d = self.add_el(img, f.cur['x'], f.cur['y'], 'layer', t, op.id, solid=False)
        f.decos.append(d)

    def op_anim(self, op, t):
        f = self.live(op.fig)
        if f is None:
            return
        size, axes = f.fig_spec
        n = max(2, int(op.dur * 15))
        frames = [fig_layer(lambda ax, u=i / (n - 1): op.draw(ax, u), size, axes, False) for i in range(n)]
        d = self.add_el(frames[-1], f.cur['x'], f.cur['y'], 'layer', t, op.id, solid=False)
        d.frames = (t, op.dur, frames)
        d.anims = [(t, t + 0.05, 'alpha', 0.0, 1.0)]
        f.decos.append(d)

    def op_question(self, op, t):
        self.clear(t)
        if getattr(op, 'fig', None) is not None:
            self.op_fig(op.fig, t)
        self.qcount += 1
        title = f'QUESTION {self.ch.num}.{self.qcount}' + (f'  \u00b7  {op.title}' if op.title else '')
        h = self.op_item(T(title, size=30, color=TEALH), t + 0.1)
        self.pinned.add(h)
        for i, it in enumerate(op.stem):
            if it.kind == 'item':
                e = self.op_item(it, t + 0.25 + 0.15 * i)
            elif it.kind == 'row':
                self.op_row(it, t + 0.25 + 0.15 * i); e = self.flow[-1]
            else:
                self.err('QUESTION stem accepts M, T, N, ROW only'); continue
            self.pinned.add(e)
        p = self.op_item(T('Pause and try', size=34, color=NOTE, italic=True), t + 0.6)
        self.ids['_pause'] = p

    def op_solve(self, op, t):
        p = self.ids.get('_pause')
        if p is not None and p.cur['alpha'] > 0:
            self.fade_out(p, t)
            self.flow.remove(p)
            self.restack(t)

    def op_hook(self, op, t):
        self.clear(t)
        img = text_item(op.text, 52, EQ, 1500)
        y = 400 - img.size[1] / 2
        e = self.add_el(img, W / 2 - img.size[0] / 2, y, 'item', t + 0.15)
        self.flow.append(e)
        self.cursor = y + img.size[1] + 40
        if op.sub:
            s = text_item(op.sub, 36, NOTE, 1400)
            e2 = self.add_el(s, W / 2 - s.size[0] / 2, self.cursor, 'item', t + 0.6)
            self.flow.append(e2)
            self.cursor += s.size[1] + GAP

    def apply(self, op, t):
        k = op.kind
        if k == 'item':
            self.op_item(op, t)
        elif k == 'key':
            self.op_key(op, t)
        elif k == 'grow':
            self.op_grow(op, t)
        elif k == 'row':
            self.op_row(op, t)
        elif k == 'deco':
            self.deco(op, t)
        elif k == 'arrow':
            self.op_arrow(op, t)
        elif k == 'out':
            for i in op.ids:
                e = self.live(i)
                if e:
                    self.fade_out(e, t)
                    if e in self.flow:
                        self.flow.remove(e)
                    if e is self.fig:          # figure gone: later items use the full board width again
                        self.fig = None
                        self.restack(t)
        elif k == 'clear':
            self.clear(t, op.keep)
        elif k == 'pin':
            for i in op.ids:
                e = self.live(i)
                if e:
                    self.pinned.add(e)
        elif k == 'fig':
            self.op_fig(op, t)
        elif k == 'diagram':
            self.op_diagram(op, t)
        elif k == 'figadd':
            self.op_figadd(op, t)
        elif k == 'anim':
            self.op_anim(op, t)
        elif k == 'question':
            self.op_question(op, t)
        elif k == 'solve':
            self.op_solve(op, t)
        elif k == 'hook':
            self.op_hook(op, t)
        else:
            self.err(f'unknown op {k}')

    # ---------- checks at the end of each beat
    def check_layout(self):
        live = [e for e in self.els if e.cur['alpha'] > 0 and e.solid and e.kind in ('item', 'fig', 'label')]
        for e in live:
            x0, y0, x1, y1 = e.ink()
            if x0 < 20 or x1 > W - 20 or y0 < BOARD[1] - 12 or y1 > BOARD[3] + 8:
                self.err(f'element off the board ({int(x0)},{int(y0)})-({int(x1)},{int(y1)})')
        for i in range(len(live)):
            for j in range(i + 1, len(live)):
                a, b = live[i].ink(), live[j].ink()
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 6 and oy > 6:
                    self.err('two elements overlap; use CLEAR/OUT or fewer items')
                    return


def stem_text(op):
    """Raw text of a stem item (tex left as is), used for the question list."""
    if op.kind == 'row':
        return ' '.join(stem_text(i) for i in op.items)
    if getattr(op, 'sub', None) == 'math':
        return '$' + ''.join(op.parts) + '$'
    return getattr(op, 'text', '')


def compile_chapter(ch, durations):
    st = Stage(ch, durations)
    tag = text_item(f'{ch.num}  \u00b7  {ch.title}', 24, GREY, 900)
    st.add_el(tag, 40, 22, 'tag', 0.5)
    # chapter card
    card1 = text_item(f'CHAPTER {ch.num}', 32, TEALH, 1200)
    card2 = text_item(ch.title, 64, EQ, 1600)
    e1 = st.add_el(card1, W / 2 - card1.size[0] / 2, 380, 'item', 0.2)
    e2 = st.add_el(card2, W / 2 - card2.size[0] / 2, 450, 'item', 0.45)
    st.flow = [e1, e2]
    t = 2.6
    st.clear(t - 0.3)
    st.questions = []                 # (start time, title, stem as plain text) for the YouTube timestamps
    for b, (text, ops, hold) in enumerate(ch.beats):
        st.cur_beat = b
        start = t
        for i, op in enumerate(ops):
            try:
                st.apply(op, start + i * STAGGER)
            except AuthorError as e:
                st.err(str(e))
            except Exception as e:
                st.err(f'{type(e).__name__}: {e}')
        is_q = any(op.kind == 'question' for op in ops)
        for op in ops:
            if op.kind == 'question':
                st.questions.append((start, op.title or '', ' '.join(stem_text(i) for i in op.stem)))
        speech = durations[b] if text else 0.0
        if text:
            st.audio.append((start + 0.1, b))
        dur = (speech + 0.1 + PAD) if text else 0.0
        dur = max(dur, hold, 0.6 + STAGGER * len(ops) if ops else 0)
        if is_q:
            dur += PAUSE_HOLD
        t = start + dur
        st.check_layout()
        st.beat_ends.append(t)
    st.total = t + 1.0
    for e in st.els:
        if e.cur['alpha'] > 0:
            e.animate('alpha', 0.0, t + 0.2, 0.6)
    return st


# =========================================================== TTS (batched, cached)
def _tts_key(text):
    return hashlib.md5(f'{VOICE}|{RATE}|{text}'.encode()).hexdigest()


def _tts_paths(text):
    key = _tts_key(text)
    return CACHE / f'a_{key}.mp3', CACHE / f'a_{key}.json'


def _tts_words(js):
    words = json.loads(js.read_text(encoding='utf-8'))
    if not isinstance(words, list) or not words or any(
        not isinstance(word, list) or len(word) != 3 or not isinstance(word[2], str)
        or any(not isinstance(t, (float, int)) or t < 0 or not math.isfinite(t) for t in word[:2])
        for word in words
    ):
        raise ValueError(f'{js.name}: invalid word timings')
    return words


def _tts_cached(mp3, js):
    try:
        return mp3.stat().st_size >= 144 and bool(_tts_words(js))
    except (OSError, ValueError):
        return False


def _replace_bytes(path, data):
    # Another chapter can request the same line. Never expose a half-written cache file.
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name, suffix='.tmp', delete=False) as f:
        tmp = Path(f.name)
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


async def _tts_one(text, sem):
    import edge_tts
    mp3, js = _tts_paths(text)
    if _tts_cached(mp3, js):
        return
    for attempt in range(10):
        try:
            async with sem:
                if _tts_cached(mp3, js):
                    return
                words = []
                c = edge_tts.Communicate(text, VOICE, rate=RATE, boundary='WordBoundary')
                buf = bytearray()
                async for ch in c.stream():
                    if ch['type'] == 'audio':
                        buf.extend(ch['data'])
                    elif ch['type'] == 'WordBoundary':
                        words.append((ch['offset'] / 1e7, ch['duration'] / 1e7, ch['text']))
                if not buf or not words:
                    raise RuntimeError('speech service returned no audio or word timings')
                _replace_bytes(mp3, buf)
                _replace_bytes(js, json.dumps(words).encode('utf-8'))
                return
        except Exception as exc:
            if attempt == 9:
                raise RuntimeError(f'TTS failed for: {text[:60]}') from exc
            await asyncio.sleep(min(60, 3 * 2 ** attempt))


def tts_batch(texts, conc=None):
    texts = [t for t in dict.fromkeys(texts) if t]
    if conc is None:
        conc = int(os.environ.get('PE_TTS_CONCURRENCY', 6))
    if conc < 1:
        raise ValueError('TTS concurrency must be positive')

    async def run():
        sem = asyncio.Semaphore(conc)
        for i, completed in enumerate(asyncio.as_completed(_tts_one(t, sem) for t in texts), 1):
            await completed
            if len(texts) >= 50 and i % 50 == 0:
                print(f'speech ready: {i}/{len(texts)} lines', flush=True)
    asyncio.run(run())


def tts_info(text):
    mp3, js = _tts_paths(text)
    try:
        dur = _tts_duration(mp3)
        words = _tts_words(js)
        if not math.isfinite(dur) or dur <= 0:
            raise ValueError('invalid audio duration')
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f'Invalid TTS cache entry {mp3.name} for {text[:60]!r}') from exc
    return mp3, dur, words


def _tts_duration(mp3):
    # Edge emits 24 kHz mono MPEG-2 Layer III at 48 kbit/s. Its untagged frames
    # are 144 bytes, each spanning 576 samples. Only use the count when every
    # frame has the expected header. Probe other formats normally.
    data = mp3.read_bytes()
    frames, tail = divmod(len(data), 144)
    header = bytes.fromhex('ff f3 64 c4')
    if frames and not tail and all(data[i::144] == bytes([b]) * frames for i, b in enumerate(header)):
        return frames * 576 / 24000
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                             str(mp3)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def estimate(text):
    return len(text.split()) / 2.6 if text else 0.0


# =========================================================== subtitles
def make_subs(st, infos):
    subs = []
    for (t, b) in st.audio:
        mp3, dur, words = infos[b]
        # restore punctuation: map each spoken word onto the original token that contains it
        toks, ti, fixed = st.ch.beats[b][0].split(), 0, []
        for (off, d, w) in words:
            j = ti
            while j < len(toks) and w.lower() not in toks[j].lower():
                j += 1
            if j < len(toks):
                fixed.append((off, d, toks[j])); ti = j + 1
            else:
                fixed.append((off, d, w))
        words = fixed
        chunk = []
        for (off, d, w) in words:
            chunk.append((off, d, w))
            text = ' '.join(x[2] for x in chunk)
            if len(chunk) >= 7 or len(text) > 44 or re.search(r'[.?!;:]$', w):
                subs.append([t + chunk[0][0], t + off + d, text])
                chunk = []
        if chunk:
            subs.append([t + chunk[0][0], t + chunk[-1][0] + chunk[-1][1], ' '.join(x[2] for x in chunk)])
    for i in range(len(subs) - 1):        # hold each chunk until the next starts (if close)
        if subs[i + 1][0] - subs[i][1] < 0.6:
            subs[i][1] = subs[i + 1][0]
    return subs


# =========================================================== rendering
def _frame_state(st, t, elements=None):
    out = []
    for e in st.els if elements is None else elements:
        a = e.val('alpha', t)
        if a <= 0.004:
            continue
        img = e.img
        if e.frames:
            t0, dur, frames = e.frames
            i = int(min(max((t - t0) / dur, 0), 1) * (len(frames) - 1))
            img = frames[i]
        out.append((e, img, round(a, 3), round(e.val('x', t), 1), round(e.val('y', t), 1)))
    return out


def _frame_states(st, nframes):
    # Element opacity is one fade in followed by at most a fade out. Check only
    # elements whose visible lifetime intersects this frame and retain draw order.
    starts = sorted((e.anims[0][0], i) for i, e in enumerate(st.els))
    ends = [max(end for _, end, attr, _, _ in e.anims if attr == 'alpha')
            for e in st.els]
    active = []
    j = 0
    for i in range(nframes):
        t = i / FPS
        while j < len(starts) and starts[j][0] <= t:
            insort(active, starts[j][1])
            j += 1
        active = [k for k in active if t <= ends[k]]
        yield t, _frame_state(st, t, (st.els[k] for k in active))


WATERMARK = os.environ.get('PE_WATERMARK', 'mcarkade · Abhinav Pullela')
_WM = None


def _watermark():
    global _WM
    if _WM is None:
        f = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 22)
        x0, y0, x1, y1 = f.getbbox(WATERMARK)
        _WM = Image.new('RGBA', (x1 + 4, y1 + 4), (0, 0, 0, 0))
        ImageDraw.Draw(_WM).text((2, 2), WATERMARK, font=f, fill=(150, 150, 150, 120))
    return _WM


def _compose(state, sub_text=None):
    canvas = Image.new('RGB', (W, H), (0, 0, 0))
    wm = _watermark()
    canvas.paste(wm, (W - wm.size[0] - 28, H - wm.size[1] - 14), wm)
    for e, img, a, x, y in state:
        if a < 0.999:
            img = img.copy()
            img.putalpha(img.getchannel('A').point(lambda v, a=a: int(v * a)))
        canvas.paste(img, (int(x), int(y)), img)
    if sub_text:
        s = sub_img(sub_text)
        canvas.paste(s, (int(W / 2 - s.size[0] / 2), SUB_Y - 6), s)
    return canvas


def render(st, infos, out_path, sparse=False):
    out_path = Path(out_path)
    with tempfile.TemporaryDirectory(dir=out_path.parent, prefix=f'{out_path.stem}-') as scratch:
        scratch = Path(scratch)
        with ThreadPoolExecutor(max_workers=1) as pool:
            audio = pool.submit(render_audio, st, infos, scratch / 'audio.wav')
            render_frames(st, infos, scratch / 'video.mp4', sparse=sparse)
            audio.result()
        final = scratch / 'chapter.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(scratch / 'video.mp4'),
                        '-i', str(scratch / 'audio.wav'), '-map', '0:v', '-map', '1:a', '-shortest',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', str(final)], check=True)
        final.replace(out_path)


def _frame_changes(st, subs, nframes, start_frame=0):
    si = 0
    last_sig = None
    states = islice(_frame_states(st, start_frame + nframes), start_frame, None)
    for i, (t, state) in enumerate(states):
        while si < len(subs) and subs[si][1] < t:
            si += 1
        sub = subs[si][2] if si < len(subs) and subs[si][0] <= t <= subs[si][1] else None
        sig = (tuple((id(e), id(img), a, x, y) for e, img, a, x, y in state), sub)
        if sig != last_sig or i == nframes - 1:
            yield i, state, sub
            last_sig = sig


def _sparse_filter(changes, directory):
    last_gap = 0
    commands = []
    for transmitted_index, (frame_index, _, _) in enumerate(changes):
        gap = frame_index - transmitted_index
        if gap != last_gap:
            # Select the command between adjacent input frame timestamps.
            at = (transmitted_index - 0.5) / FPS
            commands.append(f'{at:.8f} setpts expr PTS+{gap};')
            last_gap = gap
    if not commands:
        return []
    (directory / 'frame-timeline.txt').write_text('\n'.join(commands) + '\n', encoding='ascii')
    # Restore exact CFR frames after colour conversion and before encoding.
    return ['-vf', f'sendcmd=f=frame-timeline.txt,setpts=PTS,format=yuv420p,fps={FPS}']


def render_frames(st, infos, out_path, sparse=False, *, start_frame=0, stop_frame=None):
    full_frames = int(st.total * FPS)
    stop_frame = full_frames if stop_frame is None else stop_frame
    if not 0 <= start_frame < stop_frame <= full_frames:
        raise ValueError(f'Invalid frame range {start_frame}:{stop_frame} of {full_frames}')
    nframes = stop_frame - start_frame
    changes = _frame_changes(st, make_subs(st, infos), nframes, start_frame)
    filters = []
    if sparse:
        changes = list(changes)
        filters = _sparse_filter(changes, out_path.parent)
        print(f'video pipe: {len(changes)} changing frames of {nframes} at {FPS} fps', flush=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', *filters, '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage',
           '-crf', '21', '-pix_fmt', 'yuv420p', '-threads', '3', out_path.name]
    previous, last = 0, None
    with subprocess.Popen(cmd, cwd=out_path.parent, stdin=subprocess.PIPE) as ff:
        for i, state, sub in changes:
            if not sparse and last is not None:
                for _ in range(i - previous - 1):
                    ff.stdin.write(last)
            last = _compose(state, sub).tobytes()
            ff.stdin.write(last)
            previous = i
        ff.stdin.close()
        if ff.wait():
            raise subprocess.CalledProcessError(ff.returncode, cmd)
    if sparse:
        media = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=nb_frames,duration_ts,time_base', '-of', 'json', str(out_path)
        ], text=True))['streams'][0]
        actual_duration = int(media['duration_ts']) * Fraction(media['time_base'])
        if int(media['nb_frames']) != nframes or actual_duration != Fraction(nframes, FPS):
            raise RuntimeError(f'CFR render did not preserve all {nframes} frames at {FPS} fps: {media}')


def render_audio(st, infos, out_path):
    # audio: place every clip on one PCM timeline
    sr = 24000
    pcm = np.zeros(int((st.total + 1) * sr), dtype=np.float32)
    for (t, b) in st.audio:
        mp3 = infos[b][0]
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(mp3), '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'],
                             capture_output=True, check=True).stdout
        if not raw:
            raise RuntimeError(f'No audio samples for beat {b}: {mp3.name}')
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
        i0 = int(t * sr)
        n = min(len(a), len(pcm) - i0)
        pcm[i0:i0 + n] += a[:n]
    pcm = np.clip(pcm, -32768, 32767).astype(np.int16)
    import wave
    with wave.open(str(out_path), 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())


def contact_sheets(st, out_dir, per=12):
    """Still of the end state of every beat, tiled with beat numbers and narration snippets."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob('sheet_*.png'):
        f.unlink()
    thumbs = []
    for b, te in enumerate(st.beat_ends):
        img = _compose(_frame_state(st, te - 0.02)).resize((640, 360))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 640, 22], fill=(50, 50, 50))
        d.text((4, 4), f'{b}: {st.ch.beats[b][0][:95]}', fill=(255, 220, 0))
        thumbs.append(img)
    cols = 3
    for s in range(0, len(thumbs), per):
        chunk = thumbs[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (640 * cols + 4 * (cols - 1), 364 * rows), (90, 90, 90))
        for i, im in enumerate(chunk):
            sheet.paste(im, ((i % cols) * 644, (i // cols) * 364))
        sheet.save(out_dir / f'sheet_{s // per + 1:02d}.png')
    return len(thumbs)
