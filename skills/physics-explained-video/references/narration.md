# Writing the narration

The narration decides whether the video works. The first CM Quiz 2 video had correct maths and clean visuals, but the student stopped after two minutes. They called it "AI slop half sentences, robotic, not human", and said the voice reading maths was "uncanny". This file records what fixed it.

Write the narration yourself, as the lead agent, one chapter at a time, while you can see the screen ops. A subagent may check it afterwards (see `review_brief.md`), but don't hand off the writing: delegated authors produced the stilted version.

## How Physics Explained actually talks

This comes from the transcripts of 14 Physics Explained videos. To refresh it, run `python tools/fetch_transcripts.py 14`; it saves text only to `pe_transcripts/`. Delete the folder afterwards.

**Full, flowing sentences with spoken connectors.** "Okay, so now imagine that…", "Now, of course…", "And so…", "In other words…", "So, how do we do that? Well, the first thing to say is…", "And this is the whole reason we…".

**He narrates the board as it changes.** "If we plug in the numbers from our plot, then we see a value of 2 m/s²", "We can then cancel off the factors of two", "and we arrive at the following expression". He doesn't read every symbol of a long equation. He says "we get this" and lets the screen carry it.

**He asks, then answers.** "But can we quantify how the time measured by different observers actually differs? To answer this question, let's build a light clock."

**He says why before what.** "Now, the reason for the roughly equal sign is because this is no longer an exact statement."

**He says maths the way a person would.** "d u by d t multiplied by delta t", "C delta T divided by two, all squared", "0.5 metres per second per metre", "delta t prime equals 2L over C".

## Rules

### Sentences
- One idea per sentence, but complete sentences. No telegraphic fragments such as "Partial derivative first. Time derivative second." or "Bold r one and bold r two are position vectors, arrows from an inertial frame's origin."
- Begin beats with connectors: "Okay, so", "Now", "And so", "So", "Well,", "But", "In other words". This is what makes it sound like a lecture rather than captions.
- Use "we" and "you". Use "I" sparingly ("I'll set m, k and l to one").
- Name the payoff: "And this cancellation is exactly why gravity is so easy to solve." Don't announce it ("Here's the key insight").
- Pose questions like a person: "Here's a question. … Pause the video and give it a go." Then answer starting with "Well," or "Okay, so".
- Don't define the obvious. One clause per new symbol, the first time it matters.
- No AI vocabulary: crucial, key insight, delve, robust, it's worth noting, let's dive in, in this video, fascinating.

### Spoken maths: what the TTS voice will say
Write every symbol as words. The voice (Edge `en-US-AndrewNeural`) reads the text literally.

| Write | Never write |
|---|---|
| "one over r squared" | "inverse radius squared", "r to the minus two" |
| "per metre", "a quarter per metre" | "inverse metres", "metre inverse", "m⁻¹" |
| "m over two" | "m divided by two" (fine but slower) |
| "the total mass, M" | "capital M" |
| "theta dot", "r double dot" | "θ̇", "the time derivative of theta" every time |
| "d V by d r" | "dV/dr" |
| "the derivative of L with respect to q dot" | "partial L partial q dot" |
| "root two times the circular speed" | "sqrt 2 v_c" |
| "about two hundred and fifty five degrees" | "254.6°" |
| "twelve, in SI units" or the spoken unit | "12 kg m^2/s" |

- **Capital letters.** Don't say "capital" unless both cases of the same letter appear in that beat and the sentence would be ambiguous. Use the quantity's name instead ("the total mass M", "the centre of mass R"). The listener can also see the subtitles and the board.
- **Long equations.** Say the structure ("and so H has two kinetic terms and the potential") and let the screen show the rest. Reading thirty symbols aloud is the "uncanny" effect.
- **Primes.** "u prime", "u double prime". Say what the prime means once per chapter.
- **Greek letters.** Write the plain names: mu, theta, phi, omega, beta, alpha, lambda, epsilon.
- **Numbers.** Write them as words in the narration ("eighty one over eighty two"). The screen shows the digits.
- **Watch for spelling-based misreads:** "read", "minute", "lead", "wind", and "polar" vs "pole". Rephrase if one could be stressed wrongly.

### Rhythm for an ADHD viewer at double speed
- Something new appears on screen in every beat. The narration says it as it appears.
- Keep each beat between 8 and 35 words. Split long beats rather than cramming.
- Vary the sentence length: a short line after a long derivation step ("So the period only depends on the size.").
- End each section with a hook into the next ("And the next question is, what stays constant as it moves?").

## Before and after (from the CM Quiz 2 video)

| First version (rejected) | Rewrite |
|---|---|
| "Let's name the quantities before calculating. A generalized coordinate, called q, is an independent number describing the configuration of a system." | "Before we answer that, we need a few tools. The first is a generalized coordinate, q. It's just a number that tells you where the system is." |
| "Angular speed varies as inverse radius squared; sideways speed varies as inverse radius." | "Theta dot goes as one over r squared, but the sideways speed goes as one over r." |
| "For example, a semi-major axis of four metres gives average inverse radius one quarter per metre." | "So for example, if a is four metres, the average of one over r is a quarter per metre." |
| "Capital M R becomes capital M r one plus m two times the relative vector." | "If we substitute that into the centre of mass equation, we get M R equals M r one plus m two r." |
| "Keep the subtraction in the recipe visible. Losing that second minus would incorrectly make the spring push away from equilibrium." | "A really common mistake here is to drop one of those minus signs. If you did that, the spring would push the mass away from equilibrium, which makes no sense." |

## Workflow for rewriting narration only

`tools/narr.py` keeps the visuals fixed and swaps only the spoken text:

```
python tools/narr.py extract ch03     # narr/ch03.txt: "NNN| text" + the [screen] ops of each beat
# write narr/ch03.new: "NNN| new text" for each beat you change
python tools/narr.py apply ch03       # replaces the say() strings in chapters/ch03.py in place
python make.py ch03 --check
```

Back up `chapters/` before the first `apply`. Speech is cached per sentence, so only changed lines are re-synthesised.
