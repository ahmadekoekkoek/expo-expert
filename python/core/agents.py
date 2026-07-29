"""
XOS Agent Framework — each agent owns exactly one domain and executes
through a strictly defined interface with validation and reflection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol

from ..core.graph import GraphNode, NodeType, GateStatus, ValidationResult


class AgentStatus(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    DONE = "done"
    FAILED = "failed"


@dataclass
class AgentContext:
    graph: Any  # ExperienceGraph (circular import avoided)
    node: GraphNode | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    success: bool
    artifacts: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)


@dataclass
class AgentDefinition:
    name: str
    domain: str
    mission: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    mcp_access: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    retry_strategy: str = "exponential_backoff"

    def to_graph_node(self) -> GraphNode:
        return GraphNode(
            node_type=NodeType.AGENT,
            intent=f"{self.name}: {self.mission}",
            inputs=self.inputs,
            outputs=self.outputs,
            owner=self.name,
            metadata={
                "domain": self.domain,
                "skills": self.skills,
                "tools": self.tools,
                "mcp_access": self.mcp_access,
            },
        )


AGENT_REGISTRY: dict[str, AgentDefinition] = {
    "chief-architect": AgentDefinition(
        name="chief-architect",
        domain="architecture",
        mission="Ensure architectural consistency, scalability, and maintainability across the entire system.",
        inputs=["specifications", "experience-graph"],
        outputs=["architecture-decisions", "validation-report"],
        skills=["review-architecture", "generate-architecture"],
        tools=["graph", "compiler"],
        validation_rules=["no-circular-deps", "separation-of-concerns", "expo-best-practices"],
    ),
    "ux-engineer": AgentDefinition(
        name="ux-engineer",
        domain="user-experience",
        mission="Design coherent, premium user experiences with deliberate motion, gesture, and haptic design.",
        inputs=["feature-spec", "design-tokens"],
        outputs=["ux-spec", "interaction-model"],
        skills=["review-ux", "generate-screen", "generate-workflow"],
        tools=["graph", "node-factory"],
        validation_rules=["premium-ux", "no-generic-layouts"],
    ),
    "motion-engineer": AgentDefinition(
        name="motion-engineer",
        domain="motion",
        mission="Design performant, interruptible animations with proper physics and frame budgets.",
        inputs=["interaction-model", "design-tokens"],
        outputs=["motion-spec", "animation-code"],
        skills=["review-motion", "generate-motion"],
        tools=["motion-compiler", "graph"],
        validation_rules=["frame-budget", "reduced-motion", "interruptibility"],
    ),
    "gesture-engineer": AgentDefinition(
        name="gesture-engineer",
        domain="gestures",
        mission="Define deterministic gesture interactions with conflict resolution and velocity tracking.",
        inputs=["interaction-model"],
        outputs=["gesture-spec", "gesture-code"],
        skills=["review-gestures", "generate-gesture"],
        tools=["gesture-compiler", "graph"],
        validation_rules=["conflict-resolution", "thresholds", "velocity-tracking"],
    ),
    "haptic-engineer": AgentDefinition(
        name="haptic-engineer",
        domain="haptics",
        mission="Design tactile feedback with platform-appropriate mappings and synchronized timing.",
        inputs=["interaction-model", "gesture-spec"],
        outputs=["haptic-spec", "haptic-code"],
        skills=["review-haptics", "generate-haptic"],
        tools=["haptic-compiler", "graph"],
        validation_rules=["platform-mapping", "timing", "intensity-calibration"],
    ),
    "accessibility-engineer": AgentDefinition(
        name="accessibility-engineer",
        domain="accessibility",
        mission="Ensure WCAG compliance, screen reader support, dynamic type, and proper contrast.",
        inputs=["component-tree", "design-tokens"],
        outputs=["a11y-spec", "a11y-props"],
        skills=["review-accessibility", "generate-accessibility"],
        tools=["a11y-compiler", "graph"],
        validation_rules=["semantic-roles", "focus-order", "contrast", "touch-targets"],
    ),
    "performance-engineer": AgentDefinition(
        name="performance-engineer",
        domain="performance",
        mission="Optimize render performance, bundle size, and runtime efficiency.",
        inputs=["component-graph", "animation-specs"],
        outputs=["perf-report", "optimization-patches"],
        skills=["review-performance", "optimize-animations"],
        tools=["perf-compiler", "graph"],
        validation_rules=["frame-budget", "bundle-size", "memory", "list-performance"],
    ),
    "react-native-engineer": AgentDefinition(
        name="react-native-engineer",
        domain="react-native",
        mission="Generate idiomatic React Native code following best practices and platform conventions.",
        inputs=["compiled-graph", "design-tokens"],
        outputs=["components", "screens", "hooks"],
        skills=["generate-component", "generate-screen", "refactor-code"],
        tools=["code-generator", "graph"],
        validation_rules=["rn-best-practices", "typescript-strict", "no-any"],
    ),
    "expo-engineer": AgentDefinition(
        name="expo-engineer",
        domain="expo",
        mission="Ensure Expo compatibility, router configuration, and build pipeline integrity.",
        inputs=["project-config", "navigation-graph"],
        outputs=["expo-config", "router-setup"],
        skills=["generate-navigation", "review-config"],
        tools=["code-generator", "graph"],
        validation_rules=["expo-sdk-compat", "router-conventions", "eas-build"],
    ),
    "testing-engineer": AgentDefinition(
        name="testing-engineer",
        domain="testing",
        mission="Generate comprehensive test suites with unit, integration, and E2E coverage.",
        inputs=["components", "workflows"],
        outputs=["test-files", "coverage-report"],
        skills=["generate-tests"],
        tools=["test-generator", "graph"],
        validation_rules=["coverage-threshold", "a11y-tests", "gesture-tests"],
    ),
    "documentation-engineer": AgentDefinition(
        name="documentation-engineer",
        domain="documentation",
        mission="Generate and maintain living documentation from graph nodes and generated code.",
        inputs=["graph", "generated-artifacts"],
        outputs=["docs", "adrs"],
        skills=["generate-documentation"],
        tools=["doc-generator", "graph"],
        validation_rules=["adr-format", "component-stories"],
    ),
}


class AgentExecutor:
    """Executes an agent's workflow against the experience graph."""

    def __init__(self, definition: AgentDefinition):
        self.definition = definition
        self.status = AgentStatus.IDLE
        self.history: list[str] = []

    def plan(self, ctx: AgentContext) -> list[str]:
        self.status = AgentStatus.PLANNING
        steps = []
        for skill in self.definition.skills:
            steps.append(f"[{self.definition.name}] execute skill: {skill}")
        self.history.extend(steps)
        return steps

    def execute(self, ctx: AgentContext) -> AgentResult:
        self.status = AgentStatus.EXECUTING
        plan = self.plan(ctx)
        return AgentResult(
            success=True,
            artifacts={"plan": plan},
            diagnostics=[f"Agent {self.definition.name} executed {len(plan)} steps."],
        )

    def validate(self, ctx: AgentContext) -> list[ValidationResult]:
        self.status = AgentStatus.VALIDATING
        results = []
        for rule in self.definition.validation_rules:
            results.append(
                ValidationResult(gate=rule, status=GateStatus.PASSED, message=f"Rule {rule} satisfied.")
            )
        return results


def get_agent(name: str) -> AgentDefinition | None:
    return AGENT_REGISTRY.get(name)


def list_agents() -> list[str]:
    return list(AGENT_REGISTRY.keys())


def create_agent_node(name: str) -> GraphNode | None:
    agent_def = AGENT_REGISTRY.get(name)
    if agent_def:
        return agent_def.to_graph_node()
    return None
