"""
Experience Graph — the source of truth.  All nodes are first-class
graph entities with typed edges and constraint validation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class NodeKind(str, Enum):
    PRODUCT = "product"
    DOMAIN = "domain"
    FEATURE = "feature"
    WORKFLOW = "workflow"
    BUSINESS_RULE = "business_rule"
    SCREEN = "screen"
    COMPONENT = "component"
    NAVIGATION = "navigation"
    STATE = "state"
    DESIGN_TOKEN = "design_token"
    TYPOGRAPHY = "typography"
    COLOR = "color"
    MOTION = "motion"
    GESTURE = "gesture"
    HAPTIC = "haptic"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    PROMPT = "prompt"
    AGENT = "agent"
    MCP_TOOL = "mcp_tool"
    TEST = "test"
    DOCUMENTATION = "documentation"


class EdgeKind(str, Enum):
    REQUIRES = "requires"
    GENERATES = "generates"
    CONSTRAINS = "constrains"
    IMPLEMENTS = "implements"
    COMPOSES = "composes"
    NAVIGATES_TO = "navigates_to"
    ANIMATES = "animates"


class GraphNode:
    __slots__ = (
        "id", "kind", "name", "intent", "inputs", "outputs",
        "dependencies", "constraints", "metadata", "version", "generated_artifacts",
    )

    def __init__(
        self,
        id: str,
        kind: NodeKind,
        name: str,
        intent: str = "",
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        version: str = "0.1.0",
    ) -> None:
        self.id = id
        self.kind = kind
        self.name = name
        self.intent = intent
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.dependencies = dependencies or []
        self.constraints = constraints or {}
        self.metadata = metadata or {}
        self.version = version
        self.generated_artifacts: List[str] = []


class GraphEdge:
    __slots__ = ("source", "target", "kind")

    def __init__(self, source: str, target: str, kind: EdgeKind) -> None:
        self.source = source
        self.target = target
        self.kind = kind


class ExperienceGraph:
    """Directed graph of all specification, design, and implementation nodes."""

    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._adj_in: Dict[str, List[GraphEdge]] = {}
        self._adj_out: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> None:
        self._nodes[node.id] = node
        self._adj_in.setdefault(node.id, [])
        self._adj_out.setdefault(node.id, [])

    def add_edge(self, source: str, target: str, kind: EdgeKind) -> GraphEdge:
        edge = GraphEdge(source, target, kind)
        if source not in self._nodes or target not in self._nodes:
            raise ValueError(f"Edge references unknown node: {source} → {target}")
        self._edges.append(edge)
        self._adj_out.setdefault(source, []).append(edge)
        self._adj_in.setdefault(target, []).append(edge)
        return edge

    def get(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def nodes(self) -> List[GraphNode]:
        return list(self._nodes.values())

    def edges(self) -> List[GraphEdge]:
        return list(self._edges)

    def predecessors(self, node_id: str) -> List[GraphEdge]:
        return self._adj_in.get(node_id, [])

    def successors(self, node_id: str) -> List[GraphEdge]:
        return self._adj_out.get(node_id, [])

    def resolve_dependencies(self, node_id: str) -> List[GraphNode]:
        """Topological walk resolving all transitive dependencies."""
        visited: Set[str] = set()
        result: List[GraphNode] = []

        def _visit(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            for dep_edge in self._adj_in.get(nid, []):
                _visit(dep_edge.source)
            node = self._nodes.get(nid)
            if node and node.id != node_id:
                result.append(node)

        _visit(node_id)
        return result

    def are_dependencies_satisfied(self, node_id: str) -> Tuple[bool, List[str]]:
        node = self._nodes.get(node_id)
        if node is None:
            return False, [node_id]
        missing = [d for d in node.dependencies if d not in self._nodes]
        return len(missing) == 0, missing

    def validate_integrity(self) -> List[str]:
        issues: List[str] = []
        for node in self._nodes.values():
            for dep in node.dependencies:
                if dep not in self._nodes:
                    issues.append(f"Node '{node.id}' depends on unknown node '{dep}'")
        for edge in self._edges:
            if edge.source not in self._nodes:
                issues.append(f"Edge source '{edge.source}' does not exist")
            if edge.target not in self._nodes:
                issues.append(f"Edge target '{edge.target}' does not exist")
        return issues
