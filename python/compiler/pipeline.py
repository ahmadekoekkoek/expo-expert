"""
XOS Experience Compiler — the main compilation pipeline.

Takes specs → Knowledge Graph → Experience Graph → Agent plan →
motion/gesture/haptic/a11y compilation → performance optimisation →
React Native + Expo code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from python.core.xos_logger import get_logger
from python.graph.engine import ExperienceGraph, GraphNode, NodeKind
from python.validators.gates import GateValidator, build_builtin_validator, GateFailure

logger = get_logger(__name__)


class CompilationError(Exception):
    """Non-recoverable compilation failure."""

    def __init__(self, failures: List[GateFailure]):
        self.failures = failures
        msg = "\n".join(f"  • [{f.severity.value}] {f.gate}: {f.reason}" for f in failures)
        super().__init__(f"Compilation failed with {len(failures)} gate failure(s):\n{msg}")


@dataclass
class CompiledArtifact:
    files: Dict[str, str] = field(default_factory=dict)   # path → contents
    graph: Optional[ExperienceGraph] = None
    validation_report: List[GateFailure] = field(default_factory=list)
    agent_trace: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    passed: bool = False


class ExperienceCompiler:
    """Orchestrate the full transformation from spec to compiled output."""

    def __init__(self, validator: Optional[GateValidator] = None) -> None:
        self.validator = validator or build_builtin_validator()
        self.graph = ExperienceGraph()

    def load_spec(self, spec: Dict[str, Any]) -> None:
        """Ingest a structured feature specification and seed the graph."""
        features = spec.get("features", [])
        for feat in features:
            fid = feat.get("id", feat.get("name", ""))
            if not fid:
                continue
            self.graph.add_node(GraphNode(
                id=f"feat:{fid}",
                kind=NodeKind.FEATURE,
                name=feat.get("name", fid),
                intent=feat.get("intent", ""),
                metadata={"source_spec": feat},
            ))

    def compile(self, artifact_name: str) -> CompiledArtifact:
        """Run the full pipeline and return a CompiledArtifact."""
        result = CompiledArtifact()
        result.agent_trace.append("[compiler] Starting pipeline")

        # 1) Validate the graph against all quality gates
        failures = self.validator.validate({"graph_nodes": list(self.graph.iter_nodes())})
        result.validation_report = failures
        blockers = [f for f in failures if f.severity.value != "info"]
        if blockers:
            result.passed = False
            logger.warning("Compilation blocked — %d gate failures", len(blockers))
            return result

        # 2) Resolve dependencies (graph topology check)
        diags = self.graph.validate_topology()
        if diags:
            for d in diags:
                failures.append(GateFailure(gate="graph-topology", reason=d))
            result.passed = False
            return result

        # 3) Walk the graph and dispatch to domain generators
        result.agent_trace.append("[compiler] Dependency resolution complete")
        # (stub — generators would be invoked here)
        result.agent_trace.append(f"[compiler] Graph contains {self.graph.node_count} nodes, {self.graph.edge_count} edges")
        result.graph = self.graph
        result.passed = True
        result.metrics["node_count"] = self.graph.node_count
        result.metrics["edge_count"] = self.graph.edge_count
        return result
