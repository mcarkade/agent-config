---
name: study-notes-pdf
description: "Create syllabus-scoped study PDFs with clear teaching, contextual references and complete exam-ready solutions: paired for large physics/math subjects, integrated for POE and HuELs."
---

# Study notes PDF

Choose the output workflow from the start. For large physics/math subjects, plan a full learning guide plus a separate cheatsheet-first last-minute revision (LMR)/question-bank PDF. For POE and HuELs, including HRD and TWS, deliver one cohesive integrated PDF with clear learning, a contextual quick reference and question-oriented practice without duplicating content. Use an integrated PDF for other subjects unless the user specifies otherwise; do not apply the dual workflow universally. Deliver PDFs only, never HTML. The learning material teaches a first reading; a separate LMR opens with a contextual reference, then exam-shaped questions and complete solutions. Default to the warm dark layout in scripts/render.py. The well-received optics quiz guide is the retained reference for teaching clarity, typography, spacing and diagram geometry, not a universal exam format or difficulty level. Read [format.md](references/format.md) before authoring. Honor the requested stage: source verification, a sample, or the full subject-appropriate output.

## Establish scope and evidence

Verify the current course, campus, year, assessment cutoff and exam rules from official evidence. Reconcile old codes, editions and conflicting handout headers. Start with existing local material, then fill essential gaps through supported accessible sources; follow [sources.md](references/sources.md). Preserve confirmed decisions and original files.

Keep a working syllabus-to-source-to-question map for the selected output set with exact locators, reviewed ranges and unresolved gaps. Audit every in-scope syllabus topic, including prerequisites and applications, against teaching, reference and solved-task coverage. Distinguish exact worked tasks, merged variants, verified corrections and unavailable or uncertain sources. Report source gaps honestly; an inventory or announcement list does not prove every document was read.

Adapt teaching, reference density and question style to the subject, verified assessment format, scope and open-book permissions. Do not assume MCQs without verified PYQs or current official format evidence. Follow sources.md for permission distinctions. Feedback that M3 was too hard applies to M3; do not lower physics difficulty globally. Preserve verified course difficulty while making its reasoning learnable.

## Teach, curate and solve

In the learning material, define symbols, units, assumptions and required maths before using them. Teach what each concept or method means, why the next step follows, and how to recognize and use it. Connect mini worked examples to the theory so a cold reader can follow the first reading without another explanation. Use clear, accurate SVG diagrams where they help explain relationships. Keep necessary reasoning; remove redundant prose.

Make the quick reference contextual: formulas and results alongside symbol meanings, validity conditions, conventions and method-selection cues. Include a brief application or mini example where needed to make a result usable. Avoid unexplained formula compression. A separate physics/math LMR starts with this reference, followed by the curated question bank and complete solutions. In an integrated POE/HuEL PDF, connect learning, reference and practice with internal links; teach and solve each item once rather than duplicating sections.

Order the bank by topic and prerequisites, with the highest-value exam-shaped tasks first within each topic. Reflect actual tutorial, practice and verified PYQ patterns in stems, subparts and expected working; cover distinct relevant methods from those sources, assignments and selected textbook cases. Merge cosmetic repeats while preserving source IDs; retain changes in method, assumptions or traps. Let coverage determine length: no arbitrary page or question quota. Do not add prediction labels, selection rationale, priority badges, motivation or a hint system.

Make learning examples and bank questions complete: data, conditions and requested result, followed immediately by the solution. Typeset maths in stems and subquestions as carefully as in solutions. Mark **Worked example**, the question and **Solution** distinctly. Show substitutions and algebra on successive lines without skipping steps needed to reproduce the answer in an exam. Use implication, equality, equivalence, because or therefore only when logically correct. Add only the necessary brief plain-English explanation beside difficult transitions; do not restate obvious equations. Do not skip steps to save space, and remove redundant bloat without removing reasoning.

Finish with the result, units and domain or parameter conditions. Box key mathematical results individually to fit their contents. A sentence proof conclusion may be bold and unboxed. Use accurate SVG diagrams when geometry or relationships help; preserve essential source images when redrawing loses information.

## Assemble and verify

Give each PDF a clickable index. For the dual physics/math workflow, order the full guide as foundations and teaching modules with mini worked examples, and the separate LMR as contextual cheatsheet/reference followed by a continuously numbered selective question bank with complete solutions. For the integrated workflow, connect learning modules, contextual quick reference and question-oriented practice in one cohesive PDF without repeated content. Include concise source/scope references and provenance in the working map. Keep acquisition logs, audits, local paths and build history in working files. Videos are optional targeted backup for a specific unclear step.

Apply format.md: subtly underlined amber links, page-top destinations, fresh pages for full teaching modules and every full numbered question, smart within-module opening/solution grouping, no repeated continuation headings, and approximate module/question times plus a consistent total.

Independently verify solutions using suitable derivations, symbolic/numerical checks or authoritative answers. Check signs, units, assumptions and limits; resolve conflicting keys. Run the renderer and scripts/check_pdf.py, then inspect every page at reading size, including native stem maths, diagrams, fitted boxes and breaks. For a revision, credit unchanged page bodies only by exact comparison with already reviewed pages; inspect every changed page and recheck final navigation. Rendering alone is not comprehension QA: read the theory and representative solutions as a cold reader, checking definitions, transitions, method choice and whether each step can be reproduced without outside explanation. Repair gaps before delivery and complete the full syllabus coverage audit for the selected output set.

Deliver the exact reopened and checked subject-appropriate PDF output set with concise coverage and unresolved limits. Keep editable content, source/proof maps and checks in separate working files. When preparing the course's Study_Ready folder, put only the current official handout and the final PDF(s) for the selected workflow there; preserve source folders, archives and backups. Reuse each intended Library item/version when an update is requested. Label historical paper evidence as historical; never claim an exact predicted paper, exhaustive coverage of possible exam tasks or guaranteed marks.
