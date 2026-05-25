import "react-native-gesture-handler";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { Alert } from "react-native";
import { GestureHandlerRootView } from "react-native-gesture-handler";

import { phoneLikelyCannotReachApiUrl } from "@/lib/dev-api-url-guard";
import { useAuthStore } from "@/store/auth-store";

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

export default function RootLayout() {
  const restoreSession = useAuthStore((s) => s.restoreSession);

  useEffect(() => {
    if (typeof __DEV__ !== "undefined" && __DEV__) {
      const raw = process.env.EXPO_PUBLIC_API_URL ?? "";
      const warn = phoneLikelyCannotReachApiUrl(raw);
      if (warn) {
        Alert.alert(
          "Fix mobile/.env API URL",
          `${warn}\n\nCurrent: ${raw || "(unset)"}\nUse the same IPv4 that opens /health/ in your phone browser.`,
          [{ text: "OK" }],
        );
      }
    }
  }, []);

  useEffect(() => {
    void restoreSession().finally(() => SplashScreen.hideAsync());
  }, [restoreSession]);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }} />
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
