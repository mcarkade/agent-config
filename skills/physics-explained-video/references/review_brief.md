# Narration review brief

You are checking the spoken narration of a study video. The course topic and the study guide path are given in your task. The video is a black board where equations build up step by step, in the style of the Physics Explained YouTube channel. A text-to-speech voice reads the narration (Microsoft Edge "en-US-AndrewNeural" at double speed), and the words are also burned in as subtitles.

The narration was written in a conversational lecturer style following the skill's `narration.md`. Your job is to **check** it, not to rewrite it.

## Files (in `narr/`)

- `chNN.txt`: the extracted narration (`python tools/narr.py extract chNN`). Each beat is numbered (`NNN| text`), followed by a `[screen]` line listing what appears on screen during that beat (LaTeX equations, notes, questions). The screen content is unchanged and is the source of truth for what the viewer sees.
- `chNN.new` (if present): proposed narration, one line per beat with the same numbers. Without it, check the text in `chNN.txt` itself.

## What to check, beat by beat

1. **Physics and maths are right.** The spoken statement must be correct and must agree with the equation on screen for that beat (signs, factors, powers, which variable). Flag anything wrong or misleading. Flag a beat that says something the screen contradicts.
2. **The narration matches the screen at that beat.** If a new line describes something that appears in a different beat, or skips information the viewer needs to read the screen (for example a symbol that is defined only on screen and never explained), flag it.
3. **Text-to-speech traps.** Flag anything the voice will read badly: symbols or digits that should be words, units written as abbreviations, "capital X" when only one case of the letter is in use, "inverse" used for a reciprocal, "SI", "e.g.", Greek letters spelled oddly, ambiguous words such as "minute" or "read", and any word the voice could stress wrongly in a way that changes the meaning.
4. **Clarity and tone.** Flag lines that are still robotic, choppy or half-sentence, that use AI-style filler ("Let's dive", "crucial", "key insight", "it's worth noting"), or that would confuse a student hearing them once at double speed. Do not flag the lecturer connectors ("Okay, so", "Now", "And so", "In other words", "Well,"); they are intended.

Do not suggest stylistic changes to lines that are already correct and clear. Keep the number of changes small and worth making.

## Output

For each chapter you check, write `narr/review_chNN.txt` containing ONLY replacement lines in exactly this format, one per line:

```
NNN| full replacement text for that beat
```

followed by a line `# reason: ...` directly below each replacement, giving the reason in a few words. Write an empty file (or a file with the single line `# no changes`) if nothing needs changing. Replacement text must be plain spoken English: no LaTeX, no symbols, numbers written as words, and roughly the same length as the line it replaces. Do not edit any other file. Do not edit `chNN.new` or the chapter scripts.

When you finish, reply with a short summary per chapter: the number of replacements, and any physics error you found, quoted.
