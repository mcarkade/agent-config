"""Analytic fixtures and actual STEP readback, without project data."""
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

import cadquery as cq
from step_properties import adaptive_properties, inspect_step, main


class PropertyTests(unittest.TestCase):
    def test_asymmetric_centroid(self):
        first = cq.Workplane("XY").box(10, 20, 30).translate((123, 456, 789)).val()
        second = cq.Workplane("XY").box(40, 20, 5).translate((138, 456, 776.5)).val()
        result = adaptive_properties(first.fuse(second))
        self.assertAlmostEqual(result["volume"], 9000, places=5)
        for actual, expected in zip(result["centroid"], (129 + 2/3, 456, 784 + 5/6)):
            self.assertAlmostEqual(actual, expected, places=6)

    def test_reversed_solid_is_rejected(self):
        box = cq.Workplane("XY").box(10, 20, 30).val()
        reversed_box = cq.Shape.cast(box.wrapped.Reversed())
        with self.assertRaisesRegex(ValueError, "Nonpositive"):
            adaptive_properties(reversed_box)

    def test_empty_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            adaptive_properties(cq.Compound.makeCompound([]))

    def test_invalid_tolerance_is_rejected(self):
        box = cq.Workplane("XY").box(1, 1, 1).val()
        for eps in (0, -1, float("nan")):
            with self.assertRaises(ValueError):
                adaptive_properties(box, eps)

    def test_step_readback_identity_and_count(self):
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(prefix="step-check-", dir=root) as name:
            directory = Path(name).resolve()
            self.assertTrue(directory.is_relative_to(root))
            path = directory / "two-blocks.step"
            first = cq.Workplane("XY").box(10, 20, 30).val()
            second = first.translate((50, 0, 0))
            cq.exporters.export(cq.Compound.makeCompound([first, second]), str(path))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "Expected 1"):
                inspect_step(path)
            result = inspect_step(path, expected_solids=2)
            self.assertAlmostEqual(result["volume"], 12000, places=5)
            self.assertEqual(result["sha256"], before)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main([str(path), "--expect-solids", "2"]), 0)
            self.assertEqual(json.loads(output.getvalue())["results"][0]["sha256"], before)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
