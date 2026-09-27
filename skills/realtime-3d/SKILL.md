---
name: realtime-3d
description: Use when building or changing real-time 3D scenes, games or simulations, or diagnosing their rendering, physics, assets or streaming.
---

# Real-time 3D

Start with one representative, playable scene on the actual rendering backend and target hardware. Establish the intended camera, reference appearance, physical scale and acceptable loading/frame-time budget before expanding content. Compare the composed game view, including post-processing, rather than a separate preview render.

## Build a coherent world

- Choose sourced assets, authored geometry or procedural generation according to fidelity, rights and iteration cost. Record source licences, transforms and stable asset identities. Exercise the real loader, including cached and remote instances.
- Give position, scale, elevation, surface identity and simulation time clear owners. Rendering, collision, navigation, placement and networking must agree on their meaning. Distinguish world coordinates, route distance, local origins and display values.
- Design collision proxies for the intended contact response. Test actual contact locations and normals, seams, slopes and clearances with the real actor. Exact visual geometry can create unwanted ramps or ridges; a deliberate proxy needs its own measured envelope.
- Check effective forces and state at the engine boundary. Requested inputs or reported values alone do not prove what the native solver applies.

## Make quality measurable

Judge materials, lighting, shadows, foliage and silhouettes from normal play cameras, in motion and at relevant distances. Instance counts do not establish screen coverage. Compare near and far detail, dark scenes and transitions with matched captures. Preserve accepted visual quality when optimizing.

For instancing, inspect transform order, per-instance attributes, upload versions and shader variants. Warm the paths actually used by lighting, weather and camera changes. Prefer stable shader structure with runtime parameters where the engine supports it.

## Diagnose lifecycle cost

Separate generation, decoding, physics construction, shader building, upload, first draw and disposal. Record CPU and GPU evidence independently, with the actual adapter/backend. Profile the full operation, including work scheduled after its initiating click returns.

Exercise first arrival, revisits, distant placement, return travel, restart and disposal. Bound both residency and cache-generation work; repeated eviction can make a bounded cache catastrophically expensive. Progress deadlines should follow completed target work, retain an absolute limit and preserve independent network authority deadlines.

## Prove the claimed experience

Use the real actor, world and application entry path. Cover affected controls, contact, rendering, audio and lifecycle transitions. Check remote representations and late joining when networking is involved. Numerical gates, screenshots, listening and device playtests establish different facts. State which were observed, and verify the served artifact before claiming a deployment works.

## Validate mission simulations

- Separate evaluator truth from declared sensors, delivered messages and released work. Record observation and delivery times; a newly received packet can describe state older than the current command.
- Exercise delayed telemetry, lost commands, late starts, duplicates and restarts as causal protocol cases. Retain route occupancy until acceptance and departure are observed. Give rejected commands a bounded recovery path.
- Budget queue wait, transit, task work, return and landing before admission. Share the reserve calculation with the local failsafe and check it along the trajectory, including altitude-dependent descent. Rejecting an impossible return alone does not improve mission completion.
- Check swept motion and coverage during relay departure. Lost tracking creates uncertain occupancy; test whether a global admission pause also prevents the repair needed to clear it.
- Freeze source, configuration, assets and seed for each comparison. Distinguish kinematic, rigid-body, ideal-controller and autopilot evidence. Repeat the extracted delivery through its real entry point and record physical run-to-run spread.
- Define registered, deployed, armed, airborne, grounded, at-base and controlled-return counts separately. Keep all tasks in the denominator; separate report receipt, deadlines, disconnection, off-base landing and depletion. Challenge scoring with empty and boundary cases.
- Preserve failed runs and the original horizon. A changed budget is a new paired experiment. Freeze policy before unseen cases; after tuning, those cases are regressions. One successful actor or run cannot establish mission reliability.
