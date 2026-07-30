"""
XOS Project Builder – scaffolds a fully runnable Expo + React Native project
from the compiled feature artifacts produced by the pipeline.

Produces: package.json, tsconfig, app.json, babel.config.js, metro.config.js,
tailwind.config.js, app/ structure, components/ stubs, types/, jest setup.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


EXPO_PACKAGE_JSON_TEMPLATE = {
    "name": "xos-app",
    "version": "1.0.0",
    "private": True,
    "main": "expo-router/entry",
    "scripts": {
        "start": "expo start",
        "android": "expo start --android",
        "ios": "expo start --ios",
        "web": "expo start --web",
        "lint": "eslint . --ext ts,tsx",
        "test": "jest",
        "typecheck": "tsc --noEmit",
        "build:android": "eas build --platform android",
        "build:ios": "eas build --platform ios",
        "submit:android": "eas submit --platform android",
        "submit:ios": "eas submit --platform ios",
    },
    "dependencies": {
        "expo": "~52.0.0",
        "expo-router": "~4.0.0",
        "expo-haptics": "~14.0.0",
        "expo-status-bar": "~2.0.0",
        "expo-splash-screen": "~0.29.0",
        "expo-font": "~13.0.0",
        "expo-constants": "~17.0.0",
        "expo-linking": "~7.0.0",
        "react": "18.3.1",
        "react-dom": "18.3.1",
        "react-native": "0.76.5",
        "react-native-reanimated": "~3.16.0",
        "react-native-gesture-handler": "~2.20.0",
        "react-native-safe-area-context": "4.12.0",
        "react-native-screens": "~4.4.0",
        "@react-navigation/native": "^7.0.0",
        "@react-navigation/bottom-tabs": "^7.0.0",
        "@shopify/flash-list": "1.7.1",
        "nativewind": "~4.1.0",
        "tailwindcss": "^3.4.0",
        "zustand": "^5.0.0",
        "@tanstack/react-query": "^5.60.0",
        "react-hook-form": "^7.53.0",
        "@hookform/resolvers": "^3.9.0",
        "zod": "^3.23.0",
        "react-native-mmkv": "^3.1.0",
    },
    "devDependencies": {
        "@types/react": "~18.3.0",
        "typescript": "~5.3.0",
        "jest": "^29.7.0",
        "jest-expo": "~52.0.0",
        "@testing-library/react-native": "^12.0.0",
        "eslint": "^8.57.0",
        "prettier": "^3.4.0",
    },
    "jest": {
        "preset": "jest-expo",
        "transformIgnorePatterns": [
            "node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@sentry/react-native|native-base|react-native-svg|react-native-reanimated|react-native-gesture-handler)"
        ]
    }
}

APP_JSON_TEMPLATE = {
    "expo": {
        "name": "xos-app",
        "slug": "xos-app",
        "version": "1.0.0",
        "orientation": "portrait",
        "icon": "./assets/icon.png",
        "userInterfaceStyle": "automatic",
        "scheme": "xos",
        "splash": {
            "image": "./assets/splash.png",
            "resizeMode": "contain",
            "backgroundColor": "#FFFFFF"
        },
        "ios": {
            "supportsTablet": True,
            "bundleIdentifier": "com.xos.app"
        },
        "android": {
            "adaptiveIcon": {
                "foregroundImage": "./assets/adaptive-icon.png",
                "backgroundColor": "#FFFFFF"
            },
            "package": "com.xos.app"
        },
        "plugins": [
            "expo-router",
            "expo-haptics",
            "expo-font"
        ],
        "experiments": {
            "typedRoutes": True
        }
    }
}

TSCONFIG_TEMPLATE = {
    "extends": "expo/tsconfig.base",
    "compilerOptions": {
        "strict": True,
        "baseUrl": ".",
        "paths": {
            "@/*": ["./*"]
        }
    },
    "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
}

BABEL_CONFIG = """module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    plugins: ["react-native-reanimated/plugin"],
  };
};
"""

METRO_CONFIG = """const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: "./global.css" });
"""

TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}", "./features/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "var(--color-primary)",
          foreground: "var(--color-primary-foreground)",
        },
        background: "var(--color-background)",
        foreground: "var(--color-foreground)",
        card: "var(--color-card)",
        "card-foreground": "var(--color-card-foreground)",
        muted: "var(--color-muted)",
        "muted-foreground": "var(--color-muted-foreground)",
        border: "var(--color-border)",
      },
    },
  },
  plugins: [],
};
"""

GLOBAL_CSS = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: #0EA5E9;
  --color-primary-foreground: #FFFFFF;
  --color-background: #FAFAFA;
  --color-foreground: #0A0A0A;
  --color-card: #FFFFFF;
  --color-card-foreground: #0A0A0A;
  --color-muted: #F5F5F5;
  --color-muted-foreground: #737373;
  --color-border: #E5E5E5;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #38BDF8;
    --color-primary-foreground: #0A0A0A;
    --color-background: #0A0A0A;
    --color-foreground: #FAFAFA;
    --color-card: #171717;
    --color-card-foreground: #FAFAFA;
    --color-muted: #262626;
    --color-muted-foreground: #A3A3A3;
    --color-border: #404040;
  }
}
"""

APP_LAYOUT_TSX = """import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import "react-native-reanimated";
import "../global.css";

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerShown: false,
          animation: "fade",
          contentStyle: { backgroundColor: "var(--color-background)" },
        }}
      />
    </GestureHandlerRootView>
  );
}
"""

INDEX_TSX = """import { Redirect } from "expo-router";

