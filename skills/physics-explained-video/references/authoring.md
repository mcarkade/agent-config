# Authoring chapters

A chapter is a Python file `chapters/chNN.py` built from beats. Layout, timing, voice, subtitles and the watermark are automatic. `scripts/example_chapter.py` shows most ops; start from it.

## Chapter skeleton
```python
from studio import *
import numpy as np

ch = Chapter(5, 'The orbit equation')
say("narration ...", OP, OP, ...)      # one beat
```
A **beat** is `say(narration, *ops)`. The ops start when the beat starts, and the beat lasts as long as its speech.
- **Narration:** 1–2 short sentences, usually 8–25 words.
- **Something must appear or change in every beat.**
- **Length:** a beat over about 8 s (roughly 35 words) is too long; split it.

## Ops (all layout is automatic; you never give coordinates)
| Op | What it does |
|---|---|
| `M(tex, id=None, size=50)` | Equation line. `tex` may be a **list of parts** so you can target terms later. |
| `KEY(tex, id=None)` | Key result with a teal box. Use for results to remember. |
| `G(id, parts, k)` | Grow an equation term by term. Call with k = 1, 2, 3… in successive beats, timed to the narration. This is the signature look; use it for important derivations. |
| `T(text)`, `N(text)`, `LABEL(text)` | Caption (cream), explanatory note (peach), small teal label. Inline maths with `$...$`. |
| `ROW(a, b, ...)` | Items side by side with teal arrows between, e.g. `ROW(N('no torque'), N('l conserved'))`. Use `arrows=False` for plain side-by-side. Members can have ids. |
| `CIRCLE(id, terms=(i, j))`, `STRIKE(id, terms)`, `UNDER(id, 'label', terms)`, `BOX(id)`, `ARROW(a, b)` | Highlight, cancel, annotate, box, connect. `terms=(i, j)` covers parts i..j−1 of a list-of-parts equation. |
| `CLEAR(*keep)` | Fade everything except the kept ids, which slide to the top. Use at every change of idea. Carrying the key line up with `CLEAR('id')` is how a derivation continues. |
| `OUT(*ids)` | Fade specific items. Rarely needed. |
| `FIG(id, draw=None, axes=dict(xlim=..., ylim=..., xlabel='$r$', ylabel='$V$', equal=False, frame=True, origin=(x0, y0)))` | Matplotlib figure on the left half. It clears unpinned items; while it is visible, items flow in the right column (about 800 px wide, so keep right-column lines short). |
| `FIGADD(fig_id, id, draw)` | Add a layer on the same axes: a new curve, an energy line, points. |
| `ANIM(fig_id, id, draw(ax, u), dur=3)` | Animated layer, e.g. tracing an orbit (u goes from 0 to 1). |
| `DIAGRAM(id, name)` | A ready-made picture from the guide, placed like a figure. It loads `diagrams/NAME.png`. |
| `QUESTION(*stem, title='short')` | Clears the board, shows "QUESTION n · title", the stem, and "Pause and try", followed by a silent hold of `PAUSE_HOLD` seconds (5 s). End that beat's narration on the question itself, not on a hint. The stem stays pinned at the top. |
| `SOLVE()` | Next beat: removes "Pause and try"; the solution flows under the stem. When the board fills, everything except the stem auto-clears. |
| `HOOK(text, sub=None)` | Big centred hook question. Use at the start of the chapter and of big sections. |
| `wait(sec, *ops)` | A silent beat. Rare. |

Colours for figures: `BLUE, ORANGE, PINK, GREEN, YELLOW, EQ` (warm white), `TEALH, REDH`. Draw thin lines (lw 2–3) on a black background, with no ticks. The FIG's `frame` draws arrowed axes through `origin`.

Diagrams are project-specific PNGs in `diagrams/NAME.png` (transparent or black background, warm colours). Export them from the study guide's figures when it has them.

## Maths text (matplotlib mathtext, not full LaTeX)
- **Allowed:** `\frac`, `\sqrt{}`, `\dot{}`, `\ddot{}`, `\partial`, `\int`, `\sum`, `\left( \right)`, `\mathrm{}`, `\mathbf{}`, `\vec{}`, `\hat{}`, `\cdot`, `\times`, `\leq`, `\geq`, `\neq`, `\approx`, `\propto`, `\infty`, Greek letters, `\quad`, and `^{}`, `_{}`.
- **Not available:** `\text` (use `\mathrm{}`), `\begin{...}` and matrices, `\boxed`, `\Big`, `\big`, `\overline X` without braces, `\sqrt2` without braces. For matrices, show one row per `M` line or describe them in words.
- **Spacing:** write `a = b`, `x + y`, `x - y` with spaces around binary operators. A leading minus `-\frac{k}{r}` is handled automatically.
- **Subscript words:** `V_{\mathrm{eff}}`, `r_{\min}`, `r_{\max}`.
- **Unicode:** in `T`/`N` text, plain Unicode like → · ≤ is fine. Never use ✓ or ⟺, which the text font lacks.
- **Traps:** `\dots` renders as a dot accent, so use `\cdots` or `\ldots`. `\le` and `\ge` fail; use `\leq` and `\geq`. Write piecewise functions on one line, `0\ (x < a),\ 1\ (x\geq a)`, since `cases` is unavailable. Use raw strings for every op holding a backslash.
- **Figures in loops:** bind loop variables as lambda defaults, `(lambda n, col: lambda ax: ...)(n, col)`, or every layer draws with the last value.

## Screen discipline
- Keep about 5 lines on the board at most before you CLEAR, or carry a line up. `T` and `N` lines are short phrases of up to about 12 words.
- A figure question puts its stem in the narrow right column, so keep that stem very short.
- When a board overflows, everything unpinned fades at once, so a solve step and its result can vanish together. Split a long solve across beats, or CLEAR and restate the line you need. Never CLEAR inside a SOLVE: it removes the pinned question. In a long derivation, give the lines you still need an `id` and CLEAR to them before the board fills.
- A FIG during a solve moves everything into the right column, and a wide pinned stem can no longer fit. Put the figure before the QUESTION card, or after the solve. `OUT` on a figure gives the full board width back.
- Every beat needs spoken words; for a deliberate silent hold use `wait()`.
- Set multiple-choice options with fractions as `M` lines at size 40–44, two options per line. In a `T` line, inline fractions are too small for a phone.
- A `T` or `N` line containing maths doesn't wrap. Keep each one short, or split it into two.
- Every chapter starts with a hook and ends with a recap of its boxed results plus a couple of rapid-fire questions. The last line of every solution is a KEY answer.
- After writing, run `--sheet` and look at every sheet.
