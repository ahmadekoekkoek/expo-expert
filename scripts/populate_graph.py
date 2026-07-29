#!/usr/bin/env python3
"""Populate a complete Experience Graph for a sample e-commerce mobile app."""
from python.graph.experience_graph import ExperienceGraph, GraphNode, GraphEdge, NodeKind, EdgeKind

g = ExperienceGraph("XOS E-Commerce Demo")

# ── Product ──
g.add_node(GraphNode(id="product:store", kind=NodeKind.PRODUCT, label="Store App", intent="A premium e-commerce experience built with React Native + Expo."))

# ── Features ──
g.add_node(GraphNode(id="feat:browse", kind=NodeKind.FEATURE, label="Product Browse", intent="Browse products with rich animations, gestures, and haptic feedback.", dependencies=["product:store"]))
g.add_node(GraphNode(id="feat:checkout", kind=NodeKind.FEATURE, label="Checkout", intent="Fast, accessible checkout flow with confirmation haptics.", dependencies=["product:store"]))
g.add_node(GraphNode(id="feat:profile", kind=NodeKind.FEATURE, label="User Profile", intent="Profile management with gesture-driven navigation.", dependencies=["product:store"]))

# ── Screens ──
g.add_node(GraphNode(id="screen:home", kind=NodeKind.SCREEN, label="Home", intent="Product grid with pull-to-refresh, staggered animations, and search.", dependencies=["feat:browse"], constraints={"frame_budget": 16}))
g.add_node(GraphNode(id="screen:product-detail", kind=NodeKind.SCREEN, label="Product Detail", intent="Hero animation, swipe gallery, haptic add-to-cart.", dependencies=["feat:browse"], constraints={"frame_budget": 16}))
g.add_node(GraphNode(id="screen:cart", kind=NodeKind.SCREEN, label="Cart", intent="Swipe-to-delete, haptic confirmation, slide-up checkout sheet.", dependencies=["feat:checkout"], constraints={"frame_budget": 16}))
g.add_node(GraphNode(id="screen:checkout", kind=NodeKind.SCREEN, label="Checkout", intent="Multi-step checkout with progress animation and success haptics.", dependencies=["feat:checkout"], constraints={"frame_budget": 16}))
g.add_node(GraphNode(id="screen:profile", kind=NodeKind.SCREEN, label="Profile", intent="Settings list with gesture-driven reorder and haptic toggles.", dependencies=["feat:profile"], constraints={"frame_budget": 16}))

# ── Components ──
g.add_node(GraphNode(id="comp:product-card", kind=NodeKind.COMPONENT, label="ProductCard", intent="Animated product card with press animation and haptic feedback.", dependencies=["screen:home"]))
g.add_node(GraphNode(id="comp:image-gallery", kind=NodeKind.COMPONENT, label="ImageGallery", intent="Swipeable image gallery with pinch-to-zoom.", dependencies=["screen:product-detail"]))
g.add_node(GraphNode(id="comp:cart-item", kind=NodeKind.COMPONENT, label="CartItem", intent="Swipeable cart item with delete confirmation.", dependencies=["screen:cart"]))
g.add_node(GraphNode(id="comp:checkout-stepper", kind=NodeKind.COMPONENT, label="CheckoutStepper", intent="Animated step indicator with haptic progress.", dependencies=["screen:checkout"]))

# ── Navigation ──
g.add_node(GraphNode(id="nav:main-tabs", kind=NodeKind.NAVIGATION, label="Main Tab Navigator", intent="Bottom tabs: Home, Cart, Profile.", dependencies=["screen:home", "screen:cart", "screen:profile"]))
g.add_node(GraphNode(id="nav:product-to-detail", kind=NodeKind.NAVIGATION, label="Home → Product Detail", intent="Shared element transition from product card to detail.", dependencies=["screen:home", "screen:product-detail"]))

# ── Motion Tokens ──
g.add_node(GraphNode(id="motion:stagger-enter", kind=NodeKind.MOTION_TOKEN, label="Staggered Enter", intent="Staggered fade+slide entrance for list items.", constraints={"duration_ms": 400, "stagger_ms": 80, "curve": "ease-out", "interruptible": True, "frame_budget": 8}))
g.add_node(GraphNode(id="motion:hero-transition", kind=NodeKind.MOTION_TOKEN, label="Hero Transition", intent="Shared element morph from card to detail hero.", constraints={"duration_ms": 350, "curve": "spring", "interruptible": True, "frame_budget": 8}))
g.add_node(GraphNode(id="motion:slide-up-sheet", kind=NodeKind.MOTION_TOKEN, label="Slide-Up Sheet", intent="Bottom sheet slide-up for checkout.", constraints={"duration_ms": 300, "curve": "ease-out", "interruptible": True, "frame_budget": 8}))
g.add_node(GraphNode(id="motion:press-scale", kind=NodeKind.MOTION_TOKEN, label="Press Scale", intent="0.97 scale on press with spring rebound.", constraints={"duration_ms": 150, "curve": "spring", "interruptible": True, "frame_budget": 4}))

