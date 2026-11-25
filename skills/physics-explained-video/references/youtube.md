# YouTube upload kit

Prepare everything the user needs to upload the video, and leave the upload to them. Put the files next to the video in the deliverables folder and show each text block in your reply, ready to paste.

`python make.py --join NAME` writes `out/NAME_timestamps.txt`. For a video in parts, build one kit per part. It has the chapter list in YouTube format and the time every QUESTION card appears, measured from the real speech timing. Build the kit from that file. Do not estimate the times.

## What to hand back

**Title.** Keep it short: what the video covers, then the course code and the assessment. A part-course video names its topics (`Central Forces and Hamiltonian Mechanics | PHY F211 Quiz 2`); a full-course video names the course (`Classical Mechanics One-Shot | PHY F211 Compre`). Keep it under 100 characters.

**Description** (`YouTube_Description.txt`). Keep it short, with no intro paragraph. Use plain lines, in this order:
- a link line for each companion PDF;
- `Chapters`, followed by the chapter list;
- the course name and code;
- `References`: every source used, the textbook and sections, and any lecture series or playlist the teaching drew on.

**Tags.** Put the topics here, not in the description: course code, course name, assessment and the main topics. YouTube allows 500 characters in all. Give the tags without trailing punctuation.

The description has three limits:
- **Only the chapter timestamps.** YouTube reads every timestamp in the description as one chapter list. A single gap under 10 seconds, or one time out of order, cancels all chapters. Any list of questions, even a short "start here" list, goes in the pinned comment. The chapter list must start at `00:00`, have at least three entries, and be in order. Use `h:mm:ss` from one hour.
- **No `<` or `>`.** YouTube rejects the description. Write "negative k", not "k < 0".
- **At most 5,000 characters.**

**Pinned comment** (`YouTube_Pinned_Comment.txt`). For a revision video, open with the must-watch chapters, picked by their past-paper marks, with their timestamps. Then give the full question list, one line per question with its timestamp. Comment timestamps are clickable and do not affect chapters. Rewrite each raw TeX stem as one short line with Unicode maths: `½mẋ²`, `r₀`, `θ̇`, `≫`, `√`. Collapse a block of rapid-fire questions into one line. A comment holds at most 10,000 characters, so split a long list into numbered replies under the pinned comment (`YouTube_Question_Reply_01.txt`, …).

**Thumbnail** (`Thumbnail.png`). Make it 1280×720 and under 2 MB, in the same board style as the video:
- black background;
- the topic in large warm-white and teal text;
- one key equation in a teal box and one simple diagram;
- a line such as "One-shot revision · 100+ pause-and-try questions";
- the course code.

It must stay readable at phone size. Render it, look at it, and size any box from the measured text so nothing overflows. Render maths with matplotlib's `cm` fontset: STIX leaves a gap after primes.

**Links.** Check that every Drive or web link resolves before handing it over: a share ID read off a screenshot often confuses I, l, O and 0. When the user asks you to check the published video, take a normal look: open it, see that the chapters, description, pinned comment and links show up, and report anything wrong. yt-dlp reads the metadata quickly. Don't audit every timestamp, playback speed or signed-out view unless asked.

## Tell the user

- Turn off **Allow automatic chapters**, so the written list is used.
- Chapters can take a few hours to appear after saving.
- If chapters still don't appear, check Studio → Settings → Channel → Feature eligibility. Phone verification unlocks the intermediate features.
- A new channel may need link verification before description links work, which can take up to 24 hours. Until then, put the links in a comment.
- If the comment can't be pinned, check that comments are turned on for the video. Then pin it from the comment's ⋮ menu while signed in as the channel.
