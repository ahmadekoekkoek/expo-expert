"""
Experience Compiler — the central pipeline that turns specifications
into React Native + Expo code through the graph-gate-generate chain.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from python.core.xos_logger import get_logger
from python.graph.engine import ExperienceGraph, GraphNode, NodeKind
from python.graph.knowledge_loader import load_knowledge_graph
from python.agents.runtime import AgentRuntime, AgentDefinition, AgentSkill
from python.validators.gates import QualityGatePipeline, GateResult, GateStatus, GateResult, GateStatus

logger = get_logger(__name__)


class ExperienceCompiler:
    """Orchestrates the full specification → code pipeline."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.graph = ExperienceGraph()
        self.agent_runtime = AgentRuntime()
        self.gates = QualityGatePipeline(fail_fast=True)

    def load_knowledge(self) -> None:
        kg = load_knowledge_graph(self.repo_root / "knowledge")
        for node in kg.nodes():
            self.graph.add_node(node)
        logger.info("Knowledge graph loaded: %d nodes", len(kg.nodes()))

    def load_specs(self, spec_dir: Path) -> None:
        for f in sorted(spec_dir.rglob("*.spec.json")):
            try:
                payload = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            items: List[Dict] = payload if isinstance(payload, list) else [payload]
            for item in items:
                try:
                    node = GraphNode(
                        id=item["id"],
                        kind=NodeKind(item["kind"]),
                        name=item["name"],
                        intent=item.get("intent", ""),
                        inputs=item.get("inputs", []),
                        outputs=item.get("outputs", []),
                        dependencies=item.get("dependencies", []),
                        constraints=item.get("constraints", {}),
                        metadata=item.get("metadata", {}),
                    )
                    self.graph.add_node(node)
                except (KeyError, ValueError):
                    continue
        logger.info("Spec graph loaded: %d nodes total", len(self.graph.nodes()))

    def validate(self) -> List[GateResult]:
        return self.gates.run()

    def compile(self, target_node_id: str) -> Dict[str, Any]:
        """Walk the graph from *target_node_id*, resolve deps, validate, plan agents,
        and produce a compiled artifact plan (not raw code — generators produce code)."""
        node = self.graph.get(target_node_id)
        if node is None:
            raise ValueError(f"Node '{target_node_id}' not found in graph")

        resolved = self.graph.resolve_dependencies(target_node_id)
        logger.info("Resolved %d nodes for target '%s'", len(resolved), target_node_id)

        plan: Dict[str, Any] = {
            "target": node.name,
            "intent": node.intent,
            "resolved_nodes": [n.id for n in resolved],
            "steps": [],
        }

        for n in resolved:
            deps_ok, missing = self.graph.are_dependencies_satisfied(n.id)
            if not deps_ok:
                logger.warning("Node '%s' has unsatisfied dependencies: %s", n.id, missing)
            step = {"node_id": n.id, "kind": n.kind.value, "generator": f"generators/{n.kind.value}/generate.py"}
            plan["steps"].append(step)

        validation_results = self.validate()
        plan["validation"] = [
            {"gate": r.gate, "status": r.status.value, "message": r.message}
            for r in validation_results
        ]
        return plan
