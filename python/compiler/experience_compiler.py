"""
Experience Compiler — the central pipeline that turns a specification
into a complete React Native + Expo application.

Never generates React Native code directly.  Always compiles
through every pipeline stage.  If validation fails at any stage,
the compiler halts and produces actionable diagnostics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from python.core.xos_logger import get_logger
from python.graph.knowledge import KnowledgeGraph
from python.validators.gates import GateResult, QualityGatePipeline

logger = get_logger(__name__)


class ExperienceCompiler:
    """Orchestrates the full specification-to-code pipeline."""

    STAGES: list[str] = [
        "load_specifications",
        "expand_knowledge_graph",
        "build_experience_graph",
        "resolve_dependencies",
        "validate_constraints",
        "plan_agents",
        "compile_motion",
        "compile_gestures",
        "compile_haptics",
        "compile_accessibility",
        "optimize_performance",
        "emit_react_native_code",
        "run_tests",
        "generate_documentation",
    ]

    def __init__(self, root: Path) -> None:
        self.root = root
        self.knowledge_graph = KnowledgeGraph(root)
        self.gates = QualityGatePipeline()
        self._results: Dict[str, Any] = {}
        self._stage_results: Dict[str, Any] = {}

        # register built-in gates
        from python.validators.builtin_gates import (
            gate_spec_validation,
            gate_architecture,
            gate_design,
            gate_motion,
            gate_gesture,
            gate_haptic,
            gate_accessibility,
            gate_performance,
            gate_security,
        )
        for g in [
            gate_spec_validation,
            gate_architecture,
            gate_design,
            gate_motion,
            gate_gesture,
            gate_haptic,
            gate_accessibility,
            gate_performance,
            gate_security,
        ]:
            self.gates.register(g)

    def compile(self, spec_path: Optional[str] = None) -> Dict[str, Any]:
        self.knowledge_graph.load()

        for stage in self.STAGES:
            logger.info("--- Compiler stage: %s ---", stage)
            stage_result = self._run_stage(stage, spec_path)
            if isinstance(stage_result, dict) and stage_result.get("halt"):
                self._results["status"] = "HALTED"
                self._results["failed_stage"] = stage
                self._results["diagnostics"] = stage_result.get("diagnostics", [])
                return self._results

            self._stage_results[stage] = stage_result

        gate_context = {"root": self.root, "stage_results": self._stage_results}
        gate_results: list[GateResult] = self.gates.run(gate_context)
        fails = [r for r in gate_results if r.severity.value == "fail"]
        self._results["status"] = "PASSED" if not fails else "FAILED"
        self._results["gate_results"] = [r.__dict__ for r in gate_results]
        self._results["stage_results"] = self._stage_results

        if not fails:
            self._results["generated_artifacts"] = self._stage_results.get("emit_react_native_code", [])
            self._results["documentation"] = self._stage_results.get("generate_documentation", [])

        return self._results

    def _run_stage(self, stage: str, spec_path: Optional[str]) -> Dict[str, Any]:
        method = getattr(self, f"stage_{stage}", None)
        if method is None:
            return {"status": "skipped", "reason": f"No handler for stage '{stage}'"}
        return method(spec_path)

    # ------------------------------------------------------------------
    # Stage handlers (stubs for now — real work dispatched to generators)
    # ------------------------------------------------------------------

    def stage_load_specifications(self, spec_path: Optional[str]) -> Dict[str, Any]:
        specs_dir = self.root / "specs"
        if spec_path:
            specs_dir = Path(spec_path)
        if not specs_dir.is_dir():
            return {"halt": True, "diagnostics": [f"Specs directory not found: {specs_dir}"]}
        spec_files = list(specs_dir.glob("*.json")) + list(specs_dir.glob("*.yaml"))
        return {"status": "ok", "spec_files": [str(f) for f in spec_files]}

    def stage_expand_knowledge_graph(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "entries": len(self.knowledge_graph._entries)}

    def stage_build_experience_graph(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "nodes": 0}

    def stage_resolve_dependencies(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok"}

    def stage_validate_constraints(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {"root": self.root}
        results = self.gates.run(ctx)
        failures = [r.message for r in results if r.severity.value == "fail"]
        if failures:
            return {"halt": True, "diagnostics": failures}
        return {"status": "ok"}

    def stage_plan_agents(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "plan": []}

    def stage_compile_motion(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "motion_tokens": []}

    def stage_compile_gestures(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "gesture_map": []}

    def stage_compile_haptics(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "haptic_map": []}

    def stage_compile_accessibility(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "a11y_map": []}

    def stage_optimize_performance(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "optimizations": []}

    def stage_emit_react_native_code(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "files": []}

    def stage_run_tests(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "tests": 0}

    def stage_generate_documentation(self, _spec_path: Optional[str]) -> Dict[str, Any]:
        return {"status": "ok", "docs": []}
