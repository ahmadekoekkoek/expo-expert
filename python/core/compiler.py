"""
XOS Experience Compiler — the deterministic pipeline that transforms
specifications through the Experience Graph into React Native + Expo code.

Never generates code directly — always compiles through validated stages.
"""

from __future__ import annotations

import sys
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
    SCREEN_COMPILATION = auto()
    PERFORMANCE_OPTIMIZATION = auto()
    CODE_GENERATION = auto()


STAGE_BY_NAME = {s.name: s for s in PipelineStage}


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


class _StopAfter(Exception):
    def __init__(self, stage):
        self.stage = stage


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
        self._artifacts: dict[str, list[tuple[str, str]]] = {}
        self._validators: dict[str, Callable] = {}
        self._generators: dict[str, Callable] = {}

    def compile(self, graph: ExperienceGraph, output_dir: Path | None = None,
                target_stage: PipelineStage | None = None,
                stop_at: PipelineStage | None = None) -> CompilationResult:
        """Run the full compilation pipeline."""
        self.graph = graph
        self.diagnostics = []
        self.generated_files = []
        self._artifacts = {"motion": [], "gesture": [], "haptic": [], "accessibility": [], "screens": []}

        def _maybe_run(stage, fn):
            if target_stage is not None and stage != target_stage:
                self._info(stage, f'Skipped (targeting {target_stage.name})')
                return
            fn()
            if stop_at is not None and stage == stop_at:
                raise _StopAfter(stage)

        try:
            _maybe_run(PipelineStage.DEPENDENCY_RESOLUTION, self._stage_dependency_resolution)
            _maybe_run(PipelineStage.CONSTRAINT_VALIDATION, self._stage_constraint_validation)
            _maybe_run(PipelineStage.AGENT_PLANNING, self._stage_agent_planning)
            _maybe_run(PipelineStage.MOTION_COMPILATION, self._stage_motion_compilation)
            _maybe_run(PipelineStage.GESTURE_COMPILATION, self._stage_gesture_compilation)
            _maybe_run(PipelineStage.HAPTIC_COMPILATION, self._stage_haptic_compilation)
            _maybe_run(PipelineStage.ACCESSIBILITY_COMPILATION, self._stage_accessibility_compilation)
            _maybe_run(PipelineStage.SCREEN_COMPILATION, self._stage_screen_compilation)
            _maybe_run(PipelineStage.PERFORMANCE_OPTIMIZATION, self._stage_performance_optimization)
            _maybe_run(PipelineStage.CODE_GENERATION, lambda: self._stage_write_output(output_dir))
        except _StopAfter:
            pass
        except CompilationError as e:
            self.diagnostics.append(
                CompilationDiagnostic(stage=e.stage, level="error", message=str(e))
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
            self._info(PipelineStage.DEPENDENCY_RESOLUTION,
                       f"Resolved {len(order)} nodes in dependency order.")
        except Exception as e:
            raise CompilationError(
                PipelineStage.DEPENDENCY_RESOLUTION, f"Dependency cycle or missing node: {e}"
            )

    def _stage_constraint_validation(self) -> None:
        for node_id, node in self.graph.nodes.items():
            if node.node_type == NodeType.ACCESSIBILITY:
                min_target = node.constraints.get("min_touch_target", 0)
                if min_target < 44:
                    self._error(PipelineStage.CONSTRAINT_VALIDATION,
                                f"Touch target {min_target}pt < 44pt minimum.",
                                node_id, "Increase min_touch_target to at least 44.")
            if node.node_type == NodeType.MOTION:
                if not node.constraints.get("must_respect_reduced_motion"):
                    self._warning(PipelineStage.CONSTRAINT_VALIDATION,
                                  f"Motion node should respect reduced motion.",
                                  node_id)
                frame_budget = node.constraints.get("frame_budget_ms", 99)
                if frame_budget > 16:
                    self._warning(PipelineStage.CONSTRAINT_VALIDATION,
                                  f"Frame budget {frame_budget}ms exceeds 16ms target.",
                                  node_id)
        self._info(PipelineStage.CONSTRAINT_VALIDATION, "Constraint validation complete.")

    def _stage_agent_planning(self) -> None:
        agent_nodes = self.graph.find_by_type(NodeType.AGENT)
        self._info(PipelineStage.AGENT_PLANNING,
                   f"Planning execution for {len(agent_nodes)} agents.")

    def _stage_motion_compilation(self) -> None:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from generators.motion.motion_compiler import compile_motion, load_motion_patterns

        # Load pattern registry from project knowledge dir
        pattern_registry = {}
        for try_path in [Path("knowledge/motion/motion-patterns.json"),
                         Path.cwd() / "knowledge/motion/motion-patterns.json"]:
            if try_path.exists():
                try:
                    pattern_registry = load_motion_patterns(str(try_path))
                    self._info(PipelineStage.MOTION_COMPILATION,
                               f"Loaded {len(pattern_registry.get('patterns', {}))} motion patterns")
                    break
                except Exception as ex:
                    self._warning(PipelineStage.MOTION_COMPILATION,
                                  f"Failed to load patterns from {try_path}: {ex}")
        if not pattern_registry:
            self._warning(PipelineStage.MOTION_COMPILATION,
                          "No motion pattern registry found — all animations fall back to FadeIn")

        motion_nodes = self.graph.find_by_type(NodeType.MOTION)
        compiled = 0
        for node in motion_nodes:
            try:
                code = compile_motion(node.metadata, pattern_registry)
                self._artifacts["motion"].append((node.id, code))
                compiled += 1
            except Exception as e:
                self._warning(PipelineStage.MOTION_COMPILATION,
                              f"Failed to compile motion for {node.id}: {e}", node.id)
        self._info(PipelineStage.MOTION_COMPILATION,
                   f"Compiled {compiled}/{len(motion_nodes)} motion definitions.")

    def _stage_gesture_compilation(self) -> None:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from generators.motion.motion_compiler import compile_gesture

        gesture_nodes = self.graph.find_by_type(NodeType.GESTURE)
        compiled = 0
        for node in gesture_nodes:
            if not node.constraints.get("must_define_conflict_resolution"):
                self._warning(PipelineStage.GESTURE_COMPILATION,
                              "Gesture missing conflict resolution strategy.", node.id)
            try:
                code = compile_gesture(node.metadata)
                self._artifacts["gesture"].append((node.id, code))
                compiled += 1
            except Exception as e:
                self._warning(PipelineStage.GESTURE_COMPILATION,
                              f"Failed: {e}", node.id)
        self._info(PipelineStage.GESTURE_COMPILATION,
                   f"Compiled {compiled}/{len(gesture_nodes)} gesture definitions.")

    def _stage_haptic_compilation(self) -> None:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from generators.haptic.haptic_compiler import compile_haptics

        haptic_nodes = self.graph.find_by_type(NodeType.HAPTIC)
        compiled = 0
        for node in haptic_nodes:
            try:
                code = compile_haptics(node.metadata)
                self._artifacts["haptic"].append((node.id, code))
                compiled += 1
            except Exception as e:
                self._warning(PipelineStage.HAPTIC_COMPILATION,
                              f"Failed: {e}", node.id)
        self._info(PipelineStage.HAPTIC_COMPILATION,
                   f"Compiled {compiled}/{len(haptic_nodes)} haptic definitions.")

    def _stage_accessibility_compilation(self) -> None:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from generators.haptic.haptic_compiler import compile_accessibility

        a11y_nodes = self.graph.find_by_type(NodeType.ACCESSIBILITY)
        compiled = 0
        for node in a11y_nodes:
            try:
                code = compile_accessibility(node.metadata)
                self._artifacts["accessibility"].append((node.id, code))
                compiled += 1
            except Exception as e:
                self._warning(PipelineStage.ACCESSIBILITY_COMPILATION,
                              f"Failed: {e}", node.id)
        self._info(PipelineStage.ACCESSIBILITY_COMPILATION,
                   f"Compiled {compiled}/{len(a11y_nodes)} accessibility definitions.")


    def _stage_screen_compilation(self) -> None:
        """Compose screen-level React Native components from constituent artifacts."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from generators.screen.screen_compiler import compile_screen

        screen_nodes = self.graph.find_by_type(NodeType.SCREEN)
        compiled = 0
        for node in screen_nodes:
            try:
                code = compile_screen(
                    screen_id=node.id,
                    screen_meta=node.metadata,
                    artifacts=self._artifacts,
                    all_nodes=self.graph.nodes,
                    edges=self.graph.edges,
                )
                self._artifacts["screens"].append((node.id, code))
                compiled += 1
            except Exception as e:
                self._warning(
                    PipelineStage.SCREEN_COMPILATION,
                    f"Failed to compile screen {node.id}: {e}",
                    node.id,
                )
        self._info(
            PipelineStage.SCREEN_COMPILATION,
            f"Compiled {compiled}/{len(screen_nodes)} screens."
        )

    def _stage_performance_optimization(self) -> None:
        self._info(PipelineStage.PERFORMANCE_OPTIMIZATION,
                   "Running performance optimization passes.")

    def _stage_write_output(self, output_dir: Path | None) -> None:
        if not output_dir:
            output_dir = Path("features")
        base = output_dir

        folders = {
            "motion": base / "motion",
            "gesture": base / "gestures",
            "haptic": base / "haptics",
            "accessibility": base / "accessibility",
            "screens": base / "screens",
        }
        for d in folders.values():
            d.mkdir(parents=True, exist_ok=True)

        total = 0
        for kind, artifacts in self._artifacts.items():
            folder = folders.get(kind, base)
            for node_id, code in artifacts:
                safe_id = node_id.replace(":", "-")
                ext = ".tsx" if kind != "accessibility" else ".ts"
                path = folder / f"{safe_id}{ext}"
                path.write_text(code, encoding="utf-8")
                self.generated_files.append(path)
                total += 1

        self._info(PipelineStage.CODE_GENERATION,
                   f"Generated {total} files → {output_dir}.")

    def _error(self, stage: PipelineStage, message: str, node_id: str = "",
               suggestion: str = "") -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="error", message=message,
                                  node_id=node_id, suggestion=suggestion)
        )

    def _warning(self, stage: PipelineStage, message: str, node_id: str = "") -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="warning", message=message,
                                  node_id=node_id)
        )

    def _info(self, stage: PipelineStage, message: str) -> None:
        self.diagnostics.append(
            CompilationDiagnostic(stage=stage, level="info", message=message)
        )


class CompilationError(Exception):
    def __init__(self, stage: PipelineStage, message: str):
        self.stage = stage
        super().__init__(f"[{stage.name}] {message}")
