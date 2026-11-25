---
name: physics-explained-video
description: Use when making a narrated study or revision video that teaches physics or maths on a black board, in the style of the Physics Explained YouTube channel, or when fixing the narration of such a video.
---

# Physics-Explained-style study video

A student should be able to learn a topic from zero by watching this video once, pausing to try each question, and should enjoy it enough to keep watching. Everything below serves that. The toolkit in `scripts/` handles layout, speech, subtitles and rendering, so your effort goes into the teaching and the narration.

## What makes it work

**1. It teaches.**
- Teach from a verified study guide for the course. Every result, sign convention and answer must agree with it. If there is no guide yet, make one first with the `study-notes-pdf` skill.
- Assume the viewer starts from zero. Before planning, list the prerequisite maths and notation each chapter needs, and teach whatever the viewer may not know before using it.
- Follow the JEE one-shot flow in each chapter:
  - a hook question;
  - the idea and why it is needed;
  - a step-by-step derivation on the board;
  - small worked examples right after each idea;
  - exam questions with pause-and-try;
  - a short method summary and recap.
- Questions are the backbone. Give many, from easy checks to exam level, and solve each in full.
- Build each idea up with small check questions before the big ones. For an exam one-shot, organise the exam part of each chapter by question type:
  - how to recognise the type;
  - a method card with the steps and the usual traps;
  - several solved questions from easy to hard, taken from the textbook's end-of-chapter problems (hard ones included) and from every past paper, tutorial and quiz.
- Solve each question the way a student should write it in the exam, so they can copy the method straight onto the answer sheet:
  - the figure first, then what is given and what to find;
  - every step is its own line on the board, slow enough to follow along;
  - the conditions the method needs are checked in writing;
  - a quick check, then the boxed answer.

  The voice explains why each step works, but never carries a step the board leaves out. A long question can take several minutes. Solve multiple-choice questions with working lines too, not just the key.

**2. It looks like Physics Explained.**
- Use a black board with warm white equations that grow term by term as the voice explains them.
- Circle or strike the term being worked on. Box each key result.
- Clear the board between ideas, carrying the key line up when a derivation continues.
- Draw thin-line plots and diagrams on the left while the maths flows on the right.
- Never dim earlier lines: they either stay or leave on a clear.
- `references/authoring.md` has the ops that do all this.

**3. It sounds like a person teaching.** This is where videos fail most often.
- Before writing, read real Physics Explained transcripts (`python tools/fetch_transcripts.py`) and match how he talks:
  - full sentences joined by "Okay, so", "Now", "And so", "Well";
  - narrating the board as it changes;
  - asking a question, then answering it.
- Explain clearly, at the level Physics Explained uses. After a step of maths, say in plain words what it means or why it works. Keep the real physics, the proper terms and the full argument; simple wording, not a simpler subject. Viewers value these explanations most, so never cut them for speed, and never water the physics down to fit them.
- Write for the ear. A TTS voice reads every word literally, so say maths the way a lecturer would ("one over r squared", "per metre", "cosine").
- Apply the unslop skill to the narration and the on-screen text.
- `references/narration.md` has the details and the review checklist.

**4. It holds attention.** Pace comes from density, not speed:
- something new appears in every beat;
- there is no filler, but a hard step gets more beats and a plain explanation instead of being rushed;
- the recap repeats the key results on purpose;
- each section ends by pointing at the next question.

**5. It is one story, not a stack of lessons.** Chapters written one at a time come out as separate units, and the whole video stops feeling cohesive. Plan the links when you plan the chapters:
- open each chapter from where the last one stopped: the result it just gave, or the question it left open;
- close each chapter by saying what the next one needs and why it comes next;
- when an earlier result returns, call it back by name ("the effective potential from chapter three") instead of restating it cold.

Viewers often watch on YouTube on a phone, so keep board text large enough to read on a small screen.

## Who does what

The narration and visuals are one piece of work. Write each chapter's screen ops and narration together, so every line says what is appearing as it appears. Keep one writer for the whole video, so it has one voice: narration split across briefed authors comes out choppy and robotic.

