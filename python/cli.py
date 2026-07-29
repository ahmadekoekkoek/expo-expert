#!/usr/bin/env python3
"""
XOS CLI — the primary interface for the Experience Engineering OS.

Commands:
  xos init <project>       Initialize a new XOS project
  xos validate             Run all quality gates
  xos compile              Run the full experience compilation pipeline
  xos agent <name>         Execute a specific agent
  xos graph export         Export the experience graph
  xos anti-slop <file>     Scan a file for slop patterns
  xos knowledge list       List available knowledge entries
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core.graph import ExperienceGraph, GraphNode, NodeType, GateStatus
from .core.compiler import ExperienceCompiler
from .core.agents import AGENT_REGISTRY, AgentExecutor, AgentContext
from .core.anti_slop import AntiSlopEngine
from .core.knowledge import ALL_KNOWLEDGE, get_design_tokens, get_motion_tokens, get_haptic_tokens
from .core.node_factory import (
    create_screen_node,
    create_component_node,
    create_motion_node,
    create_gesture_node,
    create_haptic_node,
    create_accessibility_node,
    create_navigation_node,
    create_state_node,
    create_design_token_node,
)
from .core.constitution import Constitution, constitution_from_file
from .core.change import ChangeManager
from .core.clarify import ClarifyEngine
from .core.diff import GraphDiffer


def cmd_init(args):
    project_dir = Path(args.project)
    if project_dir.exists():
        print(f"❌ Project '{args.project}' already exists.")
        sys.exit(1)

    project_dir.mkdir(parents=True)
    dirs = [
        "specs", "graph", "knowledge", "agents", "skills", "mcp",
        "generators", "templates", "features", "packages", "shared",
        "docs", "tests/unit", "tests/integration", "tests/e2e", "scripts",
    ]
    for d in dirs:
        (project_dir / d).mkdir(parents=True)

    # Create initial spec
    spec = {
        "name": args.project,
        "version": "0.1.0",
        "description": "",
        "features": [],
        "design_tokens": get_design_tokens(),
        "motion_tokens": get_motion_tokens(),
        "haptic_tokens": get_haptic_tokens(),
    }
    (project_dir / "specs" / "app.spec.json").write_text(json.dumps(spec, indent=2))

    # Create initial empty graph
    graph = ExperienceGraph(name=args.project)
    graph.save(project_dir / "graph" / "experience.json")

    # Create README
    (project_dir / "README.md").write_text(
        f"# {args.project}\n\n"
        "Built with XOS — AI-Native Experience Engineering Operating System.\n\n"
        "## Commands\n"
        "- `python -m expoexpert.python.cli validate` — Run quality gates\n"
        "- `python -m expoexpert.python.cli compile` — Full compilation\n"
        "- `python -m expoexpert.python.cli anti-slop <file>` — Check code quality\n"
    )

    print(f"✅ XOS project '{args.project}' initialized.")
    print(f"   {project_dir}/")


def cmd_validate(args):
    graph_path = Path(args.graph) if args.graph else Path("graph/experience.json")
    if not graph_path.exists():
        print("❌ No experience graph found. Run 'xos init' first or specify --graph.")
        sys.exit(1)

    graph = ExperienceGraph.load(graph_path)
    compiler = ExperienceCompiler()
    result = compiler.compile(graph)

    if result.success:
        print("✅ All quality gates passed.")
    else:
        print(f"❌ {len(result.errors)} error(s) found:")
        for d in result.errors:
            print(f"   [{d.stage.name}] {d.message}")
            if d.suggestion:
                print(f"   → {d.suggestion}")

    if result.warnings:
        print(f"⚠️  {len(result.warnings)} warning(s):")
        for d in result.warnings:
            print(f"   [{d.stage.name}] {d.message}")


def cmd_compile(args):
    graph_path = Path(args.graph) if args.graph else Path("graph/experience.json")
    output_dir = Path(args.output) if args.output else Path("features")

    if not graph_path.exists():
        print("❌ No experience graph found.")
        sys.exit(1)

    graph = ExperienceGraph.load(graph_path)
    compiler = ExperienceCompiler()
    result = compiler.compile(graph, output_dir)

    if result.success:
        print(f"✅ Compilation successful. Generated {len(result.generated_files)} files.")
        for f in result.generated_files:
            print(f"   {f}")
    else:
        print(f"❌ Compilation failed with {len(result.errors)} errors.")
        for d in result.errors:
            print(f"   [{d.stage.name}] {d.message}")
        sys.exit(1)


def cmd_agent(args):
    agent_def = AGENT_REGISTRY.get(args.name)
    if not agent_def:
        print(f"❌ Unknown agent: {args.name}")
        print(f"   Available: {', '.join(AGENT_REGISTRY.keys())}")
        sys.exit(1)

    executor = AgentExecutor(agent_def)
    ctx = AgentContext(graph=ExperienceGraph())
    result = executor.execute(ctx)

    if result.success:
        print(f"✅ Agent '{args.name}' executed successfully.")
        for d in result.diagnostics:
            print(f"   {d}")
    else:
        print(f"❌ Agent '{args.name}' failed.")


def cmd_graph_export(args):
    graph_path = Path(args.graph) if args.graph else Path("graph/experience.json")
    if not graph_path.exists():
        print("❌ No experience graph found.")
        sys.exit(1)

    graph = ExperienceGraph.load(graph_path)
    output = args.output or "graph.json"
    Path(output).write_text(json.dumps(graph.to_dict(), indent=2))
    print(f"✅ Graph exported to {output}")
    print(f"   Nodes: {len(graph.nodes)}, Edges: {sum(len(e) for e in graph.edges.values())}")


def cmd_anti_slop(args):
    engine = AntiSlopEngine()
    source = Path(args.file).read_text()
    findings = engine.scan(source, args.file)

    print(engine.report())
    if engine.has_blockers():
        print(f"🚫 Generation blocked: {engine.blocker_count()} critical issue(s).")
        sys.exit(1)


def cmd_knowledge(args):
    if args.subcommand == "list":
        if args.category:
            entries = [e for e in ALL_KNOWLEDGE if e.category == args.category]
        elif args.tag:
            entries = [e for e in ALL_KNOWLEDGE if args.tag in e.tags]
        else:
            entries = ALL_KNOWLEDGE

        for e in entries:
            print(f"📚 [{e.category}] {e.name}")
            print(f"   {e.description}")
            if e.tags:
                print(f"   Tags: {', '.join(e.tags)}")
            print()
    elif args.subcommand == "tokens":
        print("🎨 Design Tokens:")
        print(json.dumps(get_design_tokens(), indent=2))
        print("\n🎬 Motion Tokens:")
        print(json.dumps(get_motion_tokens(), indent=2))
        print("\n📳 Haptic Tokens:")
        print(json.dumps(get_haptic_tokens(), indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="xos",
        description="XOS — AI-Native Experience Engineering Operating System",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize a new XOS project")
    p_init.add_argument("project", help="Project name/directory")

    # validate
    p_val = sub.add_parser("validate", help="Run all quality gates")
    p_val.add_argument("--graph", help="Path to experience graph JSON")

    # compile
    p_comp = sub.add_parser("compile", help="Run full compilation pipeline")
    p_comp.add_argument("--graph", help="Path to experience graph JSON")
    p_comp.add_argument("--output", help="Output directory for generated code")

    # agent
    p_agent = sub.add_parser("agent", help="Execute a specific agent")
    p_agent.add_argument("name", help="Agent name")

    # graph export
    p_graph = sub.add_parser("graph", help="Graph operations")
    p_graph_sub = p_graph.add_subparsers(dest="subcommand")
    p_graph_export = p_graph_sub.add_parser("export", help="Export experience graph")
    p_graph_export.add_argument("--graph", help="Path to experience graph JSON")
    p_graph_export.add_argument("--output", help="Output file path")

    # anti-slop
    p_slop = sub.add_parser("anti-slop", help="Scan file for slop patterns")
    p_slop.add_argument("file", help="File to scan")

    # knowledge
    p_know = sub.add_parser("knowledge", help="Knowledge graph operations")
    p_know_sub = p_know.add_subparsers(dest="subcommand")
    p_know_list = p_know_sub.add_parser("list", help="List knowledge entries")
    p_know_list.add_argument("--category", help="Filter by category")
    p_know_list.add_argument("--tag", help="Filter by tag")
    p_know_sub.add_parser("tokens", help="Show design/motion/haptic tokens")

    # constitution
    p_constitution = sub.add_parser("constitution", help="Manage project constitution")
    p_constitution_sub = p_constitution.add_subparsers(dest="subcommand")
    p_constitution_sub.add_parser("show", help="Show current constitution")
    p_constitution_sub.add_parser("validate", help="Validate specs against constitution")
    p_constitution_sub.add_parser("edit", help="Edit a rule")

    # change
    p_change = sub.add_parser("change", help="Manage change proposals")
    p_change_sub = p_change.add_subparsers(dest="subcommand")
    p_change_sub.add_parser("list", help="List active changes")
    p_change_sub.add_parser("new", help="Create a new change proposal").add_argument("name", help="Change name")
    p_change_sub.add_parser("apply", help="Apply a change").add_argument("name", help="Change name")
    p_change_sub.add_parser("archive", help="Archive a completed change").add_argument("name", help="Change name")

    # clarify
    p_clarify = sub.add_parser("clarify", help="Interactive spec refinement")
    p_clarify.add_argument("spec", help="Path to spec file")

    # diff
    p_diff = sub.add_parser("diff", help="Show graph differences")
    p_diff.add_argument("--before", help="Path to previous graph")
    p_diff.add_argument("--after", help="Path to current graph")


    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "agent":
        cmd_agent(args)
    elif args.command == "graph" and args.subcommand == "export":
        cmd_graph_export(args)
    elif args.command == "anti-slop":
        cmd_anti_slop(args)
    elif args.command == "knowledge":
        cmd_knowledge(args)
    elif args.command == "constitution":
        cmd_constitution(args)
    elif args.command == "change":
        cmd_change(args)
    elif args.command == "clarify":
        cmd_clarify(args)
    elif args.command == "diff":
        cmd_diff(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()




def cmd_constitution(args):
    import json
    path = "workspace/constitution.json"
    if args.subcommand == "show":
        const = Constitution.from_json_file(path)
        print(const.to_markdown())
    elif args.subcommand == "validate":
        const = Constitution.from_json_file(path)
        print(f"Constitution loaded: {len(const.rules)} rules")
        violations = const.validate("workspace/specs")
        if violations:
            for v in violations:
                print(f"  [{'BLOCK' if v.severity == 'error' else 'WARN'}] {v.rule}: {v.message}")
        else:
            print("All rules satisfied.")
    elif args.subcommand == "edit":
        print("Edit rules in workspace/constitution.json")
    else:
        print("Usage: xos constitution {show|validate|edit}")

def cmd_change(args):
    import os, json
    changes_dir = "workspace/changes"
    archive_dir = "workspace/archive"
    if args.subcommand == "list":
        if os.path.isdir(changes_dir):
            entries = os.listdir(changes_dir)
            if entries:
                for c in sorted(entries):
                    prop_path = os.path.join(changes_dir, c, "proposal.json")
                    title = c
                    if os.path.exists(prop_path):
                        try:
                            prop = json.load(open(prop_path))
                            title = prop.get("title", c)
                        except: pass
                    print(f"  {c} [{title}]")
            else:
                print("No active changes.")
        else:
            print("No active changes.")
    elif args.subcommand == "new":
        name = getattr(args, "name", "unnamed")
        os.makedirs(os.path.join(changes_dir, name), exist_ok=True)
        proposal = {"title": name, "phase": "proposal", "created": __import__("datetime").datetime.now().isoformat()}
        json.dump(proposal, open(os.path.join(changes_dir, name, "proposal.json"), "w"), indent=2)
        print(f"Created change: {name}")
    elif args.subcommand == "apply":
        name = getattr(args, "name", "")
        src = os.path.join(changes_dir, name)
        dst = os.path.join(archive_dir, name)
        if os.path.isdir(src):
            import shutil
            shutil.move(src, dst)
            print(f"Archived change: {name}")
        else:
            print(f"Change not found: {name}")
    else:
        print("Usage: xos change {list|new|apply}")

def cmd_clarify(args):
    spec_path = getattr(args, "spec", "workspace/specs")
    print(f"Scanning specs in: {spec_path}")
    print("Ready to clarify. Implement full ClarifyEngine integration here.")

def cmd_diff(args):
    old_path = getattr(args, "old", "graph/experience.json")
    new_path = getattr(args, "new", "")
    print(f"Diff: {old_path} vs {new_path or 'current'}")
    print("Ready to diff. Implement full GraphDiffer integration here.")
