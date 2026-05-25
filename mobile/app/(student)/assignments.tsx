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

type Assignment = {
  id: string;
  title: string;
  subject_name: string;
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

export default function StudentAssignmentsScreen() {
  const insets = useSafeAreaInsets();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<string, string>>({});

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

  const handleSubmit = async (assignmentId: string) => {
    setSubmittingId(assignmentId);
    try {
      const res = await api.post<ApiEnvelope<unknown>>("/assignments/submissions/", {
        assignment: assignmentId,
        submission_text: drafts[assignmentId]?.trim() ?? "",
      });
      Alert.alert("Submitted", res.data.message ?? "Submission saved.");
      await load();
    } catch (e: unknown) {
      Alert.alert("Submit failed", e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setSubmittingId(null);
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
      <Text style={styles.title}>Assignments</Text>
      <Text style={styles.sub}>Coursework and deadlines</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {assignments.length === 0 ? (
        <Text style={styles.empty}>No assignments published yet.</Text>
      ) : (
        assignments.map((item) => (
          <View key={item.id} style={styles.card}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.meta}>
              {item.subject_name} · Due {new Date(item.due_date).toLocaleDateString()} · {item.max_marks} marks
            </Text>
            <TextInput
              style={styles.input}
              placeholder="Submission notes (optional)"
              placeholderTextColor={Colors.light.textMuted}
              multiline
              value={drafts[item.id] ?? ""}
              onChangeText={(text) => setDrafts((prev) => ({ ...prev, [item.id]: text }))}
            />
            <TouchableOpacity
              style={[styles.btn, submittingId === item.id && styles.btnDisabled]}
              onPress={() => void handleSubmit(item.id)}
              disabled={submittingId === item.id}
            >
              {submittingId === item.id ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.btnLabel}>Submit</Text>
              )}
            </TouchableOpacity>
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
    marginBottom: Spacing.base,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  cardTitle: { fontSize: 16, fontWeight: "700", color: Colors.light.text },
  meta: { fontSize: 12, color: Colors.light.textMuted, marginTop: Spacing.xs, marginBottom: Spacing.sm },
  input: {
    borderWidth: 1,
    borderColor: Colors.light.border,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    minHeight: 72,
    fontSize: 14,
    color: Colors.light.text,
    backgroundColor: Colors.light.bg,
    textAlignVertical: "top",
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
