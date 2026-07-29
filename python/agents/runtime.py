"""
Agent Runtime — manages agent instances, their lifecycle, and MCP connections.

Each agent owns exactly one domain.  The runtime loads agent definitions,
validates skill compatibility, and provides a structured execution context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from python.core.xos_logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentDefinition:
    name: str
    domain: str
    mission: str = ""
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    mcp_access: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

    def validate_compatibility(self, available_mcps: List[str]) -> List[str]:
        missing_mcps = [m for m in self.mcp_access if m not in available_mcps]
        missing_tools = [t for t in self.tools if t not in []]
        issues: List[str] = [
            f"Missing MCP: {m}" for m in missing_mcps
        ]
        return issues


class AgentRuntime:
    """Registers agents and dispatches to them via Python workflows."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentDefinition] = {}
        self._mcp_registry: List[str] = []

    def register_agent(self, agent: AgentDefinition) -> None:
        self._agents[agent.name] = agent
        logger.info("Agent registered: %s [%s]", agent.name, agent.domain)

    def get(self, name: str) -> Optional[AgentDefinition]:
        return self._agents.get(name)

    def list_domains(self) -> List[str]:
        return sorted({a.domain for a in self._agents.values()})

    def register_mcp(self, name: str) -> None:
        self._mcp_registry.append(name)

    def validate_all(self) -> List[str]:
        issues: List[str] = []
        for agent in self._agents.values():
            issues.extend(agent.validate_compatibility(self._mcp_registry))
        return issues

    def create_execution_context(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        agent = self._agents.get(agent_name)
        if agent is None:
            return {"error": f"Unknown agent: {agent_name}"}
        return {
            "agent": agent.name,
            "domain": agent.domain,
            "mission": agent.mission,
            "task": task,
            "mcp_access": agent.mcp_access,
        }
