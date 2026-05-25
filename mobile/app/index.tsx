import { Redirect } from "expo-router";
import { ActivityIndicator, StyleSheet, View } from "react-native";

import { Colors } from "@/constants/Colors";
import { useAuthStore } from "@/store/auth-store";

function normalizeRole(role: string | undefined) {
  return role?.trim().toUpperCase() ?? "";
}

export default function Index() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const user = useAuthStore((s) => s.user);

  if (isLoading) {
    return (
      <View style={styles.boot}>
        <ActivityIndicator size="large" color={Colors.light.accent} />
      </View>
    );
  }

  if (!isAuthenticated) {
    return <Redirect href="/welcome" />;
  }

  const role = normalizeRole(user?.role);

  if (role === "STUDENT") {
    return <Redirect href="/(student)/dashboard" />;
  }

  if (role === "TEACHER" || role === "HOD") {
    return <Redirect href="/(teacher)/dashboard" />;
  }

  return <Redirect href="/(tabs)" />;
}

const styles = StyleSheet.create({
  boot: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.light.bg,
  },
});
