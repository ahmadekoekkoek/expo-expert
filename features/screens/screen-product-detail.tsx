// ProductDetail — Full product details with images, variants, reviews, and add-to-cart
// Route: /product/[id]
// Data: useProduct(id), useProductReviews(id)
// State: productStore, cartStore

import React from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { FadeInDown, FadeIn } from "react-native-reanimated";
import * as Haptics from "expo-haptics";

import { ImageGallery } from "@/components/image-gallery";
import { VariantPicker } from "@/components/variant-picker";
import { ReviewList } from "@/components/review-list";
import { AddToCartButton } from "@/components/add-to-cart-button";
import { StickyFooter } from "@/components/sticky-footer";

// ── Motion ──
// (resolved from motion pattern registry)
const screenEntering = FadeIn.duration(300);

import { Gesture, GestureDetector } from "react-native-gesture-handler";
// ── Gestures ──
// gesture0: pinchZoom (gallery)
const gesture0 = Gesture.Pan()
// gesture1: swipeBack
const gesture1 = Gesture.Pan()

// ── Haptics ──
const triggerHaptic = () => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy); };

export default function ProductDetail() {
  const handlePrimaryAction = () => {
    triggerHaptic();
  };

  return (
    <Animated.View
      entering={screenEntering}
      accessibilityLabel="Full product details with images, variants, reviews, and add-to-cart"
      className="flex-1 bg-background px-4 pt-safe"
    >
      <ImageGallery onAction={handlePrimaryAction} />
      <VariantPicker onAction={handlePrimaryAction} />
      <ReviewList onAction={handlePrimaryAction} />
      <AddToCartButton onAction={handlePrimaryAction} />
      <StickyFooter onAction={handlePrimaryAction} />
    </Animated.View>
  );
}