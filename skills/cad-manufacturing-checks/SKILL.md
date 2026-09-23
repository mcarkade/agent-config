---
name: cad-manufacturing-checks
description: Verify mechanical CAD and fabrication deliverables across STEP parts, flat cutting profiles and sliced print meshes. Use for manufacturing preparation or audits, rather than visual-only 3D work.
---

# CAD manufacturing checks

Keep installed geometry, stock blanks, cut patterns and printable blanks distinct. Establish units, coordinate frames, material thicknesses and immutable parts before editing. Retain accepted exterior geometry unless the task authorizes a change.

## Validate the delivered solids

Read the exported STEP before healing it. Check raw topology, expected connected-solid count, positive volume for every solid, dimensions and mass properties. An in-memory repair does not repair the file. If repair is justified, copy the shape first, export the repair and inspect a fresh readback. Healing can mutate shared topology.

Default fixed-order volume integration can be inaccurate on trimmed spline faces. For CadQuery/OCP, [scripts/step_properties.py](scripts/step_properties.py) provides read-only adaptive integration, per-solid checks, centroids and input hashes. Run with the project's CAD Python:

```text
python scripts/step_properties.py part.step
python scripts/step_properties.py assembly.step --expect-solids 12
python scripts/test_step_properties.py
```

It requires CadQuery/OCP. Adaptive centroid integration needs `CGFlag=True`; a plausible volume alone does not validate the centroid. Compare tighter tolerances on a representative difficult part. Record numerical convergence and STEP round-trip differences separately; do not choose tolerances merely to suppress failures.

For subtractive edits, check immediately after each operation: valid positive solids, volume cannot increase, removed volume cannot exceed the cutter, and the result stays within its input. Positive total volume alone can conceal complement solids. Classify disconnected pieces as separate parts or bounded cutting waste; never silently keep only the largest piece.

## Prove the cut profile

Select the stock-thickness end face, not automatically the largest planar face. A long thin plate can have a larger side face. Verify the projection frame and physical thickness, then independently parse the exported DXF, including holes and disconnected contours.

Compare profile area times thickness with the stock volume. Also extrude the actual cut profile in its declared frame and compare it geometrically with the stock shape: equal area is necessary but does not prove equal shape or hole placement. Use a stock blank for grooves or shaped plugs, with explicit secondary operations. Do not describe a partial-depth pocket as a through-cut. Recheck nesting with grain direction, margins and actual stock dimensions.

Carry a physical grain vector through each part's world-to-DXF transform and its nesting rotation. Recompute the flattening frame for mirrored parts; copying the other side's axis can pass contour and spacing checks while rotating the intended grain. Verify the transformed vector against the stock grain and inspect both mirrored profiles in the final layout. For split formers or similar aligned pieces, check their shared assembly face after changing thickness; preserving each centre independently can introduce a step.

## Verify the exact print input

Keep finished STEP and print-blank differences explicit, including post-print cutting. Record the exact STL hash, any mesh cleanup, orientation, required bed/height, walls, infill, brim and support flags. Slice that file and inspect warnings and toolpaths; exit code zero is insufficient.

Locate unsupported starts by layer and physical feature before changing geometry. Align a real end face to the bed when an approximate axis rotation leaves small toes. Try orientation and accessible support before adding parts. Check support removal access and remaining bridge lengths. Separate object mass from support/brim waste; neither is measured mass. A reference printer envelope is not proof of the owner's printer fit.

## Freeze evidence at useful boundaries

Give every installed part a unique ID and export destination. Populate dimensions and centroids from final readbacks. Verify positive-area joints, assembly interference, removal paths and moving envelopes separately; zero intersection does not prove attachment.

Freeze source, registry and artifact hashes before downstream checks. Cache part checks by artifact hash, helper/kernel version and numerical settings; pair and motion checks also depend on both parts and transforms. Preserve a checkpoint so a local correction need not rerun unrelated geometry. Metadata-only changes do not invalidate unchanged shape evidence, but the final report must identify the current registry.

State the boundary of the result: digital geometry, CAM and slicing checks do not establish material strength, adhesive quality, real hardware fit, measured balance or safe operation. Name the remaining physical coupon, fit, load or motion check instead of claiming it occurred.
