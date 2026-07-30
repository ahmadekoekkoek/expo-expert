"""
Screen Compiler — composes motion, gesture, haptic, a11y, and component
artifacts into a single React Native + Expo screen component.
"""
from __future__ import annotations
from typing import Any


def compile_screen_group(
    screen_nodes: list[tuple[str, dict[str, Any]]],
    artifacts: dict[str, list[tuple[str, str]]],
) -> dict[str, str]:
    """Compile a group of screens and return {screen_id: code}."""
    results = {}
    for sid, meta in screen_nodes:
        try:
            results[sid] = compile_screen(sid, meta, artifacts)
        except Exception as e:
            results[sid] = f"// ERROR compiling {sid}: {e}"
    return results


def compile_screen(
    screen_id: str,
    screen_meta: dict[str, Any],
    artifacts: dict[str, list[tuple[str, str]]],
    all_nodes: dict[str, Any],
    edges: dict[str, list[str]],
) -> str:
    """
    Compose a complete React Native screen from its constituent artifacts.

    artifacts dict:
      "motion"       → [(node_id, code_str), ...]
      "gesture"      → [(node_id, code_str), ...]
      "haptic"       → [(node_id, code_str), ...]
      "accessibility" → [(node_id, code_str), ...]

    Returns a complete TSX file.
    """
    name = screen_meta.get("name", "UnnamedScreen")
    route = screen_meta.get("route", "/")
    description = screen_meta.get("description", "")
    components = screen_meta.get("components", [])
    data_source = screen_meta.get("dataSource", "")
    state_store = screen_meta.get("state", "")

    motion = screen_meta.get("motion", {})
    entrance = motion.get("entrance", "fade_in")
    exit_anim = motion.get("exit", "fade_in")
    gestures = screen_meta.get("gestures", [])
    haptics = screen_meta.get("haptics", [])
    a11y = screen_meta.get("accessibility", {})

    screen_node = f"screen:{name}"

    # ── Collect artifact nodes related to this screen ──
    related_motion = _find_node(f"motion:{screen_node}", artifacts["motion"])
    related_haptic = _find_nodes(
        [f"haptic:{screen_node}:{i}" for i in range(len(haptics))],
        artifacts["haptic"],
    )
    related_gesture = _find_nodes(
        [f"gesture:{screen_node}:{i}" for i in range(len(gestures))],
        artifacts["gesture"],
    )
    related_a11y = _find_node(f"a11y:{screen_node}", artifacts["accessibility"])

    # Component names (from spec)
    component_names = components  # ['prayer-card', 'jamaah-toggle', ...]

    # ── Build the file ──
    pascal = _to_pascal(name)
    lines: list[str] = []

    # Header
    lines.append(f"// {pascal} — {description}")
    lines.append(f"// Route: {route}")
    if data_source:
        lines.append(f"// Data: {data_source}")
    if state_store:
        lines.append(f"// State: {state_store}")
    lines.append("")

    # Imports
    lines.append('import React from "react";')
    lines.append('import { View, Text, Pressable } from "react-native";')
    lines.append('import Animated, { FadeInDown, FadeIn } from "react-native-reanimated";')
    lines.append('import * as Haptics from "expo-haptics";')
    lines.append("")

    # Component imports (placeholder — real imports come from component generator)
    for comp in component_names:
        comp_pascal = _to_pascal(comp)
        lines.append(
            f'import {{ {comp_pascal} }} from "@/components/{_to_kebab(comp)}";'
        )
    if component_names:
        lines.append("")

    # Motion
    lines.append("// ── Motion ──")
    if related_motion:
        lines.append("// (resolved from motion pattern registry)")
        # Extract the entering expression
        for _nid, code in [related_motion]:
            for cl in code.split("\n"):
                if "const entering" in cl:
                    lines.append(f"const screenEntering = {cl.split('= ')[1] if '= ' in cl else 'FadeIn.duration(300)'}")
    else:
        lines.append(f"const screenEntering = FadeIn.duration(300);")
    lines.append("")

    # Gestures
    has_gesture = len(related_gesture) > 0
    if has_gesture:
        lines.append('import { Gesture, GestureDetector } from "react-native-gesture-handler";')
    lines.append("// ── Gestures ──")
    for i, (_nid, code) in enumerate(related_gesture):
        var = f"gesture{i}"
        label = gestures[i] if i < len(gestures) else 'unnamed'
        lines.append(f"// {var}: {label}")
        for cl in code.split("\n"):
            if "const gesture" in cl:
                lines.append(cl.replace("const gesture", f"const {var}"))
                break
    if not related_gesture:
        lines.append("// (none)")
    lines.append("")

    # Haptics
    lines.append("// ── Haptics ──")
    haptic_fns = []
    for i, (_nid, code) in enumerate(related_haptic):
        for cl in code.split("\n"):
            if "Haptics." in cl and not cl.strip().startswith("//"):
                stripped = cl.strip().rstrip(";")
                fn = f"triggerHaptic{i}" if i > 0 else "triggerHaptic"
                haptic_fns.append(fn)
                lines.append(f"const {fn} = () => {{ {stripped}; }};")
                break
    if not related_haptic:
        lines.append("const triggerHaptic = () => {};")
        haptic_fns.append("triggerHaptic")
    lines.append("")

    # Component
    lines.append(f"export default function {pascal}() {{")
    lines.append(f"  const handlePrimaryAction = () => {{")
    lines.append(f"    triggerHaptic();")
    lines.append(f"  }};")
    lines.append("")
    lines.append("  return (")
    lines.append('    <Animated.View')
    a11y_role = a11y.get("role", "none")
    a11y_label = a11y.get("label", description)
    lines.append(f'      entering={{screenEntering}}')
    if a11y_role and a11y_role != "none":
        lines.append(f'      accessibilityRole="{a11y_role}"')
    if a11y_label:
        lines.append(f'      accessibilityLabel="{a11y_label}"')
    lines.append('      className="flex-1 bg-background px-4 pt-safe"')
    lines.append("    >")

    # Component tree
    for comp in component_names:
        comp_pascal = _to_pascal(comp)
        lines.append(f'      <{comp_pascal} onAction={{handlePrimaryAction}} />')

    lines.append("    </Animated.View>")
    lines.append("  );")
    lines.append("}")

    return "\n".join(lines)


def _find_node(node_id: str, artifacts: list[tuple[str, str]]) -> tuple[str, str] | None:
    for nid, code in artifacts:
        if nid == node_id:
            return (nid, code)
    return None


def _find_nodes(
    node_ids: list[str],
    artifacts: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for nid, code in artifacts:
        if nid in node_ids:
            result.append((nid, code))
    return result


def _to_pascal(s: str) -> str:
    return "".join(part.capitalize() for part in s.replace("-", " ").replace("_", " ").split())


def _to_kebab(s: str) -> str:
    return s.replace("_", "-").replace(" ", "-").lower()
