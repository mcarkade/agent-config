---
name: illustrated-build-guides
description: Create or revise illustrated PDF build guides for physical projects, especially assembly, wiring, calibration and fault finding. Use when a reader must build from the guide without the working notes.
---

# Illustrated build guides

Make the guide usable at a workbench by someone who did not join the design discussion. The PDF must stand alone. Keep research history and unresolved design debate in the working record.

## Establish the build

1. Read the current design decisions, final CAD and part exports, electrical plan, BOM, and any existing guide. Settle routine engineering and presentation choices from evidence; ask only when a missing fact, material design decision or authorization requires the user. Keep part IDs, names, quantities, colors, ratings, connectors and wire labels identical across the BOM, views, steps and diagrams. Record and verify design changes in the authoritative source rather than silently introducing them in illustrations.
2. Make an assembly map before laying out pages: each part's ID, print/make/buy source and orientation, how it is retained, the order that keeps fasteners and connectors accessible, each electrical connection, and the checks before power or motion. Mark measured facts, calculated values, planned work and physical checks distinctly.

## Show what the builder must see

- Open with a clickable contents page and PDF bookmarks. Show what the finished object does, its dimensions and major assemblies, then let the reader reach the exact step or fault path quickly. Add return links when a long guide benefits from them.
- Use a restrained editorial layout with generous whitespace, fine rules and clear hierarchy on narrative pages. Give tables full plain grids so every row and column cell is visibly separated; preserve clear component boundaries in technical diagrams. Add a subtitle only when it clarifies that page's action or distinction. For this user's guides, omit running header text and use footer branding `Abhinav Pullela . mcarkade`.
- Give assembly priority over decoration. Use dimensioned CAD-derived exploded and intermediate step views with visible mating faces, orientation cues, fasteners, retention and cable paths. Cross-check each view against the final CAD or real parts. A generic box or circle cannot stand in for a mechanism whose geometry decides the build.
- Inventory supplied local real photos and original CAD/STL renders before making new art. Use them alongside helpful generated imagery, with clear part names and IDs. Label what each image depicts, such as original arena CAD versus venue photo or source mechanism versus proposed robot. Pair course turn/path SVGs with the actual track or source image they interpret. Keep source, permission and image credits in the working record or guide as appropriate. For additional part-recognition photos, use original or properly licensed images. Make generated concept art one component or assembly per asset on a plain background and label it conceptual.
- Audit each generated image against approved CAD, wiring plans or photographed parts: part count and proportions, orientation, hidden or extra hardware, mating and retention, and wire routes. Reject or correct contradictions even when the image looks polished. When the design changes, update affected art and repeat the audit. Take exact fits, labels and connector pinouts from verified source data, never from generated or reference art.
- Specify electrical parts by the properties that affect compatibility. For example, give a battery's capacity in mAh, cell count such as 2S, nominal and full voltage, connector and polarity. Give a UBEC's output voltage, continuous current rating and accepted input range. Do not substitute an impressive unrelated rating for a missing required one.
- Draw each electrical component with a distinct boundary and named pins; show every intended pin-to-net connection, polarity, fuse or switch placement, signal direction and connector view where the builder connects them. Keep diagram boxes faithful to the real components and readable at print size. Show intermediate checkpoints, not only the completed machine.
- Give a clear print/make/buy breakdown and one ordered path through fabrication, assembly, wiring, calibration and operation. For competition builds, carry it through pre-race checks, race use and fault recovery. Name the action and result at each stage instead of vague labels such as "frame set".
- State concrete hazards at the step where they matter. Put project status, limits and any pending CAD or code work in one concise page when needed. Keep checklists where the builder uses them; cut repeated disclaimers and callouts.
- Caption an image when the text clarifies orientation, action, measurement or evidence, not to restate the page heading. Use ordinary words and explain an unfamiliar term at first use. The guide must make sense without linked Markdown files.

## Prove the delivered PDF

1. Generate from the approved design snapshot. Inspect every rendered page at reading size and print scale. Check legibility, cropped labels, image resolution, line weight, contrast, page order, repeated or conflicting text, and whether dimension arrows and wire routes point to the intended part.
2. Exercise every contents link, bookmark and return link in the exported PDF. Confirm text and labels remain searchable where practical. Reopen the exact delivered file and compare its BOM, ratings and critical dimensions with source data.
3. Walk through assembly and wiring as an independent reader. At every step, identify the physical part, orientation, attachment, tool or material, next action and pass/fail check without guessing. Trace at least one likely fault from symptom to safe recovery. Fix gaps and recheck affected pages and links.
4. Report which checks used source files or simulation and which still need physical assembly, measurement, power-on or field testing. Do not present a polished PDF as hardware proof.

When the user states a lasting preference during guide work, replace the stale guidance here, update the portable `agent-config` source and local installs, validate them, and publish only within the user's authorization. Avoid appending duplicate rules for each project.
