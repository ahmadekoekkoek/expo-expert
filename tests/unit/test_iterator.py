"""
Unit tests for the AutonomousIterator compilation loop.
"""

import pytest
import tempfile
import json
from pathlib import Path
from python.core.iterator import AutonomousIterator


class TestAutonomousIterator:
    def test_iterate_convergence(self):
        spec_content = {
            "name": "checkout",
            "version": "0.1.0",
            "description": "Checkout flow",
            "features": [{
                "name": "payment",
                "screens": [{
                    "name": "checkout_screen",
                    "route": "/checkout",
                    "components": ["card_element", "pay_button"]
                }]
            }]
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            spec_file = tmp_path / "checkout.spec.json"
            spec_file.write_text(json.dumps(spec_content), encoding="utf-8")

            output_dir = tmp_path / "features"

            iterator = AutonomousIterator(
                target_score=90.0,
                max_iterations=3,
                output_dir=output_dir,
            )

            summary = iterator.iterate_from_specs(spec_path=spec_file)

            assert summary.total_iterations >= 1
            assert summary.final_scorecard.total_score >= 90.0
            assert summary.success is True
            assert len(summary.generated_files) > 0

            # Verify specs on disk were auto-healed
            healed_json = json.loads(spec_file.read_text(encoding="utf-8"))
            assert "design_tokens" in healed_json
