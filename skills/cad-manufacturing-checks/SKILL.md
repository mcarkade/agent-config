---
name: cad-manufacturing-checks
description: Verify mechanical CAD and fabrication deliverables across STEP parts, flat cutting profiles and sliced print meshes. Use for manufacturing preparation or audits, rather than visual-only 3D work.
---

# CAD manufacturing checks

Keep installed geometry, stock blanks, cut patterns and printable blanks distinct. Establish units, coordinate frames, material thicknesses and immutable parts before editing. Retain accepted exterior geometry unless the task authorizes a change.

## Establish the physical interfaces

Separate nominal CAD thickness from measured stock, printed dimensions and actual hardware. Build the tolerance stack from the process, mating parts and intended functional fit. Update both sides of a joint when thickness or manufacture changes; do not apply a universal clearance. Record what is measured, specified, inferred or still unestablished. Qualify representative coupons and dry-fit the interfaces before a full cutting or printing run; keep already manufactured parts where an evidenced local repair works.

Resolve the exact hardware model from inventory evidence and primary manufacturer drawings. A motor size, connector family or broad specification is not a hole pattern. Distinguish bolt-circle diameter, adjacent and diagonal spacing, orientation and cable/shaft datums. Conflicting drawing and marketing dimensions require an actual-part check. Preserve shaft/boss reliefs and verify seating, screw engagement and internal clearance, not only centre coordinates. Derive screws from the complete plate/washer/clamp stack and measured safe thread depth; check bottoming, hidden windings, supported washer contact and driver access. Request the smallest missing measurement or view and continue independent work.

## Validate the delivered solids

Read the exported STEP before healing it. Check raw topology, expected connected-solid count, positive volume for every solid, dimensions and mass properties. An in-memory repair does not repair the file. If repair is justified, copy the shape first, export the repair and inspect a fresh readback. Healing can mutate shared topology.

Prove functional interfaces on the exported geometry with material/void assertions at the intended sections. Check D-flats and blind shaft stops, working clamp travel, screw/nut engagement and tool access. Valid topology and mesh closure alone do not establish grip, retention or assembly.

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

When converting a load-bearing part to print, justify the material, orientation, walls and infill against its actual load path. Include loads normal to the layers, in-plane torque, clamp compression, vibration, adhesive transfer and sustained heat. Full infill alone does not establish strength; metal or wood assumptions do not transfer to a polymer. Consider creep, preload relaxation, layer adhesion and warping. Verify the actual printer and spool can make the chosen material. Manufacturer thermal/mechanical specimen data are not an allowable service temperature or a finished-part rating; name the remaining physical coupon, clamp, thermal and proof-load gates.

Keep finished STEP and print-blank differences explicit, including post-print cutting. Record the exact STL hash, any mesh cleanup, orientation, required bed/height, walls, infill, brim and support flags. Slice that file and inspect warnings and toolpaths; exit code zero is insufficient.

Locate unsupported starts by layer and physical feature before changing geometry. Align a real end face to the bed when an approximate axis rotation leaves small toes. Try orientation and accessible support before adding parts. Check support removal access and remaining bridge lengths. Separate object mass from support/brim waste; neither is measured mass. A reference printer envelope is not proof of the owner's printer fit.

For thin films or flexures, verify sliced material covers the required functional region at its intended thickness and layers. A handling tab or nearby brim cannot stand in for that region. Keep required supports and actual fastener lengths consistent across source, print manifest and guide; derive screw length from the full clamp/nut stack and access checks.

## Freeze evidence at useful boundaries

Give every installed part a unique ID and export destination. Check the identification views and the real insertion order, hand/driver approaches, adhesive faces, wire routing, strain relief and post-closure service/removal paths. Include actual head, washer, connector and support-removal envelopes; an empty CAD intersection does not prove a builder can install or retain the part. Populate dimensions and centroids from final readbacks. Verify positive-area joints, assembly interference, removal paths and moving envelopes separately; zero intersection does not prove attachment.

Freeze source, registry and artifact hashes before downstream checks. Cache part checks by artifact hash, helper/kernel version and numerical settings; pair and motion checks also depend on both parts and transforms. Preserve a checkpoint so a local correction need not rerun unrelated geometry. Metadata-only changes do not invalidate unchanged shape evidence, but the final report must identify the current registry.

Include installed padding, component tolerance and disconnected plugs in removal sweeps. For flexure clearance, distinguish the moving member and its intended root joints from fixed obstructions. Inject a blocking witness to prove the check detects binding; do not shorten or exempt a failed probe merely to make it pass.

State the boundary of the result: digital geometry, CAM and slicing checks do not establish material strength, adhesive quality, real hardware fit, measured balance or safe operation. Name the remaining physical coupon, fit, load or motion check instead of claiming it occurred.
