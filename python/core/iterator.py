"""
XOS Autonomous Iterator Engine — Orchestrates the iterative loop of compiling,
scoring, auto-healing, and re-compiling until target Silicon Valley grade is met.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .compiler import ExperienceCompiler
from .evaluator import QualityEvaluator, QualityScorecard
from .auto_healer import SpecAutoHealer
from .graph import ExperienceGraph
from .node_factory import load_spec_into_graph


@dataclass
class IterationStep:
    iteration: int
    score: float
    grade: str
    actions_taken: List[str] = field(default_factory=list)
    errors_count: int = 0
    warnings_count: int = 0


@dataclass
class IterationSummary:
    success: bool
    final_scorecard: QualityScorecard
    total_iterations: int
    history: List[IterationStep] = field(default_factory=list)
    generated_files: List[Path] = field(default_factory=list)

    def report(self) -> str:
        lines = [
            "==================================================",
            "      XOS AUTONOMOUS ITERATION REPORT",
            "==================================================",
            f" Status:           {'[OK] GOAL ACHIEVED' if self.success else '[WARN] MAX ITERATIONS REACHED'}",
            f" Total Iterations: {self.total_iterations}",
            f" Final Score:      {self.final_scorecard.total_score:.1f} / 100 ({self.final_scorecard.grade})",
            "--------------------------------------------------",
            " Iteration Progression:",
        ]
        for step in self.history:
            lines.append(
                f"  Iter {step.iteration}: Score {step.score:5.1f} ({step.grade}) | Actions: {len(step.actions_taken)}"
            )
            for act in step.actions_taken[:3]:
                lines.append(f"          -> {act}")
            if len(step.actions_taken) > 3:
                lines.append(f"          -> ... and {len(step.actions_taken) - 3} more actions.")

        lines.append("--------------------------------------------------")
        lines.append(self.final_scorecard.summary())
        return "\n".join(lines)


class AutonomousIterator:
    """Autonomous goal-seeking compilation & refinement loop."""

    def __init__(
        self,
        target_score: float = 95.0,
        max_iterations: int = 5,
        output_dir: Optional[Path] = None,
    ) -> None:
        self.target_score = target_score
        self.max_iterations = max_iterations
        self.output_dir = output_dir or Path("features")
        self.evaluator = QualityEvaluator(target_score=target_score)
        self.healer = SpecAutoHealer()
        self.compiler = ExperienceCompiler()

    def iterate_from_specs(
        self,
        spec_path: Path,
        graph_path: Optional[Path] = None,
    ) -> IterationSummary:
        spec_files: List[Path] = []
        if spec_path.is_dir():
            spec_files = sorted(list(spec_path.glob("*.json")) + list(spec_path.glob("*.yaml")))
        elif spec_path.is_file():
            spec_files = [spec_path]

        spec_dicts: List[Dict[str, Any]] = []
        for sf in spec_files:
            try:
                data = json.loads(sf.read_text(encoding="utf-8"))
                spec_dicts.append(data)
            except Exception as e:
                pass

        graph = ExperienceGraph(name="iterative")
        for sd in spec_dicts:
            load_spec_into_graph(graph, sd)

        return self.iterate(graph, spec_dicts, spec_files, graph_path)

    def iterate(
        self,
        graph: ExperienceGraph,
        spec_dicts: Optional[List[Dict[str, Any]]] = None,
        spec_files: Optional[List[Path]] = None,
        graph_path: Optional[Path] = None,
    ) -> IterationSummary:
        spec_dicts = spec_dicts or []
        history: List[IterationStep] = []
        current_graph = graph
        current_specs = spec_dicts
        generated_files: List[Path] = []

        for iteration in range(1, self.max_iterations + 1):
            # 1. Compile
            compile_res = self.compiler.compile(current_graph, output_dir=self.output_dir)
            generated_files = compile_res.generated_files

            # 2. Score
            scorecard = self.evaluator.evaluate(
                graph=current_graph,
                generated_files=generated_files,
                spec_dicts=current_specs,
            )

            # Record step
            history.append(
                IterationStep(
                    iteration=iteration,
                    score=scorecard.total_score,
                    grade=scorecard.grade,
                    errors_count=len(compile_res.errors),
                    warnings_count=len(compile_res.warnings),
                )
            )

            # 3. Check if target achieved
            if scorecard.passed_threshold or iteration == self.max_iterations:
                if graph_path:
                    graph_path.parent.mkdir(parents=True, exist_ok=True)
                    current_graph.save(graph_path)
                return IterationSummary(
                    success=scorecard.passed_threshold,
                    final_scorecard=scorecard,
                    total_iterations=iteration,
                    history=history,
                    generated_files=generated_files,
                )

            # 4. Auto-Heal & Refine
            current_graph, current_specs, actions = self.healer.heal(
                current_graph, current_specs, scorecard
            )
            history[-1].actions_taken = actions

            # Save updated specs to disk if files available
            if spec_files and len(spec_files) == len(current_specs):
                for sf, sd in zip(spec_files, current_specs):
                    try:
                        sf.write_text(json.dumps(sd, indent=2), encoding="utf-8")
                    except Exception:
                        pass

            # Re-sync spec into graph
            new_graph = ExperienceGraph(name="healed")
            for sd in current_specs:
                load_spec_into_graph(new_graph, sd)

            # Merge any extra nodes from current_graph
            for nid, node in current_graph.nodes.items():
                if nid not in new_graph.nodes:
                    new_graph.add_node(node)
            for src, targets in current_graph.edges.items():
                if src in new_graph.edges:
                    new_graph.edges[src].update(targets)
                else:
                    new_graph.edges[src] = set(targets)

            current_graph = new_graph

        final_scorecard = self.evaluator.evaluate(
            graph=current_graph,
            generated_files=generated_files,
            spec_dicts=current_specs,
        )
        return IterationSummary(
            success=final_scorecard.passed_threshold,
            final_scorecard=final_scorecard,
            total_iterations=self.max_iterations,
            history=history,
            generated_files=generated_files,
        )
