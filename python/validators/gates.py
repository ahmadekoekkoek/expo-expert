"""
Quality Gate Pipeline — validates generated artifacts against all constraints.

Generation fails if any gate fails.  Each gate produces explicit diagnostics
so the operator (human or agent) can fix the root cause deterministically.

Gate order is intentional: cheaper checks first, expensive (e.g. compile) last.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List

from python.core.xos_logger import get_logger

logger = get_logger(__name__)


class GateSeverity(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class GateResult:
    gate: str
    severity: GateSeverity
    message: str = ""
    detail: Dict[str, Any] = field(default_factory=dict)


GateFn = Callable[[Dict[str, Any]], GateResult]


class QualityGatePipeline:
    def __init__(self) -> None:
        self._gates: List[GateFn] = []

    def register(self, gate: GateFn) -> None:
        self._gates.append(gate)

    def run(self, context: Dict[str, Any]) -> List[GateResult]:
        results: List[GateResult] = []
        fail_count = 0
        for gate_fn in self._gates:
            result = gate_fn(context)
            results.append(result)
            if result.severity == GateSeverity.FAIL:
                fail_count += 1
            logger.info("Gate '%s': %s — %s", result.gate, result.severity.value, result.message)
        if fail_count:
            logger.warning("Pipeline halted: %d/%d gates failed", fail_count, len(results))
        return results

    @property
    def passed(self) -> bool:
        return all(r.severity != GateSeverity.FAIL for r in self._results) if hasattr(self, "_results") else True

    def validate(self, context: Dict[str, Any]) -> bool:
        self._results = self.run(context)
        return self.passed
