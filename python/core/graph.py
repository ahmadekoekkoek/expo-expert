"""
XOS Experience Graph — the source of truth for all application structure.

Every concept (screen, component, gesture, animation, a11y rule, etc.)
is represented as a typed, validated graph node with explicit relationships.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class NodeType(Enum):
    PRODUCT = auto()
    DOMAIN = auto()
    FEATURE = auto()
    WORKFLOW = auto()
    BUSINESS_RULE = auto()
    SCREEN = auto()
    COMPONENT = auto()
    NAVIGATION = auto()
    STATE = auto()
    DESIGN_TOKEN = auto()
    TYPOGRAPHY = auto()
    COLOR = auto()
    MOTION = auto()
    GESTURE = auto()
    HAPTIC = auto()
    ACCESSIBILITY = auto()
    PERFORMANCE = auto()
    PROMPT = auto()
    AGENT = auto()
    MCP_TOOL = auto()
    TEST = auto()
    DOCUMENTATION = auto()


class GateStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ValidationResult:
    gate: str
    status: GateStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphNode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType = NodeType.COMPONENT
    intent: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    validation: list[ValidationResult] = field(default_factory=list)
    quality_gates: dict[str, GateStatus] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    owner: str = ""
    version: str = "0.1.0"
    generated_artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_dependency(self, node_id: str) -> Self:
        if node_id not in self.dependencies:
            self.dependencies.append(node_id)
        return self

    def set_gate(self, gate: str, status: GateStatus) -> Self:
        self.quality_gates[gate] = status
        return self

    def all_gates_passed(self) -> bool:
        return all(s == GateStatus.PASSED for s in self.quality_gates.values())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "node_type": self.node_type.name,
            "intent": self.intent,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "constraints": self.constraints,
            "quality_gates": {k: v.value for k, v in self.quality_gates.items()},
            "owner": self.owner,
            "version": self.version,
            "generated_artifacts": self.generated_artifacts,
            "metadata": self.metadata,
        }


class ExperienceGraph:
    """Directed graph of all experience nodes."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[str, set[str]] = {}  # node_id -> {dependent_node_ids}

    def add_node(self, node: GraphNode) -> GraphNode:
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = set()
        for dep in node.dependencies:
            self.edges.setdefault(dep, set()).add(node.id)
        return node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def find_by_type(self, node_type: NodeType) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def topological_order(self) -> list[GraphNode]:
        """Return nodes in dependency-respecting order."""
        visited: set[str] = set()
        order: list[GraphNode] = []

        def visit(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            node = self.nodes.get(nid)
            if node:
                for dep in node.dependencies:
                    if dep in self.nodes:
                        visit(dep)
                order.append(node)

        for nid in self.nodes:
            visit(nid)
        return order

    def validate_all_gates(self) -> dict[str, list[ValidationResult]]:
        results: dict[str, list[ValidationResult]] = {}
        for node in self.topological_order():
            failures = [v for v in node.validation if v.status == GateStatus.FAILED]
            if failures:
                results[node.id] = failures
        return results

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": {nid: list(deps) for nid, deps in self.edges.items()},
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> Self:
        data = json.loads(path.read_text())
        graph = cls(name=data["name"])
        raw_nodes = data.get("nodes", {})
        raw_edges = data.get("edges", {})
        for nid, ndata in raw_nodes.items():
            node_type_str = ndata.get("node_type") or ndata.get("kind", "COMPONENT")
            try:
                nt = NodeType[node_type_str.upper()]
            except KeyError:
                nt = NodeType.COMPONENT
            node = GraphNode(
                id=nid,
                node_type=nt,
                intent=ndata.get("intent", ndata.get("label", "")),
                inputs=ndata.get("inputs", []),
                outputs=ndata.get("outputs", []),
                dependencies=ndata.get("dependencies", []),
                constraints=ndata.get("constraints", {}),
                owner=ndata.get("owner", ""),
                version=ndata.get("version", "0.1.0"),
                generated_artifacts=ndata.get("generated_artifacts", []),
                metadata=ndata.get("metadata", {}),
            )
            graph.nodes[nid] = node
        if isinstance(raw_edges, list):
            for e in raw_edges:
                graph.edges.setdefault(e["source"], set()).add(e["target"])
        else:
            for nid, deps in raw_edges.items():
                graph.edges[nid] = set(deps)
        return graph