# ── Gesture Patterns ──
g.add_node(GraphNode(id="gesture:pull-refresh", kind=NodeKind.GESTURE_PATTERN, label="Pull to Refresh", intent="Vertical pull with threshold and haptic trigger.", constraints={"threshold": 80, "velocity": 500, "priority": 0}))
g.add_node(GraphNode(id="gesture:swipe-delete", kind=NodeKind.GESTURE_PATTERN, label="Swipe to Delete", intent="Horizontal swipe revealing delete action.", constraints={"threshold": 120, "velocity": 300, "priority": 1}))
g.add_node(GraphNode(id="gesture:pinch-zoom", kind=NodeKind.GESTURE_PATTERN, label="Pinch to Zoom", intent="Two-finger pinch on product images.", constraints={"min_scale": 1, "max_scale": 3, "priority": 2}))

# ── Haptic Patterns ──
g.add_node(GraphNode(id="haptic:add-to-cart", kind=NodeKind.HAPTIC_PATTERN, label="Add to Cart", intent="Medium impact haptic on add-to-cart tap.", constraints={"intensity": "medium", "timing_ms": 50, "platform": {"ios": "impactMedium", "android": "KEYBOARD_TAP"}}))
g.add_node(GraphNode(id="haptic:delete-confirm", kind=NodeKind.HAPTIC_PATTERN, label="Delete Confirmation", intent="Heavy notification haptic on delete.", constraints={"intensity": "heavy", "timing_ms": 80, "platform": {"ios": "notificationError", "android": "LONG_PRESS"}}))
g.add_node(GraphNode(id="haptic:checkout-success", kind=NodeKind.HAPTIC_PATTERN, label="Checkout Success", intent="Success notification haptic on order complete.", constraints={"intensity": "heavy", "timing_ms": 100, "platform": {"ios": "notificationSuccess", "android": "CONFIRM"}}))
g.add_node(GraphNode(id="haptic:toggle-switch", kind=NodeKind.HAPTIC_PATTERN, label="Toggle Switch", intent="Light impact haptic on toggle.", constraints={"intensity": "light", "timing_ms": 30, "platform": {"ios": "impactLight", "android": "CLOCK_TICK"}}))

# ── Accessibility Rules ──
g.add_node(GraphNode(id="a11y:product-card", kind=NodeKind.ACCESSIBILITY_RULE, label="Product Card A11y", intent="Semantic role=button, label=product name + price.", constraints={"role": "button", "min_touch_target": 44, "contrast_ratio": 4.5}))
g.add_node(GraphNode(id="a11y:image-gallery", kind=NodeKind.ACCESSIBILITY_RULE, label="Image Gallery A11y", intent="role=image, label=product image N of M.", constraints={"role": "image", "focus_order": 1}))
g.add_node(GraphNode(id="a11y:checkout-form", kind=NodeKind.ACCESSIBILITY_RULE, label="Checkout Form A11y", intent="Semantic form fields with error announcements.", constraints={"role": "form", "announce_errors": True}))

# ── Design Tokens ──
g.add_node(GraphNode(id="token:color-primary", kind=NodeKind.DESIGN_TOKEN, label="Primary Color", intent="#4F46E5 — indigo primary.", constraints={"light": "#4F46E5", "dark": "#818CF8"}))
g.add_node(GraphNode(id="token:color-surface", kind=NodeKind.DESIGN_TOKEN, label="Surface Color", intent="Card and screen backgrounds.", constraints={"light": "#FFFFFF", "dark": "#1E1E2E"}))
g.add_node(GraphNode(id="token:spacing-scale", kind=NodeKind.DESIGN_TOKEN, label="Spacing Scale", intent="4pt grid: xs=4, sm=8, md=16, lg=24, xl=32, 2xl=48.", constraints={"scale": [4, 8, 16, 24, 32, 48]}))
g.add_node(GraphNode(id="token:type-scale", kind=NodeKind.TYPOGRAPHY_TOKEN, label="Type Scale", intent="caption=12, body=14, body-lg=16, h3=18, h2=24, h1=32.", constraints={"scale": {"caption": 12, "body": 14, "body-lg": 16, "h3": 18, "h2": 24, "h1": 32}}))

