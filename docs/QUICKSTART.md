# XOS Quickstart — From Idea to App

You have a PRD, a product spec, or just an app concept in your head. XOS compiles it into a React Native + Expo codebase.

No deep architecture knowledge required. You write specs. XOS compiles.

---

## The 3-step flow

```
PRD / App Concept  →  Spec files (JSON)  →  xos compile  →  Generated app code
```

## Step 1 — Initialize your project

```bash
xos init MyApp
cd MyApp
```

This creates the scaffold: `specs/`, `graph/`, `knowledge/`, `features/`, `tests/`.

## Step 2 — Write your spec files

Put one `.json` file per feature/screen under `specs/`. The minimum viable spec:

```json
{
  "name": "home",
  "version": "0.1.0",
  "description": "Home dashboard with prayer times and progress",
  "features": [
    {
      "name": "home-dashboard",
      "description": "Today's prayers, next-prayer countdown, Qur'an progress",
      "screens": [
        {
          "name": "home",
          "route": "/",
          "description": "Main dashboard",
          "components": ["prayer-card", "progress-ring", "greeting-header"],
          "motion": { "entrance": "fade_in" },
          "gestures": ["swipeRight (mark prayed)"],
          "haptics": ["lightImpact (log prayer)"],
          "accessibility": { "heading": "Assalamu alaikum", "focusOrder": "greeting → prayers → progress", "liveRegion": "polite" }
        }
      ]
    }
  ]
}
```

**The four fields that make premium experiences:**

| Field | What it does |
|---|---|
| `motion` | Defines entrance/exit animations (fade_in, slide_up, noor_bloom, etc.) |
| `gestures` | Swipe/pan/tap/pinch interactions on the screen |
| `haptics` | When the phone vibrates (lightImpact, success, etc.) |
| `accessibility` | Screen reader labels, focus order, dynamic type support |

Every component you list under `components` gets generated with proper props, state hooks, and these four layers baked in.

**Design tokens** go in `specs/app.spec.json`:

```json
{
  "name": "MyApp",
  "version": "0.1.0",
  "description": "My product",
  "navigation": { "type": "tab", "tabs": [ ... ] },
  "features": ["home", "profile"],
  "design_tokens": {
    "color_tokens": { "primary": "#0A84FF", "background": "#FFFFFF", ... },
    "spacing": { "xs": 4, "sm": 8, "md": 16, ... },
    "type_scale": { "body": 14, "h1": 32, ... }
  },
  "motion_tokens": {
    "presets": {
      "fade_in": { "duration": 300, "easing": "ease-out" },
      "slide_up": { "duration": 400, "easing": "spring" }
    }
  },
  "haptic_tokens": {
    "presets": {
      "success": "notificationSuccess",
      "lightImpact": "impactLight"
    }
  }
}
```

Motion patterns can also live in `knowledge/motion/motion-patterns.json` for reuse across projects.

## Step 3 — Compile

```bash
xos compile --spec specs/
```

That's it. XOS:

1. Loads all `.json` files from `specs/`
2. Builds an Experience Graph (feature → screen → component hierarchy)
3. Runs 12 quality gates (motion, gesture, haptic, a11y, performance, etc.)
4. Generates code into `features/`

Output structure:
```
features/
├── motion/          ← Reanimated animation code per screen
├── gestures/        ← Gesture Handler definitions
├── haptics/         ← expo-haptics calls
└── accessibility/   ← a11y role/label/focus-order declarations
```

## Stage-level control

Run one stage at a time:

```bash
xos compile --spec specs/ --stage MOTION_COMPILATION     # Only animations
xos compile --spec specs/ --stage HAPTIC_COMPILATION      # Only haptics
xos compile --spec specs/ --stop-at DEPENDENCY_RESOLUTION  # Stop early
```

Available stages: `DEPENDENCY_RESOLUTION`, `CONSTRAINT_VALIDATION`, `AGENT_PLANNING`, `MOTION_COMPILATION`, `GESTURE_COMPILATION`, `HAPTIC_COMPILATION`, `ACCESSIBILITY_COMPILATION`, `PERFORMANCE_OPTIMIZATION`, `CODE_GENERATION`.

## Validate without generating code

```bash
xos validate --graph graph/experience.json
```

Runs all quality gates against the experience graph. Use this after writing specs but before a full compile to catch issues early.

## Anti-slop check

```bash
xos anti-slop features/some-file.tsx
```

Scans generated code for generic boilerplate patterns and flags them with specific fixes.

## That's it

1. You write specs describing what you want.
2. XOS compiles them into production React Native + Expo outputs.
3. You wire the outputs into your Expo project.

For deep architecture, agent system, MCP, and advanced customization, see the [Developer Handbook](xos-developer-handbook.md).
