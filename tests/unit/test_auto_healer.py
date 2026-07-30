"""
Unit tests for the SpecAutoHealer engine.
"""

import pytest
from python.core.graph import ExperienceGraph, GraphNode, NodeType
from python.core.evaluator import QualityEvaluator
from python.core.auto_healer import SpecAutoHealer


class TestSpecAutoHealer:
    def test_heal_missing_nodes(self):
        graph = ExperienceGraph(name="incomplete")
        graph.add_node(GraphNode(id="screen:settings", node_type=NodeType.SCREEN, intent="Settings"))

        spec_dicts = [{
            "name": "settings",
            "features": [{
                "screens": [{
                    "name": "settings",
                    "accessibility": {"minTouchTarget": 32}  # Sub-44pt violation
                }]
            }]
        }]

        evaluator = QualityEvaluator(target_score=95.0)
        scorecard = evaluator.evaluate(graph=graph, spec_dicts=spec_dicts)

        healer = SpecAutoHealer()
        healed_graph, healed_specs, actions = healer.heal(graph, spec_dicts, scorecard)

        assert len(actions) > 0

        # Verify touch target raised
        screen_spec = healed_specs[0]["features"][0]["screens"][0]
        assert screen_spec["accessibility"]["minTouchTarget"] == 44
        assert "motion" in screen_spec
        assert "haptics" in screen_spec

        # Verify healed graph has motion/haptic/gesture/a11y nodes
        types = [n.node_type for n in healed_graph.nodes.values()]
        assert NodeType.MOTION in types
        assert NodeType.HAPTIC in types
        assert NodeType.GESTURE in types
        assert NodeType.ACCESSIBILITY in types