Then give it to an independent reviewer who did not write it. Choose the writer and the reviewer by which models are strongest at writing and at reviewing at the time. Judge each review fix before applying it, and keep the correction in natural speech.

## Workflow

1. Plan chapters from the study guide's syllabus, with a rough length for each. Fit the shape to the course: the chapter split, question mix and companion material differ between subjects, so treat this skill as principles, not a template. When deepening an existing video, keep its verified derivations and chapter links and build the new question sections around them.
   - For a long, question-heavy video, write a question bank per chapter first, in one fixed format: types, method cards, solved questions tagged easy, medium or hard, and MCQs with working. Briefed workers can write banks in parallel, since a bank is source material, not narration. Check its answers against keys where they exist.
   - Script one pilot chapter at full depth and get the user's verdict on depth and pacing before scripting the rest.
2. Copy `scripts/*` into a working folder in the project. You need `edge-tts`, `matplotlib`, `pillow`, `numpy`, `yt-dlp` and `ffmpeg`. The renderer uses Windows fonts (Cambria and Segoe UI); change the font paths in `studio.py` on another OS. Put any figures from the guide in `diagrams/NAME.png`.
3. Write each chapter as `chapters/chNN.py`. Start from `example_chapter.py`, which shows most ops.
4. Run `python make.py chNN --sheet` and look at every contact sheet. Fix clutter, tiny text and beats where nothing new appears. Have the narration reviewed. Fixing before rendering is cheap; rendering costs minutes per chapter.
5. Render with `sh queue.sh ch01 ch02 …` from a POSIX shell such as Git Bash, or run `python make.py chNN --render` for each chapter. A render reads the chapter file when it starts, so re-render any chapter edited after that. Several queues can run in parallel and share the TTS cache; check `logs/` for chapters marked FAILED and re-queue them, since the TTS service drops requests under load. `--tts` caches a chapter's voice without rendering, and `PE_SPARSE=1` speeds up long renders by sending only the frames that change.
6. Run `python qa.py`, or `python qa.py ch01 ch02 …` to check one part while another renders. It reports silences, frozen stretches and audio levels. Look at a few frames.
7. Run `python make.py --join NAME` to write one file with chapter markers and print the timestamps. The join checks each chapter's question list against its source and refuses anything over YouTube's 12-hour upload limit. Deliver it with a chapter list. A full course can ship as one video or as parts; follow the user's choice. If one video runs over the limit, cut easy repeats, never the hard questions. For parts, split at a natural break, open each later part with a short review of the earlier ones, and join each part with `--join NAME ch01-ch08`.
8. Listen to a sample of the speech if your tools allow it: a hook, a derivation and a question from a few chapters. If you can't, say that pronunciation was checked only through the text. Report what you checked and what you couldn't.
9. Once the user approves the video, ask whether to prepare a YouTube upload. If they say yes, follow `references/youtube.md` and hand back a folder they can upload from. The user uploads it, so they can choose the playlist and other settings for each video.

If the video ships with PDFs, such as worked solutions or a formula sheet, make them with the `study-notes-pdf` skill. They show the same steps as the video, in one neat, consistent layout, with only what the student uses: no source notes, process comments or padding.

To change only the narration of a finished chapter, `tools/narr.py extract chNN` lists each beat's text next to what is on screen. Edit it as `narr/chNN.new`, then run `tools/narr.py apply chNN`. The visuals stay untouched.

## Defaults

- Voice: `en-US-AndrewNeural` at natural pace (`+0%`), with burned-in subtitles. Both are set in `studio.py`. Viewers speed up on YouTube themselves; use a faster rate only when the user asks.
- Intermediates: the TTS cache, renders and contact sheets go to `PE_WORK` (default: the working folder). Point it at scratch storage when disk is tight, and delete it after delivery.
- Watermark: bottom right, from the `PE_WATERMARK` environment variable. The default is `mcarkade · Abhinav Pullela`.
- Player: recommend one that shows chapter markers, such as VLC.
