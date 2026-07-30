"""
XOS Node Factory — typed constructors for every node in the Experience Graph.

Each factory enforces required fields and default values per node type.
"""

from __future__ import annotations

from .graph import GraphNode, NodeType, GateStatus


def create_screen_node(
    name: str,
    intent: str,
    route: str = "",
    dependencies: list[str] | None = None,
    owner: str = "ux-engineer",
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.SCREEN,
        intent=f"{name}: {intent}",
        inputs=["navigation-params", "state"],
        outputs=["rendered-ui", "user-interactions"],
        dependencies=dependencies or [],
        constraints={
            "max_render_time_ms": 16,
            "supported_orientations": ["portrait"],
            "min_touch_target": 44,
        },
        owner=owner,
        metadata={"name": name, "route": route},
    )


def create_component_node(
    name: str,
    intent: str,
    props_schema: dict | None = None,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.COMPONENT,
        intent=f"{name}: {intent}",
        inputs=["props", "theme", "state"],
        outputs=["rendered-component"],
        dependencies=dependencies or [],
        constraints={
            "must_accept_test_id": True,
            "must_support_dark_mode": True,
            "must_be_tree_shakeable": True,
        },
        owner="react-native-engineer",
        metadata={"name": name, "props_schema": props_schema or {}},
    )


def create_motion_node(
    name: str,
    intent: str,
    duration_ms: int = 300,
    curve: str = "ease-out",
    interruptible: bool = True,
    frame_budget_ms: int = 8,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.MOTION,
        intent=f"{name}: {intent}",
        inputs=["trigger", "element-ref"],
        outputs=["animated-values"],
        dependencies=dependencies or [],
        constraints={
            "duration_ms": duration_ms,
            "curve": curve,
            "interruptible": interruptible,
            "frame_budget_ms": frame_budget_ms,
            "must_respect_reduced_motion": True,
        },
        owner="motion-engineer",
        metadata={"name": name},
    )


def create_gesture_node(
    name: str,
    intent: str,
    gesture_type: str = "pan",
    threshold: float = 10.0,
    priority: int = 0,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.GESTURE,
        intent=f"{name}: {intent}",
        inputs=["touch-events", "element-ref"],
        outputs=["gesture-state", "callbacks"],
        dependencies=dependencies or [],
        constraints={
            "type": gesture_type,
            "threshold": threshold,
            "priority": priority,
            "must_define_conflict_resolution": True,
            "must_support_velocity_tracking": True,
        },
        owner="gesture-engineer",
        metadata={"name": name},
    )


def create_haptic_node(
    name: str,
    intent: str,
    intensity: str = "medium",
    platform_mapping: dict | None = None,
    timing_ms: int = 50,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.HAPTIC,
        intent=f"{name}: {intent}",
        inputs=["trigger-event"],
        outputs=["haptic-feedback"],
        dependencies=dependencies or [],
        constraints={
            "intensity": intensity,
            "timing_ms": timing_ms,
            "must_map_to_platform": True,
        },
        owner="haptic-engineer",
        metadata={
            "name": name,
            "platform_mapping": platform_mapping
            or {"ios": "UIImpactFeedbackGenerator", "android": "HapticFeedbackConstants"},
        },
    )


def create_accessibility_node(
    name: str,
    intent: str,
    role: str = "button",
    label: str = "",
    focus_order: int = 0,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.ACCESSIBILITY,
        intent=f"{name}: {intent}",
        inputs=["element-ref", "content"],
        outputs=["accessibility-props"],
        dependencies=dependencies or [],
        constraints={
            "role": role,
            "label": label,
            "focus_order": focus_order,
            "must_support_screen_reader": True,
            "must_support_dynamic_type": True,
            "min_contrast_ratio": 4.5,
            "min_touch_target": 44,
        },
        owner="accessibility-engineer",
        metadata={"name": name},
    )


def create_navigation_node(
    name: str,
    intent: str,
    source_screen: str = "",
    target_screen: str = "",
    animation: str = "slide",
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.NAVIGATION,
        intent=f"{name}: {intent}",
        inputs=["navigation-state"],
        outputs=["navigation-action"],
        dependencies=dependencies or [],
        constraints={
            "must_define_back_behavior": True,
            "must_handle_deep_link": True,
            "animation": animation,
        },
        owner="expo-engineer",
        metadata={"source_screen": source_screen, "target_screen": target_screen},
    )


def create_state_node(
    name: str,
    intent: str,
    initial_value: Any = None,
    persist: bool = False,
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.STATE,
        intent=f"{name}: {intent}",
        inputs=["actions"],
        outputs=["state-snapshot"],
        dependencies=dependencies or [],
        constraints={
            "must_be_serializable": True,
            "must_define_update_rules": True,
            "persist": persist,
        },
        owner="react-native-engineer",
        metadata={"name": name, "initial_value": initial_value},
    )


