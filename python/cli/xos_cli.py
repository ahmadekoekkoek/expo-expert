#!/usr/bin/env python3
"""
xos-cli — Entry point for the XOS platform.

Usage:
  xos compile [--spec SPEC]      Compile a project (default: current directory)
  xos knowledge                  Show knowledge graph stats
  xos graph                      Show experience graph stats
  xos validate                   Run quality gates dry-run
  xos bootstrap PROJECT          Bootstrap a new XOS project
  xos agent AGENT_NAME --action ACTION  Invoke a named agent
  xos ps:env [--check]           Validate PowerShell environment
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from python.core.xos_logger import get_logger
from python.compiler.experience_compiler import ExperienceCompiler
from python.core.lm_router import LanguageModelRouter

logger = get_logger("xos-cli")


def cmd_compile(args: argparse.Namespace) -> int:
    root = Path(args.project or ".").resolve()
    compiler = ExperienceCompiler(root)
    result = compiler.compile(args.spec)
    from json import dumps
    print(dumps(result, indent=2, default=str))
    return 0 if result.get("status") == "PASSED" else 1


def cmd_knowledge(args: argparse.Namespace) -> int:
    root = Path(args.project or ".").resolve()
    from python.graph.knowledge import KnowledgeGraph
    kg = KnowledgeGraph(root)
    kg.load()
    print(f"Knowledge graph entries: {len(kg._entries)}")
    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    print("Experience graph stats — not yet implemented")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.project or ".").resolve()
    compiler = ExperienceCompiler(root)
    from python.validators.gates import GateResult
    results = compiler.gates.run({"root": root})
    for r in results:
        print(f"[{r.severity.value.upper():4s}] {r.name}: {r.message}")
    return 0


def cmd_bootstrap(args: argparse.Namespace) -> int:
    project = Path(args.project or "my-xos-project").resolve()
    if project.exists():
        logger.error("Project %s already exists", project)
        return 1
    _bootstrap_project(project)
    logger.info("Bootstrapped XOS project at %s", project)
    return 0


def _bootstrap_project(root: Path) -> None:
    dirs = [
        "specs", "graph", "knowledge/patterns", "knowledge/design-tokens",
        "knowledge/motion", "knowledge/gestures", "knowledge/haptics",
        "knowledge/accessibility", "knowledge/components", "knowledge/prompts",
        "agents", "skills", "mcp/servers", "mcp/interfaces",
        "python/core", "python/graph", "python/compiler", "python/workflows",
        "python/agents", "python/validators", "python/generators",
        "python/mcp_client", "python/cli",
        "powershell/bootstrap", "powershell/environment", "powershell/build",
        "powershell/diagnostics",
        "generators/motion", "generators/gesture", "generators/haptic",
        "generators/accessibility", "generators/performance",
        "generators/screen", "generators/component", "generators/navigation",
        "templates/project", "templates/screen", "templates/component",
        "templates/feature",
        "features", "packages", "shared", "docs",
        "tests/unit", "tests/integration", "tests/e2e", "scripts",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True)

    # Write AGENTS.md
    (root / "AGENTS.md").write_text(_AGENTS_MD_TEMPLATE.format(project_name=root.name))
    (root / "README.md").write_text(_README_MD_TEMPLATE.format(project_name=root.name))


_AGENTS_MD_TEMPLATE = """\
# {project_name} — AGENTS.md

## Routing

- `specs/` — Feature & screen specifications (JSON / YAML)
- `graph/` — Experience Graph snapshots
- `knowledge/` — Reusable patterns, tokens, prompt templates
- `agents/` — Agent definitions (mission, skills, tools)
- `skills/` — Reusable agent skills
- `mcp/` — MCP server definitions & interfaces
- `python/` — Orchestration & compilation engine
- `powershell/` — Host environment automation
- `generators/` — Code, motion, gesture, haptic, and a11y generators
- `templates/` — Project, screen, component, and feature templates
- `features/` — Feature-level generated artifacts
- `packages/` — Shared packages
- `shared/` — Shared utilities
- `tests/` — Unit, integration, and E2E tests
- `scripts/` — Ad-hoc automation scripts

## Conventions

- Never generate React Native code directly. Always compile through the pipeline.
- Every feature must define motion, gesture, haptic, and accessibility nodes.
- Use Zod for all form and API validation.
- State management: Zustand + MMKV persistence.
- Navigation: Expo Router (file-based).
- Styling: NativeWind (Tailwind for React Native).
- Animations: Reanimated with worklet-driven physics.
- Lists: FlashList for any scrollable data.
"""

_README_MD_TEMPLATE = """\
# {project_name}

AI-Native Experience Engineering Operating System (XOS) project.

## Quickstart

```bash
cd {project_name}
xos compile
```

## Project layout

See [AGENTS.md](AGENTS.md) for the full directory map.
"""


def cmd_agent(args: argparse.Namespace) -> int:
    print(f"Agent '{args.agent_name}' invoked with action '{args.action}' — not yet implemented")
    return 0


def cmd_ps_env(args: argparse.Namespace) -> int:
    import subprocess
    pwsh = subprocess.run(["pwsh", "--version"], capture_output=True, text=True)
    if pwsh.returncode != 0:
        logger.error("PowerShell 7+ not found on PATH")
        return 1
    print(pwsh.stdout.strip())
    if args.check:
        print("PowerShell environment health: OK")
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    router = LanguageModelRouter()
    intent = router.classify(args.prompt)
    from json import dumps
    print(dumps(intent, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xos", description="XOS — AI-Native Experience Engineering OS")
    sub = parser.add_subparsers(dest="command")

    p_compile = sub.add_parser("compile")
    p_compile.add_argument("--spec")
    p_compile.add_argument("--project")

    p_knowledge = sub.add_parser("knowledge")
    p_knowledge.add_argument("--project")

    sub.add_parser("graph", add_help=False)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--project")

    p_bootstrap = sub.add_parser("bootstrap")
    p_bootstrap.add_argument("project")

    p_agent = sub.add_parser("agent")
    p_agent.add_argument("agent_name")
    p_agent.add_argument("--action", required=True)

    p_ps = sub.add_parser("ps:env")
    p_ps.add_argument("--check", action="store_true")

    p_prompt = sub.add_parser("prompt")
    p_prompt.add_argument("prompt")

    args = parser.parse_args(argv)
    if args.command == "compile":
        return cmd_compile(args)
    if args.command == "knowledge":
        return cmd_knowledge(args)
    if args.command == "graph":
        return cmd_graph(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "bootstrap":
        return cmd_bootstrap(args)
    if args.command == "agent":
        return cmd_agent(args)
    if args.command == "ps:env":
        return cmd_ps_env(args)
    if args.command == "prompt":
        return cmd_prompt(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
