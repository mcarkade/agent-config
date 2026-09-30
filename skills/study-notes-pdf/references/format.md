# Format and renderer

The reference preserves the refined optics format: A4, serif body, bold question, centered vector maths, brief gray hints, restrained SVG diagrams, two-column linked index, and `Abhinav Pullela . mcarkade` footer with an Index return link and page count. Typography and geometry live in `render.py`; keep them fixed. Reference pages show index, maths notes, a worked solution, a diagram and a formula sheet. Their subject and page count are examples, not defaults.

Each topic or worked problem normally starts a new page. Use the same amount of content and whitespace as the reference; do not force a page count or compress long solutions. Make a learning example's question as complete as a tutorial question. Use typed equations and SVG diagrams; retain an essential source image only when redrawing would lose information. Define dimension arrows, symbols and axes correctly. Priority labels are small text in the existing source line, not badges or extra columns.

## Input

Save a UTF-8 JSON file in the study workspace. Paths to diagrams/images are relative to that file. The minimal form is:

```json
{
  "title": "Subject",
  "subtitle": "Assessment | Notes and worked solutions",
  "exam_line": "Course / date and time, if known",
  "route": "Start: N01, Q01, Q03. Then core questions.",
  "mode": "full",
  "sections": [
    {
      "name": "Notes",
      "units": [
        {
          "id": "N01",
          "title": "Notation",
          "source": "Course notes, p. 2",
          "blocks": [
            {"kind": "p", "text": "Brief explanation."},
            {"kind": "eq", "text": "F(k)=\\int f(x)e^{-ikx}\\,dx"},
            {"kind": "hint", "text": "Define the coordinate and units."}
          ]
        }
      ]
    }
  ]
}
```

Optional unit fields: `index_title` for a shorter index label and `priority` (`Start here`, `Core practice`, `Extension`). Other blocks: `question` and `hint` with `text`; `diagram` or `image` with `path`; `table` with `rows`; `link` with `text` and `url`. Formula-sheet equations may omit explanations already taught. Use supported Matplotlib mathtext; brace font commands and use `\frac`, not `\over`. Break long maths into consecutive equation blocks.

`mode: "cram"` omits the index and starts on the first content page. Full mode keeps the two-column index; if it overflows, shorten index labels or group questions at the topic level before changing layout. Units still have bookmarks. Fit a route in one short line or omit it when irrelevant.

## Commands

From the skill directory, using an available Python runtime with matplotlib, reportlab, svglib, PyMuPDF and Pillow:

```text
python scripts/render.py INPUT.json --output OUTPUT.pdf --work-dir BUILD_DIR
python scripts/check_pdf.py OUTPUT.pdf --manifest BUILD_DIR/layout.json --render-dir REVIEW_DIR
```

The working directory holds equation SVGs and layout data, outside the skill. QA renders every page and checks internal destinations, footer/page labels, bounds, missing text glyphs, and leaked internal commentary. External URLs and visual/math review remain the agent's responsibility.

For fidelity regression, render `assets/reference.json` and compare content pages against `assets/layout-reference.pdf`. The index is configurable for the new subject; its typography and links follow the same renderer. Renderer changes require this comparison and an overflow/link check.
