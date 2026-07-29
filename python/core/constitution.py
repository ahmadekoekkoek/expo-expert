"""XOS Constitution Engine — project-level rules enforced across all agents."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class RuleSeverity(str, Enum):
    BLOCK = "block"; WARN = "warn"; INFO = "info"

@dataclass
class ConstitutionalRule:
    id: str; category: str; description: str; severity: RuleSeverity
    check: str; fix: str = ""; applies_to: list[str] = field(default_factory=lambda: ["*"])
    def to_dict(self): return {"id":self.id,"category":self.category,"description":self.description,"severity":self.severity.value,"check":self.check,"fix":self.fix,"applies_to":self.applies_to}

@dataclass
class ConstitutionViolation:
    rule_id: str; category: str; severity: RuleSeverity; message: str; fix: str; agent: str = ""; node_id: str = ""

class Constitution:
    def __init__(self, name: str = "default"):
        self.name = name; self.rules: dict[str, ConstitutionalRule] = {}
        self._load_defaults()

    def _load_defaults(self):
        defaults = [
            ConstitutionalRule("C001","architecture","Every screen must have a specification node in the experience graph",RuleSeverity.BLOCK,"validate_screen_has_spec","Create a spec in specs/"),
            ConstitutionalRule("C002","architecture","No circular dependencies between features",RuleSeverity.BLOCK,"validate_no_circular_deps","Break cycles"),
            ConstitutionalRule("C003","design","All spacing must use design token scale (4,8,16,24,32,48)",RuleSeverity.BLOCK,"validate_spacing_scale","Use nearest design token"),
            ConstitutionalRule("C004","design","All colors must reference design tokens, not hardcoded hex",RuleSeverity.BLOCK,"validate_color_tokens","Use semantic color tokens"),
            ConstitutionalRule("C005","motion","Every animation must define a reduced-motion fallback",RuleSeverity.BLOCK,"validate_reduced_motion_fallback","Add reducedMotionFallback"),
            ConstitutionalRule("C006","motion","No animation may exceed 16ms frame budget on JS thread",RuleSeverity.BLOCK,"validate_frame_budget","Use Reanimated worklet"),
            ConstitutionalRule("C007","gesture","Every interactive element must have haptic feedback defined",RuleSeverity.BLOCK,"validate_haptic_coverage","Add haptic pattern to gesture node"),
            ConstitutionalRule("C008","accessibility","All touch targets must be at least 44pt",RuleSeverity.BLOCK,"validate_touch_targets","Increase to >= 44pt"),
            ConstitutionalRule("C009","accessibility","Every screen must have a semantic heading",RuleSeverity.BLOCK,"validate_semantic_heading","Add accessibilityRole header"),
            ConstitutionalRule("C010","performance","All scrollable lists must use FlashList",RuleSeverity.BLOCK,"validate_flashlist_usage","Replace with @shopify/flash-list"),
            ConstitutionalRule("C011","quality","No generated code may contain TODO or FIXME",RuleSeverity.WARN,"validate_no_todos","Resolve or convert to spec"),
            ConstitutionalRule("C012","quality","Every feature must have at least one test",RuleSeverity.WARN,"validate_test_coverage","Add test node to graph"),
        ]
        for rule in defaults: self.add_rule(rule)

    def add_rule(self, rule: ConstitutionalRule): self.rules[rule.id] = rule

    def validate(self, context: dict[str, Any]) -> list[ConstitutionViolation]:
        violations = []
        agent = context.get("agent",""); node_id = context.get("node_id","")
        for rule in self.rules.values():
            if not self._rule_applies(rule, agent): continue
            check_fn = getattr(self, rule.check, None)
            if check_fn and check_fn(context):
                violations.append(ConstitutionViolation(rule.id,rule.category,rule.severity,rule.description,rule.fix,agent,node_id))
        return violations

    def _rule_applies(self, rule, agent): return "*" in rule.applies_to or agent in rule.applies_to

    def validate_screen_has_spec(self,ctx): return ctx.get("node_kind")=="screen" and not ctx.get("has_spec",True)
    def validate_no_circular_deps(self,ctx): return ctx.get("circular_deps_detected",False)
    def validate_spacing_scale(self,ctx):
        allowed=ctx.get("spacing_scale",{4,8,16,24,32,48}); values=ctx.get("spacing_values",[])
        return any(v not in allowed for v in values)
    def validate_color_tokens(self,ctx): return ctx.get("hardcoded_colors_detected",False)
    def validate_reduced_motion_fallback(self,ctx): return ctx.get("missing_reduced_motion",False)
    def validate_frame_budget(self,ctx): return ctx.get("frame_budget_exceeded",False)
    def validate_haptic_coverage(self,ctx): return ctx.get("missing_haptics",False)
    def validate_touch_targets(self,ctx): return ctx.get("touch_targets_below_44",False)
    def validate_semantic_heading(self,ctx): return ctx.get("missing_semantic_heading",False)
    def validate_flashlist_usage(self,ctx): return ctx.get("uses_flatlist",False)
    def validate_no_todos(self,ctx): return ctx.get("has_todos",False)
    def validate_test_coverage(self,ctx): return ctx.get("has_tests") is False

    def to_dict(self): return {"name":self.name,"rules":{rid:r.to_dict() for rid,r in self.rules.items()}}
    def save(self, path):
        import json; from pathlib import Path
        Path(path).write_text(json.dumps(self.to_dict(),indent=2))

    @classmethod
    def load(cls, path):
        import json; from pathlib import Path
        data = json.loads(Path(path).read_text()); c = cls(name=data["name"])
        for rid, rd in data.get("rules",{}).items():
            rule = ConstitutionalRule(id=rd["id"],category=rd["category"],description=rd["description"],severity=RuleSeverity(rd["severity"]),check=rd["check"],fix=rd.get("fix",""),applies_to=rd.get("applies_to",["*"]))
            c.rules[rid] = rule
        return c


    @classmethod
    def from_json_file(cls, path: str) -> "Constitution":
        """Load constitution from a JSON file, creating default if missing."""
        import json, os
        if os.path.exists(path):
            data = json.load(open(path))
            const = cls(name=data.get("name", "xos-constitution"))
            for rid, rd in data.get("rules", {}).items():
                rule = ConstitutionalRule(
                    id=rid,
                    category=rd.get("category", "general"),
                    description=rd.get("description", ""),
                    severity=RuleSeverity(rd.get("severity", "warning")),
                    check=rd.get("check", ""),
                    fix=rd.get("fix", ""),
                    applies_to=rd.get("applies_to", ["*"]),
                )
                const.rules[rid] = rule
            return const
        const = cls()
        const.save(path)
        return const

    def to_markdown(self) -> str:
        """Render constitution as a markdown document."""
        lines = [f"# Constitution: {self.name}", "", "## Rules", ""]
        for rule in self.rules.values():
            emoji = {"block": "🚫", "warn": "⚠️", "info": "ℹ️"}.get(rule.severity.value, "")
            lines.append(f"### {emoji} {rule.id}: {rule.description}")
            lines.append(f"- **Severity**: {rule.severity.value}")
            lines.append(f"- **Category**: {rule.category}")
            lines.append(f"- **Check**: `{rule.check}`")
            if rule.fix:
                lines.append(f"- **Fix**: {rule.fix}")
            if rule.applies_to and rule.applies_to != ["*"]:
                lines.append(f"- **Applies to**: {", ".join(rule.applies_to)}")
            lines.append("")
        return "\n".join(lines)


DEFAULT_CONSTITUTION = Constitution()


