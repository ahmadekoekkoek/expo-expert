# XOS — AI-Native Experience Engineering Operating System

## Core Principle

Code is a compiled artifact. The Experience Graph is the source of truth.

## Pipeline

```
Specifications → Knowledge Graph → Experience Graph → Dependency Resolution
→ Constraint Validation → Agent Planning → Motion Compilation → Gesture Compilation
→ Haptic Compilation → Accessibility Compilation → Performance Optimization
→ React Native + Expo Code
```

## Technology Stack

### Mobile
- React Native, Expo, Expo Router, TypeScript, NativeWind, Reanimated
- React Native Gesture Handler, React Query, Zustand, React Hook Form, Zod

### Backend
- Supabase, Firebase, Appwrite, PocketBase, REST, GraphQL, tRPC

### Automation
- Python 3.13+, PowerShell 7+, Node.js, Bun, pnpm, Git, Docker

## Repository Structure

```
specs/          — Feature specifications (markdown, YAML, JSON schema)
graph/          — Experience graph definitions and serialization
knowledge/      — Reusable patterns, design tokens, motion curves, haptics
agents/         — Agent definitions (YAML manifests)
skills/         — Reusable agent skills
mcp/            — MCP server definitions and interfaces
python/         — Core Python orchestration runtime
powershell/     — Host automation and environment management
generators/     — Code generation templates and compilers
templates/      — Project, screen, and component templates
features/       — Feature implementations and generated artifacts
packages/       — Shared packages and libraries
shared/         — Shared utilities, types, constants
docs/           — Architecture decisions, guides, ADRs
tests/          — Test suites (unit, integration, e2e)
scripts/        — Utility scripts
```

## Quality Gates

1. Specification Validation
2. Graph Validation
3. Architecture Validation
4. Design Validation (motion, gesture, haptic, a11y, performance)
5. Testing
6. Documentation
7. Security Review
