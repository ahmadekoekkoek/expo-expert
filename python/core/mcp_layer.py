"""
XOS MCP Layer — treat every external capability as an MCP server.

Agents interact only through MCP interfaces. Capabilities include:
- Filesystem, Git, GitHub, Terminal, Python, PowerShell
- Expo CLI, React Native CLI, Supabase, Firebase
- Testing (Playwright, Detox, Maestro), Figma, Notion, Linear, OpenAPI
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol


class MCPStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class MCPServer:
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    endpoint: str = ""
    status: MCPStatus = MCPStatus.UNKNOWN
    auth_required: bool = False
    tools: dict[str, dict] = field(default_factory=dict)

    def is_available(self) -> bool:
        return self.status == MCPStatus.AVAILABLE


@dataclass
class MCPTool:
    server: str
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    returns: str = "any"


MCP_REGISTRY: dict[str, MCPServer] = {
    "filesystem": MCPServer(
        name="filesystem",
        description="Read, write, and manage files on the local filesystem.",
        capabilities=["read", "write", "delete", "list", "watch", "stat"],
        status=MCPStatus.AVAILABLE,
        tools={
            "read_file": {"parameters": {"path": "string"}, "returns": "string"},
            "write_file": {"parameters": {"path": "string", "content": "string"}, "returns": "void"},
            "delete_file": {"parameters": {"path": "string"}, "returns": "void"},
            "list_directory": {"parameters": {"path": "string"}, "returns": "array"},
        },
    ),
    "git": MCPServer(
        name="git",
        description="Version control operations via Git.",
        capabilities=["status", "add", "commit", "push", "pull", "branch", "log", "diff"],
        status=MCPStatus.AVAILABLE,
        tools={
            "git_status": {"parameters": {}, "returns": "string"},
            "git_commit": {"parameters": {"message": "string", "files": "array"}, "returns": "string"},
            "git_push": {"parameters": {"remote": "string", "branch": "string"}, "returns": "string"},
        },
    ),
    "github": MCPServer(
        name="github",
        description="GitHub API — PRs, issues, actions, releases.",
        capabilities=["pr", "issue", "actions", "release", "repo"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "create_pr": {"parameters": {"title": "string", "body": "string", "base": "string", "head": "string"}, "returns": "string"},
            "create_issue": {"parameters": {"title": "string", "body": "string"}, "returns": "string"},
        },
    ),
    "terminal": MCPServer(
        name="terminal",
        description="Execute shell commands in the local environment.",
        capabilities=["execute", "spawn", "env"],
        status=MCPStatus.AVAILABLE,
        tools={
            "run_command": {"parameters": {"command": "string", "cwd": "string"}, "returns": "string"},
        },
    ),
    "python": MCPServer(
        name="python",
        description="Execute Python scripts and access Python runtime.",
        capabilities=["execute", "evaluate", "import"],
        status=MCPStatus.AVAILABLE,
        tools={
            "run_script": {"parameters": {"script": "string", "args": "array"}, "returns": "string"},
        },
    ),
    "powershell": MCPServer(
        name="powershell",
        description="Execute PowerShell scripts for Windows automation.",
        capabilities=["execute", "module", "env"],
        status=MCPStatus.AVAILABLE,
        tools={
            "run_script": {"parameters": {"script": "string", "args": "array"}, "returns": "string"},
        },
    ),
    "expo": MCPServer(
        name="expo",
        description="Expo CLI — build, run, and manage Expo projects.",
        capabilities=["start", "build", "publish", "doctor", "config"],
        status=MCPStatus.AVAILABLE,
        tools={
            "expo_start": {"parameters": {"platform": "string"}, "returns": "string"},
            "expo_build": {"parameters": {"platform": "string", "profile": "string"}, "returns": "string"},
            "expo_doctor": {"parameters": {}, "returns": "string"},
        },
    ),
    "supabase": MCPServer(
        name="supabase",
        description="Supabase backend — auth, database, storage, realtime.",
        capabilities=["auth", "db", "storage", "realtime", "edge-functions"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "query": {"parameters": {"sql": "string"}, "returns": "array"},
            "auth_signup": {"parameters": {"email": "string", "password": "string"}, "returns": "object"},
        },
    ),
    "firebase": MCPServer(
        name="firebase",
        description="Firebase — auth, firestore, storage, cloud functions.",
        capabilities=["auth", "firestore", "storage", "functions", "analytics"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "firestore_query": {"parameters": {"collection": "string", "where": "array"}, "returns": "array"},
        },
    ),
    "figma": MCPServer(
        name="figma",
        description="Figma API — import designs, extract tokens, generate specs.",
        capabilities=["file", "components", "styles", "images"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "get_file": {"parameters": {"file_key": "string"}, "returns": "object"},
            "get_components": {"parameters": {"file_key": "string"}, "returns": "array"},
            "get_styles": {"parameters": {"file_key": "string"}, "returns": "array"},
        },
    ),
    "notion": MCPServer(
        name="notion",
        description="Notion API — read and write pages, databases, blocks.",
        capabilities=["page", "database", "block", "search"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "query_database": {"parameters": {"database_id": "string"}, "returns": "array"},
        },
    ),
    "linear": MCPServer(
        name="linear",
        description="Linear API — issues, projects, cycles, teams.",
        capabilities=["issue", "project", "cycle", "team"],
        status=MCPStatus.AVAILABLE,
        auth_required=True,
        tools={
            "create_issue": {"parameters": {"title": "string", "description": "string", "team_id": "string"}, "returns": "object"},
        },
    ),
    "detox": MCPServer(
        name="detox",
        description="Detox — gray-box E2E testing for React Native.",
        capabilities=["build", "test", "recorder"],
        status=MCPStatus.AVAILABLE,
        tools={
            "run_tests": {"parameters": {"config": "string"}, "returns": "string"},
        },
    ),
    "maestro": MCPServer(
        name="maestro",
        description="Maestro — simple mobile UI testing with YAML flows.",
        capabilities=["test", "studio"],
        status=MCPStatus.AVAILABLE,
        tools={
            "run_flow": {"parameters": {"flow": "string"}, "returns": "string"},
        },
    ),
}


def get_mcp(name: str) -> MCPServer | None:
    return MCP_REGISTRY.get(name)


def list_mcp() -> list[str]:
    return list(MCP_REGISTRY.keys())


def get_available_mcp() -> list[str]:
    return [name for name, s in MCP_REGISTRY.items() if s.is_available()]
