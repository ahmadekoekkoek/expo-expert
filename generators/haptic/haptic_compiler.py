"""
Haptic Generator — compiles haptic specification into expo-haptics calls.
"""
from typing import Any


HAPTIC_PATTERNS = {
    "lightImpact": {
        "ios": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)",
        "android": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)",
    },
    "mediumImpact": {
        "ios": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)",
        "android": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)",
    },
    "heavyImpact": {
        "ios": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)",
        "android": "Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)",
    },
    "selection": {
        "ios": "Haptics.selectionAsync()",
        "android": "Haptics.selectionAsync()",
    },
    "notificationSuccess": {
        "ios": "Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)",
        "android": "Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)",
    },
    "notificationError": {
        "ios": "Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)",
        "android": "Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)",
    },
    "none": {
        "ios": "// No haptic",
        "android": "// No haptic",
    },
}


def compile_haptics(haptic_spec: dict) -> str:
    """
    Given a haptic specification, produce the expo-haptics call.
    """
    intent = haptic_spec.get("intent") or haptic_spec.get("name", "lightImpact")

    pattern = HAPTIC_PATTERNS.get(intent)
    if not pattern:
        return f"// Haptic: unknown pattern '{intent}' — using lightImpact\nHaptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);"

    lines = [
        f"// Haptic: {intent} — {haptic_spec.get('description', '')}",
        "import * as Haptics from 'expo-haptics';",
        "",
        f"{pattern['ios']};",
    ]
    return "\n".join(lines)


def compile_accessibility(a11y_spec: dict) -> str:
    """
    Given an accessibility specification, produce the React Native accessibility props.
    """
    role = a11y_spec.get("role", "none")
    label = a11y_spec.get("label", a11y_spec.get("heading", ""))
    heading = a11y_spec.get("heading", "")
    focus_order = a11y_spec.get("focusOrder", "")

    lines = [f"// Accessibility: role={role}, heading={heading}"]

    props = []
    if role and role != "none":
        props.append(f'accessibilityRole="{role}"')
    if label:
        props.append(f'accessibilityLabel="{label}"')
    if role == "header":
        props.append('accessibilityRole="header"')

    if props:
        lines.append("// Props: " + " | ".join(props))

    lines.append("// Focus order: " + (focus_order or "natural document order"))
    lines.append("// Touch targets: min 44x44pt")
    lines.append("// Reduced motion: respected via AccessibilityInfo.isReduceMotionEnabled()")
    lines.append("// Dynamic type: use relative font sizes, not fixed px")

    return "\n".join(lines)
