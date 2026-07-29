"""XOS Graph Differ — detects changes between experience graph versions."""

import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class GraphDelta:
    added_nodes: list[str] = field(default_factory=list)
    removed_nodes: list[str] = field(default_factory=list)
    modified_nodes: list[str] = field(default_factory=list)
    added_edges: list[dict] = field(default_factory=list)
    removed_edges: list[dict] = field(default_factory=list)

class GraphDiffer:
    def diff(self, before_path: str, after_path: str) -> GraphDelta:
        before = json.loads(Path(before_path).read_text()) if Path(before_path).exists() else {"nodes": {}, "edges": []}
        after = json.loads(Path(after_path).read_text()) if Path(after_path).exists() else {"nodes": {}, "edges": []}
        delta = GraphDelta()
        b_nodes = set(before.get("nodes", {}).keys())
        a_nodes = set(after.get("nodes", {}).keys())
        delta.added_nodes = sorted(a_nodes - b_nodes)
        delta.removed_nodes = sorted(b_nodes - a_nodes)
        delta.modified_nodes = sorted(n for n in (b_nodes & a_nodes) if before["nodes"][n] != after["nodes"][n])
        b_edges = {(e["source"], e["target"]) for e in before.get("edges", [])}
        a_edges = {(e["source"], e["target"]) for e in after.get("edges", [])}
        delta.added_edges = [{"source": s, "target": t} for s, t in sorted(a_edges - b_edges)]
        delta.removed_edges = [{"source": s, "target": t} for s, t in sorted(b_edges - a_edges)]
        return delta

def cmd_diff(args):
    differ = GraphDiffer()
    delta = differ.diff(args.before, args.after)
    if not (delta.added_nodes or delta.removed_nodes or delta.modified_nodes or delta.added_edges or delta.removed_edges):
        print("No differences detected.")
        return
    if delta.added_nodes:
        print(f"+ {len(delta.added_nodes)} nodes added: {', '.join(delta.added_nodes)}")
    if delta.removed_nodes:
        print(f"- {len(delta.removed_nodes)} nodes removed: {', '.join(delta.removed_nodes)}")
    if delta.modified_nodes:
        print(f"~ {len(delta.modified_nodes)} nodes modified: {', '.join(delta.modified_nodes)}")
    if delta.added_edges:
        print(f"+ {len(delta.added_edges)} edges added")
    if delta.removed_edges:
        print(f"- {len(delta.removed_edges)} edges removed")