# ── State ──
g.add_node(GraphNode(id="state:cart", kind=NodeKind.STATE, label="Cart State", intent="Zustand store: items[], total, itemCount.", constraints={"persist": True, "storage": "MMKV"}))
g.add_node(GraphNode(id="state:user", kind=NodeKind.STATE, label="User State", intent="Zustand store: profile, preferences, auth.", constraints={"persist": True, "storage": "MMKV"}))

# ── Performance Targets ──
g.add_node(GraphNode(id="perf:home-fps", kind=NodeKind.PERFORMANCE_TARGET, label="Home Screen 60 FPS", intent="FlashList with getItemType for product cards. 60 FPS scroll.", constraints={"target_fps": 60, "max_render_ms": 16}))
g.add_node(GraphNode(id="perf:bundle-size", kind=NodeKind.PERFORMANCE_TARGET, label="Bundle Budget", intent="JS bundle < 2MB initial, lazy load screens.", constraints={"max_initial_kb": 2048, "lazy_routes": True}))

# ── Edges ──
g.add_edge(GraphEdge(source="screen:home", target="comp:product-card", kind=EdgeKind.COMPOSES))
g.add_edge(GraphEdge(source="screen:product-detail", target="comp:image-gallery", kind=EdgeKind.COMPOSES))
g.add_edge(GraphEdge(source="screen:cart", target="comp:cart-item", kind=EdgeKind.COMPOSES))
g.add_edge(GraphEdge(source="screen:checkout", target="comp:checkout-stepper", kind=EdgeKind.COMPOSES))

g.add_edge(GraphEdge(source="screen:home", target="nav:main-tabs", kind=EdgeKind.NAVIGATES_TO))
g.add_edge(GraphEdge(source="screen:home", target="nav:product-to-detail", kind=EdgeKind.NAVIGATES_TO))

g.add_edge(GraphEdge(source="comp:product-card", target="motion:press-scale", kind=EdgeKind.ANIMATES))
g.add_edge(GraphEdge(source="comp:product-card", target="motion:stagger-enter", kind=EdgeKind.ANIMATES))
g.add_edge(GraphEdge(source="comp:image-gallery", target="motion:hero-transition", kind=EdgeKind.ANIMATES))
g.add_edge(GraphEdge(source="comp:checkout-stepper", target="motion:slide-up-sheet", kind=EdgeKind.ANIMATES))

g.add_edge(GraphEdge(source="screen:home", target="gesture:pull-refresh", kind=EdgeKind.GESTURES))
g.add_edge(GraphEdge(source="comp:cart-item", target="gesture:swipe-delete", kind=EdgeKind.GESTURES))
g.add_edge(GraphEdge(source="comp:image-gallery", target="gesture:pinch-zoom", kind=EdgeKind.GESTURES))

g.add_edge(GraphEdge(source="comp:product-card", target="haptic:add-to-cart", kind=EdgeKind.HAPTICS))
g.add_edge(GraphEdge(source="comp:cart-item", target="haptic:delete-confirm", kind=EdgeKind.HAPTICS))
g.add_edge(GraphEdge(source="screen:checkout", target="haptic:checkout-success", kind=EdgeKind.HAPTICS))
g.add_edge(GraphEdge(source="screen:profile", target="haptic:toggle-switch", kind=EdgeKind.HAPTICS))

g.add_edge(GraphEdge(source="comp:product-card", target="a11y:product-card", kind=EdgeKind.CONSTRAINS))
g.add_edge(GraphEdge(source="comp:image-gallery", target="a11y:image-gallery", kind=EdgeKind.CONSTRAINS))
g.add_edge(GraphEdge(source="screen:checkout", target="a11y:checkout-form", kind=EdgeKind.CONSTRAINS))

g.add_edge(GraphEdge(source="screen:home", target="perf:home-fps", kind=EdgeKind.CONSTRAINS))
g.add_edge(GraphEdge(source="product:store", target="perf:bundle-size", kind=EdgeKind.CONSTRAINS))

g.add_edge(GraphEdge(source="state:cart", target="screen:cart", kind=EdgeKind.ACCESSES))
g.add_edge(GraphEdge(source="state:user", target="screen:profile", kind=EdgeKind.ACCESSES))

print(g.to_json())
