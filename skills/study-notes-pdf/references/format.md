# Format and renderer

The bundled renderer produces A4 pages in a warm dark palette, with serif body text, bold questions, centered vector mathematics, readable diagrams, and a linked two-column index in full mode. Use readable spacing and let coverage determine page count. Keep this palette scoped to study notes; respect an explicit request for another style.

## Output modes

A main subject guide defaults to the warm dark style. When it includes short notes, keep them in that style and make them a compact scan reference: group important in-scope results that recur across the guide and reusable methods by topic; give each line breathing room, brief conditions or symbol notes, and minimal boxes. Keep the selection useful rather than exhaustive, with no long caption prose.

Create a standalone cheat sheet only when requested. Use a spacious JEE-style flow on clean white pages, with minimal black styling and one readable column. Show its title on page one only; omit running headers, footers, branding, and page numbers while keeping formula-group labels with their content. Organize by topic. For each selected result, name its symbols in one short line directly under the formula, define unfamiliar objects, and state theorem conditions; give the integration region and boundary terms when relevant. A reusable worked case shows its setup, decisive intermediate calculation, and answer, with a short bridge for any non-obvious method. Cut filler, not steps needed to understand or use the result. Include recurring results and distinctive cases that reveal a non-obvious mechanism, plus simple high-contrast diagrams for geometry-driven cases. Keep the selection broad but deliberate, not an exhaustive formula dump. Keep equations readable at page size; split oversized displays and add pages rather than shrinking equations or tightening spacing. Do not add this PDF automatically to a main guide. The bundled renderer defaults to warm dark and supports white mode with the top-level theme set to `white_minimal`; use `cram` to omit the index in a standalone sheet.

## Index and page flow

Use a clickable index for a substantial guide. Group entries by the requested part and chapter, use short topic titles, and keep each practice question's source tag beside its index entry and stem. Use clear ruled part headings. Avoid priority or prediction labels, selection rationale, motivation copy, and decorative hints. Internal destinations land at page top. Keep links visibly distinct and easy to follow.

Use fresh pages for complete teaching units and numbered practice questions where this improves navigation. Let subtopics and examples flow within a unit. Keep an example's stem, solution label, and opening working together; avoid orphaned headings and navigation-only pages. When a solution continues onto another page, let its working flow without repeated headings or banners. Keep the page footer outside content panels.

## Teaching and boxes


For the requested panel style, group a notes worked example's question and solution in one panel, and group each practice solution in one panel. Box key definitions, laws, standard results, and important answers in the notes. Leave routine algebra and prose open. Keep short notes lightly boxed. Adjacent blocks with the same `panel` ID form one panel; its side rules continue across page breaks and close at the true start and end. Keep its footer outside, with no repeated panel headings. The `box` field remains a fitted one-page rectangle.

Follow each key formula with one `hint` block naming its symbols, and set `keep_next: true` on the formula so the two stay on one page. Keep short notes in the same pattern: a labelled formula, its symbol line, selective boxes, and no prose blocks.

Typeset mathematics in stems as carefully as in solutions. Use native math for fractions, functions, derivatives, exponents, subscripts, conditions, and subquestion expressions. Verify coefficients, signs, and conditions after conversion. Put separate algebra steps on separate lines; use implication symbols only when the logic supports them.

Omit time estimates and timing metadata by default. Include rough reading estimates only when requested or useful, show them once per unit and as a consistent total, and never imply time to mastery or exam readiness.

## Input

Use UTF-8 JSON in the workspace; media paths are relative to it:

