"""
XOS Agent Registry — every agent owns exactly one domain.

Agents define mission, inputs, outputs, skills, tools, and validation rules.
Orchestrated by `python/agents/agent_runtime.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence


# ──────────────────────────────────────────────────────────────────

@dataclass
class AgentDefinition:
    name: str
    mission: str
    domain: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    mcp_access: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    retry_strategy: str = "exponential_backoff"


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    output: Any = None
    diagnostics: List[str] = field(default_factory=list)


# ── built-in agent catalog ───────────────────────────────────────

AGENT_CATALOG: Dict[str, AgentDefinition] = {
    "ChiefArchitect": AgentDefinition(
        name="ChiefArchitect",
        mission="Ensure architectural integrity and deterministic design",
        domain="architecture",
        skills=["ReviewArchitecture", "DesignSystem"],
        tools=["ExperienceGraph", "KnowledgeGraph"],
    ),
    "UXEngineer": AgentDefinition(
        name="UXEngineer",
        mission="Shape interaction patterns and information architecture",
        domain="ux",
        skills=["ReviewUX", "GenerateScreen", "GenerateComponent", "GenerateNavigation"],
        tools=["ExperienceGraph", "DesignTokens"],
    ),
    "MotionEngineer": AgentDefinition(
        name="MotionEngineer",
        mission="Orchestrate every animation with physics, timing, and intent",
        domain="motion",
        skills=["GenerateMotion", "ReviewMotion", "OptimizeAnimations"],
        tools=["MotionCompiler"],
        validation_rules=["frame_budget_16ms"],
    ),
    "GestureEngineer": AgentDefinition(
        name="GestureEngineer",
        mission="Define and de-conflict every gesture across the surface",
        domain="gesture",
        skills=["GenerateGesture", "ReviewGestures"],
        tools=["GestureCompiler"],
        validation_rules=["no_priority_collisions"],
    ),
    "HapticEngineer": AgentDefinition(
        name="HapticEngineer",
        mission="Anchor every meaningful interaction with haptic feedback",
        domain="haptic",
        skills=["GenerateHaptic", "ReviewHaptics"],
        tools=["HapticCompiler"],
    ),
    "AccessibilityEngineer": AgentDefinition(
        name="AccessibilityEngineer",
        mission="Ensure every pixel and gesture is accessible to all",
        domain="accessibility",
        skills=["GenerateAccessibility", "ReviewAccessibility"],
        tools=["A11yCompiler"],
        validation_rules=["wcag_aa_contrast", "dynamic_type", "screen_reader_labels"],
    ),
    "PerformanceEngineer": AgentDefinition(
        name="PerformanceEngineer",
        mission="Ship buttery-smooth 60 FPS on every device",
        domain="performance",
        skills=["GeneratePerformance", "ReviewPerformance", "OptimizeAnimations"],
        tools=["Profiler", "FlashList"],
        validation_rules=["60fps_target"],
    ),
    "ReactNativeEngineer": AgentDefinition(
        name="ReactNativeEngineer",
        mission="Render pixel-perfect, idiomatic React Native code",
        domain="react_native",
        skills=["GenerateComponent", "GenerateScreen", "RefactorCode"],
        tools=["TypeScript", "ReactNative"],
    ),
    "ExpoEngineer": AgentDefinition(
        name="ExpoEngineer",
        mission="Master the Expo platform — routing, tooling, EAS",
        domain="expo",
        skills=["GenerateNavigation", "RefactorCode"],
        tools=["ExpoRouter", "EAS"],
    ),
    "BackendEngineer": AgentDefinition(
        name="BackendEngineer",
        mission="Connect the client to data with Supabase, Firebase, or tRPC",
        domain="backend",
        skills=["GenerateDataLayer"],
        tools=["Supabase", "Firebase", "tRPC"],
    ),
    "TestingEngineer": AgentDefinition(
        name="TestingEngineer",
        mission="Guarantee every interaction is verified before shipping",
        domain="testing",
        skills=["GenerateTests"],
        tools=["Jest", "Detox", "Maestro"],
    ),
    "DocumentationEngineer": AgentDefinition(
        name="DocumentationEngineer",
        mission="Produce crystal-clear docs from the graph itself",
        domain="docs",
        skills=["GenerateDocumentation"],
        tools=["ExperienceGraph"],
    ),
    "ReleaseEngineer": AgentDefinition(
        name="ReleaseEngineer",
        mission="Ship deterministic builds via EAS and CI",
        domain="release",
        skills=["ReleaseBuild"],
        tools=["EAS", "GitHubActions"],
    ),
    "MCPEngineer": AgentDefinition(
        name="MCPEngineer",
        mission="Wire every external capability through the MCP layer",
        domain="mcp",
        skills=["GenerateMCPInterface"],
        tools=["MCPRegistry"],
    ),
    "PythonAutomationEngineer": AgentDefinition(
        name="PythonAutomationEngineer",
        mission="Orchestrate the entire platform via Python workflows",
        domain="automation",
        skills=["GenerateWorkflow"],
        tools=["Python", "GraphEngine"],
    ),
    "PowerShellEngineer": AgentDefinition(
        name="PowerShellEngineer",
        mission="Automate the host environment — bootstrapping, builds, diagnostics",
        domain="host_automation",
        skills=["GeneratePowerShell"],
        tools=["PowerShell", "ExpoCLI", "AndroidSDK", "XcodeCLI"],
    ),
    "DesignSystemEngineer": AgentDefinition(
        name="DesignSystemEngineer",
        mission="Curate and enforce the design token system across all screens",
        domain="design_system",
        skills=["ReviewDesignTokens", "GenerateTheme"],
        tools=["DesignTokens", "NativeWind"],
    ),
}
