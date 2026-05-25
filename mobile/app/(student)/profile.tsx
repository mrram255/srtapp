import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";
import { useAuthStore } from "@/store/auth-store";

export default function StudentProfilePlaceholder() {
  const insets = useSafeAreaInsets();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  return (
    <View style={[styles.screen, { paddingTop: insets.top + Spacing["2xl"] }]}>
      <Text style={styles.title}>Profile</Text>
      <Text style={styles.line}>
        {user?.first_name} {user?.last_name}
      </Text>
      <Text style={styles.muted}>{user?.email}</Text>
      <TouchableOpacity style={styles.signOut} onPress={() => void logout()}>
        <Text style={styles.signOutLabel}>Sign out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: Colors.light.bg,
    paddingHorizontal: Spacing.xl,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: Colors.light.text,
    marginBottom: Spacing.lg,
  },
  line: {
    fontSize: 17,
    fontWeight: "600",
    color: Colors.light.text,
  },
  muted: {
    marginTop: Spacing.xs,
    fontSize: 14,
    color: Colors.light.textMuted,
    marginBottom: Spacing.xl,
  },
  signOut: {
    alignSelf: "flex-start",
    backgroundColor: Colors.light.surface,
    borderWidth: 1,
    borderColor: Colors.light.border,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: 12,
  },
  signOutLabel: {
    color: Colors.light.accent,
    fontWeight: "600",
  },
});
