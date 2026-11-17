---
name: physics-explained-video
description: Use when making a narrated study video that teaches physics or maths derivations on a black board in the style of the Physics Explained YouTube channel. Covers equations that build up term by term, pause-and-try exam questions, a neural voice with burned-in subtitles, and chapter markers. Use it to turn a study guide into a one-shot revision video, or to fix the narration of such a video.
---

# Physics-Explained-style study video

Turn a verified study guide into a one-shot revision video:
- a black board where equations grow term by term as a voice explains them;
- small worked examples after each idea;
- many pause-and-try exam questions;
- burned-in subtitles, a corner watermark and chapter markers.

The toolkit in `scripts/` handles layout, timing, speech, subtitles, rendering and joining. Your job is the teaching and the narration.

## Defaults for this user
- Voice: `en-US-AndrewNeural` at `+100%` through edge-tts. Subtitles burned in.
- Watermark: `mcarkade · Abhinav Pullela`, bottom right. Change it with the `PE_WATERMARK` environment variable.
- Audience: one student learning the topic from zero before a closed-book quiz. They have ADHD and learnt from JEE one-shot videos.
  - Pace comes from content density, not speed.
  - Something new appears in every beat.
  - Never dim earlier lines.
- Recommend VLC to watch it. Chapters appear under Playback → Chapter; `[` and `]` change speed.

## Workflow
1. **Scope and source.** Use a verified study guide as the single source of truth, with the syllabus already checked. Plan chapters that follow a JEE one-shot flow: basics with context, then derivations, then examples, then exam questions, then a recap, then a mock quiz.
2. **Set up.**
   - Copy `scripts/*` into a working folder inside the project's working-files area, not the deliverables folder.
   - Install `edge-tts`, `matplotlib`, `pillow` and `numpy`. Check that `ffmpeg` is on the PATH.
   - Export any guide diagrams to `diagrams/NAME.png`.
3. **Write the chapters, one at a time.**
   - Build the visuals with the ops in `references/authoring.md`.
   - Write the narration under the rules in `references/narration.md`. It is the most important file here: read it before writing any line.
   - Whoever writes the narration must see the screen ops beat by beat and must hold the style model: read the Physics Explained transcripts, then apply the unslop skill. Give the writing to the strongest writer available and the checking to the strongest independent reviewer, whichever models those are at the time.
   - Keep one voice per video. Narration split across many independent authors with only a brief came out robotic and half-sentenced, and the user rejected it.
   - After each chapter, run `python make.py chNN --check` and require `layout OK`.
4. **Check before rendering.**
   - Run `--sheet` and look at every contact sheet.
   - Then have an independent reviewer, not the writer, check the narration with `references/review_brief.md`. It covers physics, agreement between what is said and what is on screen, text-to-speech traps, and tone.
   - Judge each fix before applying it. Reviewers tend to reintroduce stiff wording such as "capital R" or "the whole expression measured per metre". Keep the correction and rephrase it naturally.
   - Rendering costs minutes per chapter, so fix first.
5. **Render.**
   - `sh queue.sh ch01 ch02 …` renders sequentially, with logs in `logs/`.
   - Run at most three queues in parallel; the user's laptop runs other work.
   - Speech is cached per sentence, so a re-render after a small narration fix is cheap.
   - Deliver finished chapters as they land, so the user can start watching.
6. **QA.**
   - `python qa.py` reports duration, audio level, silences of 4 s or more, and still stretches of 8 s or more.
   - Extract a few frames to check the watermark, subtitles and layout. A grey line in a still is usually a line mid fade-in, not dimming; check the next second before "fixing" it.
   - Speech can't be listened to, so check the narration text instead. Say so in the report.
7. **Join and deliver.**
   - Before joining, confirm every `out/chNN.mp4` is newer than `chapters/chNN.py` (`[ out/ch01.mp4 -nt chapters/ch01.py ]`). A render that started before the last narration apply is stale.
   - `python make.py --join NAME` writes `out/NAME.mp4` with chapter markers and prints the timestamps.
   - Copy the video and a `Chapters.txt` to the course's deliverables folder.
   - Report the length, chapters, question count, what was checked and what wasn't.
8. **Clean up after the user approves:** delete `out/`, `cache/`, `review/`, `logs/` and any `pe_transcripts/`.

## Operational lessons
- **A render reads the chapter script once, when it starts.**
  - If you edit a chapter while its render is running, stop that render and queue it again.
  - Compare the script's modification time with the "start chNN" time in `logs/`.
  - Stop only your own `make.py chNN` process, found by its command line. Never kill every ffmpeg or python process: the user runs other work.
- **Chaining queues.** `tools/after.sh LOG CH chapters…` waits for `done CH` in another queue's log before rendering, so you never run more than three renders at once.
- **Fixing narration only.**
  - `tools/narr.py extract`, then edit `narr/chNN.new`, then `tools/narr.py apply` swaps the speech without touching the visuals.
  - `tools/merge_review.py chNN [--skip 012,036]` merges a reviewer's `narr/review_chNN.txt`, so you can apply it after judging it.
  - Back up `chapters/` before the first apply.
- **Early delivery.** `tools/publish_chapters.sh DEST` copies each fresh chapter, under a readable name, into the deliverables folder. Tell the user to start watching while the rest render.
- **Length.** The `--check` estimate ran about 20% long at `+100%` (93 min estimated, 76.5 min rendered). The lecturer-style rewrite came out no longer than the terse first version (76.5 vs 80 min), so full sentences cost little time. Keep beats under about 35 words.
- **Transcripts.** The channel is `@PhysicsExplainedVideos`. `@PhysicsExplained` is a different, unrelated channel. Download subtitles only (a few hundred KB), never the videos.
- **Install on Windows.** Git Bash `ln -s` fails without developer mode. Link skills with a PowerShell junction: `New-Item -ItemType Junction`.

## Pitfalls already fixed in `studio.py` (keep them)
These are in `_prep_tex`:
- `\frac` → `\dfrac`;
- dots before exponents become `\dot{x}{}^2`;
- tight operators inside `^{}` and `_{}`;
- airy `=`;
- `{-}\,\dfrac` for a leading minus.

Matplotlib mathtext has no `\text`, `\begin`, `\boxed` or `\big`. In a Bash heredoc, backslashes collapse, so write chapter files with the Write or Edit tool, never with heredocs.

## Done means
- Every chapter passes `--check`, and its sheets have been looked at.
- The narration has been checked against `narration.md` and by a reviewer.
- `qa.py` is clean.
- The joined file plays with its chapter markers.
- The user has a clickable link and knows which player to use.
