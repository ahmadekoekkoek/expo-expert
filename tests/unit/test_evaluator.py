"""
Unit tests for the QualityEvaluator scoring engine.
"""

import pytest
from python.core.graph import ExperienceGraph, GraphNode, NodeType
from python.core.evaluator import QualityEvaluator


class TestQualityEvaluator:
    def test_evaluate_empty_graph(self):
        evaluator = QualityEvaluator(target_score=95.0)
        graph = ExperienceGraph(name="empty")
        scorecard = evaluator.evaluate(graph=graph)

        assert scorecard.total_score < 60.0
        assert scorecard.grade == "F (Unacceptable)"
        assert scorecard.passed_threshold is False
        assert len(scorecard.blocking_issues) > 0

    def test_evaluate_complete_graph(self):
        evaluator = QualityEvaluator(target_score=95.0)
        graph = ExperienceGraph(name="complete")

        # Feature
        graph.add_node(GraphNode(id="feat:home", node_type=NodeType.FEATURE, intent="Home feature"))
        # Screen
        graph.add_node(GraphNode(id="screen:home", node_type=NodeType.SCREEN, intent="Home screen"))
        graph.edges["feat:home"] = {"screen:home"}

        # Motion
        m_node = GraphNode(
            id="motion:screen:home",
            node_type=NodeType.MOTION,
            constraints={"must_respect_reduced_motion": True, "frame_budget_ms": 16},
        )
        graph.add_node(m_node)

        # Haptic
        h_node = GraphNode(id="haptic:screen:home:0", node_type=NodeType.HAPTIC, intent="lightImpact")
        graph.add_node(h_node)

        # Gesture
        g_node = GraphNode(
            id="gesture:screen:home:0",
            node_type=NodeType.GESTURE,
            constraints={"must_define_conflict_resolution": True},
        )
        graph.add_node(g_node)

        # Accessibility
        a_node = GraphNode(
            id="a11y:screen:home",
            node_type=NodeType.ACCESSIBILITY,
            constraints={"min_touch_target": 44},
        )
        graph.add_node(a_node)

        graph.edges["screen:home"] = {
            "motion:screen:home",
            "haptic:screen:home:0",
            "gesture:screen:home:0",
            "a11y:screen:home",
        }

        spec_dicts = [{
            "name": "home",
            "design_tokens": {"color": "#000"},
            "motion_tokens": {"preset": "fade"},
        }]

        scorecard = evaluator.evaluate(graph=graph, spec_dicts=spec_dicts)
        assert scorecard.total_score >= 90.0
        assert scorecard.dimensions["accessibility_inclusivity"].score == 15.0
        assert scorecard.dimensions["motion_quality"].score == 15.0
        assert scorecard.dimensions["gesture_responsiveness"].score == 15.0
