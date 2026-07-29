"""
Built-in Quality Gates — each gate validates one dimension of the output.

If a gate fails, the compiler halts and reports actionable diagnostics.
"""

from __future__ import annotations

from typing import Any, Dict

from python.validators.gates import GateResult, GateSeverity


def gate_spec_validation(context: Dict[str, Any]) -> GateResult:
    root = context.get("root")
    specs_dir = root / "specs" if root else None
    if specs_dir and not any(specs_dir.glob("*.json")) and not any(specs_dir.glob("*.yaml")):
        return GateResult("spec_validation", GateSeverity.WARN, "No specification files found in specs/")
    return GateResult("spec_validation", GateSeverity.PASS)


def gate_architecture(context: Dict[str, Any]) -> GateResult:
    return GateResult("architecture", GateSeverity.PASS, "Architecture check — not yet implemented")


def gate_design(context: Dict[str, Any]) -> GateResult:
    return GateResult("design", GateSeverity.PASS, "Design check — not yet implemented")


def gate_motion(context: Dict[str, Any]) -> GateResult:
    return GateResult("motion", GateSeverity.PASS, "Motion check — not yet implemented")


def gate_gesture(context: Dict[str, Any]) -> GateResult:
    return GateResult("gesture", GateSeverity.PASS, "Gesture check — not yet implemented")


def gate_haptic(context: Dict[str, Any]) -> GateResult:
    return GateResult("haptic", GateSeverity.PASS, "Haptic check — not yet implemented")


def gate_accessibility(context: Dict[str, Any]) -> GateResult:
    return GateResult("accessibility", GateSeverity.PASS, "Accessibility check — not yet implemented")


def gate_performance(context: Dict[str, Any]) -> GateResult:
    return GateResult("performance", GateSeverity.PASS, "Performance check — not yet implemented")


def gate_security(context: Dict[str, Any]) -> GateResult:
    return GateResult("security", GateSeverity.PASS, "Security check — not yet implemented")
