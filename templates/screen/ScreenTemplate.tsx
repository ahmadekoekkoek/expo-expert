import { View, Text, Pressable } from "react-native";
import Animated, { FadeInDown, FadeIn, FadeOutDown } from "react-native-reanimated";
import * as Haptics from "expo-haptics";
import { z } from "zod";

// ─── Props Schema ───────────────────────────────────────────────────────────
export const SCREENComponentProps = z.object({
  title: z.string(),
  subtitle: z.string().optional(),
  data: z.array(z.unknown()).optional(),
  isLoading: z.boolean().default(false),
  onAction: z.function().optional(),
});

export type SCREENComponentProps = z.infer<typeof SCREENComponentProps>;

// ─── Component ──────────────────────────────────────────────────────────────
export default function SCREEN_NAME({ title, subtitle, data, isLoading, onAction }: SCREENComponentProps) {
  return (
    <Animated.View
      entering={FadeInDown.duration(600).easing((t: number) => t)}
      exiting={FadeOutDown.duration(400)}
      className="flex-1 bg-background px-md pt-safe"
      accessibilityRole="none"
      accessibilityLabel={title}
    >
      {/* Header */}
      <View className="mb-lg">
        <Text
          className="text-headline text-foreground mb-sm"
          accessibilityRole="header"
        >
          {title}
        </Text>
        {subtitle && (
          <Text className="text-body text-muted-foreground">
            {subtitle}
          </Text>
        )}
      </View>

      {/* Content */}
      {isLoading ? (
        <SCREENSkeleton />
      ) : (
        <SCREENContent data={data} onAction={onAction} />
      )}
    </Animated.View>
  );
}

// ─── Content ────────────────────────────────────────────────────────────────
function SCREENContent({ data, onAction }: { data?: unknown[]; onAction?: () => void }) {
  const handlePress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onAction?.();
  };

  return (
    <Animated.View
      entering={FadeIn.delay(100)}
      className="flex-1 gap-md"
    >
      {data?.map((item, index) => (
        <Animated.View
          key={index}
          entering={FadeInDown.delay(index * 60)}
        >
          <Pressable
            onPress={handlePress}
            className="bg-card rounded-lg p-md shadow-sm border border-border active:opacity-80"
            accessibilityRole="button"
            style={{ minHeight: 44 }}
          >
            {/* Item content goes here */}
          </Pressable>
        </Animated.View>
      ))}
    </Animated.View>
  );
}

// ─── Skeleton ───────────────────────────────────────────────────────────────
function SCREENSkeleton() {
  return (
    <View className="flex-1 gap-md" accessibilityElementsHidden>
      {Array.from({ length: 3 }).map((_, i) => (
        <View
          key={i}
          className="bg-muted rounded-lg animate-pulse"
          style={{ height: 80 }}
        />
      ))}
    </View>
  );
}
