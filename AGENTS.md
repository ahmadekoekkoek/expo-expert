# expoexpert — AGENTS.md

## What this is

**XOS** — an AI-Native Experience Engineering Operating System for building React Native + Expo mobile applications.  
It generates **deterministic user experiences**, not merely source code.

## Core principle

> Code is a compiled artifact. The Experience Graph is the source of truth.

## Project routing

| Directory | Purpose |
|---|---|
| `specs/` | Feature & screen specifications (JSON / YAML) |
| `graph/` | Experience Graph snapshots (nodes + edges) |
| `knowledge/` | Reusable patterns: design tokens, motion, gestures, haptics, a11y, prompts |
| `agents/` | Agent definitions — each owns one domain |
| `skills/` | Reusable agent skills (generate_screen, audit_gestures, ...) |
| `mcp/` | MCP server definitions & interfaces |
| `python/` | Orchestration: CLI, graph engine, compiler, validators, generators |
| `powershell/` | Host automation: bootstrap, environment checks, builds |
| `generators/` | Code generators: motion, gesture, haptic, a11y, screen, component |
| `templates/` | Project, screen, component, and feature templates |
| `features/` | Per-feature generated artifacts |
| `packages/` | Shared packages |
| `tests/` | Unit, integration, E2E |
| `scripts/` | Ad-hoc automation |

## Compiler pipeline

```
Specification → Knowledge Graph → Experience Graph → Dependency Resolution
→ Constraint Validation → Agent Planning → Motion/Gesture/Haptic Compilation
→ Accessibility Validation → Performance Optimization → React Native + Expo Code
```

Every stage must pass its quality gate. If any gate fails, the compiler **stops** and produces actionable diagnostics.

## Technology stack

**Mobile**: React Native, Expo, Expo Router, TypeScript, NativeWind, Reanimated, Gesture Handler, React Query, Zustand, React Hook Form, Zod, MMKV, FlashList, Skia  
**Backend**: Supabase, Firebase, Appwrite, PocketBase, REST, GraphQL, tRPC  
**Automation**: Python 3.13+, PowerShell 7+, Node.js, Bun, pnpm  
**AI**: Claude Code, OpenAI Codex, Cursor, Gemini CLI, Continue, RooCode

## Critical invariants

1. Never generate React Native code directly — always compile through the pipeline.
2. Every feature must define motion, gesture, haptic, and accessibility nodes.
3. Use Zod for all form and API validation.
4. State: Zustand + MMKV persistence.
5. Navigation: Expo Router (file-based).
6. Styling: NativeWind.
7. Animations: Reanimated, worklet-driven physics.
8. Lists: FlashList for any scrollable data.
9. Reject generic, boilerplate-heavy output (Anti-AI Slop Engine).
10. Explain every rejection with a deterministic fix.

## Quality gates (12)

Specification → Graph → Architecture → Design → Motion → Gesture → Haptic → Accessibility → Performance → Testing → Documentation → Security

All must pass before code is emitted.

## CLI

```bash
xos compile [--spec SPEC]   # Compile a project
xos knowledge               # Knowledge graph stats
xos validate                # Run quality gates
xos bootstrap PROJECT       # Create a new XOS project
xos prompt "..."            # Classify a natural-language intent
xos ps:env --check          # Validate PowerShell environment
```
