import { Pressable, StyleSheet, Text, View } from "react-native";

import { Colors } from "@/constants/Colors";
import { BorderRadius, Spacing } from "@/constants/Spacing";
import { useAuthStore } from "@/store/auth-store";

export default function HomeTab() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const c = Colors.light;

  return (
    <View style={[styles.wrap, { backgroundColor: c.bg }]}>
      <Text style={[styles.title, { color: c.text }]}>Welcome back</Text>
      <Text style={[styles.meta, { color: c.textSecond }]}>
        {user?.first_name} {user?.last_name}
      </Text>
      <Text style={[styles.meta, { color: c.textMuted }]}>{user?.email}</Text>
      <Text style={[styles.badge, { color: c.accent }]}>{user?.role}</Text>

      <Pressable style={[styles.btn, { backgroundColor: c.accent }]} onPress={() => void logout()}>
        <Text style={styles.btnLabel}>Sign out</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    padding: Spacing.xl,
    gap: Spacing.sm,
  },
  title: { fontSize: 22, fontWeight: "700" },
  meta: { fontSize: 15 },
  badge: { fontWeight: "600", marginTop: Spacing.sm },
  btn: {
    marginTop: Spacing["2xl"],
    alignSelf: "flex-start",
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
  },
  btnLabel: { color: "#fff", fontWeight: "600" },
});
