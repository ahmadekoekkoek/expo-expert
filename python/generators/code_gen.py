"""
XOS Code Generators — compile graph nodes into React Native + Expo source files.

Each generator takes graph nodes as input and produces deterministically
structured TypeScript/TSX output that passes all quality gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.graph import GraphNode, NodeType


@dataclass
class GeneratedFile:
    path: Path
    content: str
    node_ids: list[str] = field(default_factory=list)

    def write(self, base_dir: Path) -> Path:
        full_path = base_dir / self.path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(self.content)
        return full_path


def generate_screen(node: GraphNode, design_tokens: dict | None = None) -> GeneratedFile:
    """Compile a SCREEN node into an Expo Router screen file."""
    metadata = node.metadata
    name = metadata.get("name", "Screen")
    route = metadata.get("route", "")
    component_name = "".join(w.capitalize() for w in name.replace("-", " ").split())

    imports = [
        "import React, { useCallback } from 'react';",
        "import { View, Text, StyleSheet, Pressable, Platform } from 'react-native';",
        "import { useSafeAreaInsets } from 'react-native-safe-area-context';",
        "import * as Haptics from 'expo-haptics';",
    ]

    content = f"""{'\\n'.join(imports)}

export default function {component_name}() {{
  const insets = useSafeAreaInsets();

  const handlePress = useCallback(() => {{
    if (Platform.OS !== 'web') {{
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }}
  }}, []);

  return (
    <View
      style={[
        styles.container,
        {{ paddingTop: insets.top, paddingBottom: insets.bottom }},
      ]}
      accessibilityRole="none"
    >
      <View style={{styles.header}} accessibilityRole="header">
        <Text style={{styles.title}} accessibilityRole="text">{name}</Text>
      </View>
      <View style={{styles.content}} accessibilityRole="none">
        <Text style={{styles.body}} accessibilityRole="text">
          {node.intent}
        </Text>
      </View>
      <View style={{styles.actions}} accessibilityRole="none">
        <Pressable
          onPress={{handlePress}}
          style={{{{ pressed }}}} => [
            styles.button,
            pressed && styles.buttonPressed,
          ]}
          accessibilityRole="button"
          accessibilityLabel={`{name} primary action`}
        >
          <Text style={{styles.buttonText}}>Continue</Text>
        </Pressable>
      </View>
    </View>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: tokens?.background ?? '#FFFFFF',
  }},
  header: {{
    paddingHorizontal: 24,
    paddingVertical: 16,
  }},
  title: {{
    fontSize: 32,
    fontWeight: '700',
    color: tokens?.text ?? '#000000',
  }},
  content: {{
    flex: 1,
    paddingHorizontal: 24,
  }},
  body: {{
    fontSize: 16,
    lineHeight: 24,
    color: tokens?.text_secondary ?? '#8E8E93',
  }},
  actions: {{
    paddingHorizontal: 24,
    paddingVertical: 16,
  }},
  button: {{
    backgroundColor: tokens?.primary ?? '#0A84FF',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    minHeight: 48,
  }},
  buttonPressed: {{
    opacity: 0.8,
    transform: [{{ scale: 0.98 }}],
  }},
  buttonText: {{
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '600',
  }},
}});
"""

    file_name = name.lower().replace(" ", "-") + ".tsx"
    route_dir = route.strip("/") if route else "features"
    return GeneratedFile(
        path=Path(route_dir) / file_name,
        content=content,
        node_ids=[node.id],
    )


def generate_component(node: GraphNode, design_tokens: dict | None = None) -> GeneratedFile:
    """Compile a COMPONENT node into a reusable React Native component."""
    metadata = node.metadata
    name = metadata.get("name", "Component")
    component_name = "".join(w.capitalize() for w in name.replace("-", " ").split())
    props_schema = metadata.get("props_schema", {})

    props_type = f"type {component_name}Props = {{\n"
    for prop_name, prop_type in props_schema.items():
        props_type += f"  {prop_name}: {prop_type};\n"
    props_type += "};\n"

    content = f"""import React from 'react';
import {{ View, Text, StyleSheet, Pressable, Platform }} from 'react-native';
import * as Haptics from 'expo-haptics';

{props_type if props_schema else ''}
export default function {component_name}({{ ...props }}: {component_name}Props) {{
  const handlePress = () => {{
    if (Platform.OS !== 'web') {{
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }}
  }};

  return (
    <Pressable
      onPress={{handlePress}}
      style={{{{ pressed }}}} => [
        styles.container,
        pressed && styles.pressed,
      ]}
      accessibilityRole="button"
      accessibilityLabel="{{{name} button}}"
      testID="{{{name}}}-component"
    >
      <Text style={{styles.label}}>{name}</Text>
    </Pressable>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    padding: 16,
    borderRadius: 12,
    backgroundColor: tokens?.surface ?? '#F2F2F7',
    minHeight: 48,
    justifyContent: 'center',
    alignItems: 'center',
  }},
  pressed: {{
    opacity: 0.7,
    transform: [{{ scale: 0.98 }}],
  }},
  label: {{
    fontSize: 16,
    fontWeight: '600',
    color: tokens?.primary ?? '#0A84FF',
  }},
}});
"""

    file_name = name.lower().replace(" ", "-") + ".tsx"
    return GeneratedFile(
        path=Path("shared") / "ui" / file_name,
        content=content,
        node_ids=[node.id],
    )


def generate_navigation(node: GraphNode) -> GeneratedFile:
    """Compile a NAVIGATION node into Expo Router layout configuration."""
    metadata = node.metadata
    source = metadata.get("source_screen", "")
    target = metadata.get("target_screen", "")

    content = f"""// Navigation route from {source or 'root'} → {target or 'target'}
