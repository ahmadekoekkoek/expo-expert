# XOS — AI-Native Experience Engineering Operating System

Build mobile apps through a **deterministic experience compiler**, not by hand-writing React Native source code.

## How it works

```
PRD / App Concept  →  Spec files (JSON)  →  xos compile  →  Generated app code
```

1. **You write specs** — screens, flows, brand tokens, interaction requirements in JSON.
2. **XOS compiles** through 12 quality gates into a production-ready Expo + React Native codebase.
3. **You get real code** — Reanimated animations, Gesture Handler definitions, haptic patterns, and a11y declarations per screen, all in `features/`.

[📖 Full Quickstart Guide →](docs/QUICKSTART.md)

## Quick commands

```bash
xos init MyApp              # Scaffold a new project
xos compile --spec specs/   # Full pipeline: specs → graph → code
xos validate                # Run quality gates without generating code
xos compile --stage MOTION_COMPILATION   # Only animations
xos compile --stop-at CONSTRAINT_VALIDATION  # Stop early for debugging
```

## Philosophy

> Humans define intent. Specifications define requirements. Graphs define relationships. Agents execute tasks.
> Python orchestrates workflows. PowerShell manages host automation.
> The Experience Compiler produces React Native + Expo applications.

## License

MIT
