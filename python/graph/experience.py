"""
XOS Experience Graph — the single source of truth for every compiled artifact.

Represents product, domain, feature, workflow, business-rule, screen,
component, navigation, state, design-token, typography, color, motion,
gesture, haptic, accessibility, performance, prompt, agent, mcp-tool,
test, and documentation nodes.

The Experience Compiler reads this graph — it NEVER generates React Native
code directly. Code is a compiled artifact; the graph is the source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import hashlib
import networkx as nx


# ──────────────────────────────────────────────────────────────────
# Node taxonomy
# ──────────────────────────────────────────────────────────────────

class XNodeKind(str, Enum):
    PRODUCT           = "product"
    DOMAIN            = "domain"
    FEATURE           = "feature"
    WORKFLOW          = "workflow"
    BUSINESS_RULE     = "business-rule"
    SCREEN            = "screen"
    COMPONENT         = "component"
    NAVIGATION        = "navigation"
    STATE             = "state"
    DESIGN_TOKEN      = "design-token"
    TYPOGRAPHY        = "typography"
    COLOR             = "color"
    MOTION            = "motion"
    GESTURE           = "gesture"
    HAPTIC            = "haptic"
    ACCESSIBILITY     = "accessibility"
    PERFORMANCE       = "performance"
    PROMPT            = "prompt"
    AGENT             = "agent"
    MCP_TOOL          = "mcp-tool"
    TEST              = "test"
    DOCUMENTATION     = "documentation"

# ──────────────────────────────────────────────────────────────────
# Constraint severity
# ──────────────────────────────────────────────────────────────────

class Severity(str, Enum):
    ERROR   = "error"
    WARNING = "warning"
    INFO    = "info"

# ──────────────────────────────────────────────────────────────────

@dataclass
class Constraint:
    name: str
    description: str
    check: str                                   # validator reference
    severity: Severity = Severity.ERROR
    auto_fix: Optional[str] = None

# ──────────────────────────────────────────────────────────────────

@dataclass
class ExperienceNode:
    id: str
    kind: XNodeKind
    intent: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    owner: str = ""
    version: int = 1
    generated_artifacts: List[str] = field(default_factory=list)
    props: Dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        raw = json.dumps(self.props, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

# ──────────────────────────────────────────────────────────────────
# Graph
# ──────────────────────────────────────────────────────────────────

class ExperienceGraph:
    """Directed acyclic graph of experience nodes.

    The compiler walks this graph to produce code, tests, docs — and
    stops immediately if any validation gate fails.
    """

    def __init__(self, store_path: Optional[Path] = None) -> None:
        self.g = nx.DiGraph()
        self._nodes: Dict[str, ExperienceNode] = {}
        self.store_path = store_path

    # ── add / get ───────────────────────────────────────────

    def add_node(self, node: ExperienceNode) -> None:
        self._nodes[node.id] = node
        self.g.add_node(node.id, kind=node.kind.value)

    def add_edge(self, src_id: str, dst_id: str) -> None:
        self.g.add_edge(src_id, dst_id)

    def get(self, node_id: str) -> Optional[ExperienceNode]:
        return self._nodes.get(node_id)

    @property
    def nodes(self) -> Dict[str, ExperienceNode]:
        return self._nodes

    # ── traversal ───────────────────────────────────────────

    def topological_order(self) -> List[str]:
        """Return node IDs in dependency-respecting order. Raises on cycles."""
        try:
            return list(nx.topological_sort(self.g))
        except nx.NetworkXUnfeasible:
            cycle = nx.find_cycle(self.g)
            raise ValueError(f"Experience graph contains a cycle: {cycle}")

    def ancestors(self, node_id: str) -> Set[str]:
        return set(nx.ancestors(self.g, node_id))

    def descendants(self, node_id: str) -> Set[str]:
        return set(nx.descendants(self.g, node_id))

    def immediate_deps(self, node_id: str) -> Set[str]:
        return set(self.g.predecessors(node_id))

    def immediate_children(self, node_id: str) -> Set[str]:
        return set(self.g.successors(node_id))

    # ── sub-graph extraction ────────────────────────────────

    def extract_feature_graph(self, feature_id: str) -> ExperienceGraph:
        """Return a new graph containing the feature and all descendants."""
        sub = ExperienceGraph()
        for nid in [feature_id] + list(self.descendants(feature_id)):
            node = self._nodes.get(nid)
            if node:
                sub.add_node(node)
        edges = [(u, v) for u, v in self.g.edges()
                 if u in sub._nodes and v in sub._nodes]
        sub.g.add_edges_from(edges)
        return sub

    # ── validation ──────────────────────────────────────────

    def validate_acyclic(self) -> List[Tuple[str, str, str]]:
        """Return list of cycles found, empty if acyclic."""
        try:
            cycles = list(nx.simple_cycles(self.g))
            return [(" → ".join(c), "cycle detected", Severity.ERROR) for c in cycles]
        except Exception:
            return []

    def validate_connectivity(self) -> List[str]:
        orphans = [nid for nid in self.g.nodes
                   if self.g.in_degree(nid) == 0 and self.g.out_degree(nid) == 0]
        return orphans

    # ── serialisation ───────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {nid: n.__dict__ for nid, n in self._nodes.items()},
            "edges": list(self.g.edges),
        }

    def to_json(self, path: Optional[Path] = None) -> str:
        payload = json.dumps(self.to_dict(), indent=2, default=str)
        if path:
            path.write_text(payload)
        return payload

    @classmethod
    def from_json(cls, path: Path) -> "ExperienceGraph":
        data = json.loads(path.read_text())
        eg = cls()
        for nid, nd in data.get("nodes", {}).items():
            eg.add_node(ExperienceNode(**{k: v for k, v in nd.items() if k != "id"} or {"id": nid}))
        eg.g.add_edges_from(data.get("edges", []))
        return eg

    def stats(self) -> Dict[str, Any]:
        by_kind: Dict[str, int] = {}
        for n in self._nodes.values():
            by_kind[n.kind.value] = by_kind.get(n.kind.value, 0) + 1
        return {
            "total_nodes": len(self._nodes),
            "total_edges": self.g.number_of_edges(),
            "by_kind": by_kind,
            "orphans": self.validate_connectivity(),
            "cycles": len(self.validate_acyclic()),
        }
