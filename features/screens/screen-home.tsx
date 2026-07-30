// Home — Main product feed with curated sections and search
// Route: /
// Data: useProducts, useCategories
// State: productStore

import React from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { FadeInDown, FadeIn } from "react-native-reanimated";
import * as Haptics from "expo-haptics";

import { ProductCard } from "@/components/product-card";
import { SearchBar } from "@/components/search-bar";
import { CategoryPills } from "@/components/category-pills";
import { HeroBanner } from "@/components/hero-banner";

// ── Motion ──
// (resolved from motion pattern registry)
const screenEntering = FadeIn.duration(300);

import { Gesture, GestureDetector } from "react-native-gesture-handler";
// ── Gestures ──
// gesture0: pullToRefresh
const gesture0 = Gesture.Pan()
// gesture1: doubleTap (favorite)
const gesture1 = Gesture.Pan()

// ── Haptics ──
const triggerHaptic = () => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); };
const triggerHaptic1 = () => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); };

export default function Home() {
  const handlePrimaryAction = () => {
    triggerHaptic();
  };

  return (
    <Animated.View
      entering={screenEntering}
      accessibilityLabel="Main product feed with curated sections and search"
      className="flex-1 bg-background px-4 pt-safe"
    >
      <ProductCard onAction={handlePrimaryAction} />
      <SearchBar onAction={handlePrimaryAction} />
      <CategoryPills onAction={handlePrimaryAction} />
      <HeroBanner onAction={handlePrimaryAction} />
    </Animated.View>
  );
}