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

type ExamResult = {
  id: string;
  exam_name: string;
  marks_obtained: number;
  percentage: number;
  grade: string;
  status: string;
  rank: number | null;
};

function unwrapList<T>(payload: ApiEnvelope<T[] | { items?: T[] }> | undefined): T[] {
  const raw = payload?.data;
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object" && Array.isArray((raw as { items?: T[] }).items)) {
    return (raw as { items: T[] }).items;
  }
  return [];
}

export default function StudentResultsScreen() {
  const insets = useSafeAreaInsets();
  const [results, setResults] = useState<ExamResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const res = await api.get<ApiEnvelope<ExamResult[]>>("/exams/results/");
      setResults(unwrapList(res.data));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load results.");
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
      <Text style={styles.title}>Results</Text>
      <Text style={styles.sub}>Exam marks and grades</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {results.length === 0 ? (
        <Text style={styles.empty}>No published results yet.</Text>
      ) : (
        results.map((row) => (
          <View key={row.id} style={styles.card}>
            <Text style={styles.exam}>{row.exam_name}</Text>
            <View style={styles.row}>
              <Text style={styles.marks}>{row.marks_obtained} marks</Text>
              <Text style={styles.pct}>{row.percentage}%</Text>
            </View>
            <View style={styles.metaRow}>
              <Text style={styles.meta}>Grade: {row.grade || "—"}</Text>
              <Text style={styles.meta}>Status: {row.status}</Text>
              {row.rank ? <Text style={styles.meta}>Rank #{row.rank}</Text> : null}
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
  exam: { fontSize: 16, fontWeight: "700", color: Colors.light.text },
  row: { flexDirection: "row", justifyContent: "space-between", marginTop: Spacing.sm },
  marks: { fontSize: 15, fontWeight: "600", color: Colors.light.accent },
  pct: { fontSize: 15, fontWeight: "700", color: Colors.light.text },
  metaRow: { flexDirection: "row", flexWrap: "wrap", gap: Spacing.sm, marginTop: Spacing.sm },
  meta: { fontSize: 12, color: Colors.light.textMuted },
});
