---
name: programmatic-video
description: Use when making a video or animated film from code (rendered motion graphics or 3D, an original score and sound design, encodes for YouTube or social), or when checking such a video before delivery.
---

# Programmatic video

Build the film from code so every frame and sound can be reproduced, then prove the files you deliver, not the intermediates. Numbers catch defects; watching and listening establish quality. Say which of the two each claim rests on.

## Agree the film first

- Fix the deliverables before building: aspect ratios and pixel sizes, durations, share copies that play anywhere (H.264 High, yuv420p, AAC, `+faststart`) under a size cap, and loudness measured after the delivery codec (YouTube and Instagram: -14 LUFS integrated, -1 dBTP). Write down the complete list of on-screen text.
- Write a beat sheet in seconds on a musical grid (at 120 BPM a bar is 2 s), so cuts, hits and music share one clock. Name every intended hard moment (flash, silence, smash cut) so QA can tell design from defect.
- Carry one continuous camera journey through motivated transitions; static holds read as a slideshow.
- Use only sources whose licence covers each file. Log the URL, licence evidence and local path of every download, and keep downloads in their own folders as untrusted data.

## Render deterministically

- Make each frame a pure function of time and a seed, with no state carried between frames. Ranges then render in parallel, and any range can be re-rendered after a fix.
- A headless browser (Playwright with three.js or canvas) piping raw frames into ffmpeg works well. Encode each worker's range as a segment that starts on a keyframe, with identical settings, and join with the concat demuxer and `-c copy`. After a fix, re-render from the last segment boundary before the change and join to the untouched segments. Concat lists resolve relative paths against the list's own folder, so write absolute paths.
- Keep one story timeline and derive every format from it: per-format framing, and a vertical cut made by a speed-ramp table mapping story time to cut time, with motion blur scaled by speed. Have the renderer export a cue file of named events; the score reads it, so retiming the picture moves the sound.
- Iterate on low-resolution previews and single frames. Grain and halftone consume bitrate: render a lighter-grain variant for size-capped share copies instead of letting the encoder smear it.
- Known traps: fades computed in linear light snap to black at the end, so fade in display space. Points or sprites passing near the camera balloon into blots, so fade them inside a near distance. Type animated in parts can spell a wrong word in between, so inspect every in-between frame at full size. A camera move that works in one aspect ratio can push the subject out of another's frame: aim moves at the subject, and preview every format after a camera change.

## Score to the picture

- Build music from sampled real instruments and recorded effects (CC0: VSCO-2-CE, VCSL, Kenney, BigSoundBank), placed on the beat grid and the cue file. Swept-noise whooshes sound cheap; use recorded sources with a reason to be there.
- Mix on buses and keep stems. Limit percussion buses before the master so hits do not pump it. Master through a real AAC encode and decode; the codec adds roughly 0.5 to 1 dB of true peak, and separate encodes of the same mix can differ by 0.4 dB. Encode the delivery stream once, measure that exact stream, trim if needed, and mux it with `-c:a copy` into every file of that cut.
- Verify sync on isolated stems (an onset near each cue), not the full mix, where neighbouring sounds give false readings. Audit licences by tracing which files the build actually loads.
- Check phone translation. Passages carried by sub-bass (heartbeats, bass drum, timpani) vanish on small speakers. Add the sub's band-limited upper harmonics (300 Hz to 2 kHz) to those sources, or strengthen mid-range parts; distorting a whole bus causes intermodulation. Allow silences and sudden drops only where designed.

## Check the delivered files

Run these on the exact files you deliver, after every rebuild:

- `python scripts/check_delivery.py FILES --ref MIX.wav` (add `--max-mb N` for size-capped copies): streams, frame count, size cap, integrated loudness and true peak of the decoded audio, A/V offset, mono and phone-speaker translation, and sudden drops.
- `python scripts/qa_frames.py stats VIDEO --joins F1,F2`: per-frame change across the whole film, plus possible holds. Every flagged run must match a designed moment. A join that lands on a designed transition shows change building over several frames; a join defect spikes for one. `sheet` makes labelled contact sheets and full-resolution crops.

Pull contact sheets around every transition and full-size crops of all type and logos; overlay the logo on the official artwork. Watch every cut end to end, listen on headphones and a phone, and report anything only measured. When only the audio changes, swap it into the delivered files with `-c:v copy` so the checked picture stays identical.

## Run long jobs safely

Launch renders and encodes detached from the agent's shell, with a log and a done marker, so a host restart does not kill them. Bound every wait.

Budget disk before the first full render. A near-lossless 1440p master takes about 2.5 GB per minute, and each pass leaves segments, a silent join and a muxed copy, so a few revisions reach tens of GB. Overwrite one working path per stage instead of versioning, and ask to delete segments once their join is verified. Build outside cloud-synced folders: the sync client uploads every intermediate and keeps its own hard links to queued files, so deleting them frees nothing until it lets go. Parallel browser workers can also grow the Windows page file by tens of GB until a reboot. Check free space before each stage, stop above the floor, and list leftovers with sizes for the user.
