import React from "react";
import { Pressable, Text, View } from "react-native";
import Animated, { withSpring, useAnimatedStyle, useSharedValue, runOnJS } from "react-native-reanimated";
import * as Haptics from "expo-haptics";
import { z } from "zod";

// ─── Props Schema ───────────────────────────────────────────────────────────
export const COMPONENTProps = z.object({
  label: z.string(),
  onPress: z.function(),
  disabled: z.boolean().default(false),
  isLoading: z.boolean().default(false),
  variant: z.enum(["primary", "secondary", "outline", "ghost", "destructive"]).default("primary"),
  size: z.enum(["sm", "md", "lg"]).default("md"),
  accessibilityLabel: z.string().optional(),
});

export type COMPONENTProps = z.infer<typeof COMPONENTProps>;

// ─── Variant Styles ─────────────────────────────────────────────────────────
const variantStyles: Record<string, { container: string; text: string }> = {
  primary: { container: "bg-primary", text: "text-primary-foreground" },
  secondary: { container: "bg-secondary", text: "text-secondary-foreground" },
  outline: { container: "border border-primary bg-transparent", text: "text-primary" },
  ghost: { container: "bg-transparent", text: "text-primary" },
  destructive: { container: "bg-destructive", text: "text-destructive-foreground" },
};

const sizeStyles: Record<string, string> = {
  sm: "px-md py-xs",
  md: "px-lg py-sm",
  lg: "px-xl py-md",
};

// ─── Component ──────────────────────────────────────────────────────────────
export default function COMPONENT_NAME({
  label,
  onPress,
  disabled = false,
  isLoading = false,
  variant = "primary",
  size = "md",
  accessibilityLabel,
}: COMPONENTProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: disabled ? 0.5 : 1,
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.96, { damping: 12, stiffness: 200 });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 12, stiffness: 200 });
  };

  const handlePress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (!disabled && !isLoading) {
      onPress();
    }
  };

  const vs = variantStyles[variant];

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onPress={handlePress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || isLoading}
        className={`rounded-md items-center justify-center ${vs.container} ${sizeStyles[size]}`}
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel ?? label}
        accessibilityState={{ disabled: disabled || isLoading }}
        style={{ minHeight: 44, minWidth: 44 }}
      >
        {isLoading ? (
          <View className="w-5 h-5 border-2 border-t-transparent rounded-full animate-spin" />
        ) : (
          <Text className={`text-subhead font-semibold ${vs.text}`}>
            {label}
          </Text>
        )}
      </Pressable>
    </Animated.View>
  );
}
