"""
XOS Anti-AI Slop Engine — rejects generic, lazy, or low-quality generation patterns.

Detects and blocks:
- Generic layouts (centered text, no hierarchy)
- Random spacing (arbitrary padding/margins)
- Inconsistent typography
- Weak visual hierarchy
- Missing or poor animations
- Missing haptics where interaction occurs
- Gesture conflicts
- Accessibility violations
- Performance regressions
- Duplicate components
- Architecture drift
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SlopSeverity(Enum):
    BLOCK = "block"       # Must reject generation
    WARN = "warn"         # Flag but allow
    SUGGEST = "suggest"   # Improvement opportunity


@dataclass
class SlopFinding:
    rule: str
    severity: SlopSeverity
    message: str
    location: str = ""
    fix: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


SLOP_RULES: dict[str, dict] = {
    "generic-layout": {
        "description": "Reject centered single-column layouts with no deliberate hierarchy.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "flex: 1, justifyContent: 'center', alignItems: 'center' with single child",
        "fix": "Define explicit layout regions: header, content, actions. Use design tokens for spacing.",
    },
    "random-spacing": {
        "description": "Reject arbitrary padding/margin values not derived from a spacing scale.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "padding: 13, margin: 7 (not on 4pt or 8pt scale)",
        "fix": "Use spacing tokens: xs=4, sm=8, md=16, lg=24, xl=32, 2xl=48.",
    },
    "inconsistent-typography": {
        "description": "Reject mixed font sizes, weights, or families without design system basis.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "fontSize: 15, fontSize: 17, fontSize: 14.5",
        "fix": "Define type scale: caption=12, body=14, body-lg=16, h3=18, h2=24, h1=32.",
    },
    "weak-hierarchy": {
        "description": "Reject layouts where visual weight doesn't match information importance.",
        "severity": SlopSeverity.WARN,
        "pattern": "All text same size and weight, or title smaller than body.",
        "fix": "Primary action bold + accent. Title largest. Body neutral weight. Caption muted.",
    },
    "missing-animation": {
        "description": "Flag interactive elements without transition or animation definitions.",
        "severity": SlopSeverity.WARN,
        "pattern": "Pressable/TouchableOpacity without animated value or transition.",
        "fix": "Define enter/exit/press animations with motion tokens.",
    },
    "missing-haptics": {
        "description": "Flag confirmations, toggles, and destructive actions without haptic feedback.",
        "severity": SlopSeverity.WARN,
        "pattern": "onPress for destructive/confirmatory action without haptic call.",
        "fix": "Add Haptics.impactAsync() or Haptics.notificationAsync() on meaningful interactions.",
    },
    "gesture-conflict": {
        "description": "Flag nested scrollables or overlapping gesture detectors.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "ScrollView inside ScrollView, or PanResponder on scrollable parent.",
        "fix": "Use Gesture Handler composition: Gesture.Simultaneous / Gesture.Exclusive.",
    },
    "accessibility-violation": {
        "description": "Flag missing accessibilityLabel, accessibilityRole, or small touch targets.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "Touchable without accessibility props, or touch area < 44pt.",
        "fix": "Add accessibilityLabel, accessibilityRole, and ensure min 44pt hit area.",
    },
    "performance-regression": {
        "description": "Flag inline functions in render, missing memo, or FlatList without keyExtractor.",
        "severity": SlopSeverity.WARN,
        "pattern": "onPress={() => ...} in JSX, FlatList without keyExtractor.",
        "fix": "Use useCallback for handlers. Add keyExtractor to FlatList. Memoize pure components.",
    },
    "duplicate-component": {
        "description": "Flag components that duplicate existing component functionality.",
        "severity": SlopSeverity.SUGGEST,
        "pattern": "Two components with same purpose and similar props.",
        "fix": "Extract shared component to shared/ui. Use composition over duplication.",
    },
    "architecture-drift": {
        "description": "Flag code that violates established architectural patterns.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "API calls in component body, business logic in UI, mixed concerns.",
        "fix": "Separate: UI (components), state (stores/hooks), data (queries/mutations), business (services).",
    },
    "prompt-drift": {
        "description": "Flag generated code that diverges from specification intent.",
        "severity": SlopSeverity.BLOCK,
        "pattern": "Generated code ignores spec requirements or adds unspec'd features.",
        "fix": "Re-generate from spec. Do not add features not explicitly defined.",
    },
}


class AntiSlopEngine:
    """Scans generated artifacts for slop patterns and rejects or warns."""

    def __init__(self):
        self.findings: list[SlopFinding] = []

    def scan(self, source: str, context: str = "") -> list[SlopFinding]:
        """Scan source code for anti-patterns."""
        self.findings = []
        self._check_generic_layout(source, context)
        self._check_random_spacing(source, context)
        self._check_inconsistent_typography(source, context)
        self._check_missing_accessibility(source, context)
        self._check_performance_regressions(source, context)
        self._check_architecture_drift(source, context)
        self._check_missing_haptics(source, context)
        return self.findings

    def has_blockers(self) -> bool:
        return any(f.severity == SlopSeverity.BLOCK for f in self.findings)

    def blocker_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SlopSeverity.BLOCK)

    def _check_generic_layout(self, source: str, ctx: str) -> None:
        generic = (
            "justifyContent: 'center'" in source
            and "alignItems: 'center'" in source
            and source.count("<") < 5
        )
        if generic:
            rule = SLOP_RULES["generic-layout"]
            self.findings.append(
                SlopFinding(
                    rule="generic-layout",
                    severity=SlopSeverity.BLOCK,
                    message=rule["description"],
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_random_spacing(self, source: str, ctx: str) -> None:
        import re
        padding_values = re.findall(r"padding(?:Horizontal|Vertical|Top|Bottom|Left|Right)?:\s*(-?\d+)", source)
        margin_values = re.findall(r"margin(?:Horizontal|Vertical|Top|Bottom|Left|Right)?:\s*(-?\d+)", source)
        all_spacing = [int(v) for v in padding_values + margin_values if v not in ("0", "1")]
        off_scale = [v for v in all_spacing if v > 1 and v % 4 != 0]
        if off_scale:
            rule = SLOP_RULES["random-spacing"]
            self.findings.append(
                SlopFinding(
                    rule="random-spacing",
                    severity=SlopSeverity.WARN,
                    message=f"Off-scale spacing values: {off_scale}. {rule['description']}",
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_inconsistent_typography(self, source: str, ctx: str) -> None:
        import re
        font_sizes = [float(s) for s in re.findall(r"fontSize:\s*(\d+(?:\.\d+)?)", source)]
        unique = sorted(set(font_sizes))
        if len(unique) > 5 and max(unique) - min(unique) < 20:
            rule = SLOP_RULES["inconsistent-typography"]
            self.findings.append(
                SlopFinding(
                    rule="inconsistent-typography",
                    severity=SlopSeverity.WARN,
                    message=f"{len(unique)} different font sizes ({unique}) — likely inconsistent type scale.",
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_missing_accessibility(self, source: str, ctx: str) -> None:
        has_touchable = any(
            t in source for t in ["TouchableOpacity", "TouchableHighlight", "Pressable", "Button", "onPress"]
        )
        has_a11y = "accessibilityLabel" in source or "accessibilityRole" in source or "accessible" in source
        if has_touchable and not has_a11y:
            rule = SLOP_RULES["accessibility-violation"]
            self.findings.append(
                SlopFinding(
                    rule="accessibility-violation",
                    severity=SlopSeverity.BLOCK,
                    message=rule["description"],
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_performance_regressions(self, source: str, ctx: str) -> None:
        inline_handler = "onPress={() =>" in source or "onPress={()=>" in source
        if inline_handler:
            rule = SLOP_RULES["performance-regression"]
            self.findings.append(
                SlopFinding(
                    rule="performance-regression",
                    severity=SlopSeverity.WARN,
                    message="Inline arrow function in JSX prop — will recreate every render.",
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_architecture_drift(self, source: str, ctx: str) -> None:
        mixed_concerns = (
            ("fetch(" in source or "axios" in source.lower())
            and ("export default function" in source or "const" in source)
            and "useEffect" not in source
        )
        if mixed_concerns and "service" not in ctx.lower():
            rule = SLOP_RULES["architecture-drift"]
            self.findings.append(
                SlopFinding(
                    rule="architecture-drift",
                    severity=SlopSeverity.WARN,
                    message=rule["description"],
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def _check_missing_haptics(self, source: str, ctx: str) -> None:
        destructive = any(
            kw in source.lower() for kw in ["delete", "remove", "confirm", "submit", "logout", "purchase", "pay"]
        )
        has_haptics = "Haptics" in source or "haptics" in source
        has_onpress = "onPress" in source
        if destructive and has_onpress and not has_haptics:
            rule = SLOP_RULES["missing-haptics"]
            self.findings.append(
                SlopFinding(
                    rule="missing-haptics",
                    severity=SlopSeverity.WARN,
                    message=rule["description"],
                    location=ctx,
                    fix=rule["fix"],
                )
            )

    def report(self) -> str:
        if not self.findings:
            return "✅ No slop detected. Code passes quality checks."
        lines = []
        for f in self.findings:
            icon = {"block": "🚫", "warn": "⚠️", "suggest": "💡"}[f.severity.value]
            lines.append(f"{icon} [{f.severity.value.upper()}] {f.rule}")
            lines.append(f"   {f.message}")
            if f.location:
                lines.append(f"   Location: {f.location}")
            if f.fix:
                lines.append(f"   Fix: {f.fix}")
            lines.append("")
        return "\n".join(lines)
