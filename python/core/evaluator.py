"""
XOS Quality Evaluator Engine — Scores Experience Graphs and generated artifacts
against Silicon Valley engineering and UX standards (0-100 scale).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .graph import ExperienceGraph, NodeType
from .anti_slop import AntiSlopEngine


@dataclass
class DimensionScore:
    name: str
    score: float
    max_score: float
    details: List[str] = field(default_factory=list)


@dataclass
class QualityScorecard:
    total_score: float
    grade: str
    passed_threshold: bool
    dimensions: Dict[str, DimensionScore] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"==================================================",
            f"          XOS QUALITY SCORECARD",
            f"==================================================",
            f" Overall Score: {self.total_score:.1f} / 100",
            f" Grade:         {self.grade}",
            f" Status:        {'[PASS] PASSED (Silicon Valley Grade)' if self.passed_threshold else '[FAIL] NEEDS REFINEMENT'}",
            f"--------------------------------------------------",
            f" Dimension Breakdown:",
        ]
        for name, dim in self.dimensions.items():
            pct = (dim.score / dim.max_score * 100) if dim.max_score > 0 else 0
            lines.append(f"  - {dim.name:<32}: {dim.score:5.1f} / {dim.max_score:4.1f} ({pct:5.1f}%)")

        if self.blocking_issues:
            lines.append(f"--------------------------------------------------")
            lines.append(f" [BLOCK] Blocking Issues ({len(self.blocking_issues)}):")
            for b in self.blocking_issues:
                lines.append(f"   * {b}")

        if self.recommendations:
            lines.append(f"--------------------------------------------------")
            lines.append(f" [WARN] Recommended Improvements ({len(self.recommendations)}):")
            for r in self.recommendations[:10]:
                lines.append(f"   * {r}")

        lines.append(f"==================================================")
        return "\n".join(lines)


class QualityEvaluator:
    """Silicon Valley Grade Product & Engineering Quality Evaluator."""

    def __init__(self, target_score: float = 95.0) -> None:
        self.target_score = target_score
        self.anti_slop = AntiSlopEngine()

    def evaluate(
        self,
        graph: ExperienceGraph,
        generated_files: Optional[List[Path]] = None,
        spec_dicts: Optional[List[Dict[str, Any]]] = None,
    ) -> QualityScorecard:
        dimensions: Dict[str, DimensionScore] = {}
        blocking_issues: List[str] = []
        recommendations: List[str] = []

        # 1. Graph Integrity & Completeness (20 pts)
        dim_graph = self._eval_graph_integrity(graph)
        dimensions["graph_integrity"] = dim_graph

        # 2. Motion & Physics Polish (15 pts)
        dim_motion = self._eval_motion(graph)
        dimensions["motion_quality"] = dim_motion

        # 3. Gesture & Feedback Responsiveness (15 pts)
        dim_gesture = self._eval_gestures(graph)
        dimensions["gesture_responsiveness"] = dim_gesture

        # 4. Accessibility & Dynamic Type (15 pts)
        dim_a11y = self._eval_accessibility(graph)
        dimensions["accessibility_inclusivity"] = dim_a11y

        # 5. Anti-Slop & Code Quality (15 pts)
        dim_slop = self._eval_anti_slop(generated_files)
        dimensions["anti_slop_code_quality"] = dim_slop

        # 6. Performance & Budget Constraints (10 pts)
        dim_perf = self._eval_performance(graph)
        dimensions["performance_budget"] = dim_perf

        # 7. Design Tokens & Styling Consistency (10 pts)
        dim_tokens = self._eval_design_tokens(graph, spec_dicts)
        dimensions["design_tokens_consistency"] = dim_tokens

        # Aggregate total score
        total_score = sum(d.score for d in dimensions.values())
        max_possible = sum(d.max_score for d in dimensions.values())
        if max_possible > 0:
            total_score = round((total_score / max_possible) * 100.0, 1)

        # Collect issues & recommendations
        for d in dimensions.values():
            for detail in d.details:
                if detail.startswith("BLOCK:"):
                    blocking_issues.append(detail[6:].strip())
                elif detail.startswith("WARN:"):
                    recommendations.append(detail[5:].strip())

        # Determine grade
        if total_score >= 95.0:
            grade = "A+ (Silicon Valley Grade)"
        elif total_score >= 85.0:
            grade = "A (Production Grade)"
        elif total_score >= 75.0:
            grade = "B (Good Baseline)"
        elif total_score >= 60.0:
            grade = "C (Needs Work)"
        else:
            grade = "F (Unacceptable)"

        passed = total_score >= self.target_score and len(blocking_issues) == 0

        return QualityScorecard(
            total_score=total_score,
            grade=grade,
            passed_threshold=passed,
            dimensions=dimensions,
            recommendations=recommendations,
            blocking_issues=blocking_issues,
        )

    def _eval_graph_integrity(self, graph: ExperienceGraph) -> DimensionScore:
        max_score = 20.0
        score = max_score
        details = []

        screens = graph.find_by_type(NodeType.SCREEN)
        features = graph.find_by_type(NodeType.FEATURE)

        if not features:
            score -= 5.0
            details.append("WARN: Graph contains no feature nodes.")
        if not screens:
            score -= 10.0
            details.append("BLOCK: Graph contains no screen nodes.")

        # Check screen completeness (each screen should have motion, haptic, gesture, a11y)
        for s in screens:
            neighbors = set()
            for edge_target in graph.edges.get(s.id, set()):
                neighbors.add(edge_target)
            # Reverse edge check
            for src_id, targets in graph.edges.items():
                if s.id in targets:
                    neighbors.add(src_id)

            has_motion = any("motion" in n or (n in graph.nodes and graph.nodes[n].node_type == NodeType.MOTION) for n in neighbors)
            has_haptic = any("haptic" in n or (n in graph.nodes and graph.nodes[n].node_type == NodeType.HAPTIC) for n in neighbors)
            has_a11y = any("a11y" in n or (n in graph.nodes and graph.nodes[n].node_type == NodeType.ACCESSIBILITY) for n in neighbors)
            has_gesture = any("gesture" in n or (n in graph.nodes and graph.nodes[n].node_type == NodeType.GESTURE) for n in neighbors)

            missing = []
            if not has_motion: missing.append("motion")
            if not has_haptic: missing.append("haptic")
            if not has_a11y: missing.append("accessibility")
            if not has_gesture: missing.append("gesture")

            if missing:
                penalty = 1.5 * len(missing)
                score = max(0.0, score - penalty)
                details.append(f"WARN: Screen '{s.id}' is missing layers: {', '.join(missing)}.")

        return DimensionScore("Graph Integrity & Completeness", round(score, 1), max_score, details)

    def _eval_motion(self, graph: ExperienceGraph) -> DimensionScore:
        max_score = 15.0
        score = max_score
        details = []

        motion_nodes = graph.find_by_type(NodeType.MOTION)
        if not motion_nodes:
            return DimensionScore("Motion & Physics Polish", 0.0, max_score, ["WARN: No motion nodes in graph."])

        for m in motion_nodes:
            constraints = m.constraints or {}
            if not constraints.get("must_respect_reduced_motion"):
                score = max(0.0, score - 2.0)
                details.append(f"WARN: Motion node '{m.id}' missing reduced-motion constraint.")

            frame_budget = constraints.get("frame_budget_ms", 16)
            if frame_budget > 16:
                score = max(0.0, score - 3.0)
                details.append(f"WARN: Motion node '{m.id}' frame budget ({frame_budget}ms) exceeds 16ms.")

        return DimensionScore("Motion & Physics Polish", round(score, 1), max_score, details)

    def _eval_gestures(self, graph: ExperienceGraph) -> DimensionScore:
        max_score = 15.0
        score = max_score
        details = []

        gesture_nodes = graph.find_by_type(NodeType.GESTURE)
        if not gesture_nodes:
            return DimensionScore("Gesture & Feedback Responsiveness", 0.0, max_score, ["WARN: No gesture nodes in graph."])

        for g in gesture_nodes:
            constraints = g.constraints or {}
            if not constraints.get("must_define_conflict_resolution"):
                score = max(0.0, score - 2.5)
                details.append(f"WARN: Gesture node '{g.id}' missing conflict resolution policy.")

        return DimensionScore("Gesture & Feedback Responsiveness", round(score, 1), max_score, details)

    def _eval_accessibility(self, graph: ExperienceGraph) -> DimensionScore:
        max_score = 15.0
        score = max_score
        details = []

        a11y_nodes = graph.find_by_type(NodeType.ACCESSIBILITY)
        if not a11y_nodes:
            return DimensionScore("Accessibility & Dynamic Type", 0.0, max_score, ["BLOCK: No accessibility nodes defined."])

        for a in a11y_nodes:
            constraints = a.constraints or {}
            min_target = constraints.get("min_touch_target", 44)
            if min_target < 44:
                score = max(0.0, score - 4.0)
                details.append(f"BLOCK: Touch target {min_target}pt < 44pt minimum on '{a.id}'.")

        return DimensionScore("Accessibility & Dynamic Type", round(score, 1), max_score, details)

    def _eval_anti_slop(self, generated_files: Optional[List[Path]]) -> DimensionScore:
        max_score = 15.0
        score = max_score
        details = []

        if not generated_files:
            return DimensionScore("Anti-Slop & Code Quality", max_score, max_score, ["INFO: No compiled files to scan yet."])

        slop_count = 0
        for f in generated_files:
            if f.exists() and f.suffix in (".ts", ".tsx"):
                content = f.read_text(encoding="utf-8")
                findings = self.anti_slop.scan(content, str(f))
                if findings:
                    slop_count += len(findings)
                    for find in findings:
                        details.append(f"WARN: Slop in {f.name}: {find.message}")

        if slop_count > 0:
            score = max(0.0, score - (slop_count * 2.0))

        return DimensionScore("Anti-Slop & Code Quality", round(score, 1), max_score, details)

    def _eval_performance(self, graph: ExperienceGraph) -> DimensionScore:
        max_score = 10.0
        score = max_score
        details = []

        screens = graph.find_by_type(NodeType.SCREEN)
        for s in screens:
            meta = s.metadata or {}
            comps = meta.get("components", [])
            # Check for list components that should specify FlashList
            has_list = any("list" in c.lower() or "feed" in c.lower() for c in comps)
            if has_list and not meta.get("uses_flash_list", True):
                score = max(0.0, score - 2.5)
                details.append(f"WARN: Screen '{s.id}' has scrollable list component but doesn't specify FlashList.")

        return DimensionScore("Performance & Budget Constraints", round(score, 1), max_score, details)

    def _eval_design_tokens(
        self, graph: ExperienceGraph, spec_dicts: Optional[List[Dict[str, Any]]]
    ) -> DimensionScore:
        max_score = 10.0
        score = max_score
        details = []

        has_tokens = False
        if spec_dicts:
            for sd in spec_dicts:
                if "design_tokens" in sd or "motion_tokens" in sd:
                    has_tokens = True
                    break

        if not has_tokens:
            score -= 3.0
            details.append("WARN: No explicit design_tokens found in spec files.")

        return DimensionScore("Design Tokens & Styling Consistency", round(score, 1), max_score, details)