// Animation: {node.constraints.get('animation', 'slide')}

import {{ Stack }} from 'expo-router';
import {{ Platform }} from 'react-native';

export default function Layout() {{
  return (
    <Stack
      screenOptions={{{{
        headerShown: true,
        animation: '{node.constraints.get('animation', 'slide')}',
        animationDuration: 300,
        gestureEnabled: true,
        contentStyle: {{{{ backgroundColor: '#FFFFFF' }}}},
      }}}}
    >
      <Stack.Screen
        name="{source or 'index'}"
        options={{{{
          title: '{source or 'Home'}',
        }}}}
      />
      <Stack.Screen
        name="{target or 'detail'}"
        options={{{{
          title: '{target or 'Detail'}',
          presentation: 'card',
        }}}}
      />
    </Stack>
  );
}}
"""

    return GeneratedFile(
        path=Path("app") / "_layout.tsx",
        content=content,
        node_ids=[node.id],
    )


def generate_motion(node: GraphNode) -> GeneratedFile:
    """Compile a MOTION node into Reanimated animation code."""
    metadata = node.metadata
    name = metadata.get("name", "animation")
    duration = node.constraints.get("duration_ms", 300)
    curve = node.constraints.get("curve", "ease-out")

    content = f"""import {{ useSharedValue, useAnimatedStyle, withTiming, withSpring, Easing }} from 'react-native-reanimated';
import {{ useReducedMotion }} from 'react-native-reanimated';

export function use{name.capitalize()}Animation() {{
  const reducedMotion = useReducedMotion();
  const progress = useSharedValue(0);
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(20);

  const animatedStyle = useAnimatedStyle(() => ({{
    opacity: opacity.value,
    transform: [{{ translateY: translateY.value }}],
  }}));

  const animateIn = () => {{
    if (reducedMotion) {{
      opacity.value = 1;
      translateY.value = 0;
      return;
    }}
    opacity.value = withTiming(1, {{
      duration: {duration},
      easing: Easing.out(Easing.cubic),
    }});
    translateY.value = withSpring(0, {{
      damping: 20,
      stiffness: 200,
    }});
  }};

  const animateOut = () => {{
    if (reducedMotion) {{
      opacity.value = 0;
      return;
    }}
    opacity.value = withTiming(0, {{ duration: 250 }});
    translateY.value = withTiming(20, {{ duration: 250 }});
  }};

  return {{ animatedStyle, animateIn, animateOut, progress }};
}}
"""

    return GeneratedFile(
        path=Path("shared") / "animations" / f"use-{name.lower().replace(' ', '-')}.ts",
        content=content,
        node_ids=[node.id],
    )


def generate_haptic(node: GraphNode) -> GeneratedFile:
    """Compile a HAPTIC node into expo-haptics usage."""
    metadata = node.metadata
    name = metadata.get("name", "feedback")
    intensity = node.constraints.get("intensity", "medium")

    intensity_map = {
        "light": "Haptics.ImpactFeedbackStyle.Light",
        "medium": "Haptics.ImpactFeedbackStyle.Medium",
        "heavy": "Haptics.ImpactFeedbackStyle.Heavy",
    }

    content = f"""import * as Haptics from 'expo-haptics';
import {{ Platform }} from 'react-native';

/**
 * {node.intent}
 * Intensity: {intensity}
 */
export function {name.replace('-', '_')}Feedback() {{
  if (Platform.OS === 'web') return;
  Haptics.impactAsync({intensity_map.get(intensity, 'Haptics.ImpactFeedbackStyle.Medium')});
}}
"""

    return GeneratedFile(
        path=Path("shared") / "haptics" / f"{name.lower().replace(' ', '-')}.ts",
        content=content,
        node_ids=[node.id],
    )


def generate_accessibility(node: GraphNode) -> GeneratedFile:
    """Compile an ACCESSIBILITY node into props and patterns."""
    metadata = node.metadata
    name = metadata.get("name", "a11y")
    role = node.constraints.get("role", "button")
    label = node.constraints.get("label", name)

    content = f"""/**
 * Accessibility configuration for: {name}
 * Role: {role}
 * Label: {label}
 */

export const {name}AccessibilityProps = {{
  accessible: true,
  accessibilityRole: '{role}' as const,
  accessibilityLabel: '{label}',
  accessibilityHint: '{node.intent}',
}};

export const {name}TouchTarget = {{
  minWidth: 44,
  minHeight: 44,
  justifyContent: 'center' as const,
  alignItems: 'center' as const,
}};
"""

    return GeneratedFile(
        path=Path("shared") / "accessibility" / f"{name.lower().replace(' ', '-')}.ts",
        content=content,
        node_ids=[node.id],
    )
