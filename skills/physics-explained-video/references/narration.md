# Narration

The narration is what makes the viewer stay. Correct maths read in stiff, captioned fragments, or symbols read aloud literally, sounds robotic and uncanny, and the viewer stops watching.

## Learn the voice from the source

Fetch transcripts of real Physics Explained videos with `python tools/fetch_transcripts.py 15`. This downloads text only. Read several before writing, and read some again when your lines start to drift. Things to notice:

- **Full sentences that flow, with spoken connectors.** "Okay, so now imagine that…", "Now, of course…", "And so…", "In other words…", "So how do we do that? Well, the first thing to say is…"
- **He narrates the board as it changes.** "We can then cancel off the factors of two, and we arrive at the following expression." He does not read every symbol of a long equation; he gives its shape and lets the screen carry the rest.
- **He asks, then answers.** "But can we quantify how much the times differ? To answer this, let's build a light clock."
- **He says why before what,** and names the payoff after it: "And this is the whole reason we…"
- **He uses "we" and "you",** and "I" now and then.

Learn the habits, not a list of phrases. If every line opens with "Okay, so", it is a new tic, not his voice.

## Write for the ear

A neural TTS voice reads every character literally, at double speed, and the same text appears as a subtitle. Write each line as you would say it to a student sitting next to you.

- **Say maths as a person would.** Write "one over r squared", not "r to the minus two" or "inverse radius squared". Write "a quarter per metre", not "metre inverse". Write "d V by d r", "theta dot", "root two times v". Write numbers as words.
- **Make grouping audible.** When a minus sign or a power covers a whole group, say so: "minus the whole quantity T minus U", "one plus e, all squared".
- **Say "capital" only when both cases of a letter are on screen.** Otherwise use the quantity's name: "the total mass M".
- **Write function names in full.** Use "cosine", "sine" and "tangent"; the voice may read "cos" as "'cause".
- **Long equations get their structure, not every symbol.** Say "so H is the kinetic term plus the potential" and let the board show it.
- **Watch words with two pronunciations,** such as "read", "minute", "lead" and "wind". Rephrase if the stress could flip the meaning.

Precision still matters. Say "partial" when the equation has a partial derivative and the difference matters.

## Shape of a beat

Each beat says what is appearing as it appears, in one or two complete sentences of roughly 8 to 35 words. Pose questions the way a person would ("Here's one to try. Pause the video and give it a go."), and start the answer the way you would say it out loud.

When an equation grows term by term over several beats, each beat is still a complete sentence. The voice synthesises every beat on its own, so a sentence split across beats sounds broken.

Two examples of fixing captions into speech:

| Caption-style (rejected) | Spoken |
|---|---|
| "Angular speed varies as inverse radius squared; sideways speed varies as inverse radius." | "Theta dot goes as one over r squared, but the sideways speed only goes as one over r." |
| "Keep the subtraction visible. Losing that second minus would make the spring push away from equilibrium." | "A really common mistake is to drop one of those minus signs. Then the spring would push the mass away from equilibrium, which makes no sense." |

Then apply the unslop skill. It removes AI vocabulary, announcing lines ("here's the key insight"), stiff definitions and fragments.

## Review checklist

The reviewer gets each beat's narration next to what is on screen (`tools/narr.py extract`). For every beat, the reviewer checks four things:
1. **Physics.** The spoken statement is correct and agrees with the equation on screen: signs, factors, powers and which variable.
2. **Sync.** The line describes what appears in that beat, and every symbol the viewer needs is explained.
3. **Speech.** Nothing would be read badly: symbols, digits, abbreviations, a needless "capital", a silent bracket, or an ambiguous word.
4. **Tone.** The line is not robotic, choppy or filler, and it is clear when heard once at double speed. The lecturer connectors are intended; leave them.

The reviewer should suggest replacement lines only where something is wrong, with a short reason for each, and leave correct lines alone. Reviewers sometimes bring back stiff wording such as "capital R". When that happens, keep their correction and say it naturally.
