import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { Spacing } from "@/constants/Spacing";
import api from "@/lib/api";
import type { ApiEnvelope } from "@/lib/types";

type Assignment = {
  id: string;
  title: string;
  subject_name: string;
  section: string;
  due_date: string;
  max_marks: number;
  status: string;
};

function unwrapList<T>(payload: ApiEnvelope<T[] | { items?: T[] }> | undefined): T[] {
  const raw = payload?.data;
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object" && Array.isArray((raw as { items?: T[] }).items)) {
    return (raw as { items: T[] }).items;
  }
  return [];
}

export default function TeacherAssignmentsScreen() {
  const insets = useSafeAreaInsets();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const res = await api.get<ApiEnvelope<Assignment[]>>("/assignments/");
      setAssignments(unwrapList(res.data));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load assignments.");
    }
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      await load();
      setLoading(false);
    })();
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={[styles.center, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={Colors.light.accent} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={{ paddingTop: insets.top + Spacing["2xl"], paddingBottom: Spacing["2xl"] }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => void onRefresh()} />}
    >
      <Text style={styles.title}>Assignments</Text>
      <Text style={styles.sub}>Your published coursework</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {assignments.length === 0 ? (
        <Text style={styles.empty}>No assignments yet.</Text>
      ) : (
        assignments.map((item) => (
          <View key={item.id} style={styles.card}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.meta}>
              {item.subject_name} · Sec {item.section} · Due {new Date(item.due_date).toLocaleDateString()}
            </Text>
            <View style={styles.footer}>
              <Text style={styles.marks}>{item.max_marks} marks</Text>
              <Text style={styles.status}>{item.status}</Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: Colors.light.bg, paddingHorizontal: Spacing.xl },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: Colors.light.bg },
  title: { fontSize: 22, fontWeight: "700", color: Colors.light.text, marginBottom: Spacing.xs },
  sub: { fontSize: 14, color: Colors.light.textMuted, marginBottom: Spacing.lg },
  error: { color: Colors.light.error, marginBottom: Spacing.base },
  empty: { fontSize: 15, color: Colors.light.textMuted },
  card: {
    backgroundColor: Colors.light.surface,
    borderRadius: 12,
    padding: Spacing.base,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  cardTitle: { fontSize: 16, fontWeight: "700", color: Colors.light.text },
  meta: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs },
  footer: { flexDirection: "row", justifyContent: "space-between", marginTop: Spacing.sm },
  marks: { fontSize: 13, fontWeight: "600", color: Colors.light.accent },
  status: { fontSize: 12, fontWeight: "700", color: Colors.light.textMuted },
});
