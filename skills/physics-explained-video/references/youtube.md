# YouTube upload kit

Prepare everything the user needs to upload the video, and leave the upload to them. Put the files next to the video in the deliverables folder and show each text block in your reply, ready to paste.

`python make.py --join NAME` writes `out/NAME_timestamps.txt`. For a video in parts, build one kit per part. It has the chapter list in YouTube format and the time every QUESTION card appears, measured from the real speech timing. Build the kit from that file. Do not estimate the times.

## What to hand back

**Title.** Name the topics first, then the course code and the assessment: `Central Forces and Hamiltonian Mechanics | PHY F211 Classical Mechanics - Quiz 2`. Keep it under 100 characters.

**Description** (`YouTube_Description.txt`). Use plain lines:
- course name and code;
- textbook and sections covered;
- `# Chapters`, followed by the chapter list;
- a one-line list of topics.

The description has three limits:
- **Only the chapter timestamps.** YouTube reads every timestamp in the description as one chapter list. A single gap under 10 seconds cancels all chapters, and two question cards are often closer than that. The chapter list must start at `00:00`, have at least three entries, and be in order. Use `h:mm:ss` from one hour.
- **No `<` or `>`.** YouTube rejects the description. Write "negative k", not "k < 0".
- **At most 5,000 characters.**

**Problems box** (`YouTube_Problems.txt`). YouTube's Problems field takes 800 characters at most. Pick one or two main questions per chapter, plus any mock quiz, as `timestamp short question`. For example: `33:37 Apsidal angle for f = −k/r^(5/2)`. Count the characters before handing it over.

**Pinned comment** (`YouTube_Pinned_Comment.txt`). This is the full question list, one line per question with its timestamp. Comment timestamps are clickable and do not affect chapters. Rewrite each raw TeX stem as one short line with Unicode maths: `½mẋ²`, `r₀`, `θ̇`, `≫`, `√`. Collapse a block of rapid-fire questions into one line.

**Thumbnail** (`Thumbnail.png`). Make it 1280×720 and under 2 MB, in the same board style as the video:
- black background;
- the topic in large warm-white and teal text;
- one key equation in a teal box and one simple diagram;
- a line such as "One-shot revision · 100+ pause-and-try questions";
- the course code.

It must stay readable at phone size. Render it, look at it, and size any box from the measured text so nothing overflows.

## Tell the user

- Turn off **Allow automatic chapters**, so the written list is used.
- Chapters can take a few hours to appear after saving.
- If chapters still don't appear, check Studio → Settings → Channel → Feature eligibility. Phone verification unlocks the intermediate features.
- If the comment can't be pinned, check that comments are turned on for the video. Then pin it from the comment's ⋮ menu while signed in as the channel.