export default function Index() {
  return <Redirect href="/(tabs)" />;
}
"""

TABS_LAYOUT_TSX = """import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "var(--color-primary)",
        tabBarInactiveTintColor: "var(--color-muted-foreground)",
        tabBarStyle: {
          backgroundColor: "var(--color-card)",
          borderTopColor: "var(--color-border)",
        },
      }}
    >
"""
TABS_LAYOUT_TSX_END = """    </Tabs>
  );
}
"""

ESLINTRC = """{
  "extends": ["expo", "prettier"],
  "plugins": ["prettier"],
  "rules": {
    "prettier/prettier": "error"
  }
}
"""

GITIGNORE = """node_modules/
.expo/
dist/
*.jks
*.p8
*.p12
*.key
*.mobileprovision
*.orig.*
web-build/
.env
.env.local
ios/Pods/
android/.gradle/
android/app/build/
android/build/
"""


class ProjectBuilder:
    def __init__(self, output_dir: Path, app_name: str = "xos-app"):
        self.output_dir = Path(output_dir)
        self.app_name = app_name

    def scaffold(self) -> list[Path]:
        """Scaffold the full Expo project. Returns list of created files."""
        created: list[Path] = []

        out = self.output_dir
        out.mkdir(parents=True, exist_ok=True)

        # ── Root config files ──
        created += self._write_json(out / "package.json", EXPO_PACKAGE_JSON_TEMPLATE)
        created += self._write_json(out / "app.json", APP_JSON_TEMPLATE)
        created += self._write_json(out / "tsconfig.json", TSCONFIG_TEMPLATE)
        created += self._write_text(out / "babel.config.js", BABEL_CONFIG)
        created += self._write_text(out / "metro.config.js", METRO_CONFIG)
        created += self._write_text(out / "tailwind.config.js", TAILWIND_CONFIG)
        created += self._write_text(out / "global.css", GLOBAL_CSS)
        created += self._write_text(out / ".eslintrc.json", ESLINTRC)
        created += self._write_text(out / ".gitignore", GITIGNORE)

        # ── app/ directory (Expo Router) ──
        app = out / "app"
        app.mkdir(parents=True, exist_ok=True)
        created += self._write_text(app / "_layout.tsx", APP_LAYOUT_TSX)
        created += self._write_text(app / "index.tsx", INDEX_TSX)

        tabs = app / "(tabs)"
        tabs.mkdir(parents=True, exist_ok=True)
        created += self._write_text(tabs / "_layout.tsx", TABS_LAYOUT_TSX + self._gen_tab_screens() + TABS_LAYOUT_TSX_END)

        # ── components/ ──
        (out / "components").mkdir(parents=True, exist_ok=True)

        # ── shared/ ──
        (out / "shared").mkdir(parents=True, exist_ok=True)

        # ── assets/ ──
        assets = out / "assets"
        assets.mkdir(parents=True, exist_ok=True)

        # ── features/ symlink or copy ──
        features_src = Path("features")
        features_dst = out / "features"
        if features_src.exists() and not features_dst.exists():
            try:
                shutil.copytree(features_src, features_dst)
                created.append(features_dst)
            except Exception:
                pass

        return created

    def _gen_tab_screens(self) -> str:
        """Generate minimal tab screen stubs."""
        tab_names = ["home", "explore", "settings"]
        lines = []
        for i, name in enumerate(tab_names):
            icon = {"home": "home", "explore": "compass", "settings": "cog"}[name]
            lines.append(f'      <Tabs.Screen')
            lines.append(f'        name="{name}"')
            lines.append(f'        options={{{{')
            lines.append(f'          title: "{name.capitalize()}",')
            lines.append(f'          tabBarIcon: ({{ color, size }}) => <Ionicons name="{icon}" size={{size}} color={{color}} />,')
            lines.append(f'        }}}}')
            lines.append(f'      />')

            tab_file = self.output_dir / "app" / "(tabs)" / f"{name}.tsx"
            if not tab_file.exists():
                content = f"""import {{ View, Text }} from "react-native";

export default function {name.capitalize()}Screen() {{
  return (
    <View style={{{{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "var(--color-background)" }}}}>
      <Text style={{{{ fontSize: 18, color: "var(--color-foreground)" }}}}>{name.capitalize()}</Text>
    </View>
  );
}}
"""
                self._write_text(self.output_dir / "app" / "(tabs)" / f"{name}.tsx", content)

        return "\n".join(lines)

    def _write_json(self, path: Path, data: dict) -> list[Path]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        return [path]

    def _write_text(self, path: Path, content: str) -> list[Path]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n")
        return [path]
