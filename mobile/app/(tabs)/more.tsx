import { StyleSheet, Text, View } from "react-native";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";

export default function MoreTab() {
  const c = Colors.light;

  return (
    <View style={[styles.wrap, { backgroundColor: c.bg }]}>
      <Text style={[styles.title, { color: c.text }]}>More</Text>
      <Text style={[styles.body, { color: c.textSecond }]}>
        Wire TanStack Query lists and API modules here as endpoints stabilize.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, padding: Spacing.xl },
  title: { fontSize: 20, fontWeight: "700", marginBottom: Spacing.sm },
  body: { fontSize: 14, lineHeight: 20 },
});
