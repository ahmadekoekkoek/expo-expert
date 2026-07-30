// Cart — Cart overview with line items, quantities, subtotal, and checkout
// Route: /cart
// Data: useCart()
// State: cartStore

import React from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { FadeInDown, FadeIn } from "react-native-reanimated";
import * as Haptics from "expo-haptics";

import { CartItem } from "@/components/cart-item";
import { QuantityStepper } from "@/components/quantity-stepper";
import { PromoInput } from "@/components/promo-input";
import { OrderSummary } from "@/components/order-summary";
import { CheckoutButton } from "@/components/checkout-button";

// ── Motion ──
// (resolved from motion pattern registry)
const screenEntering = FadeIn.duration(300);

import { Gesture, GestureDetector } from "react-native-gesture-handler";
// ── Gestures ──
// gesture0: swipe-to-delete
const gesture0 = Gesture.Pan()
// gesture1: longPress (reorder)
const gesture1 = Gesture.Pan()

// ── Haptics ──
const triggerHaptic = () => { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error); };
const triggerHaptic1 = () => { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); };

export default function Cart() {
  const handlePrimaryAction = () => {
    triggerHaptic();
  };

  return (
    <Animated.View
      entering={screenEntering}
      accessibilityLabel="Cart overview with line items, quantities, subtotal, and checkout"
      className="flex-1 bg-background px-4 pt-safe"
    >
      <CartItem onAction={handlePrimaryAction} />
      <QuantityStepper onAction={handlePrimaryAction} />
      <PromoInput onAction={handlePrimaryAction} />
      <OrderSummary onAction={handlePrimaryAction} />
      <CheckoutButton onAction={handlePrimaryAction} />
    </Animated.View>
  );
}