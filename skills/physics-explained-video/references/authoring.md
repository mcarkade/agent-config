# Authoring chapters

A chapter is a Python file `chapters/chNN.py` built from beats. Layout, timing, voice, subtitles and the watermark are automatic.

## Source of truth
Teach from a verified study guide for the course (for example one made with the study-notes-pdf skill). Every result, sign convention and answer must agree with it. Verify any new worked example by hand and with sympy. Note any sign-convention differences between the guide, the textbook and the instructor on screen.

## Files and commands
Work inside the project working folder that holds `studio.py`.
- **Your chapters:** write `chapters/chNN.py`. Study `example_chapter.py` first; it is a worked example using every feature.
- **Check:** `python make.py chNN --check`. It must end with `layout OK` and no problems. It prints the estimated length and the number of questions.
- **Contact sheets:** `python make.py chNN --sheet` writes stills of the end of every beat to `review/chNN/sheet_*.png`. Open them and look: clutter, tiny text, bad breaks, ugly maths.
- **Don't render.** Don't run `--render`; the orchestrator renders.
- **Don't edit the toolkit.** Don't edit `studio.py`, `make.py` or other people's chapters. If you need a feature that's missing, work around it and say so in your final message.

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
| `DIAGRAM(id, name)` | A ready-made picture from the guide, placed like a figure. See the list below. |
| `QUESTION(*stem, title='short')` | Clears the board, shows "QUESTION n · title", the stem, and "Pause and try", followed by a silent hold. The stem stays pinned at the top. |
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
- **Unicode:** in `T`/`N` text, plain Unicode like → · ≤ is fine. Never use ✓.

## Narration
Follow `narration.md`. It overrides any narration habit you have.

## Structure of every chapter (JEE one-shot flow)
1. **Hook (one beat):** a puzzle or question the chapter answers.
2. **Build from the basics with context:**
   - Define every symbol at first use.
   - Derive the key results step by step with G/M lines, circling or striking the term being worked on.
   - Box each key result with KEY.
3. **Small worked examples right after each idea, 2–4 per idea.** Quick, concrete, and showing *how to solve*. Questions are a central focus: the viewer wants many.
4. **Exam questions with pause-and-try:**
   - Each one: QUESTION, then SOLVE, then a full solution.
   - The last line of every solution is a KEY answer.
   - Next comes one beat of "the trick to remember" or "common mistake" when useful.
   - Use the study guide's question bank (tutorial, past-quiz and mock questions) for your topic. Include all the important ones and add your own small ones.
   - **Target 5–8 QUESTIONs per chapter**, plus the small worked examples.
5. **Method summary:** "How to attack this type" in 2–4 short lines.
6. **Recap:** CLEAR, then the 2–4 boxed results of the chapter, then 2 rapid-fire QUESTIONs with one-line answers.

## Screen discipline
- At most about 5 lines on the board before you CLEAR or carry a line up. No walls of text: `T` and `N` lines are short phrases (at most about 12 words).
- No dimming anywhere. Finished things either stay, or leave via CLEAR.
- **A FIG inside a QUESTION:** the pinned stem moves to the right column, which is narrow. Keep such stems very short, or pose a figure question as stem text only.
- After writing, run `--check` and `--sheet` and look at every sheet. Fix anything cramped, too small, wrongly wrapped or overlapping, and any beat where nothing new appears.

## Length
Each chapter has a target in minutes of the final video (2x voice) that `--check` estimates. Stay within ±20%.

## Final message
Report:
- for each of your chapters: beats, number of QUESTIONs, estimated length, and which guide units and questions it covers;
- anything you couldn't fit, and any doubt about the physics.
