"""
Knowledge Graph — reusable patterns, design tokens, and agent skills.

This is the long-lived "pattern library" that agents consult before
generating anything.  It contains architecture patterns, design tokens,
motion/graphic/haptic/accessibility patterns, component patterns, and
prompt templates.  Agents may reuse but never invent unsupported patterns.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from python.core.xos_logger import get_logger

logger = get_logger(__name__)


class KnowledgeEntry:
    __slots__ = ("name", "kind", "data", "version")

    def __init__(self, name: str, kind: str, data: dict, version: str = "1.0.0") -> None:
        self.name = name
        self.kind = kind
        self.data = data
        self.version = version


class KnowledgeGraph:
    """In-memory index over the knowledge/ directory."""

    KNOWN_KINDS = {
        "architecture",
        "design-tokens",
        "motion",
        "gestures",
        "haptics",
        "accessibility",
        "components",
        "prompts",
    }

    def __init__(self, root: Path) -> None:
        self._root = root
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._by_kind: Dict[str, List[KnowledgeEntry]] = {}

    def load(self) -> None:
        self._entries.clear()
        self._by_kind = {k: [] for k in self.KNOWN_KINDS}
        for kind in self.KNOWN_KINDS:
            kind_dir = self._root / "knowledge" / kind
            if not kind_dir.is_dir():
                continue
            for f in kind_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    logger.warning("Skipping invalid JSON: %s", f)
                    continue
                entry = KnowledgeEntry(
                    name=f.stem,
                    kind=kind,
                    data=data,
                    version=data.get("version", "1.0.0"),
                )
                self._entries[entry.name] = entry
                self._by_kind.setdefault(kind, []).append(entry)
        logger.info("Knowledge graph loaded: %d entries across %d kinds",
                     len(self._entries), len([k for k, v in self._by_kind.items() if v]))

    def get(self, name: str) -> Optional[KnowledgeEntry]:
        return self._entries.get(name)

    def list_kind(self, kind: str) -> List[KnowledgeEntry]:
        return self._by_kind.get(kind, [])

    def search(self, kind: str, tags: Optional[List[str]] = None) -> List[KnowledgeEntry]:
        candidates = self._by_kind.get(kind, [])
        if tags is None:
            return candidates
        return [e for e in candidates if set(tags).issubset(set(e.data.get("tags", [])))]
