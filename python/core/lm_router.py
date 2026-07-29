"""
Language Model Router — maps natural-language prompts to structured
intents for the agent runtime and MCP layer.

Example uses:
  - "Build me a login screen" → { action: "generate_screen", params: { name: "Login", ... } }
  - "Add haptic feedback to the onboarding flow" → { action: "add_haptic", ... }
  - "Audit all gestures in the settings screen" → { action: "audit_gestures", ... }
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from python.core.xos_logger import get_logger

logger = get_logger(__name__)

ACTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?:build|create|generate|make)\b.*?\b(?:login|sign.?in|auth|authentication|onboarding|profile|settings|home|dashboard|feed|search|notifications|chat)\b", re.I), "generate_screen"),
    (re.compile(r"(?:add|enhance|improve|apply)\b.*?\b(?:motion|animation|transition)\b", re.I), "compile_motion"),
    (re.compile(r"(?:add|enhance|improve|apply)\b.*?\b(?:haptic|vibration|tactile)\b", re.I), "compile_haptics"),
    (re.compile(r"(?:add|enhance|improve|apply)\b.*?\b(?:gesture|swipe|pan|pinch)\b", re.I), "compile_gestures"),
    (re.compile(r"(?:audit|check|review|inspect)\b.*?\b(?:screen|component|gesture|animation|perf)", re.I), "audit"),
    (re.compile(r"\b(?:fix|repair|correct)\b", re.I), "repair"),
    (re.compile(r"\b(?:deploy|ship|publish|release)\b", re.I), "deploy"),
    (re.compile(r"\b(?:test|qa|verify)\b", re.I), "run_tests"),
    (re.compile(r"\b(?:document|documentation|docs)\b", re.I), "generate_documentation"),
]


class LanguageModelRouter:
    """Parses free-text intents into XOS actions.

    In production, this is backed by an LLM call.  For now, it uses
    lightweight regex classifiers as a fast first pass.
    """

    def classify(self, prompt: str) -> Dict[str, Any]:
        best_score = 0
        best_action = "pass_through"
        for pattern, action in ACTION_PATTERNS:
            m = pattern.search(prompt)
            if m and len(m.group(0)) > best_score:
                best_score = len(m.group(0))
                best_action = action

        params = self._extract_params(prompt, best_action)
        intent: Dict[str, Any] = {"action": best_action, "params": params, "original": prompt}
        logger.info("Router classified intent → %s", best_action)
        return intent

    def _extract_params(self, prompt: str, action: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if action == "generate_screen":
            screen_match = re.search(r"(?:login|sign.?in|auth|authentication|onboarding|profile|settings|home|dashboard|feed|search|notifications|chat)", prompt, re.I)
            if screen_match:
                params["screen_name"] = screen_match.group(0).lower()
        return params
