"""
Motion Generator — compiles motion specification nodes into Reanimated animation code.
"""
import json
from typing import Any


def load_motion_patterns(path: str = "knowledge/motion/motion-patterns.json") -> dict:
    with open(path) as f:
        return json.load(f)


def compile_motion(motion_spec: dict, pattern_registry: dict) -> str:
    """
    Given a motion specification (from the experience graph or screen spec),
    produce the Reanimated animation code block.
    """
    pattern_name = motion_spec.get("animation") or motion_spec.get("entrance", "fadeIn")
    patterns = pattern_registry.get("patterns", {})
    pattern = patterns.get(pattern_name)

    if not pattern:
        return f"// Motion: {pattern_name} (pattern not found — falling back to FadeIn)\nimport {{ FadeIn }} from 'react-native-reanimated';\nconst entering = FadeIn.duration(300);"

    anim = pattern["animation"]
    easing_str = _map_easing(anim.get("easing", "easing.default"))
    duration = _resolve_duration(anim.get("duration", "duration.default"))

    from_vals = anim.get("from", {})
    to_vals = anim.get("to", {})

    lines = [f"// Motion: {pattern['name']} — {pattern['intent']}"]
    lines.append("import Animated, {")
    lines.append("  useAnimatedStyle," if "physics" not in anim else "  withSpring,")
    lines.append("  withTiming,")
    lines.append(f"}} from 'react-native-reanimated';")

    if "physics" in anim:
        physics = anim["physics"]
        lines.append(f"// Physics: damping={physics['damping']}, stiffness={physics['stiffness']}, mass={physics['mass']}")

    lines.append(f"\nconst entering = {_generate_entering(anim, from_vals, to_vals, duration, easing_str)};")
    lines.append(f"// Frame budget: {pattern.get('frameBudget', 3)} frames")
    lines.append(f"// Interruptible: {pattern.get('interruptible', True)}")
    if pattern.get("reducedMotionFallback"):
        lines.append(f"// Reduced motion fallback: {pattern['reducedMotionFallback']}")

    return "\n".join(lines)


def _generate_entering(anim: dict, from_vals: dict, to_vals: dict, duration: int, easing: str) -> str:
    """Generate the entering animation expression."""
    # For simplicity, use the built-in entering animations
    has_opacity = "opacity" in from_vals
    has_translate_y = "translateY" in from_vals
    has_translate_x = "translateX" in from_vals
    has_scale = "scale" in from_vals

    if has_opacity and has_translate_y:
        anim_name = "FadeInDown"
    elif has_opacity and has_translate_x:
        anim_name = "FadeInRight"
    elif has_opacity and has_scale:
        anim_name = "FadeIn"
    elif has_opacity:
        anim_name = "FadeIn"
    else:
        anim_name = "FadeIn"

    return f"{anim_name}.duration({duration}).easing({easing})"


def _map_easing(easing_key: str) -> str:
    """Map named easing to Reanimated easing function."""
    mapping = {
        "easing.default": "(t) => t",
        "easing.decelerate": "(t) => t",
        "easing.accelerate": "(t) => t",
        "easing.bounce": "(t) => t",
    }
    return mapping.get(easing_key, "(t) => t)")


def _resolve_duration(duration_key: str) -> int:
    """Resolve named duration to milliseconds."""
    mapping = {
        "duration.instant": 100,
        "duration.fast": 200,
        "duration.default": 300,
        "duration.slow": 500,
        "duration.entrance": 600,
        "duration.exit": 400,
    }
    return mapping.get(duration_key, 300)


def compile_gesture(gesture_spec: dict) -> str:
    """Compile a gesture specification into Gesture Handler code."""
    gesture_type = gesture_spec.get("gesture", "Pan")
    trigger = gesture_spec.get("trigger", {})
    priority = gesture_spec.get("priority", "medium")
    haptic = gesture_spec.get("haptic", "lightImpact")

    lines = [f"// Gesture: {gesture_spec.get('name', 'unnamed')} — {gesture_type} ({priority} priority)"]
    lines.append("import { Gesture, GestureDetector } from 'react-native-gesture-handler';")
    lines.append("import Animated, { runOnJS } from 'react-native-reanimated';")
    lines.append("import * as Haptics from 'expo-haptics';")
    lines.append("")

    if gesture_type == "Pan":
        threshold = trigger.get("threshold", 80)
        direction = trigger.get("direction", "vertical")
        lines.append(f"const gesture = Gesture.Pan()")
        lines.append(f"  .activeOffset{_capitalize(direction)}({threshold})")
        lines.append(f"  .onEnd((event) => {{")
        lines.append(f"    if (event.velocity{_capitalize(direction)} > 500) {{")
        lines.append(f"      runOnJS(handleGesture)();")
        lines.append(f"    }}")
        lines.append(f"  }});")

    elif gesture_type == "Tap":
        taps = trigger.get("numberOfTaps", 1)
        lines.append(f"const gesture = Gesture.Tap()")
        lines.append(f"  .numberOfTaps({taps})")
        lines.append(f"  .onEnd(() => {{")
        lines.append(f"    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.{_map_haptic(haptic)});")
        lines.append(f"    runOnJS(handleGesture)();")
        lines.append(f"  }});")

    elif gesture_type == "LongPress":
        min_duration = trigger.get("minDurationMs", 500)
        lines.append(f"const gesture = Gesture.LongPress()")
        lines.append(f"  .minDuration({min_duration})")
        lines.append(f"  .onStart(() => {{")
        lines.append(f"    Haptics.selectionAsync();")
        lines.append(f"    runOnJS(handleGesture)();")
        lines.append(f"  }});")

    elif gesture_type == "Pinch":
        lines.append(f"const gesture = Gesture.Pinch()")
        lines.append(f"  .onUpdate((event) => {{")
        lines.append(f"    scale.value = event.scale;")
        lines.append(f"  }})")
        lines.append(f"  .onEnd(() => {{")
        lines.append(f"    scale.value = withSpring(Math.max(0.5, Math.min(3, scale.value)));")
        lines.append(f"  }});")

    lines.append("")
    lines.append(f"// Usage: <GestureDetector gesture={{gesture}}><View>...</View></GestureDetector>")
    return "\n".join(lines)


def _capitalize(s: str) -> str:
    return s.capitalize() if s else s


def _map_haptic(intent: str) -> str:
    mapping = {
        "lightImpact": "Light",
        "mediumImpact": "Medium",
        "heavyImpact": "Heavy",
        "selection": "Light",
    }
    return mapping.get(intent, "Light")
