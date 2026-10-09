---
name: study-notes-pdf
description: Use when creating or revising syllabus-scoped study PDFs, including teaching notes, exam practice banks, concise references, or standalone cheat sheets.
---

# Study notes PDF

Create a coherent PDF study resource for the verified syllabus and requested scope. Use one integrated PDF for a full physics, POE, or HuEL guide unless the user requests otherwise. Keep the paired learning guide and reference-first LMR workflow for large mathematics subjects when that preference applies. Deliver PDFs, not HTML, and keep editable content, source maps, and review files in a separate working folder.

Follow the user's requested organization. A guide may use topic-ordered notes with inline worked examples, a separate topic-organized tutorial/PYQ/suggested question bank after the teaching, and concise short notes at the end. Do not move every chapter's practice next to its notes when the requested structure places one bank after all teaching. Teach and solve each task once; link back to a matching worked example instead of repeating its solution.

Use the warm dark study layout for a main guide. That preference applies only to study notes. A standalone cheat sheet is a separate mode, created only when requested; use a spacious JEE-style single-column layout on clean white pages with minimal black styling. Show the document title on page one only, omit running headers, footers, and page numbers, keep formula-group labels with their content, and do not add the sheet automatically to a guide. Include selected in-syllabus results and reusable methods, with only useful visuals or boxes. See [format.md](references/format.md) for layout details.

## Verify scope and sources

Verify the current course, campus, year, assessment cutoff, syllabus, and exam rules from official evidence. Reconcile old course codes, textbook editions, and conflicting handout headers. Verify exam permissions separately from study usefulness; follow [sources.md](references/sources.md). Start with existing local material, then fill essential gaps using supported accessible sources. Preserve confirmed decisions and original files.

Maintain a working map from every in-scope syllabus topic and distinct source method to the teaching, reference, or solved task that covers it. Record exact source locators, review status, source IDs, verified corrections, merged variants, and unresolved gaps. An inventory or announcement is not evidence that every source was read. Keep source gaps and uncertainty explicit.

Adapt teaching, reference density, and question style to the subject, learner, and verified assessment format. Spend explanation on unfamiliar mathematical prerequisites and tricky integrals; keep familiar physics at its verified exam level. Calibrate by topic instead of making every section equally elementary. Do not assume MCQs without current evidence or change a course's difficulty without user direction.

## Teach and solve

Define unfamiliar concepts, prerequisites, and notation before use. State the key result, give one or two concise lines about its meaning or method, then show a worked example. Explain enough for a learner to use foundational ideas and follow non-obvious transitions; cut lecture paraphrase, repeated narration, and filler rather than necessary reasoning. Connect diagram labels and relationships to the equations they explain. Inspect each scientific SVG and its final PDF appearance at reading size; check for clipped or overlapping text and verify its geometry, axes, arrows, and labels against the surrounding explanation.

Give each example and bank question a complete stem, data, conditions, subparts, and a clearly marked solution. Preserve source methods and provenance. Show the algebra needed to reproduce an exam answer, using readable successive lines. For integral solutions, show the setup, the antiderivative with limits, and substituted arithmetic separately. State final units and domain or validity conditions. Verify signs, limits, assumptions, and boundary cases independently; do not trust inherited answer keys without checking them.

Use fitted boxes for key definitions, laws, standard results, and important answers; keep routine algebra and prose open. When the user requests panels, group each notes example's question and solution together and each practice solution together. Use the bundled `panel` field when a panel continues across pages and `box` for a one-page rectangle. See [format.md](references/format.md) for border and footer rules.

## Assemble, check, and deliver

Use a clickable index for a substantial guide. Group it by requested part and chapter, use short topic titles, and place a compact source tag beside each practice question. Use ruled section headings. Avoid priority or prediction labels, selection rationale, motivation copy, and decorative hints. Keep source/scope notes concise and leave acquisition logs, audit history, private access details, and local paths in working files. Omit reading-time estimates and extra metadata by default; add rough reading estimates only when requested or useful.

Independently review source coverage, mathematics, diagrams, links, and final rendering. Run the bundled renderer and `scripts/check_pdf.py` when using them. Inspect every changed page at reading size; for unchanged pages, reuse earlier evidence only after exact comparison. Read the learning flow as a cold reader and check that terms are defined, the method choice is clear, each step can be reproduced, and diagrams carry meaning. Rendering and automated checks do not establish comprehension or source coverage.

Reopen the delivered PDF and confirm it is the checked artifact. Report coverage and unresolved source limits honestly. Keep original sources and backups. A course's `Study_Ready` folder contains finished guides only; that convention does not authorize deleting existing files or changing another worker's output. Historical papers show past methods, not exact predictions or guaranteed marks.
