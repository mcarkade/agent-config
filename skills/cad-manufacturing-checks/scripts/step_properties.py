"""Read-only STEP topology and adaptive mass-property inspection (CadQuery/OCP)."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import OCP
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps


def _integrate(shape, eps, centroid):
    props = GProp_GProps()
    error = BRepGProp.VolumePropertiesGK_s(
        shape.wrapped, props, eps, True, True, centroid
    )
    if not math.isfinite(error) or error < 0 or not math.isfinite(props.Mass()):
        raise ValueError("Adaptive integration failed")
    return props, error


def adaptive_properties(shape, eps=1e-7):
    """Reject invalid/nonpositive solids; never heal, reverse or modify input."""
    if not math.isfinite(eps) or eps <= 0:
        raise ValueError("Integration tolerance must be finite and positive")
    if not shape.isValid():
        raise ValueError("Raw shape topology is invalid")
    solids = shape.Solids()
    if not solids:
        raise ValueError("Shape contains no solids")
    solid_volumes = []
    for solid in solids:
        if not solid.isValid():
            raise ValueError("Raw solid topology is invalid")
        props, _ = _integrate(solid, eps, False)
        if props.Mass() <= 0:
            raise ValueError("Nonpositive solid volume; do not mask with abs()")
        solid_volumes.append(props.Mass())
    props, error = _integrate(shape, eps, True)
    centre = props.CentreOfMass()
    coordinates = [centre.X(), centre.Y(), centre.Z()]
    if props.Mass() <= 0 or not all(math.isfinite(v) for v in coordinates):
        raise ValueError("Nonpositive volume or nonfinite centroid")
    bounds = shape.BoundingBox()
    return {
        "raw_valid": True,
        "solid_count": len(solids),
        "solid_volumes": solid_volumes,
        "volume": props.Mass(),
        "centroid": coordinates,
        "bbox": [bounds.xmin, bounds.ymin, bounds.zmin,
                 bounds.xmax, bounds.ymax, bounds.zmax],
        "integration_eps": eps,
        "estimated_relative_error": error,
        "units": "Loaded CAD length units; volume uses their cube",
    }


def inspect_step(path, expected_solids=1, eps=1e-7):
    if expected_solids < 1:
        raise ValueError("Expected solid count must be positive")
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    shape = cq.importers.importStep(str(path)).val()
    result = adaptive_properties(shape, eps)
    if result["solid_count"] != expected_solids:
        raise ValueError(
            f"Expected {expected_solids} solid(s), found {result['solid_count']}"
        )
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("STEP changed during inspection")
    return {"file": str(path), "sha256": digest, **result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", nargs="+", type=Path)
    parser.add_argument("--expect-solids", type=int, default=1)
    parser.add_argument("--eps", type=float, default=1e-7)
    args = parser.parse_args(argv)
    results = []
    for path in args.step:
        try:
            results.append(inspect_step(path, args.expect_solids, args.eps))
        except Exception as exc:
            results.append({"file": str(path), "error": str(exc)})
    report = {
        "scope": "Raw STEP topology and mass properties only",
        "cadquery_version": cq.__version__,
        "ocp_version": getattr(OCP, "__version__", "unknown"),
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "results": results,
    }
    print(json.dumps(report, indent=2, allow_nan=False))
    return int(any("error" in result for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
