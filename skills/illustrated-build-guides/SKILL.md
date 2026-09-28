---
name: illustrated-build-guides
description: Create or revise illustrated PDF build guides for physical projects, especially assembly, wiring, calibration and fault finding. Use when a reader must build from the guide without the working notes.
---

# Illustrated build guides

Make the guide usable at a workbench by someone who did not join the design discussion. The PDF must stand alone. Keep research history and unresolved design debate in the working record.

## Establish the build

1. Read the current design decisions, final CAD and part exports, electrical plan, BOM, and any existing guide. Resolve conflicts before drawing. Keep part IDs, names, quantities, colors, ratings, connectors and wire labels identical across the BOM, views, steps and diagrams. Treat a guide-only engineering change as a design change: record and verify it with the owner of the design rather than silently illustrating it.
2. Make an assembly map before laying out pages: each part's ID and orientation, how it is retained, the order that keeps fasteners and connectors accessible, each electrical connection, and the checks before power or motion. Mark measured facts, calculated values, planned work and physical checks distinctly.

## Show what the builder must see

- Open with a clickable contents page and PDF bookmarks. Show what the finished object does, its dimensions and major assemblies, then let the reader reach the exact step or fault path quickly. Add return links when a long guide benefits from them.
- Give assembly priority over decoration. Use dimensioned CAD-derived exploded and intermediate step views with visible mating faces, orientation cues, fasteners, retention and cable paths. Cross-check each view against the final CAD or real parts. A generic box or circle cannot stand in for a mechanism whose geometry decides the build.
- Use clear part names alongside IDs. Add real, properly licensed photos when they help identify purchased parts or connector polarity. Keep source, permission and image credits in the working record or guide as appropriate. If image generation helps explain a concept, make one component or assembly per asset on a plain background and label it conceptual; it does not prove dimensions, fit or fabrication.
- Specify electrical parts by the properties that affect compatibility. For example, give a battery's capacity in mAh, cell count such as 2S, nominal and full voltage, connector and polarity. Give a UBEC's output voltage, continuous current rating and accepted input range. Do not substitute an impressive unrelated rating for a missing required one.
- Put exact wiring, pin names, polarity, fuse or switch placement, signal direction and connector views where the builder connects them. Follow with calibration, normal operation, recovery and fault flow. Show intermediate checkpoints, not only the completed machine.
- State concrete hazards at the step where they matter. Keep any pending CAD or code work in one concise roadmap page when a guide must precede those files; do not repeat uncertainty callouts on every page.
- Use short captions and ordinary words. Explain an unfamiliar term at first use. The guide must make sense without linked Markdown files.

## Prove the delivered PDF

1. Generate from the approved design snapshot. Inspect every rendered page at reading size and print scale. Check legibility, cropped labels, image resolution, line weight, contrast, page order, repeated or conflicting text, and whether dimension arrows and wire routes point to the intended part.
2. Exercise every contents link, bookmark and return link in the exported PDF. Confirm text and labels remain searchable where practical. Reopen the exact delivered file and compare its BOM, ratings and critical dimensions with source data.
3. Walk through assembly and wiring as an independent reader. At every step, identify the physical part, orientation, attachment, tool or material, next action and pass/fail check without guessing. Trace at least one likely fault from symptom to safe recovery. Fix gaps and recheck affected pages and links.
4. Report which checks used source files or simulation and which still need physical assembly, measurement, power-on or field testing. Do not present a polished PDF as hardware proof.

When the user states a lasting preference during guide work, replace the stale guidance here, update the portable `agent-config` source and local installs, validate them, and publish only within the user's authorization. Avoid appending duplicate rules for each project.
