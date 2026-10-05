# Format and renderer

Default to A4 with the retained optics typography and geometry: serif body, bold questions, centered native vector maths, restrained SVG diagrams, two-column linked index and Abhinav Pullela . mcarkade footer. The historical assets/layout-reference.pdf is a spacing/typography example; its light palette, subject and page count are not current defaults.

Use warm dark colors: background #211D19, normal maths/body #F2E8DB, headings #FFF2DF, readable secondary explanation #C8B6A1, muted source/time/footer #B8A48D, links #DDB079, and box strokes #B88959. Subtly underline every clickable label with a 0.35-point line, including index IDs/topics/page numbers and footer return. Internal destinations explicitly land at page top. Respect an explicit request for another theme.

## Content and flow

Plan the subject-appropriate PDF workflow from the outset, using the same layout with subject-specific pedagogy. Large physics/math subjects use two inputs and outputs: a full learning guide with notation/prerequisite teaching and mini worked examples, and a separate cheatsheet-first last-minute revision (LMR)/question-bank PDF. POE and HuELs, including HRD and TWS, use one cohesive integrated PDF combining clear learning, contextual quick reference and question-oriented practice; teach and solve each item once, linking related content instead of duplicating it. Use the integrated workflow for other subjects unless the user specifies otherwise. Do not deliver HTML. Reference entries include symbol meanings, assumptions, validity conditions and method-selection cues, with brief applications where necessary; they are not an unexplained formula list. Explain recognition and connective reasoning without verbosity. Use continuous numbering, complete stems and immediate full solutions. Distinguish a learning Worked example, its bold question and Solution. No prediction/priority labels, callouts, hint system, selection rationale or motivation clutter. The hint block is a brief necessary explanation style, never a displayed hint label.

Typeset fractions, functions, derivatives, exponents, subscripts, conditions and subquestion expressions natively in statements as well as solutions. Use math_segments for maths embedded in prose. Verify coefficients, signs and conditions after conversion. Put logical algebra steps on separate lines; do not prefix arrows automatically or equate a requirement with a deduction.

Fit individual boxes to key answers/statements and formula-reference equations. Leave intermediate algebra unboxed. Group lines only when they form one mathematical result; separate independent answers. Sentence proof conclusions may be bold and unboxed.

Keep the stem, its data, Solution label and initial meaningful working together when they fit. Keep headings and short formula introductions with their content, including boxed introductions. Reserve an opening once: later lookahead must not split that group. Clamp a generic heading's group before the next worked example. Every full teaching section/module and every full numbered bank question starts on a fresh page. Subparts, individual steps and inline worked examples flow within their module or question; do not force each onto a new page. Long solutions continue without repeated module/source/continuation headings. Preserve necessary algebra and legible type; impose no page/question quota.

Show approximate time once per learning module or bank question and a consistent total at the index. Estimate reading/following the guide, not mastery or an exam guarantee. Do not time individual steps/subquestions or repeat estimates on continuation pages. Reference units may omit times.

Use accurate SVG diagrams when geometry or relationships help. Match labels, axes, connections, dimensions and signs to stem and answer. Supply readable dark-theme artwork; preserve essential source images. Keep acquisition and engineering logs outside the guide.

## Input

Use UTF-8 JSON in the workspace; media paths are relative to it:

~~~json
{
  "title": "Study guide",
  "subtitle": "Assessment | Notes and worked solutions",
  "exam_line": "Verified course, assessment date and rules",
  "route": "Read learning modules, then work through the bank.",
  "sections": [
    {"name": "Learning notes", "units": [
      {"id": "N1", "title": "Required method", "role": "notes",
       "source": "Verified course source and page", "estimated_minutes": 8,
       "blocks": [
         {"kind": "p", "text": "A concise recognition explanation."},
         {"kind": "example_label", "text": "Worked example"},
         {"kind": "question", "text": "Evaluate the integral."},
         {"kind": "eq", "text": "\\int e^x\\,dx"},
         {"kind": "solution_label", "text": "Solution"},
         {"kind": "secondary", "text": "Differentiation verifies the antiderivative."},
         {"kind": "eq", "text": "\\int e^x\\,dx=e^x+C", "box": true}
       ]}
    ]},
    {"name": "Question bank", "units": [
      {"id": "1", "title": "Complete source task", "role": "question",
       "source": "Source question identifier", "estimated_minutes": 5,
       "blocks": [
         {"kind": "question", "text": "Solve y'=y with y(0)=1.",
          "math_segments": [{"text": "Solve "}, {"math": "y'=y"},
                            {"text": " with "}, {"math": "y(0)=1"}, {"text": "."}]},
         {"kind": "solution_label", "text": "Solution"},
         {"kind": "eq", "text": "y=Ae^x"},
         {"kind": "eq", "text": "y(0)=A=1"},
         {"kind": "eq", "text": "\\Longrightarrow y=e^x", "box": true}
       ]}
    ]}
  ]
}
~~~

Unit fields: unique id, title, source and nonempty blocks; optional index_title, role (notes/question/formula/reference), estimated_minutes. Every full module/question unit starts a new page. Formula units box equations by default. A supplied top-level estimated_minutes must equal the unit sum; otherwise the total is derived.

Block kinds: p, secondary, question, hint, example_label, solution_label, eq, link, diagram, image, table and spacer. Prose uses text; bold:true supports an unboxed conclusion. math_segments interleaves literal text and mathtext math. box:true makes one fitted box; a shared string groups adjacent parts of one result. keep_next:true joins related steps. Media uses path; tables use rows; links use text and url. Optional source_id records provenance in the working manifest.

Use supported Matplotlib mathtext with braced fraction/font arguments. Split oversized displays instead of shrinking them. For the dual physics/math workflow, render each input separately with its own build/review directory. For POE/HuELs, render the single integrated input. Keep a consistent unit-time total and default full-mode index in each PDF; cram omits it only when requested. If the index overflows, use concise topic entries or extend its pagination; keep necessary content.

## Commands and checks

Use Python with matplotlib, reportlab, svglib, PyMuPDF and Pillow:

~~~text
python scripts/render.py INPUT.json --output OUTPUT.pdf --work-dir BUILD_DIR
python scripts/check_pdf.py OUTPUT.pdf --manifest BUILD_DIR/layout.json --render-dir REVIEW_DIR
~~~

Generated SVGs, manifests and page renders belong in the workspace. Check page-top destinations, links/underlines, estimates, boxes and opening groups. Automated checks complement source/maths verification and page-by-page visual review. Exact unchanged-page comparison may reuse earlier visual evidence; inspect every changed page. Reopen the delivered copy and verify it matches the checked artifact. Visual rendering checks do not establish comprehension: a cold reader must understand definitions, transitions and method choice, and reproduce the working. Audit full syllabus coverage and disclose source gaps for the selected output set. The course's Study_Ready folder contains only the official current handout and the final PDF(s) for the selected workflow; preserve sources, archives and backups. Keep working files separate, reuse stable build/review paths, bound logs and page renders, and recheck disk headroom during long runs. Do not clean another worker's artifacts or rewrite their guide outputs.
