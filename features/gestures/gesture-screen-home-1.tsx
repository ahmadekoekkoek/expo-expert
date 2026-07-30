// Gesture: doubleTap — Pan (medium priority)
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, { runOnJS } from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

const gesture = Gesture.Pan()
  .activeOffsetVertical(80)
  .onEnd((event) => {
    if (event.velocityVertical > 500) {
      runOnJS(handleGesture)();
    }
  });

// Usage: <GestureDetector gesture={gesture}><View>...</View></GestureDetector>