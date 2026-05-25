import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Colors } from "@/constants/Colors";
import { BorderRadius, Spacing } from "@/constants/Spacing";
import api from "@/lib/api";
import type { ApiEnvelope } from "@/lib/types";

type Submission = {
  id: string;
  assignment_title: string;
  student_enrollment: string;
  status: string;
  marks_obtained: number | null;
  submitted_at: string | null;
};

function unwrapList<T>(payload: ApiEnvelope<T[] | { items?: T[] }> | undefined): T[] {
  const raw = payload?.data;
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object" && Array.isArray((raw as { items?: T[] }).items)) {
    return (raw as { items: T[] }).items;
  }
  return [];
}

export default function TeacherGradesScreen() {
  const insets = useSafeAreaInsets();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [gradingId, setGradingId] = useState<string | null>(null);
  const [marksDraft, setMarksDraft] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      setError("");
      const res = await api.get<ApiEnvelope<Submission[]>>("/assignments/submissions/", {
        params: { status: "SUBMITTED" },
      });
      setSubmissions(unwrapList(res.data));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load submissions.");
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

  const handleGrade = async (submissionId: string) => {
    const marks = Number(marksDraft[submissionId]);
    if (Number.isNaN(marks)) {
      Alert.alert("Required", "Enter marks as a number.");
      return;
    }

    setGradingId(submissionId);
    try {
      const res = await api.patch<ApiEnvelope<unknown>>(
        `/assignments/submissions/${submissionId}/grade/`,
        { marks_obtained: marks },
      );
      Alert.alert("Graded", res.data.message ?? "Submission graded.");
      await load();
    } catch (e: unknown) {
      Alert.alert("Grade failed", e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setGradingId(null);
    }
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
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.title}>Grades</Text>
      <Text style={styles.sub}>Submissions awaiting marks</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {submissions.length === 0 ? (
        <Text style={styles.empty}>No submissions to grade.</Text>
      ) : (
        submissions.map((row) => (
          <View key={row.id} style={styles.card}>
            <Text style={styles.cardTitle}>{row.assignment_title}</Text>
            <Text style={styles.meta}>
              {row.student_enrollment} · {row.status}
              {row.submitted_at ? ` · ${new Date(row.submitted_at).toLocaleDateString()}` : ""}
            </Text>
            {row.marks_obtained != null ? (
              <Text style={styles.graded}>Graded: {row.marks_obtained}</Text>
            ) : (
              <>
                <TextInput
                  style={styles.input}
                  placeholder="Marks"
                  placeholderTextColor={Colors.light.textMuted}
                  keyboardType="number-pad"
                  value={marksDraft[row.id] ?? ""}
                  onChangeText={(text) => setMarksDraft((prev) => ({ ...prev, [row.id]: text }))}
                />
                <TouchableOpacity
                  style={[styles.btn, gradingId === row.id && styles.btnDisabled]}
                  onPress={() => void handleGrade(row.id)}
                  disabled={gradingId === row.id}
                >
                  {gradingId === row.id ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.btnLabel}>Save grade</Text>
                  )}
                </TouchableOpacity>
              </>
            )}
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
  cardTitle: { fontSize: 15, fontWeight: "700", color: Colors.light.text },
  meta: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs },
  graded: { marginTop: Spacing.sm, fontSize: 14, fontWeight: "600", color: Colors.light.success },
  input: {
    marginTop: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.light.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    fontSize: 15,
    color: Colors.light.text,
    backgroundColor: Colors.light.bg,
  },
  btn: {
    marginTop: Spacing.sm,
    backgroundColor: Colors.light.accent,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    alignItems: "center",
  },
  btnDisabled: { opacity: 0.7 },
  btnLabel: { color: "#fff", fontWeight: "700", fontSize: 14 },
});
