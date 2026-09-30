---
name: study-notes-pdf
description: Create study PDFs from a syllabus, course material and exam questions, using Abhinav's established notes and worked-solution format. Use for subject revision, question banks or urgent exam notes.
---

# Study notes PDF

Produce a cohesive guide a beginner can learn from and use to solve questions. Preserve the supplied optics layout through `scripts/render.py` and `assets/layout-reference.pdf`; change subject content, not the design. Read [format.md](references/format.md) before authoring.

## Establish scope and sources

Use the user's syllabus, assessment type, deadline and existing sources. Find missing essentials in accessible files, LMS, seniors' academic Drive, Spectrum BPHC resources and assigned textbooks; follow [sources.md](references/sources.md). Ask only for essential missing material or access after checking available routes. Carry forward rules the user already confirmed.

Build a working syllabus-to-source-to-question map. Include prerequisite maths and applications covered in class even when the syllabus names only the parent topic. Keep supplementary topics clearly lower priority. Establish notation, units, signs, coordinate definitions and conventions from the course sources; translate other sources explicitly.

## Curate and solve

Teach the minimum foundations needed for each problem family, including unfamiliar symbols. Give a short explanation and a worked example, then representative practice with complete solutions. Cover every distinct relevant tutorial/PYQ method. Merge repeated prompts and cosmetic variants while retaining source IDs; keep variants that change the method, assumption or trap.

Assign a plain priority: **Start here**, **Core practice** or **Extension**. Base it on syllabus relevance, prerequisites, verified past-paper patterns and time to learn; distinguish observed evidence from judgment. Priorities should help someone starting from zero choose a realistic route, not promise exam predictions. Put the short route in the index and a question's priority in its source line.

State each complete question in bold, with data, requested result and a legible diagram when needed. Check diagram dimensions, connections and labels against the question and solution. Keep the source's method where correct. Show substitutions and successive algebra steps on separate lines, enough to reproduce the answer in an exam. Explain only the non-obvious step or assumption in readable gray. Finish with the result and units or conditions. Derived solutions and verified corrections belong in the source map; resolve ambiguities at the relevant step.

## Assemble

Use this order: clickable index and study route; notation and required maths; learning notes and examples; grouped questions and full solutions; concise sources and optional video route; formula sheets. Use one coherent guide with brief explanations, not a sequence of pasted source pages. Preserve whitespace between questions and the reference density. Long solutions may continue; split oversized equations rather than shrink them.

Keep PDF text about the subject and solving questions. Put acquisition logs, audits, local paths, build details, revisions and agent commentary in working files. Remove repeated definitions, headings that add nothing, generic subtitles, decorative callouts and prose that restates an equation. Preserve necessary steps when shortening.

If useful, select a short video overview with verified URLs and syllabus mapping. Verify claimed segments and examples; label adapted exercises. When the deadline calls for it, add a short companion or chat crib sheet with definitions, recognition cues, formulas and partial-credit setups. If the user will copy without reading, use formula-first text immediately. Follow the confirmed exam rules.

## Verify and deliver

Check every syllabus topic and selected question against its source. Independently verify each solution with suitable derivations, numerical/symbolic checks or an authoritative answer; test dimensions, signs and relevant limits. Reconcile conflicting answers rather than copying a senior's or textbook's key blindly.

Render with the supplied script, then run `scripts/check_pdf.py`. Inspect **every rendered page** at reading size, including diagrams and formula sheets; automated checks do not establish clarity or mathematical correctness. Check all index/bookmark/return destinations and external links. Compare representative pages to the retained layout reference. Fix defects and recheck affected pages and final pagination.

Deliver the exact reopened PDF and a brief account of coverage and unresolved limits. Keep the source map, checks and editable content in the study workspace. Do not ship an answer with an unresolved error as a complete solution.
