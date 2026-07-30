"""
XOS Spec Auto-Healer Engine — Automatically refines and fixes spec/graph
deficiencies to reach Silicon Valley quality benchmarks.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

from .graph import ExperienceGraph, GraphNode, NodeType
from .evaluator import QualityScorecard
from .node_factory import (
    create_motion_node,
    create_gesture_node,
    create_haptic_node,
    create_accessibility_node,
)


class SpecAutoHealer:
    """Self-healing engine for Experience Graphs and spec definitions."""

    def heal(
        self,
        graph: ExperienceGraph,
        spec_dicts: List[Dict[str, Any]],
        scorecard: QualityScorecard,
    ) -> Tuple[ExperienceGraph, List[Dict[str, Any]], List[str]]:
        healed_graph = copy.deepcopy(graph)
        healed_specs = copy.deepcopy(spec_dicts)
        actions_taken: List[str] = []

        # 1. Heal Specs
        for spec in healed_specs:
            self._heal_spec_dict(spec, actions_taken)

        # 2. Heal Graph Nodes & Constraints directly
        screens = healed_graph.find_by_type(NodeType.SCREEN)
        for s in screens:
            self._heal_screen_node(healed_graph, s, actions_taken)

        # 3. Heal Motion Constraints
        motion_nodes = healed_graph.find_by_type(NodeType.MOTION)
        for m in motion_nodes:
            if not m.constraints.get("must_respect_reduced_motion"):
                m.constraints["must_respect_reduced_motion"] = True
                actions_taken.append(f"Fixed motion node '{m.id}': set must_respect_reduced_motion=True.")
            if m.constraints.get("frame_budget_ms", 16) > 16:
                m.constraints["frame_budget_ms"] = 16
                actions_taken.append(f"Fixed motion node '{m.id}': capped frame_budget_ms to 16ms.")

        # 4. Heal Gesture Constraints
        gesture_nodes = healed_graph.find_by_type(NodeType.GESTURE)
        for g in gesture_nodes:
            if not g.constraints.get("must_define_conflict_resolution"):
                g.constraints["must_define_conflict_resolution"] = True
                actions_taken.append(f"Fixed gesture node '{g.id}': added conflict resolution policy.")

        # 5. Heal Accessibility Constraints
        a11y_nodes = healed_graph.find_by_type(NodeType.ACCESSIBILITY)
        for a in a11y_nodes:
            min_target = a.constraints.get("min_touch_target", 44)
            if min_target < 44:
                a.constraints["min_touch_target"] = 44
                actions_taken.append(f"Fixed accessibility node '{a.id}': raised min_touch_target from {min_target}pt to 44pt.")

        return healed_graph, healed_specs, actions_taken

    def _heal_spec_dict(self, spec: Dict[str, Any], actions: List[str]) -> None:
        name = spec.get("name", "app")

        # Ensure design tokens exist
        if "design_tokens" not in spec:
            from .knowledge import get_design_tokens
            spec["design_tokens"] = get_design_tokens()
            actions.append(f"Added missing design_tokens to spec '{name}'.")

        if "motion_tokens" not in spec:
            from .knowledge import get_motion_tokens
            spec["motion_tokens"] = get_motion_tokens()
            actions.append(f"Added missing motion_tokens to spec '{name}'.")

        # Heal feature screens
        features = spec.get("features", [])
        if features and isinstance(features[0], dict):
            for feat in features:
                for screen in feat.get("screens", []):
                    self._heal_screen_spec(screen, actions)
        elif "screens" in spec:
            for screen in spec.get("screens", []):
                self._heal_screen_spec(screen, actions)

    def _heal_screen_spec(self, screen: Dict[str, Any], actions: List[str]) -> None:
        sname = screen.get("name", "unnamed")

        if "motion" not in screen or not screen["motion"]:
            screen["motion"] = {"entrance": "fade_in_slide_up", "frameBudget": 16}
            actions.append(f"Auto-generated motion spec for screen '{sname}'.")

        if "haptics" not in screen or not screen["haptics"]:
            screen["haptics"] = ["lightImpact (tap)", "notificationSuccess (complete)"]
            actions.append(f"Auto-generated haptic feedback spec for screen '{sname}'.")

        if "gestures" not in screen or not screen["gestures"]:
            screen["gestures"] = ["tap (select)", "swipeRight (navigate)"]
            actions.append(f"Auto-generated gesture interaction spec for screen '{sname}'.")

        if "accessibility" not in screen or not screen["accessibility"]:
            screen["accessibility"] = {
                "heading": sname.title(),
                "minTouchTarget": 44,
                "focusOrder": "heading -> main -> actions",
                "liveRegion": "polite",
            }
            actions.append(f"Auto-generated accessibility spec for screen '{sname}'.")
        else:
            a11y = screen["accessibility"]
            if a11y.get("minTouchTarget", 44) < 44:
                a11y["minTouchTarget"] = 44
                actions.append(f"Raised minTouchTarget to 44pt in screen '{sname}'.")

    def _heal_screen_node(self, graph: ExperienceGraph, screen_node: GraphNode, actions: List[str]) -> None:
        sid = screen_node.id
        sname = sid.replace("screen:", "")

        # Collect targets connected to sid
        edge_targets = graph.edges.get(sid, set())

        # Check & create motion node if missing
        mid = f"motion:{sid}"
        if mid not in graph.nodes and mid not in edge_targets:
            mnode = create_motion_node(sname, intent="Motion: fade_in_slide_up")
            mnode.id = mid
            graph.add_node(mnode)
            if sid not in graph.edges:
                graph.edges[sid] = set()
            graph.edges[sid].add(mid)
            actions.append(f"Created graph motion node '{mid}' for screen '{sid}'.")

        # Check & create haptic node if missing
        hid = f"haptic:{sid}:0"
        if hid not in graph.nodes and not any(n.startswith(f"haptic:{sid}") for n in graph.nodes):
            hnode = create_haptic_node(sname, intent="Haptic: lightImpact")
            hnode.id = hid
            graph.add_node(hnode)
            if sid not in graph.edges:
                graph.edges[sid] = set()
            graph.edges[sid].add(hid)
            actions.append(f"Created graph haptic node '{hid}' for screen '{sid}'.")

        # Check & create gesture node if missing
        gid = f"gesture:{sid}:0"
        if gid not in graph.nodes and not any(n.startswith(f"gesture:{sid}") for n in graph.nodes):
            gnode = create_gesture_node(sname, intent="Gesture: tap", gesture_type="tap")
            gnode.id = gid
            graph.add_node(gnode)
            if sid not in graph.edges:
                graph.edges[sid] = set()
            graph.edges[sid].add(gid)
            actions.append(f"Created graph gesture node '{gid}' for screen '{sid}'.")

        # Check & create accessibility node if missing
        aid = f"a11y:{sid}"
        if aid not in graph.nodes and aid not in edge_targets:
            anode = create_accessibility_node(sname, intent=f"a11y: {sname}", role="header", label=sname)
            anode.id = aid
            graph.add_node(anode)
            if sid not in graph.edges:
                graph.edges[sid] = set()
            graph.edges[sid].add(aid)
            actions.append(f"Created graph accessibility node '{aid}' for screen '{sid}'.")
