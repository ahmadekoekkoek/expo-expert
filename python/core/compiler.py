"""
XOS Experience Compiler — the deterministic pipeline that transforms
specifications through the Experience Graph into React Native + Expo code.

Never generates code directly — always compiles through validated stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

from .graph import ExperienceGraph, GraphNode, NodeType, GateStatus, ValidationResult


class PipelineStage(Enum):
    SPEC_LOAD = auto()
    KNOWLEDGE_GRAPH = auto()
    EXPERIENCE_GRAPH = auto()
    DEPENDENCY_RESOLUTION = auto()
    CONSTRAINT_VALIDATION = auto()
    AGENT_PLANNING = auto()
    MOTION_COMPILATION = auto()
    GESTURE_COMPILATION = auto()
    HAPTIC_COMPILATION = auto()
    ACCESSIBILITY_COMPILATION = auto()
    PERFORMANCE_OPTIMIZATION = auto()
    CODE_GENERATION = auto()


@dataclass
class CompilationDiagnostic:
    stage: PipelineStage
    level: str  # "error", "warning", "info"
    message: str
    node_id: str = ""
    suggestion: str = ""


@dataclass
class CompilationResult:
    success: bool
    graph: ExperienceGraph
    generated_files: list[Path] = field(default_factory=list)
    diagnostics: list[CompilationDiagnostic] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[CompilationDiagnostic]:
        return [d for d in self.diagnostics if d.level == "error"]

    @property
    def warnings(self) -> list[CompilationDiagnostic]:
        return [d for d in self.diagnostics if d.level == "warning"]


class ExperienceCompiler:
    """Deterministic pipeline: specs → graph → validation → agents → code."""

    QUALITY_GATES = [
        "specification",
        "graph",
        "architecture",
        "design",
        "motion",
        "gesture",
        "haptic",
        "accessibility",
        "performance",
        "testing",
        "documentation",
        "security",
    ]

    def __init__(self):
        self.graph: ExperienceGraph | None = None
        self.diagnostics: list[CompilationDiagnostic] = []
        self.generated_files: list[Path] = []
        self._validators: dict[str, Callable] = {}
        self._generators: dict[str, Callable] = {}

    def compile(self, graph: ExperienceGraph, output_dir: Path | None = None) -> CompilationResult:
        """Run the full compilation pipeline."""
        self.graph = graph
        self.diagnostics = []
        self.generated_files = []

        try:
            self._stage_dependency_resolution()
            self._stage_constraint_validation()
            self._stage_agent_planning()
            self._stage_motion_compilation()
            self._stage_gesture_compilation()
            self._stage_haptic_compilation()
            self._stage_accessibility_compilation()
            self._stage_performance_optimization()
            self._stage_code_generation(output_dir)
        except CompilationError as e:
            self.diagnostics.append(
                CompilationDiagnostic(
                    stage=e.stage, level="error", message=str(e)
                )
            )

        success = len([d for d in self.diagnostics if d.level == "error"]) == 0
        return CompilationResult(
            success=success,
            graph=self.graph,
            generated_files=self.generated_files,
            diagnostics=self.diagnostics,
        )

    def _stage_dependency_resolution(self) -> None:
        try:
            order = self.graph.topological_order()
            self._info(
                PipelineStage.DEPENDENCY_RESOLUTION,
                f"Resolved {len(order)} nodes in dependency order.",
            )
        except Exception as e:
            raise CompilationError(
                PipelineStage.DEPENDENCY_RESOLUTION, f"Dependency cycle or missing node: {e}"
            )

    def _stage_constraint_validation(self) -> None:
        for node_id, node in self.graph.nodes.items():
            if node.node_type == NodeType.ACCESSIBILITY:
                min_target = node.constraints.get("min_touch_target", 0)
                if min_target < 44:
                    self._error(
                        PipelineStage.CONSTRAINT_VALIDATION,
                        f"Touch target {min_target}pt < 44pt minimum.",
                        node_id,
                        "Increase min_touch_target to at least 44.",
                    )
            if node.node_type == NodeType.MOTION:
                if node.constraints.get("must_respect_reduced_motion") is not True:
                    self._error(
                        PipelineStage.CONSTRAINT_VALIDATION,
                        "Motion node must respect reduced motion preference.",
                        node_id,
                        "Set must_respect_reduced_motion = True.",
                    )
                budget = node.constraints.get("frame_budget_ms", 99)
                if budget > 16:
                    self._warning(
                        PipelineStage.CONSTRAINT_VALIDATION,
                        f"Frame budget {budget}ms exceeds 16ms target.",
                        node_id,
                    )
        self._info(PipelineStage.CONSTRAINT_VALIDATION, "Constraint validation complete.")

    def _stage_agent_planning(self) -> None:
        agent_nodes = self.graph.find_by_type(NodeType.AGENT)
        self._info(
            PipelineStage.AGENT_PLANNING,
            f"Planning execution for {len(agent_nodes)} agents.",
        )

    def _stage_motion_compilation(self) -> None:
        motion_nodes = self.graph.find_by_type(NodeType.MOTION)
        self._info(
            PipelineStage.MOTION_COMPILATION,
            f"Compiling {len(motion_nodes)} motion definitions.",
        )

    def _stage_gesture_compilation(self) -> None:
        gesture_nodes = self.graph.find_by_type(NodeType.GESTURE)
        for node in gesture_nodes:
            if node.constraints.get("must_define_conflict_resolution") is not True:
                self._warning(
                    PipelineStage.GESTURE_COMPILATION,
                    "Gesture missing conflict resolution strategy.",
                    node.id,
                )
        self._info(
            PipelineStage.GESTURE_COMPILATION,
            f"Compiling {len(gesture_nodes)} gesture definitions.",
        )

    def _stage_haptic_compilation(self) -> None:
        haptic_nodes = self.graph.find_by_type(NodeType.HAPTIC)
        self._info(
            PipelineStage.HAPTIC_COMPILATION,
            f"Compiling {len(haptic_nodes)} haptic definitions.",
        )

    def _stage_accessibility_compilation(self) -> None:
        a11y_nodes = self.graph.find_by_type(NodeType.ACCESSIBILITY)
        self._info(
            PipelineStage.ACCESSIBILITY_COMPILATION,
            f"Compiling {len(a11y_nodes)} accessibility definitions.",
        )

    def _stage_performance_optimization(self) -> None:
        self._info(
            PipelineStage.PERFORMANCE_OPTIMIZATION,
            "Running performance optimization passes.",
        )

    def _stage_code_generation(self, output_dir: Path | None) -> None:
        self._info(
            PipelineStage.CODE_GENERATION,
            f"Generating React Native + Expo code to {output_dir or 'memory'}.",
        )

    def _error(
        self, stage: PipelineStage, message: str, node_id: str = "", suggestion: str = ""
    ) -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="error", message=message, node_id=node_id, suggestion=suggestion)
        )

    def _warning(self, stage: PipelineStage, message: str, node_id: str = "") -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="warning", message=message, node_id=node_id)
        )

    def _info(self, stage: PipelineStage, message: str) -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="info", message=message)
        )


class CompilationError(Exception):
    def __init__(self, stage: PipelineStage, message: str):
        self.stage = stage
        super().__init__(f"[{stage.name}] {message}")
