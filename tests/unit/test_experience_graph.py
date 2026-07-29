"""
Unit tests for the Experience Graph engine.
"""
import pytest
import json
import tempfile
import os
from python.graph.experience_graph import ExperienceGraph, GraphNode, GraphEdge, NodeKind, EdgeKind


class TestGraphNode:
    def test_create_node(self):
        node = GraphNode(id="test:screen", kind=NodeKind.SCREEN, label="Test Screen")
        assert node.id == "test:screen"
        assert node.kind == NodeKind.SCREEN
        assert node.label == "Test Screen"

    def test_node_serialization(self):
        node = GraphNode(id="test:comp", kind=NodeKind.COMPONENT, label="Button", metadata={"size": "md"})
        data = node.__dict__
        assert data["id"] == "test:comp"
        assert data["kind"] == NodeKind.COMPONENT
        assert data["metadata"] == {"size": "md"}

    def test_node_deserialization(self):
        node = GraphNode(id="test:feat", kind=NodeKind.FEATURE, label="Auth")
        assert node.kind == NodeKind.FEATURE
        assert node.label == "Auth"


class TestExperienceGraph:
    def test_add_node(self):
        g = ExperienceGraph()
        node = GraphNode(id="screen:home", kind=NodeKind.SCREEN, label="Home")
        g.add_node(node)
        assert g.has_node("screen:home")
        assert g.get_node("screen:home").label == "Home"

    def test_add_edge(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(id="feat:browse", kind=NodeKind.FEATURE, label="Browse"))
        g.add_node(GraphNode(id="screen:home", kind=NodeKind.SCREEN, label="Home"))
        edge = GraphEdge(source="feat:browse", target="screen:home", kind=EdgeKind.COMPOSES)
        g.add_edge(edge)
        assert "screen:home" in g.successors("feat:browse")
        assert "feat:browse" in g.predecessors("screen:home")

    def test_validate_integrity_empty(self):
        g = ExperienceGraph()
        report = g.validate_integrity()
        assert report["valid"] is True
        assert report["node_count"] == 0

    def test_validate_integrity_ok(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(id="feat:a", kind=NodeKind.FEATURE, label="A", intent="test feature"))
        g.add_node(GraphNode(id="screen:b", kind=NodeKind.SCREEN, label="B", intent="test screen", constraints={"frame_budget": 16}))
        g.add_edge(GraphEdge(source="feat:a", target="screen:b", kind=EdgeKind.COMPOSES))
        report = g.validate_integrity()
        assert report["valid"] is True
        assert report["node_count"] == 2
        assert report["edge_count"] == 1

    def test_topological_sort(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(id="feat:a", kind=NodeKind.FEATURE, label="A"))
        g.add_node(GraphNode(id="screen:b", kind=NodeKind.SCREEN, label="B"))
        g.add_node(GraphNode(id="comp:c", kind=NodeKind.COMPONENT, label="C"))
        g.add_edge(GraphEdge(source="feat:a", target="screen:b", kind=EdgeKind.COMPOSES))
        g.add_edge(GraphEdge(source="screen:b", target="comp:c", kind=EdgeKind.COMPOSES))
        order = g.topological_sort()
        assert order.index("feat:a") < order.index("screen:b")
        assert order.index("screen:b") < order.index("comp:c")

    def test_serialization_roundtrip(self):
        import tempfile
        import os
        g = ExperienceGraph()
        g.add_node(GraphNode(id="feat:a", kind=NodeKind.FEATURE, label="A"))
        g.add_node(GraphNode(id="screen:b", kind=NodeKind.SCREEN, label="B"))
        g.add_edge(GraphEdge(source="feat:a", target="screen:b", kind=EdgeKind.COMPOSES))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(g.to_json())
            json_path = f.name

        with open(json_path) as f2:
            g2 = ExperienceGraph.from_json(f2.read())
        assert g2.has_node("feat:a")
        assert g2.has_node("screen:b")
        assert "screen:b" in g2.successors("feat:a")

        os.unlink(json_path)


class TestExperienceGraphValidation:
    def test_dangling_edge_detected(self):
        g = ExperienceGraph()
        g.add_node(GraphNode(id="screen:a", kind=NodeKind.SCREEN, label="A"))
        with pytest.raises(KeyError, match="Unknown source node"):
            g.add_edge(GraphEdge(source="screen:x", target="screen:a", kind=EdgeKind.COMPOSES))