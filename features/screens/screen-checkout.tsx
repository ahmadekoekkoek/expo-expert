// Checkout — Step-by-step checkout flow with progress indicator
// Route: /checkout
// Data: useCheckout(), usePaymentSheet()
// State: checkoutStore

import React from "react";
import { View, Text, Pressable } from "react-native";
import Animated, { FadeInDown, FadeIn } from "react-native-reanimated";
import * as Haptics from "expo-haptics";

import { ProgressSteps } from "@/components/progress-steps";
import { AddressForm } from "@/components/address-form";
import { PaymentForm } from "@/components/payment-form";
import { ReviewOrder } from "@/components/review-order";
import { Confirmation } from "@/components/confirmation";

// ── Motion ──
// (resolved from motion pattern registry)
const screenEntering = FadeIn.duration(300);

import { Gesture, GestureDetector } from "react-native-gesture-handler";
// ── Gestures ──
// gesture0: swipeBack (previous step)
const gesture0 = Gesture.Pan()

// ── Haptics ──
const triggerHaptic = () => { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); };

export default function Checkout() {
  const handlePrimaryAction = () => {
    triggerHaptic();
  };

  return (
    <Animated.View
      entering={screenEntering}
      accessibilityLabel="Step-by-step checkout flow with progress indicator"
      className="flex-1 bg-background px-4 pt-safe"
    >
      <ProgressSteps onAction={handlePrimaryAction} />
      <AddressForm onAction={handlePrimaryAction} />
      <PaymentForm onAction={handlePrimaryAction} />
      <ReviewOrder onAction={handlePrimaryAction} />
      <Confirmation onAction={handlePrimaryAction} />
    </Animated.View>
  );
}