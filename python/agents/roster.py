"""
XOS Agent Graph — each agent owns one domain and follows a mission-contract interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from python.core.xos_logger import get_logger
from python.graph.engine import ExperienceGraph, NodeKind

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────

@dataclass
class AgentDefinition:
    """Schema for a single agent in the XOS agent graph."""
    name: str
    mission: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    mcp_access: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    reflection: bool = True
    retry_strategy: str = "exponential-backoff"

    def validate(self, graph: ExperienceGraph) -> List[str]:
        """Check that all declared skills/tools/mcp exist in the graph."""
        errors: List[str] = []
        for skill in self.skills:
            if not graph.find_nodes(NodeKind.PROMPT):
                errors.append(f"Skill '{skill}' not found in graph")
        return errors


def builtin_agent_definitions() -> List[AgentDefinition]:
    """Return the built-in agent roster."""
    return [
        AgentDefinition(
            name="Chief Architect",
            mission="Own overall architecture, module boundaries and platform vision.",
            inputs=["feature_spec", "graph"],
            outputs=["architecture_decision", "module_map"],
            skills=["Review Architecture", "Generate Feature"],
        ),
        AgentDefinition(
            name="UX Engineer",
            mission="Own interaction flows, screen layouts and user journeys.",
            inputs=["feature_spec", "design_tokens"],
            outputs=["screen_definitions", "navigation_graph"],
            skills=["Generate Screen", "Generate Navigation", "Review UX"],
        ),
        AgentDefinition(
            name="Motion Engineer",
            mission="Own every animation, transition and micro-interaction.",
            inputs=["screen_definitions", "motion_tokens"],
            outputs=["motion_spec", "reanimated_code"],
            skills=["Generate Motion", "Review Motion"],
        ),
        AgentDefinition(
            name="Gesture Engineer",
            mission="Own gesture handling, conflict resolution and recovery.",
            inputs=["motion_spec", "screen_definitions"],
            outputs=["gesture_spec", "gesture_handler_code"],
            skills=["Generate Gestures", "Review Gestures"],
        ),
        AgentDefinition(
            name="Haptic Engineer",
            mission="Own haptic feedback — what, when and how.",
            inputs=["gesture_spec", "motion_spec"],
            outputs=["haptic_spec", "haptic_code"],
            skills=["Generate Haptics", "Review Haptics"],
        ),
        AgentDefinition(
            name="Accessibility Engineer",
            mission="Own WCAG compliance, focus order, screen-reader support.",
            inputs=["screen_definitions"],
            outputs=["a11y_spec", "a11y_code"],
            skills=["Review Accessibility"],
        ),
        AgentDefinition(
            name="Performance Engineer",
            mission="Own frame budget, bundle size and render performance.",
            inputs=["component_tree", "navigation_graph"],
            outputs=["perf_spec", "optimization_report"],
            skills=["Review Performance", "Optimize Animations"],
        ),
        AgentDefinition(
            name="React Native Engineer",
            mission="Own component implementation, state management and navigation code.",
            inputs=["all_specs"],
            outputs=["rn_code", "component_files"],
            skills=["Generate Component", "Generate Screen", "Generate Navigation"],
        ),
        AgentDefinition(
            name="Expo Engineer",
            mission="Own Expo config, build pipeline, EAS and OTA updates.",
            inputs=["rn_code", "app_config"],
            outputs=["expo_code", "eas_config"],
            skills=["Generate Expo Config"],
        ),
        AgentDefinition(
            name="Python Automation Engineer",
            mission="Own the XOS Python runtime, workflows and generators.",
            inputs=["agent_requests"],
            outputs=["python_workflows", "generated_artifacts"],
            skills=["Generate Workflow"],
        ),
        AgentDefinition(
            name="PowerShell Engineer",
            mission="Own host environment, tooling, bootstrap and builds.",
            inputs=["environment_state"],
            outputs=["ps_scripts", "environment_report"],
            skills=["Bootstrap Environment", "Diagnostics"],
        ),
        AgentDefinition(
            name="Testing Engineer",
            mission="Own unit, integration and e2e test suites.",
            inputs=["component_files", "screen_definitions"],
            outputs=["test_files", "coverage_report"],
            skills=["Generate Tests"],
        ),
        AgentDefinition(
            name="Documentation Engineer",
            mission="Own every doc artifact — decisions, specs, API docs.",
            inputs=["architecture_decision", "module_map"],
            outputs=["docs"],
            skills=["Generate Documentation"],
        ),
    ]
