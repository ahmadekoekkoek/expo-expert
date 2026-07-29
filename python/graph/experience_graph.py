"""
XOS Experience Graph — the single source of truth for every artifact.

Every node represents a first-class concept (screen, component, gesture,
motion token, haptic pattern, accessibility rule, performance constraint).

The graph validates relationships, resolves dependencies, and drives the
deterministic compilation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid
import json

# ──────────────────────────────────────────────────────────────────

class NodeKind(str, Enum):
    SCREEN = "screen"
    COMPONENT = "component"
    NAVIGATION = "navigation"
    STATE = "state"
    MOTION_TOKEN = "motion_token"
    GESTURE_PATTERN = "gesture_pattern"
    HAPTIC_PATTERN = "haptic_pattern"
    ACCESSIBILITY_RULE = "accessibility_rule"
    DESIGN_TOKEN = "design_token"
    COLOR_TOKEN = "color_token"
    TYPOGRAPHY_TOKEN = "typography_token"
    PERFORMANCE_TARGET = "performance_target"
    AGENT = "agent"
    PROMPT = "prompt"
    MCP_TOOL = "mcp_tool"
    FEATURE = "feature"
    WORKFLOW = "workflow"
    BUSINESS_RULE = "business_rule"
    DOMAIN = "domain"
    PRODUCT = "product"
    DOCUMENTATION = "documentation"
    TEST = "test"

# ──────────────────────────────────────────────────────────────────

class EdgeKind(str, Enum):
    DEPENDS_ON = "depends_on"
    COMPOSES = "composes"
    NAVIGATES_TO = "navigates_to"
    IMPLEMENTS = "implements"
    ANIMATES = "animates"
    GESTURES = "gestures"
    HAPTICS = "haptics"
    ACCESSES = "accesses"
    THEMES = "themes"
    CONSTRAINS = "constrains"
    DERIVES_FROM = "derives_from"
    TESTS = "tests"
    DOCUMENTS = "documents"
    GENERATES = "generates"
    VALIDATES = "validates"
    PREVENTS = "prevents"

# ──────────────────────────────────────────────────────────────────

@dataclass
class GraphNode:
    id: str
    kind: NodeKind
    label: str
    intent: str = ""
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    validations: Dict[str, Any] = field(default_factory=dict)
    quality_gates: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    version: str = "0.1.0"
    generated_artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int: return hash(self.id)

# ──────────────────────────────────────────────────────────────────

@dataclass
class GraphEdge:
    source: str
    target: str
    kind: EdgeKind
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

# ──────────────────────────────────────────────────────────────────

class ExperienceGraph:
    """Mutable directed graph backed by adjacency lists."""

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self.nodes: Dict[str, GraphNode] = {}
        self._outgoing: Dict[str, Set[str]] = {}
        self._incoming: Dict[str, Set[str]] = {}
        self.edges: List[GraphEdge] = []

    # ── node CRUD ────────────────────────────────────────────

    def add_node(self, node: GraphNode) -> GraphNode:
        if node.id in self.nodes:
            raise KeyError(f"Duplicate node id: {node.id}")
        self.nodes[node.id] = node
        self._outgoing.setdefault(node.id, set())
        self._incoming.setdefault(node.id, set())
        return node

    def get_node(self, node_id: str) -> GraphNode:
        return self.nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    # ── edge CRUD ────────────────────────────────────────────

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        if edge.source not in self.nodes:
            raise KeyError(f"Unknown source node: {edge.source}")
        if edge.target not in self.nodes:
            raise KeyError(f"Unknown target node: {edge.target}")
        self.edges.append(edge)
        self._outgoing[edge.source].add(edge.target)
        self._incoming[edge.target].add(edge.source)
        return edge

    def successors(self, node_id: str) -> Set[str]:
        return self._outgoing.get(node_id, set())

    def predecessors(self, node_id: str) -> Set[str]:
        return self._incoming.get(node_id, set())

    # ── graph analysis ───────────────────────────────────────

    def topological_sort(self) -> List[str]:
        """Kahn's algorithm. Raises RuntimeError on cycle."""
        indegree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for e in self.edges:
            indegree[e.target] += 1

        queue: List[str] = [nid for nid, d in indegree.items() if d == 0]
        result: List[str] = []

        while queue:
            nid = queue.pop(0)
            result.append(nid)
            for succ in self._outgoing.get(nid, set()):
                indegree[succ] -= 1
                if indegree[succ] == 0:
                    queue.append(succ)

        if len(result) != len(self.nodes):
            remaining = {nid for nid, d in indegree.items() if d > 0}
            raise RuntimeError(f"Cycle detected among nodes: {remaining}")
        return result

    def validate_integrity(self) -> Dict[str, Any]:
        """Run all structural checks and return a report."""
        issues: List[Dict[str, Any]] = []

        for edge in self.edges:
            edge_issues = self._validate_edge(edge)
            if edge_issues:
                issues.extend(edge_issues)

        for node in self.nodes.values():
            node_issues = self._validate_node(node)
            if node_issues:
                issues.extend(node_issues)

        return {
            "valid": len(issues) == 0,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "issues": issues,
        }

    def _validate_edge(self, edge: GraphEdge) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        source = self.nodes.get(edge.source)
        target = self.nodes.get(edge.target)
        if source.kind == NodeKind.PERFORMANCE_TARGET and target.kind == NodeKind.SCREEN:
            pass  # valid
        return issues

    def _validate_node(self, node: GraphNode) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        if not node.intent:
            issues.append({"node": node.id, "issue": "Missing intent"})
        if node.kind == NodeKind.SCREEN and not node.constraints.get("frame_budget"):
            issues.append({"node": node.id, "issue": "Screen missing frame_budget constraint"})
        return issues

    # ── serialization ────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "nodes": {nid: {**n.__dict__, "kind": n.kind.value} for nid, n in self.nodes.items()},
            "edges": [{**e.__dict__, "kind": e.kind.value} for e in self.edges],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperienceGraph":
        g = cls(name=data["name"])
        for nid, nd in data["nodes"].items():
            nd["kind"] = NodeKind(nd["kind"])
            g.add_node(GraphNode(**nd))
        for ed in data["edges"]:
            ed["kind"] = EdgeKind(ed["kind"])
            g.add_edge(GraphEdge(**ed))
        return g

    @classmethod
    def from_json(cls, payload: str) -> "ExperienceGraph":
        return cls.from_dict(json.loads(payload))
