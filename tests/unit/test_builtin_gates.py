"""
Unit tests for built-in Quality Gates.
"""

import pytest
from python.validators.builtin_gates import (
    gate_spec_validation,
    gate_architecture,
    gate_motion,
    gate_gesture,
    gate_accessibility,
    gate_security,
)
from python.validators.gates import GateSeverity
from python.core.graph import ExperienceGraph, GraphNode, NodeType


class TestBuiltinGates:
    def test_gate_architecture(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(id="feat:a", node_type=NodeType.FEATURE))
        g.add_node(GraphNode(id="screen:b", node_type=NodeType.SCREEN))
        g.edges["feat:a"] = {"screen:b"}

        res = gate_architecture({"graph": g})
        assert res.severity == GateSeverity.PASS

    def test_gate_accessibility_pass(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(
            id="a11y:screen:home",
            node_type=NodeType.ACCESSIBILITY,
            constraints={"min_touch_target": 44},
        ))
        res = gate_accessibility({"graph": g})
        assert res.severity == GateSeverity.PASS

    def test_gate_accessibility_fail(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(
            id="a11y:screen:home",
            node_type=NodeType.ACCESSIBILITY,
            constraints={"min_touch_target": 30},
        ))
        res = gate_accessibility({"graph": g})
        assert res.severity == GateSeverity.FAIL

    def test_gate_security_pass(self):
        res = gate_security({"generated_files": []})
        assert res.severity == GateSeverity.PASS
