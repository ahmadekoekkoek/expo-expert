"""
XOS Knowledge Graph — reusable, curated patterns for React Native + Expo development.

Agents reference this graph. Never invent unsupported patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeEntry:
    category: str
    name: str
    description: str
    pattern: str
    example: str = ""
    constraints: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


DESIGN_TOKENS: dict[str, dict] = {
    "spacing": {
        "xs": 4,
        "sm": 8,
        "md": 16,
        "lg": 24,
        "xl": 32,
        "2xl": 48,
        "3xl": 64,
    },
    "radius": {
        "none": 0,
        "sm": 4,
        "md": 8,
        "lg": 12,
        "xl": 16,
        "full": 9999,
    },
    "type_scale": {
        "caption": 12,
        "body-sm": 13,
        "body": 14,
        "body-lg": 16,
        "h4": 18,
        "h3": 20,
        "h2": 24,
        "h1": 32,
        "display": 40,
    },
    "font_weight": {
        "regular": "400",
        "medium": "500",
        "semibold": "600",
        "bold": "700",
    },
    "color_tokens": {
        "primary": "#0A84FF",
        "primary_foreground": "#FFFFFF",
        "secondary": "#5E5CE6",
        "background": "#FFFFFF",
        "surface": "#F2F2F7",
        "text": "#000000",
        "text_secondary": "#8E8E93",
        "border": "#C6C6C8",
        "error": "#FF3B30",
        "success": "#34C759",
        "warning": "#FF9500",
    },
    "dark_color_tokens": {
        "primary": "#0A84FF",
        "primary_foreground": "#FFFFFF",
        "secondary": "#5E5CE6",
        "background": "#000000",
        "surface": "#1C1C1E",
        "text": "#FFFFFF",
        "text_secondary": "#8E8E93",
        "border": "#38383A",
        "error": "#FF453A",
        "success": "#30D158",
        "warning": "#FF9F0A",
    },
}

MOTION_TOKENS: dict[str, dict] = {
    "duration": {
        "instant": 0,
        "fast": 150,
        "normal": 300,
        "slow": 500,
        "entrance": 400,
        "exit": 250,
    },
    "curves": {
        "ease_out": "cubic-bezier(0, 0, 0.58, 1)",
        "ease_in": "cubic-bezier(0.42, 0, 1, 1)",
        "ease_in_out": "cubic-bezier(0.42, 0, 0.58, 1)",
        "spring_gentle": "spring(1, 0.9, 10)",
        "spring_bouncy": "spring(1, 0.7, 15)",
        "spring_snappy": "spring(1, 0.95, 30)",
    },
    "presets": {
        "fade_in": {"from": {"opacity": 0}, "to": {"opacity": 1}, "duration": "fast"},
        "slide_up": {"from": {"translateY": 20, "opacity": 0}, "to": {"translateY": 0, "opacity": 1}, "duration": "entrance"},
        "scale_in": {"from": {"scale": 0.95, "opacity": 0}, "to": {"scale": 1, "opacity": 1}, "duration": "fast"},
        "press_scale": {"from": {"scale": 1}, "to": {"scale": 0.97}, "duration": "fast"},
    },
}

HAPTIC_TOKENS: dict[str, Any] = {
    "light": {
        "intent": "Subtle feedback for non-critical interactions.",
        "ios": "impactAsync(ImpactStyle.Light)",
        "android": "HapticFeedbackConstants.KEYBOARD_TAP",
    },
    "medium": {
        "intent": "Standard feedback for toggles, selections.",
        "ios": "impactAsync(ImpactStyle.Medium)",
        "android": "HapticFeedbackConstants.CONTEXT_CLICK",
    },
    "heavy": {
        "intent": "Strong feedback for confirmations, arrivals.",
        "ios": "impactAsync(ImpactStyle.Heavy)",
        "android": "HapticFeedbackConstants.LONG_PRESS",
    },
    "success": {
        "intent": "Positive outcome notification.",
        "ios": "notificationAsync(NotificationType.Success)",
        "android": "HapticFeedbackConstants.CONFIRM",
    },
    "warning": {
        "intent": "Caution or attention needed.",
        "ios": "notificationAsync(NotificationType.Warning)",
        "android": "HapticFeedbackConstants.REJECT",
    },
    "error": {
        "intent": "Error or failure notification.",
        "ios": "notificationAsync(NotificationType.Error)",
        "android": "HapticFeedbackConstants.REJECT",
    },
}

ARCHITECTURE_PATTERNS: list[KnowledgeEntry] = [
    KnowledgeEntry(
        category="architecture",
        name="feature-slice",
        description="Organize code by feature, each with its own components, hooks, stores, and types.",
        pattern="features/<feature-name>/components/, hooks/, stores/, types/, utils/, index.ts",
        tags=["structure", "scalability"],
    ),
    KnowledgeEntry(
        category="architecture",
        name="shared-kernel",
        description="Shared UI components, design tokens, and utilities live in shared/.",
        pattern="shared/ui/, shared/hooks/, shared/utils/, shared/types/, shared/constants/",
        tags=["structure", "dry"],
    ),
    KnowledgeEntry(
        category="architecture",
        name="navigation-pattern",
        description="Expo Router file-based routing with typed routes.",
        pattern="app/(tabs)/, app/(stack)/, app/_layout.tsx, app/index.tsx",
        tags=["navigation", "expo-router"],
    ),
]

COMPONENT_PATTERNS: list[KnowledgeEntry] = [
    KnowledgeEntry(
        category="component",
        name="pressable-card",
        description="Touchable card with scale animation, haptics, and accessibility.",
        pattern="Pressable + Animated.View + accessibility props + Haptics on press",
        example=(
            "const Card = ({ onPress, children }) => {\n"
            "  const scale = useSharedValue(1);\n"
            "  const animatedStyle = useAnimatedStyle(() => ({\n"
            "    transform: [{ scale: scale.value }],\n"
            "  }));\n"
            "  const handlePressIn = () => { scale.value = withSpring(0.97); };\n"
            "  const handlePressOut = () => { scale.value = withSpring(1); };\n"
            "  return (<Pressable onPressIn={handlePressIn} onPressOut={handlePressOut}\n"
            "    onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); onPress(); }}\n"
            "    accessibilityRole=\"button\"><Animated.View style={animatedStyle}>{children}</Animated.View></Pressable>);\n"
            "};"
        ),
        tags=["pressable", "animation", "haptics", "accessibility"],
    ),
    KnowledgeEntry(
        category="component",
        name="skeleton-loader",
        description="Shimmer placeholder for loading states with reduced motion support.",
        pattern="Animated.View with linear gradient shimmer, skips animation when reduced motion.",
        tags=["loading", "animation", "accessibility"],
    ),
    KnowledgeEntry(
        category="component",
        name="form-field",
        description="Controlled form field with React Hook Form + Zod validation, error states, and haptic error feedback.",
        pattern="Controller + TextInput + error animation + Haptics on validation error",
        tags=["form", "validation", "haptics", "accessibility"],
    ),
]

GESTURE_PATTERNS: list[KnowledgeEntry] = [
    KnowledgeEntry(
        category="gesture",
        name="swipeable-row",
        description="Swipe-to-reveal actions with velocity-based snap and haptic confirmation.",
        pattern="Gesture.Pan() -> withDecay/withSpring snap -> haptic on action reveal",
        constraints={"min_velocity": 500, "activation_threshold": 60, "snap_points": [0, -160]},
        tags=["gesture", "list", "haptics"],
    ),
    KnowledgeEntry(
        category="gesture",
        name="pull-to-refresh",
        description="Pull down to refresh with animated indicator, haptic on trigger.",
        pattern="Gesture.Pan() vertical only + refresh control + haptic on refresh",
        constraints={"activation_distance": 80, "max_pull": 120},
        tags=["gesture", "refresh", "haptics"],
    ),
    KnowledgeEntry(
        category="gesture",
        name="pinch-to-zoom",
        description="Two-finger pinch zoom with boundaries and double-tap to reset.",
        pattern="Gesture.Pinch() + Gesture.Pan() composed, clamped scale 1-5x",
        constraints={"min_scale": 1, "max_scale": 5, "double_tap_reset": True},
        tags=["gesture", "image", "zoom"],
    ),
]

EXPO_BEST_PRACTICES: list[KnowledgeEntry] = [
    KnowledgeEntry(
        category="expo",
        name="expo-router-layouts",
        description="Use group layouts for shared UI shells. Stack for modals. Tabs for primary nav.",
        pattern="app/(tabs)/_layout.tsx with Tab, app/(modals)/_layout.tsx with Stack presentation:'modal'",
        tags=["expo-router", "navigation"],
    ),
    KnowledgeEntry(
        category="expo",
        name="env-config",
        description="Use expo-constants for env vars. Never hardcode API keys or secrets.",
        pattern="Constants.expoConfig?.extra?.apiUrl via app.config.ts extra field",
        tags=["expo", "security", "config"],
    ),
    KnowledgeEntry(
        category="expo",
        name="asset-preloading",
        description="Preload fonts and images in _layout.tsx with useFonts and Asset.loadAsync.",
        pattern="useFonts({...}) in root layout, splash screen until loaded",
        tags=["expo", "performance", "assets"],
    ),
    KnowledgeEntry(
        category="expo",
        name="status-bar-theming",
        description="Set StatusBar style per screen via StatusBar from expo-status-bar.",
        pattern="StatusBar style='dark'|'light' in screen components",
        tags=["expo", "ui"],
    ),
]

ALL_KNOWLEDGE: list[KnowledgeEntry] = (
    ARCHITECTURE_PATTERNS + COMPONENT_PATTERNS + GESTURE_PATTERNS + EXPO_BEST_PRACTICES
)


def get_by_category(category: str) -> list[KnowledgeEntry]:
    return [e for e in ALL_KNOWLEDGE if e.category == category]


def get_by_tag(tag: str) -> list[KnowledgeEntry]:
    return [e for e in ALL_KNOWLEDGE if tag in e.tags]


def get_design_tokens() -> dict:
    return DESIGN_TOKENS


def get_motion_tokens() -> dict:
    return MOTION_TOKENS


def get_haptic_tokens() -> dict:
    return HAPTIC_TOKENS
