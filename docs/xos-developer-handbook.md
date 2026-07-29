# XOS Developer Handbook

**Version 1.0.0** | **Enterprise Edition** | **Last updated: 2026-07-29**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Antigravity IDE](#3-antigravity-ide)
4. [Repository Structure](#4-repository-structure)
5. [Experience Graph](#5-experience-graph)
6. [Specifications](#6-specifications)
7. [Agent System](#7-agent-system)
8. [Model Context Protocol (MCP)](#8-model-context-protocol-mcp)
9. [Python Runtime](#9-python-runtime)
10. [PowerShell Runtime](#10-powershell-runtime)
11. [Experience Compiler](#11-experience-compiler)
12. [Development Workflow](#12-development-workflow)
13. [Quality Gates](#13-quality-gates)
14. [Debugging Guide](#14-debugging-guide)
15. [Troubleshooting](#15-troubleshooting)
16. [Best Practices](#16-best-practices)
17. [FAQ](#17-faq)
18. [Glossary](#18-glossary)

---

## 1. Introduction

### 1.1 What is XOS?

XOS (Experience Operating System) is an AI-native engineering platform for building premium React Native + Expo mobile applications. It treats the user experience — not the source code — as the primary artifact.

XOS introduces a paradigm shift: **code is a compiled artifact**. The Experience Graph is the single source of truth. Every screen, component, animation curve, gesture pattern, haptic feedback rule, and accessibility constraint exists as a typed, validated graph node with explicit dependencies and constraints.

### 1.2 Why XOS Exists

Traditional mobile development suffers from:

- **Design-implementation drift** — Figma designs rarely survive the engineering process intact
- **Inconsistent quality** — Each engineer interprets design intent differently
- **AI slop** — LLM-generated code produces generic layouts, random spacing, weak hierarchy
- **Missing premium interactions** — Haptics, spring physics, gesture choreography are treated as "polish" rather than architecture

XOS solves these by:

- **Compiling experiences, not code** — A 12-stage deterministic pipeline transforms specifications into production output
- **Enforcing quality gates** — Every artifact must pass architecture, design, motion, gesture, haptic, accessibility, and performance validation before code is emitted
- **Anti-slop enforcement** — An AI Slop Engine rejects generic patterns and proposes deterministic fixes
- **Agent specialization** — 19 domain-specific agents each own exactly one concern (motion, gesture, haptics, accessibility, etc.)

### 1.3 Architecture Philosophy

```
Humans define intent.
Specifications define requirements.
Graphs define relationships.
Agents execute tasks.
Python orchestrates workflows.
PowerShell manages host automation.
The Experience Compiler produces React Native + Expo applications.
```

Every layer in the stack is **specification-driven** and **deterministic**:

- **Specifications** are structured JSON/YAML documents describing what the application should do
- **Graphs** represent every concept as a node with explicit edges (depends_on, composes, animates, gestures, etc.)
- **Agents** are domain-specialized AI workers that validate, transform, and generate artifacts
- **The Compiler** is a pipeline of 12 stages that validates, resolves, and emits code

### 1.4 Deterministic Engineering

XOS guarantees that given the same specifications and knowledge graph, the compiler produces identical output. This means:

- **Reproducible builds** — Every run produces the same code
- **Auditable decisions** — Every compilation stage logs its diagnostics
- **Incremental compilation** — Only changed graph nodes are recompiled
- **Rollback support** — Every compilation result is versioned and reversible

### 1.5 Specification-Driven Development

Specifications are the entry point into XOS. You never write React Native code directly. Instead, you write specifications that describe:

- What screens exist and what they contain
- What data flows between them
- What interactions are supported
- What motion, gesture, haptic, and accessibility rules apply

The Experience Compiler transforms these specifications into a fully validated, production-ready Expo application.

### 1.6 Key Concepts

| Concept | Definition |
|---|---|
| **Experience Graph** | A directed graph where every node is a typed concept (screen, component, motion, gesture, etc.) with validated edges |
| **Experience Compiler** | A 12-stage deterministic pipeline that validates, resolves, and emits React Native + Expo code |
| **Knowledge Graph** | A reusable library of design tokens, component patterns, motion curves, gesture profiles, haptic patterns, and accessibility rules |
| **Quality Gate** | A validation checkpoint — the compiler halts if any gate fails |
| **Agent** | A domain-specialized AI worker that owns exactly one concern |
| **Anti-Slop Engine** | A scanner that rejects generic, low-quality generation patterns |
| **MCP** | Model Context Protocol — standardized interfaces for agent-tool communication |

---

## 2. Installation

### 2.1 Prerequisites

| Component | Minimum Version | Purpose |
|---|---|---|
| Python | 3.12+ | Core orchestration runtime |
| Node.js | 20 LTS | React Native / Expo toolchain |
| pnpm | 9+ | Package management |
| Git | 2.40+ | Version control |
| Expo CLI | Latest | Mobile development framework |
| PowerShell | 7+ | Host automation (Windows/macOS/Linux) |

### 2.2 Installing XOS

```bash
# Clone the repository
git clone https://github.com/ahmadekoekkoek/expo-expert.git
cd expo-expert

# Install Python dependencies and register the CLI
pip install -e .

# Verify installation
xos --help
```

**Expected output:**

```
usage: xos [-h] {init,validate,compile,agent,graph,anti-slop,knowledge} ...

XOS — AI-Native Experience Engineering Operating System

positional arguments:
  {init,validate,compile,agent,graph,anti-slop,knowledge}
    init                Initialize a new XOS project
    validate            Run all quality gates
    compile             Run full compilation pipeline
    agent               Execute a specific agent
    graph               Graph operations
    anti-slop           Scan file for slop patterns
    knowledge           Knowledge graph operations
```

### 2.3 Environment Validation

```bash
# Run comprehensive environment check
xos validate --graph graph/experience.json
```

### 2.4 PowerShell Environment Setup (Windows/macOS/Linux)

```powershell
# Import the XOS PowerShell module
Import-Module ./powershell/XOSEnvironment.psm1

# Validate the environment
Test-XOSEnvironment

# Bootstrap a new project
New-XOSProject -Name "MyApp" -Path "./projects"
```

### 2.5 Troubleshooting Installation

| Symptom | Cause | Resolution |
|---|---|---|
| `xos: command not found` | Package not installed | Run `pip install -e .` from the repo root |
| `ModuleNotFoundError: No module named 'python'` | Python path issue | Ensure you're in the repo root directory |
| `AttributeError: 'list' object has no attribute 'items'` | Graph format mismatch | Regenerate graph: `python3 scripts/populate_graph.py > graph/experience.json` |

---

## 3. Antigravity IDE

> **Note:** Antigravity IDE is the primary development environment for XOS. All workflows in this handbook assume Antigravity IDE is the active workspace.

### 3.1 Workspace Overview

Antigravity IDE provides a unified environment for:

- Viewing and editing source files
- Running terminal commands
- Interacting with AI agents via chat
- Inspecting the Experience Graph
- Monitoring compilation pipelines
- Debugging generated applications

### 3.2 Key Interface Areas

| Panel | Purpose | Shortcut |
|---|---|---|
| **File Explorer** | Browse and manage project files | `Ctrl+Shift+E` |
| **Editor** | Edit specifications, Python scripts, templates | `Ctrl+Enter` (focus) |
| **Terminal** | Execute shell commands, run `xos` CLI | `` Ctrl+` `` |
| **AI Chat** | Interact with XOS agents | `Ctrl+Shift+A` |
| **Graph Viewer** | Visualize the Experience Graph | `Ctrl+Shift+G` |
| **Problems Panel** | View compilation errors and quality gate failures | `Ctrl+Shift+M` |
| **Output Panel** | Stream compilation logs and agent outputs | `Ctrl+Shift+U` |
| **MCP Panel** | Manage MCP server connections | `Ctrl+Shift+P` → "MCP" |

### 3.3 Command Palette

Access all IDE commands via the Command Palette (`Ctrl+Shift+P`):

- `XOS: Initialize Project` — Creates a new XOS project scaffold
- `XOS: Validate Graph` — Runs all quality gates against the current graph
- `XOS: Compile` — Runs the full compilation pipeline
- `XOS: Scan for Slop` — Runs the Anti-Slop engine on the current file
- `XOS: View Experience Graph` — Opens the graph visualization
- `XOS: Execute Agent` — Prompts for agent name and input

### 3.4 AI Chat Integration

The AI Chat panel provides direct access to XOS agents. Commands:

- `/agent <name>` — Invoke a specific agent (e.g., `/agent motion-engineer`)
- `/compile` — Trigger a full compilation
- `/validate` — Run quality gates on the current graph
- `/graph` — Query the Experience Graph

### 3.5 Graph Viewer

The Graph Viewer renders the Experience Graph as an interactive node-edge diagram:

- **Nodes** are color-coded by type (screens = blue, components = green, motion = orange, gestures = purple, haptics = red, accessibility = teal)
- **Edges** are styled by kind (solid = composes, dashed = depends_on, dotted = navigates_to)
- **Click** any node to inspect its properties, constraints, and quality gate status
- **Hover** any edge to see its kind and metadata

### 3.6 Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Open Command Palette | `Ctrl+Shift+P` |
| Toggle Terminal | `` Ctrl+` `` |
| Toggle File Explorer | `Ctrl+Shift+E` |
| Toggle Graph Viewer | `Ctrl+Shift+G` |
| Toggle AI Chat | `Ctrl+Shift+A` |
| Find in Files | `Ctrl+Shift+F` |
| Go to File | `Ctrl+P` |
| Build (XOS Compile) | `Ctrl+Shift+B` |

---

## 4. Repository Structure

### 4.1 Directory Map

```
expoexpert/
├── specs/                 # Feature & screen specifications (JSON/YAML)
│   └── storefront.spec.json
├── graph/                 # Experience Graph snapshots
│   └── experience.json    #   Live graph: 37 nodes, 24 edges
├── knowledge/             # Reusable patterns (design tokens, motion, gestures, etc.)
│   ├── design-tokens/     #   Spacing, typography, colors, radius, shadows
│   ├── motion/            #   Spring configs, duration tokens, easing curves
│   ├── gestures/          #   Tap, swipe, pinch, pan profiles
│   ├── haptics/           #   Light/medium/heavy impact patterns
│   ├── accessibility/     #   WCAG rules, semantic roles, focus order
│   ├── components/        #   Button, Card, Input, List patterns
│   ├── patterns/          #   Architecture patterns (feature-slice, state mgmt)
│   └── prompts/           #   Agent prompt template schemas
├── agents/                # Agent definitions
│   └── agent-roster.json  #   19 domain-specialized agents
├── skills/                # Reusable agent skills
│   └── skill-registry.json #  16 skills (generate_feature, audit_motion, etc.)
├── mcp/                   # MCP server definitions & interfaces
│   ├── servers/           #   Server manifests (Expo, Supabase, Figma, etc.)
│   └── interfaces/        #   Tool schemas
├── python/                # Core Python orchestration runtime
│   ├── cli.py             #   CLI entrypoint (xos command)
│   ├── core/              #   Graph engine, compiler, validators, agents
│   ├── graph/             #   Experience Graph implementations
│   ├── validators/        #   Quality gate functions
│   ├── generators/        #   Code generation modules
│   ├── agents/            #   Agent runtime and registry
│   └── compiler/          #   Compilation pipeline stages
├── powershell/            # Host automation modules
│   ├── XOSEnvironment.psm1
│   ├── bootstrap/         #   New-XOSProject.ps1
│   ├── diagnostics/       #   Test-XOSEnvironment.ps1
│   └── xos-automation.ps1
├── templates/             # Project, screen, component templates
├── generators/            # Specialized code generators
├── tests/                 # Test suites
│   ├── unit/              #   Unit tests (10 passing)
│   ├── integration/       #   Integration tests
│   └── e2e/               #   End-to-end tests
├── docs/                  # Architecture decisions, guides, ADRs
├── scripts/               # Utility scripts
├── pyproject.toml         # Python package configuration
├── AGENTS.md              # Agent workspace routing guide
├── README.md              # Quickstart guide
└── SPECIFICATION.md       # Platform specification
```

### 4.2 Directory Purposes

| Directory | Ownership | Manual Edits | Generated |
|---|---|---|---|
| `specs/` | Product Engineer | ✅ Yes | ❌ No |
| `graph/` | Compiler + Graph Engine | ❌ No | ✅ Yes |
| `knowledge/` | Design System Engineer | ✅ Yes | ❌ No |
| `agents/` | Chief Architect | ✅ Yes | ❌ No |
| `skills/` | Chief Architect | ✅ Yes | ❌ No |
| `mcp/` | MCP Engineer | ✅ Yes | ❌ No |
| `python/` | Platform Engineers | ✅ Yes | ❌ No |
| `powershell/` | DevOps Engineers | ✅ Yes | ❌ No |
| `templates/` | React Native Engineer | ✅ Yes | ❌ No |
| `generators/` | Compiler | ⚠️ Partial | ✅ Yes |
| `tests/` | Testing Engineer | ✅ Yes | ⚠️ Partial |
| `features/` | Feature Teams | ⚠️ Partial | ✅ Yes |

---

## 5. Experience Graph

### 5.1 Graph Philosophy

The Experience Graph is the **single source of truth** for every artifact in an XOS project. It is not a documentation artifact — it is the canonical representation from which all code is compiled.

> **Principle:** If it isn't in the graph, it doesn't exist in the application.

### 5.2 Node Types

XOS defines 22 node kinds, each representing a first-class concept:

| Node Kind | Purpose | Example ID |
|---|---|---|
| `product` | Top-level product definition | `product:store` |
| `domain` | Business domain boundary | `domain:commerce` |
| `feature` | User-facing feature | `feat:browse` |
| `workflow` | Multi-step user flow | `workflow:checkout` |
| `business_rule` | Domain constraint | `rule:max-cart-items` |
| `screen` | Application screen | `screen:home` |
| `component` | Reusable UI component | `comp:product-card` |
| `navigation` | Navigation structure | `nav:tab-bar` |
| `state` | Application state slice | `state:cart-store` |
| `design_token` | Visual design value | `token:spacing-md` |
| `typography_token` | Text style definition | `typo:headline` |
| `color_token` | Semantic color value | `color:primary-500` |
| `motion_token` | Animation definition | `motion:entrance-fade` |
| `gesture_pattern` | Touch interaction | `gesture:swipe-delete` |
| `haptic_pattern` | Haptic feedback rule | `haptic:confirm` |
| `accessibility_rule` | A11y constraint | `a11y:min-touch-target` |
| `performance_target` | Performance budget | `perf:60fps-motion` |
| `agent` | AI agent definition | `agent:motion-engineer` |
| `prompt` | Agent prompt template | `prompt:generate-screen` |
| `mcp_tool` | MCP capability | `mcp:expo-build` |
| `test` | Test specification | `test:home-screen` |
| `documentation` | Doc artifact | `doc:api-reference` |

### 5.3 Edge Types

Edges define relationships between nodes:

| Edge Kind | Meaning | Example |
|---|---|---|
| `depends_on` | Source requires target | `screen:home` → `comp:product-card` |
| `composes` | Parent contains child | `feat:browse` → `screen:home` |
| `navigates_to` | Screen links to screen | `screen:home` → `screen:detail` |
| `implements` | Concrete fulfills abstract | `comp:button` → `a11y:min-touch-target` |
| `animates` | Motion applies to node | `motion:entrance` → `comp:hero` |
| `gestures` | Gesture applies to node | `gesture:swipe` → `comp:list-item` |
| `haptics` | Haptic applies to node | `haptic:confirm` → `comp:checkout-btn` |
| `accesses` | A11y rule constrains node | `a11y:contrast` → `comp:text-label` |
| `themes` | Token styles node | `color:primary` → `comp:button` |
| `constrains` | Rule limits node | `perf:60fps` → `motion:entrance` |

### 5.4 Graph Validation

The graph engine performs structural validation on every load:

```python
from python.graph.experience_graph import ExperienceGraph
import json

data = json.load(open("graph/experience.json"))
graph = ExperienceGraph.from_dict(data)
report = graph.validate_integrity()
print(f"Valid: {report['valid']}, Nodes: {report['node_count']}, Edges: {report['edge_count']}")
```

Validation checks:

1. **Missing intent** — Every node must declare its purpose
2. **Dangling edges** — Source and target nodes must exist
3. **Required constraints** — Screen nodes require `frame_budget`
4. **Edge consistency** — Edges must use defined `EdgeKind` values

### 5.5 Topological Sort

The graph supports topological sort for compilation ordering:

```python
order = graph.topological_sort()
# Ensures: dependencies appear before dependents
```

### 5.6 Incremental Compilation

When a subset of nodes changes, only affected subgraphs are recompiled:

1. Identify changed nodes
2. Walk transitive dependents
3. Compile only the affected subgraph
4. Merge with cached results from unchanged nodes

### 5.7 Graph CLI Commands

```bash
# View graph statistics
xos graph

# Export graph to JSON
xos graph --export ./graph/export.json

# Validate graph integrity
xos validate --graph ./graph/experience.json
```

---

## 6. Specifications

### 6.1 Specification Philosophy

Specifications are the entry point into XOS. They describe **what** should exist — the Experience Compiler determines **how** to build it.

### 6.2 Feature Specification

A feature spec defines a user-facing capability with screens, data sources, state, and interaction rules.

**Required fields:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique feature identifier |
| `description` | string | What the feature does |
| `screens` | array | List of screen definitions |

**Optional fields:**

| Field | Type | Description |
|---|---|---|
| `backend` | string | Backend provider (supabase, firebase, etc.) |
| `dataModel` | object | Entity definitions |
| `navigation` | object | Navigation structure |
| `theme` | string | Design system reference |

**Example:**

```json
{
  "name": "browse",
  "description": "Product browsing and search",
  "screens": [
    {
      "name": "home",
      "route": "/",
      "components": ["product-card", "search-bar"],
      "state": "productStore",
      "motion": {"entrance": "fadeIn"},
      "gestures": ["pullToRefresh"],
      "haptics": ["lightImpact (tap)"],
      "accessibility": {"heading": "Discover"}
    }
  ]
}
```

### 6.3 Screen Specification

Each screen within a feature defines:

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Screen identifier |
| `route` | ✅ | Expo Router path |
| `description` | ❌ | Human-readable purpose |
| `components` | ✅ | Component list for this screen |
| `dataSource` | ❌ | Data hooks to use |
| `state` | ❌ | Zustand store name |
| `motion` | ✅ | Entrance/mount animation |
| `gestures` | ✅ | Supported touch interactions |
| `haptics` | ✅ | Haptic feedback rules |
| `accessibility` | ✅ | A11y heading and focus order |

### 6.4 Motion Specification

```json
{
  "name": "slideInRight",
  "intent": "Screen entrance from right edge",
  "duration_ms": 300,
  "curve": "spring",
  "spring_config": {"damping": 15, "stiffness": 150},
  "interruptible": true,
  "frame_budget_ms": 8,
  "reduced_motion_fallback": "fadeIn"
}
```

### 6.5 Gesture Specification

```json
{
  "name": "swipeDelete",
  "trigger": "horizontal_pan",
  "threshold_px": 80,
  "velocity_threshold": 500,
  "direction": "left",
  "rubber_banding": true,
  "haptic": "notificationWarning",
  "recovery": "spring_back"
}
```

### 6.6 Common Specification Mistakes

| Mistake | Fix |
|---|---|
| Missing `motion` on screens | Every screen must define entrance animation |
| Missing `haptics` on interactive components | Every tappable element needs haptic intent |
| Missing `accessibility.heading` | Every screen needs a semantic heading |
| Undefined `dataSource` | Always declare data dependencies explicitly |
| Skipping `gestures` | Every screen must declare supported gestures |
| Using arbitrary strings for components | Components must reference defined component patterns |

---

## 7. Agent System

### 7.1 Architecture

XOS agents are domain-specialized AI workers. Each agent owns exactly one concern and operates within strict boundaries.

### 7.2 Agent Roster (19 Agents)

| Agent | Domain | Primary Skill |
|---|---|---|
| `chief-architect` | Architecture | review-architecture |
| `product-engineer` | Product specs | generate-feature |
| `ux-engineer` | User experience | review-ux |
| `design-system-engineer` | Design tokens | generate-component |
| `motion-engineer` | Animations | generate-motion |
| `gesture-engineer` | Touch interactions | generate-gesture |
| `haptic-engineer` | Haptic feedback | generate-haptic |
| `accessibility-engineer` | A11y compliance | review-accessibility |
| `performance-engineer` | Frame budgets | review-performance |
| `react-native-engineer` | RN components | generate-screen |
| `expo-engineer` | Expo compatibility | generate-navigation |
| `backend-engineer` | Data layer | generate-api |
| `python-automation-engineer` | Orchestration | — |
| `powershell-engineer` | Host automation | — |
| `mcp-engineer` | MCP servers | — |
| `testing-engineer` | Test suites | generate-tests |
| `documentation-engineer` | Documentation | generate-documentation |
| `release-engineer` | Builds | — |
| `security-engineer` | Security audit | review-security |

### 7.3 Agent Lifecycle

```
Input → Context Load → Planning → Execution → Validation → Reflection → Output
                                                                    ↓
                                                              Retry (if failed)
```

1. **Input** — Agent receives a specification or task
2. **Context Load** — Agent loads relevant knowledge graph patterns
3. **Planning** — Agent decomposes task into steps
4. **Execution** — Agent invokes tools via MCP
5. **Validation** — Agent runs its validation rules
6. **Reflection** — Agent assesses output quality
7. **Output** — Agent produces artifact or diagnostic
8. **Retry** — On failure, agent retries with backoff strategy

### 7.4 Invoking Agents

**Via CLI:**
```bash
xos agent motion-engineer --input '{"screen": "home", "entrance": "slideInRight"}'
```

**Via AI Chat:**
```
/agent gesture-engineer
Define swipe-to-delete for the cart-item component. Threshold: 80px. Haptic: notificationWarning.
```

### 7.5 Agent Validation Rules

Every agent defines mandatory validation rules. For example, `motion-engineer` requires:

- Animation must run at 60fps (frame budget ≤ 16ms)
- Animation must be interruptible
- Reduced-motion fallback must exist
- No JS-thread animations (worklet-only)

If any rule fails, the agent produces diagnostics instead of code.

---

## 8. Model Context Protocol (MCP)

### 8.1 What is MCP?

The Model Context Protocol (MCP) is a standardized interface for communication between AI agents and external tools. In XOS, every external capability — filesystem access, Git operations, Expo CLI, Supabase, Figma — is exposed through an MCP server.

### 8.2 MCP Architecture

```
Agent → MCP Client → Transport (stdio/HTTP) → MCP Server → Tool
                                                              ↓
                                                         External System
```

- **MCP Server** — Wraps an external system and exposes its capabilities as tools
- **MCP Client** — Used by agents to discover and invoke tools
- **Transport** — Communication channel (stdio for local, HTTP for remote)
- **Tool** — A single capability (e.g., `expo-build`, `supabase-query`)

### 8.3 Available MCP Servers

| Server | Tools | Transport |
|---|---|---|
| `filesystem` | read, write, list, delete | stdio |
| `git` | commit, push, pull, status, diff | stdio |
| `terminal` | exec, shell | stdio |
| `expo` | build, start, publish, eject | HTTP |
| `react-native` | bundle, analyze, profile | HTTP |
| `supabase` | query, migrate, auth | HTTP |
| `firebase` | deploy, analytics, crashlytics | HTTP |
| `figma` | export, inspect, components | HTTP |
| `playwright` | screenshot, test, audit | HTTP |
| `maestro` | flow, test, record | HTTP |
| `notion` | page, database, search | HTTP |
| `linear` | issue, project, cycle | HTTP |
| `openapi` | spec, validate, generate | HTTP |
| `accessibility` | audit, axe, wcag | HTTP |
| `performance` | profile, trace, benchmark | HTTP |

### 8.4 Server Configuration

MCP servers are defined in `mcp/servers/server-registry.json`:

```json
{
  "servers": {
    "expo": {
      "name": "Expo CLI Server",
      "transport": "http",
      "endpoint": "http://localhost:3001",
      "tools": ["build", "start", "publish", "eject"],
      "auth": "none"
    }
  }
}
```

### 8.5 Security Model

- Local MCP servers (stdio) run with the same permissions as the IDE
- Remote MCP servers (HTTP) require explicit connection approval
- Each agent declares required MCP access in its manifest
- The agent runtime enforces access control per agent

---


## 9. Python Runtime

### 9.1 Architecture

The Python runtime is the orchestration layer of XOS. It coordinates the entire compilation pipeline: loading specifications, building graphs, resolving dependencies, invoking agents, running quality gates, and generating artifacts.

### 9.2 Module Map

```
python/
├── cli.py                    # CLI entrypoint (xos command)
├── core/                     # Core engine
│   ├── graph.py              #   ExperienceGraph, GraphNode, NodeType
│   ├── compiler.py           #   ExperienceCompiler, PipelineStage
│   ├── agents.py             #   AgentRegistry, AgentExecutor
│   ├── anti_slop.py          #   AntiSlopEngine, SLOP_RULES
│   ├── knowledge.py          #   Knowledge loading utilities
│   ├── node_factory.py       #   Typed node constructors
│   ├── mcp_layer.py          #   MCP client abstraction
│   ├── lm_router.py          #   Language model routing
│   └── xos_logger.py         #   Structured logging
├── graph/                    # Graph implementations
│   ├── experience_graph.py   #   Primary graph engine
│   ├── experience.py         #   NetworkX-based graph
│   ├── engine.py             #   Alternative graph engine
│   ├── knowledge.py          #   Knowledge graph
│   └── knowledge_loader.py   #   Knowledge loading
├── validators/               # Quality gate functions
│   ├── gates.py              #   QualityGatePipeline
│   └── builtin_gates.py      #   9 built-in gates
├── compiler/                 # Compilation stages
│   ├── engine.py             #   Compilation engine
│   ├── experience_compiler.py #  Experience compiler variant
│   └── pipeline.py           #   Pipeline orchestration
├── generators/               # Code generation
│   └── code_gen.py           #   Code generation utilities
└── agents/                   # Agent runtime
    ├── registry.py           #   Agent discovery
    ├── roster.py             #   Agent roster management
    └── runtime.py            #   Agent execution runtime
```

### 9.3 CLI Commands

```bash
xos init <project>            # Initialize a new XOS project
xos validate [--graph PATH]   # Run all quality gates
xos compile [--graph PATH]    # Full compilation pipeline
xos agent <name> [--input]    # Execute a specific agent
xos graph [--export PATH]     # Graph operations
xos anti-slop <file>          # Scan a file for slop patterns
xos knowledge                 # Knowledge graph statistics
```

### 9.4 Using the Python API

```python
from python.core.graph import ExperienceGraph, GraphNode, NodeType
from python.core.compiler import ExperienceCompiler
from python.core.anti_slop import AntiSlopEngine

# Load a graph
graph = ExperienceGraph.load(Path("graph/experience.json"))

# Compile
compiler = ExperienceCompiler()
result = compiler.compile(graph)

if result.success:
    print(f"Generated {len(result.generated_files)} files")
else:
    for error in result.errors:
        print(f"[{error.stage.name}] {error.message}")

# Anti-slop scan
engine = AntiSlopEngine()
engine.scan(source_code)
for finding in engine.findings:
    print(f"[{finding.severity.value}] {finding.rule}: {finding.message}")
```

### 9.5 Node Factory

The node factory provides typed constructors for every node kind:

```python
from python.core.node_factory import (
    create_screen_node, create_component_node, create_motion_node,
    create_gesture_node, create_haptic_node, create_accessibility_node,
)

screen = create_screen_node("home", "Main product feed", route="/")
motion = create_motion_node("entrance", "Slide-in entrance", duration_ms=300, curve="spring")
haptic = create_haptic_node("tap", "Light tap feedback", intensity="light")
```

### 9.6 Plugin System

XOS supports plugins via Python entry points. Plugins can:

- Register custom quality gates
- Add new node types
- Extend the CLI with subcommands
- Provide custom code generators
- Add MCP server implementations

```python
# In your plugin's setup.py:
entry_points = {
    "xos.gates": ["my-gate = my_plugin.gates:my_custom_gate"],
    "xos.commands": ["my-cmd = my_plugin.cli:register"],
}
```

### 9.7 Logging

```python
from python.core.xos_logger import get_logger
logger = get_logger(__name__)
logger.info("Compiling screen: %s", screen_id)
logger.warning("Frame budget exceeded: %dms", actual_ms)
logger.error("Gate failure: %s — %s", gate_name, message)
```

---

## 10. PowerShell Runtime

### 10.1 Purpose

The PowerShell runtime manages the local development environment — bootstrapping projects, validating toolchains, configuring certificates, and running builds. It handles the "host" layer that Python and agents depend on.

### 10.2 Module Structure

```
powershell/
├── XOSEnvironment.psm1           # Main module
├── bootstrap/
│   └── New-XOSProject.ps1        # Project scaffold creation
├── diagnostics/
│   └── Test-XOSEnvironment.ps1   # Environment validation
└── xos-automation.ps1            # Automation entrypoint
```

### 10.3 Commands

**Validate environment:**
```powershell
Test-XOSEnvironment
```

Checks:
- Python 3.12+ installed
- Node.js 20+ installed
- pnpm installed
- Expo CLI available
- Android SDK (if on macOS/Linux/Windows)
- Xcode (if on macOS)
- Git configured
- Required environment variables

**Bootstrap a project:**
```powershell
New-XOSProject -Name "MyApp" -Path "./projects"
```

Creates:
- Directory structure
- Initial `app.spec.json`
- Empty experience graph
- README.md

**Environment repair:**
```powershell
Repair-XOSEnvironment
```

- Reinstalls missing dependencies
- Resets environment variables
- Clears caches
- Rebuilds virtual environments

### 10.4 Integration with Python

Python workflows invoke PowerShell scripts for host-level operations:

```python
import subprocess

def validate_environment():
    result = subprocess.run(
        ["pwsh", "-File", "powershell/diagnostics/Test-XOSEnvironment.ps1"],
        capture_output=True, text=True
    )
    return result.returncode == 0
```

---

## 11. Experience Compiler

### 11.1 Pipeline Stages

The Experience Compiler executes 12 stages in sequence. Each stage validates its inputs and produces outputs that feed the next stage. If any stage fails, the compiler halts and produces diagnostics.

```
 1. SPEC_LOAD              Load specifications from specs/
 2. KNOWLEDGE_GRAPH        Expand knowledge graph patterns
 3. EXPERIENCE_GRAPH       Build/validate the experience graph
 4. DEPENDENCY_RESOLUTION  Resolve all node dependencies
 5. CONSTRAINT_VALIDATION  Check all constraints
 6. AGENT_PLANNING         Plan agent execution order
 7. MOTION_COMPILATION     Compile motion definitions
 8. GESTURE_COMPILATION    Compile gesture definitions
 9. HAPTIC_COMPILATION     Compile haptic feedback rules
10. ACCESSIBILITY_COMPILATION  Compile accessibility rules
11. PERFORMANCE_OPTIMIZATION   Optimize for performance budgets
12. CODE_GENERATION        Emit React Native + Expo source code
```

### 11.2 Compilation Result

```python
@dataclass
class CompilationResult:
    success: bool
    graph: ExperienceGraph
    generated_files: list[Path]
    diagnostics: list[CompilationDiagnostic]
    artifacts: dict[str, Any]
```

### 11.3 Diagnostics

Each diagnostic includes:

| Field | Description |
|---|---|
| `stage` | Which pipeline stage produced it |
| `level` | `error`, `warning`, or `info` |
| `message` | Human-readable description |
| `node_id` | Affected graph node (if applicable) |
| `suggestion` | Actionable fix |

### 11.4 Quality Gates

The compiler enforces 12 quality gates. See [Section 13](#13-quality-gates) for detailed gate documentation.

### 11.5 Incremental Compilation

When only a subset of nodes changes, the compiler:

1. Computes the set of changed nodes
2. Walks transitive dependents
3. Recompiles only the affected subgraph
4. Merges results with the unchanged cache

This enables sub-second recompilation for small changes.

### 11.6 Rollback

Every compilation result is versioned. To roll back:

```bash
xos compile --rollback <version>
```

---

## 12. Development Workflow

### 12.1 Create a New Project

**Goal:** Initialize a new XOS project from scratch.

**Prerequisites:** XOS installed, `xos` CLI available.

**Steps:**

1. Open Antigravity IDE terminal.
2. Run:
   ```bash
   xos init MyApp
   cd MyApp
   ```
3. Verify the scaffold:
   ```bash
   ls -la
   # Expect: specs/ graph/ knowledge/ agents/ ...
   ```
4. Open `specs/app.spec.json` in the editor and define your first feature.

**Expected output:**
```
✅ XOS project 'MyApp' initialized.
   MyApp/
```

### 12.2 Create a Feature

**Goal:** Add a new feature specification.

**Steps:**

1. Create `specs/my-feature.spec.json`:
   ```json
   {
     "name": "my-feature",
     "description": "What this feature does",
     "screens": [...]
   }
   ```
2. Populate the experience graph:
   ```bash
   xos compile --spec specs/my-feature.spec.json
   ```
3. Review the generated graph:
   ```bash
   xos graph
   ```

**Common issues:**
- Missing required fields → Check the specification schema
- Graph validation failure → Run `xos validate` for diagnostics

### 12.3 Generate a Screen

**Goal:** Generate a complete screen from a specification.

**Steps:**

1. Invoke the screen generation agent:
   ```
   /agent react-native-engineer
   Generate screen "product-detail" from spec specs/storefront.spec.json
   ```
2. The agent produces:
   - `ProductDetailScreen.tsx` with full component tree
   - Motion, gesture, haptic, accessibility wiring
   - State connection via Zustand
   - Test file

3. Review the output in the Problems panel for any gate failures.

### 12.4 Run Quality Gates

**Goal:** Validate the entire project.

**Steps:**

1. Run:
   ```bash
   xos validate
   ```
2. If gates pass:
   ```
   ✅ All quality gates passed.
   ```
3. If gates fail:
   ```
   ❌ 3 error(s) found:
      [DEPENDENCY_RESOLUTION] Missing dependency: comp:button
      → Add component node "comp:button" to the graph.
   ```

### 12.5 Debug a Failure

**Goal:** Understand and fix a compilation failure.

**Steps:**

1. Read the error output from the compiler.
2. Identify the failing stage (e.g., `CONSTRAINT_VALIDATION`).
3. Locate the affected graph node using its ID.
4. Inspect the node:
   ```bash
   xos graph --node screen:home
   ```
5. Fix the specification or graph, then recompile.

### 12.6 Release Build

**Goal:** Produce a production build.

**Steps:**

1. Ensure all quality gates pass:
   ```bash
   xos validate
   ```
2. Run the full compilation:
   ```bash
   xos compile --output ./build
   ```
3. Use Expo to build:
   ```bash
   cd build && npx expo build:android   # or build:ios
   ```

---

## 13. Quality Gates

### 13.1 Gate Pipeline

Quality gates are the enforcement mechanism of XOS. Every generated artifact must pass all 12 gates before code is emitted. Gates run in order — cheaper checks first.

### 13.2 Gate Catalog

| # | Gate | Severity | What It Checks |
|---|---|---|---|
| 1 | `specification` | FAIL | Spec files exist and parse correctly |
| 2 | `graph` | FAIL | Graph is valid (no dangling edges, missing intents) |
| 3 | `architecture` | FAIL | No circular dependencies, feature isolation |
| 4 | `design` | FAIL | Visual hierarchy, spacing rhythm, typography consistency |
| 5 | `motion` | FAIL | All animations have defined curves, frame budgets, interruptibility |
| 6 | `gesture` | FAIL | No gesture conflicts, thresholds defined, recovery paths exist |
| 7 | `haptic` | FAIL | Every interactive element has haptic intent |
| 8 | `accessibility` | FAIL | WCAG compliance, semantic roles, focus order, dynamic type |
| 9 | `performance` | FAIL | Frame budgets, GPU/CPU cost, memory, startup time |
| 10 | `testing` | WARN | Tests exist for generated code |
| 11 | `documentation` | WARN | Documentation covers all screens and features |
| 12 | `security` | FAIL | No exposed secrets, API keys in config, secure storage |

### 13.3 Failure Response

When a gate fails, the compiler:

1. **Halts immediately** — no further stages execute
2. **Produces diagnostics** — including the specific node, rule violated, and fix
3. **Suggests remediation** — actionable steps to resolve the failure

### 13.4 Adding Custom Gates

```python
from python.validators.gates import GateResult, GateSeverity, QualityGatePipeline

def my_custom_gate(context):
    root = context.get("root")
    # Custom validation logic
    if problem_detected:
        return GateResult("my_gate", GateSeverity.FAIL, "Description of failure")
    return GateResult("my_gate", GateSeverity.PASS)

pipeline = QualityGatePipeline()
pipeline.register(my_custom_gate)
pipeline.run(context)
```


## 14. Debugging Guide

### 14.1 Log Analysis

XOS uses structured logging via `python.core.xos_logger`. All compilation stages, agent invocations, and MCP calls produce timestamped, leveled logs.

**View compilation logs:**
```bash
xos compile --verbose
```

**Key log sources:**

| Source | Location | Content |
|---|---|---|
| Compiler | stdout | Stage progress, diagnostics, timings |
| Agents | Agent output panel | Planning, execution, validation results |
| MCP | MCP panel | Tool calls, responses, errors |
| Python | `xos_logger` output | Structured log entries |
| PowerShell | Script output | Environment checks, build steps |

### 14.2 Graph Debugging

**Inspect a node:**
```bash
xos graph --node screen:home
```

**Check for circular dependencies:**
```python
from python.graph.experience_graph import ExperienceGraph
graph = ExperienceGraph.from_json_file("graph/experience.json")
# Topological sort will raise RuntimeError on cycles
try:
    order = graph.topological_sort()
except RuntimeError as e:
    print(f"Cycle detected: {e}")
```

**Find all dependents of a node:**
```python
dependents = graph.successors("comp:button")
print(f"Components that depend on button: {dependents}")
```

### 14.3 Agent Debugging

When an agent fails:

1. Check the agent's output in the AI Chat panel
2. Review the agent's validation rules in `agents/agent-roster.json`
3. Verify the agent has required MCP access
4. Check input specification for missing fields

### 14.4 MCP Debugging

**Test MCP connectivity:**
```bash
# Via the MCP panel in Antigravity IDE:
# Navigate to MCP Panel → Select server → Click "Test Connection"
```

**View MCP tool schemas:**
```bash
cat mcp/servers/server-registry.json | python3 -m json.tool
```

### 14.5 Python Debugging

**Enable verbose logging:**
```python
import logging
logging.getLogger("xos").setLevel(logging.DEBUG)
```

**Profile compilation:**
```bash
python3 -m cProfile -o compile.prof -m xos compile
python3 -c "import pstats; pstats.Stats('compile.prof').sort_stats('cumtime').print_stats(20)"
```

### 14.6 Performance Debugging

**Check frame budgets:**
```bash
xos compile --profile
```

The compiler will report any motion node exceeding its frame budget (default: 16ms for 60fps).

---

## 15. Troubleshooting

### 15.1 Compilation Failures

| Symptom | Root Cause | Diagnosis | Resolution | Prevention |
|---|---|---|---|---|
| `AttributeError: 'list' object has no attribute 'items'` | Graph edges in list format | Check `graph/experience.json` edges structure | Regenerate with `scripts/populate_graph.py` | Use `xos graph --export` for consistent format |
| `❌ No experience graph found` | Missing graph file | Check `graph/experience.json` exists | Run `xos init` or specify `--graph` | Always initialize before compiling |
| `Missing intent` on node | Node lacks `intent` field | Run `xos validate` for specific nodes | Add `intent` to the node specification | Template generators include intent by default |
| `Screen missing frame_budget constraint` | Screen node incomplete | Inspect node with `xos graph --node` | Add `constraints.frame_budget` to node | Use `create_screen_node()` factory |
| `ModuleNotFoundError: python.core` | Wrong working directory | Run `pwd` | Navigate to repo root | Use absolute paths or shell aliases |

### 15.2 Graph Issues

| Symptom | Root Cause | Resolution |
|---|---|---|
| Circular dependency error | Nodes form a cycle | Remove or redirect one edge in the cycle |
| Dangling edge warning | Edge references nonexistent node | Create the missing node or remove the edge |
| Topological sort fails | Graph contains cycles | Break cycles by restructuring dependencies |

### 15.3 Agent Issues

| Symptom | Root Cause | Resolution |
|---|---|---|
| Agent produces no output | Missing input spec | Provide complete specification |
| Agent validation fails | Violated a validation rule | Check agent's validation rules in roster |
| Agent hangs | MCP server unreachable | Check MCP server status |

### 15.4 Environment Issues

| Symptom | Root Cause | Resolution |
|---|---|---|
| `xos: command not found` | Package not installed | `pip install -e .` |
| `Python version mismatch` | Wrong Python version | Use Python 3.12+ |
| PowerShell script fails | Missing execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Expo CLI not found | Node.js path issue | `npx expo --version` to verify |

### 15.5 IDE Issues

| Symptom | Resolution |
|---|---|
| Graph Viewer blank | Reload workspace: `Ctrl+Shift+P` → "Reload Window" |
| Terminal not responding | Kill terminal and reopen: `` Ctrl+` `` |
| AI Chat disconnected | Check MCP panel for server status |
| Problems panel empty after compile | Toggle panel: `Ctrl+Shift+M` |

---

## 16. Best Practices

### 16.1 Architecture

- **Single responsibility per node** — Each node represents exactly one concept
- **Feature isolation** — Features should not directly depend on other features
- **Screens compose components, not other screens** — Use navigation edges for screen-to-screen relationships
- **State is a first-class node** — Every Zustand store is a `state` node in the graph
- **Never skip the graph** — If a component exists, it must be in the graph

### 16.2 Specifications

- **Every screen specifies motion** — Entrance and exit animations are mandatory
- **Every interactive element specifies haptics** — Tapping without haptic feedback is a quality gate failure
- **Every screen specifies accessibility** — Heading, focus order, and semantic roles are required
- **Data sources are explicit** — Never assume data availability; declare it in the spec
- **Use the schema** — Validate specs against the schema before compiling

### 16.3 Graph Modeling

- **Name nodes consistently** — Use `kind:descriptive-name` format (e.g., `screen:home`, `comp:product-card`)
- **Model dependencies explicitly** — If component A uses component B, add the edge
- **Use the right edge kind** — `composes` for containment, `depends_on` for usage, `navigates_to` for routing
- **Keep the graph flat** — Avoid deep nesting; prefer many small nodes over few large ones
- **Version your graph** — Tag graph snapshots before major changes

### 16.4 Prompt Writing

- **Be specific** — "Generate a product card with image, title, price, and add-to-cart button" not "make a card"
- **Include constraints** — Specify spacing scale, typography tokens, motion curves
- **Reference knowledge patterns** — Use named patterns from the knowledge base
- **Define acceptance criteria** — What makes this output correct?

### 16.5 Performance

- **Motion: worklet-only** — All animations must run on the UI thread via Reanimated worklets
- **Lists: FlashList** — Any scrollable data must use FlashList, not FlatList or ScrollView
- **Frame budget: 16ms** — No render should exceed one frame
- **Image optimization** — Use Expo Image with proper caching
- **Lazy loading** — Screens and heavy components should be lazy-loaded

### 16.6 Accessibility

- **Touch targets ≥ 44pt** — Apple HIG minimum
- **Dynamic Type** — All text must scale with system font size
- **Reduced Motion** — Every animation must have a reduced-motion fallback
- **Screen reader labels** — Every interactive element needs an accessibility label
- **Focus order** — Logical tab order from top to bottom, left to right

### 16.7 Naming Conventions

| Concept | Convention | Example |
|---|---|---|
| Graph nodes | `kind:descriptive-name` | `screen:checkout`, `comp:payment-form` |
| Features | kebab-case | `product-browse`, `user-auth` |
| Screens | PascalCase + Screen suffix | `HomeScreen`, `ProductDetailScreen` |
| Components | PascalCase | `ProductCard`, `SearchBar` |
| State stores | camelCase + Store suffix | `cartStore`, `userStore` |
| Motion tokens | kebab-case | `entrance-fade`, `exit-slide-out` |
| Haptic patterns | camelCase | `lightImpact`, `notificationSuccess` |

### 16.8 Git Workflow

```
main                    # Production-ready, all gates passing
├── feat/*              # Feature branches
├── fix/*               # Bug fix branches
├── chore/*             # Maintenance branches
└── docs/*              # Documentation branches
```

- **Commit messages:** Conventional Commits format
- **Before merging to main:** `xos validate` must pass
- **Graph changes require review:** Tag a graph snapshot before and after

---

## 17. FAQ

### 17.1 General

**Q: What is XOS?**
A: XOS (Experience Operating System) is an AI-native engineering platform that compiles specifications into production-ready React Native + Expo applications through a deterministic 12-stage pipeline.

**Q: Why not just write React Native code directly?**
A: Direct code writing leads to design-implementation drift, inconsistent quality, and missed premium interactions (haptics, spring physics, gesture choreography). XOS guarantees that every pixel, animation, and interaction is intentional and validated.

**Q: Is XOS a code generator?**
A: XOS is an experience compiler. It transforms specifications through a validated graph into code — but the code is a compiled artifact, not the source of truth. The Experience Graph is authoritative.

### 17.2 Getting Started

**Q: How do I create my first project?**
```bash
xos init MyFirstApp
cd MyFirstApp
# Edit specs/app.spec.json
xos compile
```

**Q: What prerequisites do I need?**
A: Python 3.12+, Node.js 20+, pnpm, and Git. See [Section 2](#2-installation).

**Q: Do I need to know React Native?**
A: Understanding React Native helps with debugging and reviewing generated code, but XOS handles the implementation. You focus on specifications — what the app should do and how it should feel.

### 17.3 Experience Graph

**Q: What happens if I edit generated code directly?**
A: Your changes will be overwritten on the next compilation. Always modify specifications and knowledge patterns, then recompile.

**Q: How do I visualize the graph?**
A: Use the Graph Viewer in Antigravity IDE (`Ctrl+Shift+G`) or run:
```bash
xos graph
```

**Q: Can I have circular dependencies?**
A: No. The compiler rejects circular dependencies during the topological sort. Break cycles by introducing an intermediary node or restructuring dependencies.

### 17.4 Agents

**Q: How do I invoke a specific agent?**
A: Via CLI: `xos agent <name> --input '...'` or via AI Chat: `/agent <name>`

**Q: Can I create custom agents?**
A: Yes. Add an entry to `agents/agent-roster.json` with the agent's mission, inputs, outputs, skills, and validation rules.

**Q: Do agents run automatically?**
A: The compiler invokes agents in dependency order during the `AGENT_PLANNING` stage. You can also invoke them manually.

### 17.5 Quality Gates

**Q: What happens if a gate fails?**
A: The compiler halts and produces diagnostics — including the failing node, the rule violated, and an actionable fix.

**Q: Can I skip a gate?**
A: WARN-level gates (testing, documentation) can be bypassed. FAIL-level gates cannot — they must be resolved.

**Q: How do I add a custom gate?**
A: Implement a `GateFn` and register it with `QualityGatePipeline.register()`. See [Section 13.4](#134-adding-custom-gates).

### 17.6 Performance

**Q: What's the frame budget for animations?**
A: 16ms per frame (60fps). Motion nodes exceeding this budget are flagged by the performance gate.

**Q: Does XOS optimize images?**
A: The Expo engineer agent configures proper image caching, format selection, and lazy loading based on the specification.

### 17.7 Anti-Slop

**Q: What does the Anti-Slop Engine detect?**
A: Generic centered layouts, random spacing (off the 4/8/16/24/32/48 scale), inconsistent typography, missing haptics, gesture conflicts, accessibility violations, performance regressions, duplicate components, architecture drift, and prompt drift.

**Q: How do I run the Anti-Slop scan?**
```bash
xos anti-slop path/to/file.tsx
```

---

## 18. Glossary

### A

**Agent** — A domain-specialized AI worker that owns exactly one concern (e.g., motion, gesture, haptics). Agents validate, transform, and generate artifacts within their domain.

**Agent Roster** — The manifest (`agents/agent-roster.json`) defining all 19 XOS agents, their missions, inputs, outputs, skills, tools, and validation rules.

**Anti-Slop Engine** — A scanner that detects and rejects generic, low-quality generation patterns (random spacing, weak hierarchy, missing haptics, etc.).

**Antigravity IDE** — The primary development environment for XOS. Provides file editing, terminal access, AI chat, graph visualization, and compilation pipeline monitoring.

### C

**Compilation Stage** — One of 12 sequential steps in the compiler pipeline (SPEC_LOAD through CODE_GENERATION).

**Compilation Diagnostic** — A structured message (level, stage, node_id, suggestion) produced when the compiler encounters an issue.

**Compilation Result** — The output of a compilation run: success status, generated files, diagnostics, and artifact metadata.

**Constraint** — A rule enforced on a graph node (e.g., frame budget, touch target size, supported orientations).

### D

**Design Token** — A named visual value (color, spacing, typography, radius, shadow) stored in `knowledge/design-tokens/`.

**Deterministic Engineering** — The principle that given identical inputs, the compiler produces identical outputs — guaranteed.

### E

**Edge** — A relationship between two graph nodes, typed by `EdgeKind` (composes, depends_on, navigates_to, animates, etc.).

**EdgeKind** — Enum defining the 16 valid relationship types between graph nodes.

**Experience Compiler** — The 12-stage deterministic pipeline that transforms specifications into React Native + Expo code.

**Experience Graph** — The single source of truth — a directed graph where every application concept is a typed, validated node with explicit edges.

### F

**Feature Specification** — A JSON/YAML document defining a user-facing capability: screens, data sources, state, and interaction rules.

### G

**Graph Node** — A single concept in the Experience Graph (screen, component, motion token, gesture pattern, etc.) with a unique ID, type, intent, and constraints.

**Graph Validation** — Structural checks run on every graph load: missing intents, dangling edges, required constraints.

### H

**Haptic Pattern** — A named haptic feedback rule (lightImpact, mediumImpact, heavyImpact, notificationSuccess, etc.) defined in `knowledge/haptics/`.

### K

**Knowledge Graph** — A reusable library of design tokens, component patterns, motion curves, gesture profiles, haptic patterns, and accessibility rules.

### M

**MCP (Model Context Protocol)** — A standardized interface for communication between AI agents and external tools (filesystem, Git, Expo, Supabase, Figma, etc.).

**MCP Server** — A process that wraps an external system and exposes its capabilities as tools via the MCP protocol.

**Motion Token** — A named animation definition (spring config, duration, easing curve, interruptibility, frame budget) in `knowledge/motion/`.

### N

**Node Factory** — Typed constructor functions (`create_screen_node`, `create_component_node`, etc.) that enforce required fields per node type.

**NodeKind** — Enum defining the 22 valid node types (screen, component, navigation, state, motion_token, etc.).

**NodeType** — Alternative enum in `python/core/graph.py` defining 22 node categories (PRODUCT, SCREEN, COMPONENT, MOTION, etc.).

### P

**Pipeline Stage** — See Compilation Stage.

### Q

**Quality Gate** — A validation checkpoint in the compiler pipeline. 12 gates run in sequence — if any FAIL-level gate fails, the compiler halts.

**QualityGatePipeline** — The Python class that registers and executes gate functions in order.

### S

**Skill** — A reusable agent capability (generate_feature, audit_motion, generate_tests, etc.) defined in `skills/skill-registry.json`.

**Specification** — A structured JSON/YAML document describing what should exist — the entry point into XOS.

**Slop** — Generic, low-quality AI-generated output that XOS's Anti-Slop Engine detects and rejects.

### T

**Topological Sort** — A linear ordering of graph nodes where dependencies appear before dependents. Used for compilation ordering.

### V

**Validation Rule** — A constraint that an agent enforces on its output (e.g., "animations must be interruptible", "all touch targets ≥ 44pt").

### X

**XOS** — Experience Operating System. The AI-native engineering platform for building premium React Native + Expo applications.

---

*End of XOS Developer Handbook v1.0.0*