~~~json
{
  "title": "Study guide",
  "subtitle": "Assessment | Notes and worked solutions",
  "exam_line": "Verified course, assessment date and rules",
  "route": "Read the notes, then work through the question bank.",
  "sections": [
    {"name": "Notes", "units": [
      {"id": "N1", "title": "Required method", "role": "notes",
       "source": "Verified course source and page",
       "blocks": [
         {"kind": "p", "text": "A concise explanation of when the method applies."},
         {"kind": "example_label", "text": "Worked example", "panel": "N1-example"},
         {"kind": "question", "text": "Evaluate the integral.", "panel": "N1-example"},
         {"kind": "eq", "text": "\\int e^x\\,dx", "panel": "N1-example"},
         {"kind": "solution_label", "text": "Solution", "panel": "N1-example"},
         {"kind": "secondary", "text": "Differentiation verifies the antiderivative.", "panel": "N1-example"},
         {"kind": "eq", "text": "\\int e^x\\,dx=e^x+C", "panel": "N1-example"},
         {"kind": "eq", "text": "\\frac{d}{dx}e^x=e^x", "box": true}
       ]},
      {"id": "R1", "title": "Short notes", "role": "reference",
       "source": "Key results and conditions",
       "blocks": [
         {"kind": "eq", "text": "\\int e^x\\,dx=e^x+C"},
         {"kind": "eq", "text": "\\frac{d}{dx}e^x=e^x"}
       ]}
    ]},
    {"name": "Practice", "units": [
      {"id": "1", "title": "Complete source task", "role": "question",
       "index_title": "Complete source task",
       "index_tag": "Tutorial",
       "source": "Tutorial question identifier",
       "blocks": [
         {"kind": "question", "text": "Solve y'=y with y(0)=1."},
         {"kind": "solution_label", "text": "Solution"},
         {"kind": "eq", "text": "y=Ae^x"},
         {"kind": "eq", "text": "y(0)=A=1"},
         {"kind": "eq", "text": "\\Longrightarrow y=e^x", "box": true}
       ]}
    ]}
  ]
}
~~~

Top-level fields may include `mode` (`full` by default or `cram` to omit the index) and `theme` (`warm_dark` by default or `white_minimal`). Use `white_minimal` with `cram` for a requested standalone cheat sheet; that combination prints the title once and suppresses recurring page furniture. Unit fields: unique `id`, `title`, `source`, and nonempty `blocks`; optional `index_title`, `index_tag`, `role` (`notes`, `question`, `formula`, or `reference`), and `estimated_minutes`. Every full module or question unit starts on a fresh page. Use role `reference` for short notes and explicitly mark selected results with `box: true`. Role `formula` boxes every equation by default. If supplied, `estimated_minutes` must be nonnegative and the top-level total must equal the unit sum.

Block kinds: `p`, `secondary`, `question`, `hint`, `example_label`, `solution_label`, `eq`, `link`, `diagram`, `image`, `table`, and `spacer`. Prose uses `text`; `bold: true` supports an unboxed conclusion. `math_segments` interleaves literal text and math. `box: true` makes a fitted one-page box; adjacent blocks with the same string value share that box. `panel` marks side rules that continue across pages; use the same identifier on adjacent blocks in the group. `keep_next: true` joins related steps. Media uses `path`; tables use `rows`; links use `text` and `url`. Optional `source_id` records provenance in the working map.

Use supported Matplotlib mathtext with braced fraction and font arguments. Split oversized displays instead of shrinking them. A shared `box` group must fit one page; use `panel` for a panel that needs to continue onto another page. The `formula` role boxes every equation, so use `reference` when short notes need selective boxes.

## Commands and checks

Use Python with matplotlib, reportlab, svglib, PyMuPDF, and Pillow:

~~~text
python scripts/render.py INPUT.json --output OUTPUT.pdf --work-dir BUILD_DIR
python scripts/check_pdf.py OUTPUT.pdf --manifest BUILD_DIR/layout.json --render-dir REVIEW_DIR
~~~

Generated SVGs, manifests, and page renders belong in the workspace. Check page-top destinations, links, estimates if present, boxes, opening groups, and panel edges at page breaks. Automated checks complement source and math verification and page-by-page visual review. Reuse earlier visual evidence only for exact unchanged pages; inspect each changed page. Reopen the delivered copy and confirm it matches the checked artifact. A cold reader must understand definitions, transitions, and method choice and reproduce the working. Audit syllabus coverage and disclose source gaps. Keep sources, archives, and backups. Keep working files separate, reuse stable review paths, bound logs and renders, and check disk headroom during long runs. Do not clean another worker's artifacts or rewrite their guide outputs.