def create_design_token_node(
    name: str,
    intent: str,
    token_type: str = "color",
    value: str = "",
    dependencies: list[str] | None = None,
) -> GraphNode:
    return GraphNode(
        node_type=NodeType.DESIGN_TOKEN,
        intent=f"{name}: {intent}",
        inputs=["theme-context"],
        outputs=["token-value"],
        dependencies=dependencies or [],
        constraints={
            "type": token_type,
            "must_support_light_dark": True,
            "must_be_nativewind_compatible": True,
        },
        owner="design-system-engineer",
        metadata={"name": name, "value": value},
    )


def load_spec_into_graph(graph, spec: dict) -> None:
    """Convert a spec dict into graph nodes and edges."""
    name = spec.get("name", "unnamed")

    # Create feature node
    fid = f"feat:{name}"
    if fid not in graph.nodes:
        graph.add_node(GraphNode(
            id=fid, node_type=NodeType.FEATURE,
            intent=spec.get("description", ""),
            metadata=spec
        ))
    if fid not in graph.edges:
        graph.edges[fid] = set()

    # Create screen nodes from screens or features.screens arrays
    screens = list(spec.get("screens", []))
    for feat in spec.get("features", []):
        if isinstance(feat, dict):
            screens.extend(feat.get("screens", []))

    for screen in screens:
        if not isinstance(screen, dict):
            continue
        sid = f"screen:{screen.get('name', name)}"
        if sid not in graph.nodes:
            graph.add_node(GraphNode(
                id=sid, node_type=NodeType.SCREEN,
                intent=screen.get("description", ""),
                constraints={"route": screen.get("route", "/")},
                metadata=screen
            ))
        if sid not in graph.edges:
            graph.edges[sid] = set()
        graph.edges[fid].add(sid)

        # Create component nodes
        for comp_name in screen.get("components", []):
            cid = f"comp:{comp_name}"
            if cid not in graph.nodes:
                graph.add_node(GraphNode(
                    id=cid, node_type=NodeType.COMPONENT,
                    intent=f"Component: {comp_name}"
                ))
            if cid not in graph.edges:
                graph.edges[cid] = set()
            graph.edges[sid].add(cid)

        # Create MOTION node
        motion = screen.get("motion", {})
        if motion:
            mid = f"motion:{sid}"
            if mid not in graph.nodes:
                graph.add_node(GraphNode(
                    id=mid, node_type=NodeType.MOTION,
                    intent=f"Motion: {motion.get('entrance', 'fadeIn')}",
                    constraints={
                        "must_respect_reduced_motion": True,
                        "frame_budget_ms": motion.get("frameBudget", 16),
                    },
                    metadata=motion
                ))
            if mid not in graph.edges:
                graph.edges[mid] = set()
            graph.edges[sid].add(mid)

        # Create HAPTIC nodes
        haptics = screen.get("haptics", [])
        for i, h in enumerate(haptics):
            hid = f"haptic:{sid}:{i}"
            if hid not in graph.nodes:
                h_name = h.split("(")[0].strip() if "(" in h else h
                graph.add_node(GraphNode(
                    id=hid, node_type=NodeType.HAPTIC,
                    intent=h,
                    metadata={"spec": h, "name": h_name}
                ))
            if hid not in graph.edges:
                graph.edges[hid] = set()
            graph.edges[sid].add(hid)

        # Create GESTURE nodes
        gestures = screen.get("gestures", [])
        for i, g in enumerate(gestures):
            gid = f"gesture:{sid}:{i}"
            if gid not in graph.nodes:
                g_name = g.split("(")[0].strip() if "(" in g else g
                graph.add_node(GraphNode(
                    id=gid, node_type=NodeType.GESTURE,
                    intent=g,
                    constraints={"must_define_conflict_resolution": True},
                    metadata={"spec": g, "name": g_name}
                ))
            if gid not in graph.edges:
                graph.edges[gid] = set()
            graph.edges[sid].add(gid)

        # Create ACCESSIBILITY node
        a11y = screen.get("accessibility", {})
        if a11y:
            aid = f"a11y:{sid}"
            if aid not in graph.nodes:
                graph.add_node(GraphNode(
                    id=aid, node_type=NodeType.ACCESSIBILITY,
                    intent=f"a11y: {a11y.get('heading', screen.get('name', ''))}",
                    constraints={
                        "min_touch_target": a11y.get("minTouchTarget", 44),
                    },
                    metadata=a11y
                ))
            if aid not in graph.edges:
                graph.edges[aid] = set()
            graph.edges[sid].add(aid)

    # Handle business rules
    for rule in spec.get("business_rules", []):
        if not isinstance(rule, dict):
            continue
        rid = f"rule:{rule.get('id', rule.get('name', 'unnamed'))}"
        if rid not in graph.nodes:
            graph.add_node(GraphNode(
                id=rid, node_type=NodeType.BUSINESS_RULE,
                intent=rule.get("description", rule.get("rule", "")),
                constraints={"condition": rule.get("condition", "")},
                metadata=rule
            ))
        if rid not in graph.edges:
            graph.edges[rid] = set()
        graph.edges[fid].add(rid)

