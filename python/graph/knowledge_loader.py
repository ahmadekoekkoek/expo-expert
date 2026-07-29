"""
Experience Graph knowledge loader — reify the static knowledge/
directory tree into GraphNodes the compiler can traverse.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from python.graph.engine import ExperienceGraph, GraphNode, NodeKind


def _walk_json_nodes(root: Path, graph: ExperienceGraph) -> None:
    """Ingest every *.graph.json file under *root*.  Each file may contain
    a list of node dicts (or a single dict)."""
    for f in sorted(root.rglob("*.graph.json")):
        try:
            payload = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        items: List[Dict] = payload if isinstance(payload, list) else [payload]
        for item in items:
            try:
                node = GraphNode(
                    id=item.get("id", ""),
                    kind=NodeKind(item["kind"]),
                    name=item["name"],
                    intent=item.get("intent", ""),
                    inputs=item.get("inputs", []),
                    outputs=item.get("outputs", []),
                    dependencies=item.get("dependencies", []),
                    constraints=item.get("constraints", {}),
                    metadata=item.get("metadata", {}),
                )
                graph.add_node(node)
            except (KeyError, ValueError):
                continue


def load_knowledge_graph(root: Path) -> ExperienceGraph:
    """Populate a graph from the knowledge/ directory tree."""
    graph = ExperienceGraph()
    _walk_json_nodes(root, graph)
    return graph
